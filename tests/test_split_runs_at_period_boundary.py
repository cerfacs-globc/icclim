"""
Runs of consecutive days that cross the boundary of an output period (issue #543).

By default a run is attributed whole to the period where it ends. With
``split_runs_at_period_boundary=True`` the runs are cut at
the boundary of every output period.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.generic.functions import _run_length_encoding
from icclim.frequency import FrequencyRegistry

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class RunIndex:
    """One of the four ECA&D indices built on max_consecutive_occurrence."""

    name: str
    variable: str
    units: str
    normal: float
    event: float
    threshold: str
    is_event: str  # how to flag the event days again, written independently


INDICES = [
    RunIndex("CDD", "pr", "mm/day", 5.0, 0.0, "< 1 mm/day", "lt1"),
    RunIndex("CWD", "pr", "mm/day", 0.0, 5.0, ">= 1 mm/day", "ge1"),
    RunIndex("CFD", "tn", "degC", 1.0, -1.0, "< 0 degC", "lt0"),
    RunIndex("CSU", "tx", "degC", 0.0, 30.0, "> 25 degC", "gt25"),
]
INDEX_IDS = [i.name for i in INDICES]

FLAGGERS = {
    "lt1": lambda v: v < 1,
    "ge1": lambda v: v >= 1,
    "lt0": lambda v: v < 0,
    "gt25": lambda v: v > 25,
}


def _longest_run(flags: np.ndarray) -> int:
    """Longest run of consecutive True values, in plain Python."""
    best = current = 0
    for flag in flags:
        current = current + 1 if flag else 0
        best = max(best, current)
    return best


def _series(index: RunIndex, start: str, end: str, event: tuple[str, str]):
    """1D daily series, with a single event window."""
    time = pd.date_range(start, end)
    values = np.where(
        (time >= event[0]) & (time <= event[1]), index.event, index.normal
    )
    return xr.DataArray(
        values,
        dims="time",
        coords={"time": time},
        name=index.variable,
        attrs={"units": index.units},
    )


def _boundary_example(index: RunIndex) -> xr.DataArray:
    """Daily 2001-2002, event from 2001-10-01 to 2002-04-30 (212 days)."""
    return _series(index, "2001-01-01", "2002-12-31", ("2001-10-01", "2002-04-30"))


def _compute(index: RunIndex, source: xr.DataArray, **kwargs) -> xr.DataArray:
    return getattr(icclim, index.name.lower())(
        source, out_file=None, completeness="none", **kwargs
    )[index.name].compute()


@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
class TestBoundaryExample:
    def test_default_attributes_the_run_to_the_period_where_it_ends(
        self, index: RunIndex
    ) -> None:
        source = _boundary_example(index)
        np.testing.assert_array_equal(_compute(index, source).values, [0, 212])
        np.testing.assert_array_equal(
            _compute(index, source, split_runs_at_period_boundary=False).values,
            [0, 212],
        )

    def test_explicit_first_preserves_pre_7_4_0_attribution(
        self, index: RunIndex
    ) -> None:
        source = _boundary_example(index)
        actual = _compute(index, source, run_index="first")
        np.testing.assert_array_equal(actual.values, [212, 0])

    def test_default_equals_explicit_last(self, index: RunIndex) -> None:
        source = _boundary_example(index)
        np.testing.assert_array_equal(
            _compute(index, source).values,
            _compute(index, source, run_index="last").values,
        )

    @pytest.mark.parametrize("run_index", ["first", "last"])
    def test_option_splits_the_run_whatever_the_run_index(
        self, index: RunIndex, run_index: str
    ) -> None:
        source = _boundary_example(index)
        actual = _compute(
            index, source, split_runs_at_period_boundary=True, run_index=run_index
        )
        # 2001-10-01 to 2001-12-31 is 92 days, 2002-01-01 to 2002-04-30 is 120 days.
        np.testing.assert_array_equal(actual.values, [92, 120])

    def test_option_matches_an_independent_computation(self, index: RunIndex) -> None:
        source = _boundary_example(index)
        flags = FLAGGERS[index.is_event](source.values)
        years = source.time.dt.year.values
        expected = [_longest_run(flags[years == year]) for year in (2001, 2002)]
        actual = _compute(index, source, split_runs_at_period_boundary=True)
        np.testing.assert_array_equal(actual.values, expected)
        assert not np.isnan(actual.values).any()


@pytest.mark.parametrize("name", ["CDD", "CFD", "max_consecutive_occurrence"])
def test_default_warning_is_on_stdout_and_explicit_run_index_is_quiet(
    name: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The 7.4.0 default notice is emitted once and cannot be filtered."""
    index = INDICES[0] if name == "CDD" else INDICES[2]
    source = _boundary_example(index)

    if name == "max_consecutive_occurrence":

        def compute(**kwargs):
            return icclim.max_consecutive_occurrence(
                source,
                var_name=index.variable,
                threshold=index.threshold,
                out_file=None,
                completeness="none",
                **kwargs,
            ).compute()
    else:

        def compute(**kwargs):
            return getattr(icclim, name.lower())(
                source,
                out_file=None,
                completeness="none",
                **kwargs,
            ).compute()

    compute()
    notice = capsys.readouterr().out
    assert notice.count("icclim 7.4.0 behaviour change") == 1
    assert name in notice
    assert 'run_index="last"' in notice
    assert 'run_index="first"' in notice
    assert "split_runs_at_period_boundary=True" in notice

    for explicit in ("first", "last"):
        compute(run_index=explicit)
        assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    ("function", "index", "variable"),
    [
        (icclim.dcsc.pxcdd, INDICES[0], "PXCDD"),
        (icclim.dcsc.pxcwd, INDICES[1], "PXCWD"),
    ],
    ids=["PXCDD", "PXCWD"],
)
def test_dcsc_longest_run_indices_use_the_same_default(
    function: Callable[..., xr.Dataset],
    index: RunIndex,
    variable: str,
) -> None:
    source = _boundary_example(index)
    default = function(source, out_file=None, completeness="none")[variable].compute()
    first = function(
        source,
        out_file=None,
        completeness="none",
        run_index="first",
    )[variable].compute()
    np.testing.assert_array_equal(default.values, [0, 212])
    np.testing.assert_array_equal(first.values, [212, 0])


@pytest.mark.parametrize("chunk", [None, 30])
@pytest.mark.parametrize("slice_mode", ["year", "month"])
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_option_on_a_grid_with_runs_crossing_several_boundaries(
    index: RunIndex, slice_mode: str, chunk: int | None
) -> None:
    """
    Compare with an independent computation that splits the periods first.

    No period is NaN because a run started in the previous one.
    """
    time = pd.date_range("2000-01-01", "2003-12-31")
    windows = {
        (0, 0): [("2000-11-15", "2001-02-10"), ("2002-12-01", "2003-03-15")],
        (0, 1): [("2001-12-31", "2002-01-01")],
        (1, 0): [("2001-07-01", "2003-02-28")],  # crosses two year boundaries
        (1, 1): [],  # no event at all
    }
    values = np.full((len(time), 2, 2), index.normal)
    for (ilat, ilon), spans in windows.items():
        for start, end in spans:
            values[(time >= start) & (time <= end), ilat, ilon] = index.event
    source = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [0.0, 1.0], "lon": [0.0, 1.0]},
        name=index.variable,
        attrs={"units": index.units},
    )
    if chunk is not None:
        source = source.chunk({"time": chunk})
    actual = _compute(
        index, source, slice_mode=slice_mode, split_runs_at_period_boundary=True
    ).transpose("time", "lat", "lon")

    flags = FLAGGERS[index.is_event](values)
    if slice_mode == "year":
        keys = time.year
        periods = sorted(set(keys))
    else:
        keys = time.year * 100 + time.month
        periods = sorted(set(keys))
    expected = np.array(
        [
            [
                [_longest_run(flags[keys == p, ilat, ilon]) for ilon in range(2)]
                for ilat in range(2)
            ]
            for p in periods
        ],
        dtype=float,
    )
    assert actual.shape == expected.shape
    assert not np.isnan(actual.values).any()
    np.testing.assert_array_equal(actual.values, expected)
    if slice_mode == "year":
        assert actual.values[1, 1, 0] == 184  # 2001-07-01 to 2001-12-31
        assert actual.values[2, 1, 0] == 365  # the whole of 2002 is inside the run
        assert actual.values[:, 1, 1].tolist() == [0, 0, 0, 0]


@pytest.mark.parametrize("split", [False, True])
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_generic_function_and_ecad_index_give_the_same_values(
    index: RunIndex,
    split: bool,
) -> None:
    source = _boundary_example(index)
    ecad = _compute(index, source, split_runs_at_period_boundary=split)
    generic = icclim.max_consecutive_occurrence(
        in_files=source,
        var_name=index.variable,
        threshold=index.threshold,
        slice_mode="year",
        out_file=None,
        completeness="none",
        split_runs_at_period_boundary=split,
    ).max_consecutive_occurrence.compute()
    np.testing.assert_array_equal(generic.values, ecad.values)
    np.testing.assert_array_equal(ecad.values, [92, 120] if split else [0, 212])


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("time_last", [False, True], ids=["time-first", "time-last"])
def test_dimension_order_does_not_depend_on_the_index_or_the_option(
    time_last: bool,
    chunked: bool,
) -> None:
    """
    The four indices return the same dimension order, with or without the option.

    The order itself (time is not the first dimension) is tracked in issue #542;
    this test only checks that the option does not change it.
    """
    dims_seen = {}
    for index in INDICES:
        series = _boundary_example(index)
        cube = series.expand_dims(lat=[0.0, 1.0], lon=[0.0, 1.0, 2.0], axis=(1, 2))
        cube = cube.transpose("lat", "lon", "time") if time_last else cube
        if chunked:
            cube = cube.chunk({"lat": 1})
        for split in (False, True):
            result = _compute(index, cube, split_runs_at_period_boundary=split)
            dims_seen[index.name, split] = result.dims
            expected = [92, 120] if split else [0, 212]
            np.testing.assert_array_equal(result.isel(lat=0, lon=0).values, expected)
    assert len(set(dims_seen.values())) == 1, dims_seen


@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_date_event_with_the_option_dates_the_run_inside_each_period(
    index: RunIndex,
) -> None:
    """``event_date_end`` is the day after the last day of the run."""
    source = _boundary_example(index)
    kwargs = {"out_file": None, "completeness": "none", "date_event": True}
    default = getattr(icclim, index.name.lower())(source, **kwargs).compute()
    split = getattr(icclim, index.name.lower())(
        source, split_runs_at_period_boundary=True, **kwargs
    ).compute()

    def as_days(da: xr.DataArray) -> list[str]:
        return [str(v)[:10] for v in da.values.astype("datetime64[D]")]

    # Default: the whole run belongs to 2002, where it ends.
    assert as_days(default.event_date_start)[1] == "2001-10-01"
    assert as_days(default.event_date_end)[1] == "2002-05-01"
    # With the option each period dates its own part of the run.
    assert as_days(split.event_date_start) == ["2001-10-01", "2002-01-01"]
    assert as_days(split.event_date_end) == ["2002-01-01", "2002-05-01"]


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("time_last", [False, True], ids=["time-first", "time-last"])
@pytest.mark.parametrize("run_index", ["first", "last"])
def test_split_encoding_has_the_dimension_order_of_the_default_encoding(
    run_index: str, time_last: bool, chunked: bool
) -> None:
    """
    The order of the dimensions of a run length encoding depends on xclim.

    The split encoding must produce the same order as the default one, whichever
    order the installed xclim returns (checked with xclim 0.45.0, 0.60.0 and 1.0.0).
    """
    time = pd.date_range("2001-01-01", "2002-12-31")
    flags = (time >= "2001-10-01") & (time <= "2002-04-30")
    cube = xr.DataArray(
        np.broadcast_to(flags[:, None, None], (len(time), 2, 3)).copy(),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [0.0, 1.0], "lon": [0.0, 1.0, 2.0]},
    )
    if time_last:
        cube = cube.transpose("lat", "lon", "time")
    if chunked:
        cube = cube.chunk({"lat": 1})
    year = FrequencyRegistry.YEAR
    default = _run_length_encoding(
        cube, year, run_index, split_at_period_boundary=False
    )
    split = _run_length_encoding(cube, year, run_index, split_at_period_boundary=True)
    assert split.dims == default.dims
    assert split.shape == default.shape
    # Only the values differ: the split encoding restarts in each year.
    assert int(default.max()) == 212
    assert int(split.max()) == 120


def _bootstrap_boundary_case() -> tuple[xr.DataArray, object]:
    """Random series with one 10-day warm spell from 2044-12-28 to 2045-01-06."""
    from icclim.threshold.factory import build_threshold

    time = pd.date_range("2042-01-01", periods=365 * 5 + 1)
    values = np.random.default_rng(3).normal(0, 1, time.size)
    values[(time >= "2044-12-28") & (time <= "2045-01-06")] = 10.0
    source = xr.DataArray(
        values,
        dims="time",
        coords={"time": time},
        name="tasmax",
        attrs={"units": "degC"},
    )
    threshold = build_threshold(
        "> 90 doy_per",
        doy_window_width=1,
        reference_period=("2042-01-01", "2043-12-31"),
    )
    return source, threshold


@pytest.mark.parametrize("mode", [None, "default", "safe"])
@pytest.mark.parametrize("split", [False, True], ids=["default", "split"])
def test_split_option_on_the_bootstrap_spell_mask_path(
    mode: str | None,
    split: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The option is applied on the bootstrap spell-mask path too.

    The three bootstrap modes (optimized, reference, exact tiled) give the same values
    with and without the option, and the option cuts the spell at 2044-12-31.
    """
    from icclim._core.generic import functions

    source, threshold = _bootstrap_boundary_case()
    masks = []
    original = functions._compute_bootstrap_spell_mask

    def spy(*args, **kwargs):
        mask = original(*args, **kwargs)
        masks.append(mask)
        return mask

    monkeypatch.setattr(functions, "_compute_bootstrap_spell_mask", spy)
    if mode is None:
        monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE", raising=False)
    else:
        monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", mode)

    result = icclim.max_consecutive_occurrence(
        source,
        threshold=threshold,
        slice_mode="year",
        out_file=None,
        completeness="none",
        run_index="last",
        split_runs_at_period_boundary=split,
    )["max_consecutive_occurrence"].compute()

    # Same values whatever the mode. 2045 holds the whole spell by default (12 days with
    # two adjacent days) and only its last 6 days when the runs are cut.
    expected = [7, 10, 4, 8, 4] if split else [7, 10, 4, 12, 4]
    np.testing.assert_array_equal(result.values, expected)
    if mode is None:
        assert any(mask is not None for mask in masks)

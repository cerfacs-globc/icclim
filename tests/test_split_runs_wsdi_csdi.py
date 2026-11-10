"""
``split_runs_at_period_boundary`` for WSDI, CSDI and ``sum_of_spell_lengths``
(issue #614), and the check that every public function accepting the option honours it.

With the option, runs are cut at every output period boundary first and then only the
pieces of at least 6 days are kept. By default a spell is attributed whole to the
period where it starts (``run_index="first"``), unchanged.
"""

from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

OPTION = "split_runs_at_period_boundary"
BASE = ("1991-01-01", "1992-12-31")


def _cube(name: str, normal: float, event: float, start: str, end: str) -> xr.DataArray:
    """Daily 2001-2002, two columns, a spell between ``start`` and ``end``."""
    time = pd.date_range("2001-01-01", "2002-12-31")
    values = np.where((time >= start) & (time <= end), event, normal)
    return xr.DataArray(
        values[:, None] * np.ones((len(time), 2)),
        dims=("time", "x"),
        coords={"time": time, "x": [0, 1]},
        name=name,
        attrs={"units": "degC"},
    )


def _with_base(study: xr.DataArray, normal: float) -> xr.DataArray:
    """Prepend a constant base period (1991-1992), so thresholds are ``normal``."""
    time = pd.date_range(BASE[0], BASE[1])
    base = xr.DataArray(
        np.full((len(time), 2), normal),
        dims=("time", "x"),
        coords={"time": time, "x": [0, 1]},
        name=study.name,
        attrs=study.attrs,
    )
    between = pd.date_range("1993-01-01", "2000-12-31")
    gap = xr.DataArray(
        np.full((len(between), 2), normal),
        dims=("time", "x"),
        coords={"time": between, "x": [0, 1]},
        name=study.name,
        attrs=study.attrs,
    )
    return xr.concat([base, gap, study], dim="time")


# name, variable, normal, event, function
SPELL_INDICES = [
    ("WSDI", "tasmax", 10.0, 20.0, icclim.wsdi),
    ("CSDI", "tasmin", 10.0, 0.0, icclim.csdi),
]


def _spell_index(name, variable, normal, event, function, spell, freq, chunked, split):
    study = _cube(variable, normal, event, *spell)
    source = _with_base(study, normal)
    if chunked:
        source = source.chunk({"x": 1})
    result = function(
        source,
        base_period_time_range=BASE,
        time_range=("2001-01-01", "2002-12-31"),
        slice_mode=freq,
        out_file=None,
        completeness="none",
        **({OPTION: True} if split else {}),
    )[name].compute()
    return result.isel(x=0).values, result


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize(
    ("name", "variable", "normal", "event", "function"), SPELL_INDICES
)
class TestSpellIndices:
    def test_yearly_default_is_unchanged(
        self, name, variable, normal, event, function, chunked
    ) -> None:
        # 10 days from 28 December to 6 January, attributed whole to 2001.
        values, _ = _spell_index(
            name,
            variable,
            normal,
            event,
            function,
            ("2001-12-28", "2002-01-06"),
            "year",
            chunked,
            split=False,
        )
        np.testing.assert_array_equal(values, [10, 0])

    def test_yearly_split_cuts_then_keeps_pieces_of_6_days(
        self, name, variable, normal, event, function, chunked
    ) -> None:
        # Pieces of 4 days (2001, dropped) and 6 days (2002, kept).
        values, result = _spell_index(
            name,
            variable,
            normal,
            event,
            function,
            ("2001-12-28", "2002-01-06"),
            "year",
            chunked,
            split=True,
        )
        np.testing.assert_array_equal(values, [0, 6])
        assert not np.isnan(values).any()
        default_dims = _spell_index(
            name,
            variable,
            normal,
            event,
            function,
            ("2001-12-28", "2002-01-06"),
            "year",
            chunked,
            split=False,
        )[1].dims
        assert result.dims == default_dims

    def test_monthly_split(
        self, name, variable, normal, event, function, chunked
    ) -> None:
        spell = ("2001-12-28", "2002-01-06")
        default, _ = _spell_index(
            name, variable, normal, event, function, spell, "month", chunked, False
        )
        split, _ = _spell_index(
            name, variable, normal, event, function, spell, "month", chunked, True
        )
        # Months of 2001-2002: December 2001 is the 12th, January 2002 the 13th.
        assert default[11] == 10
        assert default[12] == 0
        assert split[11] == 0
        assert split[12] == 6
        assert np.count_nonzero(default) == 1
        assert np.count_nonzero(split) == 1

    def test_monthly_split_drops_the_short_piece_in_the_second_month(
        self, name, variable, normal, event, function, chunked
    ) -> None:
        # 25 January to 5 February: 7 days in January, 5 days in February.
        spell = ("2001-01-25", "2001-02-05")
        default, _ = _spell_index(
            name, variable, normal, event, function, spell, "month", chunked, False
        )
        split, _ = _spell_index(
            name, variable, normal, event, function, spell, "month", chunked, True
        )
        assert default[0] == 12
        assert default[1] == 0
        assert split[0] == 7
        assert split[1] == 0

    def test_a_spell_inside_a_period_is_not_changed(
        self, name, variable, normal, event, function, chunked
    ) -> None:
        spell = ("2001-03-10", "2001-03-19")
        default, _ = _spell_index(
            name, variable, normal, event, function, spell, "year", chunked, False
        )
        split, _ = _spell_index(
            name, variable, normal, event, function, spell, "year", chunked, True
        )
        np.testing.assert_array_equal(default, [10, 0])
        np.testing.assert_array_equal(split, default)


def test_sum_of_spell_lengths_honours_the_option() -> None:
    source = _cube("tasmax", 10.0, 20.0, "2001-12-28", "2002-01-06")
    kwargs = {
        "in_files": source,
        "threshold": "> 15 degC",
        "min_spell_length": 6,
        "out_file": None,
        "completeness": "none",
    }
    default = icclim.sum_of_spell_lengths(**kwargs)
    split = icclim.sum_of_spell_lengths(**kwargs, **{OPTION: True})
    name = next(iter(default.data_vars))
    np.testing.assert_array_equal(default[name].isel(x=0).values, [10, 0])
    np.testing.assert_array_equal(split[name].isel(x=0).values, [0, 6])


def _public_functions() -> dict[str, object]:
    found = {}
    for prefix, module in (("icclim", icclim), ("icclim.dcsc", icclim.dcsc)):
        for attr in dir(module):
            fun = getattr(module, attr)
            if inspect.isfunction(fun) and OPTION in inspect.signature(fun).parameters:
                found[f"{prefix}.{attr}"] = fun
    return found


# Indices and generic functions whose result depends on runs of consecutive days.
RUN_BASED = {
    "icclim.cdd",
    "icclim.cwd",
    "icclim.cfd",
    "icclim.csu",
    "icclim.csdi",
    "icclim.wsdi",
    "icclim.max_consecutive_occurrence",
    "icclim.sum_of_spell_lengths",
    "icclim.dcsc.pxcdd",
    "icclim.dcsc.pxcwd",
    "icclim.dcsc.txhwd",
    "icclim.dcsc.tncwd",
}


def test_the_option_is_exposed_by_all_run_based_functions_and_only_by_them() -> None:
    assert set(_public_functions()) == RUN_BASED


# name, variable, units, normal, event, threshold (generic functions), extra kwargs
AUDIT = {
    "icclim.cdd": ("pr", "mm/day", 5.0, 0.0, None, {}),
    "icclim.cwd": ("pr", "mm/day", 0.0, 5.0, None, {}),
    "icclim.cfd": ("tn", "degC", 1.0, -1.0, None, {}),
    "icclim.csu": ("tx", "degC", 0.0, 30.0, None, {}),
    "icclim.dcsc.pxcdd": ("pr", "mm/day", 5.0, 0.0, None, {}),
    "icclim.dcsc.pxcwd": ("pr", "mm/day", 0.0, 5.0, None, {}),
    "icclim.max_consecutive_occurrence": (
        "tasmax",
        "degC",
        0.0,
        30.0,
        "> 25 degC",
        {},
    ),
    "icclim.sum_of_spell_lengths": (
        "tasmax",
        "degC",
        0.0,
        30.0,
        "> 25 degC",
        {"min_spell_length": 6},
    ),
}


@pytest.mark.parametrize("path", sorted(AUDIT))
def test_the_option_changes_the_result_of_each_function_in_a_boundary_case(
    path: str,
) -> None:
    variable, units, normal, event, threshold, extra = AUDIT[path]
    source = _cube(variable, normal, event, "2001-12-28", "2002-01-06")
    source.attrs["units"] = units
    function = _public_functions()[path]
    kwargs = {"out_file": None, "completeness": "none", **extra}
    if threshold:
        kwargs["threshold"] = threshold
    default = function(source, **kwargs, run_index="first")
    split = function(source, **kwargs, **{OPTION: True})
    name = next(iter(default.data_vars))
    a = default[name].isel(x=0).values
    b = split[name].isel(x=0).values
    assert not np.array_equal(a, b), (path, a, b)
    # Cut at 2001-12-31: pieces of 4 and 6 days. Pieces below 6 days are dropped
    # by the spell-length function only.
    if path == "icclim.sum_of_spell_lengths":
        np.testing.assert_array_equal(b, [0, 6])
    else:
        np.testing.assert_array_equal(b, [4, 6])


@pytest.mark.parametrize(
    ("name", "variable", "normal", "event"),
    [("WSDI", "tasmax", 10.0, 20.0), ("CSDI", "tasmin", 10.0, 0.0)],
)
def test_icclim_index_honours_the_option_for_wsdi_and_csdi(
    name: str, variable: str, normal: float, event: float
) -> None:
    source = _with_base(
        _cube(variable, normal, event, "2001-12-28", "2002-01-06"), normal
    )
    values = {}
    for split in (False, True):
        values[split] = (
            icclim.index(
                index_name=name,
                in_files=source,
                base_period_time_range=BASE,
                time_range=("2001-01-01", "2002-12-31"),
                out_file=None,
                completeness="none",
                **{OPTION: split},
            )[name]
            .isel(x=0)
            .compute()
            .values
        )
    np.testing.assert_array_equal(values[False], [10, 0])
    np.testing.assert_array_equal(values[True], [0, 6])

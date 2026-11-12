"""
Run attribution for the periods that no run starts or ends in (issue #580).

With ``run_index="first"`` or ``"last"`` a run is attributed whole to the period where
it starts or ends. A period without any event gets 0. A period that is wholly
traversed by one continuous run, which is attributed to another period, is not
reported: its value is missing (NaN). With ``split_runs_at_period_boundary=True`` the
runs are cut at the boundaries and every period gets a value.

The reference calculation below applies this rule day by day, in plain Python, without
icclim or xclim.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.generic import functions
from icclim.threshold.factory import build_threshold


@dataclass(frozen=True)
class RunIndex:
    name: str
    variable: str
    units: str
    normal: float
    event: float


INDICES = [
    RunIndex("CDD", "pr", "mm/day", 5.0, 0.0),
    RunIndex("CFD", "tn", "degC", 1.0, -1.0),
]
INDEX_IDS = [i.name for i in INDICES]
MODES = [
    ("first", False),
    ("last", False),
    ("last", True),
]
MODE_IDS = ["first", "last", "split"]
TIME = pd.date_range("2001-01-01", "2003-12-31")  # three years, 1095 days
SLICES = ["year", "month"]


def _period_keys(time: pd.DatetimeIndex, slice_mode: str) -> list[tuple[int, ...]]:
    if slice_mode == "year":
        return [(d.year,) for d in time]
    return [(d.year, d.month) for d in time]


def _runs(events: np.ndarray) -> list[tuple[int, int]]:
    """First and last day of each maximal sequence of event days."""
    runs = []
    start = None
    for day in range(len(events) + 1):
        if day < len(events) and events[day]:
            if start is None:
                start = day
        elif start is not None:
            runs.append((start, day - 1))
            start = None
    return runs


def _reference(events: np.ndarray, time: pd.DatetimeIndex, slice_mode: str, mode: str):
    """
    Value of each period, from the rule of the run attribution.

    ``mode`` is "first", "last" or "split". A run is a maximal sequence of event days.
    It is attributed whole to the period of its first (or last) day, or cut at the
    boundaries of the periods when split. A period that no run is attributed to gets 0,
    except when every day of the period is an event day: the run that traverses it is
    attributed to another period and the value is missing.
    """
    keys = _period_keys(time, slice_mode)
    periods = sorted(set(keys))
    result = dict.fromkeys(periods, 0.0)
    for start, end in _runs(events):
        if mode == "split":
            for key in periods:
                days = [d for d in range(start, end + 1) if keys[d] == key]
                result[key] = max(result[key], len(days))
        else:
            key = keys[start] if mode == "first" else keys[end]
            result[key] = max(result[key], end - start + 1)
    if mode != "split":
        for key in periods:
            whole = all(events[d] for d in range(len(keys)) if keys[d] == key)
            if whole and result[key] == 0:
                result[key] = np.nan
    return np.array([result[key] for key in periods])


def _series(index: RunIndex, events: np.ndarray, chunked: bool) -> xr.DataArray:
    values = np.where(events, index.event, index.normal)
    source = xr.DataArray(
        values,
        dims="time",
        coords={"time": TIME},
        name=index.variable,
        attrs={"units": index.units},
    )
    return source.chunk({"time": 100}) if chunked else source


def _compute(index: RunIndex, source, slice_mode: str, run_index: str, split: bool):
    return getattr(icclim, index.name.lower())(
        source,
        slice_mode=slice_mode,
        out_file=None,
        completeness="none",
        run_index=run_index,
        split_runs_at_period_boundary=split,
    )[index.name].compute()


def _events(spells: list[tuple[str, str]]) -> np.ndarray:
    time = TIME
    events = np.zeros(len(time), dtype=bool)
    for first, last in spells:
        events |= np.asarray(time >= first) & np.asarray(time <= last)
    return events


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("slice_mode", SLICES)
@pytest.mark.parametrize(("run_index", "split"), MODES, ids=MODE_IDS)
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_a_period_without_any_event_is_zero_not_missing(
    index: RunIndex, run_index: str, split: bool, slice_mode: str, chunked: bool
) -> None:
    source = _series(index, np.zeros(len(TIME), dtype=bool), chunked)
    actual = _compute(index, source, slice_mode, run_index, split)
    assert actual.size == (3 if slice_mode == "year" else 36)
    np.testing.assert_array_equal(actual.values, np.zeros(actual.size))


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
class TestThreeYearRun:
    """One continuous run from 2001-01-01 to 2003-12-31 (1095 days)."""

    def test_first_reports_the_run_in_the_first_year_only(
        self, index: RunIndex, chunked: bool
    ) -> None:
        source = _series(index, np.ones(len(TIME), dtype=bool), chunked)
        actual = _compute(index, source, "year", "first", False)
        np.testing.assert_array_equal(actual.values, [1095, np.nan, np.nan])

    def test_last_reports_the_run_in_the_last_year_only(
        self, index: RunIndex, chunked: bool
    ) -> None:
        source = _series(index, np.ones(len(TIME), dtype=bool), chunked)
        actual = _compute(index, source, "year", "last", False)
        np.testing.assert_array_equal(actual.values, [np.nan, np.nan, 1095])

    def test_split_gives_a_value_to_every_year(
        self, index: RunIndex, chunked: bool
    ) -> None:
        source = _series(index, np.ones(len(TIME), dtype=bool), chunked)
        actual = _compute(index, source, "year", "last", True)
        np.testing.assert_array_equal(actual.values, [365, 365, 365])

    def test_monthly_values(self, index: RunIndex, chunked: bool) -> None:
        source = _series(index, np.ones(len(TIME), dtype=bool), chunked)
        first = _compute(index, source, "month", "first", False).values
        last = _compute(index, source, "month", "last", False).values
        split = _compute(index, source, "month", "last", True).values
        assert first[0] == 1095
        assert np.isnan(first[1:]).all()
        assert last[-1] == 1095
        assert np.isnan(last[:-1]).all()
        np.testing.assert_array_equal(
            split, TIME.to_series().groupby([TIME.year, TIME.month]).size().values
        )


# Spells chosen so that some periods are wholly traversed, some are partly, and one
# run ends exactly at the end of a year.
SPELLS = {
    "two years": [("2001-10-01", "2003-03-13")],
    "two runs": [("2001-03-01", "2002-12-31"), ("2003-02-01", "2003-02-10")],
    "starts on 1 January": [("2002-01-01", "2002-12-31"), ("2003-06-01", "2003-06-20")],
}


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("slice_mode", SLICES)
@pytest.mark.parametrize(("run_index", "split"), MODES, ids=MODE_IDS)
@pytest.mark.parametrize("spells", SPELLS.values(), ids=SPELLS.keys())
@pytest.mark.parametrize("index", INDICES, ids=INDEX_IDS)
def test_values_follow_the_reference_calculation(
    index: RunIndex,
    spells: list[tuple[str, str]],
    run_index: str,
    split: bool,
    slice_mode: str,
    chunked: bool,
) -> None:
    events = _events(spells)
    actual = _compute(
        index, _series(index, events, chunked), slice_mode, run_index, split
    )
    mode = "split" if split else run_index
    expected = _reference(events, TIME, slice_mode, mode)
    np.testing.assert_array_equal(actual.values, expected)


def test_a_value_can_exceed_the_length_of_its_period() -> None:
    index = INDICES[0]
    events = _events([("2001-10-01", "2003-03-13")])
    source = _series(index, events, chunked=False)
    first = _compute(index, source, "year", "first", False).values
    last = _compute(index, source, "year", "last", False).values
    year_length = 365
    assert first[0] == 529
    assert last[2] == 529
    assert first[0] > year_length


def _bootstrap_case() -> tuple[xr.DataArray, object]:
    """
    Random series with one 736-day warm spell from 2044-01-01 to 2046-01-05.

    The days around the spell are cold, so it is one run. 2044 and 2045 are wholly
    traversed by it.
    """
    time = pd.date_range("2042-01-01", "2047-12-31")
    values = np.random.default_rng(3).normal(0, 1, time.size)
    spell = (time >= "2044-01-01") & (time <= "2046-01-05")
    values[spell] = 10.0
    values[(time == "2043-12-31") | (time == "2046-01-06")] = -10.0
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
def test_whole_period_on_the_bootstrap_spell_mask_path(
    mode: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, threshold = _bootstrap_case()
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

    def run(run_index: str, split: bool) -> np.ndarray:
        return (
            icclim.max_consecutive_occurrence(
                source,
                threshold=threshold,
                slice_mode="year",
                out_file=None,
                completeness="none",
                run_index=run_index,
                split_runs_at_period_boundary=split,
            )["max_consecutive_occurrence"]
            .compute()
            .values
        )

    first, last, split = run("first", False), run("last", False), run("last", True)
    # Years 2042 to 2047: the run starts on 2044-01-01 and ends on 2046-01-05.
    assert first[2] == 736
    assert np.isnan(first[3])  # 2045 is wholly traversed
    assert last[4] == 736
    assert np.isnan(last[2])  # 2044 is wholly traversed
    assert np.isnan(last[3])
    assert split[2] == 366
    assert split[3] == 365
    assert split[4] >= 5
    if mode is None:
        assert any(mask is not None for mask in masks)

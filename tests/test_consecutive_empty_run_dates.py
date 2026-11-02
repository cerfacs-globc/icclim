"""Regression tests for #524: empty consecutive runs must not report event dates."""

import numpy as np
import pandas as pd
import xarray as xr

import icclim


def _daily(
    values: np.ndarray | list[float],
    start: str,
    *,
    units: str,
    calendar: str | None = None,
) -> xr.DataArray:
    if calendar is None:
        time = pd.date_range(start, periods=len(values), freq="D")
    else:
        time = xr.date_range(
            start,
            periods=len(values),
            freq="D",
            calendar=calendar,
            use_cftime=True,
        )
    return xr.DataArray(
        np.asarray(values, dtype=float),
        dims="time",
        coords={"time": time},
        attrs={"units": units},
        name="input",
    )


def test_max_consecutive_no_event_has_missing_event_dates() -> None:
    data = _daily(np.zeros(5), "2001-01-01", units="degC")

    result = icclim.max_consecutive_occurrence(
        in_files=data,
        threshold="> 1 degC",
        slice_mode="month",
        date_event=True,
        allow_missing_periods=True,
    ).compute()

    actual = result.max_consecutive_occurrence.isel(time=0)
    assert actual.item() == 0
    assert pd.isna(actual.event_date_start.item())
    assert pd.isna(actual.event_date_end.item())


def test_max_consecutive_with_event_keeps_event_dates() -> None:
    data = _daily([0, 2, 2, 0, 0], "2001-01-01", units="degC")

    result = icclim.max_consecutive_occurrence(
        in_files=data,
        threshold="> 1 degC",
        slice_mode="month",
        date_event=True,
        allow_missing_periods=True,
    ).compute()

    actual = result.max_consecutive_occurrence.isel(time=0)
    assert actual.item() == 2
    assert pd.Timestamp(actual.event_date_start.item()) == pd.Timestamp("2001-01-02")
    assert pd.Timestamp(actual.event_date_end.item()) == pd.Timestamp("2001-01-04")


def test_max_consecutive_mixed_periods_mask_only_empty_ones() -> None:
    values = np.zeros(59)
    values[40:43] = 5  # Feb 10-12 only; January has no event
    data = _daily(values, "2001-01-01", units="degC")

    result = icclim.max_consecutive_occurrence(
        in_files=data,
        threshold="> 1 degC",
        slice_mode="month",
        date_event=True,
        allow_missing_periods=True,
    ).compute()

    jan = result.max_consecutive_occurrence.isel(time=0)
    feb = result.max_consecutive_occurrence.isel(time=1)
    assert jan.item() == 0
    assert pd.isna(jan.event_date_start.item())
    assert feb.item() == 3
    assert pd.Timestamp(feb.event_date_start.item()) == pd.Timestamp("2001-02-10")

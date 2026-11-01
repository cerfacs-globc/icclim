"""Regression tests for ONDJFM percentage denominators."""

import numpy as np
import pandas as pd
import xarray as xr

import icclim


def _full_ondjfm(start: str, days: int) -> float:
    data = xr.DataArray(
        np.ones(days),
        dims="time",
        coords={"time": pd.date_range(start, periods=days)},
        attrs={"units": "degC"},
    )
    result = icclim.count_occurrences(
        data,
        threshold="> 0 degC",
        slice_mode="ONDJFM",
        out_unit="%",
        allow_missing_periods=True,
    )
    return float(result.count_occurrences.compute().item())


def test_count_occurrences_ondjfm_uses_february_year_for_denominator() -> None:
    non_leap = _full_ondjfm("1998-10-01", 182)
    leap = _full_ondjfm("1999-10-01", 183)

    assert leap == non_leap

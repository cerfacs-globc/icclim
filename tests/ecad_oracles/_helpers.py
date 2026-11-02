"""Independent test data and numerical oracles for ECAD indices."""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr
from scipy.stats import gamma, norm


def _first_run(mask: np.ndarray, length: int) -> int | None:
    """Return the first start index of a true run without icclim/xclim code."""
    count = 0
    for index, value in enumerate(mask):
        count = count + 1 if value else 0
        if count == length:
            return index - length + 1
    return None


def gsl_oracle(time: xr.DataArray, values_c: np.ndarray) -> np.ndarray:
    """Implement ATBD v11 GSL: six days >5 C to six days <5 C after July 1."""
    years = np.unique(time.dt.year.values)
    result = np.full((len(years), *values_c.shape[1:]), np.nan)
    month = time.dt.month.values
    day = time.dt.day.values
    year_values = time.dt.year.values
    for year_index, year in enumerate(years):
        in_year = year_values == year
        after_july_1 = (month > 7) | ((month == 7) & (day > 1))
        for cell in np.ndindex(values_c.shape[1:]):
            series = values_c[(in_year, *cell)]
            if np.isnan(series).all():
                continue
            start = _first_run(np.isfinite(series) & (series > 5), 6)
            eligible_end = after_july_1[in_year]
            end = _first_run(np.isfinite(series) & (series < 5) & eligible_end, 6)
            if start is not None and end is not None and end >= start:
                result[(year_index, *cell)] = end - start
    return result


def make_gsl_cube(
    calendar: str,
    units: str,
    *,
    equality_probe: bool = False,
    isolated_missing: bool = False,
) -> xr.DataArray:
    """Create three hand-checkable years on a 2x2 grid for four CF calendars."""
    end = "2003-12-30" if calendar == "360_day" else "2003-12-31"
    time = xr.date_range(
        "2001-01-01",
        end,
        freq="D",
        calendar=calendar,
        use_cftime=calendar != "standard",
    )
    month, day = time.month, time.day
    values = np.zeros((len(time), 2, 2), dtype=float)
    starts = ((1, 10), (2, 1), (3, 1), (1, 20))
    ends = ((10, 1), (9, 15), (11, 1), (10, 20))
    for cell, (start, end_date) in enumerate(zip(starts, ends, strict=True)):
        row, col = divmod(cell, 2)
        warm = ((month > start[0]) | ((month == start[0]) & (day >= start[1]))) & (
            (month < end_date[0]) | ((month == end_date[0]) & (day < end_date[1]))
        )
        values[warm, row, col] = 10
    values[:, 1, 1] = np.nan
    if isolated_missing:
        values[(month == 6) & (day == 15), 1, 0] = np.nan
    if equality_probe:
        values[(month == 1) & (day <= 6), 0, 0] = 5
    if units == "K":
        values = values + 273.15
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="tg",
        attrs={"units": units, "standard_name": "air_temperature"},
    )


def make_spi_cube(units: str = "mm/day") -> xr.DataArray:
    """Create a deterministic 40-year positive precipitation cube."""
    time = pd.date_range("1981-01-01", "2020-12-31", freq="D")
    rng = np.random.default_rng(20261102)
    values = rng.gamma(shape=2.5, scale=1.7, size=(len(time), 2, 2))
    seasonal = 1.0 + 0.35 * np.sin(
        2 * np.pi * (time.dayofyear.to_numpy() - 20) / 365.25
    )
    values *= seasonal[:, None, None]
    values *= np.array([[0.7, 1.0], [1.3, 1.8]])[None, :, :]
    if units == "kg m-2 s-1":
        values /= 86400
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="pr",
        attrs={"units": units, "standard_name": "precipitation_flux"},
    )


def spi_gamma_oracle(pr: xr.DataArray, window: int) -> np.ndarray:
    """Fit scipy gamma distributions by ending month and transform their CDFs.

    This independently follows Guttman-style SPI using maximum-likelihood gamma
    fits with location fixed at zero. icclim uses an approximate fit, so tests
    allow 0.25 SPI units; the two methods agree much more closely away from tails.
    """
    values = pr.values * (86400 if pr.attrs["units"] == "kg m-2 s-1" else 1)
    monthly_index = pd.DatetimeIndex(pr.time.values).to_period("M").to_timestamp()
    unique_months = monthly_index.unique()
    result = np.full((len(unique_months), *values.shape[1:]), np.nan)
    calibration = (unique_months >= "1981-01-01") & (unique_months <= "2010-12-01")
    for cell in np.ndindex(values.shape[1:]):
        daily = pd.Series(
            values[(slice(None), *cell)], index=pd.DatetimeIndex(pr.time.values)
        )
        accumulated = daily.resample("MS").sum().rolling(window).sum()
        for month in range(1, 13):
            month_mask = unique_months.month == month
            sample = accumulated[calibration & month_mask].dropna().to_numpy()
            shape, _, scale = gamma.fit(sample, floc=0)
            probabilities = gamma.cdf(
                accumulated[month_mask], shape, loc=0, scale=scale
            )
            result[(month_mask, *cell)] = norm.ppf(probabilities)
    return result

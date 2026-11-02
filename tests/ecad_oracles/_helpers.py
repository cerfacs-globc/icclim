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


def make_percentile_temperature_cube(units: str = "degC") -> xr.Dataset:
    """Create five noleap years of correlated TG/TN/TX on a 2x2 grid."""
    time = xr.date_range(
        "2001-01-01",
        "2005-12-31",
        freq="D",
        calendar="noleap",
        use_cftime=True,
    )
    rng = np.random.default_rng(6402)
    doy = np.asarray([value.dayofyr for value in time])
    year = np.asarray([value.year for value in time])
    seasonal = 12 + 11 * np.sin(2 * np.pi * (doy - 80) / 365)
    noise = rng.normal(0, 2.2, size=(len(time), 2, 2))
    offsets = np.array([[-1.5, 0.0], [1.0, 2.5]])
    core = seasonal[:, None, None] + offsets[None, :, :] + noise
    study = year >= 2004
    core[study] = seasonal[study, None, None] + offsets[None, :, :]
    month = np.asarray([value.month for value in time])
    day = np.asarray([value.day for value in time])
    high_2004 = (year == 2004) & ((month == 6) | ((month == 7) & (day <= 15)))
    low_2004 = (year == 2004) & ((month == 1) | ((month == 2) & (day <= 15)))
    high_2005 = (year == 2005) & (month >= 8) & (month <= 9)
    low_2005 = (year == 2005) & (month >= 3) & (month <= 4)
    core[high_2004 | high_2005] += 10
    core[low_2004 | low_2005] -= 10
    data = {"tg": core, "tn": core - 5, "tx": core + 5}
    if units == "K":
        data = {name: values + 273.15 for name, values in data.items()}
    return xr.Dataset(
        {
            name: xr.DataArray(
                values,
                dims=("time", "lat", "lon"),
                attrs={"units": units},
            )
            for name, values in data.items()
        },
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
    )


def doy_percentile(
    time: xr.DataArray,
    values: np.ndarray,
    percentile: float,
    base_years: tuple[int, ...] = (2001, 2002, 2003),
    duplicated_year: int | None = None,
) -> np.ndarray:
    """Derive five-day-window calendar-day percentiles using ATBD type-8 quantiles."""
    years = time.dt.year.values
    doy = time.dt.dayofyear.values
    base = np.isin(years, base_years)
    result = np.full_like(values, np.nan, dtype=float)
    for target_day in range(1, 366):
        distance = np.minimum((doy - target_day) % 365, (target_day - doy) % 365)
        sample_mask = base & (distance <= 2)
        sample = values[sample_mask]
        if duplicated_year is not None:
            duplicate = values[(years == duplicated_year) & (distance <= 2)]
            sample = np.concatenate([sample, duplicate], axis=0)
        result[doy == target_day] = np.nanquantile(
            sample,
            percentile / 100,
            axis=0,
            method="median_unbiased",
        )
    return result


def annual_event_count(time: xr.DataArray, event: np.ndarray) -> np.ndarray:
    """Count true daily events independently for each calendar year."""
    years = np.unique(time.dt.year.values)
    return np.stack([np.sum(event[time.dt.year.values == year], axis=0) for year in years])


def annual_spell_count(time: xr.DataArray, event: np.ndarray, minimum: int = 6) -> np.ndarray:
    """Count all days belonging to within-year runs of at least ``minimum`` days."""
    years = np.unique(time.dt.year.values)
    result = np.zeros((len(years), *event.shape[1:]), dtype=int)
    for year_index, year in enumerate(years):
        yearly = event[time.dt.year.values == year]
        for cell in np.ndindex(event.shape[1:]):
            run = 0
            total = 0
            for value in yearly[(slice(None), *cell)]:
                if value:
                    run += 1
                else:
                    total += run if run >= minimum else 0
                    run = 0
            result[(year_index, *cell)] = total + (run if run >= minimum else 0)
    return result


def bootstrap_temperature_count(
    time: xr.DataArray,
    values: np.ndarray,
    percentile: float,
    operator: str,
) -> np.ndarray:
    """Implement the ATBD leave-one-year-out bootstrap for annual counts."""
    base_years = (2001, 2002, 2003)
    years = np.unique(time.dt.year.values)
    normal_threshold = doy_percentile(time, values, percentile)
    result = np.empty((len(years), *values.shape[1:]), dtype=float)
    compare = np.greater if operator == ">" else np.less
    for index, year in enumerate(years):
        target = time.dt.year.values == year
        if year not in base_years:
            result[index] = np.sum(compare(values[target], normal_threshold[target]), axis=0)
            continue
        estimates = []
        remaining = tuple(item for item in base_years if item != year)
        for duplicated in remaining:
            threshold = doy_percentile(
                time,
                values,
                percentile,
                base_years=remaining,
                duplicated_year=duplicated,
            )
            estimates.append(np.sum(compare(values[target], threshold[target]), axis=0))
        result[index] = np.mean(estimates, axis=0)
    return result


def make_bootstrap_temperature_series() -> xr.DataArray:
    """Create the ATBD 30-year base period plus one independent study year."""
    time = xr.date_range(
        "1961-01-01",
        "1991-12-31",
        freq="D",
        calendar="noleap",
        use_cftime=True,
    )
    rng = np.random.default_rng(9)
    doy = np.asarray([value.dayofyr for value in time])
    year = np.asarray([value.year for value in time])
    values = (
        20
        + 10 * np.sin(2 * np.pi * (doy - 80) / 365)
        + rng.normal(0, 2, len(time))
        + 0.03 * (year - 1961)
    )
    return xr.DataArray(
        values,
        dims="time",
        coords={"time": time},
        name="tx",
        attrs={"units": "degC"},
    )


def bootstrap_temperature_year(
    source: xr.DataArray,
    target_year: int,
    percentile: float,
) -> float:
    """Average the 29 ATBD replicate-and-count estimates for one base year."""
    base_years = tuple(range(1961, 1991))
    remaining = tuple(year for year in base_years if year != target_year)
    target = source.time.dt.year.values == target_year
    estimates = []
    for duplicated in remaining:
        threshold = doy_percentile(
            source.time,
            source.values,
            percentile,
            base_years=remaining,
            duplicated_year=duplicated,
        )
        estimates.append(np.sum(source.values[target] > threshold[target]))
    return float(np.mean(estimates))


def make_percentile_precip_cube(units: str = "mm/day") -> xr.DataArray:
    """Create five years with dry, floor-equal, and heavy wet days."""
    time = pd.date_range("2001-01-01", "2005-12-31", freq="D")
    rng = np.random.default_rng(7525)
    values = rng.gamma(1.8, 4.0, size=(len(time), 2, 2))
    values[rng.random(values.shape) < 0.25] = 0
    values[::17] = 1
    values *= np.array([[0.8, 1.0], [1.2, 1.5]])[None, :, :]
    values[::17] = 1
    if units == "kg m-2 s-1":
        values /= 86400
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="pr",
        attrs={"units": units},
    )


def precipitation_percentile_oracle(
    pr: xr.DataArray,
    percentile: float,
    *,
    fraction: bool,
) -> np.ndarray:
    """Apply ATBD wet-day percentile counts or fractions by calendar year."""
    values = pr.values * (86400 if pr.attrs["units"] == "kg m-2 s-1" else 1)
    years = pd.DatetimeIndex(pr.time.values).year
    base = (years >= 2001) & (years <= 2003)
    threshold = np.nanquantile(
        np.where(values[base] >= 1, values[base], np.nan),
        percentile / 100,
        axis=0,
        method="median_unbiased",
    )
    result = []
    for year in np.unique(years):
        yearly = values[years == year]
        exceedance = yearly > threshold
        if fraction:
            numerator = np.sum(np.where(exceedance, yearly, 0), axis=0)
            denominator = np.sum(np.where(yearly >= 1, yearly, 0), axis=0)
            result.append(100 * numerator / denominator)
        else:
            result.append(np.sum(exceedance, axis=0))
    return np.stack(result)

"""All ECA&D functions. Each function wraps its xclim equivalent functions adding icclim
metadata to it.
"""
from __future__ import annotations

import re
from typing import Callable
from warnings import warn

import numpy as np
import xarray as xr
import xclim.core.utils
from xarray import DataArray
from xclim import atmos
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to
from xclim.core.utils import PercentileDataArray

from icclim.models.cf_calendar import CfCalendar
from icclim.models.climate_variable import ClimateVariable
from icclim.models.constants import IN_BASE_IDENTIFIER, PERCENTILES_COORD
from icclim.models.frequency import Frequency
from icclim.models.quantile_interpolation import QuantileInterpolation


def _can_run_bootstrap(cf_var: ClimateVariable) -> bool:
    """Avoid bootstrapping if there is one single year overlapping
    or no year overlapping or all year overlapping.
    """
    study_years = np.unique(cf_var.study_da.indexes.get("time").year)
    overlapping_years = np.unique(
        cf_var.study_da.sel(time=_get_ref_period_slice(cf_var.reference_da))
        .indexes.get("time")
        .year
    )
    return 1 < len(overlapping_years) < len(study_years)


def _get_ref_period_slice(da: DataArray) -> slice:
    time_length = len(da.time)
    return slice(*da.time[0 :: time_length - 1].dt.strftime("%Y-%m-%d").values)


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    if sampling_freq == Frequency.MONTH:
        da = da / da.time.dt.daysinmonth * 100
    elif sampling_freq == Frequency.YEAR:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 366
        coef[{"time": ~leap_years}] = 365
        da = da / coef
    elif sampling_freq == Frequency.AMJJAS:
        da = da / 183
    elif sampling_freq == Frequency.ONDJFM:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 183
        coef[{"time": ~leap_years}] = 182
        da = da / coef
    elif sampling_freq == Frequency.DJF:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 91
        coef[{"time": ~leap_years}] = 90
        da = da / coef
    elif sampling_freq in [Frequency.MAM, Frequency.JJA]:
        da = da / 92
    elif sampling_freq == Frequency.SON:
        da = da / 91
    else:
        # TODO improve this for custom resampling
        warn(
            "For now, '%' unit can only be used when `slice_mode` is one of: "
            "{MONTH, YEAR, AMJJAS, ONDJFM, DJF, MAM, JJA, SON}."
        )
        return da
    da.attrs["units"] = "1"
    return da


def _is_leap_year(da: DataArray) -> np.ndarray:
    time_index = da.indexes.get("time")
    if isinstance(time_index, xr.CFTimeIndex):
        return CfCalendar.lookup(time_index.calendar).is_leap(da.time.dt.year)
    else:
        return da.time.dt.is_leap_year


def _add_bootstrap_meta(result: DataArray, per: DataArray) -> DataArray:
    result.attrs[IN_BASE_IDENTIFIER] = per.climatology_bounds
    return result


def _compute_percentile_doy(
    cf_var: ClimateVariable,
    percentile: float,
    window: int = 5,
    interpolation=QuantileInterpolation.MEDIAN_UNBIASED,
    callback: Callable = None,
) -> (DataArray, bool):
    if PercentileDataArray.is_compatible(cf_var.reference_da):
        per = cf_var.reference_da
        run_bootstrap = False
    else:
        per = percentile_doy(
            cf_var.reference_da,
            window,
            percentile,
            alpha=interpolation.alpha,
            beta=interpolation.beta,
        ).compute()  # dask "optimization"
        run_bootstrap = _can_run_bootstrap(cf_var)
    if callback is not None:
        callback(50)
    return per, run_bootstrap


def _compute_precip_percentile_over_period(
    cf_var: ClimateVariable, interpolation: QuantileInterpolation, percentiles: float
) -> DataArray:
    if PercentileDataArray.is_compatible(cf_var.reference_da):
        return cf_var.reference_da
    else:
        base_wet_days = _filter_in_wet_days(cf_var.reference_da, dry_day_value=np.nan)
    return xr.apply_ufunc(
        xclim.core.utils.calc_perc,
        base_wet_days,
        input_core_dims=[["time"]],
        output_core_dims=[[PERCENTILES_COORD]],
        kwargs=dict(
            percentiles=[percentiles],
            alpha=interpolation.alpha,
            beta=interpolation.beta,
        ),
        dask="parallelized",
        output_dtypes=[base_wet_days.dtype],
        dask_gufunc_kwargs=dict(output_sizes={PERCENTILES_COORD: len([percentiles])}),
    )


def _filter_in_wet_days(da: DataArray, dry_day_value: float):
    """Turns non wet days to NaN. dry_day_value should be NaN or 0."""
    precip = convert_units_to(da, "mm/d")
    return precip.where(precip > 1, dry_day_value)


def _compute_threshold_index(
    da: DataArray,
    threshold: float,
    freq: Frequency,
    xclim_index_fun: Callable,
) -> DataArray:
    return xclim_index_fun(
        da, thresh=f"{threshold} °C", **freq.build_frequency_kwargs()
    )


def _compute_spell_duration(
    cf_var: ClimateVariable,
    freq: Frequency,
    per_window: int,
    per_thresh: float,
    per_interpolation: QuantileInterpolation,
    min_spell_duration: int,
    save_percentile: bool,
    callback: Callable,
    xclim_index_fun: Callable,
) -> tuple[DataArray, DataArray | None]:
    per, run_bootstrap = _compute_percentile_doy(
        cf_var,
        per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    result = xclim_index_fun(
        cf_var.study_da,
        per,
        window=min_spell_duration,
        **freq.build_frequency_kwargs(),
        bootstrap=run_bootstrap,
    )
    result = result.squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if save_percentile:
        return result, per
    result.attrs["description"] = re.sub(
        r"\s\w+th\spercentile",
        f" {per_thresh}th percentile",
        result.attrs.get("description"),
    )
    return result, None


def compute_compound_index(
    tas: ClimateVariable,
    pr: ClimateVariable,
    freq: Frequency,
    tas_per_thresh: int,
    pr_per_thresh: int,
    per_window: int,
    per_interpolation: QuantileInterpolation,
    save_percentile: bool,
    callback: Callable,
    xclim_index_fun: Callable,
) -> DataArray:
    """CD, CW, WD, WW

    Parameters
    ----------
    tas : ClimateVariable
        CfVariable of tas variable.
    pr : ClimateVariable
        DataArray of pr variable.
    freq : Frequency
        Sampling frequency of the output.
    save_percentile : bool
        Flag to include coordinate variable including the computed percentiles.
        Does not contain the bootstrapped percentiles.
        Default is False.
    callback : Callable
        callback receiving an integer, may serve as a loading bar.

    Returns
    -------
        If save_percentile is True, returns a Tuple of index_result,
        computed_percentiles. Otherwise, returns the index_result
    """
    tas_per, _ = _compute_percentile_doy(
        tas,
        tas_per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    tas_per = tas_per.squeeze(PERCENTILES_COORD, drop=True)
    pr.reference_da = _filter_in_wet_days(pr.reference_da, dry_day_value=np.NAN)
    pr.study_da = _filter_in_wet_days(pr.study_da, dry_day_value=0)
    pr_per, _ = _compute_percentile_doy(
        pr,
        pr_per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    pr_per = pr_per.squeeze(PERCENTILES_COORD, drop=True)
    result = xclim_index_fun(
        tas.study_da, pr.study_da, tas_per, pr_per, **freq.build_frequency_kwargs()
    )
    if save_percentile:
        # FIXME, not consistent with other percentile based indices
        #        We should probably return a Tuple (res, [tas_per, pr_per])
        #        However, here the percentiles use the existing time dimension and not
        #        doy
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def _compute_rxxptot(
    pr: ClimateVariable,
    freq: Frequency,
    pr_per_thresh: float,
    per_interpolation: QuantileInterpolation,
    save_percentile: bool,
) -> tuple[DataArray, DataArray | None]:
    per = _compute_precip_percentile_over_period(pr, per_interpolation, pr_per_thresh)
    result = atmos.fraction_over_precip_thresh(
        pr.study_da,
        per,
        thresh="1 mm/day",
        **freq.build_frequency_kwargs(),
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    result = result * 100
    result.attrs["units"] = "%"
    if save_percentile:
        return result, per
    return result, None


def _compute_rxxp(
    pr: ClimateVariable,
    freq: Frequency,
    pr_per_thresh: float,
    per_interpolation: QuantileInterpolation,
    save_percentile: bool,
    is_percent: bool,
) -> tuple[DataArray, DataArray | None]:
    per = _compute_precip_percentile_over_period(pr, per_interpolation, pr_per_thresh)
    result = atmos.days_over_precip_thresh(
        pr.study_da,
        per,
        thresh="1 mm/day",
        **freq.build_frequency_kwargs(),
        bootstrap=False,
    )
    result = result.squeeze(PERCENTILES_COORD, drop=True)
    if is_percent:
        result = _to_percent(result, freq)
    if save_percentile:
        return result, per
    return result, None


def _compute_temperature_percentile_index(
    cf_var: ClimateVariable,
    freq: Frequency,
    tas_per_thresh: int,
    per_window: int,
    per_interpolation: QuantileInterpolation,
    save_percentile: bool,
    is_percent: bool,
    callback: Callable,
    xclim_index_fun: Callable,
) -> tuple[DataArray, DataArray | None]:
    per, run_bootstrap = _compute_percentile_doy(
        cf_var,
        tas_per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    result = xclim_index_fun(
        cf_var.study_da,
        per,
        **freq.build_frequency_kwargs(),
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if is_percent:
        result = _to_percent(result, freq)
    if save_percentile:
        return result, per
    return result, None

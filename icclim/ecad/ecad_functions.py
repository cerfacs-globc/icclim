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
from xclim import atmos, land
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to
from xclim.core.utils import PercentileDataArray

from icclim.models.cf_calendar import CfCalendar
from icclim.models.cf_variable import CfVariable
from icclim.models.constants import IN_BASE_IDENTIFIER, PERCENTILES_COORD
from icclim.models.frequency import Frequency
from icclim.models.index_config import IndexConfig
from icclim.models.quantile_interpolation import QuantileInterpolation


def gd4(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tas.study_da,
        threshold=4.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.growing_degree_days,
    )


def cfd(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmin.study_da,
        threshold=0.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.consecutive_frost_days,
    )


def fd(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmin.study_da,
        threshold=0.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.frost_days,
    )


def hd17(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tas.study_da,
        threshold=17.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.heating_degree_days,
    )


def id(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmax.study_da,
        threshold=0.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.ice_days,
    )


def csdi(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 10 if config.threshold is None else config.threshold
    return _compute_spell_duration(
        cf_var=config.tasmin,
        freq=config.frequency,
        per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        min_spell_duration=6,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.cold_spell_duration_index,
    )


def tg10p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 10 if config.threshold is None else config.threshold
    return _compute_temperature_percentile_index(
        cf_var=config.tas,
        freq=config.frequency,
        tas_per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tg10p,
    )


def tn10p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 10 if config.threshold is None else config.threshold
    return _compute_temperature_percentile_index(
        cf_var=config.tasmin,
        freq=config.frequency,
        tas_per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tn10p,
    )


def tx10p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 10 if config.threshold is None else config.threshold
    return _compute_temperature_percentile_index(
        cf_var=config.tasmax,
        freq=config.frequency,
        tas_per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tx10p,
    )


def txn(config: IndexConfig) -> DataArray:
    result = atmos.tx_min(
        config.tasmax.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def tnn(config: IndexConfig) -> DataArray:
    result = atmos.tn_min(
        config.tasmin.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def cdd(config: IndexConfig) -> DataArray:
    result = atmos.maximum_consecutive_dry_days(
        config.pr.study_da,
        thresh="1.0 mm/day",
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def su(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmax.study_da,
        threshold=25.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.tx_days_above,
    )


def tr(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmin.study_da,
        threshold=20.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.tropical_nights,
    )


def wsdi(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 90 if config.threshold is None else config.threshold
    return _compute_spell_duration(
        cf_var=config.tasmax,
        freq=config.frequency,
        per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        min_spell_duration=6,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.warm_spell_duration_index,
    )


def tg90p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 90 if config.threshold is None else config.threshold
    return _compute_temperature_percentile_index(
        cf_var=config.tas,
        freq=config.frequency,
        tas_per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tg90p,
    )


def tn90p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 90 if config.threshold is None else config.threshold
    return _compute_temperature_percentile_index(
        cf_var=config.tasmin,
        freq=config.frequency,
        tas_per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tn90p,
    )


def tx90p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    thresh = 90 if config.threshold is None else config.threshold
    return _compute_temperature_percentile_index(
        cf_var=config.tasmax,
        freq=config.frequency,
        tas_per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tx90p,
    )


def txx(config: IndexConfig) -> DataArray:
    result = atmos.tx_max(
        config.tasmax.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def tnx(config: IndexConfig) -> DataArray:
    result = atmos.tn_max(
        config.tasmin.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def csu(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmax.study_da,
        threshold=25.0 if config.threshold is None else config.threshold,
        freq=config.frequency,
        xclim_index_fun=atmos.maximum_consecutive_warm_days,
    )


def prcptot(config: IndexConfig) -> DataArray:
    result = atmos.precip_accumulation(
        _filter_in_wet_days(config.pr.study_da, dry_day_value=0),
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def rr1(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.pr.study_da,
        thresh="1.0 mm/day",
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def sdii(config: IndexConfig) -> DataArray:
    result = atmos.daily_pr_intensity(
        config.pr.study_da,
        thresh="1.0 mm/day",
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def cwd(config: IndexConfig) -> DataArray:
    result = atmos.maximum_consecutive_wet_days(
        config.pr.study_da,
        thresh="1.0 mm/day",
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def r10mm(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.pr.study_da,
        thresh="10 mm/day",
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def r20mm(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.pr.study_da,
        thresh="20 mm/day",
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def rx1day(config: IndexConfig) -> DataArray:
    result = atmos.max_1day_precipitation_amount(
        config.pr.study_da, **config.frequency.build_frequency_kwargs()
    )
    return result


def rx5day(config: IndexConfig) -> DataArray:
    result = atmos.max_n_day_precipitation_amount(
        config.pr.study_da, window=5, **config.frequency.build_frequency_kwargs()
    )
    return result


def r75p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    return _compute_rxxp(
        pr=config.pr,
        freq=config.frequency,
        pr_per_thresh=75.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
    )


def r75ptot(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    return _compute_rxxptot(
        pr=config.pr,
        freq=config.frequency,
        pr_per_thresh=75.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
    )


def r95p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    return _compute_rxxp(
        pr=config.pr,
        freq=config.frequency,
        pr_per_thresh=95.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
    )


def r95ptot(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    return _compute_rxxptot(
        pr=config.pr,
        freq=config.frequency,
        pr_per_thresh=95.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
    )


def r99p(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    return _compute_rxxp(
        pr=config.pr,
        freq=config.frequency,
        pr_per_thresh=99.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
    )


def r99ptot(config: IndexConfig) -> tuple[DataArray, DataArray | None]:
    return _compute_rxxptot(
        pr=config.pr,
        freq=config.frequency,
        pr_per_thresh=99.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
    )


def sd(config: IndexConfig) -> DataArray:
    result = land.snow_depth(
        config.pr.study_da, **config.frequency.build_frequency_kwargs()
    )
    return result


def sd1(config: IndexConfig) -> DataArray:
    result = land.snow_cover_duration(
        config.pr.study_da, thresh="1 cm", **config.frequency.build_frequency_kwargs()
    )
    return result


def sd5cm(config: IndexConfig) -> DataArray:
    result = land.snow_cover_duration(
        config.pr.study_da, thresh="5 cm", **config.frequency.build_frequency_kwargs()
    )
    return result


def sd50cm(config: IndexConfig) -> DataArray:
    result = land.snow_cover_duration(
        config.pr.study_da, thresh="50 cm", **config.frequency.build_frequency_kwargs()
    )
    return result


def tg(config: IndexConfig) -> DataArray:
    result = atmos.tg_mean(
        config.tas.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def tn(config: IndexConfig) -> DataArray:
    result = atmos.tn_mean(
        config.tasmin.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def tx(config: IndexConfig) -> DataArray:
    result = atmos.tx_mean(
        config.tasmax.study_da, **config.frequency.build_frequency_kwargs()
    )
    result = convert_units_to(result, "°C")
    return result


def dtr(config: IndexConfig) -> DataArray:
    result = atmos.daily_temperature_range(
        tasmax=config.tasmax.study_da,
        tasmin=config.tasmin.study_da,
        **config.frequency.build_frequency_kwargs(),
    )
    result.attrs["units"] = "°C"
    return result


def etr(config: IndexConfig) -> DataArray:
    result = atmos.extreme_temperature_range(
        tasmax=config.tasmax.study_da,
        tasmin=config.tasmin.study_da,
        **config.frequency.build_frequency_kwargs(),
    )
    result.attrs["units"] = "°C"
    return result


def vdtr(config: IndexConfig) -> DataArray:
    result = atmos.daily_temperature_range_variability(
        tasmax=config.tasmax.study_da,
        tasmin=config.tasmin.study_da,
        **config.frequency.build_frequency_kwargs(),
    )
    result.attrs["units"] = "°C"
    return result


def cd(config: IndexConfig) -> DataArray:
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.frequency,
        tas_per_thresh=25,
        pr_per_thresh=25,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.cold_and_dry_days,
    )


def cw(config: IndexConfig) -> DataArray:
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.frequency,
        tas_per_thresh=25,
        pr_per_thresh=75,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.cold_and_wet_days,
    )


def wd(config: IndexConfig) -> DataArray:
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.frequency,
        tas_per_thresh=75,
        pr_per_thresh=25,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.warm_and_dry_days,
    )


def ww(config: IndexConfig) -> DataArray:
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.frequency,
        tas_per_thresh=75,
        pr_per_thresh=75,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.warm_and_wet_days,
    )


def _can_run_bootstrap(cf_var: CfVariable) -> bool:
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
    cf_var: CfVariable,
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
    cf_var: CfVariable, interpolation: QuantileInterpolation, percentiles: float
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
    result = xclim_index_fun(
        da, thresh=f"{threshold} °C", **freq.build_frequency_kwargs()
    )
    return result


def _compute_spell_duration(
    cf_var: CfVariable,
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
    tas: CfVariable,
    pr: CfVariable,
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
    tas : CfVariable
        CfVariable of tas variable.
    pr : CfVariable
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
        tas=tas.study_da,
        pr=pr.study_da,
        tas_per=tas_per,
        pr_per=pr_per,
        **freq.build_frequency_kwargs(),
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
    pr: CfVariable,
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
    pr: CfVariable,
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
    cf_var: CfVariable,
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

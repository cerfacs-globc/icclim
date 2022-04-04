"""
All ECA&D functions. Each function wraps its xclim equivalent functions adding icclim
metadata to it.
"""
import re
from typing import Callable, Optional, Tuple
from warnings import warn

import numpy as np
import xarray as xr
import xclim.core.utils
from xarray import DataArray
from xclim import atmos, land
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to

from icclim.models.cf_calendar import CfCalendar
from icclim.models.constants import IN_BASE_IDENTIFIER, PERCENTILES_COORD
from icclim.models.frequency import Frequency
from icclim.models.index_config import CfVariable, IndexConfig
from icclim.models.quantile_interpolation import QuantileInterpolation


def gd4(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tas.study_da,
        threshold=4.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.growing_degree_days,
    )


def cfd(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmin.study_da,
        threshold=0.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.consecutive_frost_days,
    )


def fd(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmin.study_da,
        threshold=0.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.frost_days,
    )


def hd17(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tas.study_da,
        threshold=17.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.heating_degree_days,
    )


def id(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmax.study_da,
        threshold=0.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.ice_days,
    )


def csdi(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    thresh = 10 if config.threshold is None else config.threshold
    return _compute_spell_duration(
        cf_var=config.tasmin,
        freq=config.freq.panda_freq,
        per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        min_spell_duration=6,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.cold_spell_duration_index,
    )


def tg10p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_temperature_percentile_index(
        cf_var=config.tas,
        freq=config.freq,
        tas_per_thresh=10,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tg10p,
    )


def tn10p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_temperature_percentile_index(
        cf_var=config.tasmin,
        freq=config.freq,
        tas_per_thresh=10,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tn10p,
    )


def tx10p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_temperature_percentile_index(
        cf_var=config.tasmax,
        freq=config.freq,
        tas_per_thresh=10,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tx10p,
    )


def txn(config: IndexConfig) -> DataArray:
    result = atmos.tx_min(config.tasmax.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def tnn(config: IndexConfig) -> DataArray:
    result = atmos.tn_min(config.tasmin.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def cdd(config: IndexConfig) -> DataArray:
    result = atmos.maximum_consecutive_dry_days(
        config.pr.study_da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def su(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmax.study_da,
        threshold=25.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.tx_days_above,
    )


def tr(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmin.study_da,
        threshold=20.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.tropical_nights,
    )


def wsdi(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    thresh = 90 if config.threshold is None else config.threshold
    return _compute_spell_duration(
        cf_var=config.tasmax,
        freq=config.freq.panda_freq,
        per_thresh=thresh,
        per_window=config.window,
        per_interpolation=config.interpolation,
        min_spell_duration=6,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.warm_spell_duration_index,
    )


def tg90p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_temperature_percentile_index(
        cf_var=config.tas,
        freq=config.freq,
        tas_per_thresh=90,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tg90p,
    )


def tn90p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_temperature_percentile_index(
        cf_var=config.tasmin,
        freq=config.freq,
        tas_per_thresh=90,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tn90p,
    )


def tx90p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_temperature_percentile_index(
        cf_var=config.tasmax,
        freq=config.freq,
        tas_per_thresh=90,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
        callback=config.callback,
        xclim_index_fun=atmos.tx90p,
    )


def txx(config: IndexConfig) -> DataArray:
    result = atmos.tx_max(config.tasmax.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def tnx(config: IndexConfig) -> DataArray:
    result = atmos.tn_max(config.tasmin.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def csu(config: IndexConfig) -> DataArray:
    return _compute_threshold_index(
        da=config.tasmax.study_da,
        threshold=25.0 if config.threshold is None else config.threshold,
        freq=config.freq,
        xclim_index_fun=atmos.maximum_consecutive_warm_days,
    )


def prcptot(config: IndexConfig) -> DataArray:
    result = atmos.precip_accumulation(
        _filter_in_wet_days(config.pr.study_da, dry_day_value=0),
        freq=config.freq.panda_freq,
    )
    return result


def rr1(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.pr.study_da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def sdii(config: IndexConfig) -> DataArray:
    result = atmos.daily_pr_intensity(
        config.pr.study_da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def cwd(config: IndexConfig) -> DataArray:
    result = atmos.maximum_consecutive_wet_days(
        config.pr.study_da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def r10mm(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.pr.study_da, thresh="10 mm/day", freq=config.freq.panda_freq
    )
    return result


def r20mm(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.pr.study_da, thresh="20 mm/day", freq=config.freq.panda_freq
    )
    return result


def rx1day(config: IndexConfig) -> DataArray:
    result = atmos.max_1day_precipitation_amount(
        config.pr.study_da, freq=config.freq.panda_freq
    )
    return result


def rx5day(config: IndexConfig) -> DataArray:
    result = atmos.max_n_day_precipitation_amount(
        config.pr.study_da, window=5, freq=config.freq.panda_freq
    )
    return result


def r75p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_rxxp(
        pr=config.pr,
        freq=config.freq,
        pr_per_thresh=75.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
    )


def r75ptot(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_rxxptot(
        pr=config.pr,
        freq=config.freq.panda_freq,
        pr_per_thresh=75.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
    )


def r95p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_rxxp(
        pr=config.pr,
        freq=config.freq,
        pr_per_thresh=95.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
    )


def r95ptot(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_rxxptot(
        pr=config.pr,
        freq=config.freq.panda_freq,
        pr_per_thresh=95.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
    )


def r99p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_rxxp(
        pr=config.pr,
        freq=config.freq,
        pr_per_thresh=99.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        is_percent=config.is_percent,
    )


def r99ptot(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    return _compute_rxxptot(
        pr=config.pr,
        freq=config.freq.panda_freq,
        pr_per_thresh=99.0,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
    )


def sd(config: IndexConfig) -> DataArray:
    """
    Climate index: Mean of daily Snow Depth (SD)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Mean of daily snow depth (cm)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.pr with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_depth(config.pr.study_da, freq=config.freq.panda_freq)
    return result


def sd1(config: IndexConfig) -> DataArray:
    """
    Climate index: Snow Days with at least 1 cm of snow (SD1)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Number of days with SD ≥ 1 cm (days)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.pr with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_cover_duration(
        config.pr.study_da, thresh="1 cm", freq=config.freq.panda_freq
    )
    return result


def sd5cm(config: IndexConfig) -> DataArray:
    """
    Climate index: Snow Days with at least 5 cm of snow (SD5cm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Number of days with SD ≥ 5 cm (days)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.pr with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_cover_duration(
        config.pr.study_da, thresh="5 cm", freq=config.freq.panda_freq
    )
    return result


def sd50cm(config: IndexConfig) -> DataArray:
    """
    Climate index: Snow Days with at least 50 cm of snow (SD50cm)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Number of days with SD ≥ 50 cm (days)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.pr with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_cover_duration(
        config.pr.study_da, thresh="50 cm", freq=config.freq.panda_freq
    )
    return result


def tg(config: IndexConfig) -> DataArray:
    """
    Climate index: mean of daily averaged(G) Temperature (TG)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Mean of daily averaged temperature (°C)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.cf_variables[0] with tas
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = atmos.tg_mean(config.tas.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def tn(config: IndexConfig) -> DataArray:
    """
    Climate index: daily minimun(N) Temperature averaged (TN)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Mean of daily minimum temperature (°C)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.cf_variables[0] with tasmin
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = atmos.tn_mean(config.tasmin.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def tx(config: IndexConfig) -> DataArray:
    """
    Climate index: daily maximum(X) Temperature averaged (TX)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Mean of daily maximum temperature (°C)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.cf_variables[0] with tasmax
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = atmos.tx_mean(config.tasmax.study_da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def dtr(config: IndexConfig) -> DataArray:
    """
    Climate index: Diurnal Temperature Range (DTR)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Mean of diurnal temperature range (°C)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.cf_variables[0] with tasmax
        config.cf_variables[1] with tasmin
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = atmos.daily_temperature_range(
        tasmax=config.tasmax.study_da,
        tasmin=config.tasmin.study_da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result


def etr(config: IndexConfig) -> DataArray:
    """
    Climate index: Extreme Temperature Range (ETR)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Intra-period extreme temperature range (°C)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.cf_variables[0] with tasmax
        config.cf_variables[1] with tasmin
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = atmos.extreme_temperature_range(
        tasmax=config.tasmax.study_da,
        tasmin=config.tasmin.study_da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result


def vdtr(config: IndexConfig) -> DataArray:
    """
    Climate index:
        Mean absolute day-to-day difference in Diurnal temperature range (vDTR)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Mean absolute day-to-day difference in Diurnal temperature range (°C)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        config.cf_variables[0] with tasmax
        config.cf_variables[1] with tasmin
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = atmos.daily_temperature_range_variability(
        tasmax=config.tasmax.study_da,
        tasmin=config.tasmin.study_da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result


def cd(config: IndexConfig) -> DataArray:
    """
    Climate index: Cold and Wet days (CD)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Days with TG < 25th percentile of daily mean temperature and RR < 25th percentile of
    daily precipitation sum (cold/dry days)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        ``{cf_variables, window, interpolation, freq, save_percentile}``
    Returns
    -------
        If save_percentile is True,
            returns a Tuple of index_result, computed_percentiles
        Otherwise, returns the index_result
    """
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.freq.panda_freq,
        tas_per_thresh=25,
        pr_per_thresh=25,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.cold_and_dry_days,
    )


def cw(config: IndexConfig) -> DataArray:
    """
    Climate index: Cold and Wet days (CD)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Days with TG < 25th percentile of daily mean temperature and RR > 75th percentile of
    daily precipitation sum (cold/wet days)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        ``{cf_variables, window, interpolation, freq, save_percentile}``
    Returns
    -------
        If save_percentile is True,
            returns a Tuple of index_result, computed_percentiles
        Otherwise, returns the index_result
    """
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.freq.panda_freq,
        tas_per_thresh=25,
        pr_per_thresh=75,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.cold_and_wet_days,
    )


def wd(config: IndexConfig) -> DataArray:
    """
    Climate index: Warm and Dry days (WD)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Days with TG > 75th percentile of daily mean temperature and RR <25th percentile
    of daily precipitation sum (warm/dry days)

    Parameters
    ----------
    config : IndexConfig
        The configuration necessary to compute this index.
        For this index the following fields must be filled:
        ``{cf_variables, window, interpolation, freq, save_percentile}``
    Returns
    -------
        If save_percentile is True,
            returns a Tuple made of  index_result, computed_percentiles
        Otherwise, returns the index_result
    """
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.freq.panda_freq,
        tas_per_thresh=75,
        pr_per_thresh=25,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.warm_and_dry_days,
    )


def ww(config: IndexConfig) -> DataArray:
    """
    Climate index: Warm and Wet days (WW)

    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Days with TG > 75th percentile of daily mean temperature and RR > 75th percentile of
    daily precipitation sum (warm/wet days)
    """
    return compute_compound_index(
        tas=config.tas,
        pr=config.pr,
        freq=config.freq.panda_freq,
        tas_per_thresh=75,
        pr_per_thresh=75,
        per_window=config.window,
        per_interpolation=config.interpolation,
        save_percentile=config.save_percentile,
        callback=config.callback,
        xclim_index_fun=atmos.warm_and_wet_days,
    )


def _can_run_bootstrap(cf_var: CfVariable) -> bool:
    """
    Avoid bootstrapping if there is one single year overlapping or no year overlapping
    or all year overlapping.
    """
    study_years = np.unique(cf_var.study_da.indexes.get("time").year)
    overlapping_years = np.unique(
        cf_var.study_da.sel(time=_get_ref_period_slice(cf_var.reference_da))
        .indexes.get("time")
        .year
    )
    return len(overlapping_years) > 1 and len(overlapping_years) < len(study_years)


def _get_ref_period_slice(da: DataArray) -> slice:
    time_length = len(da.time)
    return slice(*(da.time[0 :: time_length - 1].dt.strftime("%Y-%m-%d").values))


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    if sampling_freq == Frequency.MONTH:
        da = da / da.time.dt.daysinmonth * 100
    elif sampling_freq == Frequency.YEAR:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[leap_years] = 366
        coef[~leap_years] = 365
        da = da / coef
    elif sampling_freq == Frequency.AMJJAS:
        da = da / 183
    elif sampling_freq == Frequency.ONDJFM:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[leap_years] = 183
        coef[~leap_years] = 182
        da = da / coef
    elif sampling_freq == Frequency.DJF:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[leap_years] = 91
        coef[~leap_years] = 90
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
        cf_calendar: CfCalendar = CfCalendar.lookup(time_index.calendar)
        return cf_calendar.is_leap(da.time.dt.year)
    else:
        return da.time.dt.is_leap_year


def _add_bootstrap_meta(result: DataArray, per: DataArray) -> DataArray:
    result.attrs[IN_BASE_IDENTIFIER] = per.climatology_bounds
    return result


def _compute_percentile_doy(
    da: DataArray,
    percentile: float,
    window: int = 5,
    interpolation=QuantileInterpolation.MEDIAN_UNBIASED,
    callback: Callable = None,
) -> DataArray:
    per = percentile_doy(
        da,
        window,
        percentile,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    )
    if callback is not None:
        callback(50)
    return per


def _compute_percentile_over_period(
    arr: DataArray, interpolation: QuantileInterpolation, percentiles: float
) -> DataArray:
    return xr.apply_ufunc(
        xclim.core.utils.calc_perc,
        arr,
        input_core_dims=[["time"]],
        output_core_dims=[[PERCENTILES_COORD]],
        kwargs=dict(
            percentiles=[percentiles],
            alpha=interpolation.alpha,
            beta=interpolation.beta,
        ),
        dask="parallelized",
        output_dtypes=[arr.dtype],
        dask_gufunc_kwargs=dict(output_sizes={PERCENTILES_COORD: len([percentiles])}),
    )


def _filter_in_wet_days(da: DataArray, dry_day_value: float):
    """
    Turns non wet days to NaN.
    dry_day_value may be Nan or 0.
    """
    precip = convert_units_to(da, "mm/d")
    return precip.where(precip > 1, dry_day_value)


def _compute_threshold_index(
    da: DataArray,
    threshold: float,
    freq: Frequency,
    xclim_index_fun: Callable,
) -> DataArray:
    result = xclim_index_fun(da, thresh=f"{threshold} °C", freq=freq.panda_freq)
    return result


def _compute_spell_duration(
    cf_var: CfVariable,
    freq: str,
    per_window: int,
    per_thresh: float,
    per_interpolation: QuantileInterpolation,
    min_spell_duration: int,
    save_percentile: bool,
    callback: Callable,
    xclim_index_fun: Callable,
) -> Tuple[DataArray, Optional[DataArray]]:
    per = _compute_percentile_doy(
        cf_var.reference_da,
        per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    run_bootstrap = _can_run_bootstrap(cf_var)
    result = xclim_index_fun(
        cf_var.study_da,
        per,
        window=min_spell_duration,
        freq=freq,
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
    freq: str,
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
    in_base_tas : DataArray
        DataArray of tas in_base variable.
        Used for percentile calculation only.
        Can overlap with tas.
    pr : DataArray
        DataArray of pr variable.
    in_base_pr : DataArray
        DataArray of pr in_base variable.
        Used for percentile calculation only.
        Can overlap with pr.
    window : int
        window in days used to computed each percentile.
        default is 5.
    freq : str
        pandas like frequency.
        Used to determine the time slices of the output.
        Default is "YS" as in Year Start.
    save_percentile : bool
        Flag to include coordinate variable including the computed percentiles.
        Does not contain the bootstrapped percentiles.
        Default is False.
    interpolation :QuantileInterpolation
        percentile interpolation method, default is MEDIAN_UNBIASED, a.k.a method 8.
    callback : Callable
        callback receiving an integer, may serve as a loading bar.

    Returns
    -------
        If save_percentile is True,
            returns a Tuple of index_result, computed_percentiles
        Otherwise, returns the index_result
    """
    tas_per = _compute_percentile_doy(
        tas.reference_da,
        tas_per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    tas_per = tas_per.squeeze(PERCENTILES_COORD, drop=True)
    pr_in_base = _filter_in_wet_days(pr.reference_da, dry_day_value=np.NAN)
    pr_out_of_base = _filter_in_wet_days(pr.study_da, dry_day_value=0)
    pr_per = _compute_percentile_doy(
        pr_in_base,
        pr_per_thresh,
        per_window,
        per_interpolation,
        callback,
    )
    pr_per = pr_per.squeeze(PERCENTILES_COORD, drop=True)
    result = xclim_index_fun(tas.study_da, tas_per, pr_out_of_base, pr_per, freq=freq)
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
    freq: str,
    pr_per_thresh: float,
    per_interpolation: QuantileInterpolation,
    save_percentile: bool,
) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(pr.reference_da, dry_day_value=np.nan)
    per = _compute_percentile_over_period(
        base_wet_days, per_interpolation, pr_per_thresh
    )
    result = atmos.fraction_over_precip_thresh(
        pr.study_da,
        per,
        thresh="1 mm/day",
        freq=freq,
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
) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(pr.reference_da, dry_day_value=np.nan)
    per = _compute_percentile_over_period(
        base_wet_days, per_interpolation, pr_per_thresh
    )
    result = atmos.days_over_precip_thresh(
        pr.study_da,
        per,
        thresh="1 mm/day",
        freq=freq.panda_freq,
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
) -> Tuple[DataArray, Optional[DataArray]]:
    run_bootstrap = _can_run_bootstrap(cf_var)
    per = _compute_percentile_doy(
        cf_var.reference_da,
        tas_per_thresh,
        per_window,
        per_interpolation,
        callback,
    ).compute()
    result = xclim_index_fun(
        cf_var.study_da,
        per,
        freq=freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if is_percent:
        result = _to_percent(result, freq)
    if save_percentile:
        return result, per
    return result, None

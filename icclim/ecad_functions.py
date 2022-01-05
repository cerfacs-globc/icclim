"""
All ECA&D functions. Each function wraps its Xclim equivalent functions adding icclim
metadata to it.
"""
from typing import Callable, Optional, Tuple, Union
from warnings import warn

import numpy as np
import xarray as xr
import xclim.core.utils
from xarray import DataArray
from xclim import atmos, land
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendar
from icclim.models.constants import IN_BASE_IDENTIFIER, PERCENTILES_COORD
from icclim.models.frequency import Frequency
from icclim.models.index_config import IndexConfig
from icclim.models.quantile_interpolation import QuantileInterpolation

ComputeIndexFun = Callable[
    [IndexConfig], Union[DataArray, Tuple[DataArray, Optional[DataArray]]]
]


def gd4(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "4.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.growing_degree_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def cfd(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.consecutive_frost_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def fd(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.frost_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def hd17(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "17.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.heating_degree_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def id(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.ice_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def csdi(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.cold_spell_duration_index(
        config.cf_variables[0].da,
        per,
        window=6,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        return result, per
    return result


def tg10p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tg10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def tn10p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tn10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def tx10p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tx10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def txn(config: IndexConfig) -> DataArray:
    result = atmos.tx_min(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def tnn(config: IndexConfig) -> DataArray:
    result = atmos.tn_min(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def cdd(config: IndexConfig) -> DataArray:
    result = atmos.maximum_consecutive_dry_days(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def su(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "25.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.tx_days_above(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def tr(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "20.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.tropical_nights(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def wsdi(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.warm_spell_duration_index(
        config.cf_variables[0].da,
        per,
        window=6,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        return result, per
    return result


def tg90p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tg90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def tn90p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tn90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def tx90p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tx90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def txx(config: IndexConfig) -> DataArray:
    result = atmos.tx_max(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def tnx(config: IndexConfig) -> DataArray:
    result = atmos.tn_max(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "°C")
    return result


def csu(config: IndexConfig) -> DataArray:
    if config.threshold is None:
        threshold = "25.0 °C"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.maximum_consecutive_warm_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result


def prcptot(config: IndexConfig) -> DataArray:
    result = atmos.precip_accumulation(
        _filter_in_wet_days(config.cf_variables[0].da, dry_day_value=0),
        freq=config.freq.panda_freq,
    )
    return result


def rr1(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def sdii(config: IndexConfig) -> DataArray:
    result = atmos.daily_pr_intensity(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def cwd(config: IndexConfig) -> DataArray:
    result = atmos.maximum_consecutive_wet_days(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result


def r10mm(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.cf_variables[0].da, thresh="10 mm/day", freq=config.freq.panda_freq
    )
    return result


def r20mm(config: IndexConfig) -> DataArray:
    result = atmos.wetdays(
        config.cf_variables[0].da, thresh="20 mm/day", freq=config.freq.panda_freq
    )
    return result


def rx1day(config: IndexConfig) -> DataArray:
    result = atmos.max_1day_precipitation_amount(
        config.cf_variables[0].da, freq=config.freq.panda_freq
    )
    return result


def rx5day(config: IndexConfig) -> DataArray:
    result = atmos.max_n_day_precipitation_amount(
        config.cf_variables[0].da, window=5, freq=config.freq.panda_freq
    )
    return result


def r75p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(
        config.cf_variables[0].in_base_da, dry_day_value=np.nan
    )
    per = _compute_percentile(base_wet_days, config, 75.0)
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def r75ptot(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(
        config.cf_variables[0].in_base_da, dry_day_value=np.nan
    )
    per = _compute_percentile(base_wet_days, config, 75.0)
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    result = result * 100
    result.attrs["units"] = "%"
    if config.save_percentile:
        return result, per
    return result


def r95p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(
        config.cf_variables[0].in_base_da, dry_day_value=np.nan
    )
    per = _compute_percentile(base_wet_days, config, 95.0)
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result


def r95ptot(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(
        config.cf_variables[0].in_base_da, dry_day_value=np.nan
    )
    per = _compute_percentile(base_wet_days, config, 95.0)
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    result = result * 100
    result.attrs["units"] = "%"
    if config.save_percentile:
        return result, per
    return result


def r99p(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(
        config.cf_variables[0].in_base_da, dry_day_value=np.nan
    )
    per = _compute_percentile(base_wet_days, config, 99.0)
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    if config.save_percentile:
        return result, per
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def r99ptot(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    base_wet_days = _filter_in_wet_days(
        config.cf_variables[0].in_base_da, dry_day_value=np.nan
    )
    per = _compute_percentile(base_wet_days, config, 99.0)
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=False,
    ).squeeze(PERCENTILES_COORD, drop=True)
    result = result * 100
    result.attrs["units"] = "%"
    if config.save_percentile:
        return result, per
    return result


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
        config.cf_variables[0] with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_depth(config.cf_variables[0].da, freq=config.freq.panda_freq)
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
        config.cf_variables[0] with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_cover_duration(
        config.cf_variables[0].da, thresh="1 cm", freq=config.freq.panda_freq
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
        config.cf_variables[0] with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_cover_duration(
        config.cf_variables[0].da, thresh="5 cm", freq=config.freq.panda_freq
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
        config.cf_variables[0] with the surface snow thickness
        config.freq
    Returns
    -------
    returns DataArray of the resulting index
    """
    result = land.snow_cover_duration(
        config.cf_variables[0].da, thresh="50 cm", freq=config.freq.panda_freq
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
    result = atmos.tg_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)
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
    result = atmos.tn_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)
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
    result = atmos.tx_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)
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
        tasmax=config.cf_variables[0].da,
        tasmin=config.cf_variables[1].da,
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
        tasmax=config.cf_variables[0].da,
        tasmin=config.cf_variables[1].da,
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
        tasmax=config.cf_variables[0].da,
        tasmin=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result


def cd(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 25
    ).squeeze(PERCENTILES_COORD, drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.NAN
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 25).squeeze(
        PERCENTILES_COORD, drop=True
    )
    result = atmos.cold_and_dry_days(
        tas=config.cf_variables[0].da,
        tas_25=tas_per,
        pr=precip_cfvar.da,
        pr_25=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def cw(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 25
    ).squeeze(PERCENTILES_COORD, drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.nan
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 75).squeeze(
        PERCENTILES_COORD, drop=True
    )
    result = atmos.cold_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_25=tas_per,
        pr=precip_cfvar.da,
        pr_75=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def wd(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 75
    ).squeeze(PERCENTILES_COORD, drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.nan
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 25).squeeze(
        PERCENTILES_COORD, drop=True
    )
    result = atmos.warm_and_dry_days(
        tas=config.cf_variables[0].da,
        tas_75=tas_per,
        pr=precip_cfvar.da,
        pr_25=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def ww(config: IndexConfig) -> Tuple[DataArray, Optional[DataArray]]:
    """
    Climate index: Warm and Wet days (WW)
    Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11

    Days with TG > 75th percentile of daily mean temperature and RR > 75th percentile of
    daily precipitation sum (warm/wet days)

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
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 75
    ).squeeze(PERCENTILES_COORD, drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.nan
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 75).squeeze(
        PERCENTILES_COORD, drop=True
    )
    result = atmos.warm_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_75=tas_per,
        pr=precip_cfvar.da,
        pr_75=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def _add_celsius_suffix(threshold: Optional[Union[str, float, int]]) -> Optional[str]:
    if threshold is not None:
        return f"{threshold} °C"
    return None


def _can_run_bootstrap(config: IndexConfig, percentile_period) -> bool:
    overlapping_years = np.unique(
        config.cf_variables[0].da.time.sel(time=percentile_period).dt.year
    )
    # No bootstrap if there is one single year overlapping
    # or no year overlapping
    # or all year overlapping
    run_bootstrap = (
        config.cf_variables[0].in_base_da is not config.cf_variables[0].da
        and len(overlapping_years) > 1
    )
    if run_bootstrap:
        in_base = config.cf_variables[0].in_base_da
        chunking = {d: "auto" for d in in_base.dims}
        chunking["time"] = -1
        config.cf_variables[0].in_base_da = in_base.chunk(chunking)
        config.cf_variables[0].da = config.cf_variables[0].da.chunk(chunking)
    if run_bootstrap and config.interpolation != QuantileInterpolation.MEDIAN_UNBIASED:
        raise InvalidIcclimArgumentError(
            "When bootstrapping, the interpolation must be MEDIAN_UNBIASED."
            f" Here it was {config.interpolation}."
        )
    return run_bootstrap


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
            "For now, '%' unit can only be used with slice_mode being one of "
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
    da: DataArray, config: IndexConfig, percentile: int
) -> DataArray:
    per = percentile_doy(
        da,
        config.window,
        percentile,
        alpha=config.interpolation.alpha,
        beta=config.interpolation.beta,
    )
    if config.callback is not None:
        config.callback(50)
    return per


def _compute_percentile(
    arr: DataArray, config: IndexConfig, percentiles: float
) -> DataArray:
    return xr.apply_ufunc(
        xclim.core.utils.calc_perc,
        arr,
        input_core_dims=[["time"]],
        output_core_dims=[[PERCENTILES_COORD]],
        kwargs=dict(
            percentiles=[percentiles],
            alpha=config.interpolation.alpha,
            beta=config.interpolation.beta,
        ),
        dask="parallelized",
        output_dtypes=[arr.dtype],
        dask_gufunc_kwargs=dict(output_sizes={PERCENTILES_COORD: len([percentiles])}),
    )


def _filter_in_wet_days(da: DataArray, dry_day_value):
    """
    Turns non wet days to NaN.
    """
    precip = convert_units_to(da, "mm/d")
    return precip.where(precip > 1, dry_day_value)

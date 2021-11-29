from enum import Enum
from typing import Callable, List, Optional, Tuple, Union
from warnings import warn

import numpy as np
import xarray as xr
import xclim.core.utils
from xarray import DataArray
from xclim import atmos, land
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import get_calendar_from_str
from icclim.models.constants import (
    COLD_GROUP,
    COMPOUND_GROUP,
    DROUGHT_GROUP,
    HEAT_GROUP,
    PR,
    RAIN_GROUP,
    SNOW_GROUP,
    TAS,
    TASMAX,
    TASMIN,
    TEMPERATURE_GROUP,
)
from icclim.models.frequency import Frequency
from icclim.models.indice_config import IndiceConfig
from icclim.models.quantile_interpolation import QuantileInterpolation

PERCENTILES_COORD = "percentiles"
IN_BASE_ATTRS = "reference_epoch"


def gd4(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "4.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.growing_degree_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def cfd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.consecutive_frost_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def fd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.frost_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def hd17(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "17.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.heating_degree_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def id(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.ice_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def csdi(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.cold_spell_duration_index(
        config.cf_variables[0].da,
        per,
        window=6,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        return result, per
    return result, None


def tg10p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tg10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def tn10p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tn10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def tx10p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 10
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tx10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def txn(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tx_min(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def tnn(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tn_min(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def cdd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.maximum_consecutive_dry_days(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result, None


def su(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "25.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.tx_days_above(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def tr(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "20.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.tropical_nights(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def wsdi(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.warm_spell_duration_index(
        config.cf_variables[0].da,
        per,
        window=6,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        return result, per
    return result, None


def tg90p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tg90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def tn90p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tn90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def tx90p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    per_value = 90
    per = _compute_percentile_doy(config.cf_variables[0].in_base_da, config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tx90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def txx(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tx_max(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def tnx(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tn_max(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def csu(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    if config.threshold is None:
        threshold = "25.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    result = atmos.maximum_consecutive_warm_days(
        config.cf_variables[0].da, thresh=threshold, freq=config.freq.panda_freq
    )
    return result, None


def prcptot(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.precip_accumulation(
        _filter_in_wet_days(config.cf_variables[0].da, dry_day_value=0),
        freq=config.freq.panda_freq,
        # TODO see if we should use tas and thresh
        # tas=config.cf_variables[0].da,
        # thresh=threshold
    )
    return result, None


def rr1(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.wetdays(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result, None


def sdii(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.daily_pr_intensity(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result, None


def cwd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.maximum_consecutive_wet_days(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )
    return result, None


def r10mm(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.wetdays(
        config.cf_variables[0].da, thresh="10 mm/day", freq=config.freq.panda_freq
    )
    return result, None


def r20mm(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.wetdays(
        config.cf_variables[0].da, thresh="20 mm/day", freq=config.freq.panda_freq
    )
    return result, None


def rx1day(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.max_1day_precipitation_amount(
        config.cf_variables[0].da, freq=config.freq.panda_freq
    )
    return result, None


def rx5day(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.max_n_day_precipitation_amount(
        config.cf_variables[0].da, window=5, freq=config.freq.panda_freq
    )
    return result, None


def r75p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    ).squeeze("percentiles", drop=True)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def r75ptot(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    ).squeeze("percentiles", drop=True)
    result = result * 100
    if config.save_percentile:
        return result, per
    return result, None


def r95p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    ).squeeze("percentiles", drop=True)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    if config.save_percentile:
        return result, per
    return result, None


def r95ptot(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    ).squeeze("percentiles", drop=True)
    result = result * 100
    if config.save_percentile:
        return result, per
    return result, None


def r99p(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    ).squeeze("percentiles", drop=True)
    if config.save_percentile:
        return result, per
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result, None


def r99ptot(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
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
    ).squeeze("percentiles", drop=True)
    result = result * 100
    if config.save_percentile:
        return result, per
    return result, None


def sd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = land.snow_depth(config.cf_variables[0].da, freq=config.freq.panda_freq)
    return result, None


def sd1(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = land.snow_cover_duration(
        config.cf_variables[0].da, thresh="1 cm", freq=config.freq.panda_freq
    )
    return result, None


def sd5cm(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = land.snow_cover_duration(
        config.cf_variables[0].da, thresh="5 cm", freq=config.freq.panda_freq
    )
    return result, None


def sd50cm(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = land.snow_cover_duration(
        config.cf_variables[0].da, thresh="50 cm", freq=config.freq.panda_freq
    )
    return result, None


def tg(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tg_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def tn(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tn_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def tx(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.tx_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)
    result = convert_units_to(result, "degC")
    return result, None


def dtr(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.daily_temperature_range(
        tasmax=config.cf_variables[0].da,
        tasmin=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result, None


def etr(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.extreme_temperature_range(
        tasmax=config.cf_variables[0].da,
        tasmin=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result, None


def vdtr(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    result = atmos.daily_temperature_range_variability(
        tasmax=config.cf_variables[0].da,
        tasmin=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )
    result.attrs["units"] = "°C"
    return result, None


def cd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 25
    ).squeeze("percentiles", drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.NAN
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 25).squeeze(
        "percentiles", drop=True
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
    return result, None


def cw(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 25
    ).squeeze("percentiles", drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.nan
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 75).squeeze(
        "percentiles", drop=True
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
    return result, None


def wd(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 75
    ).squeeze("percentiles", drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.nan
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 25).squeeze(
        "percentiles", drop=True
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
    return result, None


def ww(config: IndiceConfig) -> Tuple[DataArray, Optional[DataArray]]:
    tas_per = _compute_percentile_doy(
        config.cf_variables[0].in_base_da, config, 75
    ).squeeze("percentiles", drop=True)
    precip_cfvar = config.cf_variables[1]
    precip_cfvar.in_base_da = _filter_in_wet_days(
        precip_cfvar.in_base_da, dry_day_value=np.nan
    )
    precip_cfvar.da = _filter_in_wet_days(precip_cfvar.da, dry_day_value=0)
    pr_per = _compute_percentile_doy(precip_cfvar.in_base_da, config, 75).squeeze(
        "percentiles", drop=True
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
    return result, None


class Indice(Enum):
    # temperature
    TG = ("tg", tg, TEMPERATURE_GROUP, [TAS])
    TN = ("tn", tn, TEMPERATURE_GROUP, [TASMIN])
    TX = ("tx", tx, TEMPERATURE_GROUP, [TASMAX])
    DTR = ("dtr", dtr, TEMPERATURE_GROUP, [TASMAX, TASMIN])
    ETR = ("etr", etr, TEMPERATURE_GROUP, [TASMAX, TASMIN])
    VDTR = ("vdtr", vdtr, TEMPERATURE_GROUP, [TASMAX, TASMIN])
    # heat
    SU = ("su", su, HEAT_GROUP, [TASMAX])
    TR = ("tr", tr, HEAT_GROUP, [TASMIN])
    WSDI = ("wsdi", wsdi, HEAT_GROUP, [TASMAX])
    TG90P = ("tg90p", tg90p, HEAT_GROUP, [TAS])
    TN90P = ("tn90p", tn90p, HEAT_GROUP, [TASMIN])
    TX90P = ("tx90p", tx90p, HEAT_GROUP, [TASMAX])
    TXX = ("txx", txx, HEAT_GROUP, [TASMAX])
    TNX = ("tnx", tnx, HEAT_GROUP, [TASMIN])
    CSU = ("csu", csu, HEAT_GROUP, [TASMAX])
    # cold
    GD4 = ("gd4", gd4, COLD_GROUP, [TAS])
    FD = ("fd", fd, COLD_GROUP, [TASMIN])
    CFD = ("cfd", cfd, COLD_GROUP, [TASMIN])
    HD17 = ("hd17", hd17, COLD_GROUP, [TASMIN])
    ID = ("id", id, COLD_GROUP, [TASMAX])
    TG10P = ("tg10p", tg10p, COLD_GROUP, [TAS])
    TN10P = ("tn10p", tn10p, COLD_GROUP, [TASMIN])
    TX10P = ("tx10p", tx10p, COLD_GROUP, [TASMAX])
    TXN = ("txn", txn, COLD_GROUP, [TASMAX])
    TNN = ("tnn", tnn, COLD_GROUP, [TASMIN])
    CSDI = ("csdi", csdi, COLD_GROUP, [TASMIN])
    # drought
    CDD = ("cdd", cdd, DROUGHT_GROUP, [PR])
    # rain
    PRCPTOT = ("prcptot", prcptot, RAIN_GROUP, [PR])
    RR1 = ("rr1", rr1, RAIN_GROUP, [PR])
    SDII = ("sdii", sdii, RAIN_GROUP, [PR])
    CWD = ("cwd", cwd, RAIN_GROUP, [PR])
    R10MM = ("r10mm", r10mm, RAIN_GROUP, [PR])
    R20MM = ("r20mm", r20mm, RAIN_GROUP, [PR])
    RX1DAY = ("rx1day", rx1day, RAIN_GROUP, [PR])
    RX5DAY = ("rx5day", rx5day, RAIN_GROUP, [PR])
    R75P = ("r75p", r75p, RAIN_GROUP, [PR])
    R75PTOT = ("r75ptot", r75ptot, RAIN_GROUP, [PR])
    R95P = ("r95p", r95p, RAIN_GROUP, [PR])
    R95PTOT = ("r95ptot", r95ptot, RAIN_GROUP, [PR])
    R99P = ("r99p", r99p, RAIN_GROUP, [PR])
    R99PTOT = ("r99ptot", r99ptot, RAIN_GROUP, [PR])
    # snow
    SD = ("sd", sd, SNOW_GROUP, [PR])
    SD1 = ("sd1", sd1, SNOW_GROUP, [PR])
    SD5CM = ("sd5cm", sd5cm, SNOW_GROUP, [PR])
    SD50CM = ("sd50cm", sd50cm, SNOW_GROUP, [PR])
    # compound
    CD = ("cd", cd, COMPOUND_GROUP, [TAS, PR])
    CW = ("cw", cw, COMPOUND_GROUP, [TAS, PR])
    WD = ("wd", wd, COMPOUND_GROUP, [TAS, PR])
    WW = ("ww", ww, COMPOUND_GROUP, [TAS, PR])

    def __init__(
        self,
        indice_name: str,
        compute: Callable[[IndiceConfig], Tuple[DataArray, Optional[DataArray]]],
        group: str,
        variables: List[List[str]],
    ):
        self.indice_name = indice_name
        self.compute = compute
        self.group = group
        self.variables = variables


def indice_from_string(s: str) -> Indice:
    indice_to_check = s.upper()
    for e in Indice:
        if e.indice_name.upper() == indice_to_check:
            return e
    raise InvalidIcclimArgumentError(f"Unknown indice {s}")


def _add_celsius_suffix(threshold: Optional[Union[str, float, int]]) -> Optional[str]:
    if threshold is not None:
        return f"{threshold} degC"
    return None


def _can_run_bootstrap(config: IndiceConfig, percentile_period) -> bool:
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
        cf_calendar = get_calendar_from_str(time_index.calendar)
        return cf_calendar.is_leap(da.time.dt.year)
    else:
        return da.time.dt.is_leap_year


def _add_bootstrap_meta(result: DataArray, per: DataArray) -> DataArray:
    result.attrs[IN_BASE_ATTRS] = per.climatology_bounds
    return result


def _compute_percentile_doy(
    da: DataArray, config: IndiceConfig, percentile: int
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
    arr: DataArray, config: IndiceConfig, percentiles: float
) -> DataArray:
    return xr.apply_ufunc(
        xclim.core.utils.calc_perc,
        arr,
        input_core_dims=[["time"]],
        output_core_dims=[["percentiles"]],
        kwargs=dict(
            percentiles=[percentiles],
            alpha=config.interpolation.alpha,
            beta=config.interpolation.beta,
        ),
        dask="parallelized",
        output_dtypes=[arr.dtype],
        dask_gufunc_kwargs=dict(output_sizes={"percentiles": len([percentiles])}),
    )


def _filter_in_wet_days(da: DataArray, dry_day_value):
    """
    Turns non wet days to NaN.
    """
    precip = convert_units_to(da, "mm/d")
    return precip.where(precip > 1, dry_day_value)

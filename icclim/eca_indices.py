from enum import Enum
from typing import Callable, List, Optional, Union
from warnings import warn

import numpy as np
import xarray
from xarray import DataArray
from xarray.core.dataset import Dataset
from xclim import atmos, land
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency
from icclim.models.indice_config import IndiceConfig
from icclim.models.quantile_interpolation import QuantileInterpolation

PERCENTILES_COORD = "percentiles"
IN_BASE_ATTRS = "reference_epoch"


def gd4(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "4.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.growing_degree_days(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def cfd(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.consecutive_frost_days(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def fd(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.frost_days(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def hd17(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "17.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.heating_degree_days(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def id(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.ice_days(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def csdi(config: IndiceConfig) -> DataArray:
    per_value = 10
    per = _compute_percentiles(config, per_value)
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
        result = _add_percentile_meta(run_bootstrap, result, per)
    return result


def tg10p(config: IndiceConfig) -> DataArray:
    per_value = 10
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tg10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def tn10p(config: IndiceConfig) -> Dataset:
    per_value = 10
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tn10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def tx10p(config: IndiceConfig) -> DataArray:
    per_value = 10
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tx10p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def txn(config: IndiceConfig) -> DataArray:
    return atmos.tx_min(config.cf_variables[0].da, freq=config.freq.panda_freq)


def tnn(config: IndiceConfig) -> DataArray:
    return atmos.tn_min(config.cf_variables[0].da, freq=config.freq.panda_freq)


def cdd(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_dry_days(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )


def su(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "25.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.tx_days_above(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def tr(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "20.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.tropical_nights(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def wsdi(config: IndiceConfig) -> DataArray:
    per_value = 90
    per = _compute_percentiles(config, per_value)
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
        result = _add_percentile_meta(run_bootstrap, result, per)
    return result


def tg90p(config: IndiceConfig) -> DataArray:
    per_value = 90
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tg90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def tn90p(config: IndiceConfig) -> DataArray:
    per_value = 90
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tn90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def tx90p(config: IndiceConfig) -> DataArray:
    per_value = 90
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.tx90p(
        config.cf_variables[0].da,
        per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def txx(config: IndiceConfig) -> DataArray:
    return atmos.tx_max(config.cf_variables[0].da, freq=config.freq.panda_freq)


def tnx(config: IndiceConfig) -> DataArray:
    return atmos.tn_max(config.cf_variables[0].da, freq=config.freq.panda_freq)


def csu(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "25.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.maximum_consecutive_warm_days(
        config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def prcptot(config: IndiceConfig) -> DataArray:
    return atmos.precip_accumulation(
        config.cf_variables[0].da,
        freq=config.freq.panda_freq,
        # TODO see if we should use tas and thresh
        # tas=config.cf_variables[0].da,
        # thresh=threshold,
    )


def rr1(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )


def sdii(config: IndiceConfig) -> DataArray:
    return atmos.daily_pr_intensity(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )


def cwd(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_wet_days(
        config.cf_variables[0].da, thresh="1.0 mm/day", freq=config.freq.panda_freq
    )


def r10mm(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(
        config.cf_variables[0].da, thresh="10 mm/day", freq=config.freq.panda_freq
    )


def r20mm(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(
        config.cf_variables[0].da, thresh="20 mm/day", freq=config.freq.panda_freq
    )


def rx1day(config: IndiceConfig) -> DataArray:
    return atmos.max_1day_precipitation_amount(
        config.cf_variables[0].da, freq=config.freq.panda_freq
    )


def rx5day(config: IndiceConfig) -> DataArray:
    return atmos.max_n_day_precipitation_amount(
        config.cf_variables[0].da, window=5, freq=config.freq.panda_freq
    )


def r75p(config: IndiceConfig) -> DataArray:
    per_value = 75
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def r75ptot(config: IndiceConfig) -> DataArray:
    per_value = 75
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    return result


def r95p(config: IndiceConfig) -> DataArray:
    per_value = 95
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def r95ptot(config: IndiceConfig) -> DataArray:
    per_value = 95
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    return result


def r99p(config: IndiceConfig) -> DataArray:
    per_value = 99
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def r99ptot(config: IndiceConfig) -> DataArray:
    per_value = 99
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    return result


def sd(config: IndiceConfig) -> DataArray:
    return land.snow_depth(config.cf_variables[0].da, freq=config.freq.panda_freq)


def sd1(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(
        config.cf_variables[0].da, thresh="1 cm", freq=config.freq.panda_freq
    )


def sd5cm(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(
        config.cf_variables[0].da, thresh="5 cm", freq=config.freq.panda_freq
    )


def sd50cm(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(
        config.cf_variables[0].da, thresh="50 cm", freq=config.freq.panda_freq
    )


def tg(config: IndiceConfig) -> DataArray:
    return atmos.tg_mean(config.cf_variables[0].da, freq=config.freq.panda_freq)


def tn(config: IndiceConfig) -> DataArray:
    return atmos.tg_min(config.cf_variables[0].da, freq=config.freq.panda_freq)


def tx(config: IndiceConfig) -> DataArray:
    return atmos.tg_max(config.cf_variables[0].da, freq=config.freq.panda_freq)


def dtr(config: IndiceConfig) -> DataArray:
    return atmos.daily_temperature_range(
        tasmin=config.cf_variables[0].da,
        tasmax=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )


def etr(config: IndiceConfig) -> DataArray:
    return atmos.extreme_temperature_range(
        tasmin=config.cf_variables[0].da,
        tasmax=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )


def vdtr(config: IndiceConfig) -> DataArray:
    return atmos.daily_temperature_range_variability(
        tasmin=config.cf_variables[0].da,
        tasmax=config.cf_variables[1].da,
        freq=config.freq.panda_freq,
    )


def cd(config: IndiceConfig) -> DataArray:
    tas_per = _compute_percentiles(config, 25)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=25).sel(percentiles=25)
    result = atmos.cold_and_dry_days(
        tas=config.cf_variables[0].da,
        tas_25=tas_per,
        pr=config.cf_variables[1].da,
        pr_25=pr_per,
        freq=config.freq.panda_freq,
    ).squeeze("percentiles", drop=True)
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def cw(config: IndiceConfig) -> DataArray:
    tas_per = _compute_percentiles(config, 25)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=75).sel(percentiles=75)
    result = atmos.cold_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_25=tas_per,
        pr=config.cf_variables[1].da,
        pr_75=pr_per,
        freq=config.freq.panda_freq,
    ).squeeze("percentiles", drop=True)
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def wd(config: IndiceConfig) -> DataArray:
    tas_per = _compute_percentiles(config, 75)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=25).sel(percentiles=25)
    result = atmos.warm_and_dry_days(
        tas=config.cf_variables[0].da,
        tas_75=tas_per,
        pr=config.cf_variables[1].da,
        pr_25=pr_per,
        freq=config.freq.panda_freq,
    ).squeeze("percentiles", drop=True)
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def ww(config: IndiceConfig) -> DataArray:
    tas_per = _compute_percentiles(config, 75)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=75).sel(percentiles=75)
    result = atmos.warm_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_75=tas_per,
        pr=config.cf_variables[1].da,
        pr_75=pr_per,
        freq=config.freq.panda_freq,
    ).squeeze("percentiles", drop=True)
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


TEMPERATURE_GROUP = "temperature"
HEAT_GROUP = "heat"
COLD_GROUP = "cold"
DROUGHT_GROUP = "drought"
RAIN_GROUP = "rain"
SNOW_GROUP = "snow"
COMPOUND_GROUP = "compound"

# Aliases of input variables names. Source: clix-meta
PR = ["pradjust", "prec", "rr", "precip", "PREC", "Prec", "RR", "PRECIP", "Precip"]
TAS = [
    "tasadjust",
    "tmean",
    "tm",
    "tg",
    "meant",
    "TMEAN",
    "Tmean",
    "TM",
    "TG",
    "MEANT",
    "meanT",
    "tasmidpoint",
]
TASMAX = ["tasmaxadjust", "tmax", "tx", "maxt", "TMAX", "Tmax", "TX", "MAXT", "maxT"]
TASMIN = ["tasminadjust", "tmin", "tn", "mint", "TMIN", "Tmin", "TN", "MINT", "minT"]
HURS = ["hursadjust", "rh", "RH"]
PSL = ["mslp", "slp", "pp", "MSLP", "SLP", "PP"]
SND = ["sd", "SD"]
SUND = ["ss", "SS"]
WSGSMAX = ["fx", "FX"]
SFCWIND = ["sfcwind", "fg", "FG"]
SN = ["swe", "SWE"]


class Indice(Enum):
    # temperature
    TG = ("tg", tg, TEMPERATURE_GROUP, [TAS])
    TN = ("tn", tn, TEMPERATURE_GROUP, [TASMIN])
    TX = ("tx", tx, TEMPERATURE_GROUP, [TASMAX])
    DTR = ("dtr", dtr, TEMPERATURE_GROUP, [TASMIN, TASMAX])
    ETR = ("etr", etr, TEMPERATURE_GROUP, [TASMIN, TASMAX])
    VDTR = ("vdtr", vdtr, TEMPERATURE_GROUP, [TASMIN, TASMAX])
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
    GD4 = ("gd4", gd4, COLD_GROUP, [TASMIN])
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
    CD = ("cd", cd, COMPOUND_GROUP, [TASMAX, PR])
    CW = ("cw", cw, COMPOUND_GROUP, [TASMAX, PR])
    WD = ("wd", wd, COMPOUND_GROUP, [TASMAX, PR])
    WW = ("ww", ww, COMPOUND_GROUP, [TASMAX, PR])

    def __init__(
        self,
        indice_name: str,
        compute: Callable[[IndiceConfig], DataArray],
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
    # TODO add warning if the percentile is not close to 0 or 99 ?
    # TODO add warning if doing bootstrap on precipitations ?
    overlapping_years = np.unique(
        config.cf_variables[0].da.time.sel(time=percentile_period).dt.year
    )
    # No bootstrap if there is one single year or no year overlapping
    run_bootstrap = (
        config.cf_variables[0].in_base_da is not None and len(overlapping_years) > 1
    )
    if run_bootstrap and config.interpolation != QuantileInterpolation.MEDIAN_UNBIASED:
        raise InvalidIcclimArgumentError(
            "When bootstrapping, the interpolation must be MEDIAN_UNBIASED."
            f" Here it was {config.interpolation}."
        )
    return run_bootstrap


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    with xarray.set_options(keep_attrs=True):
        if sampling_freq == Frequency.MONTH:
            da = da / da.time.dt.daysinmonth * 100
        elif sampling_freq == Frequency.YEAR:
            coef = da.time
            coef[da.dt.is_leap_year] = 366
            coef[~da.dt.is_leap_year] = 365
            da = da / coef * 100
        else:
            # TODO improve this
            warn("% unit can only be used with MONTH or YEAR slice_mode.")
            return da
        da.attrs["units"] = "%"
        return da


def _add_percentile_meta(
    run_bootstrap: bool, result: DataArray, per: DataArray
) -> DataArray:
    if run_bootstrap:
        # TODO Not sufficient in the case of bootstrapping,
        #  we should retrieve the percentiles bootstrapped by xclim to be accurate
        warn(
            f"The percentile values saved in the coordinate variable {PERCENTILES_COORD} "
            f"are inaccurate for the bootstrapped period."
        )
    result.coords[PERCENTILES_COORD] = resample_doy(per, result).squeeze(
        "percentiles", drop=True
    )
    return result


def _add_bootstrap_meta(result: DataArray, per: DataArray) -> DataArray:
    result.attrs[IN_BASE_ATTRS] = per.climatology_bounds
    return result


def _compute_percentiles(config: IndiceConfig, percentile: int) -> DataArray:
    if config.cf_variables[0].in_base_da is not None:
        percentiles_studied = config.cf_variables[0].in_base_da
    else:
        percentiles_studied = config.cf_variables[0].da
    per = percentile_doy(
        percentiles_studied,
        config.window,
        percentile,
        alpha=config.interpolation.alpha,
        beta=config.interpolation.beta,
    )
    if config.callback is not None:
        config.callback(50)
    return per

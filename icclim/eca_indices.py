from enum import Enum
from typing import Callable, Optional, Union
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
        tas=config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def cfd(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.consecutive_frost_days(
        tasmin=config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def fd(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "0.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.frost_days(
        tasmin=config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def hd17(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "17.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.heating_degree_days(
        tas=config.cf_variables[0].da,
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
        config.freq.panda_freq,
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
        config.freq.panda_freq,
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
        config.freq.panda_freq,
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
    return atmos.tx_min(config.cf_variables[0].da, config.freq.panda_freq)


def tnn(config: IndiceConfig) -> DataArray:
    return atmos.tn_min(config.cf_variables[0].da, config.freq.panda_freq)


def cdd(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_dry_days(
        config.cf_variables[0].da, "1.0 mm/day", config.freq.panda_freq
    )


def su(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "25.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.tx_days_above(
        tasmax=config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def tr(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "20.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.tropical_nights(
        tasmin=config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def wsdi(config: IndiceConfig) -> DataArray:
    per_value = 90
    per = _compute_percentiles(config, per_value)
    run_bootstrap = _can_run_bootstrap(config, slice(*per.climatology_bounds))
    result = atmos.warm_spell_duration_index(
        tasmax=config.cf_variables[0].da,
        tx90=per,
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
        tasmax=config.cf_variables[0].da,
        t90=per,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
        # TODO to do on xclim as either a stand alone param or refactor bootstrap param to be a config object
        # interpolation= interpolation
    ).squeeze("percentiles", drop=True)
    if run_bootstrap:
        result = _add_bootstrap_meta(result, per)
    if config.save_percentile:
        result = _add_percentile_meta(run_bootstrap, result, per)
    if config.is_percent:
        result = _to_percent(result, config.freq)
    return result


def txx(config: IndiceConfig) -> DataArray:
    return atmos.tx_max(config.cf_variables[0].da, config.freq.panda_freq)


def tnx(config: IndiceConfig) -> DataArray:
    return atmos.tn_max(config.cf_variables[0].da, config.freq.panda_freq)


def csu(config: IndiceConfig) -> DataArray:
    if config.threshold is None:
        threshold = "25.0 degC"
    else:
        threshold = _add_celsius_suffix(config.threshold)
    return atmos.maximum_consecutive_warm_days(
        tasmax=config.cf_variables[0].da,
        thresh=threshold,
        freq=config.freq.panda_freq,
    )


def prcptot(config: IndiceConfig) -> DataArray:
    return atmos.precip_accumulation(
        pr=config.cf_variables[0].da,
        freq=config.freq.panda_freq,
        # TODO see if we should use tas and thresh
        # tas=config.cf_variables[0].da,
        # thresh=threshold,
    )


def rr1(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(
        config.cf_variables[0].da, "1.0 mm/day", config.freq.panda_freq
    )


def sdii(config: IndiceConfig) -> DataArray:
    return atmos.daily_pr_intensity(
        config.cf_variables[0].da, "1.0 mm/day", config.freq.panda_freq
    )


def cwd(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_wet_days(
        config.cf_variables[0].da, "1.0 mm/day", config.freq.panda_freq
    )


def r10mm(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(config.cf_variables[0].da, "10 mm/day", config.freq.panda_freq)


def r20mm(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(config.cf_variables[0].da, "20 mm/day", config.freq.panda_freq)


def rx1day(config: IndiceConfig) -> DataArray:
    return atmos.max_1day_precipitation_amount(
        config.cf_variables[0].da, config.freq.panda_freq
    )


def rx5day(config: IndiceConfig) -> DataArray:
    return atmos.max_n_day_precipitation_amount(
        config.cf_variables[0].da, 5, config.freq.panda_freq
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
    return land.snow_depth(config.cf_variables[0].da, config.freq.panda_freq)


def sd1(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(
        config.cf_variables[0].da, "1 cm", config.freq.panda_freq
    )


def sd5cm(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(
        config.cf_variables[0].da, "5 cm", config.freq.panda_freq
    )


def sd50cm(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(
        config.cf_variables[0].da, "50 cm", config.freq.panda_freq
    )


def tg(config: IndiceConfig) -> DataArray:
    return atmos.tg_mean(config.cf_variables[0].da, config.freq.panda_freq)


def tn(config: IndiceConfig) -> DataArray:
    return atmos.tg_min(config.cf_variables[0].da, config.freq.panda_freq)


def tx(config: IndiceConfig) -> DataArray:
    return atmos.tg_max(config.cf_variables[0].da, config.freq.panda_freq)


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
    per_value = 25
    tas_per = _compute_percentiles(config, per_value)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=25).sel(percentiles=25)
    result = atmos.cold_and_wet_days(
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
    per_value = 25
    tas_per = _compute_percentiles(config, per_value)
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
    per_value = 75
    tas_per = _compute_percentiles(config, per_value)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=25).sel(percentiles=25)
    result = atmos.cold_and_wet_days(
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
    per_value = 75
    tas_per = _compute_percentiles(config, per_value)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=config.window, per=75).sel(percentiles=75)
    result = atmos.cold_and_wet_days(
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


class Indice(Enum):
    # temperature
    TG = ("tg", tg, TEMPERATURE_GROUP)
    TN = ("tn", tn, TEMPERATURE_GROUP)
    TX = ("tx", tx, TEMPERATURE_GROUP)
    DTR = ("dtr", dtr, TEMPERATURE_GROUP)
    ETR = ("etr", etr, TEMPERATURE_GROUP)
    VDTR = ("vdtr", vdtr, TEMPERATURE_GROUP)
    # heat
    SU = ("su", su, HEAT_GROUP)
    TR = ("tr", tr, HEAT_GROUP)
    WSDI = ("wsdi", wsdi, HEAT_GROUP)
    TG90P = ("tg90p", tg90p, HEAT_GROUP)
    TN90P = ("tn90p", tn90p, HEAT_GROUP)
    TX90P = ("tx90p", tx90p, HEAT_GROUP)
    TXX = ("txx", txx, HEAT_GROUP)
    TNX = ("tnx", tnx, HEAT_GROUP)
    CSU = ("csu", csu, HEAT_GROUP)
    # cold
    GD4 = ("gd4", gd4, COLD_GROUP)
    FD = ("fd", fd, COLD_GROUP)
    CFD = ("cfd", cfd, COLD_GROUP)
    HD17 = ("hd17", hd17, COLD_GROUP)
    ID = ("id", id, COLD_GROUP)
    TG10P = ("tg10p", tg10p, COLD_GROUP)
    TN10P = ("tn10p", tn10p, COLD_GROUP)
    TX10P = ("tx10p", tx10p, COLD_GROUP)
    TXN = ("txn", txn, COLD_GROUP)
    TNN = ("tnn", tnn, COLD_GROUP)
    CSDI = ("csdi", csdi, COLD_GROUP)
    # drought
    CDD = ("cdd", cdd, DROUGHT_GROUP)
    # rain
    PRCPTOT = ("prcptot", prcptot, RAIN_GROUP)
    RR1 = ("rr1", rr1, RAIN_GROUP)
    SDII = ("sdii", sdii, RAIN_GROUP)
    CWD = ("cwd", cwd, RAIN_GROUP)
    R10MM = ("r10mm", r10mm, RAIN_GROUP)
    R20MM = ("r20mm", r20mm, RAIN_GROUP)
    RX1DAY = ("rx1day", rx1day, RAIN_GROUP)
    RX5DAY = ("rx5day", rx5day, RAIN_GROUP)
    R75P = ("r75p", r75p, RAIN_GROUP)
    R75PTOT = ("r75ptot", r75ptot, RAIN_GROUP)
    R95P = ("r95p", r95p, RAIN_GROUP)
    R95PTOT = ("r95ptot", r95ptot, RAIN_GROUP)
    R99P = ("r99p", r99p, RAIN_GROUP)
    R99PTOT = ("r99ptot", r99ptot, RAIN_GROUP)
    # snow
    SD = ("sd", sd, SNOW_GROUP)
    SD1 = ("sd1", sd1, SNOW_GROUP)
    SD5CM = ("sd5cm", sd5cm, SNOW_GROUP)
    SD50CM = ("sd50cm", sd50cm, SNOW_GROUP)
    # compound
    CD = ("cd", cd, COMPOUND_GROUP)
    CW = ("cw", cw, COMPOUND_GROUP)
    WD = ("wd", wd, COMPOUND_GROUP)
    WW = ("ww", ww, COMPOUND_GROUP)

    def __init__(
        self,
        indice_name: str,
        compute: Callable[[IndiceConfig], DataArray],
        group: str,
    ):
        self.indice_name = indice_name
        self.compute = compute
        self.group = group


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
        #  we should retrieve all the bootstrapped years for these percentiles to be accurate
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
    per = percentile_doy(
        config.cf_variables[0].in_base_da,
        config.window,
        percentile,
        alpha=config.interpolation.alpha,
        beta=config.interpolation.beta,
    )
    if config.callback is not None:
        config.callback(50)
    return per

from enum import Enum
from typing import Callable, Optional, Union

from xarray import DataArray
from xarray.core.dataset import Dataset
from xclim import atmos, land
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to

from icclim.models.indice_config import IndiceConfig
from icclim.models.quantile_interpolation import QuantileInterpolation

PERCENTILES_COORD = "percentiles"


def gd4(config: IndiceConfig) -> DataArray:
    return atmos.growing_degree_days(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def cfd(config: IndiceConfig) -> DataArray:
    return atmos.consecutive_frost_days(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def fd(config: IndiceConfig) -> DataArray:
    return atmos.frost_days(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def hd17(config: IndiceConfig) -> DataArray:
    return atmos.heating_degree_days(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def id(config: IndiceConfig) -> DataArray:
    return atmos.ice_days(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def csdi(config: IndiceConfig) -> DataArray:
    run_bootstrap = config.cf_variables[0].in_base_da is not None
    if run_bootstrap and config.interpolation != QuantileInterpolation.MEDIAN_UNBIASED:
        raise Exception(
            "The bootstrapping can only use hyndman_fan method 8 (MEDIAN_UNBIASED)"
            "to compute the percentiles"
        )
    per_10 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 10).sel(
        percentiles=10
    )
    result = atmos.cold_spell_duration_index(
        config.cf_variables[0].da,
        per_10,
        window=6,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_10, result)
    return result


def tg10p(config: IndiceConfig) -> DataArray:
    run_bootstrap = config.cf_variables[0].in_base_da is not None
    if run_bootstrap and config.interpolation != QuantileInterpolation.MEDIAN_UNBIASED:
        raise Exception(
            "The bootstrapping can only use hyndman_fan method 8 (MEDIAN_UNBIASED)"
            "to compute the percentiles"
        )
    per_10 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 10).sel(
        percentiles=10
    )
    result = atmos.tg10p(
        config.cf_variables[0].da,
        per_10,
        config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_10, result)
    return result


def tn10p(config: IndiceConfig) -> Dataset:
    run_bootstrap = _can_run_bootstrap(config)
    per_10 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 10).sel(
        percentiles=10
    )
    result = atmos.tn10p(
        config.cf_variables[0].da,
        per_10,
        config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_10, result)
    return result


def tx10p(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per_10 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 10).sel(
        percentiles=10
    )
    result = atmos.tx10p(
        config.cf_variables[0].da,
        per_10,
        config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_10, result)
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
    return atmos.tx_days_above(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def tr(config: IndiceConfig) -> DataArray:
    return atmos.tropical_nights(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def wsdi(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per_90 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 90).sel(
        percentiles=90
    )
    result = atmos.warm_spell_duration_index(
        config.cf_variables[0].da,
        per_90,
        6,
        config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_90, result)
    return result


def tg90p(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per_90 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 90).sel(
        percentiles=90
    )
    result = atmos.tg90p(
        config.cf_variables[0].da,
        per_90,
        config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_90, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def tn90p(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per_90 = percentile_doy(config.cf_variables[0].in_base_da, config.window, 90).sel(
        percentiles=90
    )
    result = atmos.tn90p(
        config.cf_variables[0].da,
        per_90,
        config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_90, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def tx90p(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per_90 = percentile_doy(
        config.cf_variables[0].in_base_da,
        config.window,
        90,
        config.interpolation.alpha,
        config.interpolation.beta,
    )
    result = atmos.tx90p(
        tasmax=config.cf_variables[0].da,
        t90=per_90,
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
        # TODO to do on xclim as either a stand alone param or refactor bootstrap param to be a config object
        # interpolation= interpolation
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per_90, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def txx(config: IndiceConfig) -> DataArray:
    return atmos.tx_max(config.cf_variables[0].da, config.freq.panda_freq)


def tnx(config: IndiceConfig) -> DataArray:
    return atmos.tn_max(config.cf_variables[0].da, config.freq.panda_freq)


def csu(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_warm_days(
        config.cf_variables[0].da,
        _add_celsius_suffix(config.threshold),
        config.freq.panda_freq,
    )


def prcptot(config: IndiceConfig) -> DataArray:
    return atmos.precip_accumulation(
        pr=config.cf_variables[0].da,
        tas=None,
        phase=None,
        thresh=_add_celsius_suffix(config.threshold),
        freq=config.freq.panda_freq,
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
    run_bootstrap = _can_run_bootstrap(config)
    per = percentile_doy(config.cf_variables[0].in_base_da, config.window, 75).sel(
        percentiles=75
    )
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
        # TODO maybe it's not a good idea to bootstrap on precipitations, especially in percentiles so far from 99
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def r75ptot(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per = percentile_doy(config.cf_variables[0].in_base_da, config.window, 75).sel(
        percentiles=75
    )
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
        # TODO maybe it's not a good idea to bootstrap on precipitations, especially in percentiles so far from 99
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def r95p(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per = percentile_doy(config.cf_variables[0].in_base_da, config.window, 95).sel(
        percentiles=95
    )
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def r95ptot(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per = percentile_doy(config.cf_variables[0].in_base_da, config.window, 95).sel(
        percentiles=95
    )
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def r99p(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per = percentile_doy(config.cf_variables[0].in_base_da, config.window, 99).sel(
        percentiles=99
    )
    result = atmos.days_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
    return result


def r99ptot(config: IndiceConfig) -> DataArray:
    run_bootstrap = _can_run_bootstrap(config)
    per = percentile_doy(config.cf_variables[0].in_base_da, config.window, 99).sel(
        percentiles=99
    )
    result = atmos.fraction_over_precip_thresh(
        config.cf_variables[0].da,
        per,
        thresh="1 mm/day",
        freq=config.freq.panda_freq,
        bootstrap=run_bootstrap,
    )
    if config.save_percentile:
        result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    if config.is_percent:
        result = result / len(config.cf_variables[0].da.time) * 100
        result.attrs["units"] = "%"
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
    tas_per = percentile_doy(
        config.cf_variables[0].in_base_da, window=config.window, per=25
    ).sel(percentiles=25)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=5, per=25).sel(percentiles=25)
    result = atmos.cold_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_25=tas_per,
        pr=config.cf_variables[1].da,
        pr_25=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def cw(config: IndiceConfig) -> DataArray:
    tas_per = percentile_doy(
        config.cf_variables[0].in_base_da, window=config.window, per=25
    ).sel(percentiles=25)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=5, per=75).sel(percentiles=75)
    result = atmos.cold_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_25=tas_per,
        pr=config.cf_variables[1].da,
        pr_75=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def wd(config: IndiceConfig) -> DataArray:
    tas_per = percentile_doy(
        config.cf_variables[0].in_base_da, window=config.window, per=75
    ).sel(percentiles=75)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=5, per=25).sel(percentiles=25)
    result = atmos.cold_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_75=tas_per,
        pr=config.cf_variables[1].da,
        pr_25=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


def ww(config: IndiceConfig) -> DataArray:
    tas_per = percentile_doy(
        config.cf_variables[0].in_base_da, window=config.window, per=75
    ).sel(percentiles=75)
    precip = convert_units_to(config.cf_variables[1].in_base_da, "mm/d")
    precip = precip.where(precip > 1, drop=True)
    pr_per = percentile_doy(precip, window=5, per=75).sel(percentiles=75)
    result = atmos.cold_and_wet_days(
        tas=config.cf_variables[0].da,
        tas_75=tas_per,
        pr=config.cf_variables[1].da,
        pr_75=pr_per,
        freq=config.freq.panda_freq,
    )
    if config.save_percentile:
        result.coords["tas_per"] = resample_doy(tas_per, result)
        result.coords["pr_per"] = resample_doy(pr_per, result)
    return result


class Indice(Enum):
    TEMPERATURE_GROUP = "temperature"
    HEAT_GROUP = "heat"
    COLD_GROUP = "cold"
    DROUGHT_GROUP = "drought"
    RAIN_GROUP = "rain"
    SNOW_GROUP = "snow"
    COMPOUND_GROUP = "compound"
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
    raise Exception(f"Unknown indice {s}")


def _add_celsius_suffix(threshold: Optional[Union[str, float, int]]) -> Optional[str]:
    if threshold is not None:
        return f"{threshold} degC"
    return None


def _can_run_bootstrap(config: IndiceConfig) -> bool:
    run_bootstrap = config.cf_variables[0].in_base_da is not None
    if run_bootstrap and config.interpolation != QuantileInterpolation.MEDIAN_UNBIASED:
        raise Exception(
            "The bootstrapping can only use hyndman_fan method 8 (MEDIAN_UNBIASED)"
            "to compute the percentiles"
        )
    return run_bootstrap

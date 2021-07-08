from enum import Enum
from icclim.models.indice_config import IndiceConfig
from typing import Callable
from xclim import atmos, land
from xarray import DataArray

from xclim.core.calendar import percentile_doy


def gd4(config: IndiceConfig) -> DataArray:
    return atmos.growing_degree_days(
        config.data_arrays[0], config.threshold, config.freq
    )


def cfd(config: IndiceConfig) -> DataArray:
    return atmos.consecutive_frost_days(
        config.data_arrays[0], config.threshold, config.freq
    )


def fd(config: IndiceConfig) -> DataArray:
    return atmos.frost_days(config.data_arrays[0], config.threshold, config.freq)


def hd17(config: IndiceConfig) -> DataArray:
    return atmos.heating_degree_days(
        config.data_arrays[0], config.threshold, config.freq
    )


def id(config: IndiceConfig) -> DataArray:
    return atmos.ice_days(config.data_arrays[0], config.threshold, config.freq)


def csdi(config: IndiceConfig) -> DataArray:
    return atmos.cold_spell_duration_index(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 10),
        window=6,
        freq=config.freq,
        bootstrap=True,
    )


def tg10p(config: IndiceConfig) -> DataArray:
    return atmos.tg10p(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 10),
        config.freq,
        True,
    )


def tn10p(config: IndiceConfig) -> DataArray:
    return atmos.tn10p(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 10),
        config.freq,
        True,
    )


def tx10p(config: IndiceConfig) -> DataArray:
    return atmos.tx10p(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 10),
        config.freq,
        True,
    )


def txn(config: IndiceConfig) -> DataArray:
    return atmos.tx_min(config.data_arrays[0], config.freq)


def tnn(config: IndiceConfig) -> DataArray:
    return atmos.tn_min(config.data_arrays[0], config.freq)


def cdd(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_dry_days(config.da, "1.0 mm/day", config.freq)


def su(config: IndiceConfig) -> DataArray:
    return atmos.tx_days_above(config.data_arrays[0], config.threshold, config.freq)


def tr(config: IndiceConfig) -> DataArray:
    return atmos.tropical_nights(config.data_arrays[0], config.threshold, config.freq)


def wsdi(config: IndiceConfig) -> DataArray:
    return atmos.warm_spell_duration_index(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 90),
        6,
        config.freq,
        True,
    )


def tg90p(config: IndiceConfig) -> DataArray:
    return atmos.tg90p(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 90),
        config.freq,
        True,
    )


def tn90p(config: IndiceConfig) -> DataArray:
    return atmos.tn90p(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 90),
        config.freq,
        True,
    )


def tx90p(config: IndiceConfig) -> DataArray:
    return atmos.tx90p(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 90),
        config.freq,
        True,
    )


def txx(config: IndiceConfig) -> DataArray:
    return atmos.tx_max(config.data_arrays[0], config.freq)


def tnx(config: IndiceConfig) -> DataArray:
    return atmos.tn_max(config.data_arrays[0], config.freq)


def csu(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_warm_days(
        config.data_arrays[0], config.threshold, config.freq
    )


def prcptot(config: IndiceConfig) -> DataArray:
    return atmos.precip_accumulation(
        pr=config.data_arrays[0],
        tas=None,
        phase=None,
        thresh=config.threshold,
        freq=config.freq,
    )


def rr1(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(config.data_arrays[0], "1.0 mm/day", config.freq)


def sdii(config: IndiceConfig) -> DataArray:
    return atmos.daily_pr_intensity(config.data_arrays[0], "1.0 mm/day", config.freq)


def cwd(config: IndiceConfig) -> DataArray:
    return atmos.maximum_consecutive_wet_days(
        config.data_arrays[0], "1.0 mm/day", config.freq
    )


def r10mm(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(config.data_arrays[0], "10 mm/day", config.freq)


def r20mm(config: IndiceConfig) -> DataArray:
    return atmos.wetdays(config.data_arrays[0], "20 mm/day", config.freq)


def rx1day(config: IndiceConfig) -> DataArray:
    return atmos.max_1day_precipitation_amount(config.data_arrays[0], config.freq)


def rx5day(config: IndiceConfig) -> DataArray:
    return atmos.max_n_day_precipitation_amount(config.data_arrays[0], 5, config.freq)


def r75p(config: IndiceConfig) -> DataArray:
    return atmos.days_over_precip_thresh(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 75),
        thresh="1 mm/day",
        freq=config.freq,
        bootstrap=True,  # TODO maybe it's not a good idea to bootstrap on precipitations, especially in percentiles so far from 99
    )


def r75ptot(config: IndiceConfig) -> DataArray:
    return atmos.fraction_over_precip_thresh(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 75),
        thresh="1 mm/day",
        freq=config.freq,
        bootstrap=True,  # TODO maybe it's not a good idea to bootstrap on precipitations, especially in percentiles so far from 99
    )


def r95p(config: IndiceConfig) -> DataArray:
    return atmos.days_over_precip_thresh(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 95),
        thresh="1 mm/day",
        freq=config.freq,
        bootstrap=True,  # TODO maybe it's not a good idea to bootstrap on precipitations
    )


def r95ptot(config: IndiceConfig) -> DataArray:
    return atmos.fraction_over_precip_thresh(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 95),
        thresh="1 mm/day",
        freq=config.freq,
        bootstrap=True,  # TODO maybe it's not a good idea to bootstrap on precipitations
    )


def r99p(config: IndiceConfig) -> DataArray:
    return atmos.days_over_precip_thresh(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 99),
        thresh="1 mm/day",
        freq=config.freq,
        bootstrap=True,  # TODO maybe it's not a good idea to bootstrap on precipitations
    )


def r99ptot(config: IndiceConfig) -> DataArray:
    return atmos.fraction_over_precip_thresh(
        config.data_arrays[0],
        percentile_doy(config.data_arrays_in_base[0], config.window, 99),
        thresh="1 mm/day",
        freq=config.freq,
        bootstrap=True,  # TODO maybe it's not a good idea to bootstrap on precipitations
    )


def sd(config: IndiceConfig) -> DataArray:
    # TODO
    raise NotImplemented("not yet implemented on xclim")


def sd1(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(config.data_arrays[0], "1 cm", config.freq)


def sd5cm(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(config.data_arrays[0], "5 cm", config.freq)


def sd50cm(config: IndiceConfig) -> DataArray:
    return land.snow_cover_duration(config.data_arrays[0], "50 cm", config.freq)


def tg(config: IndiceConfig) -> DataArray:
    return atmos.tg_mean(config.data_arrays[0], config.freq)


def tn(config: IndiceConfig) -> DataArray:
    return atmos.tg_min(config.data_arrays[0], config.freq)


def tx(config: IndiceConfig) -> DataArray:
    return atmos.tg_max(config.data_arrays[0], config.freq)


def dtr(config: IndiceConfig) -> DataArray:
    return atmos.daily_temperature_range(
        tasmin=config.data_arrays[0], tasmax=config.data_arrays[1], freq=config.freq
    )


def etr(config: IndiceConfig) -> DataArray:
    return atmos.extreme_temperature_range(
        tasmin=config.data_arrays[0], tasmax=config.data_arrays[1], freq=config.freq
    )


def vdtr(config: IndiceConfig) -> DataArray:
    return atmos.daily_temperature_range_variability(
        tasmin=config.data_arrays[0], tasmax=config.data_arrays[1], freq=config.freq
    )


def cd(config: IndiceConfig) -> DataArray:
    # TODO
    raise NotImplemented(
        "not yet implemented on xclim, see cold_and_dry_days in _multivariate.py"
    )


def cw(config: IndiceConfig) -> DataArray:
    # TODO
    raise NotImplemented("not yet implemented on xclim")


def wd(config: IndiceConfig) -> DataArray:
    # TODO
    raise NotImplemented("not yet implemented on xclim")


def ww(config: IndiceConfig) -> DataArray:
    # TODO
    raise NotImplemented("not yet implemented on xclim")


class Indice(Enum):
    GD4 = gd4
    TX90P = tx90p
    CFD = cfd
    FD = fd
    HD17 = hd17
    ID = id
    CSDI = csdi
    TG10P = tg10p
    TN10P = tn10p
    TX10P = tx10p
    TXN = txn
    TNN = tnn
    CDD = cdd
    SU = su
    TR = tr
    WSDI = wsdi
    TG90P = tg90p
    TN90P = tn90p
    TXX = txx
    TNX = tnx
    CSU = csu
    PRCPTOT = prcptot
    RR1 = rr1
    SDII = sdii
    CWD = cwd
    R10MM = r10mm
    R20MM = r20mm
    RX1DAY = rx1day
    RX5DAY = rx5day
    R75P = r75p
    R75PTOT = r75ptot
    R95P = r95p
    R95PTOT = r95ptot
    R99P = r99p
    R99PTOT = r99ptot
    SD = sd
    SD1 = sd1
    SD5CM = sd5cm
    SD50CM = sd50cm
    TG = tg
    TN = tn
    TX = tx
    DTR = dtr
    ETR = etr
    VDTR = vdtr
    CD = cd
    CW = cw
    WD = wd
    WW = ww

    def __init__(self, compute):
        self.compute: Callable[[IndiceConfig], DataArray] = compute


def indice_from_string(s: str) -> Indice:
    indice_to_check = s.upper()
    for e in Indice:
        if e.name == indice_to_check:
            return e
    raise Exception(f"Unknown indice {s}")


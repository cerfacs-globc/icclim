from enum import Enum
from typing import List

from icclim.ecad_functions import (
    ComputeIndexFun,
    cd,
    cdd,
    cfd,
    csdi,
    csu,
    cw,
    cwd,
    dtr,
    etr,
    fd,
    gd4,
    hd17,
    id,
    prcptot,
    r10mm,
    r20mm,
    r75p,
    r75ptot,
    r95p,
    r95ptot,
    r99p,
    r99ptot,
    rr1,
    rx1day,
    rx5day,
    sd,
    sd1,
    sd5cm,
    sd50cm,
    sdii,
    su,
    tg,
    tg10p,
    tg90p,
    tn,
    tn10p,
    tn90p,
    tnn,
    tnx,
    tr,
    tx,
    tx10p,
    tx90p,
    txn,
    txx,
    vdtr,
    wd,
    wsdi,
    ww,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
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


class EcadIndex(Enum):
    """
    ECA&D indices.
        index_name: str
            The index name, case insensitive.
        compute: Callable
            The function to compute the index. It wraps Xclim functions.
        group: str
            The index group category.
        variables: List[List[str]]
            The Cf variables needed to compute the index.
            The variable are individually described by a list of aliases.
        time_aware: bool
            Whether the indice is computed on a single time tick or use a rolling
            windows or may be bootstrapped. This is useful to optimize dask chunking.
    """

    # temperature
    TG = ("tg", tg, TEMPERATURE_GROUP, [TAS], False)
    TN = ("tn", tn, TEMPERATURE_GROUP, [TASMIN], False)
    TX = ("tx", tx, TEMPERATURE_GROUP, [TASMAX], False)
    DTR = ("dtr", dtr, TEMPERATURE_GROUP, [TASMAX, TASMIN], False)
    ETR = ("etr", etr, TEMPERATURE_GROUP, [TASMAX, TASMIN], False)
    VDTR = ("vdtr", vdtr, TEMPERATURE_GROUP, [TASMAX, TASMIN], False)
    # heat
    SU = ("su", su, HEAT_GROUP, [TASMAX], False)
    TR = ("tr", tr, HEAT_GROUP, [TASMIN], False)
    WSDI = ("wsdi", wsdi, HEAT_GROUP, [TASMAX], True)
    TG90P = ("tg90p", tg90p, HEAT_GROUP, [TAS], True)
    TN90P = ("tn90p", tn90p, HEAT_GROUP, [TASMIN], True)
    TX90P = ("tx90p", tx90p, HEAT_GROUP, [TASMAX], True)
    TXX = ("txx", txx, HEAT_GROUP, [TASMAX], False)
    TNX = ("tnx", tnx, HEAT_GROUP, [TASMIN], False)
    CSU = ("csu", csu, HEAT_GROUP, [TASMAX], True)
    # cold
    GD4 = ("gd4", gd4, COLD_GROUP, [TAS], False)
    FD = ("fd", fd, COLD_GROUP, [TASMIN], False)
    CFD = ("cfd", cfd, COLD_GROUP, [TASMIN], True)
    HD17 = ("hd17", hd17, COLD_GROUP, [TASMIN], False)
    ID = ("id", id, COLD_GROUP, [TASMAX], False)
    TG10P = ("tg10p", tg10p, COLD_GROUP, [TAS], True)
    TN10P = ("tn10p", tn10p, COLD_GROUP, [TASMIN], True)
    TX10P = ("tx10p", tx10p, COLD_GROUP, [TASMAX], True)
    TXN = ("txn", txn, COLD_GROUP, [TASMAX], False)
    TNN = ("tnn", tnn, COLD_GROUP, [TASMIN], False)
    CSDI = ("csdi", csdi, COLD_GROUP, [TASMIN], True)
    # drought
    CDD = ("cdd", cdd, DROUGHT_GROUP, [PR], True)
    # rain
    PRCPTOT = ("prcptot", prcptot, RAIN_GROUP, [PR], False)
    RR1 = ("rr1", rr1, RAIN_GROUP, [PR], False)
    SDII = ("sdii", sdii, RAIN_GROUP, [PR], False)
    CWD = ("cwd", cwd, RAIN_GROUP, [PR], True)
    R10MM = ("r10mm", r10mm, RAIN_GROUP, [PR], False)
    R20MM = ("r20mm", r20mm, RAIN_GROUP, [PR], False)
    RX1DAY = ("rx1day", rx1day, RAIN_GROUP, [PR], False)
    RX5DAY = ("rx5day", rx5day, RAIN_GROUP, [PR], True)
    R75P = ("r75p", r75p, RAIN_GROUP, [PR], True)
    R75PTOT = ("r75ptot", r75ptot, RAIN_GROUP, [PR], True)
    R95P = ("r95p", r95p, RAIN_GROUP, [PR], True)
    R95PTOT = ("r95ptot", r95ptot, RAIN_GROUP, [PR], True)
    R99P = ("r99p", r99p, RAIN_GROUP, [PR], True)
    R99PTOT = ("r99ptot", r99ptot, RAIN_GROUP, [PR], True)
    # snow
    SD = ("sd", sd, SNOW_GROUP, [PR], False)
    SD1 = ("sd1", sd1, SNOW_GROUP, [PR], False)
    SD5CM = ("sd5cm", sd5cm, SNOW_GROUP, [PR], False)
    SD50CM = ("sd50cm", sd50cm, SNOW_GROUP, [PR], False)
    # compound
    CD = ("cd", cd, COMPOUND_GROUP, [TAS, PR], True)
    CW = ("cw", cw, COMPOUND_GROUP, [TAS, PR], True)
    WD = ("wd", wd, COMPOUND_GROUP, [TAS, PR], True)
    WW = ("ww", ww, COMPOUND_GROUP, [TAS, PR], True)

    def __init__(
        self,
        indice_name: str,
        compute: ComputeIndexFun,
        group: str,
        variables: List[List[str]],
        time_aware: bool,
    ):
        self.index_name = indice_name
        self.compute = compute
        self.group = group
        self.variables = variables
        self.time_aware = time_aware


def index_from_string(s: str) -> EcadIndex:
    indice_to_check = s.upper()
    for e in EcadIndex:
        if e.index_name.upper() == indice_to_check:
            return e
    raise InvalidIcclimArgumentError(f"Unknown index {s}")

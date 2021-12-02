from enum import Enum
from typing import Any, List

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
    TG = ("TG", tg, TEMPERATURE_GROUP, [TAS], False)
    TN = ("TN", tn, TEMPERATURE_GROUP, [TASMIN], False)
    TX = ("TX", tx, TEMPERATURE_GROUP, [TASMAX], False)
    DTR = ("DTR", dtr, TEMPERATURE_GROUP, [TASMAX, TASMIN], False)
    ETR = ("ETR", etr, TEMPERATURE_GROUP, [TASMAX, TASMIN], False)
    VDTR = ("vDTR", vdtr, TEMPERATURE_GROUP, [TASMAX, TASMIN], False)
    # heat
    SU = ("SU", su, HEAT_GROUP, [TASMAX], False)
    TR = ("TR", tr, HEAT_GROUP, [TASMIN], False)
    WSDI = ("WSDI", wsdi, HEAT_GROUP, [TASMAX], True)
    TG90P = ("TG90p", tg90p, HEAT_GROUP, [TAS], True)
    TN90P = ("TN90p", tn90p, HEAT_GROUP, [TASMIN], True)
    TX90P = ("TX90p", tx90p, HEAT_GROUP, [TASMAX], True)
    TXX = ("TXx", txx, HEAT_GROUP, [TASMAX], False)
    TNX = ("TNx", tnx, HEAT_GROUP, [TASMIN], False)
    CSU = ("CSU", csu, HEAT_GROUP, [TASMAX], True)
    # cold
    GD4 = ("GD4", gd4, COLD_GROUP, [TAS], False)
    FD = ("FD", fd, COLD_GROUP, [TASMIN], False)
    CFD = ("CFD", cfd, COLD_GROUP, [TASMIN], True)
    HD17 = ("HD17", hd17, COLD_GROUP, [TASMIN], False)
    ID = ("ID", id, COLD_GROUP, [TASMAX], False)
    TG10P = ("TG10p", tg10p, COLD_GROUP, [TAS], True)
    TN10P = ("TN10p", tn10p, COLD_GROUP, [TASMIN], True)
    TX10P = ("TX10p", tx10p, COLD_GROUP, [TASMAX], True)
    TXN = ("TXn", txn, COLD_GROUP, [TASMAX], False)
    TNN = ("TNn", tnn, COLD_GROUP, [TASMIN], False)
    CSDI = ("CSDI", csdi, COLD_GROUP, [TASMIN], True)
    # drought
    CDD = ("CDD", cdd, DROUGHT_GROUP, [PR], True)
    # rain
    PRCPTOT = ("PRCPTOT", prcptot, RAIN_GROUP, [PR], False)
    RR1 = ("RR1", rr1, RAIN_GROUP, [PR], False)
    SDII = ("SDII", sdii, RAIN_GROUP, [PR], False)
    CWD = ("CWD", cwd, RAIN_GROUP, [PR], True)
    R10MM = ("R10mm", r10mm, RAIN_GROUP, [PR], False)
    R20MM = ("R20mm", r20mm, RAIN_GROUP, [PR], False)
    RX1DAY = ("RX1day", rx1day, RAIN_GROUP, [PR], False)
    RX5DAY = ("RX5day", rx5day, RAIN_GROUP, [PR], True)
    R75P = ("R75p", r75p, RAIN_GROUP, [PR], True)
    R75PTOT = ("R75pTOT", r75ptot, RAIN_GROUP, [PR], True)
    R95P = ("R95p", r95p, RAIN_GROUP, [PR], True)
    R95PTOT = ("R95pTOT", r95ptot, RAIN_GROUP, [PR], True)
    R99P = ("R99p", r99p, RAIN_GROUP, [PR], True)
    R99PTOT = ("R99pTOT", r99ptot, RAIN_GROUP, [PR], True)
    # snow
    SD = ("SD", sd, SNOW_GROUP, [PR], False)
    SD1 = ("SD1", sd1, SNOW_GROUP, [PR], False)
    SD5CM = ("SD5cm", sd5cm, SNOW_GROUP, [PR], False)
    SD50CM = ("SD50cm", sd50cm, SNOW_GROUP, [PR], False)
    # compound
    CD = ("CD", cd, COMPOUND_GROUP, [TAS, PR], True)
    CW = ("CW", cw, COMPOUND_GROUP, [TAS, PR], True)
    WD = ("WD", wd, COMPOUND_GROUP, [TAS, PR], True)
    WW = ("WW", ww, COMPOUND_GROUP, [TAS, PR], True)

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

    @staticmethod
    def lookup(query: str) -> Any:
        indice_to_check = query.upper()
        for e in EcadIndex:
            if e.index_name.upper() == indice_to_check:
                return e
        raise InvalidIcclimArgumentError(f"Unknown index {query}.")

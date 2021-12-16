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
    TAS_MAX,
    TAS_MIN,
    TEMPERATURE_GROUP,
)


class EcadIndex(Enum):
    """
    ECA&D indices.
        index_name: str
            The index name used in the output.
        compute: Callable
            The function to compute the index. It wraps Xclim functions.
        group: str
            The index group category. one of
            `{"temperature", "heat", "cold", "drought", "rain", "snow", "compound"}`
        variables: List[List[str]]
            The Cf variables needed to compute the index.
            The variable are individually described by a list of aliases.
    """

    # temperature
    TG = ("TG", tg, TEMPERATURE_GROUP, [TAS])
    TN = ("TN", tn, TEMPERATURE_GROUP, [TAS_MIN])
    TX = ("TX", tx, TEMPERATURE_GROUP, [TAS_MAX])
    DTR = ("DTR", dtr, TEMPERATURE_GROUP, [TAS_MAX, TAS_MIN])
    ETR = ("ETR", etr, TEMPERATURE_GROUP, [TAS_MAX, TAS_MIN])
    VDTR = ("vDTR", vdtr, TEMPERATURE_GROUP, [TAS_MAX, TAS_MIN])
    # heat
    SU = ("SU", su, HEAT_GROUP, [TAS_MAX])
    TR = ("TR", tr, HEAT_GROUP, [TAS_MIN])
    WSDI = ("WSDI", wsdi, HEAT_GROUP, [TAS_MAX])
    TG90P = ("TG90p", tg90p, HEAT_GROUP, [TAS])
    TN90P = ("TN90p", tn90p, HEAT_GROUP, [TAS_MIN])
    TX90P = ("TX90p", tx90p, HEAT_GROUP, [TAS_MAX])
    TXX = ("TXx", txx, HEAT_GROUP, [TAS_MAX])
    TNX = ("TNx", tnx, HEAT_GROUP, [TAS_MIN])
    CSU = ("CSU", csu, HEAT_GROUP, [TAS_MAX])
    # cold
    GD4 = ("GD4", gd4, COLD_GROUP, [TAS])
    FD = ("FD", fd, COLD_GROUP, [TAS_MIN])
    CFD = ("CFD", cfd, COLD_GROUP, [TAS_MIN])
    HD17 = ("HD17", hd17, COLD_GROUP, [TAS])
    ID = ("ID", id, COLD_GROUP, [TAS_MAX])
    TG10P = ("TG10p", tg10p, COLD_GROUP, [TAS])
    TN10P = ("TN10p", tn10p, COLD_GROUP, [TAS_MIN])
    TX10P = ("TX10p", tx10p, COLD_GROUP, [TAS_MAX])
    TXN = ("TXn", txn, COLD_GROUP, [TAS_MAX])
    TNN = ("TNn", tnn, COLD_GROUP, [TAS_MIN])
    CSDI = ("CSDI", csdi, COLD_GROUP, [TAS_MIN])
    # drought
    CDD = ("CDD", cdd, DROUGHT_GROUP, [PR])
    # rain
    PRCPTOT = ("PRCPTOT", prcptot, RAIN_GROUP, [PR])
    RR1 = ("RR1", rr1, RAIN_GROUP, [PR])
    SDII = ("SDII", sdii, RAIN_GROUP, [PR])
    CWD = ("CWD", cwd, RAIN_GROUP, [PR])
    R10MM = ("R10mm", r10mm, RAIN_GROUP, [PR])
    R20MM = ("R20mm", r20mm, RAIN_GROUP, [PR])
    RX1DAY = ("RX1day", rx1day, RAIN_GROUP, [PR])
    RX5DAY = ("RX5day", rx5day, RAIN_GROUP, [PR])
    R75P = ("R75p", r75p, RAIN_GROUP, [PR])
    R75PTOT = ("R75pTOT", r75ptot, RAIN_GROUP, [PR])
    R95P = ("R95p", r95p, RAIN_GROUP, [PR])
    R95PTOT = ("R95pTOT", r95ptot, RAIN_GROUP, [PR])
    R99P = ("R99p", r99p, RAIN_GROUP, [PR])
    R99PTOT = ("R99pTOT", r99ptot, RAIN_GROUP, [PR])
    # snow
    SD = ("SD", sd, SNOW_GROUP, [PR])
    SD1 = ("SD1", sd1, SNOW_GROUP, [PR])
    SD5CM = ("SD5cm", sd5cm, SNOW_GROUP, [PR])
    SD50CM = ("SD50cm", sd50cm, SNOW_GROUP, [PR])
    # compound
    CD = ("CD", cd, COMPOUND_GROUP, [TAS, PR])
    CW = ("CW", cw, COMPOUND_GROUP, [TAS, PR])
    WD = ("WD", wd, COMPOUND_GROUP, [TAS, PR])
    WW = ("WW", ww, COMPOUND_GROUP, [TAS, PR])

    def __init__(
        self,
        index_name: str,
        compute: ComputeIndexFun,
        group: str,
        variables: List[List[str]],
    ):
        self.index_name = index_name
        self.compute = compute
        self.group = group
        self.variables = variables

    @staticmethod
    def lookup(query: str) -> Any:
        for e in EcadIndex:
            if e.index_name.upper() == query.upper():
                return e
        raise InvalidIcclimArgumentError(f"Unknown index {query}.")

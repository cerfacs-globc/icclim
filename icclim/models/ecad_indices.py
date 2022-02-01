from enum import Enum
from typing import Any, Callable, List, Optional, Tuple, Union

from xarray import DataArray

from icclim.clix_meta.clix_meta_indices import ClixMetaIndices
from icclim.ecad_functions import (
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
    ECAD_ATBD,
    HEAT_GROUP,
    MODIFIABLE_QUANTILE_WINDOW,
    MODIFIABLE_THRESHOLD,
    MODIFIABLE_UNIT,
    PR,
    QUANTILE_BASED,
    RAIN_GROUP,
    SNOW_GROUP,
    TAS,
    TAS_MAX,
    TAS_MIN,
    TEMPERATURE_GROUP,
)
from icclim.models.index_config import IndexConfig

ComputeIndexFun = Callable[
    [IndexConfig], Union[DataArray, Tuple[DataArray, Optional[DataArray]]]
]

clix_indices: ClixMetaIndices = ClixMetaIndices.get_instance()


class EcadIndex(Enum):
    """
    ECA&D indices.
        index_name: str
            The index name used in the output.
        compute: Callable
            The function to compute the index. It wraps Xclim functions.
        group: str
            The index group category. one of
            ``{"temperature", "heat", "cold", "drought", "rain", "snow", "compound"}``
        variables: List[List[str]]
            The Cf variables needed to compute the index.
            The variable are individually described by a list of aliases.
        qualifiers: List[str]
            ``optional`` List of configuration to compute the index.
            Used internally to generate modules for C3S.
    """

    # Temperature
    TG = (
        "TG",
        lambda c: tg(c),
        TEMPERATURE_GROUP,
        [TAS],
    )
    TN = (
        "TN",
        lambda c: tn(c),
        TEMPERATURE_GROUP,
        [TAS_MIN],
    )
    TX = (
        "TX",
        lambda c: tx(c),
        TEMPERATURE_GROUP,
        [TAS_MAX],
    )
    DTR = (
        "DTR",
        lambda c: dtr(c),
        TEMPERATURE_GROUP,
        [TAS_MAX, TAS_MIN],
    )
    ETR = (
        "ETR",
        lambda c: etr(c),
        TEMPERATURE_GROUP,
        [TAS_MAX, TAS_MIN],
    )
    VDTR = (
        "vDTR",
        lambda c: vdtr(c),
        TEMPERATURE_GROUP,
        [TAS_MAX, TAS_MIN],
    )

    # Heat
    SU = (
        "SU",
        lambda c: su(c),
        HEAT_GROUP,
        [TAS_MAX],
        [MODIFIABLE_THRESHOLD],
    )
    TR = (
        "TR",
        lambda c: tr(c),
        HEAT_GROUP,
        [TAS_MIN],
        [MODIFIABLE_THRESHOLD],
    )
    WSDI = (
        "WSDI",
        lambda c: wsdi(c),
        HEAT_GROUP,
        [TAS_MAX],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TG90P = (
        "TG90p",
        lambda c: tg90p(c),
        HEAT_GROUP,
        [TAS],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TN90P = (
        "TN90p",
        lambda c: tn90p(c),
        HEAT_GROUP,
        [TAS_MIN],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TX90P = (
        "TX90p",
        lambda c: tx90p(c),
        HEAT_GROUP,
        [TAS_MAX],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TXX = (
        "TXx",
        lambda c: txx(c),
        HEAT_GROUP,
        [TAS_MAX],
    )
    TNX = (
        "TNx",
        lambda c: tnx(c),
        HEAT_GROUP,
        [TAS_MIN],
    )
    CSU = (
        "CSU",
        lambda c: csu(c),
        HEAT_GROUP,
        [TAS_MAX],
        [MODIFIABLE_THRESHOLD],
    )

    # Cold
    GD4 = (
        "GD4",
        lambda c: gd4(c),
        COLD_GROUP,
        [TAS],
        [MODIFIABLE_THRESHOLD],
    )
    FD = (
        "FD",
        lambda c: fd(c),
        COLD_GROUP,
        [TAS_MIN],
        [MODIFIABLE_THRESHOLD],
    )
    CFD = (
        "CFD",
        lambda c: cfd(c),
        COLD_GROUP,
        [TAS_MIN],
        [MODIFIABLE_THRESHOLD],
    )
    HD17 = (
        "HD17",
        lambda c: hd17(c),
        COLD_GROUP,
        [TAS],
        [MODIFIABLE_THRESHOLD],
    )
    ID = (
        "ID",
        lambda c: id(c),
        COLD_GROUP,
        [TAS_MAX],
        [MODIFIABLE_THRESHOLD],
    )
    TG10P = (
        "TG10p",
        lambda c: tg10p(c),
        COLD_GROUP,
        [TAS],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TN10P = (
        "TN10p",
        lambda c: tn10p(c),
        COLD_GROUP,
        [TAS_MIN],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TX10P = (
        "TX10p",
        lambda c: tx10p(c),
        COLD_GROUP,
        [TAS_MAX],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TXN = (
        "TXn",
        lambda c: txn(c),
        COLD_GROUP,
        [TAS_MAX],
    )
    TNN = (
        "TNn",
        lambda c: tnn(c),
        COLD_GROUP,
        [TAS_MIN],
    )
    CSDI = (
        "CSDI",
        lambda c: csdi(c),
        COLD_GROUP,
        [TAS_MIN],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )

    # Drought
    CDD = (
        "CDD",
        lambda c: cdd(c),
        DROUGHT_GROUP,
        [PR],
    )

    # Rain
    PRCPTOT = (
        "PRCPTOT",
        lambda c: prcptot(c),
        RAIN_GROUP,
        [PR],
    )
    RR1 = (
        "RR1",
        lambda c: rr1(c),
        RAIN_GROUP,
        [PR],
    )
    SDII = (
        "SDII",
        lambda c: sdii(c),
        RAIN_GROUP,
        [PR],
    )
    CWD = (
        "CWD",
        lambda c: cwd(c),
        RAIN_GROUP,
        [PR],
    )
    R10MM = (
        "R10mm",
        lambda c: r10mm(c),
        RAIN_GROUP,
        [PR],
    )
    R20MM = (
        "R20mm",
        lambda c: r20mm(c),
        RAIN_GROUP,
        [PR],
    )
    RX1DAY = (
        "RX1day",
        lambda c: rx1day(c),
        RAIN_GROUP,
        [PR],
    )
    RX5DAY = (
        "RX5day",
        lambda c: rx5day(c),
        RAIN_GROUP,
        [PR],
    )
    R75P = (
        "R75p",
        lambda c: r75p(c),
        RAIN_GROUP,
        [PR],
        [QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R75PTOT = (
        "R75pTOT",
        lambda c: r75ptot(c),
        RAIN_GROUP,
        [PR],
        [QUANTILE_BASED],
    )
    R95P = (
        "R95p",
        lambda c: r95p(c),
        RAIN_GROUP,
        [PR],
        [QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R95PTOT = (
        "R95pTOT",
        lambda c: r95ptot(c),
        RAIN_GROUP,
        [PR],
        [QUANTILE_BASED],
    )
    R99P = (
        "R99p",
        lambda c: r99p(c),
        RAIN_GROUP,
        [PR],
        [QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R99PTOT = (
        "R99pTOT",
        lambda c: r99ptot(c),
        RAIN_GROUP,
        [PR],
        [QUANTILE_BASED],
    )

    # Snow
    SD = (
        "SD",
        lambda c: sd(c),
        SNOW_GROUP,
        [PR],
    )
    SD1 = (
        "SD1",
        lambda c: sd1(c),
        SNOW_GROUP,
        [PR],
    )
    SD5CM = (
        "SD5cm",
        lambda c: sd5cm(c),
        SNOW_GROUP,
        [PR],
    )
    SD50CM = (
        "SD50cm",
        lambda c: sd50cm(c),
        SNOW_GROUP,
        [PR],
    )

    # Compound (precipitation and temperature)
    CD = (
        "CD",
        lambda c: cd(c),
        COMPOUND_GROUP,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    CW = (
        "CW",
        lambda c: cw(c),
        COMPOUND_GROUP,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WD = (
        "WD",
        lambda c: wd(c),
        COMPOUND_GROUP,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WW = (
        "WW",
        lambda c: ww(c),
        COMPOUND_GROUP,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )

    def __init__(
        self,
        short_name: str,
        compute: ComputeIndexFun,
        group: str,
        variables: List[List[str]],
        qualifiers: List[str] = None,
    ):
        self.short_name = short_name
        self.compute = compute
        self.group = group
        self.variables = variables
        if qualifiers is None:
            qualifiers = []
        self.qualifiers = qualifiers
        definition = ""
        clix_index = clix_indices.lookup(short_name)
        if clix_index is not None:
            definition = clix_index["output"]["long_name"]
        self.definition = definition
        self.source = ECAD_ATBD

    @staticmethod
    def lookup(query: str) -> Any:
        for e in EcadIndex:
            if e.short_name.upper() == query.upper():
                return e
        raise InvalidIcclimArgumentError(f"Unknown index {query}.")

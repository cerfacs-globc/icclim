from __future__ import annotations

from enum import Enum
from typing import Callable, Optional, Tuple, Union

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
    ECAD_ATBD,
    MODIFIABLE_QUANTILE_WINDOW,
    MODIFIABLE_THRESHOLD,
    MODIFIABLE_UNIT,
    PR,
    QUANTILE_BASED,
    TAS,
    TAS_MAX,
    TAS_MIN,
)
from icclim.models.index_config import IndexConfig
from icclim.models.index_group import IndexGroup

ComputeIndexFun = Callable[
    [IndexConfig], Union[DataArray, Tuple[DataArray, Optional[DataArray]]]
]

clix_indices: ClixMetaIndices = ClixMetaIndices.get_instance()


class EcadIndex(Enum):
    """
    ECA&D indices.
        short_name: str
            The index name used in the output.
        compute: Callable
            The function to compute the index. It wraps Xclim functions.
        group: IndexGroup
            The index group category.
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
        IndexGroup.TEMPERATURE,
        [TAS],
    )
    TN = (
        "TN",
        lambda c: tn(c),
        IndexGroup.TEMPERATURE,
        [TAS_MIN],
    )
    TX = (
        "TX",
        lambda c: tx(c),
        IndexGroup.TEMPERATURE,
        [TAS_MAX],
    )
    DTR = (
        "DTR",
        lambda c: dtr(c),
        IndexGroup.TEMPERATURE,
        [TAS_MAX, TAS_MIN],
    )
    ETR = (
        "ETR",
        lambda c: etr(c),
        IndexGroup.TEMPERATURE,
        [TAS_MAX, TAS_MIN],
    )
    VDTR = (
        "vDTR",
        lambda c: vdtr(c),
        IndexGroup.TEMPERATURE,
        [TAS_MAX, TAS_MIN],
    )

    # Heat
    SU = (
        "SU",
        lambda c: su(c),
        IndexGroup.HEAT,
        [TAS_MAX],
        [MODIFIABLE_THRESHOLD],
    )
    TR = (
        "TR",
        lambda c: tr(c),
        IndexGroup.HEAT,
        [TAS_MIN],
        [MODIFIABLE_THRESHOLD],
    )
    WSDI = (
        "WSDI",
        lambda c: wsdi(c),
        IndexGroup.HEAT,
        [TAS_MAX],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_THRESHOLD],
    )
    TG90P = (
        "TG90p",
        lambda c: tg90p(c),
        IndexGroup.HEAT,
        [TAS],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TN90P = (
        "TN90p",
        lambda c: tn90p(c),
        IndexGroup.HEAT,
        [TAS_MIN],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TX90P = (
        "TX90p",
        lambda c: tx90p(c),
        IndexGroup.HEAT,
        [TAS_MAX],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TXX = (
        "TXx",
        lambda c: txx(c),
        IndexGroup.HEAT,
        [TAS_MAX],
    )
    TNX = (
        "TNx",
        lambda c: tnx(c),
        IndexGroup.HEAT,
        [TAS_MIN],
    )
    CSU = (
        "CSU",
        lambda c: csu(c),
        IndexGroup.HEAT,
        [TAS_MAX],
        [MODIFIABLE_THRESHOLD],
    )

    # Cold
    GD4 = (
        "GD4",
        lambda c: gd4(c),
        IndexGroup.COLD,
        [TAS],
        [MODIFIABLE_THRESHOLD],
    )
    FD = (
        "FD",
        lambda c: fd(c),
        IndexGroup.COLD,
        [TAS_MIN],
        [MODIFIABLE_THRESHOLD],
    )
    CFD = (
        "CFD",
        lambda c: cfd(c),
        IndexGroup.COLD,
        [TAS_MIN],
        [MODIFIABLE_THRESHOLD],
    )
    HD17 = (
        "HD17",
        lambda c: hd17(c),
        IndexGroup.COLD,
        [TAS],
        [MODIFIABLE_THRESHOLD],
    )
    ID = (
        "ID",
        lambda c: id(c),
        IndexGroup.COLD,
        [TAS_MAX],
        [MODIFIABLE_THRESHOLD],
    )
    TG10P = (
        "TG10p",
        lambda c: tg10p(c),
        IndexGroup.COLD,
        [TAS],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TN10P = (
        "TN10p",
        lambda c: tn10p(c),
        IndexGroup.COLD,
        [TAS_MIN],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TX10P = (
        "TX10p",
        lambda c: tx10p(c),
        IndexGroup.COLD,
        [TAS_MAX],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_UNIT],
    )
    TXN = (
        "TXn",
        lambda c: txn(c),
        IndexGroup.COLD,
        [TAS_MAX],
    )
    TNN = (
        "TNn",
        lambda c: tnn(c),
        IndexGroup.COLD,
        [TAS_MIN],
    )
    CSDI = (
        "CSDI",
        lambda c: csdi(c),
        IndexGroup.COLD,
        [TAS_MIN],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_THRESHOLD],
    )

    # Drought
    CDD = (
        "CDD",
        lambda c: cdd(c),
        IndexGroup.DROUGHT,
        [PR],
    )

    # Rain
    PRCPTOT = (
        "PRCPTOT",
        lambda c: prcptot(c),
        IndexGroup.RAIN,
        [PR],
    )
    RR1 = (
        "RR1",
        lambda c: rr1(c),
        IndexGroup.RAIN,
        [PR],
    )
    SDII = (
        "SDII",
        lambda c: sdii(c),
        IndexGroup.RAIN,
        [PR],
    )
    CWD = (
        "CWD",
        lambda c: cwd(c),
        IndexGroup.RAIN,
        [PR],
    )
    R10MM = (
        "R10mm",
        lambda c: r10mm(c),
        IndexGroup.RAIN,
        [PR],
    )
    R20MM = (
        "R20mm",
        lambda c: r20mm(c),
        IndexGroup.RAIN,
        [PR],
    )
    RX1DAY = (
        "RX1day",
        lambda c: rx1day(c),
        IndexGroup.RAIN,
        [PR],
    )
    RX5DAY = (
        "RX5day",
        lambda c: rx5day(c),
        IndexGroup.RAIN,
        [PR],
    )
    R75P = (
        "R75p",
        lambda c: r75p(c),
        IndexGroup.RAIN,
        [PR],
        [QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R75PTOT = (
        "R75pTOT",
        lambda c: r75ptot(c),
        IndexGroup.RAIN,
        [PR],
        [QUANTILE_BASED],
    )
    R95P = (
        "R95p",
        lambda c: r95p(c),
        IndexGroup.RAIN,
        [PR],
        [QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R95PTOT = (
        "R95pTOT",
        lambda c: r95ptot(c),
        IndexGroup.RAIN,
        [PR],
        [QUANTILE_BASED],
    )
    R99P = (
        "R99p",
        lambda c: r99p(c),
        IndexGroup.RAIN,
        [PR],
        [QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R99PTOT = (
        "R99pTOT",
        lambda c: r99ptot(c),
        IndexGroup.RAIN,
        [PR],
        [QUANTILE_BASED],
    )

    # Snow
    SD = (
        "SD",
        lambda c: sd(c),
        IndexGroup.SNOW,
        [PR],
    )
    SD1 = (
        "SD1",
        lambda c: sd1(c),
        IndexGroup.SNOW,
        [PR],
    )
    SD5CM = (
        "SD5cm",
        lambda c: sd5cm(c),
        IndexGroup.SNOW,
        [PR],
    )
    SD50CM = (
        "SD50cm",
        lambda c: sd50cm(c),
        IndexGroup.SNOW,
        [PR],
    )

    # Compound (precipitation and temperature)
    CD = (
        "CD",
        lambda c: cd(c),
        IndexGroup.COMPOUND,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    CW = (
        "CW",
        lambda c: cw(c),
        IndexGroup.COMPOUND,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WD = (
        "WD",
        lambda c: wd(c),
        IndexGroup.COMPOUND,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WW = (
        "WW",
        lambda c: ww(c),
        IndexGroup.COMPOUND,
        [TAS, PR],
        [QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )

    def __init__(
        self,
        short_name: str,
        compute: ComputeIndexFun,
        group: IndexGroup,
        variables: list[list[str]],
        qualifiers: list[str] = None,
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
    def lookup(query: str) -> EcadIndex:
        if isinstance(query, EcadIndex):
            return query
        for e in EcadIndex:
            if e.short_name.upper() == query.upper():
                return e
        raise InvalidIcclimArgumentError(
            f"Unknown index {query}."
            f" You can list the available indices"
            f" with `icclim.list_indices()`."
        )

    @staticmethod
    def list() -> list[str]:
        """
        Get a a string list of ``EcadIndex`` enum's indices formatted in a readable
        fashion.
        """
        return [f"{i.group.value} | {i.short_name} | {i.definition}" for i in EcadIndex]

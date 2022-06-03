from __future__ import annotations

from enum import Enum

from icclim.clix_meta.clix_meta_indices import ClixMetaIndices
from icclim.ecad.ecad_functions import (
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
from icclim.models.climate_index import ClimateIndex
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
from icclim.models.index_group import IndexGroup

clix_indices: ClixMetaIndices = ClixMetaIndices.get_instance()


def _get_clix_definition(short_name: str) -> str:
    definition = ""
    clix_index = clix_indices.lookup(short_name)
    if clix_index is not None:
        definition = clix_index["output"]["long_name"]
    return definition


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
    TG = ClimateIndex(
        short_name="TG",
        compute=lambda c: tg(c),
        group=IndexGroup.TEMPERATURE,
        input_variables=[TAS],
    )
    TN = ClimateIndex(
        short_name="TN",
        compute=lambda c: tn(c),
        group=IndexGroup.TEMPERATURE,
        input_variables=[TAS_MIN],
    )
    TX = ClimateIndex(
        short_name="TX",
        compute=lambda c: tx(c),
        group=IndexGroup.TEMPERATURE,
        input_variables=[TAS_MAX],
    )
    DTR = ClimateIndex(
        short_name="DTR",
        compute=lambda c: dtr(c),
        group=IndexGroup.TEMPERATURE,
        input_variables=[TAS_MAX, TAS_MIN],
    )
    ETR = ClimateIndex(
        short_name="ETR",
        compute=lambda c: etr(c),
        group=IndexGroup.TEMPERATURE,
        input_variables=[TAS_MAX, TAS_MIN],
    )
    VDTR = ClimateIndex(
        short_name="vDTR",
        compute=lambda c: vdtr(c),
        group=IndexGroup.TEMPERATURE,
        input_variables=[TAS_MAX, TAS_MIN],
    )
    # Heat
    SU = ClimateIndex(
        short_name="SU",
        compute=lambda c: su(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    TR = ClimateIndex(
        short_name="TR",
        compute=lambda c: tr(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MIN],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    WSDI = ClimateIndex(
        short_name="WSDI",
        compute=lambda c: wsdi(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_THRESHOLD],
    )
    TG90P = ClimateIndex(
        short_name="TG90p",
        compute=lambda c: tg90p(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
            MODIFIABLE_THRESHOLD,
        ],
    )
    TN90P = ClimateIndex(
        short_name="TN90p",
        compute=lambda c: tn90p(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
            MODIFIABLE_THRESHOLD,
        ],
    )
    TX90P = ClimateIndex(
        short_name="TX90p",
        compute=lambda c: tx90p(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
            MODIFIABLE_THRESHOLD,
        ],
    )
    TXX = ClimateIndex(
        short_name="TXx",
        compute=lambda c: txx(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MAX],
    )
    TNX = ClimateIndex(
        short_name="TNx",
        compute=lambda c: tnx(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MIN],
    )
    CSU = ClimateIndex(
        short_name="CSU",
        compute=lambda c: csu(c),
        group=IndexGroup.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    # Cold
    GD4 = ClimateIndex(
        short_name="GD4",
        compute=lambda c: gd4(c),
        group=IndexGroup.COLD,
        input_variables=[TAS],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    FD = ClimateIndex(
        short_name="FD",
        compute=lambda c: fd(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    CFD = ClimateIndex(
        short_name="CFD",
        compute=lambda c: cfd(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    HD17 = ClimateIndex(
        short_name="HD17",
        compute=lambda c: hd17(c),
        group=IndexGroup.COLD,
        input_variables=[TAS],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    ID = ClimateIndex(
        short_name="ID",
        compute=lambda c: id(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MAX],
        qualifiers=[MODIFIABLE_THRESHOLD],
    )
    TG10P = ClimateIndex(
        short_name="TG10p",
        compute=lambda c: tg10p(c),
        group=IndexGroup.COLD,
        input_variables=[TAS],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
            MODIFIABLE_THRESHOLD,
        ],
    )
    TN10P = ClimateIndex(
        short_name="TN10p",
        compute=lambda c: tn10p(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
            MODIFIABLE_THRESHOLD,
        ],
    )
    TX10P = ClimateIndex(
        short_name="TX10p",
        compute=lambda c: tx10p(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
            MODIFIABLE_THRESHOLD,
        ],
    )
    TXN = ClimateIndex(
        short_name="TXn",
        compute=lambda c: txn(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MAX],
    )
    TNN = ClimateIndex(
        short_name="TNn",
        compute=lambda c: tnn(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MIN],
    )
    CSDI = ClimateIndex(
        short_name="CSDI",
        compute=lambda c: csdi(c),
        group=IndexGroup.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW, MODIFIABLE_THRESHOLD],
    )
    # Drought
    CDD = ClimateIndex(
        short_name="CDD",
        compute=lambda c: cdd(c),
        group=IndexGroup.DROUGHT,
        input_variables=[PR],
    )
    # Rain
    PRCPTOT = ClimateIndex(
        short_name="PRCPTOT",
        compute=lambda c: prcptot(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    RR1 = ClimateIndex(
        short_name="RR1",
        compute=lambda c: rr1(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    SDII = ClimateIndex(
        short_name="SDII",
        compute=lambda c: sdii(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    CWD = ClimateIndex(
        short_name="CWD",
        compute=lambda c: cwd(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    R10MM = ClimateIndex(
        short_name="R10mm",
        compute=lambda c: r10mm(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    R20MM = ClimateIndex(
        short_name="R20mm",
        compute=lambda c: r20mm(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    RX1DAY = ClimateIndex(
        short_name="RX1day",
        compute=lambda c: rx1day(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    RX5DAY = ClimateIndex(
        short_name="RX5day",
        compute=lambda c: rx5day(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
    )
    R75P = ClimateIndex(
        short_name="R75p",
        compute=lambda c: r75p(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R75PTOT = ClimateIndex(
        short_name="R75pTOT",
        compute=lambda c: r75ptot(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
        qualifiers=[QUANTILE_BASED],
    )
    R95P = ClimateIndex(
        short_name="R95p",
        compute=lambda c: r95p(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R95PTOT = ClimateIndex(
        short_name="R95pTOT",
        compute=lambda c: r95ptot(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
        qualifiers=[QUANTILE_BASED],
    )
    R99P = ClimateIndex(
        short_name="R99p",
        compute=lambda c: r99p(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_UNIT],
    )
    R99PTOT = ClimateIndex(
        short_name="R99pTOT",
        compute=lambda c: r99ptot(c),
        group=IndexGroup.RAIN,
        input_variables=[PR],
        qualifiers=[QUANTILE_BASED],
    )
    # Snow
    SD = ClimateIndex(
        short_name="SD",
        compute=lambda c: sd(c),
        group=IndexGroup.SNOW,
        input_variables=[PR],
    )
    SD1 = ClimateIndex(
        short_name="SD1",
        compute=lambda c: sd1(c),
        group=IndexGroup.SNOW,
        input_variables=[PR],
    )
    SD5CM = ClimateIndex(
        short_name="SD5cm",
        compute=lambda c: sd5cm(c),
        group=IndexGroup.SNOW,
        input_variables=[PR],
    )
    SD50CM = ClimateIndex(
        short_name="SD50cm",
        compute=lambda c: sd50cm(c),
        group=IndexGroup.SNOW,
        input_variables=[PR],
    )
    # Compound (precipitation and temperature)
    CD = ClimateIndex(
        short_name="CD",
        compute=lambda c: cd(c),
        group=IndexGroup.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    CW = ClimateIndex(
        short_name="CW",
        compute=lambda c: cw(c),
        group=IndexGroup.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WD = ClimateIndex(
        short_name="WD",
        compute=lambda c: wd(c),
        group=IndexGroup.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WW = ClimateIndex(
        short_name="WW",
        compute=lambda c: ww(c),
        group=IndexGroup.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )

    def __init__(
        self,
        climate_index: ClimateIndex,
    ):
        self.climate_index = climate_index
        self.climate_index.definition = _get_clix_definition(climate_index.short_name)
        self.climate_index.source = ECAD_ATBD

    @staticmethod
    def lookup(query: str) -> ClimateIndex:
        if isinstance(query, EcadIndex):
            return query.value
        for e in EcadIndex:
            if e.short_name.upper() == query.upper():
                return e
        raise InvalidIcclimArgumentError(f"Unknown ECA&D index {query}.")

    @property
    def group(self):
        return self.climate_index.group

    @property
    def short_name(self):
        return self.climate_index.short_name

    @property
    def definition(self):
        return self.climate_index.definition

    @property
    def compute(self):
        return self.climate_index.compute

    @property
    def input_variables(self):
        return self.climate_index.input_variables

    @property
    def qualifiers(self):
        return self.climate_index.qualifiers

    @property
    def source(self):
        return self.climate_index.source

    @staticmethod
    def list() -> list[str]:
        """
        Get a a string list of ``EcadIndex`` enum's indices formatted in a readable
        fashion.
        """
        return [f"{i.group.value} | {i.short_name} | {i.definition}" for i in EcadIndex]


def get_season_excluded_indices() -> list[EcadIndex]:
    """List of indices which cannot be computed with seasonal slice_mode."""
    return [
        EcadIndex.WSDI,
        EcadIndex.CSU,
        EcadIndex.CFD,
        EcadIndex.CSDI,
        EcadIndex.CDD,
        EcadIndex.CWD,
        EcadIndex.RX5DAY,
        EcadIndex.CD,
        EcadIndex.CW,
        EcadIndex.WD,
        EcadIndex.WW,
    ]

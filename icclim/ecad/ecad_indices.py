from __future__ import annotations

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
from icclim.models.climate_index import ClimateIndex
from icclim.models.constants import (
    ECAD_ATBD,
    MODIFIABLE_QUANTILE_WINDOW,
    MODIFIABLE_UNIT,
    PR,
    QUANTILE_BASED,
    TAS,
    TAS_MAX,
    TAS_MIN,
)
from icclim.models.index_group import IndexGroupRegistry
from icclim.models.registry import Registry

clix_indices = ClixMetaIndices.get_instance()


def _get_clix_definition(short_name: str) -> str:
    definition = ""
    clix_index = clix_indices.lookup(short_name)
    if clix_index is not None:
        definition = clix_index["output"]["long_name"]
    return definition


class EcadIndexRegistry(Registry):
    _item_class = ClimateIndex
    # TODO Add indices wind gust, wind direction,
    #                  radiation , pressure,
    #                  cloud cover, sunshine,
    #                  humidity

    @staticmethod
    def get_item_aliases(item: ClimateIndex) -> list[str]:
        return [item.short_name]

    @classmethod
    def list(cls) -> list[str]:
        return [
            f"{i.group.built_value} | {i.short_name} | {i.definition}"
            for i in cls.values()
        ]

    TG = ClimateIndex(
        definition=_get_clix_definition("TG"),
        source=ECAD_ATBD,
        short_name="TG",
        compute=lambda c: tg(c),
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[TAS],
    )
    TN = ClimateIndex(
        definition=_get_clix_definition("TN"),
        source=ECAD_ATBD,
        short_name="TN",
        compute=lambda c: tn(c),
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[TAS_MIN],
    )
    TX = ClimateIndex(
        definition=_get_clix_definition("TX"),
        source=ECAD_ATBD,
        short_name="TX",
        compute=lambda c: tx(c),
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[TAS_MAX],
    )
    DTR = ClimateIndex(
        definition=_get_clix_definition("DTR"),
        source=ECAD_ATBD,
        short_name="DTR",
        compute=lambda c: dtr(c),
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[TAS_MAX, TAS_MIN],
    )
    ETR = ClimateIndex(
        definition=_get_clix_definition("ETR"),
        source=ECAD_ATBD,
        short_name="ETR",
        compute=lambda c: etr(c),
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[TAS_MAX, TAS_MIN],
    )
    VDTR = ClimateIndex(
        definition=_get_clix_definition("vDTR"),
        source=ECAD_ATBD,
        short_name="vDTR",
        compute=lambda c: vdtr(c),
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[TAS_MAX, TAS_MIN],
    )
    # Heat
    SU = ClimateIndex(
        definition=_get_clix_definition("SU"),
        source=ECAD_ATBD,
        short_name="SU",
        compute=lambda c: su(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[],
        output_var_name="SU_{xx}",
    )
    TR = ClimateIndex(
        definition=_get_clix_definition("TR"),
        source=ECAD_ATBD,
        short_name="TR",
        compute=lambda c: tr(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MIN],
        qualifiers=[],
        output_var_name="TR_{xx}",
    )
    WSDI = ClimateIndex(
        definition=_get_clix_definition("WSDI"),
        source=ECAD_ATBD,
        short_name="WSDI",
        compute=lambda c: wsdi(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
        ],
        output_var_name="WSDI_{xx}",
    )
    TG90P = ClimateIndex(
        definition=_get_clix_definition("TG90p"),
        source=ECAD_ATBD,
        short_name="TG90p",
        compute=lambda c: tg90p(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
        ],
        output_var_name="TG_above_{xx}_P",
    )
    TN90P = ClimateIndex(
        definition=_get_clix_definition("TN90p"),
        source=ECAD_ATBD,
        short_name="TN90p",
        compute=lambda c: tn90p(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
        ],
        output_var_name="TN_above_{xx}_P",
    )
    TX90P = ClimateIndex(
        definition=_get_clix_definition("TX90p"),
        source=ECAD_ATBD,
        short_name="TX90p",
        compute=lambda c: tx90p(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
        ],
        output_var_name="TX_above_{xx}_P",
    )
    TXX = ClimateIndex(
        definition=_get_clix_definition("TXx"),
        source=ECAD_ATBD,
        short_name="TXx",
        compute=lambda c: txx(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MAX],
    )
    TNX = ClimateIndex(
        definition=_get_clix_definition("TNx"),
        source=ECAD_ATBD,
        short_name="TNx",
        compute=lambda c: tnx(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MIN],
    )
    CSU = ClimateIndex(
        definition=_get_clix_definition("CSU"),
        source=ECAD_ATBD,
        short_name="CSU",
        compute=lambda c: csu(c),
        group=IndexGroupRegistry.HEAT,
        input_variables=[TAS_MAX],
        qualifiers=[],
        output_var_name="CSU_{xx}",
    )
    # Cold
    GD4 = ClimateIndex(
        definition=_get_clix_definition("GD4"),
        source=ECAD_ATBD,
        short_name="GD4",
        compute=lambda c: gd4(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS],
        qualifiers=[],
        output_var_name="GD_{xx}",
    )
    FD = ClimateIndex(
        definition=_get_clix_definition("FD"),
        source=ECAD_ATBD,
        short_name="FD",
        compute=lambda c: fd(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[],
        output_var_name="FD_{xx}",
    )
    CFD = ClimateIndex(
        definition=_get_clix_definition("CFD"),
        source=ECAD_ATBD,
        short_name="CFD",
        compute=lambda c: cfd(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[],
        output_var_name="CFD_{xx}",
    )
    HD17 = ClimateIndex(
        definition=_get_clix_definition("HD17"),
        source=ECAD_ATBD,
        short_name="HD17",
        compute=lambda c: hd17(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS],
        qualifiers=[],
        output_var_name="HD_{xx}",
    )
    ID = ClimateIndex(
        definition=_get_clix_definition("ID"),
        source=ECAD_ATBD,
        short_name="ID",
        compute=lambda c: id(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MAX],
        qualifiers=[],
        output_var_name="ID_{xx}",
    )
    TG10P = ClimateIndex(
        definition=_get_clix_definition("TG10p"),
        source=ECAD_ATBD,
        short_name="TG10p",
        compute=lambda c: tg10p(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
        ],
        output_var_name="TG_below_{xx}_P",
    )
    TN10P = ClimateIndex(
        definition=_get_clix_definition("TN10p"),
        source=ECAD_ATBD,
        short_name="TN10p",
        compute=lambda c: tn10p(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
        ],
        output_var_name="TN_below_{xx}_P",
    )
    TX10P = ClimateIndex(
        definition=_get_clix_definition("TX10p"),
        source=ECAD_ATBD,
        short_name="TX10p",
        compute=lambda c: tx10p(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
            MODIFIABLE_UNIT,
        ],
        output_var_name="TX_below_{xx}_P",
    )
    TXN = ClimateIndex(
        definition=_get_clix_definition("TXn"),
        source=ECAD_ATBD,
        short_name="TXn",
        compute=lambda c: txn(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MAX],
    )
    TNN = ClimateIndex(
        definition=_get_clix_definition("TNn"),
        source=ECAD_ATBD,
        short_name="TNn",
        compute=lambda c: tnn(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MIN],
    )
    CSDI = ClimateIndex(
        definition=_get_clix_definition("CSDI"),
        source=ECAD_ATBD,
        short_name="CSDI",
        compute=lambda c: csdi(c),
        group=IndexGroupRegistry.COLD,
        input_variables=[TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_QUANTILE_WINDOW,
        ],
        output_var_name="CSDI_{xx}",
    )
    # Drought
    CDD = ClimateIndex(
        definition=_get_clix_definition("CDD"),
        source=ECAD_ATBD,
        short_name="CDD",
        compute=lambda c: cdd(c),
        group=IndexGroupRegistry.DROUGHT,
        input_variables=[PR],
    )
    # Rain
    PRCPTOT = ClimateIndex(
        definition=_get_clix_definition("PRCPT"),
        source=ECAD_ATBD,
        short_name="PRCPTOT",
        compute=lambda c: prcptot(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    RR1 = ClimateIndex(
        definition=_get_clix_definition("RR1"),
        source=ECAD_ATBD,
        short_name="RR1",
        compute=lambda c: rr1(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    SDII = ClimateIndex(
        definition=_get_clix_definition("SDII"),
        source=ECAD_ATBD,
        short_name="SDII",
        compute=lambda c: sdii(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    CWD = ClimateIndex(
        definition=_get_clix_definition("CWD"),
        source=ECAD_ATBD,
        short_name="CWD",
        compute=lambda c: cwd(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    R10MM = ClimateIndex(
        definition=_get_clix_definition("R10mm"),
        source=ECAD_ATBD,
        short_name="R10mm",
        compute=lambda c: r10mm(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    R20MM = ClimateIndex(
        definition=_get_clix_definition("R20mm"),
        source=ECAD_ATBD,
        short_name="R20mm",
        compute=lambda c: r20mm(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    RX1DAY = ClimateIndex(
        definition=_get_clix_definition("RX1da"),
        source=ECAD_ATBD,
        short_name="RX1day",
        compute=lambda c: rx1day(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    RX5DAY = ClimateIndex(
        definition=_get_clix_definition("RX5da"),
        source=ECAD_ATBD,
        short_name="RX5day",
        compute=lambda c: rx5day(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
    )
    R75P = ClimateIndex(
        definition=_get_clix_definition("R75p"),
        source=ECAD_ATBD,
        short_name="R75p",
        compute=lambda c: r75p(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_UNIT,
        ],
        output_var_name="R_above_{xx}_P",
    )
    R75PTOT = ClimateIndex(
        definition=_get_clix_definition("R75pT"),
        source=ECAD_ATBD,
        short_name="R75pTOT",
        compute=lambda c: r75ptot(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        output_var_name="R_above_{xx}_PTOT",
    )
    R95P = ClimateIndex(
        definition=_get_clix_definition("R95p"),
        source=ECAD_ATBD,
        short_name="R95p",
        compute=lambda c: r95p(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_UNIT,
        ],
        output_var_name="R_above_{xx}_P",
    )
    R95PTOT = ClimateIndex(
        definition=_get_clix_definition("R95pT"),
        source=ECAD_ATBD,
        short_name="R95pTOT",
        compute=lambda c: r95ptot(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        output_var_name="R_above_{xx}_PTOT",
    )
    R99P = ClimateIndex(
        definition=_get_clix_definition("R99p"),
        source=ECAD_ATBD,
        short_name="R99p",
        compute=lambda c: r99p(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
        qualifiers=[
            QUANTILE_BASED,
            MODIFIABLE_UNIT,
        ],
        output_var_name="R_above_{xx}_P",
    )
    R99PTOT = ClimateIndex(
        definition=_get_clix_definition("R99pT"),
        source=ECAD_ATBD,
        short_name="R99pTOT",
        compute=lambda c: r99ptot(c),
        group=IndexGroupRegistry.RAIN,
        input_variables=[PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        output_var_name="R_above_{xx}_PTOT",
    )
    # Snow
    SD = ClimateIndex(
        definition=_get_clix_definition("SD"),
        source=ECAD_ATBD,
        short_name="SD",
        compute=lambda c: sd(c),
        group=IndexGroupRegistry.SNOW,
        input_variables=[PR],
    )
    SD1 = ClimateIndex(
        definition=_get_clix_definition("SD1"),
        source=ECAD_ATBD,
        short_name="SD1",
        compute=lambda c: sd1(c),
        group=IndexGroupRegistry.SNOW,
        input_variables=[PR],
    )
    SD5CM = ClimateIndex(
        definition=_get_clix_definition("SD5cm"),
        source=ECAD_ATBD,
        short_name="SD5cm",
        compute=lambda c: sd5cm(c),
        group=IndexGroupRegistry.SNOW,
        input_variables=[PR],
    )
    SD50CM = ClimateIndex(
        definition=_get_clix_definition("SD50c"),
        source=ECAD_ATBD,
        short_name="SD50cm",
        compute=lambda c: sd50cm(c),
        group=IndexGroupRegistry.SNOW,
        input_variables=[PR],
    )
    # Compound (precipitation and temperature)
    CD = ClimateIndex(
        definition=_get_clix_definition("CD"),
        source=ECAD_ATBD,
        short_name="CD",
        compute=lambda c: cd(c),
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    CW = ClimateIndex(
        definition=_get_clix_definition("CW"),
        source=ECAD_ATBD,
        short_name="CW",
        compute=lambda c: cw(c),
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WD = ClimateIndex(
        definition=_get_clix_definition("WD"),
        source=ECAD_ATBD,
        short_name="WD",
        compute=lambda c: wd(c),
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )
    WW = ClimateIndex(
        definition=_get_clix_definition("WW"),
        source=ECAD_ATBD,
        short_name="WW",
        compute=lambda c: ww(c),
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[TAS, PR],
        qualifiers=[QUANTILE_BASED, MODIFIABLE_QUANTILE_WINDOW],
    )


def get_season_excluded_indices() -> list[ClimateIndex]:
    """List of indices which cannot be computed with seasonal slice_mode."""
    return [
        EcadIndexRegistry.WSDI,
        EcadIndexRegistry.CSU,
        EcadIndexRegistry.CFD,
        EcadIndexRegistry.CSDI,
        EcadIndexRegistry.CDD,
        EcadIndexRegistry.CWD,
        EcadIndexRegistry.RX5DAY,
        EcadIndexRegistry.CD,
        EcadIndexRegistry.CW,
        EcadIndexRegistry.WD,
        EcadIndexRegistry.WW,
    ]

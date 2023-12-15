from __future__ import annotations

from icclim.ecad.xclim_binding import XCLIM_BINDING
from icclim.generic_indices.generic_indicators import GenericIndicatorRegistry
from icclim.generic_indices.standard_variable import StandardVariableRegistry
from icclim.generic_indices.threshold import build_threshold
from icclim.models.constants import ECAD_ATBD, QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from icclim.models.index_group import IndexGroupRegistry
from icclim.models.registry import Registry
from icclim.models.standard_index import StandardIndex

ECAD_REFERENCE = (
    "ATBD of the ECA&D indices calculation"
    " (https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf)"
)


class EcadIndexRegistry(Registry[StandardIndex]):
    _item_class = StandardIndex
    # TODO Add indices of wind gust, wind direction,
    #                     radiation, pressure,
    #                     cloud cover, sunshine,
    #                     humidity

    @staticmethod
    def get_item_aliases(item: StandardIndex) -> list[str]:
        return [item.short_name]

    @classmethod
    def list(cls: EcadIndexRegistry) -> list[str]:
        return [
            f"{i.group.name} | {i.short_name} | {i.definition}" for i in cls.values()
        ]

    TG = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Mean of daily mean temperature",
        source=ECAD_ATBD,
        short_name="TG",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS],
    )
    TN = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Mean of daily minimum temperature",
        source=ECAD_ATBD,
        short_name="TN",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS_MIN],
    )
    TX = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Mean of daily maximum temperature",
        source=ECAD_ATBD,
        short_name="TX",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    DTR = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MeanOfDifference,
        output_unit="degree_Celsius",
        definition="Mean Diurnal Temperature Range",
        source=ECAD_ATBD,
        short_name="DTR",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[
            StandardVariableRegistry.TAS_MAX,
            StandardVariableRegistry.TAS_MIN,
        ],
    )
    ETR = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.DifferenceOfExtremes,
        output_unit="degree_Celsius",
        definition="Intra-period extreme temperature range",
        source=ECAD_ATBD,
        short_name="ETR",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[
            StandardVariableRegistry.TAS_MAX,
            StandardVariableRegistry.TAS_MIN,
        ],
    )
    VDTR = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MeanOfAbsoluteOneTimeStepDifference,
        output_unit="degree_Celsius",
        definition="Mean day-to-day variation in Diurnal Temperature Range",
        source=ECAD_ATBD,
        short_name="vDTR",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[
            StandardVariableRegistry.TAS_MAX,
            StandardVariableRegistry.TAS_MIN,
        ],
    )
    # Heat
    SU = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Number of Summer Days (Tmax > 25C)",
        source=ECAD_ATBD,
        short_name="SU",
        threshold="> 25 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    TR = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Number of Tropical Nights (Tmin > 20C)",
        source=ECAD_ATBD,
        short_name="TR",
        threshold="> 20 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[],
    )
    WSDI = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.SumOfSpellLengths,
        output_unit="day",
        definition="Warm-spell duration index (days)",
        source=ECAD_ATBD,
        short_name="WSDI",
        threshold="> 90 doy_per",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
        min_spell_length=6,
    )
    TG90P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Days when Tmean > 90th percentile",
        threshold="> 90 doy_per",
        source=ECAD_ATBD,
        short_name="TG90p",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TN90P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Days when Tmin > 90th percentile",
        threshold="> 90 doy_per",
        source=ECAD_ATBD,
        short_name="TN90p",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TX90P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="> 90 doy_per",
        output_unit="day",
        definition="Days when Tmax > 90th daily percentile",
        source=ECAD_ATBD,
        short_name="TX90p",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TXX = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Maximum,
        output_unit="degree_Celsius",
        definition="Maximum daily maximum temperature",
        source=ECAD_ATBD,
        short_name="TXx",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    TNX = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Maximum,
        output_unit="degree_Celsius",
        definition="Maximum daily minimum temperature",
        source=ECAD_ATBD,
        short_name="TNx",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
    )
    CSU = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold="> 25 degree_Celsius",
        output_unit="day",
        definition="Maximum number of consecutive summer days (Tmax >25 C)",
        source=ECAD_ATBD,
        short_name="CSU",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    # Cold
    GD4 = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Excess,
        threshold="4 degree_Celsius",
        output_unit="degree_Celsius day",
        definition="Growing degree days (sum of Tmean > 4 C)",
        source=ECAD_ATBD,
        short_name="GD4",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[],
    )
    FD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 0 degree_Celsius",
        output_unit="day",
        definition="Number of Frost Days (Tmin < 0C)",
        source=ECAD_ATBD,
        short_name="FD",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[],
    )
    CFD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold="< 0 degree_Celsius",
        output_unit="day",
        definition="Maximum number of consecutive frost days (Tmin < 0 C)",
        source=ECAD_ATBD,
        short_name="CFD",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[],
    )
    HD17 = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Deficit,
        threshold="17 degree_Celsius",
        output_unit="degree_Celsius day",
        definition="Heating degree days (sum of Tmean < 17 C)",
        source=ECAD_ATBD,
        short_name="HD17",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[],
    )
    ID = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 0 degree_Celsius",
        output_unit="day",
        definition="Number of sharp Ice Days (Tmax < 0C)",
        source=ECAD_ATBD,
        short_name="ID",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    TG10P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Days when Tmean < 10th percentile",
        source=ECAD_ATBD,
        short_name="TG10p",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TN10P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Days when Tmin < 10th percentile",
        source=ECAD_ATBD,
        short_name="TN10p",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TX10P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Days when Tmax < 10th percentile",
        source=ECAD_ATBD,
        short_name="TX10p",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TXN = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Minimum,
        output_unit="degree_Celsius",
        definition="Minimum daily maximum temperature",
        source=ECAD_ATBD,
        short_name="TXn",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    TNN = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Minimum,
        output_unit="degree_Celsius",
        definition="Minimum daily minimum temperature",
        source=ECAD_ATBD,
        short_name="TNn",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
    )
    CSDI = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.SumOfSpellLengths,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Cold-spell duration index (days)",
        source=ECAD_ATBD,
        short_name="CSDI",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
        min_spell_length=6,
    )
    # Drought
    CDD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold="< 1 mm/day",
        output_unit="day",
        definition="Maximum consecutive dry days (Precip < 1mm)",
        source=ECAD_ATBD,
        short_name="CDD",
        group=IndexGroupRegistry.DROUGHT,
        input_variables=[StandardVariableRegistry.PR],
    )
    # Rain
    PRCPTOT = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Sum,
        threshold=">= 1 mm/day",
        output_unit="mm",
        definition="Total precipitation during Wet Days",
        source=ECAD_ATBD,
        short_name="PRCPTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RR1 = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 1 mm/day",
        output_unit="day",
        definition="Number of Wet Days (precip >= 1 mm)",
        source=ECAD_ATBD,
        short_name="RR1",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    SDII = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        threshold=">= 1 mm/day",
        output_unit="mm/day",
        definition="Average precipitation during Wet Days (SDII)",
        source=ECAD_ATBD,
        short_name="SDII",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    CWD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold=">= 1 mm/day",
        output_unit="day",
        definition="Maximum consecutive wet days (Precip >= 1mm)",
        source=ECAD_ATBD,
        short_name="CWD",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RR = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Sum,
        output_unit="mm",
        definition="Precipitation sum (mm)",
        source=ECAD_ATBD,
        short_name="RR",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    R10MM = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 10 mm/day",
        output_unit="day",
        definition="Number of heavy precipitation days (Precip >=10mm)",
        source=ECAD_ATBD,
        short_name="R10mm",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    R20MM = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 20 mm/day",
        output_unit="day",
        definition="Number of very heavy precipitation days (Precip >= 20mm)",
        source=ECAD_ATBD,
        short_name="R20mm",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RX1DAY = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Maximum,
        output_unit="mm/day",
        definition="maximum 1-day total precipitation",  # from xclim
        source=ECAD_ATBD,
        short_name="RX1day",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RX5DAY = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxOfRollingSum,
        output_unit="mm",
        definition="maximum 5-day total precipitation",  # from xclim
        source=ECAD_ATBD,
        short_name="RX5day",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[],
        rolling_window_width=5,
    )
    R75P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Days with RR > 75th percentile of daily amounts (moderate wet days)"
        " (d)",
        source=ECAD_ATBD,
        short_name="R75p",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    R75PTOT = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        output_unit="%",
        definition="Precipitation fraction due to moderate wet days"
        " (> 75th percentile)",
        source=ECAD_ATBD,
        short_name="R75pTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    R95P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=build_threshold("> 95 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Days with RR > 95th percentile of daily amounts (very wet days)"
        " (days)",
        source=ECAD_ATBD,
        short_name="R95p",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    R95PTOT = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=build_threshold("> 95 period_per", threshold_min_value="1 mm/day"),
        output_unit="%",
        definition="Precipitation fraction due to very wet days (> 95th percentile)",
        source=ECAD_ATBD,
        short_name="R95pTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    R99P = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=build_threshold("> 99 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Days with RR > 99th percentile of daily amounts"
        " (extremely wet days)",
        source=ECAD_ATBD,
        short_name="R99p",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    R99PTOT = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=build_threshold("> 99 period_per", threshold_min_value="1 mm/day"),
        output_unit="%",
        definition="Precipitation fraction due to extremely wet days"
        " (> 99th percentile)",
        source=ECAD_ATBD,
        short_name="R99pTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    # Snow
    SD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="cm",
        definition="Mean of daily snow depth",
        source=ECAD_ATBD,
        short_name="SD",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.SND],
    )
    SD1 = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 1 cm",
        output_unit="day",
        definition="Snow days (SD >= 1 cm)",
        source=ECAD_ATBD,
        short_name="SD1",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.SND],
    )
    SD5CM = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        threshold=">= 5 cm",
        definition="Number of days with snow depth >= 5 cm",
        source=ECAD_ATBD,
        short_name="SD5cm",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.SND],
    )
    SD50CM = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 50 cm",
        output_unit="day",
        definition="Number of days with snow depth >= 50 cm",
        source=ECAD_ATBD,
        short_name="SD50cm",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.SND],
    )
    # Compound (precipitation and temperature)
    CD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "< 25 doy_per",
            build_threshold("< 25 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG < 25th percentile of daily mean temperature and"
        " RR <25th percentile of daily precipitation sum (cold/dry days)",
        source=ECAD_ATBD,
        short_name="CD",
        group=IndexGroupRegistry.TEMPERATURE | IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    CW = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "< 25 doy_per",
            build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG < 25th percentile of daily mean temperature and"
        " RR >75th percentile of daily precipitation sum (cold/wet days)",
        source=ECAD_ATBD,
        short_name="CW",
        group=IndexGroupRegistry.TEMPERATURE | IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    WD = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "> 75 doy_per",
            build_threshold("< 25 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG > 75th percentile of daily mean temperature and"
        " RR <25th percentile of daily precipitation sum (warm/dry days)",
        source=ECAD_ATBD,
        short_name="WD",
        group=IndexGroupRegistry.TEMPERATURE | IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    WW = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "> 75 doy_per",
            build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG > 75th percentile of daily mean temperature and"
        " RR >75th percentile of daily precipitation sum (warm/wet days)",
        source=ECAD_ATBD,
        short_name="WW",
        group=IndexGroupRegistry.TEMPERATURE | IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    # WIND
    FXX = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Maximum,
        output_unit="m s-1",
        definition="Maximum value of daily maximum wind gust",
        source=ECAD_ATBD,
        short_name="FXx",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.WSGS_MAX],
    )
    FG6BFT = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 10.8 m s-1",
        output_unit="day",
        definition="Days with daily averaged wind ≥ 6 Bft (10.8 m s-1)",
        source=ECAD_ATBD,
        short_name="FG6Bft",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.SFC_WIND],
    )
    FGCALM = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="<= 2 m s-1",
        output_unit="day",
        definition="Calm days, days with daily averaged wind <= 2 m s-1",
        source=ECAD_ATBD,
        short_name="FGcalm",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.SFC_WIND],
    )
    FG = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="m s-1",
        definition="Mean of daily mean wind strength",
        source=ECAD_ATBD,
        short_name="FG",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.SFC_WIND],
    )
    DDNORTH = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="> 315 degree OR <= 45 degree",
        output_unit="day",
        definition="Days with northerly winds (DD > 315° or DD ≤ 45°)",
        source=ECAD_ATBD,
        short_name="DDnorth",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.WIND_TO_DIRECTION],
    )
    DDEAST = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="> 45 degree AND <= 135 degree",
        output_unit="day",
        definition="Days with easterly winds (45° < DD <= 135°)",
        source=ECAD_ATBD,
        short_name="DDeast",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.WIND_TO_DIRECTION],
    )
    DDSOUTH = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="> 135 degree AND <= 225 degree",
        output_unit="day",
        definition="Days with southerly winds (135° < DD <= 225°)",
        source=ECAD_ATBD,
        short_name="DDsouth",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.WIND_TO_DIRECTION],
    )
    DDWEST = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="> 225 degree AND <= 315 degree",
        output_unit="day",
        definition="Days with westerly winds (225° < DD <= 315°)",
        source=ECAD_ATBD,
        short_name="DDwest",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.WIND_TO_DIRECTION],
    )
    GSL = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=XCLIM_BINDING.GrowingSeasonLength(),
        definition="Growing season length",
        source=ECAD_ATBD,
        short_name="GSL",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS],
        output_unit="day",
    )
    SPI6 = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=XCLIM_BINDING.StandardizedPrecipitationIndex6(),
        definition="6-Month Standardized Precipitation Index",
        source=ECAD_ATBD,
        short_name="SPI6",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[REFERENCE_PERIOD_INDEX],
        output_unit="",
    )
    SPI3 = StandardIndex(
        reference=ECAD_REFERENCE,
        indicator=XCLIM_BINDING.StandardizedPrecipitationIndex3(),
        definition="3-Month Standardized Precipitation Index",
        source=ECAD_ATBD,
        short_name="SPI3",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[REFERENCE_PERIOD_INDEX],
        output_unit="",
    )

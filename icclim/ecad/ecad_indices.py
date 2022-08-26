from __future__ import annotations

from icclim.generic_indices.cf_var_metadata import StandardVariableRegistry
from icclim.generic_indices.generic_indicators import GenericIndicatorRegistry
from icclim.models.constants import ECAD_ATBD, QUANTILE_BASED
from icclim.models.index_group import IndexGroupRegistry
from icclim.models.registry import Registry
from icclim.models.standard_index import StandardIndex
from icclim.models.threshold import Threshold


class EcadIndexRegistry(Registry):
    _item_class = StandardIndex
    # TODO Add indices of wind gust, wind direction,
    #                     radiation, pressure,
    #                     cloud cover, sunshine,
    #                     humidity

    @staticmethod
    def get_item_aliases(item: StandardIndex) -> list[str]:
        return [item.short_name]

    @classmethod
    def list(cls) -> list[str]:
        return [
            f"{i.group.built_value} | {i.short_name} | {i.definition}"
            for i in cls.values()
        ]

    TG = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Mean of daily mean temperature",
        source=ECAD_ATBD,
        short_name="TG",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS],
    )
    TN = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Mean of daily minimum temperature",
        source=ECAD_ATBD,
        short_name="TN",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS_MIN],
    )
    TX = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Mean of daily maximum temperature",
        source=ECAD_ATBD,
        short_name="TX",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    DTR = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.MeanOfDifference,
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
        generic_indicator=GenericIndicatorRegistry.DifferenceOfExtremes,
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
        generic_indicator=GenericIndicatorRegistry.MeanOfAbsoluteOneTimeStepDifference,
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
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Number of Summer Days (Tmax > 25C)",
        source=ECAD_ATBD,
        short_name="SU",
        threshold=">= 25 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    TR = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Number of Tropical Nights (Tmin > 20C)",
        source=ECAD_ATBD,
        short_name="TR",
        threshold=">= 20 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[],
    )
    WSDI = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.SumOfSpellLengths,
        output_unit="day",
        definition="Warm-spell duration index (days)",
        source=ECAD_ATBD,
        short_name="WSDI",
        threshold=">= 90 doy_per",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
        min_spell_length=6,
    )
    TG90P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Days when Tmean > 90th percentile",
        threshold=">= 90 doy_per",
        source=ECAD_ATBD,
        short_name="TG90p",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    TN90P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Days when Tmin > 90th percentile",
        threshold=">= 90 doy_per",
        source=ECAD_ATBD,
        short_name="TN90p",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    TX90P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 90 doy_per",
        output_unit="day",
        definition="Days when Tmax > 90th daily percentile",
        source=ECAD_ATBD,
        short_name="TX90p",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    TXX = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Maximum,
        output_unit="degree_Celsius",
        definition="Maximum daily maximum temperature",
        source=ECAD_ATBD,
        short_name="TXx",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    TNX = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Minimum,
        output_unit="degree_Celsius",
        definition="Maximum daily minimum temperature",
        source=ECAD_ATBD,
        short_name="TNx",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
    )
    CSU = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
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
        generic_indicator=GenericIndicatorRegistry.Excess,
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
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
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
        generic_indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
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
        generic_indicator=GenericIndicatorRegistry.Deficit,
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
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
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
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Days when Tmean < 10th percentile",
        source=ECAD_ATBD,
        short_name="TG10p",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    TN10P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Days when Tmin < 10th percentile",
        source=ECAD_ATBD,
        short_name="TN10p",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    TX10P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition="Days when Tmax < 10th percentile",
        source=ECAD_ATBD,
        short_name="TX10p",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    TXN = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Minimum,
        output_unit="degree_Celsius",
        definition="Minimum daily maximum temperature",
        source=ECAD_ATBD,
        short_name="TXn",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    TNN = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Minimum,
        output_unit="degree_Celsius",
        definition="Minimum daily minimum temperature",
        source=ECAD_ATBD,
        short_name="TNn",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
    )
    CSDI = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.SumOfSpellLengths,
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
        generic_indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold="< 1 mm day-1",
        output_unit="day",
        definition="Maximum consecutive dry days (Precip < 1mm)",
        source=ECAD_ATBD,
        short_name="CDD",
        group=IndexGroupRegistry.DROUGHT,
        input_variables=[StandardVariableRegistry.PR],
    )
    # Rain
    PRCPTOT = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Sum,
        threshold=">= 1 mm day-1",
        output_unit="mm",
        definition="Total precipitation during Wet Days",
        source=ECAD_ATBD,
        short_name="PRCPTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RR1 = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 1 mm day-1",
        output_unit="day",
        definition="Number of Wet Days (precip >= 1 mm)",
        source=ECAD_ATBD,
        short_name="RR1",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    SDII = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Average,
        threshold=">= 1 mm day-1",
        output_unit="mm day-1",
        definition="Average precipitation during Wet Days (SDII)",
        source=ECAD_ATBD,
        short_name="SDII",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    CWD = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold=">= 1 mm day-1",
        output_unit="day",
        definition="Maximum consecutive wet days (Precip >= 1mm)",
        source=ECAD_ATBD,
        short_name="CWD",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    R10MM = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 10 mm day-1",
        output_unit="day",
        definition="Number of heavy precipitation days (Precip >=10mm)",
        source=ECAD_ATBD,
        short_name="R10mm",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    R20MM = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 20 mm day-1",
        output_unit="day",
        definition="Number of very heavy precipitation days (Precip >= 20mm)",
        source=ECAD_ATBD,
        short_name="R20mm",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RX1DAY = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Maximum,
        output_unit="mm day-1",
        definition="maximum 1-day total precipitation",  # from xclim
        source=ECAD_ATBD,
        short_name="RX1day",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RX5DAY = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.MaxOfRollingSum,
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
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=Threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Days with RR > 75th percentile of daily amounts (moderate wet days)"
        " (d)",
        source=ECAD_ATBD,
        short_name="R75p",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
    )
    R75PTOT = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=Threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        output_unit="",  # unit less
        definition="Precipitation fraction due to moderate wet days"
        " (> 75th percentile)",
        source=ECAD_ATBD,
        short_name="R75pTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
    )
    R95P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=Threshold("> 95 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Days with RR > 95th percentile of daily amounts (very wet days)"
        " (days)",
        source=ECAD_ATBD,
        short_name="R95p",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
    )
    R95PTOT = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=Threshold("> 95 period_per", threshold_min_value="1 mm/day"),
        output_unit="",  # unit less
        definition="Precipitation fraction due to very wet days (> 95th percentile)",
        source=ECAD_ATBD,
        short_name="R95pTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
    )
    R99P = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=Threshold("> 99 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Days with RR > 99th percentile of daily amounts"
        " (extremely wet days)",
        source=ECAD_ATBD,
        short_name="R99p",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
    )
    R99PTOT = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=Threshold("> 99 period_per", threshold_min_value="1 mm/day"),
        output_unit="",  # unit less
        definition="Precipitation fraction due to extremely wet days"
        " (> 99th percentile)",
        source=ECAD_ATBD,
        short_name="R99pTOT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
    )
    # Snow
    SD = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.Average,
        output_unit="cm",
        definition="Mean of daily snow depth",
        source=ECAD_ATBD,
        short_name="SD",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.PR],
    )
    SD1 = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 1 cm",
        output_unit="day",
        definition="Snow days (SD >= 1 cm)",
        source=ECAD_ATBD,
        short_name="SD1",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.PR],
    )
    SD5CM = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        threshold=">= 5 cm",
        definition="Number of days with snow depth >= 5 cm",
        source=ECAD_ATBD,
        short_name="SD5cm",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.PR],
    )
    SD50CM = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 50 cm",
        output_unit="day",
        definition="Number of days with snow depth >= 50 cm",
        source=ECAD_ATBD,
        short_name="SD50cm",
        group=IndexGroupRegistry.SNOW,
        input_variables=[StandardVariableRegistry.PR],
    )
    # Compound (precipitation and temperature)
    CD = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "< 25 doy_per",
            Threshold("< 25 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG < 25th percentile of daily mean temperature and"
        " RR <25th percentile of daily precipitation sum (cold/dry days)",
        source=ECAD_ATBD,
        short_name="CD",
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    CW = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "< 25 doy_per",
            Threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG < 25th percentile of daily mean temperature and"
        " RR >75th percentile of daily precipitation sum (cold/wet days)",
        source=ECAD_ATBD,
        short_name="CW",
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    WD = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=[
            "> 75 doy_per",
            Threshold("< 25 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG > 75th percentile of daily mean temperature and"
        " RR <25th percentile of daily precipitation sum (warm/dry days)",
        source=ECAD_ATBD,
        short_name="WD",
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )
    WW = StandardIndex(
        generic_indicator=GenericIndicatorRegistry.CountOccurrences,
        # todo: use a dictionary for threshold instead ?
        threshold=[
            "> 75 doy_per",
            Threshold("> 75 period_per", threshold_min_value="1 mm/day"),
        ],
        output_unit="day",
        definition="Days with TG > 75th percentile of daily mean temperature and"
        " RR >75th percentile of daily precipitation sum (warm/wet days)",
        source=ECAD_ATBD,
        short_name="WW",
        group=IndexGroupRegistry.COMPOUND,
        input_variables=[StandardVariableRegistry.TAS, StandardVariableRegistry.PR],
        qualifiers=[
            QUANTILE_BASED,
        ],
        doy_window_width=5,
    )

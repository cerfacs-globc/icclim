"""Contain the registry of the DCSC (Meteo France) specific indices."""

from __future__ import annotations

from icclim._core.constants import NEEDS_NORMAL, QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from icclim._core.model.index_group import IndexGroupRegistry
from icclim._core.model.registry import Registry
from icclim._core.model.standard_index import StandardIndex
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.generic.registry import (
    GenericIndicatorRegistry,
)
from icclim.threshold.factory import build_threshold

DCSC_REFERENCE = "Portail DRIAS, DCSC, MeteoFrance"
DCSC_SOURCE = "Portail DRIAS, DCSC, MeteoFrance"


class DcscIndexRegistry(Registry[StandardIndex]):
    """
    Registry of the DCSC (Meteo France) specific indices.

    Note
    ----

    The indices metadata of this module are in French.
    """

    _item_class = StandardIndex

    @staticmethod
    def get_item_aliases(item: StandardIndex) -> list[str]:
        """
        Duck-typed method to get the aliases of a StandardIndex item.

        Parameters
        ----------
        item : StandardIndex
            The StandardIndex item.

        Returns
        -------
        list[str]
            The aliases of the item.

        Notes
        -----
        Every StandardIndex registry should implement this method.
        """
        return [item.short_name]

    TAV = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Moyenne de la température moyenne.",
        source=DCSC_SOURCE,
        short_name="TAV",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS],
    )
    TXAV = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="degree_Celsius",
        definition="Moyenne de la température maximale.",
        source=DCSC_SOURCE,
        short_name="TXAV",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[StandardVariableRegistry.TAS_MAX],
    )
    TRAV = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.MeanOfDifference,
        output_unit="degree_Celsius",
        definition="Moyenne de l'amplitude thermique.",
        source=DCSC_SOURCE,
        short_name="TRAV",
        group=IndexGroupRegistry.TEMPERATURE,
        input_variables=[
            StandardVariableRegistry.TAS_MIN,
            StandardVariableRegistry.TAS_MAX,
        ],
    )
    TX10 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition=(
            "Extrême froid de la température maximale"
            " journalière (10e centile de la température"
            " maximale)."
        ),
        source=DCSC_SOURCE,
        short_name="TX10",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TX90 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="> 90 doy_per",
        output_unit="day",
        definition=(
            "Extrême chaud de la température maximale journalière"
            " (90e centile de la température maximale)."
        ),
        source=DCSC_SOURCE,
        short_name="TX90",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TN10 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 10 doy_per",
        output_unit="day",
        definition=(
            "Extrême froid de la température minimale "
            " journalière (10e centile de la température minimale)."
        ),
        source=DCSC_SOURCE,
        short_name="TN10",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TN90 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition=(
            "Extrême chaud de la température minimale"
            " journalière (90e centile de la température minimale)."
        ),
        threshold="> 90 doy_per",
        source=DCSC_SOURCE,
        short_name="TN90",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[QUANTILE_BASED],
        doy_window_width=5,
    )
    TNFD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 0 degree_Celsius",
        output_unit="day",
        definition="Nombre de jours de gel (température minimale <= 0°C).",
        source=DCSC_SOURCE,
        short_name="TNFD",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[],
    )
    TXFD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold="< 0 degree_Celsius",
        output_unit="day",
        definition="Nombre de jours sans dégel (température maximale <= 0°C).",
        source=DCSC_SOURCE,
        short_name="TXFD",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    SD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Nombre de journées d'été (température maximale > 25°C).",
        source=DCSC_SOURCE,
        short_name="SD",
        threshold="> 25 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    TX35 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Nombre de jours de forte chaleur (température maximale > 35°C).",
        source=DCSC_SOURCE,
        short_name="TX35",
        threshold="> 35 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[],
    )
    TR = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition="Nombre de nuits tropicales (température minimale > 20°C).",
        source=DCSC_SOURCE,
        short_name="TR",
        threshold="> 20 degree_Celsius",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[],
    )
    TXND = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        definition=(
            "Nombre de jours anormalement chauds"
            " (température maximale supérieure de plus de 5°C à la normale)."
        ),
        source=DCSC_SOURCE,
        short_name="TXND",
        threshold=build_threshold(
            operator=">",
            value=None,  # filled when Threshold::prepare is called
            unit="degree_Celsius",
            offset=" 5 delta_degree_Celsius",
        ),
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[NEEDS_NORMAL],
    )
    TNHT = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        threshold=build_threshold(
            operator=">",
            value=None,  # filled when Threshold::prepare is called
            unit="degree_Celsius",
            offset=" 5 delta_degree_Celsius",
        ),
        source=DCSC_SOURCE,
        short_name="TNHT",
        definition="Nombre de nuits anormalement chaudes (température minimale "
        "supérieure de plus de 5°C à la normale).",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[NEEDS_NORMAL],
    )
    TNND = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        output_unit="day",
        threshold=build_threshold(
            operator="<",
            value=None,  # filled when Threshold::prepare is called
            unit="degree_Celsius",
            offset=" 5 delta_degree_Celsius",
        ),
        source=DCSC_SOURCE,
        short_name="TNND",
        definition="Nombre de jours anormalement froids"
        " (température minimale inférieure de plus de 5°C à la normale).",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[NEEDS_NORMAL],
    )
    TNCWD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.SumOfSpellLengths,
        output_unit="day",
        threshold=build_threshold(
            operator="<",
            value=None,  # filled when Threshold::prepare is called
            unit="degree_Celsius",
            offset=" 5 delta_degree_Celsius",
        ),
        source=DCSC_SOURCE,
        short_name="TNCWD",
        definition="Nombre de jours d'une vague de froid"
        " (température min < de plus de 5°C à la normale pdt au moins "
        "5j consécutifs).",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS_MIN],
        qualifiers=[NEEDS_NORMAL],
    )
    TXHWD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.SumOfSpellLengths,
        output_unit="day",
        threshold=build_threshold(
            operator="<",
            value=None,  # filled when Threshold::prepare is called
            unit="degree_Celsius",
            offset=" 5 delta_degree_Celsius",
        ),
        source=DCSC_SOURCE,
        short_name="TXHWD",
        definition="Nombre de jours d'une vague de chaleur"
        " (température max > de plus de 5°C à la normale"
        " pdt au moins 5j consécutifs).",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS_MAX],
        qualifiers=[NEEDS_NORMAL],
    )
    HDD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Deficit,
        threshold="17 degree_Celsius",
        output_unit="degree_Celsius day",
        definition="Degrés-jours de chauffage"
        " (Cumul sur la période des écarts négatifs au seuil de < 17°C"
        " par la température qt moyenne).",
        source=DCSC_SOURCE,
        short_name="HDD",
        group=IndexGroupRegistry.COLD,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[],
    )
    CDD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Excess,
        threshold="18 degree_Celsius",
        output_unit="degree_Celsius day",
        definition="Degrés-jours de climatisation"
        "(Cumul sur la période des dépassements du seuil de > 18°C"
        " par la température qt moyenne).",
        source=DCSC_SOURCE,
        short_name="CDD",
        group=IndexGroupRegistry.HEAT,
        input_variables=[StandardVariableRegistry.TAS],
        qualifiers=[],
    )
    # PRECIPITATION
    PAV = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        output_unit="mm/day",
        definition="Précipitations quotidiennes moyennes.",
        source=DCSC_SOURCE,
        short_name="PAV",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    PINT = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Average,
        threshold=">= 1 mm/day",
        output_unit="mm/day",
        definition="Précipitation moyenne des jours pluvieux (RR > 1 mm).",
        source=DCSC_SOURCE,
        short_name="PINT",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RR = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Sum,
        output_unit="mm",
        definition="Cumul de précipitation.",
        source=DCSC_SOURCE,
        short_name="RR",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    RR1MM = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 1 mm/day",
        output_unit="day",
        definition="Nombre de jours de pluie (précipitations >= 1 mm).",
        source=DCSC_SOURCE,
        short_name="RR1MM",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    PN20MM = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=">= 20 mm/day",
        output_unit="day",
        definition="Nombre de jours de fortes précipitations"
        " (précipitations >= 20 mm).",
        source=DCSC_SOURCE,
        short_name="PN20MM",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    PXCDD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold="< 1 mm/day",
        output_unit="day",
        definition="Période de sécheresse (Max [Nbj consécutifs RR < 1 mm]).",
        source=DCSC_SOURCE,
        short_name="PXCDD",
        group=IndexGroupRegistry.DROUGHT,
        input_variables=[StandardVariableRegistry.PR],
    )
    PXCWD = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.MaxConsecutiveOccurrence,
        threshold=">= 1 mm/day",
        output_unit="day",
        definition="Nombre maximum de jours pluvieux consécutifs"
        " (Max [Nbj consécutifs RR > 1 mm]).",
        source=DCSC_SOURCE,
        short_name="PXCWD",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
    )
    R99 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=build_threshold("> 99 period_per", threshold_min_value="1 mm/day"),
        output_unit="day",
        definition="Nombre de jours de précipitations extrêmes.",
        source=DCSC_SOURCE,
        short_name="R99",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    PFL90 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.FractionOfTotal,
        threshold=build_threshold("> 90 period_per", threshold_min_value="1 mm/day"),
        output_unit="%",
        definition="Fraction des précipitations journalières intenses.",
        source=DCSC_SOURCE,
        short_name="PFL90",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    PQ90 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Percentile,
        threshold=build_threshold("> 90 doy_per", threshold_min_value="1 mm/day"),
        output_unit="%",
        definition="Précipitation quotidienne intense"
        " (90e centile des précipitations).",
        source=DCSC_SOURCE,
        short_name="PQ90",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    PQ99 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.Percentile,
        threshold=build_threshold("> 99 doy_per", threshold_min_value="1 mm/day"),
        output_unit="%",
        definition="Précipitation quotidienne extrême"
        " (99e centile des précipitations).",
        source=DCSC_SOURCE,
        short_name="PQ99",
        group=IndexGroupRegistry.RAIN,
        input_variables=[StandardVariableRegistry.PR],
        qualifiers=[QUANTILE_BASED],
    )
    # VITESSE DE VENT
    FFAV = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.DifferenceOfMeans,
        output_unit="m s-1",
        definition="Écart de la vitesse du vent moyenne journalière"
        " (par rapport à une periode de référence).",
        source=DCSC_SOURCE,
        short_name="FFAV",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.SFC_WIND],
        qualifiers=[REFERENCE_PERIOD_INDEX],
    )
    FF98 = StandardIndex(
        reference=DCSC_REFERENCE,
        indicator=GenericIndicatorRegistry.CountOccurrences,
        threshold=build_threshold("> 98 period_per", threshold_min_value="1 knots"),
        output_unit="days",
        definition="Nombre de jours de vent fort"
        " (vent ≥ 98e centile de la période de référence).",
        source=DCSC_SOURCE,
        short_name="FF98",
        group=IndexGroupRegistry.WIND,
        input_variables=[StandardVariableRegistry.SFC_WIND],
        qualifiers=[REFERENCE_PERIOD_INDEX, QUANTILE_BASED],
    )

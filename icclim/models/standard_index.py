from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import icclim.models.index_group as index_group
from icclim.generic_indices.standard_variable import StandardVariable


@dataclass
class StandardIndex:
    """Standard Index data class.
    It is used to describe how a GenericIndicator should be setup to compute a climate
    index that has been defined in the literature (such as ECA&D's ATBD document).


    Attributes
    ----------

    short_name: str
        The index name used in the output.
    compute: Callable
        The function to compute the index. It usually wraps a xclim functions.
    group: IndexGroup
        The index group category.
    variables: List[List[str]]
        The Cf variables needed to compute the index.
        The variable are individually described by a list of aliases.
    qualifiers: List[str] | None
        ``optional`` List of configuration to compute the index.
        Used internally to generate modules for C3S.
    source: str | None
        Where the index definition comes from.
    definition: str | None
        A formal definition of the index. It should describe what kind of output
        the user is expected to obtain.
    """

    short_name: str
    group: index_group.IndexGroup
    input_variables: list[StandardVariable] | None  # None when index is generic
    indicator: Any  # Any -> Indicator (circular dep)
    # todo: merge qualifiers with group into a Set of qualifiers ?
    qualifiers: list[str] | None = None
    source: str | None = None
    reference: str | None = None
    definition: str | None = None
    threshold: str | None | Any | Sequence[str | Any] = None  # Any -> Threshold
    output_unit: str | None = None
    # additional, index specific args
    rolling_window_width: int | None = None
    doy_window_width: int | None = None
    min_spell_length: int | None = None

    def __str__(self):
        return f"{self.group} | {self.short_name} | {self.definition}"

    def __call__(self, *args, **kwargs):
        self.indicator(*args, **kwargs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StandardIndex):
            return False
        return (
            self.indicator == other.indicator
            and self.threshold == other.threshold
            and self.output_unit == other.output_unit
            and self.rolling_window_width == other.rolling_window_width
            and self.doy_window_width == other.doy_window_width
            and self.min_spell_length == other.min_spell_length
        )

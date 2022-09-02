from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Tuple, Union

from xarray import DataArray

from icclim.generic_indices.cf_var_metadata import StandardVariable
from icclim.models.index_group import IndexGroup

ComputeIndexFun = Callable[
    [Any], Union[DataArray, Tuple[DataArray, Optional[DataArray]]]
]


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
    group: IndexGroup
    input_variables: list[StandardVariable] | None  # None when index is generic
    generic_indicator: Any  # Any -> GenericIndicator
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
        self.generic_indicator(*args, **kwargs)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, StandardIndex):
            return False
        return (
            self.generic_indicator.name == other.generic_indicator.name
            and self.threshold == other.threshold
            and self.output_unit == other.output_unit
            and self.rolling_window_width == other.rolling_window_width
            and self.doy_window_width == other.doy_window_width
            and self.min_spell_length == other.min_spell_length
        )

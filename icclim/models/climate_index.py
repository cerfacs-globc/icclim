from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Union

# from generic_indices.generic_indicators import GenericIndicator
from generic_indices.cf_var_metadata import StandardVariable
from xarray import DataArray

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
    qualifiers: list[str] | None = None
    source: str | None = None
    definition: str | None = None
    threshold: str | None = None
    output_unit: str | None = None
    # additional, index specific args
    rolling_window_width: int | None = None
    doy_window_width: int | None = None
    min_spell_length: int | None = None

    def __str__(self):
        return f"{self.group} | {self.short_name} | {self.definition}"

    def __call__(self, *args, **kwargs):
        self.generic_indicator(*args, **kwargs)

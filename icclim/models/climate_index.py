from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Union

from xarray import DataArray

from icclim.models.index_group import IndexGroup

ComputeIndexFun = Callable[
    [Any], Union[DataArray, Tuple[DataArray, Optional[DataArray]]]
]


@dataclass
class ClimateIndex:
    """Climate index data class.

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
    compute: ComputeIndexFun
    group: IndexGroup
    input_variables: list[list[str]]
    qualifiers: list[str] | None = None
    source: str | None = None
    definition: str | None = None

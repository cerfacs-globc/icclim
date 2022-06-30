from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
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
    input_variables: list[list[str]] | None  # None when index is generic
    qualifiers: list[str] | None = None
    source: str | None = None
    definition: str | None = None
    output_var_name: str | None = None  # when None use short_name

    def __str__(self):
        return f"{self.group.value} | {self.short_name} | {self.definition}"

    def format_output_name(self, threshold: list[float] | None = None) -> str:
        if self.output_var_name is None or threshold is None:
            return self.short_name
        else:
            return self.output_var_name.replace("{xx}", "_".join(map(str, threshold)))


class ClimateIndexEnum(Enum):
    """Abstract class of indicator catalogs."""

    def __init__(self, climate_index: ClimateIndex):
        self.climate_index = climate_index

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

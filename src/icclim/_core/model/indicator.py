"""Typing for generic indices."""

from __future__ import annotations

import abc
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xarray import DataArray
    from xclim.core.missing import MissingBase


class MissingMethodLike(ABC):
    """Workaround xclim missing type."""

    # TODO @bzah: PR that to xclim
    # https://github.com/cerfacs-globc/icclim/issues/289

    @abstractmethod
    def execute(self, *args, **kwargs) -> MissingBase:
        """Execute the missing method."""
        ...

    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """Validate the missing method."""
        ...


class Indicator(ABC):
    """
    Generic indicator abstract class.

    Attributes
    ----------
    name: str
        The name of the indicator.
    standard_name: str
        The standard name of the indicator, ideally from the CF conventions.
    long_name: str
        The long name of the indicator.
    cell_methods: str
        The cell methods of the indicator.
    qualifiers: tuple
        The qualifiers of the indicator, used to classify indicators.
    templated_properties: tuple
        The properties that can be templated.
        Theses properties are used to fill the output metadata.
    """

    name: str
    standard_name: str
    long_name: str
    cell_methods: str
    qualifiers: tuple

    templated_properties = (
        "standard_name",
        "long_name",
        "cell_methods",
    )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> DataArray:
        """Compute the indicator."""
        ...

    @abc.abstractmethod
    def preprocess(self, *args, **kwargs) -> list[DataArray]:
        """Preprocess the data."""
        ...

    @abc.abstractmethod
    def postprocess(self, *args, **kwargs) -> DataArray:
        """Postprocess the data."""
        ...

    @abc.abstractmethod
    def __eq__(self, __value: object) -> bool:
        """Check if two indicators are equal."""
        ...

    def clone(self) -> Indicator:
        """Clone the indicator."""
        from copy import deepcopy

        return deepcopy(self)

"""Contain the IndexGroup class and the IndexGroupRegistry class."""

from __future__ import annotations

import dataclasses
from typing import Any

from icclim._core.model.registry import Registry


@dataclasses.dataclass(init=False)
class IndexGroup:
    """
    Class representing a group of climate indices.

    Parameters
    ----------
    name : str
        The name of the index group.
    values : list[IndexGroup] | None, optional
        The list of index groups contained within this group. Defaults to None.

    Attributes
    ----------
    name : str
        The name of the index group.
    values : list[IndexGroup]
        The list of index groups contained within this group.

    """

    name: str
    values: list[IndexGroup]

    def __init__(self, name: str, values: list[IndexGroup] | None = None) -> None:
        self.name = name
        if values is None:
            self.values = [self]
        else:
            self.values = values

    def get_indices(self) -> list[Any]:
        """
        Get the list of indices belonging to this group.

        Returns
        -------
        list[Any]
            The list of indices belonging to this group.

        Notes
        -----
        The list of indices is obtained by filtering the EcadIndexRegistry values.
        The others indices are not considered.
        """
        from icclim.ecad.registry import EcadIndexRegistry

        return list(
            filter(lambda i: i.group in self.values, EcadIndexRegistry.values()),
        )

    def __or__(self, right: IndexGroup) -> IndexGroup:
        """
        Compose 2 IndexGroups to create a new one.

        Parameters
        ----------
        right : IndexGroup
            The IndexGroup to be composed with.

        Returns
        -------
        IndexGroup
            The composed IndexGroup.

        """
        return IndexGroup(f"{self.name}_{right.name}", [self, right])

    def __eq__(self, other: object) -> bool:
        """
        Check if two IndexGroup objects are equal.

        Parameters
        ----------
        other : IndexGroup
            The IndexGroup to compare with.

        Returns
        -------
        bool
            True if the two IndexGroup objects are equal, False otherwise.

        """
        if not isinstance(other, IndexGroup):
            return False
        return other.name == self.name


class IndexGroupRegistry(Registry[IndexGroup]):
    """Registry for IndexGroup instances."""

    _item_class = IndexGroup

    TEMPERATURE = IndexGroup("temperature")
    HEAT = IndexGroup("heat")
    COLD = IndexGroup("cold")
    DROUGHT = IndexGroup("drought")
    RAIN = IndexGroup("rain")
    SNOW = IndexGroup("snow")
    WIND = IndexGroup("wind")
    PRESSURE = IndexGroup("pressure")
    SUNSHINE = IndexGroup("sunshine")
    HUMIDITY = IndexGroup("humidity")
    # no climate index should be bounded to "all"
    WILD_CARD_GROUP = IndexGroup("all")

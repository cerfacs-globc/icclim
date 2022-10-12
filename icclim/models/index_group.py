from __future__ import annotations

import dataclasses
from typing import Any

from icclim.models.registry import Registry


@dataclasses.dataclass(init=False)
class IndexGroup:
    name: str
    values: list[IndexGroup]

    def __init__(self, name: str, values: list[IndexGroup] = None):
        self.name = name
        if values is None:
            self.values = [self]
        else:
            self.values = values

    def get_indices(self) -> list[Any]:
        # import locally to avoid circular dependency (an index has a IndexGroup)
        from icclim.ecad.ecad_indices import EcadIndexRegistry

        return list(
            filter(lambda i: i.group in self.values, EcadIndexRegistry.values())
        )

    def __or__(self, right):
        """Used to compose IndexGroup, e.g., IndexGroup1 | IndexGroup2."""
        if isinstance(right, IndexGroup):
            return IndexGroup(f"{self.name}_{right.name}", [self, right])
        raise NotImplementedError(
            f"Unexpected type for {right}: {type(right)}."
            f" An IndexGroup was expected."
        )

    def __eq__(self, other):
        if not isinstance(other, IndexGroup):
            return False
        return other.name == self.name


class IndexGroupRegistry(Registry[IndexGroup]):
    _item_class = IndexGroup

    TEMPERATURE = IndexGroup("temperature")
    HEAT = IndexGroup("heat")
    COLD = IndexGroup("cold")
    DROUGHT = IndexGroup("drought")
    RAIN = IndexGroup("rain")
    SNOW = IndexGroup("snow")
    WIND = IndexGroup("wind")
    # no climate index should be bounded to "all"
    WILD_CARD_GROUP = IndexGroup("all")

from __future__ import annotations

import dataclasses
from typing import Any

from icclim.models.registry import Registry


@dataclasses.dataclass
class IndexGroup:
    name: str

    def get_indices(self) -> list[Any]:
        # import locally to avoid circular dependency (an index has a IndexGroup)
        from icclim.ecad.ecad_indices import EcadIndexRegistry

        return list(filter(lambda i: i.group == self, EcadIndexRegistry.values()))


class IndexGroupRegistry(Registry):
    _item_class = IndexGroup

    TEMPERATURE = IndexGroup("temperature")
    HEAT = IndexGroup("heat")
    COLD = IndexGroup("cold")
    DROUGHT = IndexGroup("drought")
    RAIN = IndexGroup("rain")
    SNOW = IndexGroup("snow")
    COMPOUND = IndexGroup("compound")
    GENERIC = IndexGroup("generic")
    # no climate index should be bounded to "all"
    WILD_CARD_GROUP = IndexGroup("all")

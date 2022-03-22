from __future__ import annotations

from enum import Enum
from typing import Any


class IndexGroup(Enum):
    TEMPERATURE = "temperature"
    HEAT = "heat"
    COLD = "cold"
    DROUGHT = "drought"
    RAIN = "rain"
    SNOW = "snow"
    COMPOUND = "compound"
    WILD_CARD_GROUP = "all"  # no index bound to it

    @staticmethod
    def lookup(query: str | IndexGroup) -> IndexGroup:
        if isinstance(query, IndexGroup):
            return query
        for gr in IndexGroup:
            if gr.value.upper() == query.upper():
                return gr
        valid_values = list(map(lambda x: x.value, IndexGroup))
        raise NotImplementedError(
            f"IndexGroup must be one of the following: {valid_values},"
            f" but query was {query}."
        )

    def get_indices(self) -> list[Any]:
        # import locally to avoid circular dependency (an index has already a group)
        from icclim.models.ecad_indices import EcadIndex

        return list(filter(lambda i: i.group == self, EcadIndex))

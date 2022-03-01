from enum import Enum
from typing import Any, Union


class IndexGroup(Enum):
    TEMPERATURE = "temperature"
    HEAT = "heat"
    COLD = "cold"
    DROUGHT = "drought"
    RAIN = "rain"
    SNOW = "snow"
    COMPOUND = "compound"

    @staticmethod
    def lookup(query: Union[str, Any]):
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

    def get_indices(self):
        from icclim.models.ecad_indices import EcadIndex

        return list(filter(lambda i: i.group == self, EcadIndex))

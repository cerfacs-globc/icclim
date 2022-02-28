from enum import Enum


class IndexGroup(Enum):
    TEMPERATURE = "temperature"
    HEAT = "heat"
    COLD = "cold"
    DROUGHT = "drought"
    RAIN = "rain"
    SNOW = "snow"
    COMPOUND = "compound"

    @staticmethod
    def lookup(query: str):
        for interpolation in IndexGroup:
            if interpolation.value.upper() == query.upper():
                return interpolation
        valid_values = list(map(lambda x: x.value, IndexGroup))
        raise NotImplementedError(
            f"IndexGroup must be one of the following: {valid_values},"
            f" but query was {query}."
        )

from enum import Enum
from typing import List, Union


class Frequency(Enum):
    """
    YEAR (default) 	annual
    MONTH 	monthly (all months)
    ONDJFM 	winter half-year
    AMJJAS 	summer half-year
    DJF 	winter
    MAM 	spring
    JJA 	summer
    SON 	autumn
    """

    MONTH = ("MS", ["month", "MS"])
    AMJJAS = ("", ["AMJJAS"])  # TODO
    ONDJFM = ("", ["ONDJFM"])  # TODO
    DJF = ("QS-DEC", ["DJF", "QS-DEC"])
    MAM = ("YS", ["MAM",])  # TODO
    JJA = ("YS", ["JJA",])  # TODO
    SON = ("YS", ["SON",])  # TODO
    YEAR = ("YS", ["year", "YS"])

    def __init__(self, panda_time: str, accepted_values: List[str]):
        self.panda_freq = panda_time
        self.accepted_values = accepted_values


def build_frequency(s: Union[str, Frequency]) -> Frequency:
    # TODO write unit test
    if s is Frequency:
        return s
    for f in Frequency:
        if f.name == s.upper() or s.upper() in map(f.accepted_values, str.upper()):
            return f
    raise Exception(f"Unknown frequency {s}")  # TODO use click BadParam exception

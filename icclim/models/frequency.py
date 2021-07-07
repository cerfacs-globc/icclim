from enum import Enum
from typing import Callable, List, Union
import numpy

from xarray.core.dataarray import DataArray


def sesons_resampler(start_month: int, end_month: int):
    def x(da):
        months = da.time.dt.month
        return da.where(
            numpy.logical_and(months >= start_month, months <= end_month), drop=True
        )

    return x


# Bsecause it's overlapping between 2 years, winter need it's own coputation function
def winter_resampler(start_month: int, end_month: int):
    def x(da):
        months = da.time.dt.month
        return lambda da: da.where(
            numpy.logical_or(months <= end_month, months >= start_month), drop=True
        )

    return x


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
    AMJJAS = ("MS", ["AMJJAS"], sesons_resampler(4, 9))
    ONDJFM = ("MS", ["ONDJFM"], winter_resampler(10, 3))
    DJF = ("MS", ["DJF",], winter_resampler(12, 2))
    MAM = ("MS", ["MAM",], sesons_resampler(3, 5))
    JJA = ("MS", ["JJA",], sesons_resampler(6, 8))
    SON = ("MS", ["SON",], sesons_resampler(9, 11))
    YEAR = ("YS", ["year", "YS"])

    def __init__(
        self,
        panda_time: str,
        accepted_values: List[str],
        resampler: Callable[[DataArray], DataArray] = None,
    ):
        self.panda_freq = panda_time
        self.accepted_values = accepted_values
        resampler = resampler


def build_frequency(s: Union[str, Frequency]) -> Frequency:
    # TODO write unit test
    if s is Frequency:
        return s
    for f in Frequency:
        if f.name == s.upper() or s.upper() in map(f.accepted_values, str.upper()):
            return f
    raise Exception(f"Unknown frequency {s}")  # TODO use click BadParam exception


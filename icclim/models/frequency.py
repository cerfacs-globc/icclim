from enum import Enum
from icclim.types import SliceMode
from typing import Callable, List, Tuple, Union
from _pytest.compat import NOTSET
import numpy
import xarray

from xarray.core.dataarray import DataArray


def seasons_resampler(
    start_month: int, end_month: int
) -> Callable[[DataArray], DataArray]:
    def resampler(da: DataArray):
        months = da.time.dt.month
        return da.where(
            numpy.logical_and(months >= start_month, months <= end_month), drop=True
        )

    return resampler


# Because it is overlapping between 2 years, winter need it's own computation function
def winter_resampler(
    start_month: int, end_month: int
) -> Callable[[DataArray], DataArray]:
    def resampler(da: DataArray):
        months = da.time.dt.month
        return da.where(
            numpy.logical_or(months <= end_month, months >= start_month), drop=True
        )

    return resampler


def month_resampler(month_list: List[int]) -> Callable[[DataArray], DataArray]:
    def resampler(da: DataArray):
        acc = []
        for gr, val in da.groupby(da.time.dt.month):
            if gr in month_list:
                acc.append(val)
        return xarray.concat(acc, "time")

    return resampler


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
    AMJJAS = ("MS", ["AMJJAS"], seasons_resampler(4, 9))
    ONDJFM = ("MS", ["ONDJFM"], winter_resampler(10, 3))
    DJF = ("MS", ["DJF",], winter_resampler(12, 2))
    MAM = ("MS", ["MAM",], seasons_resampler(3, 5))
    JJA = ("MS", ["JJA",], seasons_resampler(6, 8))
    SON = ("MS", ["SON",], seasons_resampler(9, 11))
    YEAR = ("YS", ["year", "YS"])
    CUSTOM = ("MS", [], None)

    def __init__(
        self,
        panda_time: str,
        accepted_values: List[str],
        resampler: Callable[[DataArray], DataArray] = None,
    ):
        self.panda_freq = panda_time
        self.accepted_values = accepted_values
        self.resampler = resampler


def build_frequency(slice_mode: SliceMode) -> Frequency:
    if isinstance(slice_mode, Frequency):
        return slice_mode
    if isinstance(slice_mode, str):
        return get_frequency_from_string(slice_mode)
    if isinstance(slice_mode, list):
        return get_frequency_from_list(slice_mode)
    raise Exception(f"Unknown frequency {slice_mode}")


def get_frequency_from_string(slice_mode: str):
    for freq in Frequency:
        if freq.name == slice_mode.upper() or slice_mode.upper() in map(
            str.upper, freq.accepted_values
        ):
            return freq
    raise Exception(f"Unknown frequency {slice_mode}")


def get_frequency_from_list(slice_mode_list: List):
    if len(slice_mode_list) < 2:
        raise f"Unknown frequency {slice_mode_list}"
    sampling_freq = slice_mode_list[0]
    months = slice_mode_list[1]
    custom_freq = Frequency.CUSTOM
    if sampling_freq == "month":
        custom_freq.resampler = month_resampler(months)
    elif sampling_freq == "season":
        if months is Tuple:
            custom_freq.resampler = winter_resampler(months[0][0], months[1][-1])
        else:
            custom_freq.resampler = seasons_resampler(months[0], months[-1])
    else:
        raise f"Unknown frequency {slice_mode_list}"
    return custom_freq

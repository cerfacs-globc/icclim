from enum import Enum
from typing import Callable, List, Tuple, Union
from _pytest.compat import NOTSET
import numpy
import pandas
import xarray

from xarray.core.dataarray import DataArray


def seasons_resampler(
    start_month: int, end_month: int
) -> Callable[[DataArray], DataArray]:
    def resampler(da: DataArray) -> Tuple[DataArray, DataArray]:
        years = numpy.unique(da.time.dt.year)
        acc = []
        time_bounds = []
        middle_date = []
        is_overlapping_season = start_month > end_month
        for year in years:
            if is_overlapping_season:
                start_season_date = pandas.to_datetime(f"{year-1}-{start_month}")
            else:
                start_season_date = pandas.to_datetime(f"{year}-{start_month}")
            end_season_date = pandas.to_datetime(f"{year}-{end_month}")
            season_of_year = da.sel(time=slice(start_season_date, end_season_date)).sum(
                "time"
            )
            middle_date.append(
                start_season_date
                + (pandas.to_datetime(f"{year}-{end_month+1}") - start_season_date) / 2
            )
            time_bounds.append([start_season_date, end_season_date])
            acc.append(season_of_year)
        seasons = xarray.concat(acc, "time")
        seasons.coords["time"] = ("time", middle_date)
        seasons.time.attrs["bounds"] = "time_bounds"
        seasons.time._copy_attrs_from(da.time)
        time_bounds_da = DataArray(
            time_bounds,
            dims=["time", "bounds"],
            coords=[("time", seasons.time), ("bounds", [0, 1])],
        )
        return (seasons, time_bounds_da)

    return resampler


def month_resampler(month_list: List[int]) -> Callable[[DataArray], DataArray]:
    def resampler(da: DataArray):
        return da.sel(time=da.time.dt.month.isin(month_list))

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
    ONDJFM = ("MS", ["ONDJFM"], seasons_resampler(10, 3))
    DJF = ("MS", ["DJF",], seasons_resampler(12, 2))
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
        self.panda_freq: str = panda_time
        self.accepted_values: List[str] = accepted_values
        self.resampler: Callable[[DataArray], DataArray] = resampler


SliceMode = Union[Frequency, str, List[Union[str, Tuple, int]]]


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
            custom_freq.resampler = seasons_resampler(months[0][0], months[1][-1])
        else:
            custom_freq.resampler = seasons_resampler(months[0], months[-1])
    else:
        raise f"Unknown frequency {slice_mode_list}"
    return custom_freq

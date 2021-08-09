from enum import Enum
from typing import Callable, List, Tuple, Union

import numpy
import pandas
import xarray
from xarray.core.dataarray import DataArray


# month_list must be ordered from first month of season to the last. Example: [11, 1, 2,4]
def seasons_resampler(
    month_list: List[int],
) -> Callable[[DataArray], Tuple[DataArray, DataArray]]:
    def resampler(da: DataArray) -> Tuple[DataArray, DataArray]:
        da_years = numpy.unique(da.time.dt.year)
        acc: List[DataArray] = []
        time_bnds = []
        middle_date = []
        start_month = month_list[0]
        end_month = month_list[-1]
        filtered_da = month_filter(month_list)(da)
        # TODO, maybe raise a warning if the month_list is not made of consecutive month (case of user error)
        for year in da_years:
            if start_month > end_month:
                start_season_date = pandas.to_datetime(f"{year-1}-{start_month}")
            else:
                start_season_date = pandas.to_datetime(f"{year}-{start_month}")
            end_season_date = (
                pandas.to_datetime(f"{year}-{end_month+1}")
                - pandas.tseries.offsets.Day()
            )  # type:ignore
            season_of_year = filtered_da.sel(
                time=slice(start_season_date, end_season_date)
            ).sum("time")
            middle_date.append(
                start_season_date + (end_season_date - start_season_date) / 2
            )
            time_bnds.append([start_season_date, end_season_date])
            acc.append(season_of_year)
        seasons = xarray.concat(acc, "time")
        seasons.coords["time"] = ("time", middle_date)
        # FIXME: In case of month_list with holes, such as [1,3,4,6]; How do we show this in metatadas ?
        seasons.time.attrs["bounds"] = "time_bnds"
        seasons.time._copy_attrs_from(da.time)
        time_bnds_da = DataArray(
            data=time_bnds,
            dims=["time", "bounds"],
            coords=[("time", seasons.time.data), ("bounds", [0, 1])],
        )  # TODO make sure it works, and there is no duplicated time coords in the final dataset
        return (seasons, time_bnds_da)

    return resampler


def month_filter(month_list: List[int]) -> Callable[[DataArray], DataArray]:
    def resampler(da: DataArray):
        # TODO see what kind of time_bounds is expected here
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
    AMJJAS = ("MS", ["AMJJAS"], seasons_resampler([*range(4, 9)]))
    ONDJFM = ("MS", ["ONDJFM"], seasons_resampler([10, 11, 12, 1, 2, 3]))
    DJF = ("MS", ["DJF"], seasons_resampler([12, 1, 2]))
    MAM = ("MS", ["MAM"], seasons_resampler([*range(3, 5)]))
    JJA = ("MS", ["JJA"], seasons_resampler([*range(6, 8)]))
    SON = ("MS", ["SON"], seasons_resampler([*range(9, 11)]))
    YEAR = ("YS", ["year", "YS"])
    CUSTOM = ("MS", [], None)

    def __init__(
        self,
        panda_time: str,
        accepted_values: List[str],
        resampler: Callable[[DataArray], Tuple[DataArray, DataArray]] = None,
    ):
        self.panda_freq: str = panda_time
        self.accepted_values: List[str] = accepted_values
        self.resampler = resampler


SliceMode = Union[Frequency, str, List[Union[str, Tuple, int]]]


def build_frequency(slice_mode: SliceMode) -> Frequency:
    if isinstance(slice_mode, Frequency):
        return slice_mode
    if isinstance(slice_mode, str):
        return get_frequency_from_string(slice_mode)
    if isinstance(slice_mode, list):
        return get_frequency_from_list(slice_mode)
    raise Exception(f"Unknown frequency {slice_mode}")


def get_frequency_from_string(slice_mode: str) -> Frequency:
    for freq in Frequency:
        if freq.name == slice_mode.upper() or slice_mode.upper() in map(
            str.upper, freq.accepted_values
        ):
            return freq
    raise Exception(f"Unknown frequency {slice_mode}")


def get_frequency_from_list(slice_mode_list: List) -> Frequency:
    if len(slice_mode_list) < 2:
        raise Exception(f"Unknown frequency {slice_mode_list}")
    sampling_freq = slice_mode_list[0]
    months = slice_mode_list[1]
    custom_freq = Frequency.CUSTOM
    if sampling_freq == "month":
        custom_freq.resampler = month_filter(months)
    elif sampling_freq == "season":
        if months is Tuple:
            # TODO add deprecation for the Tuple, because we support [11,12,1] and it will avoid the need of concat here
            custom_freq.resampler = seasons_resampler(months[1] + months[0])
        else:
            custom_freq.resampler = seasons_resampler(months)
    else:
        raise Exception(f"Unknown frequency {slice_mode_list}")
    return custom_freq

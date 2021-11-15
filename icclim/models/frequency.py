from enum import Enum
from typing import Callable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import xarray as xr
from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError


def seasons_resampler(
    month_list: List[int],
) -> Callable[[DataArray], Tuple[DataArray, DataArray]]:
    def resampler(da: DataArray) -> Tuple[DataArray, DataArray]:
        da_years = np.unique(da.time.dt.year)
        acc: List[DataArray] = []
        time_bounds = []
        middle_date = []
        start_month = month_list[0]
        end_month = month_list[-1]
        filtered_da, _ = month_filter(month_list)(da)
        # TODO, maybe raise a warning if the month_list is not made of consecutive month (case of user error)
        for year in da_years:
            if start_month > end_month:
                start_season_date = pd.to_datetime(f"{year - 1}-{start_month}")
            else:
                start_season_date = pd.to_datetime(f"{year}-{start_month}")
            end_season_date = (
                pd.to_datetime(f"{year}-{end_month + 1}") - pd.tseries.offsets.Day()
            )  # type:ignore
            season_of_year = filtered_da.sel(
                time=slice(start_season_date, end_season_date)
            ).sum("time")
            middle_date.append(
                start_season_date + (end_season_date - start_season_date) / 2
            )
            time_bounds.append([start_season_date, end_season_date])
            acc.append(season_of_year)
        seasons = xr.concat(acc, "time")
        seasons.coords["time"] = ("time", middle_date)
        time_bounds_da = DataArray(
            data=time_bounds,
            dims=["time", "bounds"],
            coords=[("time", seasons.time.values), ("bounds", [0, 1])],
        )
        return seasons, time_bounds_da

    return resampler


def month_filter(
    month_list: List[int],
) -> Callable[[DataArray], Tuple[DataArray, None]]:
    def resampler(da: DataArray) -> Tuple[DataArray, None]:
        # no time_bds for this kind of resampling
        return da.sel(time=da.time.dt.month.isin(month_list)), None

    return resampler


def _add_time_bounds(freq: str) -> Callable[[DataArray], Tuple[DataArray, DataArray]]:
    def add_bounds(da: DataArray) -> Tuple[DataArray, DataArray]:
        # da should already be resampled to freq
        offset = pd.tseries.frequencies.to_offset(freq)
        time_bounds_da = DataArray(
            data=list(zip(da.time.values, (da.time.dt.date + offset).values)),
            dims=["time", "bounds"],
            coords=[("time", da.time.values), ("bounds", [0, 1])],
        )
        return da, time_bounds_da

    return add_bounds


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

    MONTH = ("MS", ["month", "MS"], "monthly time series", _add_time_bounds("MS"))
    AMJJAS = (
        "MS",
        ["AMJJAS"],
        "summer half-year time series",
        seasons_resampler([*range(4, 9)]),
    )
    ONDJFM = (
        "MS",
        ["ONDJFM"],
        "winter half-year time series",
        seasons_resampler([10, 11, 12, 1, 2, 3]),
    )
    DJF = ("MS", ["DJF"], "winter time series", seasons_resampler([12, 1, 2]))
    MAM = ("MS", ["MAM"], "spring time series", seasons_resampler([*range(3, 5)]))
    JJA = ("MS", ["JJA"], "summer time series", seasons_resampler([*range(6, 8)]))
    SON = ("MS", ["SON"], "autumn time series", seasons_resampler([*range(9, 11)]))
    CUSTOM = ("MS", [], None, None)
    YEAR = ("YS", ["year", "YS"], "annual time series", _add_time_bounds("YS"))

    def __init__(
        self,
        panda_time: str,
        accepted_values: List[str],
        description: Optional[str] = None,
        resampler: Optional[Callable[[DataArray], Tuple[DataArray, DataArray]]] = None,
    ):
        self.panda_freq: str = panda_time
        self.accepted_values: List[str] = accepted_values
        self.description = description
        # TODO maybe rename this property, it's not always a resampler (see _add_time_bounds)
        self.resampler = resampler


SliceMode = Union[Frequency, str, List[Union[str, Tuple, int]]]


def build_frequency(slice_mode: SliceMode) -> Frequency:
    if isinstance(slice_mode, Frequency):
        return slice_mode
    if isinstance(slice_mode, str):
        return _get_frequency_from_string(slice_mode)
    if isinstance(slice_mode, list):
        return _get_frequency_from_list(slice_mode)
    raise InvalidIcclimArgumentError(
        f"Unknown frequency {slice_mode}."
        f"Use a Frequency from {[f for f in Frequency]}"
    )


def _get_frequency_from_string(slice_mode: str) -> Frequency:
    for freq in Frequency:
        if freq.name == slice_mode.upper() or slice_mode.upper() in map(
            str.upper, freq.accepted_values
        ):
            return freq
    raise InvalidIcclimArgumentError(f"Unknown frequency {slice_mode}.")


def _get_frequency_from_list(slice_mode_list: List) -> Frequency:
    if len(slice_mode_list) < 2:
        raise InvalidIcclimArgumentError(
            f"The given slice list {slice_mode_list}"
            f" has a length of {len(slice_mode_list)}."
            f" The maximum length here is 2."
        )
    sampling_freq = slice_mode_list[0]
    months = slice_mode_list[1]
    custom_freq = Frequency.CUSTOM
    if sampling_freq == "month":
        custom_freq.resampler = month_filter(months)
        custom_freq.description = f"monthly time series (months: {months})"
    elif sampling_freq == "season":
        if months is Tuple:
            month_list = months[1] + months[0]
            custom_freq.resampler = seasons_resampler(month_list)
            custom_freq.description = f"seasonal time series (season: {month_list})"
        else:
            custom_freq.resampler = seasons_resampler(months)
            custom_freq.description = f"seasonal time series (season: {months})"
    else:
        raise InvalidIcclimArgumentError(
            f"Unknown frequency {slice_mode_list}. "
            "The sampling frequency must be one of {'season', 'month'}"
        )
    return custom_freq

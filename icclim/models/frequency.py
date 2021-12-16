"""
    `icclim.models.frequency` wraps the concept of pandas frequency in order to resample
    time series.  `slice_mode` paramater of `icclim.index` is always converted to a
    `Frequency`.
"""

import datetime
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple, Union

import cftime
import numpy as np
import pandas as pd
import xarray as xr
from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError

SliceMode = Union[Any, str, List[Union[str, Tuple, int]]]


def seasons_resampler(
    month_list: List[int],
) -> Callable[[DataArray], Tuple[DataArray, DataArray]]:
    """
    Seasonal resampling method generator.
    Returns a callable of DataArray which will resample the data to
    the a season composed of the given month.
    It also attached the corresponding time_bounds.
    Parameters
    ----------
    month_list : List[int]
        List of month identified by `{1..12}`.
    Returns
    -------
    function: Callable[[DataArray], DataArray]
        function resampling the input da to the wanted season.
    """

    def resampler(da: DataArray) -> Tuple[DataArray, DataArray]:
        da_years = np.unique(da.time.dt.year)
        seasons_acc: List[DataArray] = []
        time_bounds = []
        new_time_axis = []
        start_month = month_list[0]
        end_month = month_list[-1]
        filtered_da = month_filter(da, month_list)
        # TODO, maybe raise a warning if the month_list is not made of consecutive month
        #       (case of user error)
        for year in da_years:
            if start_month > end_month:
                int_year = year - 1
            else:
                int_year = year
            first_time = filtered_da.time.values[0]
            if isinstance(first_time, cftime.datetime):
                start = cftime.datetime(
                    year, start_month, 1, calendar=first_time.calendar
                )
                end = cftime.datetime(
                    year, end_month + 1, 1, calendar=first_time.calendar
                )
            else:
                start = pd.to_datetime(f"{int_year}-{start_month}")
                end = pd.to_datetime(f"{year}-{end_month + 1}")
            end = end - datetime.timedelta(days=1)
            season = filtered_da.sel(time=slice(start, end)).sum("time")
            new_time_axis.append(start + (end - start) / 2)
            time_bounds.append([start, end])
            seasons_acc.append(season)
        seasons = xr.concat(seasons_acc, "time")
        seasons.coords["time"] = ("time", new_time_axis)
        time_bounds_da = DataArray(
            data=time_bounds,
            dims=["time", "bounds"],
            coords=[("time", seasons.time.values), ("bounds", [0, 1])],
        )
        return seasons, time_bounds_da

    return resampler


def month_filter(da: DataArray, month_list: List[int]) -> DataArray:
    return da.sel(time=da.time.dt.month.isin(month_list))


def _add_time_bounds(freq: str) -> Callable[[DataArray], Tuple[DataArray, DataArray]]:
    def add_bounds(da: DataArray) -> Tuple[DataArray, DataArray]:
        # da should already be resampled to freq
        if isinstance(da.indexes.get("time"), xr.CFTimeIndex):
            offset = xr.coding.cftime_offsets.to_offset(freq)
            start = np.array(
                [
                    cftime.datetime(
                        date.year,
                        date.month,
                        date.day,
                        date.hour,
                        date.minute,
                        date.second,
                        calendar=date.calendar,
                    )
                    for date in da.indexes.get("time")
                ]
            )
            end = start + offset
            end = end - datetime.timedelta(days=1)
        else:
            offset = pd.tseries.frequencies.to_offset(freq)
            start = pd.to_datetime(da.time.dt.floor("D"))
            end = start + offset
            end = end - pd.Timedelta(days=1)
        da["time"] = start + (end - start) / 2
        time_bounds_da = DataArray(
            data=list(zip(start, end)),
            dims=["time", "bounds"],
            coords=[("time", da.time.values), ("bounds", [0, 1])],
        )
        return da, time_bounds_da

    return add_bounds


class Frequency(Enum):
    """
    The sampling frequency of the resulting dataset.
    """

    MONTH = ("MS", ["month", "MS"], "monthly time series", _add_time_bounds("MS"))
    """ Resample to monthly values"""

    AMJJAS = (
        "MS",
        ["AMJJAS"],
        "summer half-year time series",
        seasons_resampler([*range(4, 9)]),
    )
    """ Resample to summer half-year, from April to September included."""

    ONDJFM = (
        "MS",
        ["ONDJFM"],
        "winter half-year time series",
        seasons_resampler([10, 11, 12, 1, 2, 3]),
    )
    """ Resample to winter half-year, from October to March included."""

    DJF = ("MS", ["DJF"], "winter time series", seasons_resampler([12, 1, 2]))
    """ Resample to winter season, from December to February included."""

    MAM = ("MS", ["MAM"], "spring time series", seasons_resampler([*range(3, 6)]))
    """ Resample to spring season, from March to May included."""

    JJA = ("MS", ["JJA"], "summer time series", seasons_resampler([*range(6, 9)]))
    """ Resample to summer season, from June to Agust included."""

    SON = ("MS", ["SON"], "autumn time series", seasons_resampler([*range(9, 12)]))
    """ Resample to fall season, from September to November included."""

    CUSTOM = ("MS", [], None, None)
    """ Resample to custom values. Do not use as is, use `slice_mode` with month or season
        keywords instead.
    """

    YEAR = ("YS", ["year", "YS"], "annual time series", _add_time_bounds("YS"))
    """ Resample to yearly values."""

    def __init__(
        self,
        panda_time: str,
        accepted_values: List[str],
        description: Optional[str] = None,
        post_processing: Optional[
            Callable[[DataArray], Tuple[DataArray, DataArray]]
        ] = None,
    ):
        self.panda_freq: str = panda_time
        self.accepted_values: List[str] = accepted_values
        self.description = description
        self.post_processing = post_processing

    @staticmethod
    def lookup(slice_mode: SliceMode) -> Any:
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
        custom_freq.post_processing = lambda da: month_filter(da, months)
        custom_freq.description = f"monthly time series (months: {months})"
    elif sampling_freq == "season":
        if months is Tuple:
            rearranged_months = months[1] + months[0]
            custom_freq.post_processing = seasons_resampler(rearranged_months)
            custom_freq.description = (
                f"seasonal time series (season: {rearranged_months})"
            )
        else:
            custom_freq.post_processing = seasons_resampler(months)
            custom_freq.description = f"seasonal time series (season: {months})"
    else:
        raise InvalidIcclimArgumentError(
            f"Unknown frequency {slice_mode_list}. "
            "The sampling frequency must be one of {'season', 'month'}"
        )
    return custom_freq

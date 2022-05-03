"""
    `icclim.models.frequency` wraps the concept of pandas frequency in order to resample
    time series.  `slice_mode` paramater of `icclim.index` is always converted to a
    `Frequency`.
"""
from __future__ import annotations

import datetime
from enum import Enum
from typing import Callable, List, Tuple, Union

import cftime
import numpy as np
import pandas as pd
import xarray as xr
from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import (
    AMJJAS_MONTHS,
    DJF_MONTHS,
    JJA_MONTHS,
    MAM_MONTHS,
    MONTHS_MAP,
    ONDJFM_MONTHS,
    SON_MONTHS,
)


def get_month_filter(month_list: list[int]) -> Callable:
    return lambda da: filter_months(da, month_list)


def filter_months(da: DataArray, month_list: list[int]) -> DataArray:
    return da.sel(time=da.time.dt.month.isin(month_list))


def get_seasonal_time_updater(
    start_month: int,
    end_month: int,
) -> Callable[[DataArray], tuple[DataArray, DataArray]]:
    """Seasonal time updater and time bounds creator method generator.
    Returns a callable of DataArray which will rewrite the time dimension to
    the season composed of the given month. The data must have been computed on this
    season beforehand.
    It also create the corresponding time_bounds.
    Parameters
    ----------
    start_month: int
        The season starting month, it must be between 1 and 12.
    end_month: int
        The season ending month, it must be between 1 and 12.
    Returns
    -------
    function: Callable[[DataArray], DataArray]
        function resampling the input da to the wanted season.
    """

    def add_time_bounds(da: DataArray) -> tuple[DataArray, DataArray]:
        da_years = np.unique(da.time.dt.year)
        time_bounds = []
        new_time_axis = []
        first_time = da.time.values[0]
        for year in da_years:
            if start_month > end_month:
                year_of_season_end = year + 1
            else:
                year_of_season_end = year
            if isinstance(first_time, cftime.datetime):
                start = cftime.datetime(
                    year, start_month, 1, calendar=first_time.calendar
                )
                end = cftime.datetime(
                    year_of_season_end, end_month + 1, 1, calendar=first_time.calendar
                )
            else:
                start = pd.to_datetime(f"{year}-{start_month}")
                end = pd.to_datetime(f"{year_of_season_end}-{end_month + 1}")
            end = end - datetime.timedelta(days=1)
            new_time_axis.append(start + (end - start) / 2)
            time_bounds.append([start, end])
        da.coords["time"] = ("time", new_time_axis)
        time_bounds_da = DataArray(
            data=time_bounds,
            dims=["time", "bounds"],
            coords=[("time", da.time.values), ("bounds", [0, 1])],
        )
        return da, time_bounds_da

    return add_time_bounds


def _get_time_bounds_updater(
    freq: str,
) -> Callable[[DataArray], tuple[DataArray, DataArray]]:
    def add_time_bounds(da: DataArray) -> tuple[DataArray, DataArray]:
        # da should already be resampled to freq
        if isinstance(da.indexes.get("time"), xr.CFTimeIndex):
            offset = xr.coding.cftime_offsets.to_offset(freq)
            starts = np.array(
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
            ends = starts + offset
            ends = ends - datetime.timedelta(days=1)
        else:
            offset = pd.tseries.frequencies.to_offset(freq)
            starts = pd.to_datetime(da.time.dt.floor("D"))
            ends = starts + offset
            ends = ends - pd.Timedelta(days=1)
        # make time axis values be in the middle of the bounds
        da["time"] = starts + (ends - starts) / 2
        time_bounds_da = DataArray(
            data=list(zip(starts, ends)),
            dims=["time", "bounds"],
            coords=[("time", da.time.values), ("bounds", [0, 1])],
        )
        return da, time_bounds_da

    return add_time_bounds


class _Freq:
    """Internal class to ease writing and maintaining the enum.
    Without it, in the instanciation of enum values we would have to write tuples
    would not be able to use kwargs, which make the code less readable.
    """

    def __init__(
        self,
        panda_freq: str,
        accepted_values: list[str],
        description: str,
        post_processing: Callable[[DataArray], tuple[DataArray, DataArray]],
        pre_processing: Callable[[DataArray], DataArray],
    ):
        self.panda_freq: str = panda_freq
        self.accepted_values: list[str] = accepted_values
        self.description = description
        self.post_processing = post_processing
        self.pre_processing = pre_processing


class Frequency(Enum):
    """The sampling frequency of the resulting dataset."""

    MONTH = _Freq(
        panda_freq="MS",
        accepted_values=["month", "MS"],
        description="monthly time series",
        post_processing=_get_time_bounds_updater("MS"),
        pre_processing=lambda x: x,
    )
    """ Resample to monthly values"""

    AMJJAS = _Freq(
        panda_freq="AS-APR",
        accepted_values=["AMJJAS"],
        description="summer half-year time series",
        post_processing=get_seasonal_time_updater(AMJJAS_MONTHS[0], AMJJAS_MONTHS[-1]),
        pre_processing=get_month_filter(AMJJAS_MONTHS),
    )
    """ Resample to summer half-year, from April to September included."""

    ONDJFM = _Freq(
        panda_freq="AS-OCT",
        accepted_values=["ONDJFM"],
        description="winter half-year time series",
        post_processing=get_seasonal_time_updater(ONDJFM_MONTHS[0], ONDJFM_MONTHS[-1]),
        pre_processing=get_month_filter(ONDJFM_MONTHS),
    )
    """ Resample to winter half-year, from October to March included."""

    DJF = _Freq(
        panda_freq="AS-DEC",
        accepted_values=["DJF"],
        description="winter time series",
        post_processing=get_seasonal_time_updater(DJF_MONTHS[0], DJF_MONTHS[-1]),
        pre_processing=get_month_filter(DJF_MONTHS),
    )
    """ Resample to winter season, from December to February included."""

    MAM = _Freq(
        panda_freq="AS-MAR",
        accepted_values=["MAM"],
        description="spring time series",
        post_processing=get_seasonal_time_updater(MAM_MONTHS[0], MAM_MONTHS[-1]),
        pre_processing=get_month_filter(MAM_MONTHS),
    )
    """ Resample to spring season, from March to May included."""

    JJA = _Freq(
        panda_freq="AS-JUN",
        accepted_values=["JJA"],
        description="summer time series",
        post_processing=get_seasonal_time_updater(JJA_MONTHS[0], JJA_MONTHS[-1]),
        pre_processing=get_month_filter(JJA_MONTHS),
    )
    """ Resample to summer season, from June to Agust included."""

    SON = _Freq(
        panda_freq="AS-SEP",
        accepted_values=["SON"],
        description="autumn time series",
        post_processing=get_seasonal_time_updater(SON_MONTHS[0], SON_MONTHS[-1]),
        pre_processing=get_month_filter(SON_MONTHS),
    )
    """ Resample to fall season, from September to November included."""

    CUSTOM = _Freq(
        panda_freq="MS",
        accepted_values=[],
        description="",
        post_processing=lambda x: x,
        pre_processing=lambda x: x,
    )
    """ Placeholder instance for custom sampling frequencies.
        Do not use as is, use `slice_mode` with "month", "season" or "dates" keywords
        instead.
    """

    YEAR = _Freq(
        panda_freq="YS",
        accepted_values=["year", "YS"],
        description="annual time series",
        post_processing=_get_time_bounds_updater("YS"),
        pre_processing=lambda x: x,
    )
    """ Resample to yearly values."""

    def __init__(self, freq: _Freq):
        self._freq = freq

    @property
    def panda_freq(self):
        return self._freq.panda_freq

    @property
    def accepted_values(self):
        return self._freq.accepted_values

    @property
    def description(self):
        return self._freq.description

    @property
    def post_processing(self):
        return self._freq.post_processing

    @property
    def pre_processing(self):
        return self._freq.pre_processing

    @staticmethod
    def lookup(slice_mode: SliceMode) -> Frequency:
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

    @staticmethod
    def is_seasonal(slice_mode: SliceMode) -> bool:
        return Frequency.lookup(slice_mode) in [
            Frequency.CUSTOM,
            Frequency.ONDJFM,
            Frequency.AMJJAS,
            Frequency.MAM,
            Frequency.JJA,
            Frequency.SON,
            Frequency.DJF,
        ]


def _get_frequency_from_string(slice_mode: str) -> Frequency:
    for freq in Frequency:
        if freq.name == slice_mode.upper() or slice_mode.upper() in map(
            str.upper, freq.accepted_values
        ):
            return freq
    # TODO: we could add a compatibility to other pandas freq if we detect
    #       something like WS, 4MS, etc. In which case we would use FREQUENCY.CUSTOM
    raise InvalidIcclimArgumentError(f"Unknown frequency {slice_mode}.")


def _is_season_valid(months):
    is_valid = True
    for i in range(0, len(months) - 1):
        is_valid = is_valid and months[i] > 0 and months[i] < 13
        if months[i] > months[i + 1]:
            is_valid = is_valid and months[i + 1] == 1 and months[i] == 12
        else:
            is_valid = is_valid and (months[i + 1] - months[i] == 1)
    return is_valid


def _get_frequency_from_list(slice_mode_list: list) -> Frequency:
    if len(slice_mode_list) < 2:
        raise InvalidIcclimArgumentError(
            f"The given slice list {slice_mode_list}"
            f" has a length of {len(slice_mode_list)}."
            f" The maximum length here is 2."
        )
    sampling_freq = slice_mode_list[0]
    custom_freq = Frequency.CUSTOM
    if sampling_freq in ["month", "months"]:
        months = slice_mode_list[1]

        def month_list_post_processing(da):
            res, bounds = _get_time_bounds_updater("MS")(da)
            res = get_month_filter(months)(res)
            return res, bounds

        custom_freq._freq = _Freq(
            pre_processing=get_month_filter(months),
            post_processing=month_list_post_processing,
            panda_freq="MS",
            description=f"monthly time series (months: {months})",
            accepted_values=[],
        )
    elif sampling_freq == "season":
        months = slice_mode_list[1]
        if isinstance(months, Tuple):
            months = months[0] + months[1]  # concat in case of ([12], [1, 2])
        if not _is_season_valid(months):
            raise InvalidIcclimArgumentError(
                f"A season created using `slice_mode` must be made of consecutive"
                f" months. It was {months}."
            )
        custom_freq._freq = _Freq(
            pre_processing=get_month_filter(months),
            post_processing=get_seasonal_time_updater(months[0], months[-1]),
            panda_freq=f"AS-{MONTHS_MAP[months[0]]}",
            description=f"seasonal time series (season: {months})",
            accepted_values=[],
        )
    else:
        raise InvalidIcclimArgumentError(
            f"Unknown frequency {slice_mode_list}."
            " The sampling frequency must be one of {'season', 'month'}"
        )
    return custom_freq


SliceMode = Union[Frequency, str, List[Union[str, Tuple, int]]]

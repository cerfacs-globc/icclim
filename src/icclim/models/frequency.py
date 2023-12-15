"""
    `icclim.models.frequency` wraps the concept of pandas frequency in order to resample
    time series. `slice_mode` parameter of `icclim.index` is always converted to a
    `Frequency`.
"""
from __future__ import annotations

import dataclasses
import re
from datetime import timedelta
from typing import Any, Callable, Sequence

import cftime
import numpy as np
import pandas as pd
import xarray as xr
from pandas.tseries.frequencies import to_offset
from xarray.core.dataarray import DataArray

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_types import FrequencyLike, Indexer
from icclim.models.constants import (
    AMJJAS_MONTHS,
    DJF_MONTHS,
    EN_FREQ_MAPPING,
    FREQ_DELTA_MAPPING,
    JJA_MONTHS,
    MAM_MONTHS,
    MONTHS_MAP,
    ONDJFM_MONTHS,
    SON_MONTHS,
)
from icclim.models.registry import Registry
from icclim.utils import read_date

SEASON_ERR_MSG = (
    "A season created using `slice_mode` must be made of either"
    " consecutive integers for months such as [1,2,3] or two date strings"
    " such as ['19 july', '14 august']."
)

# RUN_INDEXER is a special value used for group by when there is no proper groupby to do
# but instead a filtering should be applied before the reducer.
RUN_INDEXER = "run_indexer"


def get_seasonal_time_updater(
    start_month: int, end_month: int, start_day: int = 1, end_day: int = None
) -> Callable[[DataArray], tuple[DataArray, DataArray]]:
    """Seasonal time updater and time bounds creator method generator.
    Returns a callable of DataArray which will rewrite the time dimension to
    the season composed of the given months. The data must have been computed on this
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
                    year, start_month, start_day, calendar=first_time.calendar
                )
                end = _get_end_date(
                    use_cftime=True,
                    year=year_of_season_end,
                    month=end_month,
                    day=end_day,
                    calendar=first_time.calendar,
                )
            else:
                start = pd.to_datetime(f"{year}-{start_month}-{start_day}")
                end = _get_end_date(
                    use_cftime=False,
                    year=year_of_season_end,
                    month=end_month,
                    day=end_day,
                )
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


def get_time_bounds_updater(
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
            ends = ends - timedelta(days=1)
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


@dataclasses.dataclass
class Frequency:
    """Time sampling frequency."""

    pandas_freq: str
    accepted_values: list[str]
    adjective: str
    post_processing: Callable[[DataArray], tuple[DataArray, DataArray]] | None
    units: str
    indexer: Indexer | None
    long_name: str
    group_by_key: str | None
    delta: timedelta | np.timedelta64

    def build_frequency_kwargs(self) -> dict[str, Any]:
        """Build kwargs with possible keys in {"freq", "month", "date_bounds"}"""
        kwargs = dict(freq=self.pandas_freq)
        if self.indexer is not None:
            kwargs.update(self.indexer)
        return kwargs


class FrequencyRegistry(Registry[Frequency]):
    _item_class = Frequency

    HOUR = Frequency(
        pandas_freq="H",
        accepted_values=["hour", "h", "hourly"],
        adjective="hourly",
        indexer=None,
        post_processing=get_time_bounds_updater("H"),
        units="hours",
        long_name="hour",
        group_by_key="time.hour",
        delta=np.timedelta64(1, "h"),
    )
    """Resample to hourly values"""

    DAY = Frequency(
        pandas_freq="D",
        accepted_values=["daily", "day", "days", "d"],
        adjective="daily",
        indexer=None,
        post_processing=get_time_bounds_updater("D"),
        units="days",
        long_name="day",
        group_by_key="time.dayofyear",
        delta=np.timedelta64(1, "D"),
    )
    """Resample to daily values"""

    MONTH = Frequency(
        pandas_freq="MS",
        accepted_values=["month", "monthly", "MS"],
        adjective="monthly",
        indexer=None,
        post_processing=get_time_bounds_updater("MS"),
        units="months",
        long_name="month",
        group_by_key="time.month",
        delta=np.timedelta64(1, "M"),
    )
    """Resample to monthly values"""

    YEAR = Frequency(
        pandas_freq="YS",
        accepted_values=["year", "yearly", "annual", "YS"],
        adjective="annual",
        indexer=None,
        post_processing=get_time_bounds_updater("YS"),
        units="years",
        long_name="year",
        group_by_key="time.year",
        delta=np.timedelta64(1, "Y"),
    )
    """Resample to yearly values."""

    AMJJAS = Frequency(
        pandas_freq="AS-APR",
        accepted_values=["AMJJAS"],
        adjective="AMJJAS summery",
        indexer=dict(month=AMJJAS_MONTHS),
        post_processing=get_seasonal_time_updater(AMJJAS_MONTHS[0], AMJJAS_MONTHS[-1]),
        units="half_year_summers",
        long_name="AMJJAS season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(6, "M"),
    )
    """Resample to summer half-year, from April to September included."""

    ONDJFM = Frequency(
        pandas_freq="AS-OCT",
        accepted_values=["ONDJFM"],
        adjective="ONDJFM wintry",
        indexer=dict(month=ONDJFM_MONTHS),
        post_processing=get_seasonal_time_updater(ONDJFM_MONTHS[0], ONDJFM_MONTHS[-1]),
        units="half_year_winters",
        long_name="ONDJFM season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(6, "M"),
    )
    """Resample to winter half-year, from October to March included."""

    DJF = Frequency(
        pandas_freq="AS-DEC",
        accepted_values=["DJF"],
        adjective="DJF wintry",
        indexer=dict(month=DJF_MONTHS),
        post_processing=get_seasonal_time_updater(DJF_MONTHS[0], DJF_MONTHS[-1]),
        units="winters",
        long_name="DJF winter",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to winter season, from December to February included."""

    MAM = Frequency(
        pandas_freq="AS-MAR",
        accepted_values=["MAM"],
        adjective="MAM springlong",
        indexer=dict(month=MAM_MONTHS),
        post_processing=get_seasonal_time_updater(MAM_MONTHS[0], MAM_MONTHS[-1]),
        units="springs",
        long_name="MAM season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to spring season, from March to May included."""

    JJA = Frequency(
        pandas_freq="AS-JUN",
        accepted_values=["JJA"],
        adjective="JJA summery",
        indexer=dict(month=JJA_MONTHS),
        post_processing=get_seasonal_time_updater(JJA_MONTHS[0], JJA_MONTHS[-1]),
        units="summers",
        long_name="JJA season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to summer season, from June to Agust included."""

    SON = Frequency(
        pandas_freq="AS-SEP",
        accepted_values=["SON"],
        adjective="SON autumnal",
        indexer=dict(month=SON_MONTHS),
        post_processing=get_seasonal_time_updater(SON_MONTHS[0], SON_MONTHS[-1]),
        units="autumns",
        long_name="SON season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to fall season, from September to November included."""

    @classmethod
    def lookup(cls, item: FrequencyLike, no_error: bool = False) -> Frequency | None:
        if isinstance(item, Frequency):
            return item
        if isinstance(item, str):
            return _get_frequency_from_string(item)
        if isinstance(item, (list, tuple)):
            return _get_frequency_from_iterable(item)
        if no_error:
            return None
        raise InvalidIcclimArgumentError(
            f"Unknown frequency {item}."
            f" Use a Frequency from {FrequencyRegistry.every_aliases()}"
        )

    @staticmethod
    def get_item_aliases(item: Frequency) -> list[str]:
        return item.accepted_values


def _get_end_date(
    use_cftime: bool, year: int, month: int, day: int = None, calendar=None
):
    delta = timedelta(days=0)
    if day is None:
        if month == 12:
            day = 31
        else:
            # get the next month and subtract a day (handle any month and leap years)
            month = month + 1
            day = 1
            delta = timedelta(days=1)
    if use_cftime:
        end = cftime.datetime(year, month, day, calendar=calendar)
    else:
        end = pd.to_datetime(f"{year}-{month}-{day}")
    return end - delta


def _get_frequency_from_string(query: str) -> Frequency:
    for key, freq in FrequencyRegistry.catalog().items():
        if key == query.upper() or query.upper() in map(
            str.upper, freq.accepted_values
        ):
            return freq
    # else assumes it's a pandas frequency (such as "W" or "3MS")
    try:
        to_offset(query)  # no-op, used to check if it's a valid pandas freq
    except ValueError as e:
        raise InvalidIcclimArgumentError(
            f"Unknown frequency {query}. Use either a"
            " valid icclim frequency or a valid pandas"
            " frequency",
            e,
        )
    return Frequency(
        post_processing=get_time_bounds_updater(query),
        pandas_freq=query,
        adjective=f"time series sampled on {query}",
        accepted_values=[],
        indexer=None,
        units=query,
        long_name=_get_long_name(query),
        group_by_key=None,
        delta=_get_delta(query),
    )


def _is_season_valid(months: list[int]) -> bool:
    is_valid = True
    for i in range(0, len(months) - 1):
        is_valid = is_valid and 0 < months[i] < 13
        if months[i] > months[i + 1]:
            is_valid = is_valid and months[i + 1] == 1 and months[i] == 12
        else:
            is_valid = is_valid and (months[i + 1] - months[i] == 1)
    return is_valid


def _get_frequency_from_iterable(
    slice_mode_list: list | tuple[str, Sequence]
) -> Frequency:
    if len(slice_mode_list) < 2:
        raise InvalidIcclimArgumentError(
            "Invalid slice_mode format."
            " When slice_mode is a list, its first element must be a keyword and"
            " its second a list (e.g `slice_mode=['season', [1,2,3]]` )."
        )
    freq_keyword = slice_mode_list[0]
    if freq_keyword in ["month", "months"]:
        return _build_frequency_filtered_by_month(slice_mode_list[1])
    elif freq_keyword in ["season", "seasons"]:
        season = slice_mode_list[1]
        return _build_seasonal_freq(season)
    else:
        raise InvalidIcclimArgumentError(
            f"Unknown frequency {slice_mode_list}."
            " The sampling frequency must be one of {'season', 'month'}"
        )


def _build_frequency_filtered_by_month(months: Sequence[int]) -> Frequency:
    return Frequency(
        indexer=dict(month=months),
        post_processing=get_time_bounds_updater("MS"),
        pandas_freq="MS",
        adjective="monthly",
        accepted_values=[],
        units="months",
        long_name=f"monthly time series (months: {months})",
        group_by_key="time.month",
        delta=np.timedelta64(1, "M"),
    )


def _build_seasonal_freq(season: Sequence):
    if isinstance(season[0], str):
        return _build_seasonal_frequency_between_dates(season)
    elif isinstance(season, tuple) or isinstance(season[0], int):
        return _build_seasonal_frequency_for_months(season)
    else:
        raise NotImplementedError()


def _build_seasonal_frequency_between_dates(season: Sequence[str]) -> Frequency:
    if len(season) != 2:
        raise InvalidIcclimArgumentError(SEASON_ERR_MSG)
    begin_date = read_date(season[0])
    end_date = read_date(season[1])
    begin_formatted = begin_date.strftime("%m-%d")
    end_formatted = end_date.strftime("%m-%d")
    indexer = dict(date_bounds=(begin_formatted, end_formatted))
    return Frequency(
        indexer=indexer,
        post_processing=get_seasonal_time_updater(
            begin_date.month, end_date.month, begin_date.day, end_date.day
        ),
        pandas_freq=f"AS-{MONTHS_MAP[begin_date.month]}",
        adjective="seasonally",
        accepted_values=[],
        units=f"{MONTHS_MAP[begin_date.month]}_{MONTHS_MAP[end_date.month]}_seasons",
        long_name=f"seasonal time series"
        f" (season: from {begin_formatted} to {end_formatted})",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(end_date - begin_date),
    )


def _build_seasonal_frequency_for_months(season: tuple | list):
    if isinstance(season, tuple):
        # concat in case of ([12], [1, 2])
        season = season[0] + season[1]
    if not _is_season_valid(season):
        raise InvalidIcclimArgumentError(SEASON_ERR_MSG)
    indexer = dict(month=season)
    return Frequency(
        indexer=indexer,
        post_processing=get_seasonal_time_updater(season[0], season[-1]),
        pandas_freq=f"AS-{MONTHS_MAP[season[0]]}",
        adjective="seasonally",
        accepted_values=[],
        units=f"{MONTHS_MAP[season[0]]}_{MONTHS_MAP[season[-1]]}_seasons",
        long_name=f"seasonal time series (season: {season})",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(len(season), "M"),
    )


def _get_long_name(pandas_freq: str) -> str:
    no_digit_freq = re.findall(r"\D+", pandas_freq)[0]
    multiplier = re.findall(r"\d+", pandas_freq)
    freqs = no_digit_freq.split("-")[::-1]  # reverse
    freqs = [EN_FREQ_MAPPING[f] for f in freqs]
    freqs = " ".join(freqs)
    if multiplier:
        return f"{multiplier[0]} {freqs}"
    else:
        return freqs


def _get_delta(pandas_freq: str) -> np.timedelta64:
    """
    Build timedelta from a "pandas frequency" string.
    A "pandas frequency" string may look like ["2AS-DEC", "3W-TUE", "M", ... ]
    The anchor, such as "DEC" in "AS-DEC", does not modify the delta.

    Parameters
    ----------
    pandas_freq : str
    The frequency query.

    Returns
    -------
    The timedelta corresponding to this frequency.
    For example, "2AS-DEC" would return a 2 years delta.
    """
    # [0] to ignore the anchor
    non_digit = re.findall(r"\D+", pandas_freq)[0].split("-")[0]
    base, freq = FREQ_DELTA_MAPPING[non_digit]
    # we assume the starting digits are the multiplier.
    multiplier = re.findall(r"\d+", pandas_freq)
    if multiplier:
        multiplier = int(multiplier[0])
        return np.timedelta64(base * multiplier, freq)
    else:
        return np.timedelta64(base, freq)

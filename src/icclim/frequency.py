"""
Contain the Frequency class and the FrequencyRegistry class.

Frequency wraps the concept of pandas frequency in order to resample
time series. ``slice_mode`` parameter of `icclim.index` is always converted to a
`Frequency`.
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import cftime
import numpy as np
import pandas as pd
import xarray as xr
from pandas.tseries.frequencies import to_offset
from xarray.core.dataarray import DataArray

from icclim._core.constants import (
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
from icclim._core.model.registry import Registry
from icclim._core.utils import read_date
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from icclim._core.model.icclim_types import FrequencyLike, Indexer

SEASON_ERR_MSG = (
    "A season created using `slice_mode` must be made of either"
    " consecutive integers for months such as [1,2,3] or two date strings"
    " such as ['19 july', '14 august']."
)

# RUN_INDEXER is a special value used for group by when there is no proper groupby to do
# but instead a filtering should be applied before the reducer.
RUN_INDEXER = "run_indexer"


def get_seasonal_time_updater(
    start_month: int,
    end_month: int,
    start_day: int = 1,
    end_day: int | None = None,
) -> Callable[[DataArray], tuple[DataArray, DataArray]]:
    """
    Seasonal time updater and time bounds creator method generator.

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
    start_day: int
        The season starting day, it must be between 1 and 31.
    end_day: int
        The season ending day, it must be between 1 and 31.

    Returns
    -------
    function: Callable[[DataArray], tuple[DataArray, DataArray]]
        A function that will update the time dimension of a DataArray to the season
        composed of the given months and create the corresponding time_bounds.
    """

    def add_time_bounds(da: DataArray) -> tuple[DataArray, DataArray]:
        da_years = np.unique(da.time.dt.year)
        time_bounds = []
        new_time_axis = []
        first_time = da.time.values[0]
        for year in da_years:
            year_of_season_end = year + 1 if start_month > end_month else year
            if isinstance(first_time, cftime.datetime):
                start = cftime.datetime(
                    year,
                    start_month,
                    start_day,
                    calendar=first_time.calendar,
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
    """
    Return a function that adds time bounds to a given DataArray.

    Parameters
    ----------
    freq : str
        The frequency at which the DataArray should be resampled.

    Returns
    -------
    Callable[[DataArray], tuple[DataArray, DataArray]]
        A function that takes a DataArray as input and returns a tuple
        containing the modified DataArray and the time
        bounds as a separate DataArray.

    Notes
    -----
    The returned function assumes that the input DataArray has already
    been resampled to the specified frequency.

    The time axis values in the modified DataArray will be set to the
    middle of the calculated time bounds.
    """

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
                ],
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
            data=list(zip(starts, ends, strict=False)),
            dims=["time", "bounds"],
            coords=[("time", da.time.values), ("bounds", [0, 1])],
        )
        return da, time_bounds_da

    return add_time_bounds


@dataclasses.dataclass
class Frequency:
    """
    Time sampling frequency.

    This acts as a wrapper around the pandas frequency string.
    ``icclim.index`` will always convert the ``slice_mode`` parameter to a
    ``Frequency``.

    Parameters
    ----------
    pandas_freq : str
        The frequency string used by pandas to resample the time series.
    accepted_values : list[str]
        The list of aliases for the frequency.
    adjective : str
        The adjective form of the frequency. Used when templating the output's metadata.
    post_processing : Callable[[DataArray], tuple[DataArray, DataArray]] | None
        The function to apply for post-processing the resampled data.
    units : str
        The units of the frequency.
    indexer : Indexer | None
        The indexer to use for grouping the data.
    long_name : str
        The long name of the frequency.
    group_by_key : str | None
        The key to use for grouping the data.
    delta : np.timedelta64
        The time delta for the frequency.

    Returns
    -------
    Frequency
        The frequency object.

    Notes
    -----
    This class represents a time sampling frequency.

    Examples
    --------
    >>> freq = Frequency(
    ...     pandas_freq="D",
    ...     accepted_values=["daily", "day", "days", "d"],
    ...     adjective="daily",
    ...     indexer=None,
    ...     post_processing=get_time_bounds_updater("D"),
    ...     units="days",
    ...     long_name="day",
    ...     group_by_key="time.dayofyear",
    ...     delta=np.timedelta64(1, "D"),
    ... )
    """

    pandas_freq: str
    accepted_values: list[str]
    adjective: str
    post_processing: Callable[[DataArray], tuple[DataArray, DataArray]] | None
    units: str
    indexer: Indexer | None
    long_name: str
    group_by_key: str | None
    delta: np.timedelta64

    def build_frequency_kwargs(self) -> dict[str, Any]:
        """Build kwargs with possible keys in {"freq", "month", "date_bounds"}."""
        kwargs = {"freq": self.pandas_freq}
        if self.indexer is not None:
            kwargs.update(self.indexer)
        return kwargs


_NO_RESAMPLE_FREQUENCY = object()


class FrequencyRegistry(Registry[Frequency]):
    """Registry class for Frequency objects."""

    _item_class = Frequency

    NO_RESAMPLE = _NO_RESAMPLE_FREQUENCY
    """Does not resample"""

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
        pandas_freq="YS-APR",
        accepted_values=["AMJJAS"],
        adjective="AMJJAS summery",
        indexer={"month": AMJJAS_MONTHS},
        post_processing=get_seasonal_time_updater(AMJJAS_MONTHS[0], AMJJAS_MONTHS[-1]),
        units="half_year_summers",
        long_name="AMJJAS season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(6, "M"),
    )
    """Resample to summer half-year, from April to September included."""

    ONDJFM = Frequency(
        pandas_freq="YS-OCT",
        accepted_values=["ONDJFM"],
        adjective="ONDJFM wintry",
        indexer={"month": ONDJFM_MONTHS},
        post_processing=get_seasonal_time_updater(ONDJFM_MONTHS[0], ONDJFM_MONTHS[-1]),
        units="half_year_winters",
        long_name="ONDJFM season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(6, "M"),
    )
    """Resample to winter half-year, from October to March included."""

    DJF = Frequency(
        pandas_freq="YS-DEC",
        accepted_values=["DJF"],
        adjective="DJF wintry",
        indexer={"month": DJF_MONTHS},
        post_processing=get_seasonal_time_updater(DJF_MONTHS[0], DJF_MONTHS[-1]),
        units="winters",
        long_name="DJF winter",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to winter season, from December to February included."""

    MAM = Frequency(
        pandas_freq="YS-MAR",
        accepted_values=["MAM"],
        adjective="MAM springlong",
        indexer={"month": MAM_MONTHS},
        post_processing=get_seasonal_time_updater(MAM_MONTHS[0], MAM_MONTHS[-1]),
        units="springs",
        long_name="MAM season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to spring season, from March to May included."""

    JJA = Frequency(
        pandas_freq="YS-JUN",
        accepted_values=["JJA"],
        adjective="JJA summery",
        indexer={"month": JJA_MONTHS},
        post_processing=get_seasonal_time_updater(JJA_MONTHS[0], JJA_MONTHS[-1]),
        units="summers",
        long_name="JJA season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to summer season, from June to Agust included."""

    SON = Frequency(
        pandas_freq="YS-SEP",
        accepted_values=["SON"],
        adjective="SON autumnal",
        indexer={"month": SON_MONTHS},
        post_processing=get_seasonal_time_updater(SON_MONTHS[0], SON_MONTHS[-1]),
        units="autumns",
        long_name="SON season",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(3, "M"),
    )
    """Resample to fall season, from September to November included."""

    @classmethod
    def lookup(cls, query: FrequencyLike | Frequency) -> Frequency:
        """
        Look up a Frequency object based on the query.

        Parameters
        ----------
        query : FrequencyLike or Frequency
            The query to look up the Frequency object. Typically a string.

        Returns
        -------
        Frequency
            The Frequency object that matches the query.

        Raises
        ------
        InvalidIcclimArgumentError
            If the query is not a valid frequency.

        Notes
        -----
        The query can be a Frequency object, a string representing a frequency,
        or a list/tuple representing a frequency.

        If the query is a string, it will be converted to a Frequency object first by
        looking in the FrequencyRegistry then by assuming it's a pandas frequency and
        building a Frequency object from it.

        If the query is a list/tuple, it needs a keyword as its first element and a list
        of months or a list of two date strings as its second element. The keyword can
        be either "month" or "season".
        In "month" case, the second element must be a list of months and the Frequency
        will filter the data by these months.
        In "season" case, the second element must be a list of months or a list of two
        date and the Frequency will resample the data to the season composed of these
        months.
        """
        if isinstance(query, Frequency):
            return query
        if isinstance(query, str):
            return _get_frequency_from_string(query)
        if isinstance(query, (list, tuple)):
            return _get_frequency_from_iterable(query)
        msg = (
            f"Unknown frequency {query}."
            f" Use a Frequency from {FrequencyRegistry.every_aliases()}"
        )
        raise InvalidIcclimArgumentError(msg)

    @staticmethod
    def get_item_aliases(item: Frequency) -> list[str]:
        """
        Get the aliases of a Frequency object.

        Parameters
        ----------
        item : Frequency
            The Frequency object.

        Returns
        -------
        list[str]
            The aliases of the Frequency object.
        """
        return item.accepted_values


def _get_end_date(
    use_cftime: bool,
    year: int,
    month: int,
    day: int | None = None,
    calendar: str | None = None,
) -> cftime.datetime | pd.Timestamp:
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
            str.upper,
            freq.accepted_values,
        ):
            return freq
    # else assumes it's a pandas frequency (such as "W" or "3MS")
    try:
        to_offset(query)  # no-op, used to check if it's a valid pandas freq
    except ValueError as exc:
        msg = (
            f"Unknown frequency {query}. Use either a"
            " valid icclim frequency or a valid pandas"
            " frequency"
        )
        raise InvalidIcclimArgumentError(msg, exc) from exc
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
    for i in range(len(months) - 1):
        is_valid = is_valid and 0 < months[i] < 13
        if months[i] > months[i + 1]:
            is_valid = is_valid and months[i + 1] == 1 and months[i] == 12
        else:
            is_valid = is_valid and (months[i + 1] - months[i] == 1)
    return is_valid


def _get_frequency_from_iterable(
    slice_mode_list: list | tuple[str, Sequence],
) -> Frequency:
    if len(slice_mode_list) < 2:
        msg = (
            "Invalid slice_mode format."
            " When slice_mode is a list, its first element must be a keyword and"
            " its second a list (e.g `slice_mode=['season', [1,2,3]]` )."
        )
        raise InvalidIcclimArgumentError(msg)
    freq_keyword = slice_mode_list[0]
    if freq_keyword in ["month", "months"]:
        return _build_frequency_filtered_by_month(slice_mode_list[1])
    if freq_keyword in ["season", "seasons"]:
        season = slice_mode_list[1]
        return _build_seasonal_freq(season)
    msg = (
        f"Unknown frequency {slice_mode_list}."
        " The sampling frequency must be one of {'season', 'month'}"
    )
    raise InvalidIcclimArgumentError(msg)


def _build_frequency_filtered_by_month(months: Sequence[int]) -> Frequency:
    return Frequency(
        indexer={"month": months},
        post_processing=get_time_bounds_updater("MS"),
        pandas_freq="MS",
        adjective="monthly",
        accepted_values=[],
        units="months",
        long_name=f"monthly time series (months: {months})",
        group_by_key="time.month",
        delta=np.timedelta64(1, "M"),
    )


def _build_seasonal_freq(season: Sequence) -> Frequency:
    if isinstance(season[0], str):
        return _build_seasonal_frequency_between_dates(season)
    if isinstance(season, tuple) or isinstance(season[0], int):
        return _build_seasonal_frequency_for_months(season)
    raise NotImplementedError


def _build_seasonal_frequency_between_dates(season: Sequence[str]) -> Frequency:
    if len(season) != 2:
        raise InvalidIcclimArgumentError(SEASON_ERR_MSG)
    begin_date = read_date(season[0])
    end_date = read_date(season[1])
    begin_formatted = begin_date.strftime("%m-%d")
    end_formatted = end_date.strftime("%m-%d")
    indexer = {"date_bounds": (begin_formatted, end_formatted)}
    return Frequency(
        indexer=indexer,
        post_processing=get_seasonal_time_updater(
            begin_date.month,
            end_date.month,
            begin_date.day,
            end_date.day,
        ),
        pandas_freq=f"YS-{MONTHS_MAP[begin_date.month]}",
        adjective="seasonally",
        accepted_values=[],
        units=f"{MONTHS_MAP[begin_date.month]}_{MONTHS_MAP[end_date.month]}_seasons",
        long_name=f"seasonal time series"
        f" (season: from {begin_formatted} to {end_formatted})",
        group_by_key=RUN_INDEXER,
        delta=np.timedelta64(end_date - begin_date),
    )


def _build_seasonal_frequency_for_months(season: tuple | list) -> Frequency:
    if isinstance(season, tuple):
        # concat in case of ([12], [1, 2])
        season = season[0] + season[1]
    if not _is_season_valid(season):
        raise InvalidIcclimArgumentError(SEASON_ERR_MSG)
    indexer = {"month": season}
    return Frequency(
        indexer=indexer,
        post_processing=get_seasonal_time_updater(season[0], season[-1]),
        pandas_freq=f"YS-{MONTHS_MAP[season[0]]}",
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
    return freqs


def _get_delta(pandas_freq: str) -> np.timedelta64:
    """
    Build timedelta from a "pandas frequency" string.

    A "pandas frequency" string may look like ["2YS-DEC", "3W-TUE", "M", ... ]
    The anchor, such as "DEC" in "YS-DEC", does not modify the delta.

    Parameters
    ----------
    pandas_freq : str
    The frequency query.

    Returns
    -------
    The timedelta corresponding to this frequency.
    For example, "2YS-DEC" would return a 2 years delta.
    """
    # [0] to ignore the anchor
    non_digit = re.findall(r"\D+", pandas_freq)[0].split("-")[0]
    base, freq = FREQ_DELTA_MAPPING[non_digit]
    # we assume the starting digits are the multiplier.
    multiplier = re.findall(r"\d+", pandas_freq)
    if multiplier:
        multiplier = int(multiplier[0])
        return np.timedelta64(base * multiplier, freq)
    return np.timedelta64(base, freq)

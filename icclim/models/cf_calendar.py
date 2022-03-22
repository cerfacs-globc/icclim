from __future__ import annotations

from enum import Enum
from typing import Callable

import numpy as np
import xarray as xr
from xarray import DataArray


def _proleptic_gregorian_leap(years: DataArray) -> DataArray:
    return np.logical_or(
        years % 400 == 0, np.logical_and(years % 100 != 0, years % 4 == 0)
    )


def _julian_leap(years: DataArray) -> DataArray:
    return years % 4 == 0


def _standard_leap(years: DataArray) -> DataArray:
    res = xr.full_like(years, False)
    res[years < 1582] = _julian_leap(years[years < 1582])
    res[years >= 1582] = _proleptic_gregorian_leap(years[years >= 1582])
    return res


class CfCalendar(Enum):
    """
    CF defined calendars with some additional aliases names for convenience.
    The first value of the aliases is the calendar "main" name.

    aliases: List[str]
        All the possible aliases or poorly typed calendar names targeting the same
        calendar.
    is_leap: Callable
        It expects a DataArray argument of years such as `da.time.dt.year`.
        Returns a mask of the input telling if the value is part of a leap year or not.

    """

    NO_LEAP = (
        ["noleap", "no_leap", "days_365", "days365", "365_day", "365day"],
        lambda da: np.full_like(da.shape, False, dtype=bool),
    )
    DAYS_360 = (
        ["360_day", "days_360", "360day", "days360"],
        lambda da: np.full_like(da.shape, False, dtype=bool),
    )
    ALL_LEAP = (
        ["all_leap", "allleap", "days_366", "days366", "366_day", "366day"],
        lambda da: np.full_like(da.shape, True, dtype=bool),
    )
    PROLEPTIC_GREGORIAN = (
        ["proleptic_gregorian", "prolepticgregorian"],
        lambda da: _proleptic_gregorian_leap(da).values,
    )
    JULIAN = (["julian"], lambda da: _julian_leap(da).values)
    STANDARD = (["standard", "gregorian"], lambda da: _standard_leap(da).values)
    # Not sure what to do with none calendar
    NONE = (["none"], lambda da: _standard_leap(da).values)

    def __init__(self, aliases: list[str], is_leap: Callable[[DataArray], np.ndarray]):
        self.aliases = aliases
        self.is_leap = is_leap

    def get_name(self) -> str:
        return self.aliases[0]

    @staticmethod
    def lookup(query: str) -> CfCalendar:
        res = list(filter(lambda x: query.lower() in x.aliases, CfCalendar))
        if len(res) == 0:
            raise TypeError(f"No calendars found for query '{query}'")
        return res[0]

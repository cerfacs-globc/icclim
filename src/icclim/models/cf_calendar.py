from __future__ import annotations

import dataclasses
from typing import Callable

import numpy as np
import xarray as xr
from xarray import DataArray

from icclim.models.registry import Registry


@dataclasses.dataclass
class CfCalendar:
    aliases: list[str]
    is_leap: Callable[[DataArray], np.ndarray]

    @property
    def name(self) -> str:
        return self.aliases[0]


# todo: the whole class might be useless with the latest cftime
#      (we don't need our own CfCalendar if we can do `da.time.dt.is_leap_year`)
class CfCalendarRegistry(Registry[CfCalendar]):
    """
    Calendars known in CF plus some additional custom aliases for convenience.
    The first value of the aliases is the calendar "main" name.

    aliases: List[str]
        All the possible aliases or poorly typed calendar names targeting the same
        calendar.
    is_leap: Callable
        It expects a DataArray argument of years such as `da.time.dt.year`.
        Returns a mask of the input telling if the value is part of a leap year or not.

    """

    _item_class = CfCalendar

    NO_LEAP = CfCalendar(
        ["noleap", "no_leap", "days_365", "days365", "365_day", "365day"],
        lambda da: np.full_like(da.shape, False, dtype=bool),
    )
    DAYS_360 = CfCalendar(
        ["360_day", "days_360", "360day", "days360"],
        lambda da: np.full_like(da.shape, False, dtype=bool),
    )
    ALL_LEAP = CfCalendar(
        ["all_leap", "allleap", "days_366", "days366", "366_day", "366day"],
        lambda da: np.full_like(da.shape, True, dtype=bool),
    )
    PROLEPTIC_GREGORIAN = CfCalendar(
        ["proleptic_gregorian", "prolepticgregorian"],
        lambda da: _proleptic_gregorian_leap(da).values,
    )
    JULIAN = CfCalendar(["julian"], lambda da: _julian_leap(da).values)
    STANDARD = CfCalendar(
        ["standard", "gregorian"], lambda da: _standard_leap(da).values
    )
    # Not sure what to do with none calendar
    NONE = CfCalendar(["none"], lambda da: _standard_leap(da).values)

    @staticmethod
    def get_item_aliases(item: CfCalendar) -> list[str]:
        return list(map(str.upper, item.aliases))


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

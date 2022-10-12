from __future__ import annotations

from datetime import datetime
from typing import TypeVar

import dateparser
import xclim
from xarray import DataArray
from xclim.core.units import str2pint
from xclim.core.units import units as xc_units

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import UNITS_KEY


def read_date(in_date: str | datetime) -> datetime:
    if isinstance(in_date, datetime):
        return in_date
    date = dateparser.parse(in_date)
    if date is None:
        raise InvalidIcclimArgumentError(
            f"The date {in_date} does not have a valid format."
            " You can use various formats such as '2 december', '02-12',"
            " '1994-12-02'..."
        )
    return date


def get_date_to_iso_format(in_date: str | datetime) -> str:
    if isinstance(in_date, str):
        in_date = read_date(in_date)
    return in_date.strftime("%Y-%m-%d")


def is_number_sequence(values) -> bool:
    return isinstance(values, (tuple, list)) and all(
        map(lambda x: isinstance(x, (float, int)), values)
    )


_T = TypeVar("_T")
_X = TypeVar("_X")


def icc_convert_units_to(
    source: _T,
    target: _X,
    context: str | None = None,
) -> _T:
    """Overload xclim'sicc_convert_units_to to handle 'mm'->'kg/day/m2'"""
    src_unit = get_unit(source)
    target_unit = get_unit(target)
    if is_mm(src_unit) and has_standard_precip_unit(target_unit):
        return override_unit(source, target_unit)
    if is_mm(target_unit) and has_standard_precip_unit(src_unit):
        return source
    return xclim.units.convert_units_to(source, target, context)


def get_unit(
    query: str | DataArray | xc_units.Quantity | xc_units.Unit,
) -> xc_units.Unit:
    if isinstance(query, str):
        return str2pint(query).units
    elif isinstance(query, DataArray):
        return str2pint(query.attrs[UNITS_KEY]).units
    elif isinstance(query, xc_units.Quantity):
        return query.units
    elif isinstance(query, xc_units.Unit):
        return query
    else:
        return None


def is_mm(query: xc_units.Unit) -> bool:
    return query == xc_units.Unit("mm")


def has_standard_precip_unit(query: xc_units.Unit) -> bool:
    return xc_units.Quantity(1, query).check("[mass]/[time]/[length]**2")


def override_unit(
    query: str | DataArray | xc_units.Quantity | xc_units.Unit,
    overriding_unit: xc_units.Unit,
) -> str | DataArray | xc_units.Quantity | xc_units.Unit:
    """
    Override the unit of `query` by `overriding_unit`.
    No conversion is attempted.
    """
    if isinstance(query, str):
        return f"{str2pint(query).m} {overriding_unit}"
    elif isinstance(query, DataArray):
        query.attrs[UNITS_KEY] = str(overriding_unit)
        return query
    elif isinstance(query, xc_units.Quantity):
        return xc_units.Quantity(query.m, overriding_unit)
    elif isinstance(query, xc_units.Unit):
        return overriding_unit
    else:
        raise NotImplementedError(f"Can't get unit from a {type(query)}")

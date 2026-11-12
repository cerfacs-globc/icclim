"""Contain utility functions for icclim."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import dateparser  # type: ignore[import-untyped]

from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    from xarray import DataArray

# Number of decimals kept for a converted temperature (see `snap_converted_temperature`).
TEMPERATURE_SNAP_DECIMALS = 10


def read_date(in_date: str | datetime) -> datetime:
    """
    Read a date from a string or return the date if it is already a datetime object.

    Parameters
    ----------
    in_date: str | datetime
        A string representing a date or a datetime object.

    Returns
    -------
    datetime
        A datetime object.
    """
    if isinstance(in_date, datetime):
        return in_date
    date = dateparser.parse(in_date)
    if date is None:
        msg = (
            f"The date {in_date} does not have a valid format."
            " You can use various formats such as '2 december', '02-12',"
            " '1994-12-02'..."
        )
        raise InvalidIcclimArgumentError(msg)
    return date


def is_number_sequence(values: object) -> bool:
    """Return True if values is a sequence of numbers."""
    return isinstance(values, (tuple, list)) and all(
        (isinstance(x, (float, int)) for x in values),
    )


def snap_converted_temperature(converted: DataArray) -> DataArray:
    """
    Remove the floating-point noise left by a conversion of a temperature.

    pint converts 77 degF to 25.000000000000057 degC and 25 degC to
    76.99999999999993 degF, so a value equal to a threshold in another unit was
    counted as above it (or not as below it). The temperatures compared with a threshold
    that is not computed from them, and the converted thresholds, are rounded to
    ``TEMPERATURE_SNAP_DECIMALS`` decimals, far below the precision of any temperature.
    Anything that is not a floating-point temperature is returned as it is: the
    rounding is absolute and would destroy a small quantity such as a precipitation
    flux.

    Parameters
    ----------
    converted : DataArray
        The result of ``xclim.core.units.convert_units_to``, with its units.

    Returns
    -------
    DataArray
        The same data, rounded when it is a floating-point temperature.
    """
    from xclim.core.units import units2pint  # noqa: PLC0415

    unit = converted.attrs.get("units")
    if unit is None or converted.dtype.kind != "f":
        return converted
    try:
        is_temperature = "[temperature]" in units2pint(unit).dimensionality
    except (KeyError, TypeError, ValueError):
        return converted
    if not is_temperature:
        return converted
    snapped = converted.round(TEMPERATURE_SNAP_DECIMALS)
    snapped.attrs = converted.attrs
    return snapped

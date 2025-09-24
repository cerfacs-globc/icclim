"""Contain utility functions for icclim."""

from __future__ import annotations

from datetime import datetime

import dateparser

from icclim.exception import InvalidIcclimArgumentError


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

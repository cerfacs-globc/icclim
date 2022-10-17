from __future__ import annotations

from datetime import datetime

import dateparser

from icclim.icclim_exceptions import InvalidIcclimArgumentError


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

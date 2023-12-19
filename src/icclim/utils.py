from __future__ import annotations

import re
import warnings
from datetime import datetime
from typing import TYPE_CHECKING

import dateparser
import xclim

from icclim.icclim_exceptions import InvalidIcclimArgumentError

if TYPE_CHECKING:
    import pint
    import xarray as xr

PR_AMOUNT_STANDARD_NAME = "thickness_of_rainfall_amount"


def read_date(in_date: str | datetime) -> datetime:
    if isinstance(in_date, datetime):
        return in_date
    date = dateparser.parse(in_date)
    if date is None:
        msg = (
            f"The date {in_date} does not have a valid format."
            " You can use various formats such as '2 december', '02-12',"
            " '1994-12-02'..."
        )
        raise InvalidIcclimArgumentError(
            msg,
        )
    return date


def get_date_to_iso_format(in_date: str | datetime) -> str:
    if isinstance(in_date, str):
        if re.match(r"^\d{4}$", in_date):
            warnings.warn(
                f"{in_date} is transformed into {in_date}-01-01",
                stacklevel=2,
            )
            in_date += "-01-01"
        if re.match(r"^\d{4}-\d{2}$", in_date):
            warnings.warn(f"{in_date} is transformed into {in_date}-01", stacklevel=2)
            in_date += "-01"
        in_date = read_date(in_date)
    return in_date.strftime("%Y-%m-%d")


def is_number_sequence(values) -> bool:
    return isinstance(values, (tuple, list)) and all(
        (isinstance(x, (float, int)) for x in values),
    )


def _is_rate(u: pint.Unit) -> bool:
    return u.dimensionality.get("[time]") == -1


def _is_amount(u: pint.Unit) -> bool:
    return not _is_rate(u)


def is_precipitation_amount(source: xr.DataArray) -> bool:
    standard_name = source.attrs.get("standard_name", None)
    source_unit = xclim.core.units.units2pint(source)
    return standard_name == PR_AMOUNT_STANDARD_NAME and _is_amount(source_unit)

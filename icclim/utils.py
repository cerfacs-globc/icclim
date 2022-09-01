from __future__ import annotations

from datetime import datetime

import dateparser
import xarray
from xarray import Dataset

from icclim.icclim_exceptions import InvalidIcclimArgumentError


def _da_chunksizes(da: xarray.Variable) -> dict:
    # FIXME To remove once minimal xarray version is v0.20.0 (use .chunksizes instead)
    # Copied and adapted from xarray
    if hasattr(da.data, "chunks"):
        return {dim: c for dim, c in zip(da.dims, da.data.chunks)}
    else:
        return {}


def get_chunksizes(ds: Dataset) -> dict:
    # FIXME To remove once minimal xarray version is v0.20.0 (use .chunksizes instead)
    # Copied and adapted from xarray
    chunks: dict[str, int] = {}
    for v in ds.variables.values():
        if hasattr(v.data, "chunks"):
            for dim, c in _da_chunksizes(v).items():
                if dim in chunks and c != chunks[dim]:
                    raise ValueError(
                        f"Object has inconsistent chunks along dimension {dim}."
                        " This can be fixed by calling unify_chunks()."
                    )
                chunks[dim] = c
    return chunks


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

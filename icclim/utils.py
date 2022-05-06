from __future__ import annotations

from datetime import datetime

import dateparser
from xarray import DataArray, Dataset

from icclim.icclim_exceptions import InvalidIcclimArgumentError


def _da_chunksizes(da: DataArray) -> dict:
    # FIXME To remove once minimal xarray version is v0.20.0 (use .chunksizes instead)
    # Copied and adapted from xarray
    if hasattr(da.data, "chunks"):
        return {dim: c for dim, c in zip(da.dims, da.data.chunks)}
    else:
        return {}


def _get_chunksizes(ds: Dataset) -> dict:
    # FIXME To remove once minimal xarray version is v0.20.0 (use .chunksizes instead)
    # Copied and adapted from xarray
    chunks = {}
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


def read_date(date_string: str) -> datetime:
    error_msg = (
        "The date {} does not have a valid format."
        " You can use various formats such as '2 december' or '02-12'."
    )
    if (date := dateparser.parse(date_string)) is None:
        raise InvalidIcclimArgumentError(error_msg.format(date_string))
    return date


def get_date_to_iso_format(in_date: str | datetime) -> str:
    if isinstance(in_date, str):
        in_date = read_date(in_date)
    return in_date.strftime("%Y-%m-%d")

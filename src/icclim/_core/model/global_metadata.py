"""Global metadata model to be added to the output netCDF file."""

from __future__ import annotations

from typing import TypedDict


class GlobalMetadata(TypedDict):
    """Global metadata model.

    Attributes
    ----------
    history : str or None
        The CF history attribute.
    source : str or None
        The source of the data.
    time_encoding : dict or None
        The time encoding information to be read from ds.time.encoding.
    """

    history: str | None
    source: str | None
    time_encoding: dict | None

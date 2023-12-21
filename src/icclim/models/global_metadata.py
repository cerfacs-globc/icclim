from __future__ import annotations

from typing import TypedDict


class GlobalMetadata(TypedDict):
    history: str | None
    source: str | None
    time_encoding: dict | None  # to be read from ds.time.encoding

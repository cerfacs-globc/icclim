from __future__ import annotations

from collections.abc import Callable

"""Python library for climate indices calculation."""

from icclim import dcsc, ecad, generic
from icclim._generated._ecad import *  # noqa: F403
from icclim._generated._generic import *  # noqa: F403

__all__ = [
    # -- Threshold factory function
    "build_threshold",  # noqa: F405
    # -- Base functions
    "dcsc",
    "ecad",
    "generic",
    "index",  # noqa: F405
    "indice",  # noqa: F405 (deprecated)
    "indices",  # noqa: F405
]

__version__ = "7.0.6"


def __getattr__(name: str) -> Callable:
    if name in ["index", "indice", "indices"]:
        from icclim.main import index as index_mod  # noqa: PLC0415
        from icclim.main import indice as indice_mod  # noqa: PLC0415
        from icclim.main import indices as indices_mod  # noqa: PLC0415

        if name == "index":
            return index_mod
        if name == "indice":
            return indice_mod
        return indices_mod
    if name == "build_threshold":
        from icclim.threshold.factory import build_threshold  # noqa: PLC0415

        return build_threshold
    msg = f"module {__name__} has no attribute {name}"
    raise AttributeError(msg)

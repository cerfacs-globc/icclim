"""Helpers that hide the differences between xclim versions."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

    from xarray import DataArray, Dataset


def get_xclim_compute() -> ModuleType:
    """
    Return the xclim module holding the pure ``DataArray`` functions.

    xclim 1.0 moved ``xclim.indices`` to ``xclim.compute``.
    The import is deferred to avoid loading xclim when icclim is imported.
    """
    try:
        from xclim import compute  # noqa: PLC0415
    except ImportError:
        from xclim import indices as compute  # noqa: PLC0415
    return compute


def get_comparison_kwarg(indicator: Callable) -> str:
    """
    Return the name of the comparison operator argument of an xclim indicator.

    It is ``condition`` in xclim 1.0 and ``op`` in earlier versions.
    """
    if "condition" in inspect.signature(indicator).parameters:
        return "condition"
    return "op"


def as_dataarray(result: DataArray | Dataset) -> DataArray:
    """
    Return a DataArray from the result of an xclim indicator.

    xclim 1.0 indicators return a Dataset holding a single variable, and the
    history attribute is stored on the Dataset.
    """
    if not hasattr(result, "data_vars"):
        return result  # type: ignore[return-value]
    da = result[next(iter(result.data_vars))]
    if "history" in result.attrs and "history" not in da.attrs:
        da.attrs["history"] = result.attrs["history"]
    return da

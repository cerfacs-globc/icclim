from __future__ import annotations

from typing import TypedDict

from icclim_types import InFileBaseType

from icclim.models.threshold import Threshold


class InFileDictionary(TypedDict, total=False):
    """Dictionary grouping in_files and var_name functionnalities.
    It also allows to use a different input for thresholds such as percentiles.

    Examples
    --------

    >>> in_files = {
    ...    "tasmax": { "study": "tasmax-store.zarr",
    ...                "thresholds": Threshold(">", ["per-1.nc", "per-2.nc"])
    ...              }
    ...    "pr": "pr.nc",
    ...    "tasmin": {"study": "tasmin.nc"},
    ...     }
    """

    study: InFileBaseType
    thresholds: Threshold
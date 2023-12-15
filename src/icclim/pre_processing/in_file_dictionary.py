from __future__ import annotations

from typing import TypedDict

from icclim.generic_indices.threshold import Threshold
from icclim.icclim_types import InFileBaseType


class InFileDictionary(TypedDict, total=False):
    """Dictionary grouping in_files and var_name functionnalities.
    It also allows to use a different input for thresholds such as percentiles.

    Examples
    --------

    .. code-block:: python

        in_files = {
            "tasmax": {
                "study": "tasmax-store.zarr",
                "threshold": build_threshold(operator=">", ["per-1.nc", "per-2.nc"]),
            },
            "pr": "pr.nc",
            "tasmin": {"study": "tasmin.nc"},
        }
    """

    study: InFileBaseType
    thresholds: Threshold | None

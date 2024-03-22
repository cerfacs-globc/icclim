"""Contains the InFileDictionary class."""

from __future__ import annotations

from typing import TYPE_CHECKING

# for Python <3.11 with (Not)Required
from typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from icclim._core.model.icclim_types import InFileBaseType
    from icclim._core.model.threshold import Threshold


class InFileDictionary(TypedDict):
    """
    Dictionary grouping in_files and var_name functionnalities.

    Attributes
    ----------
    study : InFileBaseType
        Study input file.
    thresholds : NotRequired[Threshold | None]
        Thresholds to apply to the study input file.

    Examples
    --------
    .. code-block:: python

        threshold = build_threshold(operator=">", value=["per-1.nc", "per-2.nc"])
        in_files = {
            "tasmax": {
                "study": "tasmax-store.zarr",
                "threshold": threshold,
            },
            "pr": "pr.nc",
            "tasmin": {"study": "tasmin.nc"},
        }

    Notes
    -----
    It also allows to use a different input for thresholds such as percentiles.
    """

    study: InFileBaseType
    thresholds: NotRequired[Threshold | None]

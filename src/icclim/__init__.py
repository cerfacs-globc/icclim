"""Python library for climate indices calculation."""

from icclim import dcsc, ecad, generic
from icclim._generated._ecad import *  # noqa: F403 (add ECAD api to icclim namespace)
from icclim._generated._generic import *  # noqa: F403 (add generic api to icclim namespace)
from icclim.main import index, indice, indices
from icclim.rechunk import create_optimized_zarr_store
from icclim.threshold.factory import build_threshold

__all__ = [
    # -- Threshold factory function
    "build_threshold",
    # -- Rechunk function
    "create_optimized_zarr_store",
    # -- Base functions
    "dcsc",
    "ecad",
    "generic",
    "index",
    "indice",  # deprecated
    "indices",
]

__version__ = "7.0.4"

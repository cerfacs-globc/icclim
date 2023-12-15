"""Python library for climate indices calculation"""

from icclim._generated_api import *  # noqa
from icclim.generic_indices.threshold import build_threshold
from icclim.main import index, indice, indices
from icclim.pre_processing.rechunk import create_optimized_zarr_store

__all__ = [
    # -- Base functions:
    "index",
    "indice",  # deprecated
    "indices",
    # -- Rechunk function:
    "create_optimized_zarr_store",
    # -- Threshold factory function
    "build_threshold",
]

__version__ = "6.5.0"

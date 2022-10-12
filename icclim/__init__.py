from icclim._generated_api import *  # noqa
from icclim.main import index, indice, indices
from icclim.models.constants import ICCLIM_VERSION
from icclim.pre_processing.rechunk import create_optimized_zarr_store

__all__ = [
    # -- Base functions:
    "index",
    "indice",  # deprecated
    "indices",
    # -- Rechunk function:
    "create_optimized_zarr_store",
]

__version__ = ICCLIM_VERSION

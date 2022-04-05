# keep imports below to expose api in `icclim` namespace
try:
    from _generated_api import *  # noqa
except ModuleNotFoundError:
    pass

from .main import index, indice, indices  # noqa
from .pre_processing.rechunk import create_optimized_zarr_store  # noqa

__version__ = "5.1.1-dev"

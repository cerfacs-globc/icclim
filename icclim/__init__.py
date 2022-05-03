# keep imports below to expose api in `icclim` namespace
from icclim.models.constants import ICCLIM_VERSION

from ._generated_api import *  # noqa
from .main import index, indice, indices  # noqa
from .pre_processing.rechunk import create_optimized_zarr_store  # noqa

__version__ = ICCLIM_VERSION

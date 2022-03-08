# keep imports below to expose api in `icclim` namespace
from .main import index, indice, list_indices
from .pre_processing.rechunk import create_optimized_zarr_store

__version__ = "5.0.2"

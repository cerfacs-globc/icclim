from __future__ import annotations

import contextlib
import copy

import dask
import fsspec
import psutil
import xarray as xr
import zarr
from fsspec import AbstractFileSystem
from fsspec.implementations.local import LocalFileSystem
from rechunker import rechunk
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

import icclim.utils as utils
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import IcclimLogger
from icclim.pre_processing.input_parsing import read_dataset

TMP_STORE_1 = "icclim-tmp-store-1.zarr"
TMP_STORE_2 = "icclim-tmp-store-2.zarr"
DEFAULT_DASK_CONF = {
    "distributed.worker.memory.target": False,
    "distributed.worker.memory.spill": False,
    "distributed.worker.memory.pause": "0.95",
    "distributed.worker.memory.terminate": "0.98",
}

logger = IcclimLogger.get_instance()


def _get_mem_limit(factor: float = 0.9) -> int:
    # According to
    # https://github.com/pangeo-data/rechunker/issues/54#issuecomment-700748875
    # we should limit rechunk mem usage to around 0.9 and avoid spilling to disk
    if factor > 1 or factor < 0:
        raise ValueError(f"factor was {factor} but, it must be between 0 and 1.")
    try:
        import distributed

        max_sys_mem = (
            distributed.get_client()
            .submit(lambda: distributed.get_worker().memory_limit)
            .result()
        )
    except (ValueError, ImportError):
        # Assumes default scheduler is used
        max_sys_mem = psutil.virtual_memory().total
    return int(factor * max_sys_mem)


@contextlib.contextmanager
def create_optimized_zarr_store(
    in_files: str | list[str] | Dataset | DataArray,
    var_names: str | list[str],
    target_zarr_store_name: str = "icclim-target-store.zarr",
    keep_target_store: bool = False,
    chunking: dict[str, int] | None = None,
    filesystem: str | AbstractFileSystem = LocalFileSystem(),
) -> xr.Dataset:
    """
    -- EXPERIMENTAL FEATURE --
    API may changes without deprecation warning!

    Context manager to create an zarr store given an input netcdf or xarray structure.
    The execution may take a long time

    The result is rechunked according to `chunking` schema provided.
    By default, when leaving `chunking` to None, the resulting zarr store is NOT chunked
    on time dimension.
    This kind of chunking will significantly speed up the bootstrapping of
    percentiles for indices such as Tx90p, Tx10p, TN90p...
    But such chunking will most likely result in suboptimal performances for other
    indices.
    Actually, when computing indices where no bootstrap is needed,
    you should first try the computation without using `create_optimized_zarr_store`.
    If there are performance issues, you may want to use `create_optimized_zarr_store`
    with a dictionary of a better chunking schema than your current storage chunking.

    By default, `keep_target_store` being False, the resulting zarr store is destroyed
    when the context manager is exit.
    To keep the zarr store for futur uses set `keep_target_store` to True.

    The output is the resulting zarr store as a xarray Dataset.

    Examples
    --------

    >>> import icclim
    >>> with icclim.create_optimized_zarr_store(
    >>>                             in_files="tasmax.nc",
    >>>                             var_names="tasmax",
    >>>                             target_zarr_store_name="tasmax-store.zarr",
    >>>                             chunking={"time": 42, "lat": 42, "lon": 42},
    >>>                             ) as tasmax_opti:
    >>>      su_out = icclim.index(in_files = tasmax_opti, index_name = "su")

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    var_names : str | list[str]
        List of data variable to include in the target zarr store.
        All other data variable are dropped.
        The coordinate variable are untouched and are part of the target zarr store.
    target_zarr_store_name : str
        Name of the target zarr store.
        Used to avoid overriding an existing zarr store.
    chunking : dict
        The target chunking schema.
    keep_target_store : bool
        Set to True to keep the target zarr store after the execution of the context
        manager.
        Set to False to remove the target zarr store once execution is finished.
        Default is False.
    filesystem :
        A fsspec filesystem where the zarr store will be created.

    Returns
    -------
    returns xr.Dataset opened on the newly created target zarr store.

    """
    try:
        if isinstance(filesystem, str):
            filesystem = fsspec.filesystem("file")
        _remove_stores(
            TMP_STORE_1, TMP_STORE_2, target_zarr_store_name, filesystem=filesystem
        )
        yield _unsafe_create_optimized_zarr_store(
            in_files,
            var_names,
            target_zarr_store_name,
            chunking,
            _get_mem_limit(),
            filesystem,
        )
    finally:
        stores_to_remove = [TMP_STORE_1, TMP_STORE_2]
        if not keep_target_store:
            stores_to_remove.append(target_zarr_store_name)
        _remove_stores(*stores_to_remove, filesystem=filesystem)


def _remove_stores(*stores, filesystem):
    for s in stores:
        try:
            filesystem.rm(s, recursive=True, maxdepth=100)
        except FileNotFoundError:
            pass


def _unsafe_create_optimized_zarr_store(
    in_files: str | list[str] | Dataset | DataArray,
    var_names: str | list[str],
    zarr_store_name: str,
    chunking: dict[str, int] | None,
    max_mem: int,
    filesystem: AbstractFileSystem,
):
    with dask.config.set(DEFAULT_DASK_CONF):
        logger.info("Rechunking in progress, this will take some time.")
        ds, _, is_zarr = read_dataset(in_files, index=None, var_names=var_names)
        # drop all non essential data variables
        ds = ds.drop_vars(filter(lambda v: v not in var_names, ds.data_vars.keys()))
        if len(ds.data_vars.keys()) == 0:
            raise InvalidIcclimArgumentError(
                f"The variable(s) {var_names} were not found in the dataset."
            )
        if _is_rechunking_unnecessary(ds, chunking):
            raise InvalidIcclimArgumentError(
                f"The given input is already chunked following {chunking}."
                f" It's unnecessary to rechunk data with"
                f" `create_optimized_zarr_store` here."
            )
        elif chunking is None:
            chunking = _build_default_chunking(ds)
        # It seems rechunker performs better when the dataset is first converted
        # to a zarr store, without rechunking anything.
        if not is_zarr:
            # needed to have unified chunk that can be written to zarr
            ds = ds.chunk("auto").unify_chunks()
            ds.to_zarr(TMP_STORE_1, mode="w")
            ds = xr.open_zarr(TMP_STORE_1)
        ds = ds.chunk(chunking)
        target_chunks = {}
        for data_var in ds.data_vars:
            ds[data_var].encoding = {}
            acc = {}
            for dim in ds[data_var].dims:
                acc.update({dim: utils._get_chunksizes(ds)[dim][0]})
            target_chunks.update({data_var: acc})
        for c in ds.coords:
            ds[c].encoding = {}
            target_chunks.update({c: None})
        rechunk(
            source=ds,
            target_chunks=target_chunks,
            max_mem=max_mem,
            target_store=zarr_store_name,
            temp_store=TMP_STORE_2,
        ).execute()
        _remove_stores(TMP_STORE_1, TMP_STORE_2, filesystem=filesystem)
        zarr.consolidate_metadata(zarr_store_name)
        return xr.open_zarr(zarr_store_name)


def _build_default_chunking(ds: Dataset) -> dict:
    # Leave dask find the best chunking schema for all dimensions but `dim`
    chunking = {d: "auto" for d in ds.dims}
    chunking["time"] = -1
    return chunking


def _is_rechunking_unnecessary(ds, chunking) -> bool:
    cp = copy.deepcopy(ds.chunks)
    if chunking is None:
        return len(ds.chunks["time"]) == 1
    else:
        return ds.chunk(chunking).chunks == cp

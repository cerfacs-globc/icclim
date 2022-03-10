import contextlib
import shutil
from typing import List, Union

import dask
import psutil
import xarray as xr
from rechunker import rechunk
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.pre_processing.input_parsing import read_dataset

TMP_STORE_1 = "icclim-tmp-store-1.zarr"
TMP_STORE_2 = "icclim-tmp-store-2.zarr"


def _get_mem_limit(factor: float = 0.9) -> int:
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
    in_files: Union[str, List[str], Dataset, DataArray],
    var_names: Union[str, List[str]],
    target_zarr_store_name: str = "icclim-target-store.zarr",
    dim="time",
    keep_target_store: bool = False,
):
    """
    EXPERIMENTAL FEATURE

    todo fill doc

    Parameters
    ----------
    in_files :
    var_names :
    target_zarr_store_name :
    dim :
    keep_target_store :

    Returns
    -------

    """
    # According to
    # https://github.com/pangeo-data/rechunker/issues/54#issuecomment-700748875
    # we should limit rechunk mem usage to around 0.9 and avoid spilling to disk
    try:
        shutil.rmtree(TMP_STORE_1, ignore_errors=True)
        shutil.rmtree(TMP_STORE_2, ignore_errors=True)
        shutil.rmtree(target_zarr_store_name, ignore_errors=True)
        yield _unsafe_create_optimized_zarr_store(
            in_files, var_names, target_zarr_store_name, dim, _get_mem_limit()
        )
    finally:
        shutil.rmtree(TMP_STORE_1, ignore_errors=True)
        shutil.rmtree(TMP_STORE_2, ignore_errors=True)
        if not keep_target_store:
            shutil.rmtree(target_zarr_store_name, ignore_errors=True)


def _unsafe_create_optimized_zarr_store(
    in_files: Union[str, List[str], Dataset, DataArray],
    var_names: Union[str, List[str]],
    zarr_store_name: str,
    dim: str,
    max_mem: int,
):
    """
    Create a single zarr store for for the variables var_names initialy stored in
    in_files.
    This zarr store chunking is optimized for analysis on `dim` dimension.
    Thus, it's optimal for icclim when dim=="time.

    Parameters
    ----------
    in_files :
    var_names :
    zarr_store_name :
    dim :

    Returns
    -------

    """
    with dask.config.set(
        {
            "distributed.worker.memory.target": "0.95",
            "distributed.worker.memory.spill": "0.95",
            "distributed.worker.memory.pause": "0.95",
            "distributed.worker.memory.terminate": "0.98",
        }
    ):
        ds, _ = read_dataset(in_files, index=None, var_names=var_names)
        # drop all non essential data variables
        ds = ds.drop_vars(filter(lambda v: v not in var_names, ds.data_vars.keys()))
        ds = ds.chunk("auto")
        ds.to_zarr(TMP_STORE_1, mode="w")
        # Leave dask find the best chunking schema for all dimensions but `dim`
        chunking = {d: "auto" for d in ds.dims}
        chunking[dim] = -1  # no chunking on dim to use map_block
        ds_zarr = xr.open_zarr(TMP_STORE_1).chunk(chunking)
        target_chunks = {}
        for data_var in ds_zarr.data_vars:
            ds_zarr[data_var].encoding = {}
            acc = {}
            for dim in ds_zarr[data_var].dims:
                # fixme: `.chunksizes` is only available on xarray v0.20.0
                acc.update({dim: ds_zarr[data_var].chunksizes[dim][0]})
            target_chunks.update({data_var: acc})
        for c in ds_zarr.coords:
            ds_zarr[c].encoding = {}
            target_chunks.update({c: None})
        rechunk(
            source=ds_zarr,
            target_chunks=target_chunks,
            max_mem=max_mem,
            target_store=zarr_store_name,
            temp_store=TMP_STORE_2,
        ).execute()
        return xr.open_zarr(zarr_store_name)

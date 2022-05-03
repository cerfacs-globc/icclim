from __future__ import annotations

import xarray as xr
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.ecad_indices import EcadIndex


def read_dataset(
    data: str | list[str] | Dataset | DataArray,
    index: EcadIndex | None = None,
    var_names: str | list[str] | None = None,
) -> tuple[Dataset, bool, bool]:
    is_zarr = False
    if isinstance(data, Dataset):
        input_dataset = data
        chunk_da = False
    elif isinstance(data, DataArray):
        if index is None:
            # user index case
            if var_names is None or (
                isinstance(var_names, list) and len(var_names) > 1
            ):
                raise InvalidIcclimArgumentError(
                    "When the input is a DataArray, var_names must be a string."
                )
            if isinstance(var_names, list):
                var_names = var_names[0]
            data_name = var_names
        else:
            if len(index.variables) > 1:
                raise InvalidIcclimArgumentError(
                    f"Index {index.name} needs {len(index.variables)} variables."
                    f" Please provide them with an xarray.Dataset, a netCDF file or a"
                    f" zarr store."
                )
            data_name = index.variables[0][0]  # first alias of the unique variable
        input_dataset = data.to_dataset(name=data_name, promote_attrs=True)
        chunk_da = False
    elif isinstance(data, list):
        input_dataset = xr.open_mfdataset(data, parallel=True)
        chunk_da = True
    elif isinstance(data, str):
        if ".nc" in data:
            input_dataset = xr.open_dataset(data)
            chunk_da = True
        else:  # assume it's a zarr store
            input_dataset = xr.open_zarr(data)
            chunk_da = True
            is_zarr = True
    else:
        raise NotImplementedError("`in_files` format was not recognized.")
    return input_dataset, chunk_da, is_zarr


def update_to_standard_coords(ds: Dataset) -> tuple[Dataset, dict]:
    """
    Mutate input ds to use more icclim friendly coordinate name.
    """
    # TODO see if cf-xarray could replace this
    revert = {}
    if ds.coords.get("latitude") is not None:
        ds = ds.rename({"latitude": "lat"})
        revert.update({"lat": "latitude"})
    if ds.coords.get("longitude") is not None:
        ds = ds.rename({"longitude": "lon"})
        revert.update({"lon": "longitude"})
    if ds.coords.get("t") is not None:
        ds = ds.rename({"t": "time"})
        revert.update({"time": "t"})
    return ds, revert

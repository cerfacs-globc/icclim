from typing import Dict, List, Optional, Tuple, Union

import xarray as xr
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.ecad_indices import EcadIndex


def read_dataset(
    data: Union[str, List[str], Dataset, DataArray],
    index: Optional[EcadIndex],
    var_names: Union[str, List[str], None],
) -> Tuple[Dataset, bool]:
    # TODO add unit test
    if isinstance(data, Dataset):
        input_dataset = data
        chunk_da = False
    elif isinstance(data, DataArray):
        if index is None:
            # user index case
            if isinstance(var_names, str):
                var_names = [var_names]
            if len(var_names) > 1 or var_names[0] is None:
                raise InvalidIcclimArgumentError(
                    "When the input is a DataArray, var_names must be a string"
                )
            name = var_names
        else:
            if len(index.variables) > 1:
                raise InvalidIcclimArgumentError(
                    f"Index {index.name} need {len(index.variables)} variables."
                    f"Please provides them with an xarray.Dataset or a netCDF file."
                )
            name = index.variables[0][0]  # first alias of the unique variable
        input_dataset = data.to_dataset(name=name, promote_attrs=True)
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
    else:
        raise NotImplementedError("in_files format was not recognized.")
    return input_dataset, chunk_da


def update_to_standard_coords(ds: Dataset) -> Tuple[Dataset, Dict]:
    """
    Mutate input ds to use more icclim friendly coordinate name.
    """
    # TODO add unit test
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

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, TypedDict, Union, Sequence

import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from xclim.core.calendar import percentile_doy
from xclim.core.utils import PercentileDataArray

from generic_indices import CF_VAR_METADATA_REGISTRY
from icclim.generic_indices.cf_var_metadata import CfVarMetadata
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendar
from icclim.models.climate_index import ClimateIndex
from icclim.models.constants import VALID_PERCENTILE_DIMENSION
from icclim.models.frequency import Frequency
from icclim.models.index_group import IndexGroup
from icclim.utils import get_date_to_iso_format
from icclim_types import ThresholdType

InFileBaseType = Union[str, List[str], Dataset, DataArray]

DEFAULT_INPUT_FREQUENCY = "days"


class InFileDictionary(TypedDict, total=False):
    """Dictionary grouping in_files and var_name functionnalities.
    It also allows to use a different input for thresholds such as percentiles.

    Examples
    --------

    >>> in_files = {
    ...    "tasmax": { "study": "tasmax-store.zarr",
    ...                "thresholds": ["per-1.nc", "per-2.nc"],
    ...                "climatology_bounds":['1990-01-01', '1991-12-31'],
    ...                "threshold_var_name":"tas_max_per" },
    ...    "pr": "pr.nc",
    ...    "tasmin": {"study": "tasmin.nc"},
    ...     }
    """

    study: InFileBaseType
    thresholds: InFileBaseType | ThresholdType | Sequence[ThresholdType]
    climatology_bounds: Sequence[str, str] | None  # may be guessed if missing
    threshold_var_name: str | None  # may be guessed if missing


InFileType = Union[Dict[str, Union[InFileDictionary, InFileBaseType]], InFileBaseType]


def guess_var_names(
    ds: Dataset,
    index: ClimateIndex | None = None,
    var_names: str | Sequence[str] | None = None,
) -> list[str]:
    if var_names is None:
        if index is None:
            raise InvalidIcclimArgumentError(
                "Unable to guess variable(s) name. Provide it/them using `var_name`."
            )
        return _guess_dataset_var_names(index, ds)
    elif isinstance(var_names, str):
        return [var_names]
    elif isinstance(var_names, (list, tuple)):
        return var_names
    else:
        raise NotImplementedError("`var_name` must be a string a list or None.")


def read_dataset(
    in_files: InFileType,
    index: ClimateIndex = None,
    var_name: str | Sequence[str] = None,  # used only if input is a DataArray
) -> Dataset:
    if isinstance(in_files, Dataset):
        ds = in_files
    elif isinstance(in_files, DataArray):
        ds = _read_dataarray(in_files, index, var_name=var_name)
    elif isinstance(in_files, (list, tuple)) and is_netcdf(in_files[0]):
        # we assumes it's a list of netCDF files
        ds = xr.open_mfdataset(in_files, parallel=True)
    elif is_netcdf(in_files):
        ds = xr.open_dataset(in_files)
    elif is_zarr(in_files):
        ds = xr.open_zarr(in_files)
    else:
        raise NotImplementedError("`in_files` format was not recognized.")
    return update_to_standard_coords(ds).chunk("auto")

def update_to_standard_coords(ds: Dataset) -> Dataset:
    """
    Mutate input ds to use more icclim friendly coordinate name.
    """
    # TODO see if cf-xarray could replace this
    reset = {}
    if ds.coords.get("latitude") is not None:
        ds = ds.rename({"latitude": "lat"})
        reset.update({"lat": "latitude"})
    if ds.coords.get("longitude") is not None:
        ds = ds.rename({"longitude": "lon"})
        reset.update({"lon": "longitude"})
    if ds.coords.get("t") is not None:
        ds = ds.rename({"t": "time"})
        reset.update({"time": "t"})
    ds.attrs["reset_coords_dict"] = reset
    return ds


def is_zarr(path: InFileBaseType):
    return isinstance(path, str) and ".zarr" in path


def is_netcdf(path: InFileBaseType):
    return isinstance(path, str) and ".nc" in path


def _standardize_percentile_dim_name(per_da: DataArray) -> DataArray:
    # This function could probably be backported to xclim PercentileDataArray
    per_dim_name = None
    for d in VALID_PERCENTILE_DIMENSION:
        if d in per_da.dims:
            per_dim_name = d
        elif f"{d}s" in per_da.dims:
            # plural handling
            per_dim_name = f"{d}s"
    if per_dim_name is None:
        raise InvalidIcclimArgumentError(
            "Percentile data must contain a recognizable"
            " percentiles dimension such as 'percentiles',"
            " 'quantile', 'per' or 'centile'."
        )
    per_da = per_da.rename({per_dim_name: "percentiles"})
    if "quantile" in per_dim_name:
        per_da.coords["percentiles"] = per_da.coords["percentiles"] * 100
    return per_da


def _read_clim_bounds(
    climatology_bounds: Sequence[str, str], per_da: DataArray
) -> list[str]:
    bds = climatology_bounds or per_da.attrs.get("climatology_bounds", None)
    if len(bds) != 2:
        raise InvalidIcclimArgumentError(
            "climatology_bounds must be a iterable of length 2."
        )
    return [d for d in map(lambda bd: get_date_to_iso_format(bd), bds)]


def _read_dataarray(
    data: DataArray, index: ClimateIndex = None, var_name: str | Sequence[str] = None
) -> Dataset:
    if isinstance(var_name, list):
        if len(var_name) > 1:
            raise InvalidIcclimArgumentError(
                "When the `in_file` is a DataArray, there"
                " can only be one value in `var_name`."
            )
        else:
            var_name = var_name[0]
    if index is not None:
        if index.input_variables and len(index.input_variables) > 1:
            raise InvalidIcclimArgumentError(
                f"Index {index.short_name} needs {len(index.input_variables)} variables."
                f" Please provide them with an xarray.Dataset, netCDF file(s) or a"
                f" zarr store."
            )
        # first alias of the unique variable
        data_name = var_name or index.input_variables[0][0]
    else:
        data_name = var_name or data.name or "unnamed_var"
    return data.to_dataset(name=data_name, promote_attrs=True)


def _guess_dataset_var_names(index: ClimateIndex, ds: Dataset) -> list[str]:
    """Try to guess the variable names using the expected kind of variable for
    the index.
    """

    def get_error() -> Exception:
        main_aliases = ", ".join(map(lambda v: v[0], index_expected_vars))
        return InvalidIcclimArgumentError(
            f"Index {index.short_name} needs the following variable(s)"
            f" [{main_aliases}], some of them were not recognized in the input."
            f" Use `var_name` parameter to explicitly use data variable names"
            f" from your input dataset: {list(ds.data_vars)}."
        )

    index_expected_vars = index.input_variables
    # todo if index_expected_vars is empty find all standard variable using cf_input
    if len(ds.data_vars) == 1:
        if len(index_expected_vars) != 1:
            raise get_error()
        return [get_name_of_first_var(ds)]
    climate_var_names = []
    for indice_var in index_expected_vars:
        for alias in indice_var:
            # check if dataset contains this alias
            if _is_alias_valid(ds, index, alias):
                climate_var_names.append(alias)
                break
    if len(climate_var_names) < len(index_expected_vars):
        raise get_error()
    return climate_var_names


def guess_input_type(data: DataArray) -> CfVarMetadata:
    cf_input = CF_VAR_METADATA_REGISTRY.lookup(data)
    cf_input.frequency = Frequency.lookup(
        xr.infer_freq(data.time) or DEFAULT_INPUT_FREQUENCY
    )
    cf_input.units = data.attrs.get("units", cf_input.default_units)
    return cf_input


def build_study_da(
    original_da: DataArray,
    time_range: list[str] | None,
    ignore_Feb29th: bool,
    sampling_frequency: Frequency,
) -> DataArray:
    if time_range is not None:
        check_time_range_pre_validity("time_range", time_range)
        time_range = [get_date_to_iso_format(x) for x in time_range]
        da = original_da.sel(time=slice(time_range[0], time_range[1]))
        check_time_range_post_validity(da, original_da, "time_range", time_range)
        if len(da.time) == 0:
            raise InvalidIcclimArgumentError(
                f"The given `time_range` {time_range} "
                f"is out of the dataset time period: "
                f"{original_da.time.min().dt.floor('D').values} "
                f"- {original_da.time.max().dt.floor('D').values}."
            )
    else:
        da = original_da
    if ignore_Feb29th:
        da = xclim.core.calendar.convert_calendar(da, CfCalendar.NO_LEAP.get_name())
    if sampling_frequency.time_clipping is not None:
        da = sampling_frequency.time_clipping(da)
    return da


def check_time_range_pre_validity(key: str, tr: Sequence[datetime | str]) -> None:
    if len(tr) != 2:
        raise InvalidIcclimArgumentError(
            f"The given `{key}` {tr}"
            f" has {len(tr)} elements."
            f" It must have exactly 2 dates."
        )


def check_time_range_post_validity(da, original_da, key: str, tr: list) -> None:
    if len(da.time) == 0:
        raise InvalidIcclimArgumentError(
            f"The given `{key}` {tr} is out of the sample time bounds:"
            f" {original_da.time.min().dt.floor('D').values}"
            f" - {original_da.time.max().dt.floor('D').values}."
        )


def _is_alias_valid(ds, index, alias):
    return ds.get(alias, None) is not None and _has_valid_unit(index.group, ds[alias])


def _has_valid_unit(group: IndexGroup, da: DataArray) -> bool:
    if group == IndexGroup.SNOW:
        try:
            # todo: unit check might be replaced by cf-xarray
            xclim.core.units.check_units.__wrapped__(da, "[length]")
        except xclim.core.utils.ValidationError:
            return False
    # We delegate to xclim other unit checks
    return True


def _get_threshold_var_name(
    ds: Dataset, threshold_var_name: str, climate_var_name: str
) -> str:
    if threshold_var_name is not None:
        return threshold_var_name
    elif len(ds.data_vars) == 1:
        return get_name_of_first_var(ds)
    else:
        return _guess_threshold_var_name(climate_var_name, ds)


def _guess_threshold_var_name(climate_var_name: str, ds: Dataset) -> str:
    data_var_names = map(lambda v: str(v.name), ds.data_vars)
    for x in data_var_names:
        if climate_var_name in x:
            return x
    raise InvalidIcclimArgumentError(
        "Could not guess the variable name for percentiles"
        f" of {climate_var_name}. Please, provide the"
        f" explicite name using threshold_var_name like so:"
        f" \u007bf'{climate_var_name}':"
        f" \u007b'study': 'x.nc',"
        f" 'percentiles': 'y.nc',"
        f" threshold_var_name='{climate_var_name}_percentiles'"
        f" \u007d\u007d"
    )


def get_name_of_first_var(ds: Dataset) -> str:
    return str(ds.data_vars[list(ds.data_vars.keys())[0]].name)

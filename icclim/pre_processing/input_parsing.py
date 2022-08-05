from __future__ import annotations

import re
from datetime import datetime
from typing import Sequence

import numpy as np
import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from xclim.core.units import convert_units_to
from xclim.core.utils import PercentileDataArray

from icclim.generic_indices.cf_var_metadata import CfVarMetadata, CfVarMetadataRegistry
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_types import InFileBaseType, InFileType
from icclim.models.cf_calendar import CfCalendarRegistry
from icclim.models.climate_index import ClimateIndex
from icclim.models.constants import VALID_PERCENTILE_DIMENSION
from icclim.models.frequency import Frequency, FrequencyRegistry
from icclim.models.index_group import IndexGroup, IndexGroupRegistry
from icclim.utils import get_date_to_iso_format

DEFAULT_INPUT_FREQUENCY = "days"


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
    elif is_glob_path(in_files) or (
        isinstance(in_files, (list, tuple)) and is_netcdf_path(in_files[0])
    ):
        # we assumes it's a list of netCDF files
        #  join="override" is used for cases some dimension are a tiny bit different
        #  in different files (was the case with eobs).
        ds = xr.open_mfdataset(in_files, parallel=True, join="override")
    elif is_netcdf_path(in_files):
        ds = xr.open_dataset(in_files)
    elif is_zarr_path(in_files):
        ds = xr.open_zarr(in_files)
    else:
        raise NotImplementedError("`in_files` format was not recognized.")
    return update_to_standard_coords(ds)


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


def is_zarr_path(path: InFileBaseType) -> bool:
    return isinstance(path, str) and ".zarr" in path


def is_netcdf_path(path: InFileBaseType) -> bool:
    return isinstance(path, str) and ".nc" in path


def is_glob_path(path: InFileBaseType) -> bool:
    return isinstance(path, str) and "*" in path


def standardize_percentile_dim_name(per_da: DataArray) -> DataArray:
    # todo This function could probably be backported to xclim PercentileDataArray
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


def read_clim_bounds(
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
    if isinstance(var_name, (tuple, list)):
        if len(var_name) > 1:
            raise InvalidIcclimArgumentError(
                "When the `in_file` is a DataArray, there"
                f" can only be one value in `var_name` but var_name was: {var_name} "
            )
        else:
            var_name = var_name[0]
    if index is not None:
        if index.input_variables and len(index.input_variables) > 1:
            raise InvalidIcclimArgumentError(
                f"Index {index.short_name} needs {len(index.input_variables)} "
                f"variables."
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
    cf_input = CfVarMetadataRegistry.lookup(str(data.name))
    cf_input.frequency = FrequencyRegistry.lookup(
        xr.infer_freq(data.time) or DEFAULT_INPUT_FREQUENCY
    )
    cf_input.units = data.attrs.get("units", cf_input.default_units)
    return cf_input


def build_study_da(
    original_da: DataArray,
    time_range: Sequence[str] | None,
    ignore_Feb29th: bool,
    sampling_frequency: Frequency,
    cf_meta_unit: str,
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
        da = xclim.core.calendar.convert_calendar(da, CfCalendarRegistry.NO_LEAP.name)
    if sampling_frequency.time_clipping is not None:
        da = sampling_frequency.time_clipping(da)
    if da.attrs.get("units", None):
        da.attrs["units"] = cf_meta_unit
    da = da.chunk("auto")
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
    if group == IndexGroupRegistry.SNOW:
        try:
            # todo: unit check might be replaced by cf-xarray
            xclim.core.units.check_units.__wrapped__(da, "[length]")
        except xclim.core.utils.ValidationError:
            return False
    # We delegate to xclim other unit checks
    return True


def get_name_of_first_var(ds: Dataset) -> str:
    return str(ds.data_vars[list(ds.data_vars.keys())[0]].name)


def is_dataset_path(query: Sequence | str) -> bool:
    if isinstance(query, (tuple, list)):
        return all(map(lambda q: is_netcdf_path(q), query))
    return is_zarr_path(query) or is_glob_path(query) or is_netcdf_path(query)


def reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use `only_leap_years` parameter."
        )
    return xr.concat(reduced_list, "time")


def read_string_threshold(query: str):
    value = re.findall(r"-?\d+\.?\d*", query)[0]
    value_index = query.find(value)
    operator = query[0:value_index].strip()
    if value_index < len(query) - 1:
        unit = query[value_index + len(value) :].strip()
    else:
        unit = None
    return operator, unit, float(value)


def read_threshold_DataArray(
    thresh_da: DataArray,
    threshold_min_value: str | float,
    climatology_bounds: Sequence[str],
    unit: str,
):
    if PercentileDataArray.is_compatible(thresh_da):
        built_value = PercentileDataArray.from_da(
            standardize_percentile_dim_name(thresh_da),
            read_clim_bounds(climatology_bounds, thresh_da),
        )
        built_value.attrs["unit"] = unit
    else:
        if threshold_min_value:
            if isinstance(threshold_min_value, str):
                threshold_min_value = convert_units_to(threshold_min_value, thresh_da)
            # todo in prcptot the replacing value (np.nan) needs to be 0
            built_value = thresh_da.where(thresh_da > threshold_min_value, np.nan)
        else:
            built_value = thresh_da
        built_value.attrs["unit"] = unit
    return built_value


def build_reference_da(
    original_da: DataArray,
    base_period_time_range: Sequence[datetime | str] | None,
    only_leap_years: bool,
    sampling_frequency: Frequency,
    percentile_min_value: str | float | None,
) -> DataArray:
    # todo [refacto] move back to threshold ?
    reference = original_da
    if base_period_time_range:
        check_time_range_pre_validity("base_period_time_range", base_period_time_range)
        base_period_time_range = [
            get_date_to_iso_format(x) for x in base_period_time_range
        ]
        reference = original_da.sel(
            time=slice(base_period_time_range[0], base_period_time_range[1])
        )
        check_time_range_post_validity(
            reference, original_da, "base_period_time_range", base_period_time_range
        )
    if sampling_frequency.time_clipping is not None:
        reference = sampling_frequency.time_clipping(reference)
    if only_leap_years:
        reference = reduce_only_leap_years(original_da)
    if percentile_min_value:
        if isinstance(percentile_min_value, str):
            percentile_min_value = convert_units_to(percentile_min_value, reference)
        # todo in prcptot the replacing value (np.nan) needs to be 0
        reference = reference.where(reference >= percentile_min_value, np.nan)
    return reference

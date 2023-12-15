from __future__ import annotations

from datetime import datetime
from typing import Hashable, Sequence

import numpy as np
import xarray as xr
import xclim
from pint import Quantity
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from xclim.core.units import convert_units_to

from icclim.generic_indices.standard_variable import (
    StandardVariable,
    StandardVariableRegistry,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_types import InFileBaseType
from icclim.models.cf_calendar import CfCalendarRegistry
from icclim.models.constants import UNITS_KEY, VALID_PERCENTILE_DIMENSION
from icclim.models.standard_index import StandardIndex
from icclim.utils import get_date_to_iso_format, is_precipitation_amount

DEFAULT_INPUT_FREQUENCY = "days"


class PercentileDataArray(xr.DataArray):
    """Wrap xarray DataArray for percentiles values."""

    __slots__ = ()

    @classmethod
    def is_compatible(cls, source: xr.DataArray) -> bool:
        """Evaluate whether PecentileDataArray is conformant with expected fields.

        A PercentileDataArray must have climatology_bounds attributes and either a
        quantile or percentiles coordinate, the window is not mandatory.
        """
        return (
            isinstance(source, xr.DataArray)
            and source.attrs.get("climatology_bounds", None) is not None
            and ("quantile" in source.coords or "percentiles" in source.coords)
        )

    @classmethod
    def from_da(
        cls, source: xr.DataArray, climatology_bounds: list[str] = None
    ) -> PercentileDataArray:
        """Create a PercentileDataArray from a xarray.DataArray.

        Parameters
        ----------
        source : xr.DataArray
            A DataArray with its content containing percentiles values.
            It must also have a coordinate variable percentiles or quantile.
        climatology_bounds : list[str]
            Optional. A List of size two which contains the period on which the
            percentiles were computed. See
            `xclim.core.calendar.build_climatology_bounds`
            to build this list from a DataArray.

        Returns
        -------
        PercentileDataArray
            The initial `source` DataArray but wrap by PercentileDataArray class.
            The data is unchanged and only climatology_bounds attributes is overridden
            if q new value is given in inputs.
        """
        if (
            climatology_bounds is None
            and source.attrs.get("climatology_bounds", None) is None
        ):
            raise ValueError("PercentileDataArray needs a climatology_bounds.")
        per = cls(source)
        # handle case where da was created with `quantile()` method
        if "quantile" in source.coords:
            per = per.rename({"quantile": "percentiles"})
            per.coords["percentiles"] = per.coords["percentiles"] * 100
        clim_bounds = source.attrs.get("climatology_bounds", climatology_bounds)
        per.attrs["climatology_bounds"] = clim_bounds
        if "percentiles" in per.coords:
            return per
        raise ValueError(
            f"DataArray {source.name} could not be turned into"
            f" PercentileDataArray. The DataArray must have a"
            f" 'percentiles' coordinate variable."
        )


def guess_var_names(
    ds: Dataset,
    var_names: str | Sequence[str] | None,
    standard_index: StandardIndex | None,
) -> list[Hashable]:
    if var_names is None:
        return _guess_dataset_var_names(ds=ds, standard_index=standard_index)
    elif isinstance(var_names, str):
        return [var_names]
    elif isinstance(var_names, (list, tuple)):
        return var_names
    else:
        raise NotImplementedError("`var_name` must be a string a list or None.")


def read_dataset(
    in_files: InFileBaseType,
    standard_var: StandardVariable | None = None,
    var_name: str | Sequence[str] = None,
) -> Dataset:
    if isinstance(in_files, Dataset):
        ds = in_files
    elif isinstance(in_files, DataArray):
        ds = _read_dataarray(in_files, standard_var=standard_var, var_name=var_name)
    elif is_glob_path(in_files) or (
        isinstance(in_files, (list, tuple)) and is_netcdf_path(in_files[0])
    ):
        # we assumes it's a list of netCDF files
        #  join="override" is used for cases some dimension are a tiny bit different
        #  in different files (was the case with eobs).
        ds = xr.open_mfdataset(in_files, parallel=True, join="override")  # noqa
    elif is_netcdf_path(in_files):
        ds = xr.open_dataset(in_files)
    elif is_zarr_path(in_files):
        ds = xr.open_zarr(in_files)
    elif isinstance(in_files, (list, tuple)):
        return xr.merge(
            [
                read_dataset(in_file, standard_var, var_name[i])
                for i, in_file in enumerate(in_files)
            ]
        )
    else:
        raise NotImplementedError(
            f"`in_files` format {type(in_files)} was not" f" recognized."
        )
    return update_to_standard_coords(ds)


def update_to_standard_coords(ds: Dataset) -> Dataset:
    """
    Mutate input ds to use more icclim friendly coordinate names.
    """
    # TODO see if cf-xarray could replace this
    if ds.coords.get("t") is not None:
        ds = ds.rename({"t": "time"})
    return ds


def is_zarr_path(path: InFileBaseType) -> bool:
    return isinstance(path, str) and ".zarr" in path


def is_netcdf_path(path: InFileBaseType) -> bool:
    return isinstance(path, str) and ".nc" in path


def is_glob_path(path: InFileBaseType) -> bool:
    return isinstance(path, str) and "*" in path


def standardize_percentile_dim_name(per_da: DataArray) -> DataArray:
    # todo [xclim backport] This function could probably be in PercentileDataArray
    per_dim_name = None
    for d in VALID_PERCENTILE_DIMENSION:
        if d in per_da.dims:
            per_dim_name = d
        elif f"{d}s" in per_da.dims:
            # plural handling
            per_dim_name = f"{d}s"
    if per_dim_name is None:
        raise InvalidIcclimArgumentError(
            "Percentile data must contain a recognizable percentiles dimension such as"
            " 'percentiles', 'quantile', 'per' or 'centile'."
        )
    per_da = per_da.rename({per_dim_name: "percentiles"})
    if "quantile" in per_dim_name:
        per_da.coords["percentiles"] = per_da.coords["percentiles"] * 100
    return per_da


def read_clim_bounds(
    climatology_bounds: Sequence[str, str] | None, per_da: DataArray
) -> list[str]:
    bds = climatology_bounds or per_da.attrs.get("climatology_bounds", None)
    if len(bds) != 2:
        raise InvalidIcclimArgumentError(
            "climatology_bounds must be a iterable of length 2."
        )
    return [d for d in map(lambda bd: get_date_to_iso_format(bd), bds)]


def _read_dataarray(
    data: DataArray,
    standard_var: StandardVariable | None = None,
    var_name: str | Sequence[str] = None,
) -> Dataset:
    if isinstance(var_name, (tuple, list)):
        if len(var_name) > 1:
            raise InvalidIcclimArgumentError(
                "When the `in_file` is a DataArray, there"
                f" can only be one value in `var_name` but var_name was: {var_name} "
            )
        else:
            var_name = var_name[0]
        data_name = var_name or standard_var.short_name or None
    else:
        data_name = var_name or data.name or "unnamed_var"
    return data.to_dataset(name=data_name, promote_attrs=True)


def _guess_dataset_var_names(
    standard_index: StandardIndex, ds: Dataset
) -> list[Hashable]:
    """Try to guess the variable names using the expected kind of variable for
    the index.
    """
    if standard_index is not None:
        main_aliases = ", ".join(
            map(lambda v: v.short_name, standard_index.input_variables)
        )
        error_msg = (
            f"Index {standard_index.short_name} needs the following variable(s)"
            f" [{main_aliases}], but the input variables were {list(ds.data_vars)}."
            f" Use `var_name` parameter to explicitly set variable names."
        )
        if len(ds.data_vars) == 1:
            if len(standard_index.input_variables) != 1:
                raise InvalidIcclimArgumentError(error_msg)
            return [get_name_of_first_var(ds)]
        climate_var_names = []
        for expected_standard_var in standard_index.input_variables:
            for alias in expected_standard_var.aliases:
                # check if dataset contains this alias
                if _is_alias_valid(ds, alias):
                    climate_var_names.append(_get_actual_name(ds, alias))
                    break
        if len(climate_var_names) < len(standard_index.input_variables):
            raise InvalidIcclimArgumentError(error_msg)
        return climate_var_names
    else:
        if len(ds.data_vars) == 1:
            return [get_name_of_first_var(ds)]
        else:
            return find_standard_vars(ds)


def find_standard_vars(ds: Dataset) -> list[Hashable]:
    return [
        v
        for v in ds.data_vars
        if StandardVariableRegistry.lookup(str(v), no_error=True) is not None
    ]


def guess_input_type(data: DataArray) -> StandardVariable | None:
    cf_input = StandardVariableRegistry.lookup(str(data.name), no_error=True)
    if cf_input is None and data.attrs.get("standard_name", None) is not None:
        cf_input = StandardVariableRegistry.lookup(
            data.attrs.get("standard_name"), no_error=True
        )
    if cf_input is None:
        return None
    return cf_input


def build_studied_data(
    original_da: DataArray,
    time_range: Sequence[str] | None,
    ignore_Feb29th: bool,
    standard_var: StandardVariable | None,
) -> DataArray:
    if time_range is not None:
        check_time_range_pre_validity("time_range", time_range)
        time_range = [get_date_to_iso_format(x) for x in time_range]
        da = original_da.sel(time=slice(time_range[0], time_range[1]))
        check_time_range_post_validity(da, original_da, "time_range", time_range)
        if len(da.time) == 0:
            raise InvalidIcclimArgumentError(
                f"The given `time_range` {time_range} is out of the dataset time"
                f" period: {original_da.time.min().dt.floor('D').values}"
                f" - {original_da.time.max().dt.floor('D').values}."
            )
    else:
        da = original_da
    if ignore_Feb29th:
        da = xclim.core.calendar.convert_calendar(da, CfCalendarRegistry.NO_LEAP.name)
    if da.attrs.get(UNITS_KEY, None) is None and standard_var is not None:
        da.attrs[UNITS_KEY] = standard_var.default_units
    if is_precipitation_amount(da):
        da = xclim.core.units.amount2rate(da)
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


def _is_alias_valid(ds, alias) -> bool:
    for ds_var in ds.data_vars:
        if str(ds_var).upper() == alias.upper():
            return True
    return False


def _get_actual_name(ds, alias) -> str:
    for ds_var in ds.data_vars:
        if str(ds_var).upper() == alias.upper():
            return str(ds_var)
    raise KeyError(f"Could not find {alias} in dataset.")


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
                threshold_min_value = convert_units_to(
                    threshold_min_value, thresh_da, context="hydro"
                )
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
    percentile_min_value: Quantity | None,
) -> DataArray:
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
    if only_leap_years:
        reference = reduce_only_leap_years(original_da)
    if percentile_min_value is not None:
        percentile_min_value = convert_units_to(
            str(percentile_min_value), reference, context="hydro"
        )
        reference = reference.where(reference >= percentile_min_value, np.nan)
    return reference

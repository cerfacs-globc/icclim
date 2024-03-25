"""Module to parse input data and make it usable for icclim."""

from __future__ import annotations

import re
import warnings
from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np
import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from xclim.core.units import convert_units_to

from icclim._core.constants import UNITS_KEY, VALID_PERCENTILE_DIMENSION
from icclim._core.model.cf_calendar import CfCalendarRegistry
from icclim._core.model.standard_variable import (
    StandardVariable,
    StandardVariableRegistry,
)
from icclim._core.utils import read_date
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    from collections.abc import Hashable
    from datetime import datetime

    import pint
    from pint import Quantity

    from icclim._core.model.icclim_types import InFileBaseType, InFileLike
    from icclim._core.model.in_file_dictionary import InFileDictionary
    from icclim._core.model.standard_index import StandardIndex
    from icclim._core.model.threshold import Threshold


DEFAULT_INPUT_FREQUENCY = "days"
PR_AMOUNT_STANDARD_NAME = "thickness_of_rainfall_amount"


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
        cls,
        source: xr.DataArray,
        climatology_bounds: list[str] | None = None,
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
            msg = "PercentileDataArray needs a climatology_bounds."
            raise ValueError(msg)
        per = cls(source)
        # handle case where da was created with `quantile()` method
        if "quantile" in source.coords:
            per = per.rename({"quantile": "percentiles"})
            per.coords["percentiles"] = per.coords["percentiles"] * 100
        clim_bounds = source.attrs.get("climatology_bounds", climatology_bounds)
        per.attrs["climatology_bounds"] = clim_bounds
        if "percentiles" in per.coords:
            return per
        msg = (
            f"DataArray {source.name} could not be turned into"
            f" PercentileDataArray. The DataArray must have a"
            f" 'percentiles' coordinate variable."
        )
        raise ValueError(msg)


def guess_var_names(
    ds: Dataset,
    var_names: str | Sequence[str] | None,
    standard_index: StandardIndex | None,
) -> list[Hashable]:
    """
    Attempt to guess the variable names from the dataset and the standard index.

    Parameters
    ----------
    ds : Dataset
        The dataset to guess the variable names from.
    var_names : str | Sequence[str] | None
        The variable names to use. If None, the function will attempt to guess the
        variable names.
    standard_index : StandardIndex | None
        The standard index to use to guess the variable names.

    Returns
    -------
    list[Hashable]
        The list of guessed variable names.
    """
    if var_names is None:
        return _guess_dataset_var_names(ds=ds, standard_index=standard_index)
    if isinstance(var_names, str):
        return [var_names]
    if isinstance(var_names, (list, tuple)):
        return var_names
    msg = "`var_name` must be a string a list or None."
    raise NotImplementedError(msg)


def read_dataset(
    in_files: InFileBaseType,
    standard_var: StandardVariable | None = None,
    var_name: str | Sequence[str] | None = None,
) -> Dataset:
    """
    Read a dataset from input files.

    Parameters
    ----------
    in_files : InFileBaseType
        The input files to read the dataset from. It can be a single file path,
        a list of file paths, a glob pattern, a netCDF file, or a Zarr store.
    standard_var : StandardVariable | None, optional
        The standard variable to use for parsing the dataset, by default None.
    var_name : str | Sequence[str] | None, optional
        The variable name(s) to extract from the dataset, by default None.

    Returns
    -------
    Dataset
        The parsed dataset.

    Raises
    ------
    NotImplementedError
        If the format of `in_files` is not recognized.

    Notes
    -----
    This function supports reading datasets from various file formats, including
    netCDF and Zarr. It can handle single files, multiple files, and glob patterns.
    If `standard_var` is provided, it will use the specified standard variable for
    parsing the dataset. If `var_name` is provided, it will extract the specified
    variable(s) from the dataset.

    Examples
    --------
    >>> files = ["data1.nc", "data2.nc"]
    >>> ds = read_dataset(files, standard_var="temperature", var_name="temp")
    """
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
        # TODO @bzah: change parallel to True when issue is fixed on netcdf4 (py and C)
        # https://github.com/Unidata/netcdf4-python/issues/1192
        ds = xr.open_mfdataset(in_files, parallel=False, join="override")
    elif is_netcdf_path(in_files):
        ds = xr.open_dataset(in_files)
    elif is_zarr_path(in_files):
        ds = xr.open_zarr(in_files)
    elif isinstance(in_files, (list, tuple)):
        return xr.merge(
            [
                read_dataset(in_file, standard_var, var_name[i])
                for i, in_file in enumerate(in_files)
            ],
        )
    else:
        msg = f"`in_files` format {type(in_files)} was not recognized."
        raise NotImplementedError(msg)
    return update_to_standard_coords(ds)


def update_to_standard_coords(ds: Dataset) -> Dataset:
    """Mutate input ds to use more icclim friendly coordinate names."""
    # TODO @bzah: see if cf-xarray could replace this
    # https://github.com/cerfacs-globc/icclim/issues/289
    if ds.coords.get("t") is not None:
        ds = ds.rename({"t": "time"})
    return ds


def is_zarr_path(path: InFileBaseType) -> bool:
    """Check if the input path is a Zarr store."""
    return isinstance(path, str) and ".zarr" in path


def is_netcdf_path(path: InFileBaseType) -> bool:
    """Check if the input path is a netCDF file."""
    return isinstance(path, str) and ".nc" in path


def is_glob_path(path: InFileBaseType) -> bool:
    """Check if the input path is a glob pattern."""
    return isinstance(path, str) and "*" in path


def standardize_percentile_dim_name(per_da: DataArray) -> DataArray:
    """
    Standardizes the name of the percentile dimension in the input DataArray.

    Parameters
    ----------
    per_da : DataArray
        The input DataArray containing percentile data.

    Returns
    -------
    DataArray
        The input DataArray with the percentile dimension standardized.

    Raises
    ------
    InvalidIcclimArgumentError
        If the percentile data does not contain a recognizable percentiles dimension.

    Notes
    -----
    This function standardizes the name of the percentile dimension in the input
    DataArray to "percentiles".

    If the percentile dimension name contains the word "quantile", the values in the
    "percentiles" coordinate are multiplied by 100.
    """
    per_dim_name = None
    for d in VALID_PERCENTILE_DIMENSION:
        if d in per_da.dims:
            per_dim_name = d
        elif f"{d}s" in per_da.dims:
            # plural handling
            per_dim_name = f"{d}s"
    if per_dim_name is None:
        msg = (
            "Percentile data must contain a recognizable percentiles dimension such as"
            " 'percentiles', 'quantile', 'per' or 'centile'."
        )
        raise InvalidIcclimArgumentError(msg)
    per_da = per_da.rename({per_dim_name: "percentiles"})
    if "quantile" in per_dim_name:
        per_da.coords["percentiles"] = per_da.coords["percentiles"] * 100
    return per_da


def get_date_to_iso_format(in_date: str | datetime) -> str:
    """
    Get a date in ISO format from a string or a datetime object.

    Parameters
    ----------
    in_date: str | datetime
        A string representing a date or a datetime object.

    Returns
    -------
    str
        A string representing a date in ISO format.
    """
    if isinstance(in_date, str):
        if re.match(r"^\d{4}$", in_date):
            warnings.warn(
                f"{in_date} is transformed into {in_date}-01-01",
                stacklevel=2,
            )
            in_date += "-01-01"
        if re.match(r"^\d{4}-\d{2}$", in_date):
            warnings.warn(f"{in_date} is transformed into {in_date}-01", stacklevel=2)
            in_date += "-01"
        in_date = read_date(in_date)
    return in_date.strftime("%Y-%m-%d")


def read_clim_bounds(
    climatology_bounds: Sequence[str, str] | None,
    per_da: xr.DataArray,
) -> list[str]:
    """
    Read climatology bounds from input.

    The climatology bounds represent the start and end dates of the climatology period.

    Parameters
    ----------
    climatology_bounds : sequence of str or None
        The climatology bounds as a sequence of two strings representing the start and
        end dates.
        If None, the climatology bounds will be retrieved from the `climatology_bounds`
        attribute of `per_da`.
    per_da : xr.DataArray
        The input data array.

    Returns
    -------
    list of str
        A list of climatology bounds converted to ISO format.

    Raises
    ------
    InvalidIcclimArgumentError
        If the length of `climatology_bounds` is not equal to 2.

    Notes
    -----
    If `climatology_bounds` is None, the function will attempt to retrieve the
    climatology bounds from the `climatology_bounds` attribute of `per_da`.
    """
    bds = climatology_bounds or per_da.attrs.get("climatology_bounds", None)
    if len(bds) != 2:
        msg = "climatology_bounds must be an iterable of length 2."
        raise InvalidIcclimArgumentError(msg)
    return [get_date_to_iso_format(bd) for bd in bds]


def build_input_dict(
    in_files: InFileLike,
    var_names: Sequence[str] | None,
    threshold: Threshold | Sequence[Threshold] | None,
    standard_index: StandardIndex | None,
) -> dict[str, InFileDictionary]:
    """
    Build an input dictionary based on the provided input files and variables.

    The input dictionary is used to map which input files correspond to which variables.

    Parameters
    ----------
    in_files : InFileLike
        The input files. It can be a dictionary where the keys represent the variable
        names and the values represent the file paths, or a single file path.
    var_names : Sequence[str] | None
        The variable names. If `in_files` is a dictionary, this parameter must be None.
        Otherwise, it should be a sequence of variable names corresponding to the single
        file path.
    threshold : Threshold | Sequence[Threshold] | None
        The threshold values. It can be a single threshold value, a sequence of
        threshold values, or None.
    standard_index : StandardIndex | None
        The standard index. It can be a standard index value or None.

    Returns
    -------
    dict[str, InFileDictionary]
        The built input dictionary.

    Raises
    ------
    InvalidIcclimArgumentError
        If `var_names` is not None when `in_files` is a dictionary.

    Notes
    -----
    - If `in_files` is a dictionary, the dictionary keys are used as variable names.
    - If `in_files` is a dictionary and the dictionary values are also dictionaries,
      the input dictionary is returned as is.
    - If `in_files` is a dictionary and the dictionary values are file paths,
      the input dictionary is built using the file paths and variable names.
    - If `in_files` is a single file path and `var_names` is a single variable name,
      the input dictionary is built using the file path and variable name.
    """
    if isinstance(in_files, dict):
        if var_names is not None:
            msg = (
                "`var_name` must be None when `in_files` is a dictionary."
                " The dictionary keys are used in place of `var_name`."
            )
            raise InvalidIcclimArgumentError(msg)
        if isinstance(next(iter(in_files.values())), dict):
            # case of in_files={tasmax: {"study": "tasmax.nc"}}
            return in_files
        # case of in_files={tasmax: "tasmax.nc"}
        return _build_in_file_dict(
            in_files=list(in_files.values()),
            standard_index=standard_index,
            threshold=threshold,
            var_names=list(in_files.keys()),
        )
    # case of in_files="tasmax.nc" and var_names="tasmax"
    return _build_in_file_dict(in_files, var_names, threshold, standard_index)


def find_standard_vars(ds: Dataset) -> list[Hashable]:
    """
    Find standard variables in a dataset.

    Parameters
    ----------
    ds : Dataset
        The input dataset.

    Returns
    -------
    list[Hashable]
        A list of standard variables found in the dataset.
    """
    return [
        v
        for v in ds.data_vars
        if StandardVariableRegistry.lookup_no_error(str(v)) is not None
    ]


def guess_standard_variable(data: DataArray) -> StandardVariable | None:
    """
    Guesses the standard variable based on the metadata of `data`.

    Parameters
    ----------
    data : DataArray
        The input data.

    Returns
    -------
    StandardVariable or None
        The guessed standard variable, or None if no standard variable is found.

    Notes
    -----
    StandardVariableRegistry is used as a lookup table to find the standard variable
    using the dataarray name or standard name attribute.
    """
    std_var = StandardVariableRegistry.lookup_no_error(str(data.name))
    if std_var is None and data.attrs.get("standard_name", None) is not None:
        std_var = StandardVariableRegistry.lookup(
            data.attrs.get("standard_name"),
            no_error=True,
        )
    if std_var is None:
        return None
    return std_var


def is_precipitation_amount(source: xr.DataArray) -> bool:
    """
    Return True if the source is a precipitation amount.

    Parameters
    ----------
    source: xr.DataArray
        A DataArray object.

    Returns
    -------
    bool
        True if the source is a precipitation amount, False otherwise.

    Notes
    -----
    Using pint, the rate is a quantity with a dimensionality of [time]^-1.
    """
    standard_name = source.attrs.get("standard_name", None)
    source_unit = xclim.core.units.units2pint(source)
    return standard_name == PR_AMOUNT_STANDARD_NAME and _is_amount(source_unit)


def build_studied_data(
    original_da: DataArray,
    time_range: Sequence[datetime | str] | None,
    ignore_Feb29th: bool,  # noqa: N803
    default_units: str | None,
) -> DataArray:
    """
    Preprocesss the input data to select the period of interest.

    Parameters
    ----------
    original_da : DataArray
        The original data array.
    time_range : Sequence[datetime | str] | None
        The time range to select from the data array. If None, the entire time range is
        used.
    ignore_Feb29th : bool
        Whether to ignore February 29th when processing the data.
    default_units : str | None
        The default units to use for the data array if it is uniteless.
        If None and the data array is uniteless, "units" attribute remains unset.

    Returns
    -------
    DataArray
        The processed data array.

    Raises
    ------
    InvalidIcclimArgumentError
        If the given `time_range` is out of the dataset time period.

    """
    if time_range is not None:
        _check_time_range_pre_validity("time_range", time_range)
        time_range = [get_date_to_iso_format(x) for x in time_range]
        da = original_da.sel(time=slice(time_range[0], time_range[1]))
        _check_time_range_post_validity(da, original_da, "time_range", time_range)
        if len(da.time) == 0:
            msg = (
                f"The given `time_range` {time_range} is out of the dataset time"
                f" period: {original_da.time.min().dt.floor('D').values}"
                f" - {original_da.time.max().dt.floor('D').values}."
            )
            raise InvalidIcclimArgumentError(msg)
    else:
        da = original_da
    if ignore_Feb29th:
        da = xclim.core.calendar.convert_calendar(da, CfCalendarRegistry.NO_LEAP.name)
    if da.attrs.get(UNITS_KEY, None) is None and default_units is not None:
        da.attrs[UNITS_KEY] = default_units
    if is_precipitation_amount(da):
        da = xclim.core.units.amount2rate(da)
    return da.chunk("auto")


def get_name_of_first_var(ds: Dataset) -> str:
    """
    Get the name of the first variable in the given Dataset.

    Parameters
    ----------
    ds : Dataset
        The input Dataset.

    Returns
    -------
    str
        The name of the first variable in the Dataset.

    Raises
    ------
    IndexError
        If the Dataset is empty.
    """
    return str(ds.data_vars[next(iter(ds.data_vars.keys()))].name)


def is_dataset_path(query: InFileBaseType) -> bool:
    """
    Check if the given query is a valid dataset path.

    Parameters
    ----------
    query : InFileBaseType
        The query to check. It can be a single path or a list/tuple of paths.

    Returns
    -------
    bool
        True if the query is a valid dataset path, False otherwise.

    Notes
    -----
    A valid dataset path can be either a NetCDF path, a Zarr path, a glob path, or a
    list/tuple of valid paths.

    """
    if isinstance(query, (tuple, list)):
        return all(is_netcdf_path(q) for q in query)
    return is_zarr_path(query) or is_glob_path(query) or is_netcdf_path(query)


def build_reference_da(
    original_da: DataArray,
    base_period_time_range: Sequence[datetime | str] | None,
    only_leap_years: bool,
    percentile_min_value: Quantity | None,
) -> DataArray:
    """
    Build a reference DataArray to be used for percentile doy computation.

    Parameters
    ----------
    original_da: DataArray
        The DataArray used as a base.
    base_period_time_range: Sequence[datetime | str] | None
        The period to slice in the base DataArray.
    only_leap_years: bool
        Flag to only use leap years (years with 366 days).
    percentile_min_value: Quantity | None
        Optional, if set will replace every value from the base DataArray that are below
        the `percentile_min_value` with np.nan.
    """
    reference = original_da
    if base_period_time_range:
        _check_time_range_pre_validity("base_period_time_range", base_period_time_range)
        base_period_time_range = [
            get_date_to_iso_format(x) for x in base_period_time_range
        ]
        reference = original_da.sel(
            time=slice(base_period_time_range[0], base_period_time_range[1]),
        )
        _check_time_range_post_validity(
            reference,
            original_da,
            "base_period_time_range",
            base_period_time_range,
        )
    if only_leap_years:
        reference = _reduce_only_leap_years(original_da)
    if percentile_min_value is not None:
        percentile_min_value = convert_units_to(
            str(percentile_min_value),
            reference,
            context="hydro",
        )
        reference = reference.where(reference >= percentile_min_value, np.nan)
    return reference


def get_dataarray_from_dataset(
    var_name: str | None,
    value: xr.Dataset | str,
    standard_var: StandardVariable | None = None,
) -> xr.DataArray:
    """
    Extract a DataArray from a Dataset based on the provided variable name.

    Parameters
    ----------
    var_name : str or None
        The name of the variable to extract from the Dataset. If None, the function
        will try to guess the variable based on the Dataset's contents.
    value : xr.Dataset or str
        The Dataset object or the path to the Dataset file.
    standard_var : StandardVariable
        The standard variable used to find a matching variable in the Dataset.

    Returns
    -------
    xr.DataArray
        The extracted DataArray.

    Raises
    ------
    InvalidIcclimArgumentError
        If the variable name cannot be guessed and `var_name` is None.

    Notes
    -----
    This function can be used to extract a specific variable from a Dataset object
    or a Dataset file. If `var_name` is None, the function will try to guess the
    variable based on the Dataset's contents.
    """
    ds = (
        value
        if isinstance(value, xr.Dataset)
        else read_dataset(value, standard_var=standard_var)
    )
    if var_name is not None:
        return ds[var_name]
    if len(ds.data_vars) == 1:
        return ds[get_name_of_first_var(ds)]
    matching_name = _find_matching_standard_var(ds, standard_var)
    if matching_name is not None:
        return ds[matching_name]
    names = find_standard_vars(ds)
    if len(names) == 1:
        return ds[var_name]
    msg = (
        f"Could not guess the variable to use for the normal in {ds}."
        f" Use `normal_var_name` to specify which variable should be"
        f" used."
    )
    raise InvalidIcclimArgumentError(msg)


def _build_in_file_dict(
    in_files: InFileBaseType,
    var_names: Sequence[str],
    threshold: Threshold | Sequence[Threshold] | None,
    standard_index: StandardIndex | None,
) -> InFileDictionary:
    standard_var = (
        standard_index.input_variables[0] if standard_index is not None else None
    )
    input_dataset = read_dataset(
        in_files=in_files,
        standard_var=standard_var,
        var_name=var_names,
    )
    var_names = guess_var_names(
        ds=input_dataset,
        standard_index=standard_index,
        var_names=var_names,
    )
    if threshold is not None:
        if len(var_names) == 1:
            return {
                var_names[0]: {
                    "study": input_dataset[var_names[0]],
                    "thresholds": threshold,
                },
            }
        if not isinstance(threshold, Sequence):
            threshold = [threshold]
        if len(threshold) != len(var_names):
            # Allow 1 var with multiple thresholds or 1 threshold per var
            # but no other case
            msg = (
                "There must be as many thresholds as there are variables. There was"
                f" {len(threshold)} thresholds and {len(var_names)} variables."
            )
            raise InvalidIcclimArgumentError(msg)
        return {
            var_name: {"study": input_dataset[var_name], "thresholds": threshold[i]}
            for i, var_name in enumerate(var_names)
        }
    return {var_name: {"study": input_dataset[var_name]} for var_name in var_names}


def _read_dataarray(
    data: DataArray,
    standard_var: StandardVariable | None = None,
    var_name: str | Sequence[str] | None = None,
) -> Dataset:
    if isinstance(var_name, (tuple, list)):
        if len(var_name) > 1:
            msg = (
                "When `in_file` is a DataArray, there"
                f" can only be one value in `var_name` but var_name was: {var_name} "
            )
            raise InvalidIcclimArgumentError(msg)
        var_name = var_name[0]
        data_name = var_name or standard_var.short_name or None
    else:
        data_name = var_name or data.name or "unnamed_var"
    return data.to_dataset(name=data_name, promote_attrs=True)


def _guess_dataset_var_names(
    standard_index: StandardIndex,
    ds: Dataset,
) -> list[Hashable]:
    """Try to guess the variable names.

    The expected kind of variable of the index is used to guess the variable names.
    """
    if standard_index is not None:
        main_aliases = ", ".join(
            (v.short_name for v in standard_index.input_variables),
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
    if len(ds.data_vars) == 1:
        return [get_name_of_first_var(ds)]
    return find_standard_vars(ds)


def _check_time_range_pre_validity(key: str, tr: Sequence[datetime | str]) -> None:
    if len(tr) != 2:
        msg = (
            f"The given `{key}` {tr}"
            f" has {len(tr)} elements."
            f" It must have exactly 2 dates."
        )
        raise InvalidIcclimArgumentError(msg)


def _check_time_range_post_validity(
    da: DataArray, original_da: DataArray, key: str, tr: list
) -> None:
    if len(da.time) == 0:
        msg = (
            f"The given `{key}` {tr} is out of the sample time bounds:"
            f" {original_da.time.min().dt.floor('D').values}"
            f" - {original_da.time.max().dt.floor('D').values}."
        )
        raise InvalidIcclimArgumentError(msg)


def _is_alias_valid(ds: Dataset, alias: str) -> bool:
    return any(str(ds_var).upper() == alias.upper() for ds_var in ds.data_vars)


def _get_actual_name(ds: Dataset, alias: str) -> str:
    for ds_var in ds.data_vars:
        if str(ds_var).upper() == alias.upper():
            return str(ds_var)
    msg = f"Could not find {alias} in dataset."
    raise KeyError(msg)


def _reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        msg = "No leap year in current dataset. Do not use `only_leap_years` parameter."
        raise InvalidIcclimArgumentError(msg)
    return xr.concat(reduced_list, "time")


def _is_rate(u: pint.Unit) -> bool:
    return u.dimensionality.get("[time]") == -1


def _is_amount(u: pint.Unit) -> bool:
    return not _is_rate(u)


def _find_matching_standard_var(ds: xr.Dataset, std: StandardVariable) -> str | None:
    for v in ds.data_vars:
        standardized_var = StandardVariableRegistry.lookup_no_error(str(v))
        if std == standardized_var:
            return str(v)
    return None

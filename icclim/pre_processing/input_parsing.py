from __future__ import annotations

from typing import Callable, Dict, List, TypedDict, Union

import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from xclim.core.utils import PercentileDataArray

from icclim.ecad.ecad_indices import EcadIndex
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendar
from icclim.models.cf_variable import CfVariable
from icclim.models.climate_index import ClimateIndex
from icclim.models.constants import VALID_PERCENTILE_DIMENSION
from icclim.models.frequency import Frequency
from icclim.models.index_group import IndexGroup
from icclim.utils import get_date_to_iso_format

# zarr or netcdf, or list of netcdf or xarray struct
InFileBaseType = Union[str, List[str], Dataset, DataArray]


class InFileDictionary(TypedDict, total=False):
    """Dictionary grouping in_files and var_name functionnalities.
    It also allows to use a different input for percentiles.

    Examples
    --------

    >>> in_files = {
    ...    "tasmax": { "study": "tasmax-store.zarr",
    ...                "thresholds": ["per-1.nc", "per-2.nc"],
    ...                "climatology_bounds":['1990-01-01', '1991-12-31'],
    ...                "per_var_name":"tas_max_per" },
    ...    "pr": "pr.nc",
    ...    "tasmin": {"study": "tasmin.nc"},
    ...     }
    """

    study: InFileBaseType
    thresholds: InFileBaseType | None
    climatology_bounds: tuple[str, str] | list[str] | None  # may be guessed if missing
    per_var_name: str | None  # may be guessed if missing


InFileType = Union[Dict[str, Union[InFileDictionary, InFileBaseType]], InFileBaseType]


def guess_var_names(
    ds: Dataset,
    in_data: InFileType | None = None,
    index: ClimateIndex | None = None,
    var_names: str | list[str] | None = None,
) -> list[str]:
    if isinstance(in_data, dict):
        # case InFileDictionary
        if var_names is not None:
            raise InvalidIcclimArgumentError(
                "When `in_files` is a dictionary, `var_name` must be empty."
                " The dictionary's keys are the expected variable names."
            )
        return list(in_data.keys())
    elif var_names is None:
        if index is None:
            raise InvalidIcclimArgumentError(
                "Unable to guess variable name." " Provide one using `var_name`"
            )
        return _guess_dataset_var_names(index, ds)
    elif isinstance(var_names, str):
        return [var_names]
    elif isinstance(var_names, list):
        return var_names
    else:
        raise NotImplementedError("`var_name` must be a string a list or None.")


def read_dataset(
    in_data: InFileType,
    index: EcadIndex = None,
    var_name: str | list[str] = None,  # used only if input is a DataArray
) -> Dataset:
    if isinstance(in_data, dict):
        return _read_dictionary(in_data, index)
    elif isinstance(in_data, Dataset):
        return in_data
    elif isinstance(in_data, DataArray):
        return _read_dataarray(in_data, index, var_name=var_name)
    elif isinstance(in_data, list):
        # we assumes it's a list of netCDF files
        return xr.open_mfdataset(in_data, parallel=True)
    elif is_netcdf(in_data):
        return xr.open_dataset(in_data)
    elif is_zarr(in_data):
        return xr.open_zarr(in_data)
    else:
        raise NotImplementedError("`in_files` format was not recognized.")


def build_cf_variables(
    var_names: list[str],
    ds: Dataset,
    time_range: list[str] | None,
    ignore_Feb29th: bool,
    base_period_time_range: list[str] | None,
    only_leap_years: bool,
    freq: Frequency,
) -> list[CfVariable]:
    return [
        _build_cf_variable(
            ds=ds,
            name=var_name,
            time_range=time_range,
            ignore_Feb29th=ignore_Feb29th,
            base_period_time_range=base_period_time_range,
            only_leap_years=only_leap_years,
            time_clipping=freq.time_clipping,
        )
        for var_name in var_names
    ]


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


def is_zarr(data: InFileBaseType):
    return isinstance(data, str) and ".nc" not in data


def is_netcdf(data: InFileBaseType):
    return isinstance(data, str) and ".nc" in data


def _read_dictionary(in_data, index):
    ds_acc = []
    for climate_var_name, climate_var_data in in_data.items():
        if isinstance(climate_var_data, dict):
            study_ds = read_dataset(climate_var_data["study"], index, climate_var_name)
            if climate_var_data.get("thresholds", None) is not None:
                ds_acc.append(_read_thresholds(climate_var_data, climate_var_name))
        else:
            study_ds = read_dataset(climate_var_data, index, climate_var_name)
        ds_acc.append(study_ds)
    return xr.merge(ds_acc)


def _read_thresholds(climate_var_data: InFileDictionary, climate_var_name: str):
    per_ds = read_dataset(climate_var_data["thresholds"], index=None)
    per_var_name = _get_percentile_var_name(per_ds, climate_var_data, climate_var_name)
    per_da = per_ds[per_var_name].rename(f"{climate_var_name}_thresholds")
    per_da = _standardize_percentile_dim_name(per_da)
    per_da = PercentileDataArray.from_da(
        per_da,
        climatology_bounds=_read_clim_bounds(climate_var_data, per_da),
    )
    return per_da


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


def _read_clim_bounds(input_dict: InFileDictionary, per_da: DataArray) -> list[str]:
    bds = input_dict.get("climatology_bounds", None) or per_da.attrs.get(
        "climatology_bounds", None
    )
    if len(bds) != 2:
        raise InvalidIcclimArgumentError(
            "climatology_bounds must be a iterable of length 2."
        )
    return [d for d in map(lambda bd: get_date_to_iso_format(bd), bds)]


def _read_dataarray(
    data: DataArray, index: EcadIndex = None, var_name: str | list[str] = None
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
        if len(index.input_variables) > 1:
            raise InvalidIcclimArgumentError(
                f"Index {index.name} needs {len(index.input_variables)} variables."
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
    if len(ds.data_vars) == 1:
        if len(index_expected_vars) != 1:
            raise get_error()
        return [_get_name_of_first_var(ds)]
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


def _has_percentile_variable(ds: Dataset, name: str) -> bool:
    # fixme: Not the best to use a string (the name) to identify percentiles data
    return f"{name}_thresholds" in ds.data_vars


def _build_cf_variable(
    ds: Dataset,
    name: str,
    time_range: list[str] | None,
    ignore_Feb29th: bool,
    base_period_time_range: list[str] | None,
    only_leap_years: bool,
    time_clipping: Callable,
) -> CfVariable:
    if len(ds.data_vars) == 1:
        da = ds[_get_name_of_first_var(ds)]
    else:
        da = ds[name]
    study_da = _build_study_da(da, time_range, ignore_Feb29th)
    if _has_percentile_variable(ds, name):
        if base_period_time_range is not None:
            raise InvalidIcclimArgumentError(
                "Cannot determine the data to use for percentiles when both"
                " `base_period_time_range` and an in_files `thresholds` are given."
                " Please fill only one of the two."
            )
        reference_da = PercentileDataArray.from_da(ds[f"{name}_thresholds"])
    elif base_period_time_range is not None:
        reference_da = _build_reference_da(da, base_period_time_range, only_leap_years)
    else:
        reference_da = study_da
    if time_clipping is not None:
        study_da = time_clipping(study_da)
        reference_da = time_clipping(reference_da)
    # TODO: all these pre-processing operations should probably be added in history
    #       metadata or
    #       provenance it could be a property in CfVariable which will be reused when we
    #       update the metadata of the index, at the end.
    #       We could have a singleton "taking notes" of each operation that must be
    #       logged into the output netcdf/provenance/metadata
    return CfVariable(name, study_da, reference_da)


def _build_study_da(
    original_da: DataArray, time_range: list[str] | None, ignore_Feb29th: bool
) -> DataArray:
    if time_range is not None:
        _check_time_range_pre_validity("time_range", time_range)
        time_range = [get_date_to_iso_format(x) for x in time_range]
        da = original_da.sel(time=slice(time_range[0], time_range[1]))
        _check_time_range_post_validity(da, original_da, "time_range", time_range)
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
    return da


def _build_reference_da(
    original_da: DataArray,
    base_time_range: list[str],
    only_leap_years: bool,
) -> DataArray:
    _check_time_range_pre_validity("base_period_time_range", base_time_range)
    base_time_range = [get_date_to_iso_format(x) for x in base_time_range]
    da = original_da.sel(time=slice(base_time_range[0], base_time_range[1]))
    _check_time_range_post_validity(
        da, original_da, "base_period_time_range", base_time_range
    )
    if only_leap_years:
        da = _reduce_only_leap_years(original_da)
    return da


def _reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use `only_leap_years` parameter."
        )
    return xr.concat(reduced_list, "time")


def _check_time_range_pre_validity(key: str, tr: list) -> None:
    if len(tr) != 2:
        raise InvalidIcclimArgumentError(
            f"The given `{key}` {tr}"
            f" has {len(tr)} elements."
            f" It must have exactly 2 dates."
        )


def _check_time_range_post_validity(da, original_da, key: str, tr: list) -> None:
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


def _get_percentile_var_name(
    per_ds: Dataset, in_dict: InFileDictionary, climate_var_name: str
) -> str:
    if per_var_name := in_dict.get("per_var_name", None):
        return per_var_name
    elif len(per_ds.data_vars) == 1:
        return _get_name_of_first_var(per_ds)
    else:
        return _guess_per_var_name(climate_var_name, per_ds)


def _guess_per_var_name(climate_var_name: str, per_ds: Dataset) -> str:
    data_var_names = map(lambda v: str(v.name), per_ds.data_vars)
    for x in data_var_names:
        if climate_var_name in x:
            return x
    raise InvalidIcclimArgumentError(
        "Could not guess the variable name for percentiles"
        f" of {climate_var_name}. Please, provide the"
        f" explicite name using per_var_name like so:"
        f" \u007bf'{climate_var_name}':"
        f" \u007b'study': 'x.nc',"
        f" 'percentiles': 'y.nc',"
        f" per_var_name='{climate_var_name}_percentiles'"
        f" \u007d\u007d"
    )


def _get_name_of_first_var(ds: Dataset) -> str:
    return str(ds.data_vars[list(ds.data_vars.keys())[0]].name)

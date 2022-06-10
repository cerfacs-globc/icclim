from __future__ import annotations

from typing import Callable, Dict, Hashable, List, TypedDict, Union

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
    ...                "percentiles": ["per-1.nc", "per-2.nc"],
    ...                "climatology_bounds":['1990-01-01', '1991-12-31'],
    ...                "per_var_name":"tas_max_per" },
    ...    "pr": "pr.nc"
    ...     }
    """

    study: InFileBaseType
    percentiles: InFileBaseType | None
    climatology_bounds: tuple[str, str] | list[str] | None
    per_var_name: str | None


InFileType = Union[Dict[str, Union[InFileDictionary, InFileBaseType]], InFileBaseType]


def guess_var_names(
    in_data: dict[str, InFileDictionary | InFileBaseType] | InFileBaseType,
    ds: Dataset,
    index: ClimateIndex | None = None,
    var_names: str | list[str] | None = None,
) -> list[str]:
    if isinstance(in_data, dict):
        if var_names is not None:
            raise InvalidIcclimArgumentError(
                "When `in_files` is a dictionary, `var_name` must be empty."
                " The dictionary's keys are the expected variable names."
            )
        return list(in_data.keys())
    elif var_names is None:
        return _guess_variable_names(index, ds)
    elif isinstance(var_names, str):
        return [var_names]
    elif isinstance(var_names, list):
        return var_names


def read_multiple(
    in_data: InFileType,
    index: EcadIndex | None = None,
    var_names: str | list[str] | None = None,
) -> Dataset:
    if isinstance(in_data, dict):
        ds_acc = []
        for climate_var, data in in_data.items():
            if isinstance(in_data, dict):
                data: InFileDictionary
                ds_acc.append(read_dataset(data["study"], index, climate_var))
                if data.get("percentiles", None) is not None:
                    per_ds = read_dataset(
                        data["percentiles"],
                        index=None,
                        var_names=f"{climate_var}_percentiles",
                    )
                    per_da = per_ds[_get_percentile_var_name(per_ds, data, climate_var)]
                    # TODO: Maybe we should construct the CfVariable here
                    #       to avoid relying on a string to retrieve the percentiles
                    #       later.
                    per_da = per_da.rename(f"{climate_var}_percentiles")
                    per_da = _standardize_percentile_dim_name(per_da)
                    per_da = PercentileDataArray.from_da(
                        per_da, climatology_bounds=_read_clim_bounds(data, per_da)
                    )
                    ds_acc.append(per_da)  # todo make sure it works to merge da and ds
            else:
                data: InFileBaseType
                ds_acc.append(read_dataset(data, index, climate_var))
        return xr.merge(ds_acc)
    return read_dataset(in_data, index, var_names)


def read_dataset(
    data: InFileBaseType,
    index: EcadIndex | None = None,
    var_names: str | list[str] | None = None,
) -> Dataset:
    if isinstance(data, Dataset):
        return data
    elif isinstance(data, DataArray):
        return _read_dataarray(data, index, var_names)
    elif isinstance(data, list):
        # we assumes it's a list of netCDF files
        return xr.open_mfdataset(data, parallel=True)
    elif is_netcdf(data):
        return xr.open_dataset(data)
    elif is_zarr(data):
        return xr.open_zarr(data)
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
    data: InFileBaseType,
    index: EcadIndex | None = None,
    var_names: str | list[str] | None = None,
) -> Dataset:
    if isinstance(var_names, list) and len(var_names) > 1:
        raise InvalidIcclimArgumentError(
            "When the input is a DataArray, var_name must be a string."
        )
    if var_names is None:
        if index is not None and len(index.input_variables) > 1:
            raise InvalidIcclimArgumentError(
                f"Index {index.name} needs {len(index.input_variables)} variables."
                f" Please provide them with an xarray.Dataset, netCDF file(s) or a"
                f" zarr store."
            )
        # first alias of the unique variable
        data_name = index.input_variables[0][0]
    elif isinstance(var_names, list):
        data_name = var_names[0]
    else:
        data_name = var_names
    return data.to_dataset(name=data_name, promote_attrs=True)


def _guess_variable_names(index: ClimateIndex, ds: Dataset) -> list[str]:
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
        return [str(ds.data_vars[0].name)]
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


def _guess_per_var_name(climate_var_name: str, per_ds: Dataset) -> Hashable:
    for x in map(lambda v: str(v.name), per_ds.data_vars):
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


def _has_percentile_variable(ds: Dataset, name: str) -> bool:
    # fixme: Not the best to use a string (the name) to identify percentiles data
    return f"{name}_percentiles" in ds.data_vars


def _build_cf_variable(
    ds: Dataset,
    name: str,
    time_range: list[str] | None,
    ignore_Feb29th: bool,
    base_period_time_range: list[str] | None,
    only_leap_years: bool,
    time_clipping: Callable,
) -> CfVariable:
    ds = ds.chunk("auto")
    da = ds[name]
    study_da = _build_study_da(da, time_range, ignore_Feb29th)
    if _has_percentile_variable(ds, name):
        if base_period_time_range is not None:
            raise InvalidIcclimArgumentError(
                "Cannot determine the reference data to compute percentiles."
            )
        reference_da = PercentileDataArray.from_da(ds[f"{name}_percentiles"])
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
) -> Hashable:
    if per_var_name := in_dict.get("per_var_name", None):
        return per_var_name
    elif len(per_ds.data_vars) == 1:
        return per_ds.data_vars[list(per_ds.data_vars.keys())[0]].name
    else:
        return _guess_per_var_name(climate_var_name, per_ds)

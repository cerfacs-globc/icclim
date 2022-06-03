from __future__ import annotations

from typing import Callable, List, Union

import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.ecad.ecad_indices import EcadIndex
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendar
from icclim.models.cf_variable import CfVariable
from icclim.models.climate_index import ClimateIndex
from icclim.models.index_group import IndexGroup
from icclim.utils import get_date_to_iso_format

InFileBaseType = Union[str, List[str], Dataset, DataArray]

# # todo valid input to handle:
# in_files = {
#     "tasmax": {"study": "tasmax-store.zarr", "reference": ["per-1.nc", "per-2.nc"]},
#     "pr":     {"study": xr.open_dataset("pr").pr, },
# }
#
#
# class InputDictionary(TypedDict):
#     study: InFileBaseType
#     reference: InFileBaseType
#
#
# def read_multiple(
#         dudul: dict[str, InputDictionary] | InFileBaseType,
#         index: EcadIndex | None = None,
#         var_names: str | list[str] | None = None,
# ) -> Dataset:
#     if isinstance(dudul, dict):
#         data = read_dataset(dudul["study"], index, var_names)
#         percentiles = read_dataset(
#             dudul["reference"], index=None, var_names="percentiles",
#         )
#         return xr.merge([data[0], percentiles[0]])
#     return read_dataset(dudul)


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


def _read_dataarray(
    data: InFileBaseType,
    index: EcadIndex | None = None,
    var_names: str | list[str] | None = None,
) -> Dataset:
    if index is None:
        # user index case
        if var_names is None or (isinstance(var_names, list) and len(var_names) > 1):
            raise InvalidIcclimArgumentError(
                "When the input is a DataArray, var_names must be a string."
            )
        if isinstance(var_names, list):
            data_name = var_names[0]
        else:
            data_name = var_names
    else:
        if len(index.input_variables) > 1:
            raise InvalidIcclimArgumentError(
                f"Index {index.name} needs {len(index.input_variables)} variables."
                f" Please provide them with an xarray.Dataset, netCDF file(s) or a"
                f" zarr store."
            )
        # first alias of the unique variable
        data_name = index.input_variables[0][0]
    return data.to_dataset(name=data_name, promote_attrs=True)


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


def _guess_variable_names(
    in_var_name: str | list[str], index: ClimateIndex, ds: Dataset
) -> list[str]:
    """Try to guess the variable names using the expected kind of variable for
    the index.
    """
    if isinstance(in_var_name, str):
        return [in_var_name]
    elif isinstance(in_var_name, list):
        return in_var_name
    variable_names = []
    index_variables = index.input_variables
    for indice_var in index_variables:
        for alias in indice_var:
            # check if dataset contains this alias
            if is_alias_valid(ds, index, alias):
                variable_names.append(alias)
                break
    if len(variable_names) < len(index_variables):
        main_aliases = ", ".join(map(lambda v: v[0], index_variables))
        raise InvalidIcclimArgumentError(
            f"Index {index.short_name} needs the following variable(s)"
            f" [{main_aliases}], some of them were not recognized in the input."
            f" Use `var_name` parameter to explicitly use data variable names"
            f" from your input dataset: {list(ds.data_vars)}."
        )
    return variable_names


def build_cf_variables(
    var_name,
    index,
    ds,
    time_range,
    ignore_Feb29th,
    base_period_time_range,
    only_leap_years,
    freq,
) -> list[CfVariable]:
    # TODO:
    #     1. read variables var_names, in_files, guess_variable_name
    #     2. reduce variables (time_range, base_period_time_range, in_files(dict))
    #     Il faut que la partie qui associe quels nom pour quels variables (
    #     var_names, in_files(dict), guess_variable_name,
    #     ignore_Feb29th, only_leap_years)
    # todo move `_guess_variable_names` to `read_dataset` and build a dictionnary of
    #  {var_name: {in_da, in_ref_da, in_per}}
    #     then, and only then, apply time_range, base_period_time_range etc
    var_names = _guess_variable_names(var_name, index, ds)
    return [
        _build_cf_variable(
            da=ds[var_name],
            name=var_name,
            time_range=time_range,
            ignore_Feb29th=ignore_Feb29th,
            base_period_time_range=base_period_time_range,
            only_leap_years=only_leap_years,
            time_clipping=freq.time_clipping,
        )
        for var_name in var_names
    ]


def _build_cf_variable(
    da: DataArray,
    # ref_da: DataArray,
    name: str,
    time_range: list[str] | None,
    ignore_Feb29th: bool,
    base_period_time_range: list[str] | None,
    only_leap_years: bool,
    time_clipping: Callable,
) -> CfVariable:
    da = da.chunk("auto")
    study_da = _build_study_da(da, time_range, ignore_Feb29th)
    if base_period_time_range is not None:  # and ref_da is not None:
        raise InvalidIcclimArgumentError(
            "Cannot determine the reference data to compute percentiles."
        )
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
        da = xclim.core.calendar.convert_calendar(
            da, CfCalendar.NO_LEAP.get_name()
        )  # type:ignore
    return da


def _build_reference_da(
    original_da: DataArray,
    base_time_range: list[str],
    only_leap_years: bool,
) -> DataArray:
    check_time_range_pre_validity("base_period_time_range", base_time_range)
    base_time_range = [get_date_to_iso_format(x) for x in base_time_range]
    da = original_da.sel(time=slice(base_time_range[0], base_time_range[1]))
    check_time_range_post_validity(
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


def check_time_range_pre_validity(key: str, tr: list) -> None:
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


def is_alias_valid(ds, index, alias):
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

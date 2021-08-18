from datetime import datetime
from typing import List, Optional, Union

import numpy as np
import xarray
from xarray import DataArray
from xclim.core import calendar

from icclim.models.frequency import Frequency, build_frequency
from icclim.models.netcdf_version import NetcdfVersion, get_netcdf_version
from icclim.models.quantile_interpolation import QuantileInterpolation


class CfVariable:
    da: DataArray
    in_base_da: Optional[DataArray] = None

    def __init__(self, da: DataArray, in_base_da: DataArray = None) -> None:
        self.da = da
        self.in_base_da = in_base_da


class IndiceConfig:
    freq: Frequency
    cf_variables: List[CfVariable]
    save_percentile: bool = False
    is_percent: bool = False
    netcdf_version: NetcdfVersion
    window: Optional[int]
    threshold: Optional[str]
    transfer_limit_Mbytes: Optional[int] = None
    out_unit: Optional[str] = None

    def __init__(
        self,
        base_period_time_range,
        ds,
        ignore_Feb29th,
        only_leap_years,
        save_percentile,
        slice_mode,
        time_range,
        var_name,
        window_width,
        netcdf_version: Union[str, NetcdfVersion],
        transfer_limit_Mbytes: Optional[int] = None,
        out_unit: Optional[str] = None,
        interpolation: Optional[QuantileInterpolation] = None,
    ):
        self.freq = build_frequency(slice_mode)
        self.cf_variables = [
            _build_cf_variable(
                ds[cf_var_name],
                time_range,
                ignore_Feb29th,
                base_period_time_range,
                only_leap_years,
                transfer_limit_Mbytes,
            )
            for cf_var_name in var_name
        ]
        self.window = window_width
        self.save_percentile = save_percentile
        self.is_percent = out_unit == "%"
        self.transfer_limit_Mbytes = transfer_limit_Mbytes
        if isinstance(netcdf_version, str):
            self.netcdf_version = get_netcdf_version(netcdf_version)
        else:
            self.netcdf_version = netcdf_version
        self.interpolation = interpolation


def _build_cf_variable(
    da: DataArray,
    time_range: Optional[List[datetime]],
    ignore_Feb29th: bool,
    base_period_time_range: Optional[List[datetime]],
    only_leap_years: bool,
    transfer_limit_Mbytes: Optional[int],
) -> CfVariable:
    cf_var = CfVariable(
        _build_data_array(da, time_range, ignore_Feb29th, transfer_limit_Mbytes)
    )
    if base_period_time_range is not None:
        cf_var.in_base_da = _build_in_base_da(
            da, base_period_time_range, only_leap_years, transfer_limit_Mbytes
        )
    return cf_var


def _build_data_array(
    da: DataArray,
    time_range: Optional[List[datetime]],
    ignore_Feb29th: bool,
    transfer_limit_Mbytes: Optional[int],
) -> DataArray:
    if time_range is not None:
        if len(time_range) != 2:
            raise Exception("Not a valid time range")
        da = da.sel(time=slice(time_range[0], time_range[1]))
    if ignore_Feb29th:
        da = calendar.convert_calendar(da, "noleap")  # type:ignore
    if transfer_limit_Mbytes is not None:
        da = _chunk_data(transfer_limit_Mbytes, da)
    return da


def _build_in_base_da(
    da: DataArray,
    base_period_time_range: List[datetime],
    only_leap_years: bool,
    transfer_limit_Mbytes: Optional[int],
) -> DataArray:
    if len(base_period_time_range) != 2:
        raise Exception("Not a valid time range")
    da = da.sel(time=slice(base_period_time_range[0], base_period_time_range[1]))
    if only_leap_years:
        da = _reduce_only_leap_years(da)
    if transfer_limit_Mbytes is not None:
        da = _chunk_data(transfer_limit_Mbytes, da)
    return da


def _chunk_data(transfer_limit_Mbytes: int, da: DataArray) -> DataArray:
    # TODO add warning if ckunks are too small ? xarray doc suggest at least 1000 x 1000 elements per chunk
    # TODO if dataset has more than 3 dims (such as a depth dim) it will only chunk on lat,lon and not on other dims
    transfer_limit_bytes = transfer_limit_Mbytes * 1024 * 1024
    optimal_tile_dimension = int(
        np.sqrt(transfer_limit_bytes / (len(da.time) * da.dtype.itemsize))
    )
    return da.chunk(
        chunks={"lat": optimal_tile_dimension, "lon": optimal_tile_dimension}
    )


def _reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list: List[DataArray] = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if reduced_list == []:
        raise Exception(
            "No leap year in current dataset. Do not use only_leap_years parameter."
        )
    return xarray.concat(reduced_list, "time")

from datetime import datetime
from typing import List, Optional, Union

import numpy as np
import xarray
from xarray import DataArray, Dataset
from xclim.core import calendar

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency, SliceMode, build_frequency
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
    threshold: Optional[float]
    transfer_limit_Mbytes: Optional[int]
    out_unit: Optional[str]

    def __init__(
        self,
        ds: Dataset,
        slice_mode: SliceMode,
        var_name: List[str],
        netcdf_version: Union[str, NetcdfVersion],
        save_percentile: bool = False,
        only_leap_years: bool = False,
        ignore_Feb29th: bool = False,
        window_width: Optional[int] = 5,
        time_range: Optional[List[datetime]] = None,
        base_period_time_range: Optional[List[datetime]] = None,
        transfer_limit_Mbytes: Optional[int] = None,
        threshold: Optional[float] = None,
        out_unit: Optional[str] = None,
        interpolation: Optional[
            QuantileInterpolation
        ] = QuantileInterpolation.MEDIAN_UNBIASED,
    ):
        self.freq = build_frequency(slice_mode)
        if time_range is not None:
            time_range = [x.strftime("%Y-%m-%d") for x in time_range]
        if base_period_time_range is not None:
            base_period_time_range = [
                x.strftime("%Y-%m-%d") for x in base_period_time_range
            ]
        self.cf_variables = [
            _build_cf_variable(
                da=ds[cf_var_name],
                time_range=time_range,
                ignore_Feb29th=ignore_Feb29th,
                base_period_time_range=base_period_time_range,
                only_leap_years=only_leap_years,
                transfer_limit_Mbytes=transfer_limit_Mbytes,
            )
            for cf_var_name in var_name
        ]
        self.window = window_width
        self.save_percentile = save_percentile
        self.is_percent = out_unit == "%"
        self.out_unit = out_unit
        self.transfer_limit_Mbytes = transfer_limit_Mbytes
        if isinstance(netcdf_version, str):
            self.netcdf_version = get_netcdf_version(netcdf_version)
        else:
            self.netcdf_version = netcdf_version
        self.interpolation = interpolation
        self.threshold = threshold


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
            raise InvalidIcclimArgumentError(
                f"The given time_range {time_range}"
                f" has a length of {len(time_range)}."
                f" It must be exactly a length of 2."
            )
        da = da.sel(time=slice(time_range[0], time_range[1]))
        if len(da.time) == 0:
            raise InvalidIcclimArgumentError(
                f"The given time range {time_range!r} "
                f"is out of the dataset time period."
            )
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
        raise InvalidIcclimArgumentError(
            f"The given time_range {base_period_time_range}"
            f" has a length of {len(base_period_time_range)}."
            f" It must be exactly a length of 2."
        )
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
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use only_leap_years parameter."
        )
    return xarray.concat(reduced_list, "time")

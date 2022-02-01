from datetime import datetime
from typing import Any, Callable, List, Optional, Union

import xarray
from xarray import DataArray, Dataset
from xclim.core import calendar

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendar
from icclim.models.frequency import Frequency, SliceMode
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation


class CfVariable:
    """
    CfVariable groups together two xarray DataArray for the same variable.
    One represent the whole studied period. The other is only the in base period used by
    percentile based indices to compute percentiles.

    Parameters
    ----------
    da: DataArray
        The variable studied.
    in_base_da: DataArray
        The variable studied limited to the in base period.
    """

    # TODO: seems unnecessary abstraction between ds and da. Replace by a Dataset.
    da: DataArray
    in_base_da: DataArray

    def __init__(self, da: DataArray, in_base_da: DataArray) -> None:
        self.da = da
        self.in_base_da = in_base_da


class IndexConfig:
    """
    Configuration class for ECA&D indices.

    Parameters
    ----------
    freq: Frequency
        The expected resampling frequency of the output.
    cf_variables: List[CfVariable]
        List of CfVariable necessary to compute the index.
    save_percentile: bool = False
        On percentile based indices, if True, this saves the percentile in the output
        netcdf.
    is_percent: bool = False
        On indices resulting in a numbers of days, if True, this converts the results to
        % of the sampling frequency
    netcdf_version: NetcdfVersion
        Netcdf version to be used when creating the output
    window: Optional[int]
        On indices relying on a rolling window of days, configure the window width.
    threshold: Optional[float]
        On indices relying on a threshold, configure the threshold value. Unit less.
        The unit "degC" is added by icclim.
    transfer_limit_Mbytes: Optional[int]
        The dask maximum chunk size.
    out_unit: Optional[str]
        The output unit overriding Xclim results.
    callback: Optional[Callable]
        A callable to produce a progress bar
    """

    freq: Frequency
    _cf_variables: List[CfVariable]
    save_percentile: bool = False
    is_percent: bool = False
    netcdf_version: NetcdfVersion
    window: Optional[int]
    threshold: Optional[float]
    transfer_limit_Mbytes: Optional[int]
    out_unit: Optional[str]
    callback: Optional[Callable]

    def __init__(
        self,
        ds: Dataset,
        slice_mode: SliceMode,
        var_name: List[str],
        netcdf_version: Union[str, NetcdfVersion],
        index: Optional[Any],  # EcadIndex proper typing causes circular dependency
        save_percentile: bool = False,
        only_leap_years: bool = False,
        ignore_Feb29th: bool = False,
        window_width: Optional[int] = 5,
        time_range: Optional[List[datetime]] = None,
        base_period_time_range: Optional[List[datetime]] = None,
        threshold: Optional[float] = None,
        out_unit: Optional[str] = None,
        interpolation: Optional[
            QuantileInterpolation
        ] = QuantileInterpolation.MEDIAN_UNBIASED,
        callback: Optional[Callable] = None,
        chunk_it: bool = False,
    ):
        self.freq = Frequency.lookup(slice_mode)
        if time_range is not None:
            time_range = [x.strftime("%Y-%m-%d") for x in time_range]
        if base_period_time_range is not None:
            base_period_time_range = [
                x.strftime("%Y-%m-%d") for x in base_period_time_range
            ]
        self._cf_variables = [
            _build_cf_variable(
                da=ds[cf_var_name],
                time_range=time_range,
                ignore_Feb29th=ignore_Feb29th,
                base_period_time_range=base_period_time_range,
                only_leap_years=only_leap_years,
                chunk_it=chunk_it,
            )
            for cf_var_name in var_name
        ]
        self.window = window_width
        self.save_percentile = save_percentile
        self.is_percent = out_unit == "%"
        self.out_unit = out_unit
        if isinstance(netcdf_version, str):
            self.netcdf_version = NetcdfVersion.lookup(netcdf_version)
        else:
            self.netcdf_version = netcdf_version
        self.interpolation = interpolation
        self.threshold = threshold
        self.callback = callback
        self.index = index

    @property
    def tas(self) -> CfVariable:
        return self._cf_variables[0]

    @property
    def tasmax(self) -> CfVariable:
        return self._cf_variables[0]

    @property
    def tasmin(self) -> CfVariable:
        if len(self._cf_variables) > 1:
            return self._cf_variables[1]
        return self._cf_variables[0]

    @property
    def pr(self) -> CfVariable:
        if len(self._cf_variables) > 1:
            return self._cf_variables[1]
        return self._cf_variables[0]


def _build_cf_variable(
    da: DataArray,
    time_range: Optional[List[datetime]],
    ignore_Feb29th: bool,
    base_period_time_range: Optional[List[datetime]],
    only_leap_years: bool,
    chunk_it: bool,
) -> CfVariable:
    if chunk_it:
        # todo maybe do it only on indices where parallelization will be useful
        da = da.chunk("auto")  # typing fixed in next xarray version
    out_of_base_da = _build_data_array(da, time_range, ignore_Feb29th)
    if base_period_time_range is not None:
        in_base_da = _build_in_base_da(da, base_period_time_range, only_leap_years)
    else:
        in_base_da = out_of_base_da
    return CfVariable(out_of_base_da, in_base_da)


def _build_data_array(
    original_da: DataArray, time_range: Optional[List[datetime]], ignore_Feb29th: bool
) -> DataArray:
    if time_range is not None:
        if len(time_range) != 2:
            raise InvalidIcclimArgumentError(
                f"The given `time_range` {time_range}"
                f" has {len(time_range)} elements."
                f" It must have exactly 2 dates."
            )
        da = original_da.sel(time=slice(time_range[0], time_range[1]))
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
        da = calendar.convert_calendar(da, CfCalendar.NO_LEAP.get_name())  # type:ignore
    return da


def _build_in_base_da(
    original_da: DataArray,
    base_period_time_range: List[datetime],
    only_leap_years: bool,
) -> DataArray:
    # TODO merge with _build_data_array ?
    if len(base_period_time_range) != 2:
        raise InvalidIcclimArgumentError(
            f"The given `base_period_time_range` {base_period_time_range}"
            f" has {len(base_period_time_range)} elements."
            f" It must have exactly 2 dates."
        )
    da = original_da.sel(
        time=slice(base_period_time_range[0], base_period_time_range[1])
    )
    if len(da.time) == 0:
        raise InvalidIcclimArgumentError(
            f"The given `base_period_time_range` {base_period_time_range}"
            f" is out of the sample time bounds: "
            f"{original_da.time.min().dt.floor('D').values} "
            f"- {original_da.time.max().dt.floor('D').values}."
        )
    if only_leap_years:
        da = _reduce_only_leap_years(original_da)
    return da


def _reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list: List[DataArray] = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use only_leap_years parameter."
        )
    return xarray.concat(reduced_list, "time")

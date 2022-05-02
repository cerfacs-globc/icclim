from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import xarray
from xarray import DataArray, Dataset
from xclim.core import calendar

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.cf_calendar import CfCalendar
from icclim.models.constants import PR, TAS, TAS_MAX, TAS_MIN
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
    study_da: DataArray
        The variable studied.
    reference_da: DataArray
        The variable studied limited to the in base period.
    """

    name: str
    study_da: DataArray
    reference_da: DataArray

    def __init__(self, name: str, study_da: DataArray, reference_da: DataArray) -> None:
        self.name = name
        self.study_da = study_da
        self.reference_da = reference_da


class IndexConfig:
    """
    Configuration class for ECA&D indices.

    Parameters
    ----------
    freq: Frequency
        The expected resampling frequency of the output.
    cf_variables:
        List of CfVariable necessary to compute the index.
    save_percentile: bool = False
        On percentile based indices, if True, this saves the percentile in the output
        netcdf.
    is_percent:
        On indices resulting in a numbers of days, if True, this converts the results to
        % of the sampling frequency
    netcdf_version:
        Netcdf version to be used when creating the output
    window:
        On indices relying on a rolling window of days, configure the window width.
    threshold:
        On indices relying on a threshold, configure the threshold value. Unit less.
        The unit "degC" is added by icclim.
    transfer_limit_Mbytes:
        The dask maximum chunk size.
    out_unit:
        The output unit overriding Xclim results.
    callback:
        A callable to produce a progress bar
    """

    freq: Frequency
    _cf_variables: list[CfVariable]
    save_percentile: bool = False
    is_percent: bool = False
    netcdf_version: NetcdfVersion
    window: int | None
    threshold: float | None
    transfer_limit_Mbytes: int | None
    out_unit: str | None
    callback: Callable[[int], None] | None

    def __init__(
        self,
        ds: Dataset,
        slice_mode: SliceMode,
        var_names: list[str],
        netcdf_version: str | NetcdfVersion,
        index: Any | None,  # EcadIndex proper typing causes circular dependency
        save_percentile: bool = False,
        only_leap_years: bool = False,
        ignore_Feb29th: bool = False,
        window_width: int | None = 5,
        time_range: list[datetime] | None = None,
        base_period_time_range: list[datetime] | None = None,
        threshold: float | None = None,
        out_unit: str | None = None,
        interpolation: QuantileInterpolation
        | None = QuantileInterpolation.MEDIAN_UNBIASED,
        callback: Callable[[int], None] | None = None,
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
                da=ds[var_name],
                name=var_name,
                time_range=time_range,
                ignore_Feb29th=ignore_Feb29th,
                base_period_time_range=base_period_time_range,
                only_leap_years=only_leap_years,
                chunk_it=chunk_it,
                pre_processing=self.freq.pre_processing,
            )
            for var_name in var_names
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
        tas_vars = list(filter(lambda v: v.name in TAS, self._cf_variables))
        if len(tas_vars) == 1:
            return tas_vars[0]
        # Otherwise rely on positional guess
        return self._cf_variables[0]

    @property
    def tasmax(self) -> CfVariable:
        tas_max_vars = list(filter(lambda v: v.name in TAS_MAX, self._cf_variables))
        if len(tas_max_vars) == 1:
            return tas_max_vars[0]
        # Otherwise rely on positional guess
        return self._cf_variables[0]

    @property
    def tasmin(self) -> CfVariable:
        tas_min_vars = list(filter(lambda v: v.name in TAS_MIN, self._cf_variables))
        if len(tas_min_vars) == 1:
            return tas_min_vars[0]
        # Otherwise rely on positional guess
        if len(self._cf_variables) > 1:
            # compound indices case
            return self._cf_variables[1]
        return self._cf_variables[0]

    @property
    def pr(self) -> CfVariable:
        pr_vars = list(filter(lambda v: v.name in PR, self._cf_variables))
        if len(pr_vars) == 1:
            return pr_vars[0]
        # Otherwise rely on positional guess
        if len(self._cf_variables) > 1:
            # compound indices case
            return self._cf_variables[1]
        return self._cf_variables[0]


def _build_cf_variable(
    da: DataArray,
    name: str,
    time_range: list[str] | None,
    ignore_Feb29th: bool,
    base_period_time_range: list[str] | None,
    only_leap_years: bool,
    chunk_it: bool,
    pre_processing: Callable,
) -> CfVariable:
    if chunk_it:
        da = da.chunk("auto")  # noqa - typing fixed in futur xarray version
    study_da = _build_study_da(da, time_range, ignore_Feb29th)
    study_da = pre_processing(study_da)
    if base_period_time_range is not None:
        reference_da = _build_reference_da(da, base_period_time_range, only_leap_years)
        reference_da = pre_processing(reference_da)
    else:
        reference_da = study_da
    # TODO: all these operations should probably be added in history metadata
    #       it could be a property in CfVariable which will be reused when we update the
    #       metadata of the index, at the end.
    return CfVariable(name, study_da, reference_da)


def _build_study_da(
    original_da: DataArray, time_range: list[str] | None, ignore_Feb29th: bool
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


def _build_reference_da(
    original_da: DataArray,
    base_period_time_range: list[str],
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
    reduced_list: list[DataArray] = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if not reduced_list:
        raise InvalidIcclimArgumentError(
            "No leap year in current dataset. Do not use only_leap_years parameter."
        )
    return xarray.concat(reduced_list, "time")

from __future__ import annotations

from typing import Callable

from icclim.models.cf_variable import CfVariable
from icclim.models.climate_index import ClimateIndex
from icclim.models.constants import PR, TAS, TAS_MAX, TAS_MIN
from icclim.models.frequency import Frequency
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation


class IndexConfig:
    """
    Configuration class for standard indices.

    Parameters
    ----------
    frequency: Frequency
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

    frequency: Frequency
    cf_variables: list[CfVariable]
    save_percentile: bool = False
    is_percent: bool = False
    netcdf_version: NetcdfVersion
    window: int | None
    threshold: list[float] | float | None
    transfer_limit_Mbytes: int | None
    out_unit: str | None
    callback: Callable[[int], None] | None

    def __init__(
        self,
        frequency: Frequency,
        netcdf_version: str | NetcdfVersion,
        index: ClimateIndex | None,
        cf_variables: list[CfVariable],
        save_percentile: bool = False,
        window_width: int | None = 5,
        threshold: list[float] | float | None = None,
        out_unit: str | None = None,
        interpolation=QuantileInterpolation.MEDIAN_UNBIASED,
        callback: Callable[[int], None] | None = None,
    ):
        self.frequency = frequency
        self.cf_variables = cf_variables
        self.window = window_width
        self.save_percentile = save_percentile
        self.is_percent = out_unit == "%"
        self.out_unit = out_unit
        self.netcdf_version = NetcdfVersion.lookup(netcdf_version)
        self.interpolation = interpolation
        self.threshold = threshold
        self.callback = callback
        self.index = index

    @property
    def tas(self) -> CfVariable:
        tas_vars = list(filter(lambda v: v.name in TAS, self.cf_variables))
        if len(tas_vars) == 1:
            return tas_vars[0]
        # Otherwise rely on positional guess
        return self.cf_variables[0]

    @property
    def tasmax(self) -> CfVariable:
        tas_max_vars = list(filter(lambda v: v.name in TAS_MAX, self.cf_variables))
        if len(tas_max_vars) == 1:
            return tas_max_vars[0]
        # Otherwise rely on positional guess
        return self.cf_variables[0]

    @property
    def tasmin(self) -> CfVariable:
        tas_min_vars = list(filter(lambda v: v.name in TAS_MIN, self.cf_variables))
        if len(tas_min_vars) == 1:
            return tas_min_vars[0]
        # Otherwise rely on positional guess
        if len(self.cf_variables) > 1:
            # compound indices case
            return self.cf_variables[1]
        return self.cf_variables[0]

    @property
    def pr(self) -> CfVariable:
        pr_vars = list(filter(lambda v: v.name in PR, self.cf_variables))
        if len(pr_vars) == 1:
            return pr_vars[0]
        # Otherwise rely on positional guess
        if len(self.cf_variables) > 1:
            # compound indices case
            return self.cf_variables[1]
        return self.cf_variables[0]

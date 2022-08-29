from __future__ import annotations

import dataclasses
from typing import Callable

from icclim.models.climate_variable import ClimateVariable
from icclim.models.frequency import Frequency
from icclim.models.logical_link import LogicalLink
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation


@dataclasses.dataclass
class IndexConfig:
    """
    DTO class to map icclim.index input to the Indicator usable configs.

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
    scalar_thresholds:
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
    climate_variables: list[ClimateVariable]
    window: int | None
    out_unit: str | None
    callback: Callable[[int], None] | None
    netcdf_version: NetcdfVersion
    save_thresholds: bool
    interpolation: QuantileInterpolation
    is_single_var: bool
    reference_period: tuple[str, str] | None
    indicator_name: str
    logical_link: LogicalLink
    coef: float | None
    date_event: bool

    @property
    def is_percent(self) -> bool:
        # todo delete ? unit handling should be in GenericIndicator postprocessing
        return self.out_unit == "%"

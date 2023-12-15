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
    DTO class to map icclim.index input the parameters of the different indicator
    compute functions.

    Attributes
    ----------
    frequency: Frequency
        The expected resampling frequency of the output.
    climate_variables: list[ClimateVariable]
        List of CfVariable necessary to compute the index.
    save_percentile: bool = False
        On percentile based indices, if True, this saves the percentile in the output
        netcdf.
    netcdf_version:
        Netcdf version to be used when creating the output
    rolling_window_width:
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
    min_spell_length: int | None
    rolling_window_width: int | None
    out_unit: str | None
    callback: Callable[[int], None] | None
    netcdf_version: NetcdfVersion
    save_thresholds: bool
    interpolation: QuantileInterpolation
    is_compared_to_reference: bool
    reference_period: tuple[str, str] | None
    indicator_name: str
    logical_link: LogicalLink
    coef: float | None
    date_event: bool
    sampling_method: str

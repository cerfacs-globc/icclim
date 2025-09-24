"""
Contain the IndexConfig class.

It holds the compiled configuration for the computation of climate indices.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from icclim._core.climate_variable import ClimateVariable
    from icclim._core.model.indicator import Indicator
    from icclim._core.model.logical_link import LogicalLink
    from icclim._core.model.netcdf_version import NetcdfVersion
    from icclim._core.model.quantile_interpolation import QuantileInterpolation
    from icclim.frequency import Frequency


@dataclasses.dataclass
class IndexConfig:
    """
    Configuration class for defining climate index parameters.

    Parameters
    ----------
    frequency : Frequency
        The time frequency of the output. Built from ``slice_mode``.
    climate_variables : list[ClimateVariable]
        The list of climate variables used in the index calculation.
    min_spell_length : int | None
        The minimum spell length for the index calculation.
        None if the index is not a spell index.
    rolling_window_width : int | None
        The width of the rolling window for the index calculation.
        None if the index is not a rolling index.
    out_unit : str | None
        The output unit for the index calculation.
        Optional, used to override the default unit.
    callback : Callable[[int], None] | None
        The callback function for progress updates during the index calculation.
        Deprecated.
    netcdf_version : NetcdfVersion
        The version of the NetCDF file format to use for saving the index results.
        Default is NetcdfVersion.NETCDF4.
    save_thresholds : bool
        Flag indicating whether to save the threshold values used in the index
        calculation.
    interpolation : QuantileInterpolation
        The interpolation method to use for calculating quantiles/percentiles.
    is_compared_to_reference : bool
        Flag indicating whether the index is compared to a reference period.
    reference_period : tuple[str, str] | None
        The reference period for the index calculation.
    indicator_name : str
        The name of the index.
    logical_link : LogicalLink
        The logical link to use for combining multiple indices.
    coef : float | None
        The coefficient to apply to the index values.
    date_event : bool
        Flag indicating whether the index represents a date or an event.
    sampling_method : str
        The sampling method to use for the index calculation.
        In conjonction with the Frequency, it is used on specific indices such as the
        anomaly (a.k.a diff_of_means) to determine if the reference period and the
        studied period should be grouped by or resampled.
        It can be either 'group_by', 'resample', or
        'group_by_ref_and_resample_study'.
        'group_by' will group the data by the specified frequency, for example every
        data of every January together.
        'resample' will resample the data to the specified frequency, for example every
        days of each month independently together.
        'group_by_ref_and_resample_study' will group the reference data by the specified
        frequency and resample the study data to the same frequency.
        This last method allows for example to compare each January, independently, of
        the study period to every January of the reference period.
        This is typically used to compare the each month of the studied period
        to a normal (the reference) of many aggregated years.
    rename : str | None
        The new name for the output variable.
        Optional, used to override the default index name.
    indicator : Indicator
        The indicator to be computed.
    reference : str
        The reference value for the index calculation.
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
    rename: str | None
    indicator: Indicator
    reference: str

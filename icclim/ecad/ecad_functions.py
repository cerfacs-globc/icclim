"""All ECA&D functions. Each function wraps its xclim equivalent functions adding icclim
metadata to it.
"""
from __future__ import annotations

from warnings import warn

import numpy as np
import xarray as xr
from xarray import DataArray
from xclim import atmos
from xclim.core.units import convert_units_to

from icclim.models.cf_calendar import CfCalendarRegistry
from icclim.models.constants import (
    IN_BASE_IDENTIFIER,
    PART_OF_A_WHOLE_UNIT,
    UNITS_ATTRIBUTE_KEY,
)
from icclim.models.frequency import Frequency, FrequencyRegistry
from icclim.models.index_config import IndexConfig


def prcptot(config: IndexConfig) -> DataArray:
    result = atmos.precip_accumulation(
        _filter_in_wet_days(config.pr.studied_data, dry_day_value=0),
        **config.frequency.build_frequency_kwargs(),
    )
    return result


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    if sampling_freq == FrequencyRegistry.MONTH:
        da = da / da.time.dt.daysinmonth * 100
    elif sampling_freq == FrequencyRegistry.YEAR:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 366
        coef[{"time": ~leap_years}] = 365
        da = da / coef
    elif sampling_freq == FrequencyRegistry.AMJJAS:
        da = da / 183
    elif sampling_freq == FrequencyRegistry.ONDJFM:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 183
        coef[{"time": ~leap_years}] = 182
        da = da / coef
    elif sampling_freq == FrequencyRegistry.DJF:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 91
        coef[{"time": ~leap_years}] = 90
        da = da / coef
    elif sampling_freq in [FrequencyRegistry.MAM, FrequencyRegistry.JJA]:
        da = da / 92
    elif sampling_freq == FrequencyRegistry.SON:
        da = da / 91
    else:
        # TODO improve this for custom resampling
        warn(
            "For now, '%' unit can only be used when `slice_mode` is one of: "
            "{MONTH, YEAR, AMJJAS, ONDJFM, DJF, MAM, JJA, SON}."
        )
        return da
    da.attrs[UNITS_ATTRIBUTE_KEY] = PART_OF_A_WHOLE_UNIT
    return da


def _is_leap_year(da: DataArray) -> np.ndarray:
    time_index = da.indexes.get("time")
    if isinstance(time_index, xr.CFTimeIndex):
        return CfCalendarRegistry.lookup(time_index.calendar).is_leap(da.time.dt.year)
    else:
        return da.time.dt.is_leap_year


def _add_bootstrap_meta(result: DataArray, per: DataArray) -> DataArray:
    result.attrs[IN_BASE_IDENTIFIER] = per.climatology_bounds
    return result


def _filter_in_wet_days(da: DataArray, dry_day_value: float):
    """Turns non wet days to NaN. dry_day_value should be NaN or 0."""
    precip = convert_units_to(da, "mm/d")
    return precip.where(precip > 1, dry_day_value)

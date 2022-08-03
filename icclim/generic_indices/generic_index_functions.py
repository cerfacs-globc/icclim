from __future__ import annotations

from typing import Any, Sequence

import numpy as np
import xarray as xr
from xarray import DataArray
from xclim.core.calendar import build_climatology_bounds, percentile_doy
from xclim.core.utils import PercentileDataArray, calc_perc

from icclim.models.frequency import Frequency
from icclim.models.quantile_interpolation import QuantileInterpolation


def _can_run_bootstrap(da: DataArray, threshold: Any) -> bool:
    """Avoid bootstrapping if there is one single year overlapping
    or no year overlapping or all year overlapping.
    """
    # TODO: when true add bootstrap to metadata
    if not threshold.is_doy_per_threshold:
        return False
    reference = threshold.value
    study_years = np.unique(da.indexes.get("time").year)
    overlapping_years = np.unique(
        da.sel(time=_get_ref_period_slice(reference)).indexes.get("time").year
    )
    return 1 < len(overlapping_years) < len(study_years)


def _get_ref_period_slice(da: DataArray) -> slice:
    if (bds := da.attrs.get("climatology_bounds", None)) is not None:
        return slice(*bds)
    time_length = len(da.time)
    return slice(*da.time[0 :: time_length - 1].dt.strftime("%Y-%m-%d").values)


def build_period_per(
    per_val: float,
    base_period_time_range: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    sampling_frequency: Frequency,
    study_da: DataArray,
    percentile_min_value: float | None,
) -> PercentileDataArray:
    from icclim.pre_processing.input_parsing import build_reference_da

    reference = build_reference_da(
        study_da,
        base_period_time_range,
        only_leap_years,
        sampling_frequency,
        percentile_min_value=percentile_min_value,
    )
    computed_per = xr.apply_ufunc(
        calc_perc,
        reference,
        input_core_dims=[["time"]],
        output_core_dims=[["percentiles"]],
        keep_attrs=True,
        kwargs=dict(
            percentiles=[per_val],
            alpha=interpolation.alpha,
            beta=interpolation.beta,
            copy=True,
        ),
        dask="parallelized",
        output_dtypes=[reference.dtype],
        dask_gufunc_kwargs=dict(output_sizes={"percentiles": 1}, allow_rechunk=True),
    )
    computed_per = computed_per.assign_coords(
        percentiles=xr.DataArray([per_val], dims=("percentiles",))
    )
    res = PercentileDataArray.from_da(
        source=computed_per,
        climatology_bounds=build_climatology_bounds(reference),
    )
    return res


def build_doy_per(
    per_val: float,
    base_period_time_range: Sequence[str],
    interpolation: QuantileInterpolation,
    only_leap_years: bool,
    window: int,
    sampling_frequency: Frequency,
    study_da: DataArray,
    percentile_min_value: float | None,
) -> PercentileDataArray:
    from icclim.pre_processing.input_parsing import build_reference_da

    reference = build_reference_da(
        study_da,
        base_period_time_range,
        only_leap_years,
        sampling_frequency,
        percentile_min_value,
    )
    res = percentile_doy(
        arr=reference,
        window=window,
        per=per_val,
        alpha=interpolation.alpha,
        beta=interpolation.beta,
    ).compute()  # "optimization" (diminish dask scheduler workload)
    return res

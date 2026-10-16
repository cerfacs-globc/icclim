"""Compiled helpers for reliable percentile bootstrap counts."""
# ruff: noqa: ANN001, ANN202, PLR2004

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

import numpy as np
from xarray.coding.cftimeindex import CFTimeIndex

from icclim._core.constants import REFERENCE_PERIOD_ID
from icclim._core.generic.bootstrap_capability import (
    is_optimized_doy_percentile_count_supported,
    is_optimized_doy_percentile_threshold_supported,
)
from icclim._core.generic.bootstrap_primitives import (
    BootstrapPreparedInputs,
    build_bootstrap_array_inputs,
    build_bootstrap_output,
    build_bootstrap_prepared_inputs,
    build_bootstrap_reference_sample,
    build_bootstrap_temporal_indexing,
)
from icclim._core.model.operator import Operator

if TYPE_CHECKING:
    from xarray import DataArray

    from icclim._core.generic.threshold.percentile import PercentileThreshold


NON_LEAP_YEAR_DAY_COUNT = 365
LEAP_YEAR_DAY_COUNT = 366


def _compute_multiple_percentiles(
    reducer,
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    *,
    percentiles_after_time: bool = False,
    **kwargs,
) -> DataArray | None:
    """Evaluate a scalar-percentile kernel sequentially for each percentile."""
    percentile_coord = threshold.percentile_coord()
    if percentile_coord.size <= 1:
        return None
    import xarray as xr  # noqa: PLC0415

    results = []
    percentile_values = np.asarray(percentile_coord.values, dtype=float).reshape(-1)
    for percentile in percentile_values:
        sliced = copy(threshold)
        if threshold.is_ready:
            sliced._prepared_value = threshold.value.sel(  # noqa: SLF001
                percentiles=[percentile]
            )
        else:
            sliced.initial_value = [float(percentile)]
        result = reducer(study, sliced, freq, **kwargs)
        if result is None:
            return None
        if "percentiles" in result.coords and "percentiles" not in result.dims:
            result = result.drop_vars("percentiles")
        results.append(result)
    combined = xr.concat(
        results,
        dim=xr.IndexVariable("percentiles", percentile_values),
    )
    other_dims = tuple(
        dim for dim in combined.dims if dim not in {"time", "percentiles"}
    )
    if percentiles_after_time:
        return combined.transpose("time", "percentiles", *other_dims)
    return combined.transpose("time", *other_dims, "percentiles")


def bootstrap_array_dtype(study: DataArray) -> np.dtype:
    """Return the calculation dtype required by the study calendar."""
    time_index = study.indexes["time"]
    if isinstance(time_index, CFTimeIndex):
        return np.float64
    return np.float32


def _use_order_stat_thresholds(study: DataArray) -> bool:
    return isinstance(study.indexes["time"], CFTimeIndex)


def compute_doy_percentile_bootstrap_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute percentile bootstrap counts without building a huge dask graph."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_count,
        study,
        threshold,
        freq,
        percentiles_after_time=True,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        return None
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        study=reference_sample.study,
        threshold=threshold,
    )
    result = _bootstrap_count_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        _use_order_stat_thresholds(reference_sample.study),
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="d",
    )
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def _build_nominal_full_thresholds(
    study: DataArray,
    threshold: PercentileThreshold,
    min_threshold: float = np.nan,
) -> np.ndarray:
    time_index = study.indexes["time"]
    if not isinstance(time_index, CFTimeIndex):
        return np.empty((0, 0), dtype=np.float64)
    if study.time.dt.dayofyear.max().item() != 366:
        return np.empty((0, 0), dtype=np.float64)
    threshold.ensure_ready(study)
    nominal_threshold = threshold.value
    if int(nominal_threshold.dayofyear.max()) != 366:
        return np.empty((0, 0), dtype=np.float64)
    if "percentiles" in nominal_threshold.dims:
        nominal_threshold = nominal_threshold.squeeze("percentiles")
    nominal_threshold = nominal_threshold.transpose("dayofyear", ...)
    values = np.asarray(nominal_threshold.data, dtype=np.float64).reshape(
        nominal_threshold.sizes["dayofyear"],
        -1,
    )
    if not np.isnan(min_threshold):
        values = np.where(values > min_threshold, values, min_threshold)
    return values


def compute_doy_percentile_bootstrap_count_threshold_bank_prototype(  # noqa: C901, PLR0912
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Prototype a per-target threshold-bank exact count path.

    This helper is intentionally not wired into runtime routing. It exists to
    validate a candidate exact algorithm shape for `cftime` bootstrap counts.
    """
    if not _can_compute_threshold_bank_bootstrap_count(study, threshold, freq):
        return None
    threshold_builder = getattr(
        _build_bootstrap_threshold_series_for_cell,
        "py_func",
        None,
    )
    count_exceedances = getattr(_count_exceedances, "py_func", None)
    if threshold_builder is None or count_exceedances is None:
        return None
    prepared_inputs = build_bootstrap_prepared_inputs(
        study,
        threshold,
        freq,
        dtype=np.float64,
    )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    quantile = float(threshold.percentile_coord().item()) / 100.0
    alpha = float(threshold.interpolation.alpha)
    beta = float(threshold.interpolation.beta)
    op_code = _operator_code(threshold.operator)
    max_samples = temporal_indexing.sample_indices_by_day_of_year.shape[1]
    n_reference_years = temporal_indexing.substitute_alignment.shape[1]
    n_cells = array_inputs.flat_study.shape[1]
    output = np.empty(
        (len(temporal_indexing.output_group_labels), n_cells),
        dtype=np.float64,
    )
    overlap_reference = array_inputs.flat_reference_raw
    nominal_thresholds_by_cell = [
        threshold_builder(
            array_inputs.flat_reference_filtered,
            temporal_indexing.sample_indices_by_day_of_year,
            temporal_indexing.reference_index_year,
            temporal_indexing.reference_index_position,
            temporal_indexing.substitute_alignment,
            -1,
            -1,
            cell,
            max_samples,
            quantile,
            alpha,
            beta,
            min_threshold,
        )
        for cell in range(n_cells)
    ]
    threshold_bank = np.full(
        (
            n_reference_years,
            n_reference_years,
            temporal_indexing.sample_indices_by_day_of_year.shape[0],
            n_cells,
        ),
        np.nan,
        dtype=np.float64,
    )
    for target_ref_i in range(n_reference_years):
        for substitute_i in range(n_reference_years):
            if substitute_i == target_ref_i:
                continue
            for cell in range(n_cells):
                threshold_bank[target_ref_i, substitute_i, :, cell] = threshold_builder(
                    overlap_reference,
                    temporal_indexing.sample_indices_by_day_of_year,
                    temporal_indexing.reference_index_year,
                    temporal_indexing.reference_index_position,
                    temporal_indexing.substitute_alignment,
                    target_ref_i,
                    substitute_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    min_threshold,
                )
    for year_i, target_ref_i in enumerate(temporal_indexing.year_to_reference_index):
        group_start = temporal_indexing.year_group_starts[year_i]
        group_stop = temporal_indexing.year_group_stops[year_i]
        for cell in range(n_cells):
            if target_ref_i < 0:
                thresholds = nominal_thresholds_by_cell[cell]
                for group_i in range(group_start, group_stop):
                    output[group_i, cell] = count_exceedances(
                        array_inputs.flat_study,
                        thresholds,
                        temporal_indexing.study_day_of_years,
                        temporal_indexing.output_starts[group_i],
                        temporal_indexing.output_lengths[group_i],
                        cell,
                        temporal_indexing.year_max_day_of_years[year_i],
                        op_code,
                    )
                continue
            for group_i in range(group_start, group_stop):
                output[group_i, cell] = 0.0
            substitute_count = 0
            for substitute_i in range(n_reference_years):
                if substitute_i == target_ref_i:
                    continue
                thresholds = threshold_bank[target_ref_i, substitute_i, :, cell]
                for group_i in range(group_start, group_stop):
                    output[group_i, cell] += count_exceedances(
                        array_inputs.flat_study,
                        thresholds,
                        temporal_indexing.study_day_of_years,
                        temporal_indexing.output_starts[group_i],
                        temporal_indexing.output_lengths[group_i],
                        cell,
                        temporal_indexing.year_max_day_of_years[year_i],
                        op_code,
                    )
                substitute_count += 1
            for group_i in range(group_start, group_stop):
                output[group_i, cell] /= substitute_count
    out = build_bootstrap_output(
        flat_result=output,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="d",
    )
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Prototype a compiled per-target threshold-bank exact count path."""
    if not _can_compute_threshold_bank_bootstrap_count(study, threshold, freq):
        return None
    if _bootstrap_count_threshold_bank_kernel is None:
        return None
    prepared_inputs = build_bootstrap_prepared_inputs(
        study,
        threshold,
        freq,
        dtype=np.float64,
    )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    result = _bootstrap_count_threshold_bank_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="d",
    )
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_bootstrap_exceedance_sum(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    *,
    prepared_inputs: BootstrapPreparedInputs | None = None,
) -> DataArray | None:
    """Compute bootstrap sums of exceedance-day values with the optimized path."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_exceedance_sum,
        study,
        threshold,
        freq,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        union_mask = compute_doy_percentile_bootstrap_union_exceedance_mask(
            study,
            threshold,
            freq,
            prepared_inputs=prepared_inputs,
        )
        if union_mask is None:
            return None
        result = (
            reference_sample.study.where(union_mask).resample(time=freq).sum(dim="time")
        )
        result.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
        return result.assign_coords(percentiles=threshold.percentile_coord().item())
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        reference_sample.study,
        threshold,
        min_threshold,
    )
    result = _bootstrap_sum_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        _use_order_stat_thresholds(reference_sample.study),
        min_threshold,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units=reference_sample.study.attrs.get("units", ""),
    )
    out = out.astype(reference_sample.study.dtype)
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_bootstrap_union_exceedance_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    *,
    prepared_inputs: BootstrapPreparedInputs | None = None,
) -> DataArray | None:
    """Count union exceedance days for thresholded bootstrap mean reducers."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_union_exceedance_count,
        study,
        threshold,
        freq,
        percentiles_after_time=True,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        union_mask = compute_doy_percentile_bootstrap_union_exceedance_mask(
            study,
            threshold,
            freq,
            prepared_inputs=prepared_inputs,
        )
        if union_mask is None:
            return None
        result = union_mask.resample(time=freq).sum(dim="time")
        result.attrs["units"] = "d"
        return result.assign_coords(percentiles=threshold.percentile_coord().item())
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        reference_sample.study,
        threshold,
        min_threshold,
    )
    result = _bootstrap_union_count_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        _use_order_stat_thresholds(reference_sample.study),
        min_threshold,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="d",
    )
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_bootstrap_union_exceedance_mask(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    *,
    prepared_inputs: BootstrapPreparedInputs | None = None,
) -> DataArray | None:
    """Compute the daily union exceedance mask for spell-style bootstrap reducers."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_union_exceedance_mask,
        study,
        threshold,
        freq,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    import xarray as xr  # noqa: PLC0415

    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        reference_sample.study,
        threshold,
        min_threshold,
    )
    flat_result = _bootstrap_union_mask_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.study_year_starts,
        temporal_indexing.study_year_lengths,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        _use_order_stat_thresholds(reference_sample.study),
        min_threshold,
    )
    data = flat_result.reshape(reference_sample.study.shape)
    out = xr.DataArray(
        data,
        dims=reference_sample.study.dims,
        coords=reference_sample.study.coords,
        attrs={"climatology_bounds": reference_sample.climatology_bounds},
    )
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_bootstrap_mean_threshold(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    *,
    prepared_inputs: BootstrapPreparedInputs | None = None,
) -> DataArray | None:
    """Compute the daily mean threshold produced by overlap substitutions."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_mean_threshold,
        study,
        threshold,
        freq,
    )
    if multiple is not None:
        return multiple
    if not is_optimized_doy_percentile_threshold_supported(study, threshold, freq):
        return None
    import xarray as xr  # noqa: PLC0415

    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        reference_sample.study,
        threshold,
        min_threshold,
    )
    flat_result = _bootstrap_mean_threshold_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.study_year_starts,
        temporal_indexing.study_year_lengths,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _use_order_stat_thresholds(reference_sample.study),
        min_threshold,
    )
    out = xr.DataArray(
        flat_result.reshape(reference_sample.study.shape),
        dims=reference_sample.study.dims,
        coords=reference_sample.study.coords,
        attrs={
            "units": reference_sample.study.attrs.get("units", ""),
            REFERENCE_PERIOD_ID: reference_sample.climatology_bounds,
        },
    )
    return out.expand_dims(
        percentiles=threshold.percentile_coord().values,
        axis=-1,
    )


def compute_doy_percentile_bootstrap_exceedance_average(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute bootstrap averages of exceedance-day values with the optimized path."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_exceedance_average,
        study,
        threshold,
        freq,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        union_mask = compute_doy_percentile_bootstrap_union_exceedance_mask(
            study,
            threshold,
            freq,
            prepared_inputs=BootstrapPreparedInputs(
                reference_sample=reference_sample,
                temporal_indexing=temporal_indexing,
                array_inputs=build_bootstrap_array_inputs(
                    reference_sample,
                    dtype=bootstrap_array_dtype(reference_sample.study),
                ),
            ),
        )
        if union_mask is None:
            return None
        result = (
            reference_sample.study.where(union_mask)
            .resample(time=freq)
            .mean(dim="time")
        )
        result.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
        return result.assign_coords(percentiles=threshold.percentile_coord().item())
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        reference_sample.study,
        threshold,
        min_threshold,
    )
    result = _bootstrap_average_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        _use_order_stat_thresholds(reference_sample.study),
        min_threshold,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units=reference_sample.study.attrs.get("units", ""),
    )
    out = out.astype(reference_sample.study.dtype)
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_bootstrap_fraction_of_total(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute bootstrap fractions of total with the optimized path."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_bootstrap_fraction_of_total,
        study,
        threshold,
        freq,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        return None
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    min_threshold = (
        np.nan
        if reference_sample.threshold_floor_in_reference_units is None
        else float(reference_sample.threshold_floor_in_reference_units)
    )
    flat_nominal_thresholds = _build_nominal_full_thresholds(
        reference_sample.study,
        threshold,
        min_threshold,
    )
    result = _bootstrap_fraction_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        flat_nominal_thresholds,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        _use_order_stat_thresholds(reference_sample.study),
        min_threshold,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="1",
    )
    out = out.astype(reference_sample.study.dtype)
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_scalar_bounded_bootstrap_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
) -> DataArray | None:
    """Compute bounded bootstrap counts for one percentile and one scalar guard."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_scalar_bounded_bootstrap_count,
        study,
        threshold,
        freq,
        percentiles_after_time=True,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        return None
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    result = _bootstrap_bounded_count_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
        np.float32(scalar_bound),
        scalar_op_code,
        logical_link_code,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="d",
    )
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
) -> DataArray | None:
    """Compute bounded bootstrap sums for one percentile and one scalar guard."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum,
        study,
        threshold,
        freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        return None
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    result = _bootstrap_bounded_sum_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
        np.float32(scalar_bound),
        scalar_op_code,
        logical_link_code,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units=reference_sample.study.attrs.get("units", ""),
    )
    out = out.astype(reference_sample.study.dtype)
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
) -> DataArray | None:
    """Compute bounded bootstrap averages for one percentile and one scalar guard."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average,
        study,
        threshold,
        freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        return None
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    result = _bootstrap_bounded_average_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
        np.float32(scalar_bound),
        scalar_op_code,
        logical_link_code,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units=reference_sample.study.attrs.get("units", ""),
    )
    out = out.astype(reference_sample.study.dtype)
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
) -> DataArray | None:
    """Compute bounded bootstrap fractions for one percentile and one scalar guard."""
    multiple = _compute_multiple_percentiles(
        compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total,
        study,
        threshold,
        freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
    )
    if multiple is not None:
        return multiple
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    if temporal_indexing.output_groups_cross_bootstrap_epochs:
        return None
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=bootstrap_array_dtype(reference_sample.study),
    )
    result = _bootstrap_bounded_fraction_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
        temporal_indexing.sample_indices_by_day_of_year,
        temporal_indexing.reference_index_year,
        temporal_indexing.reference_index_position,
        temporal_indexing.substitute_alignment,
        temporal_indexing.output_starts,
        temporal_indexing.output_lengths,
        temporal_indexing.year_group_starts,
        temporal_indexing.year_group_stops,
        temporal_indexing.year_max_day_of_years,
        temporal_indexing.year_to_reference_index,
        temporal_indexing.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
        np.float32(scalar_bound),
        scalar_op_code,
        logical_link_code,
    )
    out = build_bootstrap_output(
        flat_result=result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=array_inputs.spatial_shape,
        units="1",
    )
    out = out.astype(reference_sample.study.dtype)
    out.attrs[REFERENCE_PERIOD_ID] = reference_sample.climatology_bounds
    del out.attrs["climatology_bounds"]
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def _can_compute_optimized_bootstrap(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> bool:
    return is_optimized_doy_percentile_count_supported(study, threshold, freq)


def _can_compute_threshold_bank_bootstrap_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> bool:
    if _can_compute_optimized_bootstrap(study, threshold, freq):
        return True
    time_index = study.indexes["time"]
    return (
        isinstance(time_index, CFTimeIndex)
        and threshold.is_doy_per_threshold
        and threshold.threshold_min_value is None
        and threshold.percentile_coord().size == 1
    )


def _operator_code(operator: Operator | str) -> int:
    operand = operator.operand if isinstance(operator, Operator) else str(operator)
    return {">": 0, ">=": 1, "<": 2, "<=": 3}.get(operand, -1)


try:
    from numba import njit, prange
except Exception:  # noqa: BLE001
    njit = None
    prange = range


if njit is not None:

    @njit(cache=True)
    def _fill_sorted_nominal_values(
        flat_ref,
        sample_indices,
        doy_i,
        cell,
        base_buf,
    ):
        n = 0
        for sample_i in range(sample_indices.shape[1]):
            ref_i = sample_indices[doy_i, sample_i]
            if ref_i < 0:
                continue
            value = flat_ref[ref_i, cell]
            if not np.isnan(value):
                base_buf[n] = value
                n += 1
        if n > 1:
            base_buf[:n].sort()
        return n

    @njit(cache=True)
    def _fill_sorted_removed_values(
        flat_ref,
        sample_indices,
        index_year,
        doy_i,
        cell,
        target_ref_i,
        removed_buf,
    ):
        if target_ref_i < 0:
            return 0
        n = 0
        for sample_i in range(sample_indices.shape[1]):
            ref_i = sample_indices[doy_i, sample_i]
            if ref_i < 0 or index_year[ref_i] != target_ref_i:
                continue
            value = flat_ref[ref_i, cell]
            if not np.isnan(value):
                removed_buf[n] = value
                n += 1
        if n > 1:
            removed_buf[:n].sort()
        return n

    @njit(cache=True)
    def _fill_sorted_inserted_values(
        flat_ref,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        doy_i,
        cell,
        target_ref_i,
        substitute_i,
        inserted_buf,
    ):
        if target_ref_i < 0 or substitute_i < 0:
            return 0
        n = 0
        for sample_i in range(sample_indices.shape[1]):
            ref_i = sample_indices[doy_i, sample_i]
            if ref_i < 0 or index_year[ref_i] != target_ref_i:
                continue
            mapped_i = substitute_aligned[target_ref_i, substitute_i, index_pos[ref_i]]
            if mapped_i < 0:
                continue
            value = flat_ref[mapped_i, cell]
            if not np.isnan(value):
                inserted_buf[n] = value
                n += 1
        if n > 1:
            inserted_buf[:n].sort()
        return n

    @njit(cache=True)
    def _value_at_adjusted_rank(
        base_buf,
        base_n,
        removed_buf,
        removed_n,
        inserted_buf,
        inserted_n,
        rank,
    ):
        base_i = 0
        removed_i = 0
        inserted_i = 0
        current_rank = -1
        while True:
            while (
                base_i < base_n
                and removed_i < removed_n
                and base_buf[base_i] == removed_buf[removed_i]
            ):
                base_i += 1
                removed_i += 1
            has_base = base_i < base_n
            has_inserted = inserted_i < inserted_n
            if not has_base and not has_inserted:
                return np.nan
            if has_inserted and (
                not has_base or inserted_buf[inserted_i] <= base_buf[base_i]
            ):
                value = inserted_buf[inserted_i]
                inserted_i += 1
            else:
                value = base_buf[base_i]
                base_i += 1
            current_rank += 1
            if current_rank == rank:
                return value

    @njit(cache=True)
    def _method8_adjusted_quantile(
        base_buf,
        base_n,
        removed_buf,
        removed_n,
        inserted_buf,
        inserted_n,
        quantile,
        alpha,
        beta,
    ):
        n = base_n - removed_n + inserted_n
        if n <= 0:
            return np.nan
        if n == 1:
            return _value_at_adjusted_rank(
                base_buf,
                base_n,
                removed_buf,
                removed_n,
                inserted_buf,
                inserted_n,
                0,
            )
        virtual = n * quantile + (alpha + quantile * (1.0 - alpha - beta)) - 1.0
        if virtual >= n - 1:
            return _value_at_adjusted_rank(
                base_buf,
                base_n,
                removed_buf,
                removed_n,
                inserted_buf,
                inserted_n,
                n - 1,
            )
        if virtual < 0.0:
            return _value_at_adjusted_rank(
                base_buf,
                base_n,
                removed_buf,
                removed_n,
                inserted_buf,
                inserted_n,
                0,
            )
        previous = int(np.floor(virtual))
        gamma = virtual - previous
        left = _value_at_adjusted_rank(
            base_buf,
            base_n,
            removed_buf,
            removed_n,
            inserted_buf,
            inserted_n,
            previous,
        )
        right = _value_at_adjusted_rank(
            base_buf,
            base_n,
            removed_buf,
            removed_n,
            inserted_buf,
            inserted_n,
            previous + 1,
        )
        diff = right - left
        if gamma >= 0.5:
            return right - diff * (1.0 - gamma)
        return left + diff * gamma

    @njit(cache=True)
    def _build_order_stat_threshold_series_for_cell(
        flat_ref,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        target_ref_i,
        substitute_i,
        cell,
        quantile,
        alpha,
        beta,
        min_threshold,
        max_samples,
    ):
        thresholds = np.empty(sample_indices.shape[0], dtype=np.float64)
        base_buf = np.empty(max_samples, dtype=np.float64)
        removed_buf = np.empty(max_samples, dtype=np.float64)
        inserted_buf = np.empty(max_samples, dtype=np.float64)
        for doy_i in range(sample_indices.shape[0]):
            base_n = _fill_sorted_nominal_values(
                flat_ref,
                sample_indices,
                doy_i,
                cell,
                base_buf,
            )
            removed_n = _fill_sorted_removed_values(
                flat_ref,
                sample_indices,
                index_year,
                doy_i,
                cell,
                target_ref_i,
                removed_buf,
            )
            inserted_n = _fill_sorted_inserted_values(
                flat_ref,
                sample_indices,
                index_year,
                index_pos,
                substitute_aligned,
                doy_i,
                cell,
                target_ref_i,
                substitute_i,
                inserted_buf,
            )
            threshold_value = _method8_adjusted_quantile(
                base_buf,
                base_n,
                removed_buf,
                removed_n,
                inserted_buf,
                inserted_n,
                quantile,
                alpha,
                beta,
            )
            if not np.isnan(min_threshold) and (
                np.isnan(threshold_value) or threshold_value <= min_threshold
            ):
                threshold_value = min_threshold
            thresholds[doy_i] = threshold_value
        return thresholds

    @njit(parallel=True, cache=True)
    def _bootstrap_count_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        min_threshold,
    ):
        """Compute yearly bootstrap counts with the compiled order-stat route."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        overlap_reference = flat_ref_raw
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                if (
                    year_max_doys[year_i] == 366
                    and flat_nominal_thresholds.shape[0] == 366
                ):
                    # Reuse the prepared 366-day threshold field directly for
                    # non-reference leap years so count comparisons match the
                    # public threshold workflow exactly.
                    _write_count_groups_for_cell_with_full_thresholds(
                        out,
                        flat_study,
                        flat_nominal_thresholds,
                        study_doys,
                        study_starts,
                        study_lengths,
                        group_start,
                        group_stop,
                        cell,
                        op_code,
                    )
                    continue
                thresholds = _build_exact_bootstrap_threshold_series_for_cell(
                    flat_ref_masked,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    -1,
                    -1,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    use_order_stat_thresholds,
                    min_threshold,
                )
                _write_count_groups_for_cell(
                    out,
                    flat_study,
                    thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                )
                continue
            for group_i in range(group_start, group_stop):
                out[group_i, cell] = 0.0
            substitute_count = 0
            for substitute_i in range(n_ref_years):
                if substitute_i == target_ref_i:
                    continue
                thresholds = _build_exact_bootstrap_threshold_series_for_cell(
                    overlap_reference,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    substitute_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    use_order_stat_thresholds,
                    min_threshold,
                )
                _accumulate_count_groups_for_cell(
                    out,
                    flat_study,
                    thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                )
                substitute_count += 1
            _average_count_groups_for_cell(
                out,
                group_start,
                group_stop,
                cell,
                substitute_count,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_count_threshold_bank_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        min_threshold,
    ):
        """Prototype compiled count reduction using a per-target threshold bank."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        for cell in prange(n_cells):
            nominal_thresholds = _build_bootstrap_threshold_series_for_cell(
                flat_ref_masked,
                sample_indices,
                index_year,
                index_pos,
                substitute_aligned,
                -1,
                -1,
                cell,
                max_samples,
                quantile,
                alpha,
                beta,
                min_threshold,
            )
            overlap_reference = flat_ref_raw
            threshold_bank = np.full(
                (n_ref_years, n_ref_years, sample_indices.shape[0]),
                np.nan,
                dtype=np.float64,
            )
            for target_ref_i in range(n_ref_years):
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    threshold_bank[target_ref_i, substitute_i, :] = (
                        _build_bootstrap_threshold_series_for_cell(
                            overlap_reference,
                            sample_indices,
                            index_year,
                            index_pos,
                            substitute_aligned,
                            target_ref_i,
                            substitute_i,
                            cell,
                            max_samples,
                            quantile,
                            alpha,
                            beta,
                            min_threshold,
                        )
                    )
            for year_i in range(n_years):
                target_ref_i = year_to_ref[year_i]
                group_start = year_group_starts[year_i]
                group_stop = year_group_stops[year_i]
                if target_ref_i < 0:
                    _write_count_groups_for_cell(
                        out,
                        flat_study,
                        nominal_thresholds,
                        study_doys,
                        study_starts,
                        study_lengths,
                        group_start,
                        group_stop,
                        cell,
                        year_max_doys[year_i],
                        op_code,
                    )
                    continue
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = 0.0
                substitute_count = 0
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    _accumulate_count_groups_for_cell(
                        out,
                        flat_study,
                        threshold_bank[target_ref_i, substitute_i, :],
                        study_doys,
                        study_starts,
                        study_lengths,
                        group_start,
                        group_stop,
                        cell,
                        year_max_doys[year_i],
                        op_code,
                    )
                    substitute_count += 1
                _average_count_groups_for_cell(
                    out,
                    group_start,
                    group_stop,
                    cell,
                    substitute_count,
                )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_sum_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        min_threshold,
    ):
        """Compute yearly bootstrap exceedance sums from shared thresholds."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                thresholds = _build_nominal_daily_thresholds_for_cell(
                    flat_ref_masked,
                    flat_nominal_thresholds,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                )
            else:
                thresholds = _build_overlap_daily_union_thresholds_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                    flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT
                    or np.isnan(min_threshold),
                )
            _write_sum_groups_for_cell_with_daily_thresholds(
                out,
                flat_study,
                thresholds,
                study_doys,
                study_starts,
                study_lengths,
                group_start,
                group_stop,
                cell,
                op_code,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_union_count_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        min_threshold,
    ):
        """Count union exceedance days from shared bootstrap thresholds."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                thresholds = _build_nominal_daily_thresholds_for_cell(
                    flat_ref_masked,
                    flat_nominal_thresholds,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                )
            else:
                thresholds = _build_overlap_daily_union_thresholds_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                    flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT
                    or np.isnan(min_threshold),
                )
            _write_count_groups_for_cell_with_daily_thresholds(
                out,
                flat_study,
                thresholds,
                study_doys,
                study_starts,
                study_lengths,
                group_start,
                group_stop,
                cell,
                op_code,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_union_mask_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_year_starts,
        study_year_lengths,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        min_threshold,
    ):
        """Build the daily union exceedance mask for spell-style bootstrap reducers."""
        n_years = len(year_to_ref)
        n_times = flat_study.shape[0]
        n_cells = flat_study.shape[1]
        out = np.empty((n_times, n_cells), dtype=np.float32)
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            year_start = study_year_starts[year_i]
            year_length = study_year_lengths[year_i]
            if target_ref_i < 0:
                thresholds = _build_nominal_daily_thresholds_for_cell(
                    flat_ref_masked,
                    flat_nominal_thresholds,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                )
            else:
                thresholds = _build_overlap_daily_union_thresholds_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                    flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT
                    or np.isnan(min_threshold),
                )
            _write_union_mask_year_for_cell_with_daily_thresholds(
                out,
                flat_study,
                thresholds,
                study_doys,
                year_start,
                year_length,
                cell,
                op_code,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_mean_threshold_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_year_starts,
        study_year_lengths,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        use_order_stat_thresholds,
        min_threshold,
    ):
        n_years = len(year_to_ref)
        n_times = len(study_doys)
        n_cells = flat_ref_raw.shape[1]
        out = np.empty((n_times, n_cells), dtype=np.float64)
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            if target_ref_i < 0:
                thresholds = _build_nominal_daily_thresholds_for_cell(
                    flat_ref_masked,
                    flat_nominal_thresholds,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    0,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                )
            else:
                thresholds = _build_overlap_daily_mean_thresholds_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                    flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT
                    or np.isnan(min_threshold),
                )
            start = study_year_starts[year_i]
            length = study_year_lengths[year_i]
            for offset in range(length):
                doy = study_doys[start + offset]
                out[start + offset, cell] = thresholds[doy - 1]
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_average_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        min_threshold,
    ):
        """Compute yearly bootstrap exceedance averages from shared thresholds."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                thresholds = _build_nominal_daily_thresholds_for_cell(
                    flat_ref_masked,
                    flat_nominal_thresholds,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                )
            else:
                thresholds = _build_overlap_daily_union_thresholds_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                    flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT
                    or np.isnan(min_threshold),
                )
            _write_average_groups_for_cell_with_daily_thresholds(
                out,
                flat_study,
                thresholds,
                study_doys,
                study_starts,
                study_lengths,
                group_start,
                group_stop,
                cell,
                op_code,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_fraction_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        min_threshold,
    ):
        """Compute yearly bootstrap fractions of total from shared thresholds."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                thresholds = _build_nominal_daily_thresholds_for_cell(
                    flat_ref_masked,
                    flat_nominal_thresholds,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                )
            else:
                thresholds = _build_overlap_daily_union_thresholds_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    op_code,
                    use_order_stat_thresholds,
                    year_max_doys[year_i],
                    min_threshold,
                    flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT
                    or np.isnan(min_threshold),
                )
            _write_fraction_groups_for_cell_with_daily_thresholds(
                out,
                flat_study,
                thresholds,
                study_doys,
                study_starts,
                study_lengths,
                group_start,
                group_stop,
                cell,
                op_code,
                min_threshold,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_bounded_count_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        min_threshold,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            overlap_reference = flat_ref_raw
            if target_ref_i < 0:
                thresholds = _build_reducer_threshold_series_for_cell(
                    _build_bootstrap_threshold_series_for_cell(
                        flat_ref_masked,
                        sample_indices,
                        index_year,
                        index_pos,
                        substitute_aligned,
                        -1,
                        -1,
                        cell,
                        max_samples,
                        quantile,
                        alpha,
                        beta,
                        min_threshold,
                    )
                )
                _write_bounded_count_groups_for_cell(
                    out,
                    flat_study,
                    thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
            else:
                union_thresholds = _initialize_union_threshold_series(
                    op_code,
                    sample_indices.shape[0],
                )
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_reducer_threshold_series_for_cell(
                        _build_bootstrap_threshold_series_for_cell(
                            overlap_reference,
                            sample_indices,
                            index_year,
                            index_pos,
                            substitute_aligned,
                            target_ref_i,
                            substitute_i,
                            cell,
                            max_samples,
                            quantile,
                            alpha,
                            beta,
                            min_threshold,
                        )
                    )
                    _update_union_threshold_series(
                        union_thresholds,
                        thresholds,
                        op_code,
                    )
                _write_bounded_count_groups_for_cell(
                    out,
                    flat_study,
                    union_thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_bounded_sum_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        min_threshold,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            overlap_reference = flat_ref_raw
            if target_ref_i < 0:
                thresholds = _build_reducer_threshold_series_for_cell(
                    _build_bootstrap_threshold_series_for_cell(
                        flat_ref_masked,
                        sample_indices,
                        index_year,
                        index_pos,
                        substitute_aligned,
                        -1,
                        -1,
                        cell,
                        max_samples,
                        quantile,
                        alpha,
                        beta,
                        min_threshold,
                    )
                )
                _write_bounded_sum_groups_for_cell(
                    out,
                    flat_study,
                    thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
            else:
                union_thresholds = _initialize_union_threshold_series(
                    op_code,
                    sample_indices.shape[0],
                )
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_reducer_threshold_series_for_cell(
                        _build_bootstrap_threshold_series_for_cell(
                            overlap_reference,
                            sample_indices,
                            index_year,
                            index_pos,
                            substitute_aligned,
                            target_ref_i,
                            substitute_i,
                            cell,
                            max_samples,
                            quantile,
                            alpha,
                            beta,
                            min_threshold,
                        )
                    )
                    _update_union_threshold_series(
                        union_thresholds,
                        thresholds,
                        op_code,
                    )
                _write_bounded_sum_groups_for_cell(
                    out,
                    flat_study,
                    union_thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_bounded_average_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        min_threshold,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            overlap_reference = flat_ref_raw
            if target_ref_i < 0:
                thresholds = _build_reducer_threshold_series_for_cell(
                    _build_bootstrap_threshold_series_for_cell(
                        flat_ref_masked,
                        sample_indices,
                        index_year,
                        index_pos,
                        substitute_aligned,
                        -1,
                        -1,
                        cell,
                        max_samples,
                        quantile,
                        alpha,
                        beta,
                        min_threshold,
                    )
                )
                _write_bounded_average_groups_for_cell(
                    out,
                    flat_study,
                    thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
            else:
                union_thresholds = _initialize_union_threshold_series(
                    op_code,
                    sample_indices.shape[0],
                )
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_reducer_threshold_series_for_cell(
                        _build_bootstrap_threshold_series_for_cell(
                            overlap_reference,
                            sample_indices,
                            index_year,
                            index_pos,
                            substitute_aligned,
                            target_ref_i,
                            substitute_i,
                            cell,
                            max_samples,
                            quantile,
                            alpha,
                            beta,
                            min_threshold,
                        )
                    )
                    _update_union_threshold_series(
                        union_thresholds,
                        thresholds,
                        op_code,
                    )
                _write_bounded_average_groups_for_cell(
                    out,
                    flat_study,
                    union_thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_bounded_fraction_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        study_starts,
        study_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        min_threshold,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            overlap_reference = flat_ref_raw
            if target_ref_i < 0:
                thresholds = _build_reducer_threshold_series_for_cell(
                    _build_bootstrap_threshold_series_for_cell(
                        flat_ref_masked,
                        sample_indices,
                        index_year,
                        index_pos,
                        substitute_aligned,
                        -1,
                        -1,
                        cell,
                        max_samples,
                        quantile,
                        alpha,
                        beta,
                        min_threshold,
                    )
                )
                _write_bounded_fraction_groups_for_cell(
                    out,
                    flat_study,
                    thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
            else:
                union_thresholds = _initialize_union_threshold_series(
                    op_code,
                    sample_indices.shape[0],
                )
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_reducer_threshold_series_for_cell(
                        _build_bootstrap_threshold_series_for_cell(
                            overlap_reference,
                            sample_indices,
                            index_year,
                            index_pos,
                            substitute_aligned,
                            target_ref_i,
                            substitute_i,
                            cell,
                            max_samples,
                            quantile,
                            alpha,
                            beta,
                            min_threshold,
                        )
                    )
                    _update_union_threshold_series(
                        union_thresholds,
                        thresholds,
                        op_code,
                    )
                _write_bounded_fraction_groups_for_cell(
                    out,
                    flat_study,
                    union_thresholds,
                    study_doys,
                    study_starts,
                    study_lengths,
                    group_start,
                    group_stop,
                    cell,
                    year_max_doys[year_i],
                    op_code,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                )
        return out

    @njit(cache=True)
    def _build_bootstrap_threshold_series_for_cell(
        flat_ref,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        target_ref_i,
        substitute_i,
        cell,
        max_samples,
        quantile,
        alpha,
        beta,
        min_threshold,
    ):
        thresholds = np.empty(sample_indices.shape[0], dtype=np.float64)
        buf = np.empty(max_samples, dtype=np.float64)
        for doy_i in range(sample_indices.shape[0]):
            threshold_value = _quantile_for_doy_cell(
                flat_ref,
                sample_indices,
                index_year,
                index_pos,
                substitute_aligned,
                target_ref_i,
                substitute_i,
                doy_i,
                cell,
                buf,
                quantile,
                alpha,
                beta,
            )
            if not np.isnan(min_threshold) and (
                np.isnan(threshold_value) or threshold_value <= min_threshold
            ):
                threshold_value = min_threshold
            thresholds[doy_i] = threshold_value
        return thresholds

    @njit(cache=True)
    def _quantile_for_doy_cell(
        flat_ref,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        target_ref_i,
        substitute_i,
        doy_i,
        cell,
        buf,
        quantile,
        alpha,
        beta,
    ):
        n = 0
        for sample_i in range(sample_indices.shape[1]):
            ref_i = sample_indices[doy_i, sample_i]
            if ref_i < 0:
                continue
            mapped_i = ref_i
            if target_ref_i >= 0 and index_year[ref_i] == target_ref_i:
                mapped_i = substitute_aligned[
                    target_ref_i, substitute_i, index_pos[ref_i]
                ]
            if mapped_i < 0:
                continue
            value = flat_ref[mapped_i, cell]
            if not np.isnan(value):
                buf[n] = value
                n += 1
        return _method8_quantile_select(buf, n, quantile, alpha, beta)

    @njit(cache=True)
    def _method8_quantile_select(buf, n, quantile, alpha, beta):
        if n == 0:
            return np.nan
        if n == 1:
            return buf[0]
        virtual = n * quantile + (alpha + quantile * (1.0 - alpha - beta)) - 1.0
        if virtual >= n - 1:
            return _select_kth(buf, n, n - 1)
        if virtual < 0:
            return _select_kth(buf, n, 0)
        previous = int(np.floor(virtual))
        gamma = virtual - previous
        left = _select_kth(buf, n, previous)
        right = _select_kth(buf, n, previous + 1)
        diff = right - left
        if gamma >= 0.5:
            return right - diff * (1.0 - gamma)
        return left + diff * gamma

    @njit(cache=True)
    def _select_kth(buf, n, k):
        left = 0
        right = n - 1
        while True:
            if left == right:
                return buf[left]
            pivot_index = (left + right) // 2
            pivot_index = _partition(buf, left, right, pivot_index)
            if k == pivot_index:
                return buf[k]
            if k < pivot_index:
                right = pivot_index - 1
            else:
                left = pivot_index + 1

    @njit(cache=True)
    def _partition(buf, left, right, pivot_index):
        pivot_value = buf[pivot_index]
        _swap(buf, pivot_index, right)
        store_index = left
        for i in range(left, right):
            if buf[i] < pivot_value:
                _swap(buf, store_index, i)
                store_index += 1
        _swap(buf, right, store_index)
        return store_index

    @njit(cache=True)
    def _swap(buf, i, j):
        value = buf[i]
        buf[i] = buf[j]
        buf[j] = value

    @njit(cache=True)
    def _count_exceedances(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
    ):
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _compare(value, threshold, op_code):
                count += 1.0
        return count

    @njit(cache=True)
    def _count_exceedances_with_full_thresholds(
        flat_study,
        flat_thresholds,
        study_doys,
        start,
        length,
        cell,
        op_code,
    ):
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = flat_thresholds[doy - 1, cell]
            value = flat_study[start + offset, cell]
            if _compare(value, threshold, op_code):
                count += 1.0
        return count

    @njit(cache=True)
    def _count_exceedances_with_daily_thresholds(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        op_code,
    ):
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            value = flat_study[start + offset, cell]
            if _compare(value, thresholds[doy - 1], op_code):
                count += 1.0
        return count

    @njit(cache=True)
    def _sum_exceedances_with_daily_thresholds(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        op_code,
    ):
        total = np.float32(0.0)
        for offset in range(length):
            doy = study_doys[start + offset]
            value = flat_study[start + offset, cell]
            if _compare(value, thresholds[doy - 1], op_code):
                total = np.float32(total + np.float32(value))
        return float(total)

    @njit(cache=True)
    def _average_exceedances_with_daily_thresholds(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        op_code,
    ):
        total = np.float32(0.0)
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            value = flat_study[start + offset, cell]
            if _compare(value, thresholds[doy - 1], op_code):
                total = np.float32(total + np.float32(value))
                count += 1.0
        if count == 0.0:
            return np.nan
        return float(np.float32(total / np.float32(count)))

    @njit(cache=True)
    def _fraction_with_daily_thresholds(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        op_code,
        min_threshold,
    ):
        exceedance_total = np.float32(0.0)
        total = np.float32(0.0)
        for offset in range(length):
            doy = study_doys[start + offset]
            value = flat_study[start + offset, cell]
            if np.isnan(min_threshold) or _compare(value, min_threshold, op_code):
                total = np.float32(total + np.float32(value))
            if _compare(value, thresholds[doy - 1], op_code):
                exceedance_total = np.float32(exceedance_total + np.float32(value))
        if total == np.float32(0.0):
            return np.nan
        return float(np.float32(exceedance_total / total))

    @njit(cache=True)
    def _count_bounded_exceedances(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _combine_logical_matches(
                _compare(value, threshold, op_code),
                _compare(value, scalar_bound, scalar_op_code),
                logical_link_code,
            ):
                count += 1.0
        return count

    @njit(cache=True)
    def _sum_exceedances(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
    ):
        total = np.float32(0.0)
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _compare(value, threshold, op_code):
                total = np.float32(total + np.float32(value))
        return float(total)

    @njit(cache=True)
    def _sum_bounded_exceedances(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        total = np.float32(0.0)
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _combine_logical_matches(
                _compare(value, threshold, op_code),
                _compare(value, scalar_bound, scalar_op_code),
                logical_link_code,
            ):
                total = np.float32(total + np.float32(value))
        return float(total)

    @njit(cache=True)
    def _average_exceedances(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
    ):
        total = np.float32(0.0)
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _compare(value, threshold, op_code):
                total = np.float32(total + np.float32(value))
                count += 1.0
        if count == 0.0:
            return np.nan
        return float(np.float32(total / np.float32(count)))

    @njit(cache=True)
    def _average_bounded_exceedances(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        total = np.float32(0.0)
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _combine_logical_matches(
                _compare(value, threshold, op_code),
                _compare(value, scalar_bound, scalar_op_code),
                logical_link_code,
            ):
                total = np.float32(total + np.float32(value))
                count += 1.0
        if count == 0.0:
            return np.nan
        return float(np.float32(total / np.float32(count)))

    @njit(cache=True)
    def _fraction_of_total(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
        min_threshold,
    ):
        exceedance_total = np.float32(0.0)
        total = np.float32(0.0)
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if np.isnan(min_threshold) or _compare(value, min_threshold, op_code):
                total = np.float32(total + np.float32(value))
            if _compare(value, threshold, op_code):
                exceedance_total = np.float32(exceedance_total + np.float32(value))
        if total == np.float32(0.0):
            return np.nan
        return float(np.float32(exceedance_total / total))

    @njit(cache=True)
    def _bounded_fraction_of_total(
        flat_study,
        thresholds,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        exceedance_total = np.float32(0.0)
        total = np.float32(0.0)
        for offset in range(length):
            doy = study_doys[start + offset]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            total = np.float32(total + np.float32(value))
            if _combine_logical_matches(
                _compare(value, threshold, op_code),
                _compare(value, scalar_bound, scalar_op_code),
                logical_link_code,
            ):
                exceedance_total = np.float32(exceedance_total + np.float32(value))
        if total == np.float32(0.0):
            return np.nan
        return float(np.float32(exceedance_total / total))

    @njit(cache=True)
    def _initialize_union_threshold_series(op_code, day_count):
        if op_code in (0, 1):
            return np.full(day_count, np.inf, dtype=np.float64)
        return np.full(
            day_count,
            -np.inf,
            dtype=np.float64,
        )

    @njit(cache=True)
    def _initialize_daily_union_thresholds(op_code, day_count):
        if op_code in (0, 1):
            return np.full(day_count, np.inf, dtype=np.float64)
        return np.full(day_count, -np.inf, dtype=np.float64)

    @njit(cache=True)
    def _update_daily_union_thresholds(
        union_thresholds,
        thresholds,
        op_code,
        max_target_doy,
        min_threshold,
        interpolate_missing,
    ):
        prepared_thresholds = _prepare_thresholds_for_calendar_interpolation(
            thresholds,
            min_threshold,
            interpolate_missing,
        )
        for doy_i in range(max_target_doy):
            threshold_value = _adjusted_threshold(
                prepared_thresholds,
                doy_i + 1,
                max_target_doy,
            )
            if not np.isnan(min_threshold) and (
                np.isnan(threshold_value) or threshold_value <= min_threshold
            ):
                threshold_value = min_threshold
            if np.isnan(threshold_value):
                continue
            current_value = union_thresholds[doy_i]
            if op_code in (0, 1):
                if threshold_value < current_value:
                    union_thresholds[doy_i] = threshold_value
            elif threshold_value > current_value:
                union_thresholds[doy_i] = threshold_value

    @njit(cache=True)
    def _prepare_thresholds_for_calendar_interpolation(
        thresholds,
        min_threshold,
        interpolate_missing,
    ):
        if interpolate_missing:
            return _interpolate_missing_thresholds(thresholds)
        prepared = thresholds.copy()
        if np.isnan(min_threshold):
            return prepared
        for threshold_i in range(len(prepared)):
            if (
                np.isnan(prepared[threshold_i])
                or prepared[threshold_i] <= min_threshold
            ):
                prepared[threshold_i] = min_threshold
        return prepared

    @njit(cache=True)
    def _interpolate_missing_thresholds(thresholds):
        filled = thresholds.copy()
        for i in range(len(filled)):
            if not np.isnan(filled[i]):
                continue
            left = i - 1
            while left >= 0 and np.isnan(filled[left]):
                left -= 1
            right = i + 1
            while right < len(filled) and np.isnan(filled[right]):
                right += 1
            if left >= 0 and right < len(filled):
                weight = (i - left) / (right - left)
                filled[i] = filled[left] + weight * (filled[right] - filled[left])
        return filled

    @njit(cache=True)
    def _copy_nominal_daily_thresholds(
        flat_nominal_thresholds,
        cell,
        op_code,
        max_target_doy,
    ):
        thresholds = _initialize_daily_union_thresholds(op_code, max_target_doy)
        for doy_i in range(max_target_doy):
            threshold_value = flat_nominal_thresholds[doy_i, cell]
            if not np.isnan(threshold_value):
                thresholds[doy_i] = threshold_value
        return thresholds

    @njit(cache=True)
    def _build_reducer_threshold_series_for_cell(
        thresholds,
        preserve_precision=False,
    ):
        converted = np.empty(len(thresholds), dtype=np.float64)
        for day_i in range(len(thresholds)):
            if preserve_precision:
                converted[day_i] = thresholds[day_i]
            else:
                converted[day_i] = np.float32(thresholds[day_i])
        return converted

    @njit(cache=True)
    def _build_exact_bootstrap_threshold_series_for_cell(
        flat_ref,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        target_ref_i,
        substitute_i,
        cell,
        max_samples,
        quantile,
        alpha,
        beta,
        use_order_stat_thresholds,
        min_threshold,
    ):
        if use_order_stat_thresholds:
            return _build_order_stat_threshold_series_for_cell(
                flat_ref,
                sample_indices,
                index_year,
                index_pos,
                substitute_aligned,
                target_ref_i,
                substitute_i,
                cell,
                quantile,
                alpha,
                beta,
                min_threshold,
                max_samples,
            )
        return _build_bootstrap_threshold_series_for_cell(
            flat_ref,
            sample_indices,
            index_year,
            index_pos,
            substitute_aligned,
            target_ref_i,
            substitute_i,
            cell,
            max_samples,
            quantile,
            alpha,
            beta,
            min_threshold,
        )

    @njit(cache=True)
    def _build_nominal_daily_thresholds_for_cell(
        flat_ref_masked,
        flat_nominal_thresholds,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        cell,
        max_samples,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        max_target_doy,
        min_threshold,
    ):
        if flat_nominal_thresholds.shape[0] == LEAP_YEAR_DAY_COUNT:
            return _copy_nominal_daily_thresholds(
                flat_nominal_thresholds,
                cell,
                op_code,
                max_target_doy,
            )
        thresholds = _build_reducer_threshold_series_for_cell(
            _build_exact_bootstrap_threshold_series_for_cell(
                flat_ref_masked,
                sample_indices,
                index_year,
                index_pos,
                substitute_aligned,
                -1,
                -1,
                cell,
                max_samples,
                quantile,
                alpha,
                beta,
                use_order_stat_thresholds,
                np.nan,
            ),
            use_order_stat_thresholds,
        )
        daily_thresholds = _initialize_daily_union_thresholds(
            op_code,
            max_target_doy,
        )
        _update_daily_union_thresholds(
            daily_thresholds,
            thresholds,
            op_code,
            max_target_doy,
            min_threshold,
            np.isnan(min_threshold),
        )
        return daily_thresholds

    @njit(cache=True)
    def _build_overlap_daily_union_thresholds_for_cell(
        flat_ref_raw,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        target_ref_i,
        cell,
        max_samples,
        quantile,
        alpha,
        beta,
        op_code,
        use_order_stat_thresholds,
        max_target_doy,
        min_threshold,
        interpolate_missing,
    ):
        daily_thresholds = _initialize_daily_union_thresholds(
            op_code,
            max_target_doy,
        )
        for substitute_i in range(substitute_aligned.shape[1]):
            if substitute_i == target_ref_i:
                continue
            thresholds = _build_reducer_threshold_series_for_cell(
                _build_exact_bootstrap_threshold_series_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    substitute_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    use_order_stat_thresholds,
                    np.nan,
                ),
                use_order_stat_thresholds,
            )
            _update_daily_union_thresholds(
                daily_thresholds,
                thresholds,
                op_code,
                max_target_doy,
                min_threshold,
                interpolate_missing,
            )
        return daily_thresholds

    @njit(cache=True)
    def _build_overlap_daily_mean_thresholds_for_cell(
        flat_ref_raw,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        target_ref_i,
        cell,
        max_samples,
        quantile,
        alpha,
        beta,
        use_order_stat_thresholds,
        max_target_doy,
        min_threshold,
        interpolate_missing,
    ):
        daily_thresholds = np.zeros(max_target_doy, dtype=np.float64)
        counts = np.zeros(max_target_doy, dtype=np.int64)
        for substitute_i in range(substitute_aligned.shape[1]):
            if substitute_i == target_ref_i:
                continue
            thresholds = _build_reducer_threshold_series_for_cell(
                _build_exact_bootstrap_threshold_series_for_cell(
                    flat_ref_raw,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    target_ref_i,
                    substitute_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    use_order_stat_thresholds,
                    np.nan,
                ),
                use_order_stat_thresholds,
            )
            prepared = _prepare_thresholds_for_calendar_interpolation(
                thresholds,
                min_threshold,
                interpolate_missing,
            )
            for doy_i in range(max_target_doy):
                value = _adjusted_threshold(prepared, doy_i + 1, max_target_doy)
                if not np.isnan(min_threshold) and (
                    np.isnan(value) or value <= min_threshold
                ):
                    value = min_threshold
                if not np.isnan(value):
                    daily_thresholds[doy_i] += value
                    counts[doy_i] += 1
        for doy_i in range(max_target_doy):
            if counts[doy_i] == 0:
                daily_thresholds[doy_i] = np.nan
            else:
                daily_thresholds[doy_i] /= counts[doy_i]
        return daily_thresholds

    @njit(cache=True)
    def _update_union_threshold_series(union_thresholds, thresholds, op_code):
        for day_i in range(len(union_thresholds)):
            threshold_value = thresholds[day_i]
            if np.isnan(threshold_value):
                continue
            current_value = union_thresholds[day_i]
            if op_code in (0, 1):
                if threshold_value < current_value:
                    union_thresholds[day_i] = threshold_value
            elif threshold_value > current_value:
                union_thresholds[day_i] = threshold_value

    @njit(cache=True)
    def _write_count_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _count_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
            )

    @njit(cache=True)
    def _write_count_groups_for_cell_with_full_thresholds(
        out,
        flat_study,
        flat_thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _count_exceedances_with_full_thresholds(
                flat_study,
                flat_thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                op_code,
            )

    @njit(cache=True)
    def _write_sum_groups_for_cell_with_daily_thresholds(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _sum_exceedances_with_daily_thresholds(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                op_code,
            )

    @njit(cache=True)
    def _write_count_groups_for_cell_with_daily_thresholds(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _count_exceedances_with_daily_thresholds(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                op_code,
            )

    @njit(cache=True)
    def _write_average_groups_for_cell_with_daily_thresholds(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _average_exceedances_with_daily_thresholds(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                op_code,
            )

    @njit(cache=True)
    def _write_fraction_groups_for_cell_with_daily_thresholds(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        op_code,
        min_threshold,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _fraction_with_daily_thresholds(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                op_code,
                min_threshold,
            )

    @njit(cache=True)
    def _write_bounded_count_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _count_bounded_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
                scalar_bound,
                scalar_op_code,
                logical_link_code,
            )

    @njit(cache=True)
    def _accumulate_count_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] += _count_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
            )

    @njit(cache=True)
    def _write_sum_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _sum_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
            )

    @njit(cache=True)
    def _write_bounded_sum_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _sum_bounded_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
                scalar_bound,
                scalar_op_code,
                logical_link_code,
            )

    @njit(cache=True)
    def _write_average_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _average_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
            )

    @njit(cache=True)
    def _write_bounded_average_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _average_bounded_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
                scalar_bound,
                scalar_op_code,
                logical_link_code,
            )

    @njit(cache=True)
    def _write_fraction_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
        min_threshold,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _fraction_of_total(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
                min_threshold,
            )

    @njit(cache=True)
    def _write_bounded_fraction_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
        scalar_bound,
        scalar_op_code,
        logical_link_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] = _bounded_fraction_of_total(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
                scalar_bound,
                scalar_op_code,
                logical_link_code,
            )

    @njit(cache=True)
    def _write_union_mask_year_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        year_start,
        year_length,
        cell,
        max_target_doy,
        op_code,
    ):
        for offset in range(year_length):
            study_i = year_start + offset
            doy = study_doys[study_i]
            threshold = _adjusted_threshold(thresholds, doy, max_target_doy)
            value = flat_study[study_i, cell]
            out[study_i, cell] = np.float32(_compare(value, threshold, op_code))

    @njit(cache=True)
    def _write_union_mask_year_for_cell_with_daily_thresholds(
        out,
        flat_study,
        thresholds,
        study_doys,
        year_start,
        year_length,
        cell,
        op_code,
    ):
        for offset in range(year_length):
            study_i = year_start + offset
            doy = study_doys[study_i]
            value = flat_study[study_i, cell]
            out[study_i, cell] = np.float32(
                _compare(value, thresholds[doy - 1], op_code)
            )

    @njit(cache=True)
    def _accumulate_sum_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] += _sum_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
            )

    @njit(cache=True)
    def _accumulate_average_groups_for_cell(
        out,
        flat_study,
        thresholds,
        study_doys,
        study_starts,
        study_lengths,
        group_start,
        group_stop,
        cell,
        max_target_doy,
        op_code,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] += _average_exceedances(
                flat_study,
                thresholds,
                study_doys,
                study_starts[group_i],
                study_lengths[group_i],
                cell,
                max_target_doy,
                op_code,
            )

    @njit(cache=True)
    def _average_count_groups_for_cell(
        out,
        group_start,
        group_stop,
        cell,
        substitute_count,
    ):
        for group_i in range(group_start, group_stop):
            out[group_i, cell] /= substitute_count

    @njit(cache=True)
    def _compare(value, threshold, op_code):
        if op_code == 0:
            return value > threshold
        if op_code == 1:
            return value >= threshold
        if op_code == 2:
            return value < threshold
        return value <= threshold

    @njit(cache=True)
    def _combine_logical_matches(left_match, right_match, logical_link_code):
        if logical_link_code == 0:
            return left_match and right_match
        return left_match or right_match

    @njit(cache=True)
    def _adjusted_threshold(thresholds, doy, max_target_doy):
        source_day_count = len(thresholds)
        if max_target_doy == source_day_count:
            return thresholds[doy - 1]
        position = (doy - 1.0) * (source_day_count - 1.0) / (max_target_doy - 1.0)
        lower = int(np.floor(position))
        if lower >= source_day_count - 1:
            return thresholds[source_day_count - 1]
        gamma = position - lower
        diff = thresholds[lower + 1] - thresholds[lower]
        if gamma >= 0.5:
            return thresholds[lower + 1] - diff * (1.0 - gamma)
        return thresholds[lower] + diff * gamma

else:

    def _bootstrap_count_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    _bootstrap_count_threshold_bank_kernel = None

    def _bootstrap_sum_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_union_count_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_union_mask_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_average_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_fraction_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_bounded_count_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_bounded_sum_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_bounded_average_kernel(*args, **kwargs):  # noqa: ARG001
        return None

    def _bootstrap_bounded_fraction_kernel(*args, **kwargs):  # noqa: ARG001
        return None

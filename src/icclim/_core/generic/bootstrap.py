"""Compiled helpers for reliable percentile bootstrap counts."""
# ruff: noqa: ANN001, ANN202, PLR2004

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from xarray.coding.cftimeindex import CFTimeIndex

from icclim._core.constants import REFERENCE_PERIOD_ID
from icclim._core.generic.bootstrap_capability import (
    is_optimized_doy_percentile_count_supported,
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


def _bootstrap_array_dtype(study: DataArray) -> np.dtype:
    time_index = study.indexes["time"]
    if isinstance(time_index, CFTimeIndex):
        return np.float64
    return np.float32


def compute_doy_percentile_bootstrap_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute percentile bootstrap counts without building a huge dask graph."""
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
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
    return np.asarray(nominal_threshold.data, dtype=np.float64).reshape(
        nominal_threshold.sizes["dayofyear"],
        -1,
    )


def compute_doy_percentile_bootstrap_count_threshold_bank_prototype(
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
    overlap_reference = (
        array_inputs.flat_reference_filtered
        if not np.isnan(min_threshold)
        else array_inputs.flat_reference_raw
    )
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
        (n_reference_years, n_reference_years, NON_LEAP_YEAR_DAY_COUNT, n_cells),
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=_bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    result = _bootstrap_sum_kernel(
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=_bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    result = _bootstrap_union_count_kernel(
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


def compute_doy_percentile_bootstrap_union_exceedance_mask(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
    *,
    prepared_inputs: BootstrapPreparedInputs | None = None,
) -> DataArray | None:
    """Compute the daily union exceedance mask for spell-style bootstrap reducers."""
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    import xarray as xr  # noqa: PLC0415

    if prepared_inputs is None:
        prepared_inputs = build_bootstrap_prepared_inputs(
            study,
            threshold,
            freq,
            dtype=_bootstrap_array_dtype(study),
        )
    reference_sample = prepared_inputs.reference_sample
    temporal_indexing = prepared_inputs.temporal_indexing
    array_inputs = prepared_inputs.array_inputs
    flat_result = _bootstrap_union_mask_kernel(
        array_inputs.flat_reference_raw,
        array_inputs.flat_reference_filtered,
        array_inputs.flat_study,
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
        (
            np.nan
            if reference_sample.threshold_floor_in_reference_units is None
            else float(reference_sample.threshold_floor_in_reference_units)
        ),
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


def compute_doy_percentile_bootstrap_exceedance_average(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute bootstrap averages of exceedance-day values with the optimized path."""
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
    )
    result = _bootstrap_average_kernel(
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
    )
    result = _bootstrap_fraction_kernel(
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
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
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    reference_sample = build_bootstrap_reference_sample(study, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        freq,
        doy_window_width=threshold.doy_window_width,
    )
    array_inputs = build_bootstrap_array_inputs(
        reference_sample,
        dtype=_bootstrap_array_dtype(reference_sample.study),
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
        thresholds = np.empty(NON_LEAP_YEAR_DAY_COUNT, dtype=np.float64)
        base_buf = np.empty(max_samples, dtype=np.float64)
        removed_buf = np.empty(max_samples, dtype=np.float64)
        inserted_buf = np.empty(max_samples, dtype=np.float64)
        for doy_i in range(NON_LEAP_YEAR_DAY_COUNT):
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
        min_threshold,
    ):
        """Compute yearly bootstrap counts with the compiled order-stat route."""
        n_years = len(year_to_ref)
        n_groups = len(study_starts)
        n_cells = flat_study.shape[1]
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        overlap_reference = (
            flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
        )
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
                thresholds = _build_order_stat_threshold_series_for_cell(
                    flat_ref_masked,
                    sample_indices,
                    index_year,
                    index_pos,
                    substitute_aligned,
                    -1,
                    -1,
                    cell,
                    quantile,
                    alpha,
                    beta,
                    min_threshold,
                    max_samples,
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
                thresholds = _build_order_stat_threshold_series_for_cell(
                    overlap_reference,
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            threshold_bank = np.full(
                (n_ref_years, n_ref_years, NON_LEAP_YEAR_DAY_COUNT),
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
        """Compute yearly bootstrap exceedance sums from shared thresholds."""
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_sum_groups_for_cell(
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
            else:
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_sum_groups_for_cell(
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
                )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_union_count_kernel(
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
        """Count union exceedance days from shared bootstrap thresholds."""
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
            else:
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_count_groups_for_cell(
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
                )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_union_mask_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat_study,
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
        min_threshold,
    ):
        """Build the daily union exceedance mask for spell-style bootstrap reducers."""
        n_years = len(year_to_ref)
        n_times = flat_study.shape[0]
        n_cells = flat_study.shape[1]
        out = np.empty((n_times, n_cells), dtype=np.float32)
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            year_start = study_year_starts[year_i]
            year_length = study_year_lengths[year_i]
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
            else:
                thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    substitute_thresholds = (
                        _build_float32_bootstrap_threshold_series_for_cell(
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
                    )
                    _update_union_threshold_series(
                        thresholds,
                        substitute_thresholds,
                        op_code,
                    )
            _write_union_mask_year_for_cell(
                out,
                flat_study,
                thresholds,
                study_doys,
                year_start,
                year_length,
                cell,
                year_max_doys[year_i],
                op_code,
            )
        return out

    @njit(parallel=True, cache=True)
    def _bootstrap_average_kernel(
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
        """Compute yearly bootstrap exceedance averages from shared thresholds."""
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_average_groups_for_cell(
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
            elif np.isnan(min_threshold):
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_average_groups_for_cell(
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
                )
            else:
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = 0.0
                substitute_count = 0
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                    _accumulate_average_groups_for_cell(
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
    def _bootstrap_fraction_kernel(
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
        """Compute yearly bootstrap fractions of total from shared thresholds."""
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_fraction_groups_for_cell(
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
                    min_threshold,
                )
            else:
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                _write_fraction_groups_for_cell(
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
            overlap_reference = (
                flat_ref_masked if not np.isnan(min_threshold) else flat_ref_raw
            )
            if target_ref_i < 0:
                thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
                union_thresholds = _initialize_union_threshold_series(op_code)
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_float32_bootstrap_threshold_series_for_cell(
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
        thresholds = np.empty(NON_LEAP_YEAR_DAY_COUNT, dtype=np.float64)
        buf = np.empty(max_samples, dtype=np.float64)
        for doy_i in range(NON_LEAP_YEAR_DAY_COUNT):
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
    def _initialize_union_threshold_series(op_code):
        if op_code in (0, 1):
            return np.full(
                NON_LEAP_YEAR_DAY_COUNT, np.float32(np.inf), dtype=np.float32
            )
        return np.full(
            NON_LEAP_YEAR_DAY_COUNT,
            np.float32(-np.inf),
            dtype=np.float32,
        )

    @njit(cache=True)
    def _build_float32_bootstrap_threshold_series_for_cell(thresholds):
        converted = np.empty(NON_LEAP_YEAR_DAY_COUNT, dtype=np.float32)
        for day_i in range(NON_LEAP_YEAR_DAY_COUNT):
            converted[day_i] = np.float32(thresholds[day_i])
        return converted

    @njit(cache=True)
    def _update_union_threshold_series(union_thresholds, thresholds, op_code):
        for day_i in range(NON_LEAP_YEAR_DAY_COUNT):
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
        if max_target_doy == NON_LEAP_YEAR_DAY_COUNT:
            return thresholds[doy - 1]
        position = (doy - 1.0) * 364.0 / 365.0
        lower = int(np.floor(position))
        if lower >= 364:
            return thresholds[364]
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

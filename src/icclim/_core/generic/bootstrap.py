"""Compiled helpers for reliable percentile bootstrap counts."""
# ruff: noqa: ANN001, ANN202, PLR2004

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from icclim._core.constants import REFERENCE_PERIOD_ID
from icclim._core.generic.bootstrap_capability import (
    is_optimized_doy_percentile_count_supported,
)
from icclim._core.generic.bootstrap_primitives import (
    build_bootstrap_array_inputs,
    build_bootstrap_output,
    build_bootstrap_reference_sample,
    build_bootstrap_temporal_indexing,
)
from icclim._core.model.operator import Operator

if TYPE_CHECKING:
    from xarray import DataArray

    from icclim._core.generic.threshold.percentile import PercentileThreshold


NON_LEAP_YEAR_DAY_COUNT = 365


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
    array_inputs = build_bootstrap_array_inputs(reference_sample)
    result = _bootstrap_count_kernel(
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


def _can_compute_optimized_bootstrap(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> bool:
    return is_optimized_doy_percentile_count_supported(study, threshold, freq)


def _operator_code(operator: Operator | str) -> int:
    operand = operator.operand if isinstance(operator, Operator) else str(operator)
    return {">": 0, ">=": 1, "<": 2, "<=": 3}.get(operand, -1)


try:
    from numba import njit, prange
except Exception:  # noqa: BLE001
    njit = None
    prange = range


if njit is not None:

    @njit(parallel=True, cache=True)
    def _bootstrap_count_kernel(
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
        """Compute yearly bootstrap counts from threshold generation plus counting."""
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
            if target_ref_i < 0:
                thresholds = _build_bootstrap_threshold_series_for_cell(
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
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = 0.0
                substitute_count = 0
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    thresholds = _build_bootstrap_threshold_series_for_cell(
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

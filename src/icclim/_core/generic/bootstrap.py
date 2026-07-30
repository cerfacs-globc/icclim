"""Compiled helpers for reliable percentile bootstrap counts."""
# ruff: noqa: ANN001, ANN202, PLR2004

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import xarray as xr

from icclim._core.constants import REFERENCE_PERIOD_ID
from icclim._core.generic.bootstrap_capability import (
    is_optimized_doy_percentile_count_supported,
)
from icclim._core.model.operator import Operator

if TYPE_CHECKING:
    import pandas as pd
    from xarray import DataArray

    from icclim._core.generic.threshold.percentile import PercentileThreshold


def compute_doy_percentile_bootstrap_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute percentile bootstrap counts without building a huge dask graph."""
    if not _can_compute_optimized_bootstrap(study, threshold, freq):
        return None
    loaded = study.load()
    climatology_bounds = threshold.climatology_bounds(loaded)
    ref_raw = loaded.sel(time=slice(*climatology_bounds))
    min_threshold = _threshold_min_value_in_reference_units(threshold, ref_raw)
    ref_masked = ref_raw
    if min_threshold is not None:
        ref_masked = ref_raw.where(ref_raw >= min_threshold, np.nan)
    study_time = loaded.indexes["time"]
    ref_time = ref_raw.indexes["time"]
    ref_year_indices = _indices_by_year(ref_time)
    study_year_indices = _indices_by_year(study_time)
    ref_years = np.asarray(list(ref_year_indices), dtype=np.int64)
    output_group_indices = _indices_by_resample_group(loaded, freq)
    output_group_labels = list(output_group_indices)
    output_starts = np.asarray(
        [indices[0] for indices in output_group_indices.values()],
        dtype=np.int64,
    )
    output_lengths = np.asarray(
        [len(indices) for indices in output_group_indices.values()],
        dtype=np.int64,
    )
    source_max_doy = int(ref_time.dayofyear.max())
    study_year_max_doy = {
        year: source_max_doy
        if source_max_doy == 366
        else int(study_time[indices].dayofyear.max())
        for year, indices in study_year_indices.items()
    }
    output_years = np.asarray(
        [int(study_time[indices[0]].year) for indices in output_group_indices.values()],
        dtype=np.int64,
    )
    bootstrap_years = np.asarray(list(dict.fromkeys(output_years)), dtype=np.int64)
    year_group_starts, year_group_stops = _group_bounds_by_year(
        output_years,
        bootstrap_years,
    )
    year_max_doys = np.asarray(
        [study_year_max_doy[year] for year in bootstrap_years],
        dtype=np.int64,
    )
    year_to_ref = np.asarray(
        [
            int(np.where(ref_years == year)[0][0]) if year in ref_year_indices else -1
            for year in bootstrap_years
        ],
        dtype=np.int64,
    )
    flat = np.asarray(loaded.transpose("time", ...).data, dtype=np.float64).reshape(
        loaded.sizes["time"],
        -1,
    )
    flat_ref_raw = np.asarray(
        ref_raw.transpose("time", ...).data,
        dtype=np.float64,
    ).reshape(
        ref_raw.sizes["time"],
        -1,
    )
    flat_ref_masked = np.asarray(
        ref_masked.transpose("time", ...).data,
        dtype=np.float64,
    ).reshape(
        ref_masked.sizes["time"],
        -1,
    )
    sample_indices = _rolling_sample_index_matrix(
        ref_time,
        window=threshold.doy_window_width,
    )
    index_year, index_pos = _ref_index_year_and_position(
        ref_year_indices,
        len(ref_time),
    )
    substitute_aligned = _substitute_alignment_matrix(ref_time, ref_year_indices)
    result = _bootstrap_count_kernel(
        flat_ref_raw,
        flat_ref_masked,
        flat,
        sample_indices,
        index_year,
        index_pos,
        substitute_aligned,
        output_starts,
        output_lengths,
        year_group_starts,
        year_group_stops,
        year_max_doys,
        year_to_ref,
        study_time.dayofyear.to_numpy(dtype=np.int64),
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        np.nan if min_threshold is None else float(min_threshold),
    )
    data = result.reshape((len(output_group_labels), *loaded.shape[1:]))
    out = xr.DataArray(
        data,
        dims=loaded.dims,
        coords={
            "time": output_group_labels,
            **{coord: loaded.coords[coord] for coord in loaded.dims if coord != "time"},
        },
        attrs={"units": "d", REFERENCE_PERIOD_ID: climatology_bounds},
    )
    for coord in loaded.coords:
        if coord not in out.coords and "time" not in loaded[coord].dims:
            out = out.assign_coords({coord: loaded[coord]})
    return out.assign_coords(percentiles=threshold.percentile_coord().item())


def _can_compute_optimized_bootstrap(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> bool:
    return is_optimized_doy_percentile_count_supported(study, threshold, freq)


def _threshold_min_value_in_reference_units(
    threshold: PercentileThreshold,
    ref: DataArray,
) -> float | None:
    if threshold.threshold_min_value is None:
        return None
    from xclim.core.units import convert_units_to  # noqa: PLC0415

    converted = convert_units_to(threshold.threshold_min_value, ref, context="hydro")
    if hasattr(converted, "magnitude"):
        return float(converted.magnitude)
    return float(converted)


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
            max_target_doy = year_max_doys[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                q = _quantiles_for_cell(
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
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = _count_exceedances(
                        flat_study,
                        q,
                        study_doys,
                        study_starts[group_i],
                        study_lengths[group_i],
                        cell,
                        max_target_doy,
                        op_code,
                    )
            else:
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = 0.0
                substitute_count = 0
                for substitute_i in range(n_ref_years):
                    if substitute_i == target_ref_i:
                        continue
                    q = _quantiles_for_cell(
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
                    for group_i in range(group_start, group_stop):
                        out[group_i, cell] += _count_exceedances(
                            flat_study,
                            q,
                            study_doys,
                            study_starts[group_i],
                            study_lengths[group_i],
                            cell,
                            max_target_doy,
                            op_code,
                        )
                    substitute_count += 1
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] /= substitute_count
        return out

    @njit(cache=True)
    def _quantiles_for_cell(
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
        q = np.empty(365, dtype=np.float64)
        buf = np.empty(max_samples, dtype=np.float64)
        for doy_i in range(365):
            q_value = _quantile_for_doy_cell(
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
                np.isnan(q_value) or q_value <= min_threshold
            ):
                q_value = min_threshold
            q[doy_i] = q_value
        return q

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
        q,
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
            threshold = _adjusted_threshold(q, doy, max_target_doy)
            value = flat_study[start + offset, cell]
            if _compare(value, threshold, op_code):
                count += 1.0
        return count

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
    def _adjusted_threshold(q, doy, max_target_doy):
        if max_target_doy == 365:
            return q[doy - 1]
        position = (doy - 1.0) * 364.0 / 365.0
        lower = int(np.floor(position))
        if lower >= 364:
            return q[364]
        gamma = position - lower
        diff = q[lower + 1] - q[lower]
        if gamma >= 0.5:
            return q[lower + 1] - diff * (1.0 - gamma)
        return q[lower] + diff * gamma

else:

    def _bootstrap_count_kernel(*args, **kwargs):  # noqa: ARG001
        return None


def _indices_by_year(time: pd.DatetimeIndex) -> dict[int, np.ndarray]:
    return {int(year): np.where(time.year == year)[0] for year in np.unique(time.year)}


def _indices_by_resample_group(
    da: DataArray, freq: str
) -> dict[np.datetime64, np.ndarray]:
    groups = da.resample(time=freq).groups
    out = {}
    for label, indexer in groups.items():
        if isinstance(indexer, slice):
            start = 0 if indexer.start is None else indexer.start
            stop = da.sizes["time"] if indexer.stop is None else indexer.stop
            step = 1 if indexer.step is None else indexer.step
            indices = np.arange(start, stop, step, dtype=np.int64)
        else:
            indices = np.asarray(indexer, dtype=np.int64)
        out[np.datetime64(label)] = indices
    return out


def _group_bounds_by_year(
    output_years: np.ndarray,
    bootstrap_years: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    starts = np.empty(len(bootstrap_years), dtype=np.int64)
    stops = np.empty(len(bootstrap_years), dtype=np.int64)
    for i, year in enumerate(bootstrap_years):
        group_indices = np.where(output_years == year)[0]
        starts[i] = int(group_indices[0])
        stops[i] = int(group_indices[-1]) + 1
    return starts, stops


def _rolling_sample_index_matrix(
    time: pd.DatetimeIndex,
    *,
    window: int,
) -> np.ndarray:
    half_window = window // 2
    sample_indices: dict[int, list[int]] = {doy: [] for doy in range(1, 366)}
    doys = time.dayofyear.to_numpy()
    for center, doy in enumerate(doys):
        if doy == 366:
            continue
        start = max(0, center - half_window)
        stop = min(len(time), center + half_window + 1)
        sample_indices[int(doy)].extend(range(start, stop))
    max_samples = max(len(indices) for indices in sample_indices.values())
    matrix = np.full((365, max_samples), -1, dtype=np.int64)
    for doy, indices in sample_indices.items():
        matrix[doy - 1, : len(indices)] = indices
    return matrix


def _ref_index_year_and_position(
    ref_year_indices: dict[int, np.ndarray],
    n_ref_time: int,
) -> tuple[np.ndarray, np.ndarray]:
    index_year = np.full(n_ref_time, -1, dtype=np.int64)
    index_pos = np.full(n_ref_time, -1, dtype=np.int64)
    for year_index, indices in enumerate(ref_year_indices.values()):
        index_year[indices] = year_index
        index_pos[indices] = np.arange(len(indices), dtype=np.int64)
    return index_year, index_pos


def _substitute_alignment_matrix(
    ref_time: pd.DatetimeIndex,
    ref_year_indices: dict[int, np.ndarray],
) -> np.ndarray:
    max_year_len = max(len(indices) for indices in ref_year_indices.values())
    n_years = len(ref_year_indices)
    aligned = np.full((n_years, n_years, max_year_len), -1, dtype=np.int64)
    years = list(ref_year_indices)
    for target_i, target_year in enumerate(years):
        target_indices = ref_year_indices[target_year]
        target_time = ref_time[target_indices]
        for substitute_i, substitute_year in enumerate(years):
            substitute_indices = ref_year_indices[substitute_year]
            aligned[target_i, substitute_i, : len(target_indices)] = (
                _substitute_indices_aligned_to_target(
                    target_time,
                    ref_time[substitute_indices],
                    substitute_indices,
                )
            )
    return aligned


def _substitute_indices_aligned_to_target(
    target_time: pd.DatetimeIndex,
    substitute_time: pd.DatetimeIndex,
    substitute_indices: np.ndarray,
) -> np.ndarray:
    if len(target_time) == len(substitute_time):
        return substitute_indices
    substitute_by_month_day = {
        (int(month), int(day)): int(index)
        for month, day, index in zip(
            substitute_time.month,
            substitute_time.day,
            substitute_indices,
            strict=True,
        )
    }
    return np.asarray(
        [
            substitute_by_month_day.get((int(month), int(day)), -1)
            for month, day in zip(target_time.month, target_time.day, strict=True)
        ],
        dtype=np.int64,
    )

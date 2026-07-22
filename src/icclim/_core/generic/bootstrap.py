"""Compiled helpers for reliable percentile bootstrap counts."""
# ruff: noqa: ANN001, ANN202, PLR2004

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import xarray as xr

from icclim._core.constants import REFERENCE_PERIOD_ID
from icclim._core.model.operator import Operator

if TYPE_CHECKING:
    from xarray import DataArray

    from icclim._core.generic.threshold.percentile import PercentileThreshold


def compute_doy_percentile_bootstrap_count(
    study: DataArray,
    threshold: PercentileThreshold,
    freq: str,
) -> DataArray | None:
    """Compute percentile bootstrap counts without building a huge dask graph."""
    if not _can_compute_fast_bootstrap(study, threshold):
        return None
    loaded = study.load()
    climatology_bounds = threshold.value.attrs["climatology_bounds"]
    ref = loaded.sel(time=slice(*climatology_bounds))
    study_time = pd.DatetimeIndex(loaded.time.values)
    ref_time = pd.DatetimeIndex(ref.time.values)
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
        year: source_max_doy if source_max_doy == 366 else int(study_time[indices].dayofyear.max())
        for year, indices in study_year_indices.items()
    }
    output_years = [int(study_time[indices[0]].year) for indices in output_group_indices.values()]
    output_max_doys = np.asarray(
        [study_year_max_doy[year] for year in output_years],
        dtype=np.int64,
    )
    output_to_ref = np.asarray(
        [
            int(np.where(ref_years == year)[0][0]) if year in ref_year_indices else -1
            for year in output_years
        ],
        dtype=np.int64,
    )
    flat = np.asarray(loaded.transpose("time", ...).data, dtype=np.float64).reshape(
        loaded.sizes["time"],
        -1,
    )
    flat_ref = np.asarray(ref.transpose("time", ...).data, dtype=np.float64).reshape(
        ref.sizes["time"],
        -1,
    )
    nominal_threshold = _nominal_threshold(threshold)
    nominal_source_doy_count = nominal_threshold.sizes["dayofyear"]
    flat_nominal = np.asarray(
        nominal_threshold.transpose("dayofyear", ...).data,
        dtype=np.float64,
    ).reshape(nominal_source_doy_count, -1)
    sample_indices = _rolling_sample_index_matrix(
        ref_time,
        window=threshold.doy_window_width,
    )
    index_year, index_pos = _ref_index_year_and_position(
        ref_year_indices,
        len(ref_time),
    )
    donor_aligned = _donor_alignment_matrix(ref_time, ref_year_indices)
    result = _bootstrap_count_kernel(
        flat_ref,
        flat,
        flat_nominal,
        sample_indices,
        index_year,
        index_pos,
        donor_aligned,
        output_starts,
        output_lengths,
        output_max_doys,
        output_to_ref,
        study_time.dayofyear.to_numpy(dtype=np.int64),
        float(threshold.value.coords["percentiles"].item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        _operator_code(threshold.operator),
        nominal_source_doy_count,
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
    return out.assign_coords(percentiles=threshold.value.coords["percentiles"].item())


def _can_compute_fast_bootstrap(
    study: DataArray,
    threshold: PercentileThreshold,
) -> bool:
    try:
        pd.DatetimeIndex(study.time.values)
    except (TypeError, ValueError):
        return False
    return (
        njit is not None
        and threshold.threshold_min_value is None
        and not threshold.only_leap_years
        and threshold.value.coords["percentiles"].size == 1
        and _operator_code(threshold.operator) >= 0
    )


def _nominal_threshold(
    threshold: PercentileThreshold,
) -> DataArray:
    nominal = threshold.value
    if "percentiles" in nominal.dims:
        nominal = nominal.squeeze("percentiles", drop=True)
    return nominal


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
        flat_ref,
        flat_study,
        flat_nominal,
        sample_indices,
        index_year,
        index_pos,
        donor_aligned,
        study_starts,
        study_lengths,
        study_max_doys,
        study_to_ref,
        study_doys,
        quantile,
        alpha,
        beta,
        op_code,
        nominal_source_doy_count,
    ):
        n_years = len(study_starts)
        n_cells = flat_study.shape[1]
        out = np.empty((n_years, n_cells), dtype=np.float64)
        n_ref_years = donor_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = study_to_ref[year_i]
            max_target_doy = study_max_doys[year_i]
            start = study_starts[year_i]
            length = study_lengths[year_i]
            if target_ref_i < 0:
                out[year_i, cell] = _count_exceedances_with_nominal_threshold(
                    flat_study,
                    flat_nominal,
                    study_doys,
                    start,
                    length,
                    cell,
                    max_target_doy,
                    op_code,
                    nominal_source_doy_count,
                )
            else:
                donor_total = 0.0
                donor_count = 0
                for donor_i in range(n_ref_years):
                    if donor_i == target_ref_i:
                        continue
                    q = np.empty(365, dtype=np.float64)
                    buf = np.empty(max_samples, dtype=np.float64)
                    for doy_i in range(365):
                        q[doy_i] = _quantile_for_doy_cell(
                            flat_ref,
                            sample_indices,
                            index_year,
                            index_pos,
                            donor_aligned,
                            target_ref_i,
                            donor_i,
                            doy_i,
                            cell,
                            buf,
                            quantile,
                            alpha,
                            beta,
                        )
                    donor_total += _count_exceedances(
                        flat_study,
                        q,
                        study_doys,
                        start,
                        length,
                        cell,
                        max_target_doy,
                        op_code,
                    )
                    donor_count += 1
                out[year_i, cell] = donor_total / donor_count
        return out

    @njit(cache=True)
    def _count_exceedances_with_nominal_threshold(
        flat_study,
        flat_nominal,
        study_doys,
        start,
        length,
        cell,
        max_target_doy,
        op_code,
        nominal_source_doy_count,
    ):
        count = 0.0
        for offset in range(length):
            doy = study_doys[start + offset]
            value = flat_study[start + offset, cell]
            threshold = _adjusted_nominal_threshold(
                flat_nominal,
                doy,
                cell,
                max_target_doy,
                nominal_source_doy_count,
            )
            if _compare(value, threshold, op_code):
                count += 1.0
        return count

    @njit(cache=True)
    def _adjusted_nominal_threshold(
        flat_nominal,
        doy,
        cell,
        max_target_doy,
        nominal_source_doy_count,
    ):
        if nominal_source_doy_count == max_target_doy:
            return flat_nominal[doy - 1, cell]
        position = (doy - 1.0) * (nominal_source_doy_count - 1.0) / (
            max_target_doy - 1.0
        )
        lower = int(np.floor(position))
        if lower >= nominal_source_doy_count - 1:
            return flat_nominal[nominal_source_doy_count - 1, cell]
        gamma = position - lower
        left = flat_nominal[lower, cell]
        right = flat_nominal[lower + 1, cell]
        diff = right - left
        if gamma >= 0.5:
            return right - diff * (1.0 - gamma)
        return left + diff * gamma

    @njit(cache=True)
    def _quantile_for_doy_cell(
        flat_ref,
        sample_indices,
        index_year,
        index_pos,
        donor_aligned,
        target_ref_i,
        donor_i,
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
                mapped_i = donor_aligned[target_ref_i, donor_i, index_pos[ref_i]]
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


def _indices_by_resample_group(da: DataArray, freq: str) -> dict[np.datetime64, np.ndarray]:
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


def _donor_alignment_matrix(
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
        for donor_i, donor_year in enumerate(years):
            donor_indices = ref_year_indices[donor_year]
            aligned[target_i, donor_i, : len(target_indices)] = (
                _donor_indices_aligned_to_target(
                    target_time,
                    ref_time[donor_indices],
                    donor_indices,
                )
            )
    return aligned


def _donor_indices_aligned_to_target(
    target_time: pd.DatetimeIndex,
    donor_time: pd.DatetimeIndex,
    donor_indices: np.ndarray,
) -> np.ndarray:
    if len(target_time) == len(donor_time):
        return donor_indices
    donor_by_month_day = {
        (int(month), int(day)): int(index)
        for month, day, index in zip(
            donor_time.month,
            donor_time.day,
            donor_indices,
            strict=True,
        )
    }
    return np.asarray(
        [
            donor_by_month_day.get((int(month), int(day)), -1)
            for month, day in zip(target_time.month, target_time.day, strict=True)
        ],
        dtype=np.int64,
    )

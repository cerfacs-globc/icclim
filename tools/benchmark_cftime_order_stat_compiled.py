# ruff: noqa: N806, PLR2004, PLW0603, RUF059

from __future__ import annotations

import argparse
import json
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

import cftime
import numpy as np
import xarray as xr


def _resolve_import_root(repo: Path) -> Path:
    for candidate in (repo / "src", repo):
        if (candidate / "icclim" / "__init__.py").is_file():
            return candidate
    msg = f"Could not locate icclim import root under {repo}"
    raise FileNotFoundError(msg)


def _build_time_coord(
    start_year: int,
    study_year_count: int,
) -> list[cftime.DatetimeGregorian]:
    end_year = start_year + study_year_count - 1
    time = xr.date_range(
        f"{start_year}-01-01",
        f"{end_year}-12-31",
        freq="D",
        use_cftime=True,
    )
    return [
        cftime.DatetimeGregorian(int(ts.year), int(ts.month), int(ts.day))
        for ts in time
    ]


def _build_case(
    case_name: str,
    *,
    start_year: int,
    study_year_count: int,
    lat_length: int,
    lon_length: int,
) -> xr.DataArray:
    time = _build_time_coord(start_year, study_year_count)
    data = np.full((len(time), lat_length, lon_length), 300.0, dtype=np.float64)
    tas = xr.DataArray(
        data,
        dims=["time", "lat", "lon"],
        coords={
            "time": time,
            "lat": np.arange(lat_length, dtype=np.float64),
            "lon": np.arange(lon_length, dtype=np.float64),
        },
        attrs={"units": "K"},
        name="tas",
    )
    if case_name == "constant":
        return tas.chunk(
            {"time": 365, "lat": max(1, lat_length), "lon": max(1, lon_length)}
        )
    if case_name == "leap_day_cold_spike":
        for timestamp in (
            cftime.DatetimeGregorian(2044, 2, 28),
            cftime.DatetimeGregorian(2044, 2, 29),
            cftime.DatetimeGregorian(2044, 3, 1),
        ):
            if timestamp in tas.indexes["time"]:
                tas.loc[{"time": timestamp}] = 250.0
        return tas.chunk(
            {"time": 365, "lat": max(1, lat_length), "lon": max(1, lon_length)}
        )
    if case_name == "reference_overlap_shift":
        for year, month, day, value in (
            (2042, 2, 28, 305.0),
            (2043, 2, 28, 295.0),
            (2044, 2, 29, 285.0),
            (2045, 2, 28, 310.0),
            (2045, 3, 1, 280.0),
        ):
            timestamp = cftime.DatetimeGregorian(year, month, day)
            if timestamp in tas.indexes["time"]:
                tas.loc[{"time": timestamp}] = value
        return tas.chunk(
            {"time": 365, "lat": max(1, lat_length), "lon": max(1, lon_length)}
        )
    msg = f"Unsupported case: {case_name}"
    raise ValueError(msg)


def _build_threshold(reference_start_year: int, reference_year_count: int):
    from icclim.threshold.factory import build_threshold

    reference_end_year = reference_start_year + reference_year_count - 1
    return build_threshold(
        "> 90 doy_per",
        doy_window_width=1,
        reference_period=(
            f"{reference_start_year}-01-01",
            f"{reference_end_year}-12-31",
        ),
    )


@contextmanager
def _force_compiled_cftime_count():
    from icclim._core.generic import bootstrap as bootstrap_module

    original = bootstrap_module.is_optimized_doy_percentile_count_supported
    bootstrap_module.is_optimized_doy_percentile_count_supported = lambda *_: True
    try:
        yield
    finally:
        bootstrap_module.is_optimized_doy_percentile_count_supported = original


@dataclass(frozen=True)
class CompiledOrderStatBenchmark:
    case_name: str
    freq: str
    lat_length: int
    lon_length: int
    current_seconds: float
    compiled_bank_seconds: float
    compiled_order_stat_seconds: float
    changed_cells_vs_current: int
    max_abs_diff_vs_current: float
    speed_ratio_current_over_compiled_order_stat: float
    speed_ratio_compiled_bank_over_compiled_order_stat: float


def _load_numba():
    from numba import njit, prange

    return njit, prange


def _build_compiled_order_stat_kernel():
    njit, prange = _load_numba()
    NON_LEAP_DAY_COUNT = 365

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
        base_buf, base_n, removed_buf, removed_n, inserted_buf, inserted_n, rank
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
    def _adjusted_threshold(thresholds, doy, max_target_doy):
        if max_target_doy == NON_LEAP_DAY_COUNT:
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
    def _build_thresholds_for_cell(
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
        thresholds = np.empty(NON_LEAP_DAY_COUNT, dtype=np.float64)
        base_buf = np.empty(max_samples, dtype=np.float64)
        removed_buf = np.empty(max_samples, dtype=np.float64)
        inserted_buf = np.empty(max_samples, dtype=np.float64)
        for doy_i in range(NON_LEAP_DAY_COUNT):
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
    def _compiled_order_stat_count_kernel(
        flat_ref,
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
        n_ref_years = substitute_aligned.shape[1]
        max_samples = sample_indices.shape[1]
        out = np.empty((n_groups, n_cells), dtype=np.float64)
        for flat_i in prange(n_years * n_cells):
            year_i = flat_i // n_cells
            cell = flat_i % n_cells
            target_ref_i = year_to_ref[year_i]
            group_start = year_group_starts[year_i]
            group_stop = year_group_stops[year_i]
            if target_ref_i < 0:
                thresholds = _build_thresholds_for_cell(
                    flat_ref,
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
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = _count_exceedances(
                        flat_study,
                        thresholds,
                        study_doys,
                        study_starts[group_i],
                        study_lengths[group_i],
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
                thresholds = _build_thresholds_for_cell(
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
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] += _count_exceedances(
                        flat_study,
                        thresholds,
                        study_doys,
                        study_starts[group_i],
                        study_lengths[group_i],
                        cell,
                        year_max_doys[year_i],
                        op_code,
                    )
                substitute_count += 1
            for group_i in range(group_start, group_stop):
                out[group_i, cell] /= substitute_count
        return out

    return _compiled_order_stat_count_kernel


_COMPILED_ORDER_STAT_COUNT_KERNEL = None


def _compiled_order_stat_count_kernel():
    global _COMPILED_ORDER_STAT_COUNT_KERNEL
    if _COMPILED_ORDER_STAT_COUNT_KERNEL is None:
        _COMPILED_ORDER_STAT_COUNT_KERNEL = _build_compiled_order_stat_kernel()
    return _COMPILED_ORDER_STAT_COUNT_KERNEL


def _compute_compiled_order_stat(
    case_name: str,
    freq: str,
    *,
    start_year: int,
    study_year_count: int,
    reference_start_year: int,
    reference_year_count: int,
    lat_length: int,
    lon_length: int,
) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap_primitives import (
        build_bootstrap_output,
        build_bootstrap_prepared_inputs,
    )

    tas = _build_case(
        case_name,
        start_year=start_year,
        study_year_count=study_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    threshold = _build_threshold(reference_start_year, reference_year_count)
    prepared = build_bootstrap_prepared_inputs(
        tas,
        threshold,
        freq,
        dtype=np.float64,
    )
    ref = prepared.reference_sample
    idx = prepared.temporal_indexing
    arr = prepared.array_inputs
    min_threshold = (
        np.nan
        if ref.threshold_floor_in_reference_units is None
        else float(ref.threshold_floor_in_reference_units)
    )
    quantile = float(threshold.percentile_coord().item()) / 100.0
    alpha = float(threshold.interpolation.alpha)
    beta = float(threshold.interpolation.beta)
    op_code = 0 if threshold.operator.operand == ">" else 1
    flat_ref = (
        arr.flat_reference_filtered
        if not np.isnan(min_threshold)
        else arr.flat_reference_raw
    )
    kernel = _compiled_order_stat_count_kernel()
    start = perf_counter()
    out = kernel(
        flat_ref,
        arr.flat_study,
        idx.sample_indices_by_day_of_year,
        idx.reference_index_year,
        idx.reference_index_position,
        idx.substitute_alignment,
        idx.output_starts,
        idx.output_lengths,
        idx.year_group_starts,
        idx.year_group_stops,
        idx.year_max_day_of_years,
        idx.year_to_reference_index,
        idx.study_day_of_years,
        quantile,
        alpha,
        beta,
        op_code,
        min_threshold,
    )
    seconds = perf_counter() - start
    result = build_bootstrap_output(
        flat_result=out,
        reference_sample=ref,
        temporal_indexing=idx,
        spatial_shape=arr.spatial_shape,
        units="d",
    ).assign_coords(percentiles=threshold.percentile_coord().item())
    return result.load(), seconds


def _compute_current(
    case_name: str,
    freq: str,
    *,
    start_year: int,
    study_year_count: int,
    reference_start_year: int,
    reference_year_count: int,
    lat_length: int,
    lon_length: int,
) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count,
    )

    tas = _build_case(
        case_name,
        start_year=start_year,
        study_year_count=study_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    threshold = _build_threshold(reference_start_year, reference_year_count)
    start = perf_counter()
    with _force_compiled_cftime_count():
        result = compute_doy_percentile_bootstrap_count(tas, threshold, freq)
    seconds = perf_counter() - start
    if result is None:
        msg = f"Current compiled count returned None for case={case_name} freq={freq}"
        raise RuntimeError(msg)
    return result.load(), seconds


def _compute_compiled_bank(
    case_name: str,
    freq: str,
    *,
    start_year: int,
    study_year_count: int,
    reference_start_year: int,
    reference_year_count: int,
    lat_length: int,
    lon_length: int,
) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype,
    )

    tas = _build_case(
        case_name,
        start_year=start_year,
        study_year_count=study_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    threshold = _build_threshold(reference_start_year, reference_year_count)
    start = perf_counter()
    result = compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype(
        tas,
        threshold,
        freq,
    )
    seconds = perf_counter() - start
    if result is None:
        msg = (
            "Compiled threshold-bank prototype returned None for "
            f"case={case_name} freq={freq}"
        )
        raise RuntimeError(msg)
    return result.load(), seconds


def _compare(a: xr.DataArray, b: xr.DataArray) -> tuple[int, float]:
    diff = np.abs(np.asarray(a.values) - np.asarray(b.values))
    return (
        int(np.count_nonzero(diff > 1.0e-9)),
        float(np.nanmax(diff)) if diff.size else 0.0,
    )


def _benchmark_one(
    *,
    case_name: str,
    freq: str,
    start_year: int,
    study_year_count: int,
    reference_start_year: int,
    reference_year_count: int,
    lat_length: int,
    lon_length: int,
) -> CompiledOrderStatBenchmark:
    current, current_seconds = _compute_current(
        case_name,
        freq,
        start_year=start_year,
        study_year_count=study_year_count,
        reference_start_year=reference_start_year,
        reference_year_count=reference_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    compiled_bank, compiled_bank_seconds = _compute_compiled_bank(
        case_name,
        freq,
        start_year=start_year,
        study_year_count=study_year_count,
        reference_start_year=reference_start_year,
        reference_year_count=reference_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    compiled_order_stat, compiled_order_stat_seconds = _compute_compiled_order_stat(
        case_name,
        freq,
        start_year=start_year,
        study_year_count=study_year_count,
        reference_start_year=reference_start_year,
        reference_year_count=reference_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    changed_cells, max_abs_diff = _compare(current, compiled_order_stat)
    return CompiledOrderStatBenchmark(
        case_name=case_name,
        freq=freq,
        lat_length=lat_length,
        lon_length=lon_length,
        current_seconds=current_seconds,
        compiled_bank_seconds=compiled_bank_seconds,
        compiled_order_stat_seconds=compiled_order_stat_seconds,
        changed_cells_vs_current=changed_cells,
        max_abs_diff_vs_current=max_abs_diff,
        speed_ratio_current_over_compiled_order_stat=(
            current_seconds / compiled_order_stat_seconds
            if compiled_order_stat_seconds > 0.0
            else float("inf")
        ),
        speed_ratio_compiled_bank_over_compiled_order_stat=(
            compiled_bank_seconds / compiled_order_stat_seconds
            if compiled_order_stat_seconds > 0.0
            else float("inf")
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument(
        "--case",
        choices=("constant", "leap_day_cold_spike", "reference_overlap_shift"),
        default="reference_overlap_shift",
    )
    parser.add_argument("--freq", choices=("MS", "YS"), default="MS")
    parser.add_argument("--start-year", type=int, default=1950)
    parser.add_argument("--study-years", type=int, default=65)
    parser.add_argument("--reference-start-year", type=int, default=1961)
    parser.add_argument("--reference-years", type=int, default=30)
    parser.add_argument("--lat-length", type=int, default=4)
    parser.add_argument("--lon-length", type=int, default=4)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(_resolve_import_root(repo)))
    result = _benchmark_one(
        case_name=args.case,
        freq=args.freq,
        start_year=args.start_year,
        study_year_count=args.study_years,
        reference_start_year=args.reference_start_year,
        reference_year_count=args.reference_years,
        lat_length=args.lat_length,
        lon_length=args.lon_length,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

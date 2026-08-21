from __future__ import annotations

import argparse
import json
import math
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

import cftime
import numpy as np
import xarray as xr

NON_LEAP_DAY_COUNT = 365


def _resolve_import_root(repo: Path) -> Path:
    for candidate in (repo / "src", repo):
        if (candidate / "icclim" / "__init__.py").is_file():
            return candidate
    msg = f"Could not locate icclim import root under {repo}"
    raise FileNotFoundError(msg)


def _build_time_coord() -> list[cftime.DatetimeGregorian]:
    time = xr.date_range(
        "2042-01-01",
        periods=365 * 5 + 1,
        freq="D",
        use_cftime=True,
    )
    return [
        cftime.DatetimeGregorian(int(ts.year), int(ts.month), int(ts.day))
        for ts in time
    ]


def _build_case(case_name: str) -> xr.DataArray:
    time = _build_time_coord()
    data = np.full((len(time), 1, 1), 300.0, dtype=np.float64)
    tas = xr.DataArray(
        data,
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": [0.0], "lon": [0.0]},
        attrs={"units": "K"},
        name="tas",
    )
    if case_name == "constant":
        return tas.chunk({"time": 365, "lat": 1, "lon": 1})
    if case_name == "leap_day_cold_spike":
        for timestamp in (
            cftime.DatetimeGregorian(2044, 2, 28),
            cftime.DatetimeGregorian(2044, 2, 29),
            cftime.DatetimeGregorian(2044, 3, 1),
        ):
            tas.loc[{"time": timestamp}] = 250.0
        return tas.chunk({"time": 365, "lat": 1, "lon": 1})
    if case_name == "reference_overlap_shift":
        tas.loc[{"time": cftime.DatetimeGregorian(2042, 2, 28)}] = 305.0
        tas.loc[{"time": cftime.DatetimeGregorian(2043, 2, 28)}] = 295.0
        tas.loc[{"time": cftime.DatetimeGregorian(2044, 2, 29)}] = 285.0
        tas.loc[{"time": cftime.DatetimeGregorian(2045, 2, 28)}] = 310.0
        tas.loc[{"time": cftime.DatetimeGregorian(2045, 3, 1)}] = 280.0
        return tas.chunk({"time": 365, "lat": 1, "lon": 1})
    msg = f"Unsupported case: {case_name}"
    raise ValueError(msg)


def _build_threshold():
    from icclim.threshold.factory import build_threshold  # noqa: PLC0415

    return build_threshold(
        "> 90 doy_per",
        doy_window_width=1,
        reference_period=("2042-01-01", "2044-12-31"),
    )


@contextmanager
def _force_compiled_cftime_count():
    from icclim._core.generic import bootstrap as bootstrap_module  # noqa: PLC0415

    original = bootstrap_module.is_optimized_doy_percentile_count_supported
    bootstrap_module.is_optimized_doy_percentile_count_supported = lambda *_: True
    try:
        yield
    finally:
        bootstrap_module.is_optimized_doy_percentile_count_supported = original


@dataclass(frozen=True)
class ThresholdSeriesComparison:
    changed_doys: int
    max_abs_diff: float
    nominal_changed_doys: int
    overlap_changed_doys: int
    max_removed_values: int
    max_inserted_values: int
    mean_removed_values: float
    mean_inserted_values: float


def _nominal_sorted_sample_for_cell(
    flat_ref: np.ndarray,
    sample_indices: np.ndarray,
    doy_i: int,
    cell: int,
) -> np.ndarray:
    values = []
    for sample_i in range(sample_indices.shape[1]):
        ref_i = sample_indices[doy_i, sample_i]
        if ref_i < 0:
            continue
        value = flat_ref[ref_i, cell]
        if not np.isnan(value):
            values.append(float(value))
    return np.asarray(sorted(values), dtype=np.float64)


def _removed_values_for_target(
    base_sorted: np.ndarray,
    flat_ref: np.ndarray,
    sample_indices: np.ndarray,
    index_year: np.ndarray,
    doy_i: int,
    cell: int,
    target_ref_i: int,
) -> np.ndarray:
    if target_ref_i < 0:
        return np.empty(0, dtype=np.float64)
    removed = []
    for sample_i in range(sample_indices.shape[1]):
        ref_i = sample_indices[doy_i, sample_i]
        if ref_i < 0 or index_year[ref_i] != target_ref_i:
            continue
        value = flat_ref[ref_i, cell]
        if not np.isnan(value):
            removed.append(float(value))
    if not removed:
        return np.empty(0, dtype=np.float64)
    return np.asarray(sorted(removed), dtype=np.float64)


def _inserted_values_for_substitute(
    flat_ref: np.ndarray,
    sample_indices: np.ndarray,
    index_year: np.ndarray,
    index_pos: np.ndarray,
    substitute_aligned: np.ndarray,
    doy_i: int,
    cell: int,
    target_ref_i: int,
    substitute_i: int,
) -> np.ndarray:
    if target_ref_i < 0 or substitute_i < 0:
        return np.empty(0, dtype=np.float64)
    inserted = []
    for sample_i in range(sample_indices.shape[1]):
        ref_i = sample_indices[doy_i, sample_i]
        if ref_i < 0 or index_year[ref_i] != target_ref_i:
            continue
        mapped_i = substitute_aligned[target_ref_i, substitute_i, index_pos[ref_i]]
        if mapped_i < 0:
            continue
        value = flat_ref[mapped_i, cell]
        if not np.isnan(value):
            inserted.append(float(value))
    if not inserted:
        return np.empty(0, dtype=np.float64)
    return np.asarray(sorted(inserted), dtype=np.float64)


def _skip_removed(
    base_sorted: np.ndarray,
    removed_sorted: np.ndarray,
    base_i: int,
    removed_i: int,
) -> tuple[int, int]:
    while (
        base_i < len(base_sorted)
        and removed_i < len(removed_sorted)
        and base_sorted[base_i] == removed_sorted[removed_i]
    ):
        base_i += 1
        removed_i += 1
    return base_i, removed_i


def _value_at_adjusted_rank(
    base_sorted: np.ndarray,
    removed_sorted: np.ndarray,
    inserted_sorted: np.ndarray,
    rank: int,
) -> float:
    base_i = 0
    removed_i = 0
    inserted_i = 0
    current_rank = -1
    while True:
        base_i, removed_i = _skip_removed(base_sorted, removed_sorted, base_i, removed_i)
        has_base = base_i < len(base_sorted)
        has_inserted = inserted_i < len(inserted_sorted)
        if not has_base and not has_inserted:
            raise IndexError(rank)
        if has_inserted and (not has_base or inserted_sorted[inserted_i] <= base_sorted[base_i]):
            value = inserted_sorted[inserted_i]
            inserted_i += 1
        else:
            value = base_sorted[base_i]
            base_i += 1
        current_rank += 1
        if current_rank == rank:
            return float(value)


def _method8_quantile_from_adjusted_sorted(
    base_sorted: np.ndarray,
    removed_sorted: np.ndarray,
    inserted_sorted: np.ndarray,
    quantile: float,
    alpha: float,
    beta: float,
) -> float:
    n = len(base_sorted) - len(removed_sorted) + len(inserted_sorted)
    if n == 0:
        return float("nan")
    if n == 1:
        return _value_at_adjusted_rank(base_sorted, removed_sorted, inserted_sorted, 0)
    virtual = n * quantile + (alpha + quantile * (1.0 - alpha - beta)) - 1.0
    if virtual >= n - 1:
        return _value_at_adjusted_rank(base_sorted, removed_sorted, inserted_sorted, n - 1)
    if virtual < 0:
        return _value_at_adjusted_rank(base_sorted, removed_sorted, inserted_sorted, 0)
    previous = int(math.floor(virtual))
    gamma = virtual - previous
    left = _value_at_adjusted_rank(base_sorted, removed_sorted, inserted_sorted, previous)
    right = _value_at_adjusted_rank(
        base_sorted,
        removed_sorted,
        inserted_sorted,
        previous + 1,
    )
    diff = right - left
    if gamma >= 0.5:
        return right - diff * (1.0 - gamma)
    return left + diff * gamma


def _build_order_stat_threshold_series_for_cell(
    flat_ref: np.ndarray,
    sample_indices: np.ndarray,
    index_year: np.ndarray,
    index_pos: np.ndarray,
    substitute_aligned: np.ndarray,
    target_ref_i: int,
    substitute_i: int,
    cell: int,
    quantile: float,
    alpha: float,
    beta: float,
    min_threshold: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    thresholds = np.empty(NON_LEAP_DAY_COUNT, dtype=np.float64)
    removed_sizes = np.zeros(NON_LEAP_DAY_COUNT, dtype=np.int64)
    inserted_sizes = np.zeros(NON_LEAP_DAY_COUNT, dtype=np.int64)
    for doy_i in range(NON_LEAP_DAY_COUNT):
        base_sorted = _nominal_sorted_sample_for_cell(flat_ref, sample_indices, doy_i, cell)
        removed_sorted = _removed_values_for_target(
            base_sorted,
            flat_ref,
            sample_indices,
            index_year,
            doy_i,
            cell,
            target_ref_i,
        )
        inserted_sorted = _inserted_values_for_substitute(
            flat_ref,
            sample_indices,
            index_year,
            index_pos,
            substitute_aligned,
            doy_i,
            cell,
            target_ref_i,
            substitute_i,
        )
        removed_sizes[doy_i] = len(removed_sorted)
        inserted_sizes[doy_i] = len(inserted_sorted)
        threshold_value = _method8_quantile_from_adjusted_sorted(
            base_sorted,
            removed_sorted,
            inserted_sorted,
            quantile,
            alpha,
            beta,
        )
        if not np.isnan(min_threshold) and (
            np.isnan(threshold_value) or threshold_value <= min_threshold
        ):
            threshold_value = min_threshold
        thresholds[doy_i] = threshold_value
    return thresholds, removed_sizes, inserted_sizes


def compare_order_stat_threshold_series(
    case_name: str,
    freq: str,
) -> ThresholdSeriesComparison:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        _build_bootstrap_threshold_series_for_cell,
    )
    from icclim._core.generic.bootstrap_primitives import (  # noqa: PLC0415
        build_bootstrap_prepared_inputs,
    )

    tas = _build_case(case_name)
    threshold = _build_threshold()
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
    build_thresholds = _build_bootstrap_threshold_series_for_cell.py_func
    n_ref_years = idx.substitute_alignment.shape[1]
    flat_ref = arr.flat_reference_filtered if not np.isnan(min_threshold) else arr.flat_reference_raw
    changed_doys = 0
    max_abs_diff = 0.0
    nominal_changed_doys = 0
    overlap_changed_doys = 0
    max_removed_values = 0
    max_inserted_values = 0
    removed_total = 0
    inserted_total = 0
    compared_series = 0

    nominal_current = build_thresholds(
        flat_ref,
        idx.sample_indices_by_day_of_year,
        idx.reference_index_year,
        idx.reference_index_position,
        idx.substitute_alignment,
        -1,
        -1,
        0,
        idx.sample_indices_by_day_of_year.shape[1],
        quantile,
        alpha,
        beta,
        min_threshold,
    )
    nominal_prototype, removed_sizes, inserted_sizes = _build_order_stat_threshold_series_for_cell(
        flat_ref,
        idx.sample_indices_by_day_of_year,
        idx.reference_index_year,
        idx.reference_index_position,
        idx.substitute_alignment,
        -1,
        -1,
        0,
        quantile,
        alpha,
        beta,
        min_threshold,
    )
    nominal_diff = np.abs(nominal_current - nominal_prototype)
    nominal_changed = int(np.count_nonzero(nominal_diff > 1.0e-9))
    changed_doys += nominal_changed
    nominal_changed_doys += nominal_changed
    max_abs_diff = max(max_abs_diff, float(np.nanmax(nominal_diff)) if nominal_diff.size else 0.0)
    max_removed_values = max(max_removed_values, int(removed_sizes.max(initial=0)))
    max_inserted_values = max(max_inserted_values, int(inserted_sizes.max(initial=0)))
    removed_total += int(removed_sizes.sum())
    inserted_total += int(inserted_sizes.sum())
    compared_series += 1

    for target_ref_i in range(n_ref_years):
        for substitute_i in range(n_ref_years):
            if substitute_i == target_ref_i:
                continue
            current = build_thresholds(
                flat_ref,
                idx.sample_indices_by_day_of_year,
                idx.reference_index_year,
                idx.reference_index_position,
                idx.substitute_alignment,
                target_ref_i,
                substitute_i,
                0,
                idx.sample_indices_by_day_of_year.shape[1],
                quantile,
                alpha,
                beta,
                min_threshold,
            )
            prototype, removed_sizes, inserted_sizes = _build_order_stat_threshold_series_for_cell(
                flat_ref,
                idx.sample_indices_by_day_of_year,
                idx.reference_index_year,
                idx.reference_index_position,
                idx.substitute_alignment,
                target_ref_i,
                substitute_i,
                0,
                quantile,
                alpha,
                beta,
                min_threshold,
            )
            diff = np.abs(current - prototype)
            overlap_changed = int(np.count_nonzero(diff > 1.0e-9))
            changed_doys += overlap_changed
            overlap_changed_doys += overlap_changed
            max_abs_diff = max(max_abs_diff, float(np.nanmax(diff)) if diff.size else 0.0)
            max_removed_values = max(max_removed_values, int(removed_sizes.max(initial=0)))
            max_inserted_values = max(max_inserted_values, int(inserted_sizes.max(initial=0)))
            removed_total += int(removed_sizes.sum())
            inserted_total += int(inserted_sizes.sum())
            compared_series += 1

    return ThresholdSeriesComparison(
        changed_doys=changed_doys,
        max_abs_diff=max_abs_diff,
        nominal_changed_doys=nominal_changed_doys,
        overlap_changed_doys=overlap_changed_doys,
        max_removed_values=max_removed_values,
        max_inserted_values=max_inserted_values,
        mean_removed_values=removed_total / (NON_LEAP_DAY_COUNT * compared_series),
        mean_inserted_values=inserted_total / (NON_LEAP_DAY_COUNT * compared_series),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument(
        "--case",
        choices=("constant", "leap_day_cold_spike", "reference_overlap_shift", "all"),
        default="all",
    )
    parser.add_argument(
        "--freq",
        choices=("YS", "MS", "both"),
        default="both",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    import_root = _resolve_import_root(repo)
    sys.path.insert(0, str(import_root))

    case_names = (
        ("constant", "leap_day_cold_spike", "reference_overlap_shift")
        if args.case == "all"
        else (args.case,)
    )
    frequencies = ("YS", "MS") if args.freq == "both" else (args.freq,)
    payload: dict[str, object] = {"repo": str(repo), "cases": {}}
    for case_name in case_names:
        case_payload: dict[str, object] = {}
        for freq in frequencies:
            case_payload[freq] = asdict(compare_order_stat_threshold_series(case_name, freq))
        payload["cases"][case_name] = case_payload
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

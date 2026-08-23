from __future__ import annotations

import argparse
import json
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
    from icclim.threshold.factory import build_threshold

    return build_threshold(
        "> 90 doy_per",
        doy_window_width=1,
        reference_period=("2042-01-01", "2044-12-31"),
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
class PrototypeMetrics:
    nominal_series_built: int
    bank_series_built: int
    bank_bytes_float64: int
    bank_build_seconds: float
    evaluation_seconds: float
    total_seconds: float


def _compute_current_compiled(case_name: str, freq: str) -> xr.DataArray:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count,
    )

    tas = _build_case(case_name)
    threshold = _build_threshold()
    with _force_compiled_cftime_count():
        result = compute_doy_percentile_bootstrap_count(
            tas,
            threshold,
            freq,
        )
    if result is None:
        msg = f"Compiled bootstrap count returned None for case={case_name} freq={freq}"
        raise RuntimeError(msg)
    return result.load()


def _compute_threshold_bank_prototype(
    case_name: str,
    freq: str,
) -> tuple[xr.DataArray, PrototypeMetrics]:
    from icclim._core.generic.bootstrap import (
        _build_bootstrap_threshold_series_for_cell,
        _count_exceedances,
    )
    from icclim._core.generic.bootstrap_primitives import (
        build_bootstrap_output,
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
    op_code = 0 if threshold.operator.operand == ">" else 1
    build_thresholds = _build_bootstrap_threshold_series_for_cell.py_func
    count_exceedances = _count_exceedances.py_func
    max_samples = idx.sample_indices_by_day_of_year.shape[1]
    n_years = len(idx.bootstrap_years)
    n_groups = len(idx.output_group_labels)
    n_cells = arr.flat_study.shape[1]
    n_ref_years = idx.substitute_alignment.shape[1]
    out = np.empty((n_groups, n_cells), dtype=np.float64)

    total_start = perf_counter()
    build_start = perf_counter()
    nominal_thresholds_by_cell: list[np.ndarray] = []
    for cell in range(n_cells):
        nominal_thresholds_by_cell.append(
            build_thresholds(
                arr.flat_reference_filtered,
                idx.sample_indices_by_day_of_year,
                idx.reference_index_year,
                idx.reference_index_position,
                idx.substitute_alignment,
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
    threshold_bank = np.full(
        (n_ref_years, n_ref_years, 365, n_cells),
        np.nan,
        dtype=np.float64,
    )
    bank_series_built = 0
    for target_ref_i in range(n_ref_years):
        for substitute_i in range(n_ref_years):
            if substitute_i == target_ref_i:
                continue
            for cell in range(n_cells):
                threshold_bank[target_ref_i, substitute_i, :, cell] = build_thresholds(
                    arr.flat_reference_raw,
                    idx.sample_indices_by_day_of_year,
                    idx.reference_index_year,
                    idx.reference_index_position,
                    idx.substitute_alignment,
                    target_ref_i,
                    substitute_i,
                    cell,
                    max_samples,
                    quantile,
                    alpha,
                    beta,
                    min_threshold,
                )
                bank_series_built += 1
    bank_build_seconds = perf_counter() - build_start

    evaluation_start = perf_counter()
    for year_i in range(n_years):
        target_ref_i = idx.year_to_reference_index[year_i]
        group_start = idx.year_group_starts[year_i]
        group_stop = idx.year_group_stops[year_i]
        for cell in range(n_cells):
            if target_ref_i < 0:
                thresholds = nominal_thresholds_by_cell[cell]
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] = count_exceedances(
                        arr.flat_study,
                        thresholds,
                        idx.study_day_of_years,
                        idx.output_starts[group_i],
                        idx.output_lengths[group_i],
                        cell,
                        idx.year_max_day_of_years[year_i],
                        op_code,
                    )
                continue
            for group_i in range(group_start, group_stop):
                out[group_i, cell] = 0.0
            substitute_count = 0
            for substitute_i in range(n_ref_years):
                if substitute_i == target_ref_i:
                    continue
                thresholds = threshold_bank[target_ref_i, substitute_i, :, cell]
                for group_i in range(group_start, group_stop):
                    out[group_i, cell] += count_exceedances(
                        arr.flat_study,
                        thresholds,
                        idx.study_day_of_years,
                        idx.output_starts[group_i],
                        idx.output_lengths[group_i],
                        cell,
                        idx.year_max_day_of_years[year_i],
                        op_code,
                    )
                substitute_count += 1
            for group_i in range(group_start, group_stop):
                out[group_i, cell] /= substitute_count
    evaluation_seconds = perf_counter() - evaluation_start
    total_seconds = perf_counter() - total_start
    result = build_bootstrap_output(
        flat_result=out,
        reference_sample=ref,
        temporal_indexing=idx,
        spatial_shape=arr.spatial_shape,
        units="d",
    ).assign_coords(percentiles=threshold.percentile_coord().item())
    return result.load(), PrototypeMetrics(
        nominal_series_built=n_cells,
        bank_series_built=bank_series_built,
        bank_bytes_float64=int(threshold_bank.nbytes),
        bank_build_seconds=bank_build_seconds,
        evaluation_seconds=evaluation_seconds,
        total_seconds=total_seconds,
    )


def _compare(current: xr.DataArray, prototype: xr.DataArray) -> dict[str, object]:
    current_values = np.asarray(current.values)
    prototype_values = np.asarray(prototype.values)
    diff = np.abs(current_values - prototype_values)
    return {
        "changed_cells": int(np.count_nonzero(diff > 1.0e-9)),
        "max_abs_diff": float(np.nanmax(diff)) if diff.size else 0.0,
        "current_shape": list(current.shape),
        "prototype_shape": list(prototype.shape),
    }


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

    import sys

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
            current = _compute_current_compiled(case_name, freq)
            prototype, metrics = _compute_threshold_bank_prototype(case_name, freq)
            case_payload[freq] = {
                "comparison": _compare(current, prototype),
                "metrics": asdict(metrics),
            }
        payload["cases"][case_name] = case_payload
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

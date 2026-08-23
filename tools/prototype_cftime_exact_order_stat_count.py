from __future__ import annotations

import argparse
import importlib.util
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


def _load_quantile_tool(repo: Path):
    module_path = repo / "tools" / "prototype_cftime_exact_order_stat_quantile.py"
    spec = importlib.util.spec_from_file_location(
        "prototype_cftime_exact_order_stat_quantile",
        module_path,
    )
    if spec is None or spec.loader is None:
        msg = f"Cannot load quantile tool from {module_path}"
        raise RuntimeError(msg)
    quantile_tool = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = quantile_tool
    spec.loader.exec_module(quantile_tool)

    return quantile_tool


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
class CountPrototypeComparison:
    changed_cells: int
    max_abs_diff: float
    current_seconds: float
    order_stat_seconds: float
    compiled_bank_seconds: float
    speed_ratio_current_over_order_stat: float
    speed_ratio_compiled_bank_over_order_stat: float


def _compare(a: xr.DataArray, b: xr.DataArray) -> tuple[int, float]:
    diff = np.abs(np.asarray(a.values) - np.asarray(b.values))
    return (
        int(np.count_nonzero(diff > 1.0e-9)),
        float(np.nanmax(diff)) if diff.size else 0.0,
    )


def _compute_current(case_name: str, freq: str) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count,
    )

    tas = _build_case(case_name)
    threshold = _build_threshold()
    start = perf_counter()
    with _force_compiled_cftime_count():
        result = compute_doy_percentile_bootstrap_count(tas, threshold, freq)
    seconds = perf_counter() - start
    if result is None:
        msg = f"Current compiled count returned None for case={case_name} freq={freq}"
        raise RuntimeError(msg)
    return result.load(), seconds


def _compute_compiled_bank(case_name: str, freq: str) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype,
    )

    tas = _build_case(case_name)
    threshold = _build_threshold()
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


def _compute_order_stat(
    case_name: str,
    freq: str,
    repo: Path,
) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import _count_exceedances
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
    count_exceedances = _count_exceedances.py_func
    n_years = len(idx.bootstrap_years)
    n_groups = len(idx.output_group_labels)
    n_cells = arr.flat_study.shape[1]
    n_ref_years = idx.substitute_alignment.shape[1]
    flat_ref = (
        arr.flat_reference_filtered
        if not np.isnan(min_threshold)
        else arr.flat_reference_raw
    )
    quantile_tool = _load_quantile_tool(repo)
    out = np.empty((n_groups, n_cells), dtype=np.float64)

    start = perf_counter()
    nominal_thresholds_by_cell: list[np.ndarray] = []
    for cell in range(n_cells):
        thresholds, _, _ = quantile_tool._build_order_stat_threshold_series_for_cell(
            flat_ref,
            idx.sample_indices_by_day_of_year,
            idx.reference_index_year,
            idx.reference_index_position,
            idx.substitute_alignment,
            -1,
            -1,
            cell,
            quantile,
            alpha,
            beta,
            min_threshold,
        )
        nominal_thresholds_by_cell.append(thresholds)

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
                thresholds, _, _ = (
                    quantile_tool._build_order_stat_threshold_series_for_cell(
                        flat_ref,
                        idx.sample_indices_by_day_of_year,
                        idx.reference_index_year,
                        idx.reference_index_position,
                        idx.substitute_alignment,
                        target_ref_i,
                        substitute_i,
                        cell,
                        quantile,
                        alpha,
                        beta,
                        min_threshold,
                    )
                )
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
    seconds = perf_counter() - start

    result = build_bootstrap_output(
        flat_result=out,
        reference_sample=ref,
        temporal_indexing=idx,
        spatial_shape=arr.spatial_shape,
        units="d",
    ).assign_coords(percentiles=threshold.percentile_coord().item())
    return result.load(), seconds


def compare_count_prototypes(
    case_name: str,
    freq: str,
    *,
    repo: Path | None = None,
) -> CountPrototypeComparison:
    if repo is None:
        repo = Path(__file__).resolve().parents[1]
    current, current_seconds = _compute_current(case_name, freq)
    order_stat, order_stat_seconds = _compute_order_stat(case_name, freq, repo)
    compiled_bank, compiled_bank_seconds = _compute_compiled_bank(case_name, freq)
    changed_cells, max_abs_diff = _compare(current, order_stat)
    bank_changed_cells, bank_max_abs_diff = _compare(current, compiled_bank)
    if bank_changed_cells != 0 or bank_max_abs_diff != 0.0:
        msg = "Compiled threshold-bank prototype no longer matches current output"
        raise RuntimeError(msg)
    return CountPrototypeComparison(
        changed_cells=changed_cells,
        max_abs_diff=max_abs_diff,
        current_seconds=current_seconds,
        order_stat_seconds=order_stat_seconds,
        compiled_bank_seconds=compiled_bank_seconds,
        speed_ratio_current_over_order_stat=(
            current_seconds / order_stat_seconds
            if order_stat_seconds > 0.0
            else float("inf")
        ),
        speed_ratio_compiled_bank_over_order_stat=(
            compiled_bank_seconds / order_stat_seconds
            if order_stat_seconds > 0.0
            else float("inf")
        ),
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
            case_payload[freq] = asdict(
                compare_count_prototypes(case_name, freq, repo=repo)
            )
        payload["cases"][case_name] = case_payload
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

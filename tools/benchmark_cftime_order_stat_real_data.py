# ruff: noqa: PLR2004

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import xarray as xr

LAT_VALUE = 51.875
LON_VALUE = 30.9375
BASE_PERIOD = ("1961-01-01", "1990-12-31")
TIME_RANGE = ("1950-01-01", "2014-12-31")


def _resolve_import_root(repo: Path) -> Path:
    for candidate in (repo / "src", repo):
        if (candidate / "icclim" / "__init__.py").is_file():
            return candidate
    msg = f"Could not locate icclim import root under {repo}"
    raise FileNotFoundError(msg)


def _load_validation_module():
    script_path = Path(__file__).with_name("run_real_data_validation.py")
    spec = importlib.util.spec_from_file_location(
        "run_real_data_validation",
        script_path,
    )
    if spec is None or spec.loader is None:
        msg = f"Cannot load validation module from {script_path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_quantile_tool():
    script_path = Path(__file__).with_name(
        "prototype_cftime_exact_order_stat_quantile.py"
    )
    spec = importlib.util.spec_from_file_location(
        "prototype_cftime_exact_order_stat_quantile",
        script_path,
    )
    if spec is None or spec.loader is None:
        msg = f"Cannot load quantile tool from {script_path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _build_threshold():
    from icclim.threshold.factory import build_threshold

    return build_threshold(
        "> 90 doy_per",
        doy_window_width=5,
        reference_period=BASE_PERIOD,
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
class RealDataBenchmark:
    label: str
    freq: str
    lat_length: int
    lon_length: int
    changed_cells_vs_current: int
    max_abs_diff_vs_current: float
    compiled_bank_changed_cells_vs_current: int
    compiled_bank_max_abs_diff_vs_current: float
    current_seconds: float
    order_stat_seconds: float
    compiled_bank_seconds: float
    speed_ratio_current_over_order_stat: float
    speed_ratio_current_over_compiled_bank: float


def _subset_centered_on_point(
    tas: xr.DataArray,
    *,
    lat_value: float,
    lon_value: float,
    lat_length: int,
    lon_length: int,
) -> xr.DataArray:
    lat_index = int(np.abs(tas["lat"].values - lat_value).argmin())
    lon_index = int(np.abs(tas["lon"].values - lon_value).argmin())
    lat_start = max(0, lat_index - lat_length // 2)
    lon_start = max(0, lon_index - lon_length // 2)
    lat_stop = min(tas.sizes["lat"], lat_start + lat_length)
    lon_stop = min(tas.sizes["lon"], lon_start + lon_length)
    lat_start = max(0, lat_stop - lat_length)
    lon_start = max(0, lon_stop - lon_length)
    return tas.isel(
        lat=slice(lat_start, lat_stop),
        lon=slice(lon_start, lon_stop),
    )


def _open_real_subset(
    validation_module,
    *,
    lat_length: int,
    lon_length: int,
) -> xr.DataArray:
    tas = validation_module._open_var(validation_module.TAS_GLOB, "tas")
    tas = validation_module._as_cftime_gregorian(tas)
    tas = tas.sel(time=slice(*TIME_RANGE))
    tas = _subset_centered_on_point(
        tas,
        lat_value=LAT_VALUE,
        lon_value=LON_VALUE,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    return tas.chunk(
        {
            "time": 365,
            "lat": max(1, min(8, lat_length)),
            "lon": max(1, min(8, lon_length)),
        }
    )


def _compare(a: xr.DataArray, b: xr.DataArray) -> tuple[int, float]:
    a_aligned, b_aligned = xr.align(a, b, join="outer", copy=False)
    diff = np.abs(np.asarray(a_aligned.values) - np.asarray(b_aligned.values))
    return (
        int(np.count_nonzero(diff > 1.0e-9)),
        float(np.nanmax(diff)) if diff.size else 0.0,
    )


def _compute_current(tas: xr.DataArray, freq: str) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count,
    )

    threshold = _build_threshold()
    start = perf_counter()
    with _force_compiled_cftime_count():
        result = compute_doy_percentile_bootstrap_count(tas, threshold, freq)
    seconds = perf_counter() - start
    if result is None:
        msg = f"Current compiled count returned None for freq={freq}"
        raise RuntimeError(msg)
    return result.load(), seconds


def _compute_compiled_bank(tas: xr.DataArray, freq: str) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype,
    )

    threshold = _build_threshold()
    start = perf_counter()
    result = compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype(
        tas,
        threshold,
        freq,
    )
    seconds = perf_counter() - start
    if result is None:
        msg = f"Compiled threshold-bank prototype returned None for freq={freq}"
        raise RuntimeError(msg)
    return result.load(), seconds


def _compute_order_stat(tas: xr.DataArray, freq: str) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap import _count_exceedances
    from icclim._core.generic.bootstrap_primitives import (
        build_bootstrap_output,
        build_bootstrap_prepared_inputs,
    )

    quantile_tool = _load_quantile_tool()
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


def _benchmark_one(
    validation_module,
    *,
    label: str,
    freq: str,
    lat_length: int,
    lon_length: int,
) -> RealDataBenchmark:
    tas = _open_real_subset(
        validation_module,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    current, current_seconds = _compute_current(tas, freq)
    order_stat, order_stat_seconds = _compute_order_stat(tas, freq)
    compiled_bank, compiled_bank_seconds = _compute_compiled_bank(tas, freq)
    changed_cells_vs_current, max_abs_diff_vs_current = _compare(current, order_stat)
    compiled_bank_changed_cells_vs_current, compiled_bank_max_abs_diff_vs_current = (
        _compare(
            current,
            compiled_bank,
        )
    )
    return RealDataBenchmark(
        label=label,
        freq=freq,
        lat_length=lat_length,
        lon_length=lon_length,
        changed_cells_vs_current=changed_cells_vs_current,
        max_abs_diff_vs_current=max_abs_diff_vs_current,
        compiled_bank_changed_cells_vs_current=compiled_bank_changed_cells_vs_current,
        compiled_bank_max_abs_diff_vs_current=compiled_bank_max_abs_diff_vs_current,
        current_seconds=current_seconds,
        order_stat_seconds=order_stat_seconds,
        compiled_bank_seconds=compiled_bank_seconds,
        speed_ratio_current_over_order_stat=(
            current_seconds / order_stat_seconds
            if order_stat_seconds > 0.0
            else float("inf")
        ),
        speed_ratio_current_over_compiled_bank=(
            current_seconds / compiled_bank_seconds
            if compiled_bank_seconds > 0.0
            else float("inf")
        ),
    )


def _parse_shape(shape: str) -> tuple[int, int]:
    try:
        lat_length_str, lon_length_str = shape.lower().split("x", maxsplit=1)
        lat_length = int(lat_length_str)
        lon_length = int(lon_length_str)
    except Exception as exc:
        msg = f"Invalid shape {shape!r}. Expected format like '1x1' or '2x2'."
        raise ValueError(msg) from exc
    if lat_length <= 0 or lon_length <= 0:
        msg = f"Shape lengths must be positive, got {shape!r}."
        raise ValueError(msg)
    return lat_length, lon_length


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--freq", choices=("MS", "YS", "both"), default="both")
    parser.add_argument("--shape", default="4x4")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(_resolve_import_root(repo)))

    validation_module = _load_validation_module()
    frequencies = ("MS", "YS") if args.freq == "both" else (args.freq,)
    lat_length, lon_length = _parse_shape(args.shape)
    payload: dict[str, object] = {
        "repo": str(repo),
        "shape": args.shape,
        "frequencies": {},
    }
    for freq in frequencies:
        result = _benchmark_one(
            validation_module,
            label=f"real-{args.shape.lower()}",
            freq=freq,
            lat_length=lat_length,
            lon_length=lon_length,
        )
        payload["frequencies"][freq] = asdict(result)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

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


def _load_compiled_tool():
    script_path = Path(__file__).with_name("benchmark_cftime_order_stat_compiled.py")
    spec = importlib.util.spec_from_file_location(
        "benchmark_cftime_order_stat_compiled",
        script_path,
    )
    if spec is None or spec.loader is None:
        msg = f"Cannot load compiled order-stat tool from {script_path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _build_threshold():
    from icclim.threshold.factory import build_threshold  # noqa: PLC0415

    return build_threshold(
        "> 90 doy_per",
        doy_window_width=5,
        reference_period=BASE_PERIOD,
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
class RealDataCompiledBenchmark:
    freq: str
    lat_length: int
    lon_length: int
    changed_cells_vs_current: int
    max_abs_diff_vs_current: float
    compiled_bank_changed_cells_vs_current: int
    compiled_bank_max_abs_diff_vs_current: float
    current_seconds: float
    compiled_order_stat_seconds: float
    compiled_bank_seconds: float
    speed_ratio_current_over_compiled_order_stat: float
    speed_ratio_current_over_compiled_bank: float


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


def _open_real_subset(validation_module, *, lat_length: int, lon_length: int) -> xr.DataArray:
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
    from icclim._core.generic.bootstrap import compute_doy_percentile_bootstrap_count  # noqa: PLC0415

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
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
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


def _compute_compiled_order_stat(
    tas: xr.DataArray,
    freq: str,
) -> tuple[xr.DataArray, float]:
    from icclim._core.generic.bootstrap_primitives import (  # noqa: PLC0415
        build_bootstrap_output,
        build_bootstrap_prepared_inputs,
    )

    compiled_tool = _load_compiled_tool()
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
    flat_ref = (
        arr.flat_reference_filtered
        if not np.isnan(min_threshold)
        else arr.flat_reference_raw
    )
    kernel = compiled_tool._compiled_order_stat_count_kernel()
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


def _benchmark_one(
    validation_module,
    *,
    freq: str,
    lat_length: int,
    lon_length: int,
) -> RealDataCompiledBenchmark:
    tas = _open_real_subset(
        validation_module,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    current, current_seconds = _compute_current(tas, freq)
    compiled_order_stat, compiled_order_stat_seconds = _compute_compiled_order_stat(
        tas,
        freq,
    )
    compiled_bank, compiled_bank_seconds = _compute_compiled_bank(tas, freq)
    changed_cells_vs_current, max_abs_diff_vs_current = _compare(
        current,
        compiled_order_stat,
    )
    compiled_bank_changed_cells_vs_current, compiled_bank_max_abs_diff_vs_current = _compare(
        current,
        compiled_bank,
    )
    return RealDataCompiledBenchmark(
        freq=freq,
        lat_length=lat_length,
        lon_length=lon_length,
        changed_cells_vs_current=changed_cells_vs_current,
        max_abs_diff_vs_current=max_abs_diff_vs_current,
        compiled_bank_changed_cells_vs_current=compiled_bank_changed_cells_vs_current,
        compiled_bank_max_abs_diff_vs_current=compiled_bank_max_abs_diff_vs_current,
        current_seconds=current_seconds,
        compiled_order_stat_seconds=compiled_order_stat_seconds,
        compiled_bank_seconds=compiled_bank_seconds,
        speed_ratio_current_over_compiled_order_stat=(
            current_seconds / compiled_order_stat_seconds
            if compiled_order_stat_seconds > 0.0
            else float("inf")
        ),
        speed_ratio_current_over_compiled_bank=(
            current_seconds / compiled_bank_seconds
            if compiled_bank_seconds > 0.0
            else float("inf")
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--freq", choices=("MS", "YS", "both"), default="both")
    parser.add_argument("--shape", default="1x1")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(_resolve_import_root(repo)))
    validation_module = _load_validation_module()
    lat_length, lon_length = _parse_shape(args.shape)
    frequencies = ("MS", "YS") if args.freq == "both" else (args.freq,)
    payload: dict[str, object] = {
        "repo": str(repo),
        "shape": args.shape,
        "frequencies": {},
    }
    for freq in frequencies:
        payload["frequencies"][freq] = asdict(
            _benchmark_one(
                validation_module,
                freq=freq,
                lat_length=lat_length,
                lon_length=lon_length,
            )
        )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

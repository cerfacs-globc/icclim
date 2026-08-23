# ruff: noqa: PLR2004

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


def _build_time_coord(
    start_year: int, study_year_count: int
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
class BenchmarkResult:
    case_name: str
    freq: str
    lat_length: int
    lon_length: int
    study_year_count: int
    reference_year_count: int
    current_seconds: float
    python_prototype_seconds: float
    compiled_prototype_seconds: float
    speed_ratio_current_over_python: float
    speed_ratio_current_over_compiled: float
    changed_cells: int
    max_abs_diff: float
    compiled_changed_cells: int
    compiled_max_abs_diff: float


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
) -> BenchmarkResult:
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count,
        compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype,
        compute_doy_percentile_bootstrap_count_threshold_bank_prototype,
    )

    tas = _build_case(
        case_name,
        start_year=start_year,
        study_year_count=study_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    threshold = _build_threshold(reference_start_year, reference_year_count)

    current_start = perf_counter()
    with _force_compiled_cftime_count():
        current = compute_doy_percentile_bootstrap_count(tas, threshold, freq)
    current_seconds = perf_counter() - current_start
    if current is None:
        msg = f"Current compiled count returned None for case={case_name} freq={freq}"
        raise RuntimeError(msg)
    current = current.load()

    prototype_start = perf_counter()
    prototype = compute_doy_percentile_bootstrap_count_threshold_bank_prototype(
        tas,
        threshold,
        freq,
    )
    python_prototype_seconds = perf_counter() - prototype_start
    if prototype is None:
        msg = f"Threshold-bank prototype returned None for case={case_name} freq={freq}"
        raise RuntimeError(msg)
    prototype = prototype.load()

    compiled_start = perf_counter()
    compiled_prototype = (
        compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype(
            tas,
            threshold,
            freq,
        )
    )
    compiled_prototype_seconds = perf_counter() - compiled_start
    if compiled_prototype is None:
        msg = (
            "Compiled threshold-bank prototype returned None for "
            f"case={case_name} freq={freq}"
        )
        raise RuntimeError(msg)
    compiled_prototype = compiled_prototype.load()

    diff = np.abs(np.asarray(current.values) - np.asarray(prototype.values))
    changed_cells = int(np.count_nonzero(diff > 1.0e-9))
    max_abs_diff = float(np.nanmax(diff)) if diff.size else 0.0
    compiled_diff = np.abs(
        np.asarray(current.values) - np.asarray(compiled_prototype.values)
    )
    compiled_changed_cells = int(np.count_nonzero(compiled_diff > 1.0e-9))
    compiled_max_abs_diff = (
        float(np.nanmax(compiled_diff)) if compiled_diff.size else 0.0
    )
    speed_ratio_current_over_python = (
        current_seconds / python_prototype_seconds
        if python_prototype_seconds > 0.0
        else float("inf")
    )
    speed_ratio_current_over_compiled = (
        current_seconds / compiled_prototype_seconds
        if compiled_prototype_seconds > 0.0
        else float("inf")
    )
    return BenchmarkResult(
        case_name=case_name,
        freq=freq,
        lat_length=lat_length,
        lon_length=lon_length,
        study_year_count=study_year_count,
        reference_year_count=reference_year_count,
        current_seconds=current_seconds,
        python_prototype_seconds=python_prototype_seconds,
        compiled_prototype_seconds=compiled_prototype_seconds,
        speed_ratio_current_over_python=speed_ratio_current_over_python,
        speed_ratio_current_over_compiled=speed_ratio_current_over_compiled,
        changed_cells=changed_cells,
        max_abs_diff=max_abs_diff,
        compiled_changed_cells=compiled_changed_cells,
        compiled_max_abs_diff=compiled_max_abs_diff,
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
    import_root = _resolve_import_root(repo)

    import sys

    sys.path.insert(0, str(import_root))

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

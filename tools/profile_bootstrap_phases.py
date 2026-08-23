from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Any

import cftime
import numpy as np
import xarray as xr

TAS_GLOB = "/scratch/globc/page/models/tas_day_ACCESS-CM2_historical_*.nc"
PR_GLOB = "/scratch/globc/page/models/pr_day_ACCESS-CM2_historical_*.nc"
LAT_SLICE = slice(35.0, 70.0)
LON_SLICE = slice(0.0, 40.0)
DRY_PR_LAT_SLICE = slice(35.0, 45.0)
DRY_PR_LON_SLICE = slice(0.0, 30.0)
BASE_PERIOD = ("1961-01-01", "1990-12-31")
TIME_RANGE = ("1950-01-01", "2014-12-31")
DEFAULT_CHUNKS = {"time": 365, "lat": 24, "lon": 32}
ALT_CHUNKS = {"time": 730, "lat": 7, "lon": 9}


def _resolve_import_root(repo: Path) -> Path:
    for candidate in (repo / "src", repo / "icclim", repo):
        if (candidate / "icclim" / "__init__.py").is_file():
            return candidate
    msg = f"Could not locate icclim package import root under {repo}"
    raise FileNotFoundError(msg)


def _open_var(
    file_glob: str,
    var_name: str,
    *,
    chunks: dict[str, int],
) -> xr.DataArray:
    import glob

    files = sorted(glob.glob(file_glob))
    if not files:
        raise FileNotFoundError(file_glob)
    ds = xr.open_mfdataset(files, combine="by_coords", chunks=chunks)
    return ds[var_name].sel(lat=LAT_SLICE, lon=LON_SLICE)


def _as_cftime_gregorian(da: xr.DataArray) -> xr.DataArray:
    time_values = da.indexes["time"]
    cftime_time = [
        cftime.DatetimeGregorian(
            int(ts.year),
            int(ts.month),
            int(ts.day),
            int(getattr(ts, "hour", 0)),
            int(getattr(ts, "minute", 0)),
            int(getattr(ts, "second", 0)),
        )
        for ts in time_values
    ]
    return da.assign_coords(time=cftime_time)


def _build_workload(icclim, workload: str, *, chunks: dict[str, int]) -> xr.Dataset:
    tas = _open_var(TAS_GLOB, "tas", chunks=chunks)
    if workload == "generic_pr_average_bootstrap_yearly":
        pr = _open_var(
            PR_GLOB,
            "pr",
            chunks=chunks,
        ).sel(lat=DRY_PR_LAT_SLICE, lon=DRY_PR_LON_SLICE)
        return icclim.average(
            in_files=pr,
            var_name="pr",
            threshold=icclim.build_threshold(
                "> 95 doy_per",
                reference_period=BASE_PERIOD,
                threshold_min_value="1 mm/day",
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_compound_percentile_or_count_yearly":
        return icclim.count_occurrences(
            in_files=tas,
            var_name="tas",
            threshold=icclim.build_threshold(
                thresholds=["> 95 doy_per", "<= 10 doy_per"],
                logical_link="or",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_compound_percentile_or_average_yearly":
        return icclim.average(
            in_files=tas,
            var_name="tas",
            threshold=icclim.build_threshold(
                thresholds=["> 95 doy_per", "<= 10 doy_per"],
                logical_link="or",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_compound_percentile_or_sum_yearly":
        return icclim.sum(
            in_files=tas,
            var_name="tas",
            threshold=icclim.build_threshold(
                thresholds=["> 95 doy_per", "<= 10 doy_per"],
                logical_link="or",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_compound_percentile_or_fraction_yearly":
        return icclim.fraction_of_total(
            in_files=tas,
            var_name="tas",
            threshold=icclim.build_threshold(
                thresholds=["> 95 doy_per", "<= 10 doy_per"],
                logical_link="or",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_spell_bootstrap_yearly":
        return icclim.sum_of_spell_lengths(
            in_files=tas,
            var_name="tas",
            threshold=icclim.build_threshold(
                "> 90 doy_per",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
            min_spell_length=6,
        )
    if workload == "wsdi_yearly":
        return icclim.index(
            index_name="WSDI",
            in_files=tas,
            var_name="tas",
            base_period_time_range=BASE_PERIOD,
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "csdi_yearly":
        return icclim.index(
            index_name="CSDI",
            in_files=tas,
            var_name="tas",
            base_period_time_range=BASE_PERIOD,
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "tx90p_cftime_yearly":
        tas = _as_cftime_gregorian(tas)
        return icclim.index(
            index_name="TX90p",
            in_files=tas,
            var_name="tas",
            base_period_time_range=BASE_PERIOD,
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "tx90p_cftime_monthly":
        tas = _as_cftime_gregorian(tas)
        return icclim.index(
            index_name="TX90p",
            in_files=tas,
            var_name="tas",
            base_period_time_range=BASE_PERIOD,
            time_range=TIME_RANGE,
            slice_mode="month",
        )
    msg = f"Unsupported workload: {workload}"
    raise ValueError(msg)


def _warmup(icclim) -> None:
    time_coord = xr.date_range("2000-01-01", periods=365 * 4 + 1, freq="D")
    tas = xr.DataArray(
        np.full((len(time_coord), 1, 1), 300.0, dtype=np.float32),
        dims=["time", "lat", "lon"],
        coords={"time": time_coord, "lat": [0], "lon": [0]},
        attrs={"units": "K"},
        name="tas",
    ).chunk({"time": 365, "lat": 1, "lon": 1})
    try:
        icclim.index(
            index_name="TG",
            in_files=tas,
            var_name="tas",
            slice_mode="month",
        ).load()
    except Exception:
        pass


@contextmanager
def _timed_patch(module: Any, attr: str, stats: dict[str, dict[str, float]]):
    original = getattr(module, attr)

    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        result = original(*args, **kwargs)
        elapsed = time.perf_counter() - start
        phase_stats = stats.setdefault(attr, {"seconds": 0.0, "calls": 0.0})
        phase_stats["seconds"] += elapsed
        phase_stats["calls"] += 1.0
        return result

    setattr(module, attr, wrapped)
    try:
        yield
    finally:
        setattr(module, attr, original)


@contextmanager
def _timed_patch_if_present(
    module: Any,
    attr: str,
    stats: dict[str, dict[str, float]],
):
    if not hasattr(module, attr):
        yield
        return
    with _timed_patch(module, attr, stats):
        yield


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--chunk-profile", choices=("default", "alt"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(_resolve_import_root(repo)))

    import icclim

    bootstrap_module = None
    primitives_module = None
    functions_module = importlib.import_module("icclim._core.generic.functions")
    try:
        bootstrap_module = importlib.import_module("icclim._core.generic.bootstrap")
    except ModuleNotFoundError:
        pass
    try:
        primitives_module = importlib.import_module(
            "icclim._core.generic.bootstrap_primitives"
        )
    except ModuleNotFoundError:
        pass
    get_bootstrap_profile = getattr(functions_module, "get_bootstrap_profile", dict)
    reset_bootstrap_profile = getattr(
        functions_module, "reset_bootstrap_profile", lambda: None
    )

    chunk_profile = DEFAULT_CHUNKS if args.chunk_profile == "default" else ALT_CHUNKS
    phase_stats: dict[str, dict[str, float]] = {}
    reset_bootstrap_profile()
    _warmup(icclim)

    started = time.perf_counter()
    with (
        _timed_patch_if_present(
            functions_module,
            "_compute_threshold_exceedance_mask",
            phase_stats,
        ),
        _timed_patch_if_present(
            functions_module,
            "_compute_exceedance_mask",
            phase_stats,
        ),
        _timed_patch_if_present(
            functions_module,
            "_compute_safe_tiled_count_occurrences",
            phase_stats,
        ),
        _timed_patch_if_present(
            functions_module,
            "_compute_safe_tiled_count_occurrences_with_max_cells",
            phase_stats,
        ),
        _timed_patch_if_present(
            functions_module,
            "_compute_exact_tiled_bootstrap_spell_mask",
            phase_stats,
        ),
        _timed_patch_if_present(
            functions_module,
            "_compute_fast_tiled_count_occurrences",
            phase_stats,
        ),
        _timed_patch_if_present(
            primitives_module,
            "_normalize_bootstrap_chunks",
            phase_stats,
        )
        if primitives_module is not None
        else nullcontext(),
        _timed_patch_if_present(
            primitives_module,
            "build_bootstrap_reference_sample",
            phase_stats,
        )
        if primitives_module is not None
        else nullcontext(),
        _timed_patch_if_present(
            primitives_module,
            "build_bootstrap_prepared_inputs",
            phase_stats,
        )
        if primitives_module is not None
        else nullcontext(),
        _timed_patch_if_present(
            bootstrap_module,
            "compute_doy_percentile_bootstrap_count",
            phase_stats,
        )
        if bootstrap_module is not None
        else nullcontext(),
        _timed_patch_if_present(
            bootstrap_module,
            "build_bootstrap_temporal_indexing",
            phase_stats,
        )
        if bootstrap_module is not None
        else nullcontext(),
        _timed_patch_if_present(
            bootstrap_module,
            "build_bootstrap_array_inputs",
            phase_stats,
        )
        if bootstrap_module is not None
        else nullcontext(),
    ):
        ds = _build_workload(icclim, args.workload, chunks=chunk_profile).load()
    elapsed = time.perf_counter() - started

    payload = {
        "workload": args.workload,
        "chunk_profile": args.chunk_profile,
        "duration_seconds": elapsed,
        "data_vars": list(ds.data_vars),
        "phase_stats": phase_stats,
        "bootstrap_profile": get_bootstrap_profile(),
    }
    out_path = Path(args.out)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
from dask.callbacks import Callback

DEFAULT_WORKLOADS = (
    "baseline_count",
    "baseline_sum",
    "rolling_sum_5day",
    "rolling_mean_5day",
    "date_event_max_monthly",
    "date_event_min_monthly",
    "date_event_count_monthly",
    "date_event_consecutive_monthly",
    "reference_diff_daily",
    "reference_diff_monthly",
)
DEFAULT_LAYOUTS = ("single", "many")
DEFAULT_CHUNK_MODES = ("native", "user", "auto")
USER_CHUNKS = {"time": 180, "lat": 8, "lon": 8}
MIN_REFERENCE_YEARS = 4


@dataclass(frozen=True)
class BenchmarkCase:
    workload: str
    layout: str
    chunk_mode: str

    @property
    def name(self) -> str:
        return f"{self.workload}-{self.layout}-{self.chunk_mode}"


class SchedulerRecorder(Callback):
    def __init__(self) -> None:
        super().__init__()
        self.graph_sizes: list[int] = []

    def _start(self, dsk: Any) -> None:
        self.graph_sizes.append(len(dsk))


def _resolve_import_root(repo: Path) -> Path:
    for candidate in (repo / "src", repo / "icclim", repo):
        if (candidate / "icclim" / "__init__.py").is_file():
            return candidate
    msg = f"Could not locate icclim package import root under {repo}"
    raise FileNotFoundError(msg)


def _peak_rss_bytes() -> int:
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024


def _write_synthetic_inputs(
    root: Path,
    *,
    years: int,
    lat_size: int,
    lon_size: int,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    time_coord = pd.date_range(
        "2000-01-01",
        periods=365 * years,
        freq="D",
    )
    day = np.arange(time_coord.size, dtype=np.float32)[:, np.newaxis, np.newaxis]
    lat = np.linspace(-20, 20, lat_size, dtype=np.float32)
    lon = np.linspace(0, 30, lon_size, dtype=np.float32)
    values = (
        280.0
        + 8.0 * np.sin(day * np.float32(2 * np.pi / 365.0))
        + lat[np.newaxis, :, np.newaxis] * np.float32(0.03)
        + lon[np.newaxis, np.newaxis, :] * np.float32(0.01)
    ).astype(np.float32)
    source = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time_coord, "lat": lat, "lon": lon},
        name="tas",
        attrs={"units": "K", "standard_name": "air_temperature"},
    )
    encoding = {
        "tas": {
            "chunksizes": (min(365, time_coord.size), lat_size, lon_size),
        },
    }
    source.to_dataset().to_netcdf(root / "single.nc", encoding=encoding)
    many_dir = root / "many"
    many_dir.mkdir(exist_ok=True)
    for year, sample in source.groupby("time.year"):
        sample.to_dataset().to_netcdf(
            many_dir / f"tas-{int(year)}.nc",
            encoding={
                "tas": {
                    "chunksizes": (sample.sizes["time"], lat_size, lon_size),
                },
            },
        )


def _input_paths(root: Path, layout: str) -> list[Path]:
    if layout == "single":
        return [root / "single.nc"]
    if layout == "many":
        paths = sorted((root / "many").glob("*.nc"))
        if paths:
            return paths
    msg = f"No input files found for layout {layout!r} under {root}"
    raise FileNotFoundError(msg)


def _open_source(root: Path, layout: str, chunk_mode: str) -> xr.DataArray:
    paths = _input_paths(root, layout)
    chunks: dict[str, int] | str
    if chunk_mode == "native":
        chunks = {}
    elif chunk_mode == "user":
        chunks = USER_CHUNKS
    elif chunk_mode == "auto":
        chunks = "auto"
    else:
        msg = f"Unknown chunk mode: {chunk_mode}"
        raise ValueError(msg)
    if layout == "single":
        dataset = xr.open_dataset(paths[0], chunks=chunks)
    else:
        dataset = xr.open_mfdataset(paths, combine="by_coords", chunks=chunks)
    return dataset["tas"]


def _reference_ranges(source: xr.DataArray) -> tuple[tuple[str, str], tuple[str, str]]:
    years = np.unique(source.time.dt.year.values)
    if years.size < MIN_REFERENCE_YEARS:
        msg = "Reference-difference benchmarks require at least four years"
        raise ValueError(msg)
    midpoint = years.size // 2
    reference_years = years[:midpoint]
    study_years = years[midpoint:]
    return (
        (f"{reference_years[0]}-01-01", f"{reference_years[-1]}-12-31"),
        (f"{study_years[0]}-01-01", f"{study_years[-1]}-12-31"),
    )


def _build_workload(icclim: Any, source: xr.DataArray, workload: str) -> xr.Dataset:
    common = {
        "in_files": source,
        "var_name": "tas",
        "allow_missing_periods": True,
        "logs_verbosity": "SILENT",
    }
    if workload == "baseline_count":
        return icclim.count_occurrences(
            **common,
            threshold="> 280 K",
            slice_mode="year",
        )
    if workload == "baseline_sum":
        return icclim.sum(**common, slice_mode="year")
    if workload == "rolling_sum_5day":
        return icclim.max_of_rolling_sum(
            **common,
            rolling_window_width=5,
            slice_mode="year",
        )
    if workload == "rolling_mean_5day":
        return icclim.max_of_rolling_average(
            **common,
            rolling_window_width=5,
            slice_mode="year",
        )
    if workload == "date_event_max_monthly":
        return icclim.maximum(**common, slice_mode="month", date_event=True)
    if workload == "date_event_min_monthly":
        return icclim.minimum(**common, slice_mode="month", date_event=True)
    if workload == "date_event_count_monthly":
        return icclim.count_occurrences(
            **common,
            threshold="> 280 K",
            slice_mode="month",
            date_event=True,
        )
    if workload == "date_event_consecutive_monthly":
        return icclim.max_consecutive_occurrence(
            **common,
            threshold="> 280 K",
            slice_mode="month",
            date_event=True,
        )
    if workload in {"reference_diff_daily", "reference_diff_monthly"}:
        reference_range, study_range = _reference_ranges(source)
        return icclim.index(
            index_name="difference_of_means",
            in_files=source,
            var_name="tas",
            base_period_time_range=reference_range,
            time_range=study_range,
            sampling_method="groupby_ref_and_resample_study",
            slice_mode="day" if workload.endswith("daily") else "month",
            allow_missing_periods=True,
            logs_verbosity="SILENT",
        )
    msg = f"Unknown workload: {workload}"
    raise ValueError(msg)


def _graph_task_count(dataset: xr.Dataset) -> int:
    graph = dataset.__dask_graph__()
    return 0 if graph is None else len(graph)


def _numeric_checksum(dataset: xr.Dataset) -> float:
    checksum = 0.0
    for data_var in dataset.data_vars.values():
        if np.issubdtype(data_var.dtype, np.number):
            checksum += float(data_var.sum(skipna=True).item())
    return checksum


def _run_worker(
    repo: Path,
    input_root: Path,
    case: BenchmarkCase,
) -> dict[str, Any]:
    sys.path.insert(0, str(_resolve_import_root(repo)))
    import icclim

    rss_before = _peak_rss_bytes()
    started = time.perf_counter()
    result: dict[str, Any] = {
        **asdict(case),
        "case": case.name,
        "status": "error",
        "icclim_version": icclim.__version__,
    }
    build_started: float | None = None
    try:
        source = _open_source(input_root, case.layout, case.chunk_mode)
        build_started = time.perf_counter()
        build_recorder = SchedulerRecorder()
        with build_recorder:
            dataset = _build_workload(icclim, source, case.workload)
        result["build_seconds"] = time.perf_counter() - build_started
        result["task_count"] = _graph_task_count(dataset)
        compute_recorder = SchedulerRecorder()
        compute_started = time.perf_counter()
        with compute_recorder:
            dataset = dataset.load()
        result.update(
            {
                "status": "ok",
                "compute_seconds": time.perf_counter() - compute_started,
                "scheduler_calls": len(build_recorder.graph_sizes)
                + len(compute_recorder.graph_sizes),
                "scheduler_build_calls": len(build_recorder.graph_sizes),
                "scheduler_compute_calls": len(compute_recorder.graph_sizes),
                "scheduler_build_graph_sizes": build_recorder.graph_sizes,
                "scheduler_compute_graph_sizes": compute_recorder.graph_sizes,
                "checksum": _numeric_checksum(dataset),
                "output_sizes": {
                    name: int(size) for name, size in dataset.sizes.items()
                },
            },
        )
    except Exception as error:
        if build_started is not None and "build_seconds" not in result:
            result["build_seconds"] = time.perf_counter() - build_started
        result.update(
            {
                "error_type": type(error).__name__,
                "error": str(error),
                "traceback": traceback.format_exc(),
            },
        )
    peak_rss = _peak_rss_bytes()
    result.update(
        {
            "wall_seconds": time.perf_counter() - started,
            "rss_before_bytes": rss_before,
            "peak_rss_bytes": peak_rss,
            "peak_rss_delta_bytes": max(0, peak_rss - rss_before),
        },
    )
    return result


def _parse_selection(value: str, allowed: tuple[str, ...]) -> tuple[str, ...]:
    if value == "all":
        return allowed
    selected = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown = sorted(set(selected) - set(allowed))
    if unknown:
        msg = f"Unknown selection(s): {', '.join(unknown)}"
        raise ValueError(msg)
    return selected


def _run_subprocess(
    script: Path,
    repo: Path,
    input_root: Path,
    case: BenchmarkCase,
    result_path: Path,
) -> dict[str, Any]:
    env = os.environ.copy()
    import_root = str(_resolve_import_root(repo))
    env["PYTHONPATH"] = os.pathsep.join(
        value for value in (import_root, env.get("PYTHONPATH")) if value
    )
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--worker",
            "--repo",
            str(repo),
            "--input-root",
            str(input_root),
            "--workload",
            case.workload,
            "--layout",
            case.layout,
            "--chunk-mode",
            case.chunk_mode,
            "--result",
            str(result_path),
        ],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result_path.is_file():
        result = json.loads(result_path.read_text())
    else:
        result = {
            **asdict(case),
            "case": case.name,
            "status": "worker_error",
        }
    result.update(
        {
            "worker_returncode": completed.returncode,
            "worker_stdout": completed.stdout,
            "worker_stderr": completed.stderr,
        },
    )
    return result


def _worker_main(args: argparse.Namespace) -> None:
    case = BenchmarkCase(args.workload, args.layout, args.chunk_mode)
    result = _run_worker(
        Path(args.repo).resolve(),
        Path(args.input_root).resolve(),
        case,
    )
    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def _parent_main(args: argparse.Namespace) -> None:
    repo = Path(args.repo).resolve()
    output = Path(args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    workloads = _parse_selection(args.workloads, DEFAULT_WORKLOADS)
    layouts = _parse_selection(args.layouts, DEFAULT_LAYOUTS)
    chunk_modes = _parse_selection(args.chunk_modes, DEFAULT_CHUNK_MODES)
    script = Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix="icclim-non-bootstrap-") as temp_dir:
        temp_root = Path(temp_dir)
        input_root = (
            Path(args.input_root).resolve()
            if args.input_root is not None
            else temp_root / "inputs"
        )
        if args.input_root is None:
            _write_synthetic_inputs(
                input_root,
                years=args.years,
                lat_size=args.lat_size,
                lon_size=args.lon_size,
            )
        results = []
        for workload in workloads:
            for layout in layouts:
                for chunk_mode in chunk_modes:
                    case = BenchmarkCase(workload, layout, chunk_mode)
                    result_path = temp_root / f"{case.name}.json"
                    result = _run_subprocess(
                        script,
                        repo,
                        input_root,
                        case,
                        result_path,
                    )
                    results.append(result)
                    print(
                        f"{case.name}: {result['status']} "
                        f"wall={result.get('wall_seconds', float('nan')):.3f}s "
                        f"peak_rss={result.get('peak_rss_bytes', 0) / 2**20:.1f}MiB",
                        flush=True,
                    )
    payload = {
        "schema_version": 1,
        "repo": str(repo),
        "cube": {
            "years": args.years,
            "lat_size": args.lat_size,
            "lon_size": args.lon_size,
        },
        "results": results,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--out")
    parser.add_argument("--input-root")
    parser.add_argument("--workloads", default="all")
    parser.add_argument("--layouts", default="all")
    parser.add_argument("--chunk-modes", default="all")
    parser.add_argument("--years", type=int, default=6)
    parser.add_argument("--lat-size", type=int, default=32)
    parser.add_argument("--lon-size", type=int, default=48)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--workload", choices=DEFAULT_WORKLOADS)
    parser.add_argument("--layout", choices=DEFAULT_LAYOUTS)
    parser.add_argument("--chunk-mode", choices=DEFAULT_CHUNK_MODES)
    parser.add_argument("--result")
    return parser


def main() -> None:
    parser = _parser()
    args = parser.parse_args()
    if args.worker:
        required = (
            args.input_root,
            args.workload,
            args.layout,
            args.chunk_mode,
            args.result,
        )
        if any(value is None for value in required):
            parser.error("worker mode requires input, case, and result arguments")
        _worker_main(args)
    else:
        if args.out is None:
            parser.error("--out is required")
        _parent_main(args)


if __name__ == "__main__":
    main()

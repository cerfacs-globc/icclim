"""Benchmark TG90p bootstrap behavior on realistic NetCDF inputs."""

from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
import time
from pathlib import Path

import dask
import xarray as xr


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark TG90p bootstrap performance on daily tas inputs.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the icclim repository to benchmark.",
    )
    parser.add_argument(
        "--file-glob",
        required=True,
        help="Glob pattern for input tas files.",
    )
    parser.add_argument("--lat-min", type=float, default=35.0)
    parser.add_argument("--lat-max", type=float, default=70.0)
    parser.add_argument("--lon-min", type=float, default=0.0)
    parser.add_argument("--lon-max", type=float, default=40.0)
    parser.add_argument("--time-chunk", type=int, default=365)
    parser.add_argument("--lat-chunk", type=int, default=24)
    parser.add_argument("--lon-chunk", type=int, default=32)
    parser.add_argument("--time-range-start", default="1950-01-01")
    parser.add_argument("--time-range-end", default="2014-12-31")
    parser.add_argument("--base-period-start", default="1961-01-01")
    parser.add_argument("--base-period-end", default="1990-12-31")
    parser.add_argument(
        "--scheduler",
        default="threads",
        choices=["threads", "single-threaded", "synchronous", "processes"],
    )
    parser.add_argument(
        "--bootstrap",
        default="auto",
        choices=["auto", "true", "false", "safe"],
        help="Override bootstrap behavior when supported by the checked out code.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Directory where benchmark summaries and outputs are cached.",
    )
    parser.add_argument(
        "--cache-key",
        default=None,
        help="Name prefix for cached files. Defaults to repo name plus bootstrap mode.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recompute even when cached outputs already exist.",
    )
    parser.add_argument(
        "--save-output",
        action="store_true",
        help="Persist the TG90p result to a NetCDF file in the cache directory.",
    )
    return parser.parse_args()


def _git_rev_parse(repo: Path, ref: str) -> str | None:
    git_dir = repo / ".git"
    if not git_dir.exists():
        return None
    try:
        return (
            subprocess.check_output(  # noqa: S603
                ["git", "-C", str(repo), "rev-parse", ref],  # noqa: S607
                text=True,
            )
            .strip()
        )
    except Exception:  # noqa: BLE001
        return None


def _resolve_bootstrap_arg(value: str) -> bool | str | None:
    if value == "auto":
        return None
    if value == "safe":
        return "safe"
    return value == "true"


def _default_cache_key(repo: Path, bootstrap: str) -> str:
    return f"{repo.name}-{bootstrap}"


def _cached_paths(cache_dir: Path, cache_key: str) -> tuple[Path, Path]:
    return (
        cache_dir / f"{cache_key}.summary.json",
        cache_dir / f"{cache_key}.result.nc",
    )


def main() -> None:
    """Run the benchmark and print a JSON summary."""
    args = _parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / "src"))

    import icclim  # noqa: PLC0415
    from icclim._core.generic import functions as generic_functions  # noqa: PLC0415

    cache_dir = args.cache_dir.resolve() if args.cache_dir else None
    cache_key = args.cache_key or _default_cache_key(repo, args.bootstrap)
    summary_path: Path | None = None
    result_path: Path | None = None
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        summary_path, result_path = _cached_paths(cache_dir, cache_key)
        if summary_path.exists() and (not args.save_output or result_path.exists()) and not args.force:
            print(summary_path.read_text())
            return

    files = sorted(glob.glob(args.file_glob))  # noqa: PTH207
    if not files:
        msg = f"No files matched {args.file_glob!r}."
        raise FileNotFoundError(msg)

    open_start = time.perf_counter()
    ds = xr.open_mfdataset(
        files,
        combine="by_coords",
        chunks={
            "time": args.time_chunk,
            "lat": args.lat_chunk,
            "lon": args.lon_chunk,
        },
    )
    da = ds["tas"].sel(
        lat=slice(args.lat_min, args.lat_max),
        lon=slice(args.lon_min, args.lon_max),
    )
    open_end = time.perf_counter()

    build_start = time.perf_counter()
    index_kwargs = {
        "index_name": "tg90p",
        "in_files": da,
        "var_name": "tas",
        "slice_mode": "year",
        "time_range": (args.time_range_start, args.time_range_end),
        "base_period_time_range": (args.base_period_start, args.base_period_end),
    }
    bootstrap = _resolve_bootstrap_arg(args.bootstrap)
    if bootstrap is not None:
        index_kwargs["bootstrap"] = bootstrap
    reset_bootstrap_profile = getattr(
        generic_functions,
        "reset_bootstrap_profile",
        None,
    )
    get_bootstrap_profile = getattr(
        generic_functions,
        "get_bootstrap_profile",
        None,
    )
    if reset_bootstrap_profile is not None:
        reset_bootstrap_profile()
    with dask.config.set(scheduler=args.scheduler):
        result = icclim.index(**index_kwargs)
    build_end = time.perf_counter()
    bootstrap_profile = (
        get_bootstrap_profile() if get_bootstrap_profile is not None else {}
    )

    tg90p = result["TG90p"]
    graph_getter = getattr(tg90p.data, "__dask_graph__", None)
    graph = graph_getter() if graph_getter is not None else None

    compute_start = time.perf_counter()
    with dask.config.set(scheduler=args.scheduler):
        loaded = tg90p.load()
    compute_end = time.perf_counter()

    summary: dict[str, object] = {
        "repo": str(repo),
        "head_commit": _git_rev_parse(repo, "HEAD"),
        "origin_master_commit": _git_rev_parse(repo, "origin/master"),
        "icclim_version": icclim.__version__,
        "n_files": len(files),
        "subset_sizes": {k: int(v) for k, v in da.sizes.items()},
        "chunks": {
            "time": args.time_chunk,
            "lat": args.lat_chunk,
            "lon": args.lon_chunk,
        },
        "scheduler": args.scheduler,
        "bootstrap": args.bootstrap,
        "open_seconds": open_end - open_start,
        "build_seconds": build_end - build_start,
        "compute_seconds": compute_end - compute_start,
        "total_seconds": compute_end - open_start,
        "graph_tasks": len(graph) if graph is not None else 0,
        "result_shape": tuple(int(x) for x in loaded.shape),
        "result_mean": float(loaded.mean().item()),
        "bootstrap_profile": bootstrap_profile,
    }

    if result_path is not None and args.save_output:
        loaded.to_netcdf(result_path)
        summary["result_path"] = str(result_path)
    if summary_path is not None:
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

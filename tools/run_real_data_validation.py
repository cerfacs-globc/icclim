from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import xarray as xr

TAS_GLOB = "/scratch/globc/page/models/tas_day_ACCESS-CM2_historical_*.nc"
PR_GLOB = "/scratch/globc/page/models/pr_day_ACCESS-CM2_historical_*.nc"
TASMAX_GLOB = "/scratch/globc/page/models/tasmax_day_EC-Earth3_historical_*.nc"
LAT_SLICE = slice(35.0, 70.0)
LON_SLICE = slice(0.0, 40.0)
DATE_EVENT_LAT_SLICE = slice(35.0, 55.0)
DATE_EVENT_LON_SLICE = slice(0.0, 20.0)
BASE_PERIOD = ("1961-01-01", "1990-12-31")
TIME_RANGE = ("1950-01-01", "2014-12-31")
TASMAX_TIME_RANGE = ("1986-01-01", "1999-12-31")
DATE_EVENT_TIME_RANGE = ("1980-01-01", "2014-12-31")
CHUNKS = {"time": 365, "lat": 24, "lon": 32}


def _git_rev_parse(repo: Path, ref: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", ref],
            text=True,
        ).strip()
    except Exception:
        return None


def _open_var(
    file_glob: str,
    var_name: str,
    *,
    lat_slice: slice = LAT_SLICE,
    lon_slice: slice = LON_SLICE,
) -> xr.DataArray:
    files = sorted(glob.glob(file_glob))
    if not files:
        raise FileNotFoundError(file_glob)
    ds = xr.open_mfdataset(files, combine="by_coords", chunks=CHUNKS)
    return ds[var_name].sel(lat=lat_slice, lon=lon_slice)


def _open_combined_dataset(*, eager: bool = False) -> xr.Dataset:
    tas = _open_var(TAS_GLOB, "tas")
    pr = _open_var(PR_GLOB, "pr")
    ds = xr.Dataset({"tas": tas, "pr": pr})
    if eager:
        ds = ds.load()
    return ds


def _warmup(icclim) -> None:
    time_coord = xr.date_range("2000-01-01", periods=365 * 4 + 1, freq="D")
    tas = xr.DataArray(
        np.full((len(time_coord), 2, 2), 300.0, dtype=np.float32),
        dims=["time", "lat", "lon"],
        coords={"time": time_coord, "lat": [0, 1], "lon": [0, 1]},
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


def _build_workload(icclim, workload: str) -> xr.Dataset:
    if workload == "tg_monthly":
        tas = _open_var(TAS_GLOB, "tas")
        return icclim.index(
            index_name="TG",
            in_files=tas,
            var_name="tas",
            time_range=TIME_RANGE,
            slice_mode="MS",
        )
    if workload == "tg_djf_seasonal":
        tas = _open_var(TAS_GLOB, "tas")
        return icclim.index(
            index_name="TG",
            in_files=tas,
            var_name="tas",
            time_range=TIME_RANGE,
            slice_mode="DJF",
        )
    if workload == "rr1_yearly":
        pr = _open_var(PR_GLOB, "pr")
        return icclim.index(
            index_name="RR1",
            in_files=pr,
            var_name="pr",
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "su_tasmax_yearly":
        tasmax = _open_var(TASMAX_GLOB, "tasmax")
        return icclim.index(
            index_name="SU",
            in_files=tasmax,
            var_name="tasmax",
            time_range=TASMAX_TIME_RANGE,
            slice_mode="year",
        )
    if workload == "prcptot_yearly":
        pr = _open_var(PR_GLOB, "pr")
        return icclim.index(
            index_name="PRCPTOT",
            in_files=pr,
            var_name="pr",
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_count_date_event_monthly":
        # A smaller real-data subset keeps this generic date-event validation
        # representative without turning the oracle run into an overnight job.
        tas = _open_var(
            TAS_GLOB,
            "tas",
            lat_slice=DATE_EVENT_LAT_SLICE,
            lon_slice=DATE_EVENT_LON_SLICE,
        )
        return icclim.count_occurrences(
            in_files=tas,
            var_name="tas",
            threshold="> 25 degC",
            time_range=DATE_EVENT_TIME_RANGE,
            slice_mode="month",
            date_event=True,
        )
    if workload == "generic_tas_bounded_count_yearly":
        tas = _open_var(TAS_GLOB, "tas")
        percentile_threshold = icclim.threshold.build_threshold(
            "> 90 doy_per",
            reference_period=BASE_PERIOD,
        )
        return icclim.count_occurrences(
            in_files=tas,
            var_name="tas",
            threshold=icclim.threshold.build_threshold(
                thresholds=[percentile_threshold, "<= 30 degC"],
                logical_link="and",
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_pr_fraction_bootstrap_yearly":
        pr = _open_var(PR_GLOB, "pr")
        return icclim.fraction_of_total(
            in_files=pr,
            var_name="pr",
            threshold=icclim.threshold.build_threshold(
                "> 95 doy_per",
                threshold_min_value="1 mm/day",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
        )
    if workload == "generic_tas_spell_bootstrap_yearly":
        tas = _open_var(TAS_GLOB, "tas")
        return icclim.sum_of_spell_lengths(
            in_files=tas,
            var_name="tas",
            threshold=icclim.threshold.build_threshold(
                "> 90 doy_per",
                reference_period=BASE_PERIOD,
            ),
            time_range=TIME_RANGE,
            slice_mode="year",
            min_spell_length=6,
        )
    if workload == "tg90p_save_thresholds_monthly":
        tas = _open_var(TAS_GLOB, "tas")
        return icclim.index(
            index_name="TG90p",
            in_files=tas,
            var_name="tas",
            base_period_time_range=BASE_PERIOD,
            time_range=TIME_RANGE,
            slice_mode="MS",
            save_thresholds=True,
        )
    if workload == "combined_cd_yearly":
        # Compound logical-link indices currently exercise xarray boolean
        # operations that behave differently on lazy arrays across versions.
        # Loading the subset keeps this as a real-data validation while making
        # the oracle path executable.
        ds = _open_combined_dataset(eager=True)
        return icclim.index(
            index_name="CD",
            in_files=ds,
            time_range=TIME_RANGE,
            base_period_time_range=BASE_PERIOD,
            slice_mode="year",
        )
    if workload == "indices_mixed_yearly":
        ds = _open_combined_dataset(eager=True)
        # Keep the mixed multi-index validation on the tas+pr pair, but avoid
        # compound logical-link indices here because the oracle release itself
        # is currently blocked by an upstream xarray boolean-operation issue.
        return icclim.indices(
            index_group=["TG", "RR1", "PRCPTOT", "TG90p"],
            in_files=ds,
            time_range=TIME_RANGE,
            base_period_time_range=BASE_PERIOD,
            slice_mode="year",
            ignore_error=False,
        )
    if workload == "indices_mixed_with_cd_yearly":
        ds = _open_combined_dataset(eager=True)
        return icclim.indices(
            index_group=["TG", "RR1", "PRCPTOT", "CD", "TG90p"],
            in_files=ds,
            time_range=TIME_RANGE,
            base_period_time_range=BASE_PERIOD,
            slice_mode="year",
            ignore_error=False,
        )
    msg = f"Unknown workload: {workload}"
    raise ValueError(msg)


def _dataset_summary(ds: xr.Dataset) -> dict[str, object]:
    var_means = {}
    for name, data_var in ds.data_vars.items():
        if np.issubdtype(data_var.dtype, np.number):
            var_means[name] = float(data_var.mean(skipna=True).item())
        else:
            var_means[name] = None
    return {
        "data_vars": list(ds.data_vars),
        "coords": list(ds.coords),
        "sizes": {name: int(size) for name, size in ds.sizes.items()},
        "var_means": var_means,
        "dataset_attrs": sorted(ds.attrs),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo / "src"))
    import icclim

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    _warmup(icclim)
    start = time.perf_counter()
    ds = _build_workload(icclim, args.workload).load()
    duration = time.perf_counter() - start

    result_nc = out_dir / f"{args.label}-{args.workload}.result.nc"
    summary_json = out_dir / f"{args.label}-{args.workload}.summary.json"
    ds.to_netcdf(result_nc)

    summary = {
        "label": args.label,
        "workload": args.workload,
        "repo": str(repo),
        "head_commit": _git_rev_parse(repo, "HEAD"),
        "icclim_version": icclim.__version__,
        "duration_seconds": duration,
        "output_path": str(result_nc),
        "dataset": _dataset_summary(ds),
    }
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

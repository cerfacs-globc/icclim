"""Micro-benchmark of the compiled percentile bootstrap count (not run in CI).

Compares the default kernel (incremental replicate percentiles) with the reference
one (``ICCLIM_BOOTSTRAP_PERCENTILE=reference``) on synthetic data.

Example::

    python tools/benchmark_bootstrap_percentile.py --threads 4 --bases 10 20 30 \
        --windows 1 5 --cells 10 --study-years 30
"""

from __future__ import annotations

import argparse
import os
import time
import warnings


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--threads", type=int, default=0, help="NUMBA_NUM_THREADS")
    parser.add_argument("--bases", type=int, nargs="+", default=[10, 20, 30])
    parser.add_argument("--windows", type=int, nargs="+", default=[1, 5])
    parser.add_argument("--cells", type=int, default=10, help="grid is cells x cells")
    parser.add_argument("--study-years", type=int, default=0, help="0: base + 10")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.threads:
        os.environ["NUMBA_NUM_THREADS"] = str(args.threads)
    warnings.filterwarnings("ignore")
    import numba
    import numpy as np
    import pandas as pd
    import xarray as xr

    from icclim import build_threshold
    from icclim._core.generic.bootstrap import (
        compute_doy_percentile_bootstrap_count,
    )

    print(f"threads={numba.get_num_threads()} grid={args.cells}x{args.cells}")
    print("n_base  w  study  reference_s  incremental_s  speedup")
    rng = np.random.default_rng(1)
    for n_base in args.bases:
        n_study = args.study_years or n_base + 10
        time_axis = pd.date_range("1961-01-01", f"{1961 + n_study - 1}-12-31", freq="D")
        doy = time_axis.dayofyear.to_numpy()[:, None, None]
        data = 285 + 8 * np.sin(2 * np.pi * (doy - 100) / 365.25)
        data = data + rng.normal(0, 3, (len(time_axis), args.cells, args.cells))
        study = xr.DataArray(
            data.astype("float32"),
            dims=("time", "lat", "lon"),
            coords={
                "time": time_axis,
                "lat": np.arange(args.cells) * 1.0,
                "lon": np.arange(args.cells) * 1.0,
            },
            attrs={"units": "K"},
            name="tasmax",
        ).chunk({"time": 730})
        for window in args.windows:
            threshold = build_threshold(
                "> 90 doy_per",
                reference_period=["1961-01-01", f"{1961 + n_base - 1}-12-31"],
                doy_window_width=window,
            )
            timings = {}
            results = {}
            for mode in ("reference", "default"):
                os.environ["ICCLIM_BOOTSTRAP_PERCENTILE"] = mode
                compute_doy_percentile_bootstrap_count(  # warm-up (compilation)
                    study.isel(lat=slice(0, 2), lon=slice(0, 2)).isel(
                        time=slice(0, 365 * (n_base + 1))
                    ),
                    threshold,
                    "YS",
                )
                start = time.perf_counter()
                results[mode] = compute_doy_percentile_bootstrap_count(
                    study, threshold, "YS"
                )
                timings[mode] = time.perf_counter() - start
            same = np.array_equal(
                results["reference"].values, results["default"].values
            )
            print(
                f"{n_base:6d} {window:2d} {n_study:6d} {timings['reference']:11.2f} "
                f"{timings['default']:13.2f} {timings['reference'] / timings['default']:8.2f}"
                f"{'' if same else '  RESULTS DIFFER'}"
            )
    os.environ.pop("ICCLIM_BOOTSTRAP_PERCENTILE", None)


if __name__ == "__main__":
    main()

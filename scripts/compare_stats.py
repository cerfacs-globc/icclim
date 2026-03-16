"""Utility to compare climate indices statistics between versions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import icclim

if TYPE_CHECKING:
    import xarray as xr


def get_stats(da: xr.DataArray) -> dict[str, float]:
    """Calculate summary statistics for a DataArray."""
    return {
        "mean": float(da.mean().values),
        "min": float(da.min().values),
        "max": float(da.max().values),
        "std": float(da.std().values),
    }


def main(output_file: str, data_path_str: str | None = None) -> None:
    """Compute statistics for standard indices and save to JSON."""
    if data_path_str is None:
        data_path = Path(
            "/Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/data/latest"
        )
    else:
        data_path = Path(data_path_str)

    # Patterns for CMIP6 data
    tas_files = [str(f) for f in data_path.glob("tas_day*CMCC*historical*2014*.nc")]
    pr_files = [str(f) for f in data_path.glob("pr_day*CMCC*historical*2014*.nc")]

    if not tas_files or not pr_files:
        print(f"Error: No NetCDF files found in {data_path}")  # noqa: T201
        sys.exit(1)

    results = {}

    print(  # noqa: T201
        f"Computing statistics for {icclim.__name__} {icclim.__version__}..."
    )

    # 1. SU (Summer Days)
    su = icclim.index(index_name="SU", in_files=tas_files, var_name="tas")
    results["SU"] = get_stats(su.SU)

    # 2. TG (Average Temperature)
    tg = icclim.index(index_name="TG", in_files=tas_files, var_name="tas")
    results["TG"] = get_stats(tg.TG)

    # 3. PRCPTOT (Total Precipitation)
    prcptot = icclim.index(index_name="PRCPTOT", in_files=pr_files, var_name="pr")
    results["PRCPTOT"] = get_stats(prcptot.PRCPTOT)

    with Path(output_file).open("w") as f:
        json.dump(results, f, indent=4)
    print(f"Stats saved to {output_file}")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compare_stats.py <output_json> [data_path]")  # noqa: T201
    else:
        out = sys.argv[1]
        dp = sys.argv[2] if len(sys.argv) > 2 else None
        main(out, dp)

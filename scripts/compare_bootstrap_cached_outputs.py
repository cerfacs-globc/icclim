"""Compare cached TG90p benchmark outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import xarray as xr


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare cached TG90p benchmark outputs.",
    )
    parser.add_argument("--left", type=Path, required=True, help="Left NetCDF result.")
    parser.add_argument(
        "--right", type=Path, required=True, help="Right NetCDF result."
    )
    parser.add_argument(
        "--label-left",
        default="left",
        help="Human-readable label for the left result.",
    )
    parser.add_argument(
        "--label-right",
        default="right",
        help="Human-readable label for the right result.",
    )
    return parser.parse_args()


def main() -> None:
    """Print a JSON summary of numerical differences between two outputs."""
    args = _parse_args()
    left = xr.open_dataarray(args.left)
    right = xr.open_dataarray(args.right)
    diff = left - right
    mask = ~np.isclose(diff.values, 0.0, atol=1e-10, rtol=1e-10)
    per_year = np.abs(diff).mean(dim=("lat", "lon"), skipna=True)
    top = per_year.to_series().sort_values(ascending=False).head(10)
    summary = {
        f"{args.label_left}_mean": float(left.mean().item()),
        f"{args.label_right}_mean": float(right.mean().item()),
        "mean_diff": float(diff.mean().item()),
        "max_abs_diff": float(np.nanmax(np.abs(diff.values))),
        "changed_cells": int(mask.sum()),
        "n_cells": int(diff.size),
        "top_year_mean_abs_diff": {str(k): float(v) for k, v in top.items()},
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

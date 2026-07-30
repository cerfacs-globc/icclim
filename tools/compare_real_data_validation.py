from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import xarray as xr


def _compare_numeric(a: xr.DataArray, b: xr.DataArray) -> dict[str, object]:
    a_values = np.asarray(a.values)
    b_values = np.asarray(b.values)
    changed = ~np.isclose(a_values, b_values, atol=1e-10, rtol=1e-10, equal_nan=True)
    diff = a_values - b_values
    finite_diff = np.where(np.isfinite(diff), np.abs(diff), np.nan)
    return {
        "equal": bool(np.all(~changed)),
        "max_abs_diff": float(np.nanmax(finite_diff)) if finite_diff.size else 0.0,
        "mean_abs_diff": float(np.nanmean(finite_diff)) if finite_diff.size else 0.0,
        "changed_cells": int(np.count_nonzero(changed)),
        "n_cells": int(a.size),
    }


def _compare_non_numeric(a: xr.DataArray, b: xr.DataArray) -> dict[str, object]:
    equal = bool(a.equals(b))
    return {
        "equal": equal,
        "changed_cells": 0 if equal else -1,
    }


def _compare_variable(a: xr.DataArray, b: xr.DataArray) -> dict[str, object]:
    if a.dims != b.dims:
        return {"equal": False, "reason": f"dims differ: {a.dims} vs {b.dims}"}
    if a.shape != b.shape:
        return {"equal": False, "reason": f"shape differ: {a.shape} vs {b.shape}"}
    if np.issubdtype(a.dtype, np.number) and np.issubdtype(b.dtype, np.number):
        return _compare_numeric(a, b)
    return _compare_non_numeric(a, b)


def _compare_datasets(current_path: Path, baseline_path: Path) -> dict[str, object]:
    current = xr.open_dataset(current_path)
    baseline = xr.open_dataset(baseline_path)

    shared_data_vars = sorted(set(current.data_vars) & set(baseline.data_vars))
    shared_coords = sorted(set(current.coords) & set(baseline.coords))

    data_var_comparison = {
        name: _compare_variable(current[name], baseline[name]) for name in shared_data_vars
    }
    coord_comparison = {
        name: _compare_variable(current.coords[name], baseline.coords[name])
        for name in shared_coords
        if name != "time"
    }

    dataset_attrs = {
        "current": sorted(current.attrs),
        "baseline": sorted(baseline.attrs),
        "history_equal": current.attrs.get("history") == baseline.attrs.get("history"),
        "non_history_equal": {
            key: current.attrs.get(key) == baseline.attrs.get(key)
            for key in sorted((set(current.attrs) | set(baseline.attrs)) - {"history"})
        },
    }

    return {
        "current_path": str(current_path),
        "baseline_path": str(baseline_path),
        "current_data_vars": sorted(current.data_vars),
        "baseline_data_vars": sorted(baseline.data_vars),
        "current_coords": sorted(current.coords),
        "baseline_coords": sorted(baseline.coords),
        "data_var_comparison": data_var_comparison,
        "coord_comparison": coord_comparison,
        "dataset_attrs": dataset_attrs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    summary = _compare_datasets(Path(args.current), Path(args.baseline))
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

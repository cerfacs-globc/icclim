"""Assess icclim outputs against manual reference computations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import xarray as xr
from xarray import DataArray, Dataset
from xclim.core.calendar import select_time
from xclim.core.units import rate2amount

import icclim
from icclim._core.constants import UNITS_KEY
from icclim._core.generic.functions import _is_rate, check_freq
from icclim.frequency import Frequency, FrequencyRegistry

WET_DAY_THRESHOLD = 1.0


def _parse_slice_mode(raw: str) -> object:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _reduce_to_point(ds: Dataset, isel_specs: list[str]) -> Dataset:
    if not isel_specs:
        return ds
    indexers: dict[str, int] = {}
    for spec in isel_specs:
        if "=" not in spec:
            msg = f"Invalid --isel value {spec!r}, expected DIM=INDEX."
            raise ValueError(msg)
        dim, raw_index = spec.split("=", 1)
        indexers[dim] = int(raw_index)
    return ds.isel(indexers, drop=True)


def _subset_for_slice_mode(
    da: DataArray, slice_mode: object
) -> tuple[DataArray, Frequency]:
    freq = FrequencyRegistry.lookup(slice_mode)
    if freq.indexer:
        da = select_time(da, **freq.indexer, drop=True)
    return da, freq


def _threshold_count(
    da: DataArray,
    slice_mode: object,
    threshold: float,
    op: str,
) -> DataArray:
    subset, freq = _subset_for_slice_mode(da, slice_mode)
    if op == ">":
        hits = subset > threshold
    elif op == ">=":
        hits = subset >= threshold
    else:
        msg = f"Unsupported threshold operator {op!r}."
        raise ValueError(msg)
    out = hits.resample(time=freq.pandas_freq).sum(dim="time")
    out.attrs[UNITS_KEY] = "day"
    return out


def _manual_rr(da: DataArray, slice_mode: object) -> DataArray:
    subset, freq = _subset_for_slice_mode(da, slice_mode)
    if _is_rate(subset):
        subset = rate2amount(subset)
    return subset.resample(time=freq.pandas_freq).sum(dim="time")


def _manual_prcptot(da: DataArray, slice_mode: object) -> DataArray:
    subset, freq = _subset_for_slice_mode(da, slice_mode)
    if _is_rate(subset):
        subset = rate2amount(subset)
    return (
        subset.where(subset >= WET_DAY_THRESHOLD, 0)
        .resample(time=freq.pandas_freq)
        .sum(dim="time")
    )


def _manual_mean(da: DataArray, slice_mode: object) -> DataArray:
    subset, freq = _subset_for_slice_mode(da, slice_mode)
    return subset.resample(time=freq.pandas_freq).mean(dim="time")


def _manual_max(da: DataArray, slice_mode: object) -> DataArray:
    subset, freq = _subset_for_slice_mode(da, slice_mode)
    return subset.resample(time=freq.pandas_freq).max(dim="time")


def _manual_min(da: DataArray, slice_mode: object) -> DataArray:
    subset, freq = _subset_for_slice_mode(da, slice_mode)
    return subset.resample(time=freq.pandas_freq).min(dim="time")


MANUAL_COMPARATORS = {
    "PRCPTOT": _manual_prcptot,
    "R10MM": lambda da, slice_mode: _threshold_count(da, slice_mode, 10.0, ">="),
    "R20MM": lambda da, slice_mode: _threshold_count(da, slice_mode, 20.0, ">="),
    "RR": _manual_rr,
    "RR1": lambda da, slice_mode: _threshold_count(da, slice_mode, 1.0, ">="),
    "SU": lambda da, slice_mode: _threshold_count(da, slice_mode, 25.0, ">"),
    "TG": _manual_mean,
    "TN": _manual_mean,
    "TNN": _manual_min,
    "TNX": _manual_max,
    "TR": lambda da, slice_mode: _threshold_count(da, slice_mode, 20.0, ">"),
    "TX": _manual_mean,
    "TXN": _manual_min,
    "TXX": _manual_max,
}


def _data_var_name(ds: Dataset) -> str:
    if len(ds.data_vars) != 1:
        msg = f"Expected exactly one data variable, found {list(ds.data_vars)}."
        raise ValueError(msg)
    return next(iter(ds.data_vars))


def _summarize_result(icclim_da: DataArray, manual_da: DataArray) -> dict[str, object]:
    if "time" in icclim_da.dims and "time" in manual_da.dims:
        if icclim_da.sizes["time"] != manual_da.sizes["time"]:
            msg = (
                "Manual reference and icclim result have different numbers of periods: "
                f"{manual_da.sizes['time']} vs {icclim_da.sizes['time']}."
            )
            raise ValueError(msg)
        aligned_icclim = icclim_da
        aligned_manual = manual_da.assign_coords(time=icclim_da.time)
    else:
        aligned_icclim, aligned_manual = xr.align(icclim_da, manual_da, join="inner")
    abs_diff = abs(aligned_icclim - aligned_manual)
    max_abs_diff = float(abs_diff.max().compute().item())
    return {
        "period_count": int(aligned_icclim.sizes.get("time", 1)),
        "icclim_units": icclim_da.attrs.get(UNITS_KEY),
        "manual_units": manual_da.attrs.get(UNITS_KEY),
        "max_abs_diff": max_abs_diff,
        "icclim_values": aligned_icclim.values.tolist(),
        "manual_values": aligned_manual.values.tolist(),
        "time": [str(t) for t in aligned_icclim.time.values],
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Compare an icclim index against a simple manual reference "
            "computation and export a reduced subset for external tools."
        )
    )
    parser.add_argument("--in-file", required=True, help="Input NetCDF file path.")
    parser.add_argument("--var-name", required=True, help="Target variable name.")
    parser.add_argument(
        "--index-name",
        required=True,
        help="icclim index name, for example RR, PRCPTOT, SU, TG, TXx.",
    )
    parser.add_argument(
        "--slice-mode",
        required=True,
        help='icclim slice_mode, for example "JJA" or ["season", [6, 7, 8]].',
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where reports and optional subsets will be written.",
    )
    parser.add_argument(
        "--isel",
        action="append",
        default=[],
        help="Optional point extraction before comparison, repeated as DIM=INDEX.",
    )
    return parser


def main() -> None:
    """Run the reference comparison CLI."""
    parser = build_parser()
    args = parser.parse_args()

    index_name = args.index_name.upper()
    if index_name not in MANUAL_COMPARATORS:
        msg = (
            f"Unsupported index {args.index_name!r}. "
            f"Supported indices: {sorted(MANUAL_COMPARATORS)}."
        )
        raise ValueError(msg)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    slice_mode = _parse_slice_mode(args.slice_mode)
    source_ds = xr.open_dataset(args.in_file)
    source_ds = _reduce_to_point(source_ds, args.isel)
    da = source_ds[args.var_name]

    inferred_freq = check_freq(da, strict=False)
    icclim_res = icclim.index(
        index_name=args.index_name,
        in_files=source_ds,
        var_name=args.var_name,
        slice_mode=slice_mode,
        logs_verbosity="silent",
    )
    icclim_var_name = _data_var_name(icclim_res)
    icclim_da = icclim_res[icclim_var_name].load()
    manual_da = MANUAL_COMPARATORS[index_name](da, slice_mode).load()

    summary = {
        "input_file": str(Path(args.in_file).resolve()),
        "var_name": args.var_name,
        "index_name": args.index_name,
        "slice_mode": slice_mode,
        "input_units": da.attrs.get(UNITS_KEY),
        "input_frequency": inferred_freq,
        "assessment": _summarize_result(icclim_da, manual_da),
    }

    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    subset_path = output_dir / "reference_subset.nc"
    source_ds[[args.var_name]].to_netcdf(subset_path)

    print(f"Wrote assessment to {summary_path}")
    print(f"Wrote reduced subset to {subset_path}")


if __name__ == "__main__":
    main()

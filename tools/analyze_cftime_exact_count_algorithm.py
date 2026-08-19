from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

import numpy as np
import xarray as xr

from icclim._core.constants import UNITS_KEY
from icclim._core.generic.bootstrap_primitives import (
    build_bootstrap_prepared_inputs,
)
from icclim.threshold.factory import build_threshold

NON_LEAP_DAY_COUNT = 365


@dataclass(frozen=True)
class ThresholdBankEstimate:
    name: str
    threshold_series_per_cell: int
    bytes_per_cell_float64: int
    bytes_per_cell_float32: int
    bytes_total_float64: int
    bytes_total_float32: int


@dataclass(frozen=True)
class CountAlgorithmAnalysis:
    study_year_count: int
    reference_year_count: int
    overlap_year_count: int
    non_overlap_year_count: int
    output_group_count: int
    spatial_cell_count: int
    current_threshold_series_per_cell: int
    nominal_series_per_cell: int
    overlap_series_per_cell: int
    reusable_nominal_series_savings_per_cell: int
    estimates: list[ThresholdBankEstimate]


def _build_synthetic_cftime_tas(
    *,
    start_year: int,
    study_year_count: int,
    lat_length: int,
    lon_length: int,
) -> xr.DataArray:
    end_year = start_year + study_year_count - 1
    time = xr.date_range(
        f"{start_year}-01-01",
        f"{end_year}-12-31",
        freq="D",
        use_cftime=True,
    )
    values = np.full(
        (len(time), lat_length, lon_length),
        300.0,
        dtype=np.float32,
    )
    return xr.DataArray(
        values,
        dims=["time", "lat", "lon"],
        coords={
            "time": time,
            "lat": np.arange(lat_length),
            "lon": np.arange(lon_length),
        },
        attrs={UNITS_KEY: "K"},
        name="tas",
    )


def _estimate_bank(
    *,
    name: str,
    threshold_series_per_cell: int,
    spatial_cell_count: int,
) -> ThresholdBankEstimate:
    bytes_per_cell_float64 = threshold_series_per_cell * NON_LEAP_DAY_COUNT * 8
    bytes_per_cell_float32 = threshold_series_per_cell * NON_LEAP_DAY_COUNT * 4
    return ThresholdBankEstimate(
        name=name,
        threshold_series_per_cell=threshold_series_per_cell,
        bytes_per_cell_float64=bytes_per_cell_float64,
        bytes_per_cell_float32=bytes_per_cell_float32,
        bytes_total_float64=bytes_per_cell_float64 * spatial_cell_count,
        bytes_total_float32=bytes_per_cell_float32 * spatial_cell_count,
    )


def analyze_count_algorithm(
    *,
    start_year: int,
    study_year_count: int,
    reference_start_year: int,
    reference_year_count: int,
    lat_length: int,
    lon_length: int,
    freq: str,
) -> CountAlgorithmAnalysis:
    tas = _build_synthetic_cftime_tas(
        start_year=start_year,
        study_year_count=study_year_count,
        lat_length=lat_length,
        lon_length=lon_length,
    )
    reference_end_year = reference_start_year + reference_year_count - 1
    threshold = build_threshold(
        query="> 90 doy_per",
        reference_period=(
            f"{reference_start_year}-01-01",
            f"{reference_end_year}-12-31",
        ),
    )
    prepared = build_bootstrap_prepared_inputs(
        tas,
        threshold,
        freq,
        dtype=np.float64,
    )
    indexing = prepared.temporal_indexing
    spatial_cell_count = int(np.prod(prepared.array_inputs.spatial_shape))
    overlap_year_count = int(np.count_nonzero(indexing.year_to_reference_index >= 0))
    non_overlap_year_count = len(indexing.bootstrap_years) - overlap_year_count
    nominal_series_per_cell = 1
    overlap_series_per_cell = overlap_year_count * (reference_year_count - 1)
    current_threshold_series_per_cell = (
        non_overlap_year_count + overlap_series_per_cell
    )
    full_bank_series_per_cell = nominal_series_per_cell + overlap_series_per_cell
    per_target_bank_series_per_cell = max(1, reference_year_count - 1)
    estimates = [
        _estimate_bank(
            name="current_full_rebuild_work",
            threshold_series_per_cell=current_threshold_series_per_cell,
            spatial_cell_count=spatial_cell_count,
        ),
        _estimate_bank(
            name="full_threshold_bank",
            threshold_series_per_cell=full_bank_series_per_cell,
            spatial_cell_count=spatial_cell_count,
        ),
        _estimate_bank(
            name="single_target_threshold_bank",
            threshold_series_per_cell=per_target_bank_series_per_cell,
            spatial_cell_count=spatial_cell_count,
        ),
        _estimate_bank(
            name="nominal_only_cache",
            threshold_series_per_cell=nominal_series_per_cell,
            spatial_cell_count=spatial_cell_count,
        ),
    ]
    return CountAlgorithmAnalysis(
        study_year_count=len(indexing.bootstrap_years),
        reference_year_count=reference_year_count,
        overlap_year_count=overlap_year_count,
        non_overlap_year_count=non_overlap_year_count,
        output_group_count=len(indexing.output_group_labels),
        spatial_cell_count=spatial_cell_count,
        current_threshold_series_per_cell=current_threshold_series_per_cell,
        nominal_series_per_cell=nominal_series_per_cell,
        overlap_series_per_cell=overlap_series_per_cell,
        reusable_nominal_series_savings_per_cell=max(0, non_overlap_year_count - 1),
        estimates=estimates,
    )


def _as_json_ready(analysis: CountAlgorithmAnalysis) -> dict[str, object]:
    payload = asdict(analysis)
    payload["estimates"] = [asdict(item) for item in analysis.estimates]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int, default=1950)
    parser.add_argument("--study-years", type=int, default=65)
    parser.add_argument("--reference-start-year", type=int, default=1961)
    parser.add_argument("--reference-years", type=int, default=30)
    parser.add_argument("--lat-length", type=int, default=28)
    parser.add_argument("--lon-length", type=int, default=21)
    parser.add_argument("--freq", default="MS")
    args = parser.parse_args()

    analysis = analyze_count_algorithm(
        start_year=args.start_year,
        study_year_count=args.study_years,
        reference_start_year=args.reference_start_year,
        reference_year_count=args.reference_years,
        lat_length=args.lat_length,
        lon_length=args.lon_length,
        freq=args.freq,
    )
    print(json.dumps(_as_json_ready(analysis), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

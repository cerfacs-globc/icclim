from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import xarray as xr

NON_LEAP_DAY_COUNT = 365


@dataclass(frozen=True)
class ReplacementStructureSummary:
    max_samples_per_doy: int
    min_samples_per_doy: int
    mean_samples_per_doy: float
    max_target_year_slots_per_doy: int
    min_target_year_slots_per_doy: int
    mean_target_year_slots_per_doy: float
    max_effective_substitute_slots_per_doy: int
    min_effective_substitute_slots_per_doy: int
    mean_effective_substitute_slots_per_doy: float


@dataclass(frozen=True)
class OrderStatDesignAnalysis:
    study_year_count: int
    reference_year_count: int
    overlap_year_count: int
    non_overlap_year_count: int
    output_group_count: int
    spatial_cell_count: int
    current_threshold_series_per_cell: int
    overlap_series_per_cell: int
    replacement_structure: ReplacementStructureSummary


def _resolve_import_root(repo: Path) -> Path:
    for candidate in (repo / "src", repo):
        if (candidate / "icclim" / "__init__.py").is_file():
            return candidate
    msg = f"Could not locate icclim import root under {repo}"
    raise FileNotFoundError(msg)


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
    values = np.full((len(time), lat_length, lon_length), 300.0, dtype=np.float32)
    return xr.DataArray(
        values,
        dims=["time", "lat", "lon"],
        coords={
            "time": time,
            "lat": np.arange(lat_length),
            "lon": np.arange(lon_length),
        },
        attrs={"units": "K"},
        name="tas",
    )


def _summarize_replacement_structure(
    sample_indices: np.ndarray,
    index_year: np.ndarray,
    index_pos: np.ndarray,
    substitute_aligned: np.ndarray,
) -> ReplacementStructureSummary:
    n_doys = sample_indices.shape[0]
    n_ref_years = substitute_aligned.shape[1]
    sample_count_per_doy = np.count_nonzero(sample_indices >= 0, axis=1)
    target_year_slots = np.zeros((n_ref_years, n_doys), dtype=np.int64)
    effective_substitute_slots = []

    for doy_i in range(n_doys):
        for sample_i in range(sample_indices.shape[1]):
            ref_i = sample_indices[doy_i, sample_i]
            if ref_i < 0:
                continue
            target_ref_i = index_year[ref_i]
            if target_ref_i < 0:
                continue
            target_year_slots[target_ref_i, doy_i] += 1

    for target_ref_i in range(n_ref_years):
        for substitute_i in range(n_ref_years):
            if substitute_i == target_ref_i:
                continue
            for doy_i in range(n_doys):
                count = 0
                for sample_i in range(sample_indices.shape[1]):
                    ref_i = sample_indices[doy_i, sample_i]
                    if ref_i < 0 or index_year[ref_i] != target_ref_i:
                        continue
                    mapped_i = substitute_aligned[
                        target_ref_i,
                        substitute_i,
                        index_pos[ref_i],
                    ]
                    if mapped_i >= 0:
                        count += 1
                effective_substitute_slots.append(count)

    non_zero_target_slots = target_year_slots[target_year_slots > 0]
    effective_substitute_slots_array = np.asarray(
        effective_substitute_slots,
        dtype=np.int64,
    )
    max_samples_per_doy = (
        int(sample_count_per_doy.max()) if sample_count_per_doy.size else 0
    )
    min_samples_per_doy = (
        int(sample_count_per_doy.min()) if sample_count_per_doy.size else 0
    )
    max_target_year_slots_per_doy = (
        int(non_zero_target_slots.max()) if non_zero_target_slots.size else 0
    )
    min_target_year_slots_per_doy = (
        int(non_zero_target_slots.min()) if non_zero_target_slots.size else 0
    )
    max_effective_substitute_slots_per_doy = (
        int(effective_substitute_slots_array.max())
        if effective_substitute_slots_array.size
        else 0
    )
    min_effective_substitute_slots_per_doy = (
        int(effective_substitute_slots_array.min())
        if effective_substitute_slots_array.size
        else 0
    )
    return ReplacementStructureSummary(
        max_samples_per_doy=max_samples_per_doy,
        min_samples_per_doy=min_samples_per_doy,
        mean_samples_per_doy=float(sample_count_per_doy.mean()),
        max_target_year_slots_per_doy=max_target_year_slots_per_doy,
        min_target_year_slots_per_doy=min_target_year_slots_per_doy,
        mean_target_year_slots_per_doy=float(non_zero_target_slots.mean()),
        max_effective_substitute_slots_per_doy=max_effective_substitute_slots_per_doy,
        min_effective_substitute_slots_per_doy=min_effective_substitute_slots_per_doy,
        mean_effective_substitute_slots_per_doy=float(
            effective_substitute_slots_array.mean()
        ),
    )


def analyze_order_stat_design(
    *,
    start_year: int,
    study_year_count: int,
    reference_start_year: int,
    reference_year_count: int,
    lat_length: int,
    lon_length: int,
    freq: str,
) -> OrderStatDesignAnalysis:
    from icclim._core.generic.bootstrap_primitives import (
        build_bootstrap_prepared_inputs,
    )
    from icclim.threshold.factory import build_threshold

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
    overlap_year_count = int(np.count_nonzero(indexing.year_to_reference_index >= 0))
    non_overlap_year_count = len(indexing.bootstrap_years) - overlap_year_count
    overlap_series_per_cell = overlap_year_count * (reference_year_count - 1)
    replacement_structure = _summarize_replacement_structure(
        indexing.sample_indices_by_day_of_year,
        indexing.reference_index_year,
        indexing.reference_index_position,
        indexing.substitute_alignment,
    )
    return OrderStatDesignAnalysis(
        study_year_count=len(indexing.bootstrap_years),
        reference_year_count=reference_year_count,
        overlap_year_count=overlap_year_count,
        non_overlap_year_count=non_overlap_year_count,
        output_group_count=len(indexing.output_group_labels),
        spatial_cell_count=int(np.prod(prepared.array_inputs.spatial_shape)),
        current_threshold_series_per_cell=(
            non_overlap_year_count + overlap_series_per_cell
        ),
        overlap_series_per_cell=overlap_series_per_cell,
        replacement_structure=replacement_structure,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--start-year", type=int, default=1950)
    parser.add_argument("--study-years", type=int, default=65)
    parser.add_argument("--reference-start-year", type=int, default=1961)
    parser.add_argument("--reference-years", type=int, default=30)
    parser.add_argument("--lat-length", type=int, default=28)
    parser.add_argument("--lon-length", type=int, default=21)
    parser.add_argument("--freq", default="MS")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(_resolve_import_root(repo)))

    analysis = analyze_order_stat_design(
        start_year=args.start_year,
        study_year_count=args.study_years,
        reference_start_year=args.reference_start_year,
        reference_year_count=args.reference_years,
        lat_length=args.lat_length,
        lon_length=args.lon_length,
        freq=args.freq,
    )
    print(json.dumps(asdict(analysis), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

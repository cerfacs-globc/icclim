"""Reusable threshold and indexing helpers for percentile bootstrap.

These helpers keep bootstrap workflow steps visible in domain language:

1. build the reference sample used by bootstrap;
2. build the temporal indexing needed by bootstrap kernels;
3. let family-specific implementations focus on their own reducer logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd
    from xarray import DataArray

    from icclim._core.generic.threshold.percentile import PercentileThreshold


LEAP_YEAR_DAY_COUNT = 366


@dataclass(frozen=True)
class BootstrapReferenceSample:
    """Reference-period data prepared for bootstrap threshold generation."""

    study: DataArray
    climatology_bounds: tuple[str, str]
    reference_sample: DataArray
    filtered_reference_sample: DataArray
    threshold_floor_in_reference_units: float | None


@dataclass(frozen=True)
class BootstrapTemporalIndexing:
    """Year and resampling indexes shared by bootstrap implementations."""

    reference_year_indices: dict[int, np.ndarray]
    study_year_indices: dict[int, np.ndarray]
    output_group_indices: dict[np.datetime64, np.ndarray]
    output_group_labels: list[np.datetime64]
    output_starts: np.ndarray
    output_lengths: np.ndarray
    output_years: np.ndarray
    bootstrap_years: np.ndarray
    year_group_starts: np.ndarray
    year_group_stops: np.ndarray
    year_max_day_of_years: np.ndarray
    year_to_reference_index: np.ndarray
    study_day_of_years: np.ndarray
    sample_indices_by_day_of_year: np.ndarray
    reference_index_year: np.ndarray
    reference_index_position: np.ndarray
    substitute_alignment: np.ndarray


@dataclass(frozen=True)
class BootstrapArrayInputs:
    """Flattened arrays shared by optimized bootstrap kernels."""

    flat_study: np.ndarray
    flat_reference_raw: np.ndarray
    flat_reference_filtered: np.ndarray
    spatial_shape: tuple[int, ...]


def build_bootstrap_output(
    *,
    flat_result: np.ndarray,
    reference_sample: BootstrapReferenceSample,
    temporal_indexing: BootstrapTemporalIndexing,
    spatial_shape: tuple[int, ...],
    units: str,
) -> DataArray:
    """Rebuild an xarray result from bootstrap kernel output."""
    import xarray as xr  # noqa: PLC0415

    data = flat_result.reshape(
        (len(temporal_indexing.output_group_labels), *spatial_shape)
    )
    output = xr.DataArray(
        data,
        dims=reference_sample.study.dims,
        coords={
            "time": temporal_indexing.output_group_labels,
            **{
                coord: reference_sample.study.coords[coord]
                for coord in reference_sample.study.dims
                if coord != "time"
            },
        },
        attrs={
            "units": units,
            "climatology_bounds": reference_sample.climatology_bounds,
        },
    )
    for coord in reference_sample.study.coords:
        if (
            coord not in output.coords
            and "time" not in reference_sample.study[coord].dims
        ):
            output = output.assign_coords({coord: reference_sample.study[coord]})
    return output


def build_bootstrap_reference_sample(
    study: DataArray,
    threshold: PercentileThreshold,
) -> BootstrapReferenceSample:
    """Load and prepare the reference-period sample for bootstrap."""
    loaded_study = study.load()
    climatology_bounds = threshold.climatology_bounds(loaded_study)
    reference_sample = loaded_study.sel(time=slice(*climatology_bounds))
    threshold_floor = _threshold_min_value_in_reference_units(
        threshold,
        reference_sample,
    )
    filtered_reference_sample = reference_sample
    if threshold_floor is not None:
        filtered_reference_sample = reference_sample.where(
            reference_sample >= threshold_floor,
            np.nan,
        )
    return BootstrapReferenceSample(
        study=loaded_study,
        climatology_bounds=climatology_bounds,
        reference_sample=reference_sample,
        filtered_reference_sample=filtered_reference_sample,
        threshold_floor_in_reference_units=threshold_floor,
    )


def build_bootstrap_array_inputs(
    reference_sample: BootstrapReferenceSample,
) -> BootstrapArrayInputs:
    """Build flattened arrays consumed by optimized bootstrap kernels."""
    study = reference_sample.study.transpose("time", ...)
    reference_raw = reference_sample.reference_sample.transpose("time", ...)
    reference_filtered = reference_sample.filtered_reference_sample.transpose(
        "time", ...
    )
    return BootstrapArrayInputs(
        flat_study=np.asarray(study.data, dtype=np.float64).reshape(
            study.sizes["time"],
            -1,
        ),
        flat_reference_raw=np.asarray(reference_raw.data, dtype=np.float64).reshape(
            reference_raw.sizes["time"],
            -1,
        ),
        flat_reference_filtered=np.asarray(
            reference_filtered.data,
            dtype=np.float64,
        ).reshape(
            reference_filtered.sizes["time"],
            -1,
        ),
        spatial_shape=study.shape[1:],
    )


def build_bootstrap_temporal_indexing(
    study: DataArray,
    reference_sample: DataArray,
    freq: str,
    *,
    doy_window_width: int,
) -> BootstrapTemporalIndexing:
    """Build year and grouping indexes shared by bootstrap kernels."""
    study_time = study.indexes["time"]
    reference_time = reference_sample.indexes["time"]
    reference_year_indices = indices_by_year(reference_time)
    study_year_indices = indices_by_year(study_time)
    reference_years = np.asarray(list(reference_year_indices), dtype=np.int64)
    output_group_indices = indices_by_resample_group(study, freq)
    output_group_labels = list(output_group_indices)
    output_starts = np.asarray(
        [indices[0] for indices in output_group_indices.values()],
        dtype=np.int64,
    )
    output_lengths = np.asarray(
        [len(indices) for indices in output_group_indices.values()],
        dtype=np.int64,
    )
    source_max_day_of_year = int(reference_time.dayofyear.max())
    study_year_max_day_of_year = {
        year: source_max_day_of_year
        if source_max_day_of_year == LEAP_YEAR_DAY_COUNT
        else int(study_time[indices].dayofyear.max())
        for year, indices in study_year_indices.items()
    }
    output_years = np.asarray(
        [int(study_time[indices[0]].year) for indices in output_group_indices.values()],
        dtype=np.int64,
    )
    bootstrap_years = np.asarray(list(dict.fromkeys(output_years)), dtype=np.int64)
    year_group_starts, year_group_stops = group_bounds_by_year(
        output_years,
        bootstrap_years,
    )
    year_max_day_of_years = np.asarray(
        [study_year_max_day_of_year[year] for year in bootstrap_years],
        dtype=np.int64,
    )
    year_to_reference_index = np.asarray(
        [
            int(np.where(reference_years == year)[0][0])
            if year in reference_year_indices
            else -1
            for year in bootstrap_years
        ],
        dtype=np.int64,
    )
    sample_indices_by_day_of_year = rolling_sample_index_matrix(
        reference_time,
        window=doy_window_width,
    )
    reference_index_year, reference_index_position = ref_index_year_and_position(
        reference_year_indices,
        len(reference_time),
    )
    substitute_alignment = substitute_alignment_matrix(
        reference_time,
        reference_year_indices,
    )
    return BootstrapTemporalIndexing(
        reference_year_indices=reference_year_indices,
        study_year_indices=study_year_indices,
        output_group_indices=output_group_indices,
        output_group_labels=output_group_labels,
        output_starts=output_starts,
        output_lengths=output_lengths,
        output_years=output_years,
        bootstrap_years=bootstrap_years,
        year_group_starts=year_group_starts,
        year_group_stops=year_group_stops,
        year_max_day_of_years=year_max_day_of_years,
        year_to_reference_index=year_to_reference_index,
        study_day_of_years=study_time.dayofyear.to_numpy(dtype=np.int64),
        sample_indices_by_day_of_year=sample_indices_by_day_of_year,
        reference_index_year=reference_index_year,
        reference_index_position=reference_index_position,
        substitute_alignment=substitute_alignment,
    )


def indices_by_year(time: pd.DatetimeIndex) -> dict[int, np.ndarray]:
    return {int(year): np.where(time.year == year)[0] for year in np.unique(time.year)}


def indices_by_resample_group(
    da: DataArray,
    freq: str,
) -> dict[np.datetime64, np.ndarray]:
    groups = da.resample(time=freq).groups
    out: dict[np.datetime64, np.ndarray] = {}
    for label, indexer in groups.items():
        if isinstance(indexer, slice):
            start = 0 if indexer.start is None else indexer.start
            stop = da.sizes["time"] if indexer.stop is None else indexer.stop
            step = 1 if indexer.step is None else indexer.step
            indices = np.arange(start, stop, step, dtype=np.int64)
        else:
            indices = np.asarray(indexer, dtype=np.int64)
        out[np.datetime64(label)] = indices
    return out


def group_bounds_by_year(
    output_years: np.ndarray,
    bootstrap_years: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    starts = np.empty(len(bootstrap_years), dtype=np.int64)
    stops = np.empty(len(bootstrap_years), dtype=np.int64)
    for i, year in enumerate(bootstrap_years):
        group_indices = np.where(output_years == year)[0]
        starts[i] = int(group_indices[0])
        stops[i] = int(group_indices[-1]) + 1
    return starts, stops


def rolling_sample_index_matrix(
    time: pd.DatetimeIndex,
    *,
    window: int,
) -> np.ndarray:
    half_window = window // 2
    sample_indices: dict[int, list[int]] = {doy: [] for doy in range(1, 366)}
    day_of_years = time.dayofyear.to_numpy()
    for center, day_of_year in enumerate(day_of_years):
        if day_of_year == LEAP_YEAR_DAY_COUNT:
            continue
        start = max(0, center - half_window)
        stop = min(len(time), center + half_window + 1)
        sample_indices[int(day_of_year)].extend(range(start, stop))
    max_samples = max(len(indices) for indices in sample_indices.values())
    matrix = np.full((365, max_samples), -1, dtype=np.int64)
    for day_of_year, indices in sample_indices.items():
        matrix[day_of_year - 1, : len(indices)] = indices
    return matrix


def ref_index_year_and_position(
    reference_year_indices: dict[int, np.ndarray],
    n_reference_time: int,
) -> tuple[np.ndarray, np.ndarray]:
    index_year = np.full(n_reference_time, -1, dtype=np.int64)
    index_position = np.full(n_reference_time, -1, dtype=np.int64)
    for year_index, indices in enumerate(reference_year_indices.values()):
        index_year[indices] = year_index
        index_position[indices] = np.arange(len(indices), dtype=np.int64)
    return index_year, index_position


def substitute_alignment_matrix(
    reference_time: pd.DatetimeIndex,
    reference_year_indices: dict[int, np.ndarray],
) -> np.ndarray:
    max_year_length = max(len(indices) for indices in reference_year_indices.values())
    n_years = len(reference_year_indices)
    aligned = np.full((n_years, n_years, max_year_length), -1, dtype=np.int64)
    years = list(reference_year_indices)
    for target_index, target_year in enumerate(years):
        target_indices = reference_year_indices[target_year]
        target_time = reference_time[target_indices]
        for substitute_index, substitute_year in enumerate(years):
            substitute_indices = reference_year_indices[substitute_year]
            aligned[target_index, substitute_index, : len(target_indices)] = (
                substitute_indices_aligned_to_target(
                    target_time,
                    reference_time[substitute_indices],
                    substitute_indices,
                )
            )
    return aligned


def substitute_indices_aligned_to_target(
    target_time: pd.DatetimeIndex,
    substitute_time: pd.DatetimeIndex,
    substitute_indices: np.ndarray,
) -> np.ndarray:
    if len(target_time) == len(substitute_time):
        return substitute_indices
    substitute_by_month_day = {
        (int(month), int(day)): int(index)
        for month, day, index in zip(
            substitute_time.month,
            substitute_time.day,
            substitute_indices,
            strict=True,
        )
    }
    return np.asarray(
        [
            substitute_by_month_day.get((int(month), int(day)), -1)
            for month, day in zip(target_time.month, target_time.day, strict=True)
        ],
        dtype=np.int64,
    )


def _threshold_min_value_in_reference_units(
    threshold: PercentileThreshold,
    reference_sample: DataArray,
) -> float | None:
    if threshold.threshold_min_value is None:
        return None
    from xclim.core.units import convert_units_to  # noqa: PLC0415

    converted = convert_units_to(
        threshold.threshold_min_value,
        reference_sample,
        context="hydro",
    )
    if hasattr(converted, "magnitude"):
        return float(converted.magnitude)
    return float(converted)

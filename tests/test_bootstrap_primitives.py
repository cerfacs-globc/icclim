from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

from icclim._core.generic.bootstrap_primitives import (
    _block_slices,
    _materialize_bootstrap_study,
    _preferred_spatial_block_sizes,
    build_bootstrap_array_inputs,
    build_bootstrap_output,
    build_bootstrap_reference_sample,
    build_bootstrap_temporal_indexing,
    substitute_indices_aligned_to_target,
)
from icclim.threshold.factory import build_threshold
from tests.testing_utils import stub_pr, stub_tas


def test_build_bootstrap_reference_sample_applies_threshold_floor() -> None:
    pr = stub_pr(0.0)
    pr[1:] = 2.0e-5
    threshold = build_threshold("> 90 doy_per", threshold_min_value="1 mm/day")

    reference_sample = build_bootstrap_reference_sample(pr, threshold)

    assert reference_sample.climatology_bounds == ["2042-01-01", "2046-12-31"]
    assert reference_sample.threshold_floor_in_reference_units is not None
    assert np.isnan(reference_sample.filtered_reference_sample.isel(time=0).item())
    assert not np.isnan(reference_sample.filtered_reference_sample.isel(time=1).item())
    xr.testing.assert_identical(
        reference_sample.reference_sample, reference_sample.study
    )


def test_build_bootstrap_temporal_indexing_tracks_years_and_groups() -> None:
    tas = stub_tas()
    threshold = build_threshold("> 90 doy_per")
    reference_sample = build_bootstrap_reference_sample(tas, threshold)

    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        "MS",
        doy_window_width=threshold.doy_window_width,
    )

    np.testing.assert_array_equal(
        temporal_indexing.bootstrap_years,
        np.asarray([2042, 2043, 2044, 2045, 2046]),
    )
    assert len(temporal_indexing.output_group_labels) == 60
    assert int(temporal_indexing.output_lengths.sum()) == tas.sizes["time"]
    np.testing.assert_array_equal(
        temporal_indexing.year_to_reference_index,
        np.asarray([0, 1, 2, 3, 4]),
    )
    assert temporal_indexing.sample_indices_by_day_of_year.shape[0] == 365
    assert temporal_indexing.reference_index_year.shape == (tas.sizes["time"],)
    assert temporal_indexing.reference_index_position.shape == (tas.sizes["time"],)
    assert temporal_indexing.substitute_alignment.shape[:2] == (5, 5)


def test_build_bootstrap_array_inputs_flattens_study_and_reference() -> None:
    tas = stub_tas(lat_length=2, lon_length=3)
    threshold = build_threshold("> 90 doy_per")
    reference_sample = build_bootstrap_reference_sample(tas, threshold)

    array_inputs = build_bootstrap_array_inputs(reference_sample)

    assert array_inputs.flat_study.shape == (tas.sizes["time"], 6)
    assert array_inputs.flat_reference_raw.shape == (tas.sizes["time"], 6)
    assert array_inputs.flat_reference_filtered.shape == (tas.sizes["time"], 6)
    assert array_inputs.spatial_shape == (2, 3)


def test_substitute_indices_aligned_to_target_marks_missing_february_29() -> None:
    target_time = pd.DatetimeIndex(
        ["2044-02-28", "2044-02-29", "2044-03-01"],
    )
    substitute_time = pd.DatetimeIndex(
        ["2043-02-28", "2043-03-01"],
    )
    substitute_indices = np.asarray([10, 11], dtype=np.int64)

    aligned = substitute_indices_aligned_to_target(
        target_time,
        substitute_time,
        substitute_indices,
    )

    np.testing.assert_array_equal(
        aligned,
        np.asarray([10, -1, 11], dtype=np.int64),
    )


def test_build_bootstrap_output_rebuilds_coordinates_and_attrs() -> None:
    tas = stub_tas(lat_length=2, lon_length=1)
    threshold = build_threshold("> 90 doy_per")
    reference_sample = build_bootstrap_reference_sample(tas, threshold)
    temporal_indexing = build_bootstrap_temporal_indexing(
        reference_sample.study,
        reference_sample.reference_sample,
        "YS",
        doy_window_width=threshold.doy_window_width,
    )
    flat_result = np.zeros((len(temporal_indexing.output_group_labels), 2), dtype=float)

    output = build_bootstrap_output(
        flat_result=flat_result,
        reference_sample=reference_sample,
        temporal_indexing=temporal_indexing,
        spatial_shape=(2, 1),
        units="d",
    )

    assert output.dims == ("time", "lat", "lon")
    assert output.shape == (5, 2, 1)
    assert output.attrs["units"] == "d"
    assert output.attrs["climatology_bounds"] == ["2042-01-01", "2046-12-31"]


def test_materialize_bootstrap_study_loads_chunked_spatial_tiles_exactly() -> None:
    tas = stub_tas(lat_length=3, lon_length=5).chunk({"time": 2, "lat": 1, "lon": 2})

    materialized = _materialize_bootstrap_study(tas)

    xr.testing.assert_identical(materialized, tas.transpose("time", ...).load())


def test_block_slices_covers_full_axis() -> None:
    block_slices = _block_slices(size=5, preferred_block_size=2)

    assert block_slices == [slice(0, 2), slice(2, 4), slice(4, 5)]


def test_preferred_spatial_block_sizes_uses_backend_hints() -> None:
    tas = stub_tas(lat_length=3, lon_length=5)
    tas.encoding["preferred_chunks"] = {"lat": 10, "lon": 2}

    block_sizes = _preferred_spatial_block_sizes(tas)

    assert block_sizes == {"lat": 3, "lon": 2}

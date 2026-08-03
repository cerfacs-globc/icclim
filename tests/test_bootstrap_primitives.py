from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim._core.generic.bootstrap import (
    _bootstrap_average_kernel,
    _bootstrap_bounded_average_kernel,
    _bootstrap_bounded_count_kernel,
    _bootstrap_bounded_fraction_kernel,
    _bootstrap_bounded_sum_kernel,
    _bootstrap_count_kernel,
    _bootstrap_fraction_kernel,
    _bootstrap_sum_kernel,
    _bootstrap_union_count_kernel,
    _bootstrap_union_mask_kernel,
    compute_doy_percentile_bootstrap_count,
    compute_doy_percentile_bootstrap_exceedance_average,
    compute_doy_percentile_bootstrap_exceedance_sum,
    compute_doy_percentile_bootstrap_fraction_of_total,
    compute_doy_percentile_bootstrap_union_exceedance_count,
    compute_doy_percentile_bootstrap_union_exceedance_mask,
    compute_doy_percentile_scalar_bounded_bootstrap_count,
    compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average,
    compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum,
    compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total,
)
from icclim._core.generic.bootstrap_primitives import (
    _block_slices,
    _materialize_bootstrap_study,
    _preferred_spatial_block_sizes,
    build_bootstrap_array_inputs,
    build_bootstrap_output,
    build_bootstrap_prepared_inputs,
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


def test_compiled_bootstrap_count_wrappers_match_constant_expectations() -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    expected_count = tas.resample(time="YS").count(dim="time")

    count = compute_doy_percentile_bootstrap_count(tas, threshold, "YS")
    union_count = compute_doy_percentile_bootstrap_union_exceedance_count(
        tas, threshold, "YS"
    )
    union_mask = compute_doy_percentile_bootstrap_union_exceedance_mask(
        tas, threshold, "YS"
    )

    assert count is not None
    assert union_count is not None
    assert union_mask is not None
    xr.testing.assert_allclose(
        count.reset_coords("percentiles", drop=True), expected_count
    )
    xr.testing.assert_allclose(
        union_count.reset_coords("percentiles", drop=True), expected_count
    )
    xr.testing.assert_allclose(
        union_mask.reset_coords("percentiles", drop=True),
        xr.ones_like(tas, dtype=np.float32),
    )


def test_compiled_bootstrap_value_aggregate_wrappers_match_constant_expectations() -> (
    None
):
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    expected_count = tas.resample(time="YS").count(dim="time").astype(np.float32)
    expected_sum = (expected_count * np.float32(300.0)).astype(tas.dtype)
    expected_average = xr.full_like(expected_sum, 300.0)
    expected_fraction = xr.full_like(expected_sum, 1.0)

    summed = compute_doy_percentile_bootstrap_exceedance_sum(tas, threshold, "YS")
    averaged = compute_doy_percentile_bootstrap_exceedance_average(tas, threshold, "YS")
    fraction = compute_doy_percentile_bootstrap_fraction_of_total(tas, threshold, "YS")

    assert summed is not None
    assert averaged is not None
    assert fraction is not None
    xr.testing.assert_allclose(
        summed.reset_coords("percentiles", drop=True),
        expected_sum,
    )
    xr.testing.assert_allclose(
        averaged.reset_coords("percentiles", drop=True),
        expected_average,
    )
    xr.testing.assert_allclose(
        fraction.reset_coords("percentiles", drop=True),
        expected_fraction,
    )


def test_compiled_scalar_bounded_wrappers_match_constant_expectations() -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    expected_count = tas.resample(time="YS").count(dim="time")
    expected_sum = (expected_count * 300.0).astype(tas.dtype)
    expected_average = xr.full_like(expected_sum, 300.0)
    expected_fraction = xr.full_like(expected_sum, 1.0)

    count = compute_doy_percentile_scalar_bounded_bootstrap_count(
        tas,
        threshold,
        "YS",
        303.15,
        3,
        0,
    )
    summed = compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum(
        tas,
        threshold,
        "YS",
        303.15,
        3,
        0,
    )
    averaged = compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average(
        tas,
        threshold,
        "YS",
        303.15,
        3,
        0,
    )
    fraction = compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total(
        tas,
        threshold,
        "YS",
        303.15,
        3,
        0,
    )

    assert count is not None
    assert summed is not None
    assert averaged is not None
    assert fraction is not None
    xr.testing.assert_allclose(
        count.reset_coords("percentiles", drop=True), expected_count
    )
    xr.testing.assert_allclose(
        summed.reset_coords("percentiles", drop=True), expected_sum
    )
    xr.testing.assert_allclose(
        averaged.reset_coords("percentiles", drop=True),
        expected_average,
    )
    xr.testing.assert_allclose(
        fraction.reset_coords("percentiles", drop=True),
        expected_fraction,
    )


def test_compiled_bootstrap_returns_none_when_not_optimized() -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")

    assert compute_doy_percentile_bootstrap_count(tas, threshold, "D") is None


def _kernel_common_args(
    tas: xr.DataArray,
    threshold,
) -> tuple[tuple, xr.DataArray]:
    prepared = build_bootstrap_prepared_inputs(tas, threshold, "YS", dtype=np.float32)
    ref = prepared.reference_sample
    idx = prepared.temporal_indexing
    arr = prepared.array_inputs
    min_threshold = (
        np.nan
        if ref.threshold_floor_in_reference_units is None
        else float(ref.threshold_floor_in_reference_units)
    )
    args = (
        arr.flat_reference_raw,
        arr.flat_reference_filtered,
        arr.flat_study,
        idx.sample_indices_by_day_of_year,
        idx.reference_index_year,
        idx.reference_index_position,
        idx.substitute_alignment,
        idx.output_starts,
        idx.output_lengths,
        idx.year_group_starts,
        idx.year_group_stops,
        idx.year_max_day_of_years,
        idx.year_to_reference_index,
        idx.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        1,
        min_threshold,
    )
    return args, ref.study


@pytest.mark.parametrize(
    ("kernel", "wrapper"),
    [
        (_bootstrap_count_kernel, compute_doy_percentile_bootstrap_count),
        (_bootstrap_sum_kernel, compute_doy_percentile_bootstrap_exceedance_sum),
        (
            _bootstrap_union_count_kernel,
            compute_doy_percentile_bootstrap_union_exceedance_count,
        ),
        (
            _bootstrap_average_kernel,
            compute_doy_percentile_bootstrap_exceedance_average,
        ),
        (
            _bootstrap_fraction_kernel,
            compute_doy_percentile_bootstrap_fraction_of_total,
        ),
    ],
)
def test_numba_python_kernels_match_wrapper_outputs(kernel, wrapper) -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    args, _study = _kernel_common_args(tas, threshold)

    kernel_result = kernel.py_func(*args)
    wrapper_result = wrapper(tas, threshold, "YS")

    assert wrapper_result is not None
    expected = wrapper_result.values.reshape(kernel_result.shape)
    np.testing.assert_allclose(kernel_result, expected)


def test_numba_python_union_mask_kernel_matches_wrapper_output() -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    prepared = build_bootstrap_prepared_inputs(tas, threshold, "YS", dtype=np.float32)
    ref = prepared.reference_sample
    idx = prepared.temporal_indexing
    arr = prepared.array_inputs
    min_threshold = (
        np.nan
        if ref.threshold_floor_in_reference_units is None
        else float(ref.threshold_floor_in_reference_units)
    )

    kernel_result = _bootstrap_union_mask_kernel.py_func(
        arr.flat_reference_raw,
        arr.flat_reference_filtered,
        arr.flat_study,
        idx.sample_indices_by_day_of_year,
        idx.reference_index_year,
        idx.reference_index_position,
        idx.substitute_alignment,
        idx.study_year_starts,
        idx.study_year_lengths,
        idx.year_max_day_of_years,
        idx.year_to_reference_index,
        idx.study_day_of_years,
        float(threshold.percentile_coord().item()) / 100.0,
        float(threshold.interpolation.alpha),
        float(threshold.interpolation.beta),
        1,
        min_threshold,
    )
    wrapper_result = compute_doy_percentile_bootstrap_union_exceedance_mask(
        tas,
        threshold,
        "YS",
        prepared_inputs=prepared,
    )

    assert wrapper_result is not None
    np.testing.assert_allclose(
        kernel_result,
        wrapper_result.values.reshape(kernel_result.shape),
    )


@pytest.mark.parametrize(
    ("kernel", "wrapper"),
    [
        (
            _bootstrap_bounded_count_kernel,
            compute_doy_percentile_scalar_bounded_bootstrap_count,
        ),
        (
            _bootstrap_bounded_sum_kernel,
            compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum,
        ),
        (
            _bootstrap_bounded_average_kernel,
            compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average,
        ),
        (
            _bootstrap_bounded_fraction_kernel,
            compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total,
        ),
    ],
)
def test_numba_python_bounded_kernels_match_wrapper_outputs(kernel, wrapper) -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    args, _study = _kernel_common_args(tas, threshold)
    bounded_args = (*args, np.float32(303.15), 3, 0)

    kernel_result = kernel.py_func(*bounded_args)
    wrapper_result = wrapper(tas, threshold, "YS", 303.15, 3, 0)

    assert wrapper_result is not None
    expected = wrapper_result.values.reshape(kernel_result.shape)
    np.testing.assert_allclose(kernel_result, expected)

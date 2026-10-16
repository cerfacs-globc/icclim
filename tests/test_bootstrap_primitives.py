from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import cftime
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xarray.coding.cftimeindex import CFTimeIndex

import icclim
from icclim._core.generic import bootstrap as bootstrap_module
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
    _build_nominal_full_thresholds,
    compute_doy_percentile_bootstrap_count,
    compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype,
    compute_doy_percentile_bootstrap_count_threshold_bank_prototype,
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

if TYPE_CHECKING:
    from pathlib import Path


@contextmanager
def _force_compiled_cftime_count():
    original = bootstrap_module.is_optimized_doy_percentile_count_supported
    bootstrap_module.is_optimized_doy_percentile_count_supported = lambda *_: True
    try:
        yield
    finally:
        bootstrap_module.is_optimized_doy_percentile_count_supported = original


def _build_cftime_overlap_case(case_name: str) -> xr.DataArray:
    time = xr.date_range(
        "2042-01-01",
        periods=365 * 5 + 1,
        freq="D",
        use_cftime=True,
    )
    tas = xr.DataArray(
        np.full((len(time), 1, 1), 300.0, dtype=np.float64),
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": [0.0], "lon": [0.0]},
        attrs={"units": "K"},
        name="tas",
    )
    if case_name == "constant":
        return tas.chunk({"time": 365, "lat": 1, "lon": 1})
    if case_name == "leap_day_cold_spike":
        for timestamp in (
            cftime.DatetimeGregorian(2044, 2, 28),
            cftime.DatetimeGregorian(2044, 2, 29),
            cftime.DatetimeGregorian(2044, 3, 1),
        ):
            tas.loc[{"time": timestamp}] = 250.0
        return tas.chunk({"time": 365, "lat": 1, "lon": 1})
    if case_name == "reference_overlap_shift":

        def _timestamp(year: int, month: int, day: int) -> object:
            return time[
                (time.year == year) & (time.month == month) & (time.day == day)
            ][0]

        tas.loc[{"time": _timestamp(2042, 2, 28)}] = 305.0
        tas.loc[{"time": _timestamp(2043, 2, 28)}] = 295.0
        tas.loc[{"time": _timestamp(2044, 2, 29)}] = 285.0
        tas.loc[{"time": _timestamp(2045, 2, 28)}] = 310.0
        tas.loc[{"time": _timestamp(2045, 3, 1)}] = 280.0
        return tas.chunk({"time": 365, "lat": 1, "lon": 1})
    msg = f"Unsupported case: {case_name}"
    raise ValueError(msg)


def _build_cftime_filtered_overlap_case() -> xr.DataArray:
    time = xr.date_range(
        "2042-01-01",
        periods=365 * 5 + 1,
        freq="D",
        use_cftime=True,
    )
    day = np.arange(len(time))
    values = 0.35 * (day % 19)
    values[day % 3 == 0] = 0.0
    pr = xr.DataArray(
        values[:, np.newaxis, np.newaxis],
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": [0.0], "lon": [0.0]},
        attrs={"units": "mm/day"},
        name="pr",
    )
    return pr.chunk({"time": 365, "lat": 1, "lon": 1})


def _build_non_gregorian_overlap_case(calendar: str) -> xr.DataArray:
    days_per_year = (
        360
        if calendar == "360_day"
        else 366
        if calendar
        in {
            "366_day",
            "all_leap",
        }
        else 365
    )
    time = xr.date_range(
        "2042-01-01",
        periods=days_per_year * 5,
        freq="D",
        calendar=calendar,
        use_cftime=True,
    )
    values = np.full((len(time), 1, 1), 300.0, dtype=np.float32)
    values[100] = 350.0
    values[days_per_year + 100] = 250.0
    return xr.DataArray(
        values,
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": [0.0], "lon": [0.0]},
        attrs={"units": "K"},
        name="tas",
    ).chunk({"time": days_per_year, "lat": 1, "lon": 1})


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


def test_build_bootstrap_temporal_indexing_supports_cftime_groups() -> None:
    tas = stub_tas(use_cftime=True)
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


def test_file_reopen_preserves_cftime_coordinates(tmp_path) -> None:
    source = stub_tas(lat_length=2, lon_length=2)
    source_path = tmp_path / "tas.nc"
    source.to_netcdf(source_path)
    file_backed = xr.open_dataarray(source_path, chunks={"time": 2})
    cftime_study = file_backed.assign_coords(
        time=[
            cftime.DatetimeGregorian(
                timestamp.year,
                timestamp.month,
                timestamp.day,
            )
            for timestamp in file_backed.indexes["time"]
        ]
    ).isel(time=slice(1, -1))

    materialized = _materialize_bootstrap_study(
        cftime_study,
        prefer_file_reopen=True,
    )

    assert isinstance(materialized.indexes["time"], CFTimeIndex)
    xr.testing.assert_equal(materialized, cftime_study.load())


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


def test_compiled_bootstrap_supports_groups_crossing_calendar_years() -> None:
    tas = stub_tas(300.0).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")

    result = compute_doy_percentile_bootstrap_count(tas, threshold, "W-MON")

    assert result is None
    union_count = compute_doy_percentile_bootstrap_union_exceedance_count(
        tas,
        threshold,
        "W-MON",
    )
    assert union_count is not None
    xr.testing.assert_allclose(
        union_count.reset_coords("percentiles", drop=True),
        tas.resample(time="W-MON").count(),
    )


def test_cross_year_union_count_matches_reference_daily_mask() -> None:
    rng = np.random.default_rng(4)
    tas = stub_tas(300.0)
    tas.data[:, 0, 0] = rng.normal(300.0, 8.0, tas.sizes["time"])
    threshold_kwargs = {
        "query": "> 90 doy_per",
        "doy_window_width": 5,
        "reference_period": ("2042-01-01", "2043-12-31"),
    }
    reference_mask = build_threshold(**threshold_kwargs).compute(
        tas,
        freq="W-MON",
        bootstrap=True,
    )
    expected = (
        reference_mask.fillna(False)
        .astype(bool)
        .resample(time="W-MON")
        .sum(dim="time")
        .squeeze("percentiles", drop=True)
    )

    result = compute_doy_percentile_bootstrap_union_exceedance_count(
        tas.chunk({"time": 365, "lat": 1, "lon": 1}),
        build_threshold(**threshold_kwargs),
        "W-MON",
    )

    assert result is not None
    xr.testing.assert_equal(
        result.reset_coords("percentiles", drop=True),
        expected,
    )


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
        isinstance(ref.study.indexes["time"], CFTimeIndex),
        min_threshold,
    )
    return args, ref.study


def _count_kernel_args(tas: xr.DataArray, threshold) -> tuple[tuple, xr.DataArray]:
    args, study = _kernel_common_args(tas, threshold)
    nominal_thresholds = _build_nominal_full_thresholds(study, threshold)
    count_args = (args[0], args[1], args[2], nominal_thresholds, *args[3:])
    return count_args, study


def _daily_kernel_args(tas: xr.DataArray, threshold) -> tuple[tuple, xr.DataArray]:
    args, study = _kernel_common_args(tas, threshold)
    nominal_thresholds = _build_nominal_full_thresholds(
        study,
        threshold,
        args[-1],
    )
    return (args[0], args[1], args[2], nominal_thresholds, *args[3:]), study


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
    if kernel is _bootstrap_count_kernel:
        args, _study = _count_kernel_args(tas, threshold)
    else:
        args, _study = _daily_kernel_args(tas, threshold)

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
    nominal_thresholds = _build_nominal_full_thresholds(
        ref.study,
        threshold,
        min_threshold,
    )

    kernel_result = _bootstrap_union_mask_kernel.py_func(
        arr.flat_reference_raw,
        arr.flat_reference_filtered,
        arr.flat_study,
        nominal_thresholds,
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
        False,
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


def test_numba_python_count_kernel_matches_constant_cftime_monthly_counts() -> None:
    tas = stub_tas(300.0, use_cftime=True).chunk({"time": 365, "lat": 1, "lon": 1})
    threshold = build_threshold(">= 90 doy_per")
    prepared = build_bootstrap_prepared_inputs(tas, threshold, "MS", dtype=np.float64)
    ref = prepared.reference_sample
    idx = prepared.temporal_indexing
    arr = prepared.array_inputs
    min_threshold = (
        np.nan
        if ref.threshold_floor_in_reference_units is None
        else float(ref.threshold_floor_in_reference_units)
    )

    kernel_result = _bootstrap_count_kernel.py_func(
        arr.flat_reference_raw,
        arr.flat_reference_filtered,
        arr.flat_study,
        np.empty((0, 0), dtype=np.float64),
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
        True,
        min_threshold,
    )

    expected = (
        tas.resample(time="MS").count(dim="time").values.reshape(kernel_result.shape)
    )
    np.testing.assert_allclose(kernel_result, expected)


@pytest.mark.parametrize("indicator_name", ["sum", "average", "fraction_of_total"])
@pytest.mark.parametrize("case_name", ["constant", "leap_day_cold_spike"])
@pytest.mark.parametrize("slice_mode", ["month", "year"])
def test_cftime_value_aggregate_matches_reference_on_overlap_cases(
    indicator_name: str,
    case_name: str,
    slice_mode: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_cftime_overlap_case(case_name).rename("tas")
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            "> 90 doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2044-12-31"),
        ),
        "time_range": ("2042-01-01", "2046-12-31"),
        "slice_mode": slice_mode,
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "safe")
    exact_tiled = api(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized[indicator_name],
        reference[indicator_name],
    )
    xr.testing.assert_allclose(
        exact_tiled[indicator_name],
        reference[indicator_name],
    )


@pytest.mark.parametrize("slice_mode", ["month", "year"])
def test_cftime_spell_paths_match_reference_on_overlap_case(
    slice_mode: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    time = xr.date_range(
        "2042-01-01",
        periods=365 * 5 + 1,
        freq="D",
        use_cftime=True,
    )
    tas = xr.DataArray(
        np.full((len(time), 1, 1), 300.0, dtype=np.float64),
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": [0.0], "lon": [0.0]},
        attrs={"units": "K"},
        name="tas",
    )
    tas.loc[{"time": slice("2042-01-01", "2042-12-31")}] = 299.0
    tas.loc[{"time": slice("2043-01-01", "2043-12-31")}] = 303.0
    for year in (2042, 2043):
        start = cftime.DatetimeGregorian(year, 7, 10)
        stop = cftime.DatetimeGregorian(year, 7, 16)
        tas.loc[{"time": slice(start, stop)}] = 301.0
    source_path = tmp_path / "tas.nc"
    tas.assign_coords(
        time=pd.date_range("2042-01-01", periods=len(time), freq="D")
    ).to_netcdf(source_path)
    tas = xr.open_dataarray(
        source_path,
        chunks={"time": 365, "lat": 1, "lon": 1},
    ).assign_coords(time=time)

    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            "> 90 doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2043-12-31"),
        ),
        "time_range": ("2042-01-01", "2046-12-31"),
        "slice_mode": slice_mode,
        "min_spell_length": 6,
    }

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = icclim.sum_of_spell_lengths(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = icclim.sum_of_spell_lengths(**common_kwargs).compute()
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "safe")
    exact_tiled = icclim.sum_of_spell_lengths(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized.sum_of_spell_lengths,
        reference.sum_of_spell_lengths,
    )
    xr.testing.assert_allclose(
        exact_tiled.sum_of_spell_lengths,
        reference.sum_of_spell_lengths,
    )


def test_filtered_pandas_spell_matches_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pr = _build_cftime_filtered_overlap_case().assign_coords(
        time=pd.date_range("2042-01-01", periods=365 * 5 + 1, freq="D")
    )
    common_kwargs = {
        "in_files": pr,
        "var_name": "pr",
        "threshold": build_threshold(
            "> 90 doy_per",
            threshold_min_value="1 mm/day",
            doy_window_width=1,
            reference_period=("2042-01-01", "2043-12-31"),
        ),
        "slice_mode": "year",
        "min_spell_length": 3,
    }

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = icclim.sum_of_spell_lengths(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = icclim.sum_of_spell_lengths(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized.sum_of_spell_lengths,
        reference.sum_of_spell_lengths,
    )


@pytest.mark.parametrize(
    "indicator_name",
    ["sum", "count_occurrences", "average", "fraction_of_total"],
)
@pytest.mark.parametrize("slice_mode", ["month", "year"])
def test_cftime_filtered_value_aggregate_matches_reference(
    indicator_name: str,
    slice_mode: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pr = _build_cftime_filtered_overlap_case()
    common_kwargs = {
        "in_files": pr,
        "var_name": "pr",
        "threshold": build_threshold(
            "> 90 doy_per",
            threshold_min_value="1 mm/day",
            doy_window_width=1,
            reference_period=("2042-01-01", "2043-12-31"),
        ),
        "time_range": ("2042-01-01", "2046-12-31"),
        "slice_mode": slice_mode,
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized[indicator_name],
        reference[indicator_name],
    )


@pytest.mark.parametrize("indicator_name", ["excess", "deficit"])
@pytest.mark.parametrize("slice_mode", ["month", "year"])
def test_cftime_numeric_threshold_aggregate_matches_reference(
    monkeypatch,
    indicator_name: str,
    slice_mode: str,
) -> None:
    tas = _build_cftime_overlap_case("reference_overlap_shift").rename("tas")
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            "90 doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2044-12-31"),
        ),
        "slice_mode": slice_mode,
    }

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = getattr(icclim, indicator_name)(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = getattr(icclim, indicator_name)(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized[indicator_name],
        reference[indicator_name],
    )


@pytest.mark.parametrize(
    "calendar",
    ["360_day", "365_day", "noleap", "366_day", "all_leap"],
)
@pytest.mark.parametrize(
    "indicator_name",
    ["count_occurrences", "average", "fraction_of_total"],
)
def test_non_gregorian_bootstrap_matches_reference(
    calendar: str,
    indicator_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_non_gregorian_overlap_case(calendar)
    reference_end = "2043-12-30" if calendar == "360_day" else "2043-12-31"
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            "> 90 doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", reference_end),
        ),
        "slice_mode": "year",
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()

    xr.testing.assert_allclose(optimized[indicator_name], reference[indicator_name])


def test_daily_bootstrap_output_matches_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_cftime_overlap_case("reference_overlap_shift")
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            "> 90 doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2044-12-31"),
        ),
        "slice_mode": "day",
    }

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = icclim.count_occurrences(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = icclim.count_occurrences(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized.count_occurrences,
        reference.count_occurrences,
    )


@pytest.mark.parametrize(
    "indicator_name",
    ["count_occurrences", "average", "sum", "fraction_of_total", "excess", "deficit"],
)
def test_multiple_percentile_bootstrap_matches_reference(
    indicator_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_cftime_overlap_case("reference_overlap_shift")
    threshold_kwargs = {
        "value": [10, 90],
        "operator": "reach" if indicator_name in {"excess", "deficit"} else ">",
        "unit": "doy_per",
        "doy_window_width": 1,
        "reference_period": ("2042-01-01", "2044-12-31"),
    }
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(**threshold_kwargs),
        "slice_mode": "year",
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()

    assert optimized[indicator_name].dims == reference[indicator_name].dims
    xr.testing.assert_allclose(optimized[indicator_name], reference[indicator_name])


@pytest.mark.parametrize(
    "indicator_name",
    [
        "maximum",
        "minimum",
        "standard_deviation",
        "max_of_rolling_sum",
        "min_of_rolling_sum",
        "max_of_rolling_average",
        "min_of_rolling_average",
    ],
)
def test_mask_consumer_bootstrap_matches_reference(
    indicator_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_cftime_overlap_case("reference_overlap_shift")
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            ">= 50 doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2044-12-31"),
        ),
        "slice_mode": "year",
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()

    xr.testing.assert_allclose(optimized[indicator_name], reference[indicator_name])


@pytest.mark.parametrize("percentiles", [[90], [10, 90]])
def test_date_event_bootstrap_matches_reference(
    percentiles: list[int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_cftime_overlap_case("reference_overlap_shift")
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            value=percentiles,
            operator=">",
            unit="doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2044-12-31"),
        ),
        "slice_mode": "year",
        "date_event": True,
    }

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = icclim.count_occurrences(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = icclim.count_occurrences(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized.count_occurrences,
        reference.count_occurrences,
    )


@pytest.mark.parametrize(
    "indicator_name",
    ["count_occurrences", "average", "sum", "fraction_of_total"],
)
def test_filtered_bounded_bootstrap_matches_reference(
    indicator_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pr = _build_cftime_filtered_overlap_case()
    common_kwargs = {
        "in_files": pr,
        "var_name": "pr",
        "threshold": build_threshold(
            thresholds=["> 90 doy_per", "<= 5 mm/day"],
            logical_link="and",
            threshold_min_value="1 mm/day",
            doy_window_width=1,
            reference_period=("2042-01-01", "2043-12-31"),
        ),
        "slice_mode": "year",
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()

    xr.testing.assert_allclose(optimized[indicator_name], reference[indicator_name])


@pytest.mark.parametrize(
    "indicator_name",
    ["count_occurrences", "average", "sum", "fraction_of_total"],
)
def test_multiple_percentile_bounded_bootstrap_matches_reference(
    indicator_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pr = _build_cftime_filtered_overlap_case()
    percentile = build_threshold(
        value=[10, 90],
        operator=">",
        unit="doy_per",
        threshold_min_value="1 mm/day",
        doy_window_width=1,
        reference_period=("2042-01-01", "2043-12-31"),
    )
    common_kwargs = {
        "in_files": pr,
        "var_name": "pr",
        "threshold": build_threshold(
            thresholds=[percentile, "<= 5 mm/day"],
            logical_link="and",
        ),
        "slice_mode": "year",
    }

    api = getattr(icclim, indicator_name)
    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = api(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = api(**common_kwargs).compute()

    xr.testing.assert_allclose(optimized[indicator_name], reference[indicator_name])


def test_multiple_percentile_pandas_spell_matches_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = _build_cftime_overlap_case("reference_overlap_shift").assign_coords(
        time=pd.date_range("2042-01-01", periods=365 * 5 + 1, freq="D")
    )
    common_kwargs = {
        "in_files": tas,
        "var_name": "tas",
        "threshold": build_threshold(
            value=[10, 90],
            operator=">",
            unit="doy_per",
            doy_window_width=1,
            reference_period=("2042-01-01", "2044-12-31"),
        ),
        "slice_mode": "year",
        "min_spell_length": 3,
    }

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", "default")
    reference = icclim.sum_of_spell_lengths(**common_kwargs).compute()
    monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE")
    optimized = icclim.sum_of_spell_lengths(**common_kwargs).compute()

    xr.testing.assert_allclose(
        optimized.sum_of_spell_lengths,
        reference.sum_of_spell_lengths,
    )


def test_count_kernel_uses_full_nominal_thresholds_for_leap_non_reference_year() -> (
    None
):
    kernel_result = _bootstrap_count_kernel.py_func(
        np.zeros((1, 1), dtype=np.float64),
        np.zeros((1, 1), dtype=np.float64),
        np.asarray([[0.5]], dtype=np.float64),
        np.vstack(
            [
                np.full((336, 1), 0.0, dtype=np.float64),
                np.asarray([[0.5]], dtype=np.float64),
                np.full((29, 1), 0.0, dtype=np.float64),
            ]
        ),
        np.full((365, 1), -1, dtype=np.int64),
        np.zeros(1, dtype=np.int64),
        np.zeros(1, dtype=np.int64),
        np.zeros((1, 1, 1), dtype=np.int64),
        np.asarray([0], dtype=np.int64),
        np.asarray([1], dtype=np.int64),
        np.asarray([0], dtype=np.int64),
        np.asarray([1], dtype=np.int64),
        np.asarray([366], dtype=np.int64),
        np.asarray([-1], dtype=np.int64),
        np.asarray([337], dtype=np.int64),
        0.9,
        1.0 / 3.0,
        1.0 / 3.0,
        0,
        False,
        np.nan,
    )

    np.testing.assert_allclose(kernel_result, np.asarray([[0.0]]))


@pytest.mark.parametrize(
    "case_name",
    ["constant", "leap_day_cold_spike", "reference_overlap_shift"],
)
@pytest.mark.parametrize("freq", ["MS", "YS"])
def test_threshold_bank_prototype_matches_forced_compiled_cftime_counts(
    case_name: str,
    freq: str,
) -> None:
    tas = _build_cftime_overlap_case(case_name)
    threshold = build_threshold(
        "> 90 doy_per",
        doy_window_width=1,
        reference_period=("2042-01-01", "2044-12-31"),
    )

    with _force_compiled_cftime_count():
        current = compute_doy_percentile_bootstrap_count(tas, threshold, freq)
    prototype = compute_doy_percentile_bootstrap_count_threshold_bank_prototype(
        tas,
        threshold,
        freq,
    )

    assert current is not None
    assert prototype is not None
    xr.testing.assert_allclose(current, prototype)


@pytest.mark.parametrize(
    "case_name",
    ["constant", "leap_day_cold_spike", "reference_overlap_shift"],
)
@pytest.mark.parametrize("freq", ["MS", "YS"])
def test_compiled_threshold_bank_prototype_matches_forced_compiled_cftime_counts(
    case_name: str,
    freq: str,
) -> None:
    tas = _build_cftime_overlap_case(case_name)
    threshold = build_threshold(
        "> 90 doy_per",
        doy_window_width=1,
        reference_period=("2042-01-01", "2044-12-31"),
    )

    with _force_compiled_cftime_count():
        current = compute_doy_percentile_bootstrap_count(tas, threshold, freq)
    prototype = (
        compute_doy_percentile_bootstrap_count_threshold_bank_compiled_prototype(
            tas,
            threshold,
            freq,
        )
    )

    assert current is not None
    assert prototype is not None
    xr.testing.assert_allclose(current, prototype)


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
    bounded_args = (*args[:-2], args[-1], np.float32(303.15), 3, 0)

    kernel_result = kernel.py_func(*bounded_args)
    wrapper_result = wrapper(tas, threshold, "YS", 303.15, 3, 0)

    assert wrapper_result is not None
    expected = wrapper_result.values.reshape(kernel_result.shape)
    np.testing.assert_allclose(kernel_result, expected)

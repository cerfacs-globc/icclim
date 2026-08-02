import numpy as np
import pytest
import xarray as xr

from icclim._core.climate_variable import ClimateVariable
from icclim._core.constants import GROUP_BY_METHOD
from icclim._core.generic import bootstrap_primitives
from icclim._core.generic.functions import (
    _compute_threshold_exceedance_mask,
    _safe_to_agg_units,
    average,
    count_occurrences,
    generic_sum,
    max_consecutive_occurrence,
    maximum,
    minimum,
    percentile,
)
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.frequency import FrequencyRegistry
from icclim.generic.registry import GenericIndicatorRegistry
from icclim.threshold.factory import build_threshold
from tests.testing_utils import stub_tas


def _make_clim_var(tas_val=42, thresh="> 20 degC") -> ClimateVariable:
    tas = stub_tas(tas_val)
    return ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=tas,
        threshold=build_threshold(thresh) if thresh else None,
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )


def test_percentile() -> None:
    tas = stub_tas(42)
    tas[0:10] = -5
    study = ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=tas,
        threshold=build_threshold("> 2 period_per"),
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )
    result = percentile(
        climate_vars=[study],
        to_percent=False,
        sampling_method=GROUP_BY_METHOD,
        resample_freq=FrequencyRegistry.MONTH,
        is_compared_to_reference=False,
    )
    assert result[0] == -5


def test_missing_mask_supports_latest_xclim_constructor_style() -> None:
    class NewStyleMissing:
        def __init__(self, da, freq=None, src_timestep=None, **indexer):
            self.da = da
            self.freq = freq
            self.src_timestep = src_timestep
            self.indexer = indexer

        def __call__(self):
            return xr.zeros_like(self.da, dtype=bool)

    tas = stub_tas()
    mask = GenericIndicatorRegistry.CountOccurrences._compute_missing_mask(
        NewStyleMissing,
        tas,
        "YS-JUN",
        "D",
        {"month": [6, 7, 8]},
    )
    assert not bool(mask.any())


def test_average() -> None:
    study = _make_clim_var(25.0, None)
    result = average(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
    )
    assert result[0] == 25.0


def test_maximum() -> None:
    study = _make_clim_var(30.0, None)
    result = maximum(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        date_event=False,
    )
    assert result[0] == 30.0


def test_minimum() -> None:
    study = _make_clim_var(-10.0, None)
    result = minimum(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        date_event=False,
    )
    assert result[0] == -10.0


def test_count_occurrences() -> None:
    # 300 K is > 20 degC (293.15 K), so it occurs every day
    study = _make_clim_var(300.0, "> 20 degC")
    result = count_occurrences(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        logical_link=LogicalLinkRegistry.LOGICAL_AND,
        date_event=False,
        to_percent=False,
    )
    # the first year has 365 days
    assert int(result.isel(time=0).values) == 365


def test_logical_link_and_normalizes_chunked_numeric_masks() -> None:
    left = xr.DataArray(
        [[[1.0], [0.0]], [[1.0], [np.nan]]],
        dims=["time", "lat", "lon"],
        coords={"time": [0, 1], "lat": [0, 1], "lon": [0]},
    ).chunk({"time": 1, "lat": 1, "lon": 1})
    right = xr.DataArray(
        [[[1.0], [1.0]], [[0.0], [1.0]]],
        dims=["time", "lat", "lon"],
        coords={"time": [0, 1], "lat": [0, 1], "lon": [0]},
    ).chunk({"time": 1, "lat": 1, "lon": 1})

    result = LogicalLinkRegistry.LOGICAL_AND.compute([left, right]).load()

    expected = xr.DataArray(
        [[[True], [False]], [[False], [False]]],
        dims=["time", "lat", "lon"],
        coords={"time": [0, 1], "lat": [0, 1], "lon": [0]},
    )
    xr.testing.assert_equal(result, expected)


def test_generic_sum() -> None:
    study = _make_clim_var(2.0, None)
    result = generic_sum(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
    )
    # 2.0 * len(YEAR) -> > 700 usually (365 or 366 days)
    assert float(result[0].mean().values) > 700


def test_max_consecutive_occurrence() -> None:
    # 300 K is > 20 degC, so consecutive exceedances equal the year length
    study = _make_clim_var(300.0, "> 20 degC")
    result = max_consecutive_occurrence(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        logical_link=LogicalLinkRegistry.LOGICAL_AND,
        date_event=False,
        source_freq_delta="1D",
    )
    assert int(result.isel(time=0).values) >= 365


def test_safe_to_agg_units_drops_unsupported_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: dict[str, object] = {}

    def fake_to_agg_units(
        out,
        orig,
        op,
        dim="time",
    ):
        received["out"] = out
        received["orig"] = orig
        received["op"] = op
        received["dim"] = dim
        return out

    monkeypatch.setattr("xclim.core.units.to_agg_units", fake_to_agg_units)
    da = stub_tas()

    result = _safe_to_agg_units(da, da, "count", dim="time", deffreq="YS")

    assert result is da
    assert received == {
        "out": da,
        "orig": da,
        "op": "count",
        "dim": "time",
    }


def test_compound_percentile_threshold_reuses_prepared_bootstrap_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tas = stub_tas(27.0, lat_length=2, lon_length=2).chunk(
        {"time": 365, "lat": 1, "lon": 1}
    )
    threshold = build_threshold(
        thresholds=["> 95 doy_per", "<= 10 doy_per"],
        logical_link="or",
        reference_period=("2042-01-01", "2043-12-31"),
    )
    climate_var = ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=tas,
        threshold=threshold,
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )
    build_calls = {"count": 0}

    original_builder = bootstrap_primitives.build_bootstrap_prepared_inputs

    def counted_builder(*args, **kwargs):
        build_calls["count"] += 1
        return original_builder(*args, **kwargs)

    monkeypatch.setenv("ICCLIM_BOOTSTRAP_FAST_TILE_CELLS", "1")
    monkeypatch.setattr(
        bootstrap_primitives,
        "build_bootstrap_prepared_inputs",
        counted_builder,
    )

    mask = _compute_threshold_exceedance_mask(
        climate_var=climate_var,
        threshold=threshold,
        resample_freq=FrequencyRegistry.YEAR,
        prepared_inputs_cache={},
    )

    assert mask is not None
    assert build_calls["count"] == 4

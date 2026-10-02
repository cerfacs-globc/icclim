import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.model.index_config import (
    CompletenessPolicy,
    resolve_completeness_policy,
    resolve_legacy_completeness_policy,
)
from icclim.frequency import FrequencyRegistry
from icclim.generic.registry import GenericIndicatorRegistry


def test_strict_policy_has_stable_provenance() -> None:
    policy = resolve_legacy_completeness_policy(
        allow_missing_periods=False,
        missing_method="any",
        missing_options=None,
    )

    assert policy.name == "strict"
    assert policy.method == "any"
    assert policy.options == {}
    assert policy.metadata() == {
        "completeness_policy": "strict",
        "completeness_method": "xclim:any",
        "completeness_options": "{}",
    }


def test_none_policy_disables_masking() -> None:
    policy = resolve_legacy_completeness_policy(
        allow_missing_periods=True,
        missing_method="any",
        missing_options=None,
    )

    assert not policy.is_applied
    assert policy.metadata()["completeness_policy"] == "none"
    assert policy.metadata()["completeness_method"] == "not_applied"


def test_named_method_and_options_are_preserved_for_future_profiles() -> None:
    options = {"n": 350}

    policy = resolve_legacy_completeness_policy(
        allow_missing_periods=False,
        missing_method="at_least_n",
        missing_options=options,
    )
    options["n"] = 1

    assert policy.name == "at_least_n"
    assert policy.method == "at_least_n"
    assert policy.options == {"n": 350}
    assert policy.metadata()["completeness_options"] == '{"n": 350}'


def test_policy_reference_and_version_are_available_for_fair_provenance() -> None:
    policy = CompletenessPolicy(
        name="ecad",
        method="at_least_n",
        options={"n": 350},
        reference="ECA&D ATBD section 5.1",
        version="2023",
    )

    assert policy.metadata()["completeness_reference"] == "ECA&D ATBD section 5.1"
    assert policy.metadata()["completeness_policy_version"] == "2023"


def test_default_ecad_policy_resolves_from_output_period() -> None:
    expected = {
        "month": ("month", 25),
        "JJA": ("season", 85),
        "AMJJAS": ("half_year", 175),
        "year": ("year", 350),
    }

    for frequency_name, (period, minimum_days) in expected.items():
        policy = resolve_completeness_policy(
            completeness=None,
            allow_missing_periods=None,
            frequency=FrequencyRegistry.lookup(frequency_name),
            source_frequency=FrequencyRegistry.DAY,
            missing_method="any",
            missing_options=None,
        )

        assert policy.name == "ecad"
        assert policy.method == "at_least_n"
        assert policy.options == {"n": minimum_days}
        assert policy.period == period
        assert policy.version == "11"


def test_ecad_policy_scales_day_minimum_for_regular_subdaily_input() -> None:
    policy = resolve_completeness_policy(
        completeness="ecad",
        allow_missing_periods=None,
        frequency=FrequencyRegistry.MONTH,
        source_frequency=FrequencyRegistry.HOUR,
        missing_method="any",
        missing_options=None,
    )

    assert policy.method == "at_least_n"
    assert policy.options == {"n": 25 * 24}


def test_wmo_policy_resolves_by_aggregation_kind() -> None:
    expected = {
        "mean": ("wmo", {"nm": 11, "nc": 5}),
        "count": ("wmo", {"nm": 11, "nc": 5}),
        "sum": ("any", {}),
        "extreme": (None, {}),
        "other": ("any", {}),
    }

    for aggregation, (method, options) in expected.items():
        policy = resolve_completeness_policy(
            completeness="wmo",
            allow_missing_periods=None,
            frequency=FrequencyRegistry.MONTH,
            source_frequency=FrequencyRegistry.DAY,
            missing_method="any",
            missing_options=None,
            wmo_aggregation=aggregation,
        )

        assert policy.name == "wmo"
        assert policy.method == method
        assert policy.options == options
        assert policy.aggregation == aggregation
        assert policy.version == "WMO-No. 1203 (2017)"


def test_wmo_policy_uses_strict_fallback_outside_daily_standard_periods() -> None:
    policy = resolve_completeness_policy(
        completeness="wmo",
        allow_missing_periods=None,
        frequency=FrequencyRegistry.MONTH,
        source_frequency=FrequencyRegistry.HOUR,
        missing_method="any",
        missing_options=None,
        wmo_aggregation="mean",
    )

    assert policy.method == "any"
    assert policy.period == "month_strict_fallback"


def test_wmo_policy_uses_strict_fallback_for_custom_date_seasons() -> None:
    policy = resolve_completeness_policy(
        completeness="wmo",
        allow_missing_periods=None,
        frequency=FrequencyRegistry.lookup(("season", ("15 march", "15 june"))),
        source_frequency=FrequencyRegistry.DAY,
        missing_method="any",
        missing_options=None,
        wmo_aggregation="mean",
    )

    assert policy.method == "any"
    assert policy.period == "season_strict_fallback"


def test_numeric_policy_is_a_configurable_minimum_valid_fraction() -> None:
    policy = resolve_completeness_policy(
        completeness=0.8,
        allow_missing_periods=None,
        frequency=FrequencyRegistry.MONTH,
        source_frequency=FrequencyRegistry.DAY,
        missing_method="any",
        missing_options=None,
    )

    assert policy.name == "minimum_valid_fraction"
    assert policy.method == "pct"
    assert policy.options["tolerance"] > 0.2
    assert policy.period == "month"
    assert policy.metadata()["completeness_minimum_valid_fraction"] == "0.8"


def test_explicit_legacy_boolean_retains_7_2_behavior() -> None:
    policy = resolve_completeness_policy(
        completeness=None,
        allow_missing_periods=False,
        frequency=FrequencyRegistry.YEAR,
        source_frequency=FrequencyRegistry.DAY,
        missing_method="any",
        missing_options=None,
    )

    assert policy.name == "strict"
    assert policy.method == "any"


def test_spatially_varying_season_uses_safe_strict_fallback() -> None:
    start = xr.DataArray(np.array([[100, 120]]), dims=["lat", "lon"])
    end = xr.DataArray(np.array([[200, 220]]), dims=["lat", "lon"])
    frequency = FrequencyRegistry.lookup((start, end))

    policy = resolve_completeness_policy(
        completeness="ecad",
        allow_missing_periods=None,
        frequency=frequency,
        source_frequency=FrequencyRegistry.DAY,
        missing_method="any",
        missing_options=None,
    )

    assert policy.name == "ecad"
    assert policy.method == "any"
    assert policy.period == "year"

    fraction_policy = resolve_completeness_policy(
        completeness=0.8,
        allow_missing_periods=None,
        frequency=frequency,
        source_frequency=FrequencyRegistry.DAY,
        missing_method="any",
        missing_options=None,
    )
    assert fraction_policy.method == "any"
    assert fraction_policy.period == "spatial_season_strict_fallback"


def test_ecad_annual_boundary_is_applied_to_index_result() -> None:
    below = _summer_day_input(349)
    boundary = _summer_day_input(350)

    below_result = icclim.index(
        below,
        index_name="SU",
        var_name="tasmax",
        slice_mode="year",
        logs_verbosity="SILENT",
    )
    boundary_result = icclim.index(
        boundary,
        index_name="SU",
        var_name="tasmax",
        slice_mode="year",
        logs_verbosity="SILENT",
    )

    assert np.isnan(below_result.SU.compute().item())
    assert boundary_result.SU.compute().item() == 350
    assert boundary_result.SU.attrs["completeness_policy"] == "ecad"
    assert boundary_result.SU.attrs["completeness_options"] == '{"n": 350}'


def test_configurable_fraction_boundary_is_applied_to_index_result() -> None:
    below = _summer_day_input(24)
    boundary = _summer_day_input(25)

    below_result = icclim.index(
        below,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness=0.8,
        logs_verbosity="SILENT",
    )
    boundary_result = icclim.index(
        boundary,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness=0.8,
        logs_verbosity="SILENT",
    )

    assert np.isnan(below_result.SU.compute().item())
    assert boundary_result.SU.compute().item() == 25


def test_wmo_count_rejects_11_missing_or_5_consecutive_days() -> None:
    accepted = _month_with_missing_days(range(0, 20, 2))
    eleven_missing = _month_with_missing_days(range(0, 22, 2))
    five_consecutive = _month_with_missing_days(range(5, 10))

    accepted_result = icclim.index(
        accepted,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )
    eleven_result = icclim.index(
        eleven_missing,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )
    consecutive_result = icclim.index(
        five_consecutive,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )

    assert accepted_result.SU.compute().item() == 21
    assert np.isnan(eleven_result.SU.compute().item())
    assert np.isnan(consecutive_result.SU.compute().item())
    assert accepted_result.SU.attrs["completeness_aggregation"] == "count"
    assert accepted_result.SU.attrs["completeness_options"] == '{"nc": 5, "nm": 11}'
    assert accepted_result.SU.attrs["completeness_method"] == "icclim:wmo"


def test_wmo_count_treats_omitted_dates_as_consecutive_missing_days() -> None:
    data = _month_with_missing_days([]).drop_sel(
        time=pd.date_range("2001-01-06", periods=5)
    )

    result = icclim.index(
        data,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )

    assert np.isnan(result.SU.compute().item())


@pytest.mark.parametrize("index_name", ["TG", "SU"])
@pytest.mark.parametrize(
    ("slice_mode", "first_period_is_partial"),
    [
        ("MAM", False),
        ("JJA", False),
        ("SON", False),
        ("AMJJAS", False),
        ("DJF", True),
        ("ONDJFM", True),
    ],
)
def test_wmo_seasons_ignore_out_of_season_months_and_keep_partial_boundaries(
    index_name: str,
    slice_mode: str,
    first_period_is_partial: bool,
) -> None:
    time = pd.date_range("2000-01-01", "2003-12-31", freq="D")
    tas = xr.DataArray(
        np.full(time.size, 303.15),
        coords={"time": time},
        dims="time",
        name="tas",
        attrs={"units": "K"},
    )

    result = icclim.index(
        in_files=tas,
        var_name="tas",
        index_name=index_name,
        slice_mode=slice_mode,
        completeness="wmo",
        allow_partial_seasons="end",
        logs_verbosity="SILENT",
    )

    values = result[index_name].values
    expected_missing = [first_period_is_partial, *([False] * (values.size - 1))]
    assert np.isnan(values).tolist() == expected_missing


def test_ecad_amjjas_uses_the_complete_april_to_september_half_year() -> None:
    time = pd.date_range("2001-01-01", "2003-12-31", freq="D")
    tas = xr.DataArray(
        np.full(time.size, 303.15),
        coords={"time": time},
        dims="time",
        name="tas",
        attrs={"units": "K"},
    )

    result = icclim.index(
        tas,
        var_name="tas",
        index_name="SU",
        slice_mode="AMJJAS",
        completeness="ecad",
        logs_verbosity="SILENT",
    )

    np.testing.assert_array_equal(result.SU.values, [183, 183, 183])


@pytest.mark.parametrize(
    ("allow_partial_seasons", "first_missing", "last_missing"),
    [
        (False, True, True),
        ("start", False, True),
        ("end", True, False),
        (True, False, False),
    ],
)
def test_wmo_cross_year_season_preserves_partial_period_controls(
    allow_partial_seasons: bool | str,
    first_missing: bool,
    last_missing: bool,
) -> None:
    time = pd.date_range("2000-01-01", "2003-12-31", freq="D")
    tas = xr.DataArray(
        np.full(time.size, 283.15),
        coords={"time": time},
        dims="time",
        name="tas",
        attrs={"units": "K"},
    )

    result = icclim.index(
        in_files=tas,
        var_name="tas",
        index_name="TG",
        slice_mode="DJF",
        completeness="wmo",
        allow_partial_seasons=allow_partial_seasons,
        logs_verbosity="SILENT",
    )

    missing = np.isnan(result.TG.values)
    assert missing[0] == first_missing
    assert not missing[1:-1].any()
    assert missing[-1] == last_missing


def test_wmo_season_masks_an_omitted_constituent_month() -> None:
    time = pd.date_range("2000-01-01", "2003-12-31", freq="D")
    time = time[~((time.year == 2001) & (time.month == 4))]
    tas = xr.DataArray(
        np.full(time.size, 283.15),
        coords={"time": time},
        dims="time",
        name="tas",
        attrs={"units": "K"},
    )

    with pytest.warns(UserWarning, match="could not infer a regular source"):
        result = icclim.index(
            in_files=tas,
            var_name="tas",
            index_name="TG",
            slice_mode="MAM",
            completeness="wmo",
            logs_verbosity="SILENT",
        )

    assert np.isnan(result.TG.values).tolist() == [False, True, False, False]


@pytest.mark.parametrize(
    "calendar",
    [
        "standard",
        "proleptic_gregorian",
        "julian",
        "noleap",
        "all_leap",
        "360_day",
    ],
)
def test_wmo_seasons_support_cftime_boundaries(calendar: str) -> None:
    end = "2003-12-30" if calendar == "360_day" else "2003-12-31"
    time = xr.date_range(
        "2000-01-01",
        end,
        freq="D",
        calendar=calendar,
        use_cftime=True,
    )
    tas = xr.DataArray(
        np.full(time.size, 283.15),
        coords={"time": time},
        dims="time",
        name="tas",
        attrs={"units": "K"},
    )

    mam = icclim.index(
        tas,
        var_name="tas",
        index_name="TG",
        slice_mode="MAM",
        completeness="wmo",
        allow_partial_seasons="end",
        logs_verbosity="SILENT",
    )
    djf = icclim.index(
        tas,
        var_name="tas",
        index_name="TG",
        slice_mode="DJF",
        completeness="wmo",
        allow_partial_seasons="end",
        logs_verbosity="SILENT",
    )

    assert not np.isnan(mam.TG.values).any()
    assert np.isnan(djf.TG.values).tolist() == [True, False, False, False, False]


def test_wmo_count_preserves_non_midnight_daily_timestamps() -> None:
    data = _month_with_missing_days(range(0, 20, 2)).assign_coords(
        time=pd.date_range("2001-01-01 12:00", periods=31)
    )

    result = icclim.index(
        data,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )

    assert result.SU.compute().item() == 21


@pytest.mark.parametrize(
    ("calendar", "days"),
    [
        ("noleap", 31),
        ("all_leap", 31),
        ("360_day", 30),
        ("standard", 31),
        ("julian", 31),
        ("proleptic_gregorian", 31),
    ],
)
def test_wmo_count_supports_cftime_calendars(calendar: str, days: int) -> None:
    values = np.full(days, 303.15)
    values[range(0, 20, 2)] = np.nan
    data = xr.DataArray(
        values,
        coords={
            "time": xr.date_range(
                "2001-01-01 12:00",
                periods=days,
                freq="D",
                calendar=calendar,
                use_cftime=True,
            )
        },
        dims="time",
        attrs={"units": "K"},
        name="tasmax",
    )

    result = icclim.index(
        data,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )

    assert result.SU.compute().item() == days - 10


def test_wmo_count_propagates_invalid_month_to_annual_output() -> None:
    data = _summer_day_input(365)
    data[5:10] = np.nan

    result = icclim.index(
        data,
        index_name="SU",
        var_name="tasmax",
        slice_mode="year",
        completeness="wmo",
        logs_verbosity="SILENT",
    )

    assert np.isnan(result.SU.compute().item())


def test_wmo_consecutive_run_does_not_cross_month_boundary() -> None:
    values = np.full(59, 303.15)
    values[28:33] = np.nan
    data = xr.DataArray(
        values,
        coords={"time": pd.date_range("2001-01-01", periods=59)},
        dims="time",
        attrs={"units": "K"},
        name="tasmax",
    )

    result = icclim.index(
        data,
        index_name="SU",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    ).SU.compute()

    np.testing.assert_array_equal(result.values, [28, 26])


def test_wmo_sum_is_strict_and_simple_extreme_uses_available_days() -> None:
    data = _month_with_missing_days([5])

    summed = icclim.index(
        data.rename("pr").assign_attrs(units="mm/day"),
        index_name="sum",
        var_name="pr",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )
    maximum = icclim.index(
        data,
        index_name="maximum",
        var_name="tasmax",
        slice_mode="month",
        completeness="wmo",
        logs_verbosity="SILENT",
    )

    assert np.isnan(summed["sum"].compute().item())
    assert maximum.maximum.compute().item() == 30
    assert maximum.maximum.attrs["completeness_method"] == "not_applied"
    assert maximum.maximum.attrs["completeness_aggregation"] == "extreme"


def _summer_day_input(number_of_days: int) -> xr.DataArray:
    return xr.DataArray(
        np.full(number_of_days, 303.15),
        coords={"time": pd.date_range("2001-01-01", periods=number_of_days)},
        dims="time",
        attrs={"units": "K"},
        name="tasmax",
    )


def _month_with_missing_days(missing_indices) -> xr.DataArray:
    values = np.full(31, 303.15)
    values[list(missing_indices)] = np.nan
    return xr.DataArray(
        values,
        coords={"time": pd.date_range("2001-01-01", periods=31)},
        dims="time",
        attrs={"units": "K"},
        name="tasmax",
    )


def test_missing_options_support_the_xclim_legacy_call_api() -> None:
    received = {}

    class LegacyMissingMethod:
        def __init__(self, da, freq, src_timestep, **indexer) -> None:
            received.update(
                da=da,
                freq=freq,
                src_timestep=src_timestep,
                indexer=indexer,
            )

        def __call__(self, **options):
            received["options"] = options
            return xr.DataArray([False], dims="time")

    source = _summer_day_input(350)
    indicator = GenericIndicatorRegistry.CountOccurrences
    result = indicator._compute_missing_mask(
        LegacyMissingMethod,
        source,
        "YS",
        "D",
        {},
        {"n": 350},
    )

    assert not result.item()
    assert received["options"] == {"n": 350}
    assert received["indexer"] == {}

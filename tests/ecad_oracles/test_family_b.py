"""Independent value oracles for ECAD percentile and spell indices."""

from __future__ import annotations

import numpy as np
import pytest

import icclim

from ._helpers import (
    annual_event_count,
    annual_spell_count,
    bootstrap_temperature_year,
    doy_percentile,
    make_bootstrap_temperature_series,
    make_percentile_precip_cube,
    make_percentile_temperature_cube,
    precipitation_percentile_oracle,
)

TEMPERATURE_INDICES = (
    ("TG10p", "tg", 10, "<", False),
    ("TG90p", "tg", 90, ">", False),
    ("TN10p", "tn", 10, "<", False),
    ("TN90p", "tn", 90, ">", False),
    ("TX10p", "tx", 10, "<", False),
    ("TX90p", "tx", 90, ">", False),
    ("CSDI", "tn", 10, "<", True),
    ("WSDI", "tx", 90, ">", True),
)


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(("name", "variable", "percentile", "operator", "spell"), TEMPERATURE_INDICES)
def test_temperature_percentile_indices(
    name: str,
    variable: str,
    percentile: int,
    operator: str,
    spell: bool,
    chunk: int | None,
) -> None:
    """ATBD uses strict comparisons to type-8 five-day-window DOY percentiles."""
    units = "K" if chunk == 7 else "degC"
    source = make_percentile_temperature_cube(units)[variable]
    values = source.values - (273.15 if units == "K" else 0)
    threshold = doy_percentile(source.time, values, percentile)
    event = values > threshold if operator == ">" else values < threshold
    expected = annual_spell_count(source.time, event) if spell else annual_event_count(source.time, event)
    study = source if chunk is None else source.chunk({"time": chunk})

    actual = getattr(icclim, name.lower())(
        study,
        base_period_time_range=["2001-01-01", "2003-12-31"],
        bootstrap=False,
        out_file=None,
        completeness="none",
    )[name].compute()

    np.testing.assert_allclose(actual.values[-2:], expected[-2:], equal_nan=True)
    assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs["units"] == "d"
    assert actual.attrs["long_name"]
    assert actual.attrs["standard_name"]


@pytest.mark.xfail(strict=True, reason="#540")
def test_tx90p_bootstrap_matches_atbd_leave_one_year_out() -> None:
    """Base-period overlap follows the ATBD replicate-and-average bootstrap."""
    source = make_bootstrap_temperature_series()
    expected = bootstrap_temperature_year(source, 1961, 90)
    actual = icclim.tx90p(
        source,
        base_period_time_range=["1961-01-01", "1990-12-31"],
        bootstrap=True,
        out_file=None,
        completeness="none",
    ).TX90p.compute()
    np.testing.assert_allclose(actual.values[0], expected)


PRECIPITATION_INDICES = (
    ("R75p", 75, False),
    ("R95p", 95, False),
    ("R99p", 99, False),
    ("R75pTOT", 75, True),
    ("R95pTOT", 95, True),
    ("R99pTOT", 99, True),
)


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(("name", "percentile", "fraction"), PRECIPITATION_INDICES)
def test_precipitation_percentile_indices(
    name: str,
    percentile: int,
    fraction: bool,
    chunk: int | None,
) -> None:
    """Wet-day percentiles use RR>=1 mm; fractions retain floor-equal totals."""
    units = "kg m-2 s-1" if chunk == 7 else "mm/day"
    source = make_percentile_precip_cube(units)
    expected = precipitation_percentile_oracle(source, percentile, fraction=fraction)
    study = source if chunk is None else source.chunk({"time": chunk})

    actual = getattr(icclim, name.lower())(
        study,
        base_period_time_range=["2001-01-01", "2003-12-31"],
        bootstrap=False,
        out_file=None,
        completeness="none",
    )[name].compute()

    np.testing.assert_allclose(actual.values, expected, rtol=1e-10, atol=1e-10, equal_nan=True)
    assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs["long_name"]
    assert actual.attrs["standard_name"]

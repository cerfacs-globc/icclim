"""Independent value oracles for ECAD family A: GSL, SPI3, and SPI6."""

from __future__ import annotations

import numpy as np
import pytest

import icclim

from ._helpers import gsl_oracle, make_gsl_cube, make_spi_cube, spi_gamma_oracle


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(
    ("calendar", "units"),
    [("standard", "degC"), ("noleap", "K"), ("360_day", "degC"), ("all_leap", "K")],
)
def test_gsl_matches_atbd_oracle(calendar: str, units: str, chunk: int | None) -> None:
    """ATBD onset is the first six-day run >5 C; cessation is <5 C after July 1."""
    source = make_gsl_cube(calendar, units)
    expected_values = source.values - (273.15 if units == "K" else 0)
    expected = gsl_oracle(source.time, expected_values)
    study = source if chunk is None else source.chunk({"time": chunk})

    actual = icclim.gsl(study, out_file=None, completeness="none").GSL.compute()

    np.testing.assert_allclose(actual.values, expected, equal_nan=True)
    assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs["units"] == "days"
    assert actual.attrs["long_name"]
    assert actual.attrs["standard_name"]


@pytest.mark.xfail(strict=True, reason="#537")
def test_gsl_strictly_excludes_days_equal_to_five_degrees() -> None:
    """ATBD v11 says TG > 5 C, so six days exactly at 5 C cannot start GSL."""
    source = make_gsl_cube("standard", "degC", equality_probe=True)
    expected = gsl_oracle(source.time, source.values)
    actual = icclim.gsl(source, out_file=None, completeness="none").GSL.compute()
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


@pytest.mark.xfail(strict=True, reason="#538")
def test_gsl_honors_disabled_completeness_for_isolated_nan() -> None:
    """One missing interior day must not erase GSL when completeness is disabled."""
    source = make_gsl_cube("standard", "degC", isolated_missing=True)
    expected = gsl_oracle(source.time, source.values)
    actual = icclim.gsl(source, out_file=None, completeness="none").GSL.compute()
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)


def test_gsl_ignore_feb29_and_time_range_are_value_stable() -> None:
    """Dropping leap days and selecting a time range agree with direct slicing."""
    source = make_gsl_cube("all_leap", "degC")
    keep = ~((source.time.dt.month == 2) & (source.time.dt.day == 29))
    expected = gsl_oracle(source.time[keep], source.values[keep])
    ignored = icclim.gsl(
        source,
        out_file=None,
        completeness="none",
        ignore_Feb29th=True,
    ).GSL.compute()
    np.testing.assert_allclose(ignored.values, expected, equal_nan=True)

    full = icclim.gsl(source, out_file=None, completeness="none").GSL.compute()
    subset = icclim.gsl(
        source,
        out_file=None,
        completeness="none",
        time_range=["2002-01-01", "2003-12-31"],
    ).GSL.compute()
    np.testing.assert_allclose(subset.values, full.values[1:], equal_nan=True)
    np.testing.assert_array_equal(subset.time.values, full.time.values[1:])


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(("name", "window"), [("SPI3", 3), ("SPI6", 6)])
def test_spi_matches_direct_scipy_gamma_fit(name: str, window: int, chunk: int | None) -> None:
    """Compare monthly SPI with an independent scipy MLE gamma fit (atol 0.30)."""
    units = "kg m-2 s-1" if chunk == 7 else "mm/day"
    source = make_spi_cube(units)
    expected = spi_gamma_oracle(source, window)
    study = source if chunk is None else source.chunk({"time": chunk})

    function = getattr(icclim, name.lower())
    actual = function(
        study,
        base_period_time_range=["1981-01-01", "2010-12-31"],
        out_file=None,
    )[name].compute()

    np.testing.assert_allclose(actual.values, expected, atol=0.30, rtol=0, equal_nan=True)
    assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs["long_name"]
    assert actual.attrs["standard_name"]

"""Independent value oracles for ECAD extrema, means, ranges, and weather indices."""

from __future__ import annotations

import numpy as np
import pytest

import icclim

from ._helpers import annual_reduce, make_extreme_cube, rx5day_oracle, vdtr_oracle

SINGLE_INDICES = (
    ("TG", "tg", "mean"),
    ("TN", "tn", "mean"),
    ("TX", "tx", "mean"),
    ("TXx", "tx", "max"),
    ("TNx", "tn", "max"),
    ("TXn", "tx", "min"),
    ("TNn", "tn", "min"),
    ("RR", "pr", "sum"),
    ("RX1day", "pr", "max"),
    ("FXx", "wsgs_max", "max"),
    ("FG", "sfcWind", "mean"),
    ("PP", "psl", "mean"),
    ("SS", "sund", "sum"),
    ("RH", "hurs", "mean"),
)


def _extreme_expected(source, variable: str, reducer: str):
    values = source[variable].values.copy()
    units = source[variable].attrs["units"]
    if units == "K":
        values -= 273.15
    elif units == "kg m-2 s-1":
        values *= 86400
    elif units == "Pa":
        values /= 100
    if reducer in {"mean", "sum"}:
        return annual_reduce(source.time, values, reducer)
    years = np.unique(source.time.dt.year.values)
    function = np.max if reducer == "max" else np.min
    return np.stack([function(values[source.time.dt.year.values == year], axis=0) for year in years])


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(("name", "variable", "reducer"), SINGLE_INDICES)
def test_single_variable_extrema_and_means(
    name: str,
    variable: str,
    reducer: str,
    chunk: int | None,
) -> None:
    """Annual extrema, means, and sums directly implement their ATBD reductions."""
    source = make_extreme_cube(converted_units=chunk == 7)
    expected = _extreme_expected(source, variable, reducer)
    study = source[variable] if chunk is None else source[variable].chunk({"time": chunk})
    actual = getattr(icclim, name.lower())(
        study,
        out_file=None,
        completeness="none",
    )[name].compute()
    np.testing.assert_allclose(actual.values, expected, rtol=1e-10, atol=1e-10, equal_nan=True)
    assert actual.dims == ("time", "lat", "lon")
    assert actual.attrs["units"]
    assert actual.attrs["long_name"]
    assert actual.attrs["standard_name"]


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize("name", ["DTR", "ETR", "vDTR"])
def test_temperature_ranges(name: str, chunk: int | None) -> None:
    """DTR/ETR/vDTR follow ATBD daily-range definitions without icclim formulas."""
    source = make_extreme_cube(converted_units=chunk == 7)
    tx = source.tx.values - (273.15 if source.tx.attrs["units"] == "K" else 0)
    tn = source.tn.values - (273.15 if source.tn.attrs["units"] == "K" else 0)
    if name == "DTR":
        expected = annual_reduce(source.time, tx - tn, "mean")
    elif name == "ETR":
        years = np.unique(source.time.dt.year.values)
        expected = np.stack(
            [
                np.max(tx[source.time.dt.year.values == year], axis=0)
                - np.min(tn[source.time.dt.year.values == year], axis=0)
                for year in years
            ]
        )
    else:
        expected = vdtr_oracle(source.time, tx, tn)
    study = source[["tx", "tn"]] if chunk is None else source[["tx", "tn"]].chunk({"time": chunk})
    actual = getattr(icclim, name.lower())(
        study,
        var_name=["tx", "tn"],
        out_file=None,
        completeness="none",
    )[name].compute()
    np.testing.assert_allclose(actual.values, expected, rtol=1e-10, atol=1e-10, equal_nan=True)


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize("name", ["PRCPTOT", "SDII", "RX5day"])
def test_precipitation_extrema_and_wet_day_reducers(
    name: str,
    chunk: int | None,
    request: pytest.FixtureRequest,
) -> None:
    """Wet days are RR>=1 mm and RX5day uses within-period five-day sums."""
    if name == "RX5day" and chunk == 7:
        request.applymarker(pytest.mark.xfail(strict=True, reason="#544"))
    source = make_extreme_cube(converted_units=chunk == 7)
    values = source.pr.values * (86400 if source.pr.attrs["units"] == "kg m-2 s-1" else 1)
    if name == "PRCPTOT":
        expected = annual_reduce(source.time, np.where(values >= 1, values, 0), "sum")
    elif name == "SDII":
        wet_sum = annual_reduce(source.time, np.where(values >= 1, values, 0), "sum")
        wet_count = annual_reduce(source.time, values >= 1, "sum")
        expected = wet_sum / wet_count
    else:
        expected = rx5day_oracle(source.time, values)
    study = source.pr if chunk is None else source.pr.chunk({"time": chunk})
    actual = getattr(icclim, name.lower())(study, out_file=None, completeness="none")[name].compute()
    np.testing.assert_allclose(actual.values, expected, rtol=1e-10, atol=1e-10, equal_nan=True)


WIND_COUNTS = (
    ("FG6Bft", lambda values: values >= 10.8),
    ("FGcalm", lambda values: values <= 2),
    ("DDnorth", lambda values: (values > 315) | (values <= 45)),
    ("DDeast", lambda values: (values > 45) & (values <= 135)),
    ("DDsouth", lambda values: (values > 135) & (values <= 225)),
    ("DDwest", lambda values: (values > 225) & (values <= 315)),
)


@pytest.mark.parametrize("chunk", [None, 1, 7])
@pytest.mark.parametrize(("name", "condition"), WIND_COUNTS)
def test_wind_threshold_counts(name, condition, chunk: int | None) -> None:
    """Wind speed and direction boundary comparisons are independently explicit."""
    source = make_extreme_cube()
    variable = "DD" if name.startswith("DD") else "sfcWind"
    expected = annual_reduce(source.time, condition(source[variable].values), "sum")
    study = source[variable] if chunk is None else source[variable].chunk({"time": chunk})
    actual = getattr(icclim, name.lower())(study, out_file=None, completeness="none")[name].compute()
    np.testing.assert_allclose(actual.values, expected, equal_nan=True)

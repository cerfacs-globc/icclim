"""
A temperature equal to a threshold in another unit is equal to it (issue #675).

77 degF is 25 degC. The conversion of a float64 temperature from degF to degC by pint
gives 25.000000000000057, which used to be counted as above a strict ``> 25 degC``
threshold. The converted temperatures and thresholds are now snapped to the nearest
1e-10, far below the precision of any temperature.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.units import convert_units_to

import icclim
from icclim._core.generic.threshold.basic import BasicThreshold
from icclim._core.utils import snap_converted_temperature

TIME = pd.date_range("2001-01-01", periods=3)
TO_UNIT = {
    "degC": lambda c: c,
    "K": lambda c: c + 273.15,
    "degF": lambda c: c * 9.0 / 5.0 + 32.0,
}


def _series(value_degc: float, name: str, unit: str) -> xr.DataArray:
    return xr.DataArray(
        [TO_UNIT[unit](value_degc)] * 3,
        dims="time",
        coords={"time": TIME},
        name=name,
        attrs={"units": unit},
    )


@pytest.mark.parametrize("unit", ["degF", "K", "degC"])
@pytest.mark.parametrize(
    ("name", "variable", "value"),
    [("sd", "tasmax", 25.0), ("tx35", "tasmax", 35.0), ("tr", "tasmin", 20.0)],
)
def test_dcsc_strict_thresholds_do_not_count_a_value_equal_to_them(
    name: str, variable: str, value: float, unit: str
) -> None:
    """The reproducer of the issue: a value equal to a strict ``>`` threshold."""
    actual = getattr(icclim.dcsc, name)(
        _series(value, variable, unit),
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name.upper()]
    np.testing.assert_array_equal(actual.values, [0])


@pytest.mark.parametrize("unit", ["degF", "K", "degC"])
@pytest.mark.parametrize(
    ("name", "variable", "value"), [("su", "tasmax", 25.0), ("tr", "tasmin", 20.0)]
)
def test_ecad_strict_thresholds_do_not_count_a_value_equal_to_them(
    name: str, variable: str, value: float, unit: str
) -> None:
    actual = getattr(icclim, name)(
        _series(value, variable, unit),
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )[name.upper()]
    np.testing.assert_array_equal(actual.values, [0])


COUNTS_AT_THE_THRESHOLD = {">": 0, ">=": 3, "<=": 3, "<": 0}


@pytest.mark.parametrize("unit", ["degF", "K", "degC"])
@pytest.mark.parametrize(("operator", "expected"), COUNTS_AT_THE_THRESHOLD.items())
def test_counts_of_a_value_equal_to_a_threshold_given_in_degc(
    operator: str, expected: int, unit: str
) -> None:
    """Data in any unit against a threshold in degC: the four operators."""
    result = icclim.count_occurrences(
        _series(25.0, "tasmax", unit),
        threshold=f"{operator} 25 degC",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )
    np.testing.assert_array_equal(result.count_occurrences.values, [expected])


@pytest.mark.parametrize("threshold_unit", ["degF", "K"])
@pytest.mark.parametrize(("operator", "expected"), COUNTS_AT_THE_THRESHOLD.items())
def test_counts_of_a_value_equal_to_a_threshold_given_in_another_unit(
    operator: str, expected: int, threshold_unit: str
) -> None:
    """Data in degC against a threshold in degF or K: the four operators."""
    threshold = TO_UNIT[threshold_unit](25.0)
    result = icclim.count_occurrences(
        _series(25.0, "tasmax", "degC"),
        threshold=f"{operator} {threshold!r} {threshold_unit}",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )
    np.testing.assert_array_equal(result.count_occurrences.values, [expected])


def test_a_value_just_above_the_threshold_is_still_counted() -> None:
    """The snapping is far below the precision of a temperature: 1e-6 degC counts."""
    source = _series(25.000001, "tasmax", "degF")
    source.values[:] = (25.000001) * 9.0 / 5.0 + 32.0
    result = icclim.count_occurrences(
        source,
        threshold="> 25 degC",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    )
    np.testing.assert_array_equal(result.count_occurrences.values, [3])


# The snapping applies to float64 temperatures only (issue #675).


def _random_cube(dtype: str, unit: str) -> xr.DataArray:
    rng = np.random.default_rng(675)
    celsius = rng.uniform(-10, 45, (400, 3, 4))
    values = TO_UNIT[unit](celsius).astype(dtype)
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": pd.date_range("2000-01-01", periods=400)},
        name="tasmax",
        attrs={"units": unit},
    )


@pytest.mark.parametrize("unit", ["degC", "K", "degF"])
def test_float32_temperatures_are_returned_bit_identical(unit: str) -> None:
    data = _random_cube("float32", unit)
    snapped = snap_converted_temperature(data)
    assert snapped.dtype == np.float32
    np.testing.assert_array_equal(
        snapped.values.view(np.uint32), data.values.view(np.uint32)
    )
    assert snapped.attrs == data.attrs


@pytest.mark.parametrize("unit", ["degC", "K", "degF"])
def test_float32_data_compared_with_a_threshold_are_not_modified(unit: str) -> None:
    data = _random_cube("float32", unit)
    threshold = BasicThreshold(operator=">", value=25.0, unit="degC")
    seen = []

    def spy(left: xr.DataArray, right: object) -> xr.DataArray:
        seen.append(left)
        return left > 0

    threshold.compute(data, override_op=spy)
    assert seen[0].dtype == np.float32
    np.testing.assert_array_equal(
        seen[0].values.view(np.uint32), data.values.view(np.uint32)
    )


@pytest.mark.parametrize("operator", [">", "<="])
def test_float64_degf_77_is_equal_to_25_degc(operator: str) -> None:
    source = _series(25.0, "tasmax", "degF")
    assert source.dtype == np.float64
    actual = icclim.count_occurrences(
        source,
        threshold=f"{operator} 25 degC",
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    ).count_occurrences.values
    np.testing.assert_array_equal(actual, [0 if operator == ">" else 3])


@pytest.mark.parametrize("unit", ["degC", "K"])
def test_float64_k_and_degc_results_are_those_of_a_plain_comparison(unit: str) -> None:
    data = _random_cube("float64", unit)
    celsius = _random_cube("float64", "degC").values
    actual = icclim.su(
        data,
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    ).SU.compute()
    years = data.time.dt.year.values
    expected = np.stack(
        [(celsius[years == y] > 25).sum(axis=0) for y in np.unique(years)]
    )
    np.testing.assert_array_equal(
        actual.transpose("time", "lat", "lon").values, expected
    )


@pytest.mark.parametrize("dtype", ["int32", "int64"])
@pytest.mark.parametrize("operator", [">", "<="])
def test_integer_degf_77_is_equal_to_25_degc(dtype: str, operator: str) -> None:
    """Integer data are converted to float64 by pint, then snapped like float64 data."""
    source = _series(25.0, "tasmax", "degF").astype(dtype)
    assert source.dtype == dtype
    actual = icclim.count_occurrences(
        source,
        threshold=f"{operator} 25 degC",
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    ).count_occurrences.values
    np.testing.assert_array_equal(actual, [0 if operator == ">" else 3])


@pytest.mark.parametrize("dtype", ["int32", "int64"])
def test_integer_degf_is_float64_after_the_conversion_to_degc(dtype: str) -> None:
    source = _series(25.0, "tasmax", "degF").astype(dtype)
    assert convert_units_to(source, "degC").dtype == np.float64

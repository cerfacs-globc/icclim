"""
DCSC TRAV, the absolute value of the mean of the daily thermal amplitude (issue #668).

The index is the absolute value, for each grid point, of the mean over the period of
``TX - TN``. It is never negative and it does not depend on the order of ``var_name``.
The reference calculation below is written with numpy only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

TEMPERATURE_UNITS = {
    "degC": lambda values: values,
    "K": lambda values: values + 273.15,
    "degF": lambda values: values * 9.0 / 5.0 + 32.0,
}
VAR_NAMES = [["tasmax", "tasmin"], ["tasmin", "tasmax"], None]
VAR_NAMES_IDS = ["tx-first", "tn-first", "without-var_name"]


def _cube() -> xr.Dataset:
    """Three years of daily tasmin and tasmax on 2x2 grid points, with gaps."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261112)
    phase = 2 * np.pi * (time.dayofyear.to_numpy() - 80) / 365.25
    tas = 12 + 11 * np.sin(phase)[:, None, None]
    tas = (
        tas
        + np.array([[-2.0, 0.0], [1.5, 3.0]])
        + rng.normal(0, 0.8, (len(time), 2, 2))
    )
    tasmin = tas - 5.0 - rng.uniform(0, 1, tas.shape)
    tasmax = tas + 5.0 + rng.uniform(0, 1, tas.shape)
    tasmin[time == pd.Timestamp("2001-05-11"), 0, 1] = np.nan
    tasmax[time == pd.Timestamp("2002-06-12"), 1, 0] = np.nan
    coords = {"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]}
    return xr.Dataset(
        {
            "tasmin": xr.DataArray(
                tasmin, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
            "tasmax": xr.DataArray(
                tasmax, dims=("time", "lat", "lon"), attrs={"units": "degC"}
            ),
        },
        coords=coords,
    )


def _reference(source: xr.Dataset) -> np.ndarray:
    """Absolute value of the yearly mean of TX - TN, over the days with both."""
    years = np.asarray(source.time.dt.year.values)
    outputs = []
    for year in np.unique(years):
        selected = years == year
        amplitude = (
            source["tasmax"].values[selected] - source["tasmin"].values[selected]
        )
        outputs.append(np.abs(np.nanmean(amplitude, axis=0)))
    return np.stack(outputs)


def _in_unit(source: xr.Dataset, unit: str) -> xr.Dataset:
    converted = source.copy(deep=True)
    for variable in converted.data_vars.values():
        variable.data = TEMPERATURE_UNITS[unit](variable.data)
        variable.attrs["units"] = unit
    return converted


def _trav(source: xr.Dataset, var_name=None, **kwargs) -> xr.DataArray:
    options = {
        "slice_mode": "year",
        "out_file": None,
        "completeness": "none",
        "logs_verbosity": "SILENT",
    }
    options.update(kwargs)
    if var_name is not None:
        options["var_name"] = var_name
    return icclim.dcsc.trav(source, **options).TRAV.compute()


def _two_variables(low: float, high: float) -> xr.Dataset:
    """Three days of tasmin = low and tasmax = high, the reproducer of the issue."""
    time = pd.date_range("2001-01-01", periods=3)

    def series(value: float, name: str) -> xr.DataArray:
        return xr.DataArray(
            [value] * 3,
            dims="time",
            coords={"time": time},
            name=name,
            attrs={"units": "degC"},
        )

    return xr.merge([series(low, "tasmin"), series(high, "tasmax")])


@pytest.mark.parametrize("var_name", VAR_NAMES, ids=VAR_NAMES_IDS)
def test_both_orders_of_var_name_give_the_reproducer_of_issue_668(
    var_name: list[str] | None,
) -> None:
    actual = _trav(_two_variables(0.0, 10.0), var_name)
    np.testing.assert_array_equal(actual.values, [10.0])


@pytest.mark.parametrize("var_name", VAR_NAMES, ids=VAR_NAMES_IDS)
def test_trav_is_positive_when_tx_is_below_tn_everywhere(
    var_name: list[str] | None,
) -> None:
    """Inconsistent data (TX below TN) are not flagged: the result is positive."""
    actual = _trav(_two_variables(low=10.0, high=0.0), var_name)
    np.testing.assert_array_equal(actual.values, [10.0])
    cube = _cube()
    inverted = cube.rename({"tasmin": "tasmax", "tasmax": "tasmin"})
    values = _trav(inverted, var_name)
    assert (values.values[~np.isnan(values.values)] > 0).all()
    np.testing.assert_allclose(
        values.transpose("time", "lat", "lon").values,
        _reference(cube),
        equal_nan=True,
    )


@pytest.mark.parametrize("var_name", VAR_NAMES, ids=VAR_NAMES_IDS)
@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
def test_trav_is_the_absolute_value_of_the_mean_of_tx_minus_tn(
    chunk_size: int | None, var_name: list[str] | None
) -> None:
    source = _cube()
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    actual = _trav(source, var_name)
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        _reference(_cube()),
        equal_nan=True,
    )
    assert (actual.values[~np.isnan(actual.values)] >= 0).all()
    assert actual.attrs["units"]


@pytest.mark.parametrize("unit", ["K", "degF"])
def test_trav_gives_the_same_amplitude_in_other_units(unit: str) -> None:
    """The inputs are converted to degree_Celsius, the unit of the output."""
    actual = _trav(_in_unit(_cube(), unit), ["tasmin", "tasmax"])
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        _reference(_cube()),
        rtol=1e-6,
        equal_nan=True,
    )


@pytest.mark.parametrize("completeness", ["none", "strict", "ecad"])
@pytest.mark.parametrize("var_name", VAR_NAMES, ids=VAR_NAMES_IDS)
def test_missing_values_and_completeness_are_those_of_the_mean_of_difference(
    completeness: str, var_name: list[str] | None
) -> None:
    """TRAV is the absolute value of DTR, with the same NaN and the same masks."""
    source = _cube()
    actual = _trav(source, var_name, completeness=completeness)
    dtr = icclim.dtr(
        source,
        var_name=["tasmax", "tasmin"],
        slice_mode="year",
        out_file=None,
        completeness=completeness,
        logs_verbosity="SILENT",
    ).DTR.compute()
    np.testing.assert_array_equal(np.isnan(actual.values), np.isnan(dtr.values))
    np.testing.assert_allclose(actual.values, np.abs(dtr.values), equal_nan=True)


def test_strict_completeness_masks_the_periods_with_a_missing_day() -> None:
    source = _cube()
    strict = _trav(source, completeness="strict")
    complete = _trav(source, completeness="none")
    # 2001-05-11 of the grid point (45.0, 2.0) and 2002-06-12 of (46.0, 1.0) are missing.
    assert np.isnan(strict.sel(lat=45.0, lon=2.0).values[1])
    assert np.isnan(strict.sel(lat=46.0, lon=1.0).values[2])
    assert not np.isnan(complete.values).any()


def test_a_grid_point_without_any_data_is_missing() -> None:
    source = _cube().copy(deep=True)
    source["tasmin"].loc[{"lat": 45.0, "lon": 1.0}] = np.nan
    actual = _trav(source)
    assert actual.sel(lat=45.0, lon=1.0).isnull().all()
    assert not actual.sel(lat=46.0, lon=2.0).isnull().any()


def test_the_generic_function_takes_the_absolute_value_of_the_period_mean() -> None:
    """The mean of the differences is taken first, not the mean of their absolute."""
    time = pd.date_range("2001-01-01", periods=4)
    first = xr.DataArray(
        [10.0, 0.0, 10.0, 0.0],
        dims="time",
        coords={"time": time},
        name="tasmax",
        attrs={"units": "degC"},
    )
    second = xr.DataArray(
        [0.0, 10.0, 0.0, 10.0],
        dims="time",
        coords={"time": time},
        name="tasmin",
        attrs={"units": "degC"},
    )
    source = xr.merge([first, second])
    # The differences are 10 and -10 in turn: their mean is 0, the mean of their
    # absolute values would be 10.
    actual = icclim.dcsc.trav(
        source,
        var_name=["tasmax", "tasmin"],
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    ).TRAV
    np.testing.assert_array_equal(actual.values, [0.0])
    generic = icclim.absolute_mean_of_difference(
        source,
        var_name=["tasmax", "tasmin"],
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
    ).absolute_mean_of_difference
    np.testing.assert_array_equal(generic.values, [0.0])

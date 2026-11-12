"""
DCSC TRAV, the mean of the daily thermal amplitude (issue #668).

The DRIAS definition is the mean of ``TX - TN``, as for the ECA&D ``DTR``. The
reference calculation below is written with numpy only.
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
    """Yearly mean of TX - TN over the days where both are known."""
    years = np.asarray(source.time.dt.year.values)
    outputs = []
    for year in np.unique(years):
        selected = years == year
        amplitude = (
            source["tasmax"].values[selected] - source["tasmin"].values[selected]
        )
        outputs.append(np.nanmean(amplitude, axis=0))
    return np.stack(outputs)


def _in_unit(source: xr.Dataset, unit: str) -> xr.Dataset:
    converted = source.copy(deep=True)
    for variable in converted.data_vars.values():
        variable.data = TEMPERATURE_UNITS[unit](variable.data)
        variable.attrs["units"] = unit
    return converted


def _trav(source: xr.Dataset, **kwargs) -> xr.DataArray:
    return icclim.dcsc.trav(
        source,
        var_name=["tasmax", "tasmin"],
        slice_mode="year",
        out_file=None,
        completeness="none",
        logs_verbosity="SILENT",
        **kwargs,
    ).TRAV.compute()


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
def test_trav_is_the_mean_of_tx_minus_tn(chunk_size: int | None) -> None:
    source = _cube()
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    actual = _trav(source)
    expected = _reference(_cube())
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values, expected, equal_nan=True
    )
    assert (actual.values > 0).all()
    assert actual.attrs["units"]


@pytest.mark.parametrize("unit", ["K", "degF"])
def test_trav_gives_the_same_amplitude_in_other_units(unit: str) -> None:
    """The inputs are converted to degree_Celsius, the unit of the output."""
    actual = _trav(_in_unit(_cube(), unit))
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        _reference(_cube()),
        rtol=1e-6,
        equal_nan=True,
    )


def test_trav_of_a_dataset_with_tasmin_and_tasmax_is_positive() -> None:
    """Reproducer of issue 668 without var_name: the variables are found by name."""
    time = pd.date_range("2001-01-01", periods=3)

    def series(value: float, name: str) -> xr.DataArray:
        return xr.DataArray(
            [value] * 3,
            dims="time",
            coords={"time": time},
            name=name,
            attrs={"units": "degC"},
        )

    source = xr.merge([series(0.0, "tasmin"), series(10.0, "tasmax")])
    actual = icclim.dcsc.trav(
        source, out_file=None, completeness="none", logs_verbosity="SILENT"
    ).TRAV
    np.testing.assert_array_equal(actual.values, [10.0])


def test_the_order_of_the_variables_gives_the_sign() -> None:
    """The first variable is TX: with var_name the first name is, whatever its name."""
    time = pd.date_range("2001-01-01", periods=3)

    def series(value: float, name: str) -> xr.DataArray:
        return xr.DataArray(
            [value] * 3,
            dims="time",
            coords={"time": time},
            name=name,
            attrs={"units": "degC"},
        )

    source = xr.merge([series(0.0, "tasmin"), series(10.0, "tasmax")])

    def trav(**kwargs) -> np.ndarray:
        return icclim.dcsc.trav(
            source,
            out_file=None,
            completeness="none",
            logs_verbosity="SILENT",
            **kwargs,
        ).TRAV.values

    # Variables found in the dataset: TX - TN, as the ECA&D DTR.
    np.testing.assert_array_equal(trav(), [10.0])
    np.testing.assert_array_equal(trav(var_name=["tasmax", "tasmin"]), [10.0])
    # With var_name the order is the one given: the first name is the minuend.
    np.testing.assert_array_equal(trav(var_name=["tasmin", "tasmax"]), [-10.0])

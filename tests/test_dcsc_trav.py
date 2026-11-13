"""
DCSC TRAV, the mean of the daily thermal amplitude (issue #668).

The DRIAS definition is the mean of ``TX - TN``, as for the ECA&D ``DTR``. The
reference calculation below is written with numpy only.
"""

from __future__ import annotations

import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim.main import _reset_input_order_notices

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


NOTICE = (
    "TRAV = {first} - {second} (first input minus second; "
    "pass var_name=['tasmax', 'tasmin'] to control the order)\n"
)


@pytest.fixture(autouse=True)
def _forget_the_input_order_notices() -> None:
    """The notice is printed once per process: start every test afresh."""
    _reset_input_order_notices()


def _two_variables(low: str = "tasmin", high: str = "tasmax") -> xr.Dataset:
    time = pd.date_range("2001-01-01", periods=3)

    def series(value: float, name: str) -> xr.DataArray:
        return xr.DataArray(
            [value] * 3,
            dims="time",
            coords={"time": time},
            name=name,
            attrs={"units": "degC"},
        )

    return xr.merge([series(0.0, low), series(10.0, high)])


def _call_trav(source: xr.Dataset, **kwargs) -> np.ndarray:
    return icclim.dcsc.trav(
        source, out_file=None, completeness="none", **kwargs
    ).TRAV.values


def test_the_notice_is_printed_once_per_process(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _two_variables()
    _call_trav(source)
    assert capsys.readouterr().out == NOTICE.format(first="tasmax", second="tasmin")
    _call_trav(source)
    _call_trav(source, var_name=["tasmin", "tasmax"])
    assert capsys.readouterr().out == ""


def test_resetting_the_state_prints_the_notice_again(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _two_variables()
    _call_trav(source)
    capsys.readouterr()
    _reset_input_order_notices()
    _call_trav(source)
    assert capsys.readouterr().out.startswith("TRAV = ")


@pytest.mark.parametrize(
    ("var_name", "first", "second", "sign"),
    [
        (["tasmax", "tasmin"], "tasmax", "tasmin", 10.0),
        (["tasmin", "tasmax"], "tasmin", "tasmax", -10.0),
        (None, "tasmax", "tasmin", 10.0),
    ],
    ids=["tx-first", "tn-first", "without-var_name"],
)
def test_the_notice_gives_the_variables_that_are_used_and_the_sign(
    var_name: list[str] | None,
    first: str,
    second: str,
    sign: float,
    capsys: pytest.CaptureFixture[str],
) -> None:
    kwargs = {} if var_name is None else {"var_name": var_name}
    result = _call_trav(_two_variables(), **kwargs)
    assert capsys.readouterr().out == NOTICE.format(first=first, second=second)
    np.testing.assert_array_equal(result, [sign])


def test_the_notice_uses_the_names_of_the_variables_of_the_dataset(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _two_variables(low="lowT", high="highT")
    result = _call_trav(source, var_name=["highT", "lowT"])
    assert capsys.readouterr().out == NOTICE.format(first="highT", second="lowT")
    np.testing.assert_array_equal(result, [10.0])


def test_the_other_indices_print_no_notice(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = _two_variables()
    icclim.dtr(source, out_file=None, completeness="none")
    icclim.dcsc.txav(source, var_name="tasmax", out_file=None, completeness="none")
    assert capsys.readouterr().out == ""


def test_nothing_is_printed_when_icclim_is_imported() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import icclim"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "TRAV" not in completed.stdout

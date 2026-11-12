"""
DCSC indices with a normal, whatever the unit of the input (issue #617).

TXND, TNHT, TNND, TNCWD and TXHWD add or subtract 5 delta_degree_Celsius to the normal.
They raised ``DimensionalityError`` ("cannot convert from delta_degree_Celsius to
degree_Celsius") with input in degC or degF, and worked with input in K.
The same physical data in K, degC and degF must give the same result, boundary
included (days exactly at normal +/- 5 degC count).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

# unit -> (value in this unit of a temperature given in degC)
UNITS = {
    "K": lambda c: c + 273.15,
    "degC": lambda c: c,
    "degF": lambda c: c * 9 / 5 + 32,
}
NORMAL_C = 10.0
# name, function, variable, sign of the departure from the normal, spell based
CASES = [
    ("TXND", icclim.dcsc.txnd, "tasmax", +1, False),
    ("TNHT", icclim.dcsc.tnht, "tasmin", +1, False),
    ("TNND", icclim.dcsc.tnnd, "tasmin", -1, False),
    ("TNCWD", icclim.dcsc.tncwd, "tasmin", -1, True),
    ("TXHWD", icclim.dcsc.txhwd, "tasmax", +1, True),
]


def _cube(variable: str, unit: str, spell_c: float, chunked: bool) -> xr.DataArray:
    """2001, one 8-day spell from 1 to 8 July, ``spell_c`` degC, otherwise the normal."""
    time = pd.date_range("2001-01-01", "2001-12-31")
    values_c = np.where(
        (time >= "2001-07-01") & (time <= "2001-07-08"), spell_c, NORMAL_C
    )
    da = xr.DataArray(
        UNITS[unit](values_c)[:, None] * np.ones((len(time), 2)),
        dims=("time", "x"),
        coords={"time": time, "x": [0, 1]},
        name=variable,
        attrs={"units": unit},
    )
    return da.chunk({"x": 1}) if chunked else da


def _compute(name, function, variable, unit, spell_c, chunked=False) -> float:
    normal = _cube(variable, unit, NORMAL_C, chunked=False)
    result = function(
        _cube(variable, unit, spell_c, chunked),
        normal=normal,
        out_file=None,
        completeness="none",
    )[name]
    return float(result.compute().isel(x=0).values.ravel()[0])


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", UNITS)
@pytest.mark.parametrize(("name", "function", "variable", "sign", "spell"), CASES)
class TestDcscNormalUnits:
    def test_a_spell_beyond_the_threshold_counts(
        self, name, function, variable, sign, spell, unit, chunked
    ) -> None:
        # 10 degC above or below the normal.
        assert (
            _compute(name, function, variable, unit, NORMAL_C + sign * 10, chunked) == 8
        )

    def test_days_exactly_at_the_threshold_count(
        self, name, function, variable, sign, spell, unit, chunked
    ) -> None:
        assert (
            _compute(name, function, variable, unit, NORMAL_C + sign * 5, chunked) == 8
        )

    def test_days_just_inside_the_threshold_do_not_count(
        self, name, function, variable, sign, spell, unit, chunked
    ) -> None:
        assert (
            _compute(name, function, variable, unit, NORMAL_C + sign * 4.5, chunked)
            == 0
        )

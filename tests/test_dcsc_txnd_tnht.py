"""
DCSC indices TXND and TNHT against the DRIAS catalogue (issue #620).

DRIAS: ``Tx quot >= normale quot + 5°C`` (TXND) and ``Tn quot >= normale quot + 5°C``
(TNHT). Constant normal of 10 degC, input in K, one 8-day spell from 1 to 8 July 2001
and yearly output.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

NORMAL = 283.15  # 10 degC
CASES = [
    ("TXND", icclim.dcsc.txnd, "tasmax"),
    ("TNHT", icclim.dcsc.tnht, "tasmin"),
]


def _series(variable: str, spell: float, chunked: bool = False) -> xr.DataArray:
    time = pd.date_range("2001-01-01", "2001-12-31")
    values = np.where((time >= "2001-07-01") & (time <= "2001-07-08"), spell, NORMAL)
    da = xr.DataArray(
        values[:, None] * np.ones((len(time), 2)),
        dims=("time", "x"),
        coords={"time": time, "x": [0, 1]},
        name=variable,
        attrs={"units": "K"},
    )
    return da.chunk({"x": 1}) if chunked else da


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize(("name", "function", "variable"), CASES)
class TestAnomalyDays:
    def _compute(self, name, function, variable, spell, chunked) -> np.ndarray:
        result = function(
            _series(variable, spell, chunked),
            normal=_series(variable, NORMAL),
            out_file=None,
            completeness="none",
        )[name]
        return result.compute().isel(x=0).values

    def test_days_beyond_the_threshold_count(
        self, name, function, variable, chunked
    ) -> None:
        np.testing.assert_array_equal(
            self._compute(name, function, variable, 293.15, chunked), [8]
        )

    def test_days_exactly_at_normal_plus_5_count(
        self, name, function, variable, chunked
    ) -> None:
        np.testing.assert_array_equal(
            self._compute(name, function, variable, NORMAL + 5, chunked), [8]
        )

    def test_days_half_a_kelvin_inside_the_threshold_do_not_count(
        self, name, function, variable, chunked
    ) -> None:
        np.testing.assert_array_equal(
            self._compute(name, function, variable, NORMAL + 4.5, chunked), [0]
        )

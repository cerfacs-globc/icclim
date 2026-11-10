"""
DCSC indices TXHWD, TNCWD and TNND against the DRIAS catalogue (issue #616).

Constant normal of 10 degC, input in K, one 8-day spell from 1 to 8 July 2001 and
yearly output. DRIAS: TXHWD ``Tx >= normal + 5`` for more than 5 consecutive days,
TNCWD ``Tn <= normal - 5`` for more than 5 consecutive days, TNND ``Tn <= normal - 5``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

NORMAL = 283.15  # 10 degC
AT_THRESHOLD_WARM = 288.15  # normal + 5
AT_THRESHOLD_COLD = 278.15  # normal - 5


def _series(variable: str, base: float, spell: float, chunked: bool) -> xr.DataArray:
    time = pd.date_range("2001-01-01", "2001-12-31")
    values = np.where((time >= "2001-07-01") & (time <= "2001-07-08"), spell, base)
    da = xr.DataArray(
        values[:, None] * np.ones((len(time), 2)),
        dims=("time", "x"),
        coords={"time": time, "x": [0, 1]},
        name=variable,
        attrs={"units": "K"},
    )
    return da.chunk({"x": 1}) if chunked else da


def _normal(variable: str) -> xr.DataArray:
    return _series(variable, NORMAL, NORMAL, chunked=False)


CASES = [
    ("TXHWD", icclim.dcsc.txhwd, "tasmax", 293.15, AT_THRESHOLD_WARM),
    ("TNCWD", icclim.dcsc.tncwd, "tasmin", 273.15, AT_THRESHOLD_COLD),
    ("TNND", icclim.dcsc.tnnd, "tasmin", 273.15, AT_THRESHOLD_COLD),
]


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize(("name", "function", "variable", "spell", "at"), CASES)
class TestAnomalyIndices:
    def _compute(self, name, function, variable, value, chunked) -> np.ndarray:
        source = _series(variable, NORMAL, value, chunked)
        result = function(
            source, normal=_normal(variable), out_file=None, completeness="none"
        )[name]
        return result.compute().isel(x=0).values

    def test_spell_beyond_the_threshold_counts_its_days(
        self, name, function, variable, spell, at, chunked
    ) -> None:
        np.testing.assert_array_equal(
            self._compute(name, function, variable, spell, chunked), [8]
        )

    def test_days_exactly_at_the_threshold_count(
        self, name, function, variable, spell, at, chunked
    ) -> None:
        np.testing.assert_array_equal(
            self._compute(name, function, variable, at, chunked), [8]
        )

    def test_days_just_inside_the_threshold_do_not_count(
        self, name, function, variable, spell, at, chunked
    ) -> None:
        inside = at - 0.5 if at > NORMAL else at + 0.5
        np.testing.assert_array_equal(
            self._compute(name, function, variable, inside, chunked), [0]
        )


@pytest.mark.parametrize(("name", "function", "variable", "spell", "at"), CASES[:2])
def test_spells_need_more_than_5_days(name, function, variable, spell, at) -> None:
    # A 5-day spell does not count, a 6-day spell does ("plus de 5 jours").
    time = pd.date_range("2001-01-01", "2001-12-31")
    for length, expected in ((5, 0), (6, 6)):
        end = pd.Timestamp("2001-07-01") + pd.Timedelta(days=length - 1)
        values = np.where((time >= "2001-07-01") & (time <= end), spell, NORMAL)
        source = xr.DataArray(
            values,
            dims="time",
            coords={"time": time},
            name=variable,
            attrs={"units": "K"},
        )
        result = function(
            source,
            normal=_normal(variable).isel(x=0, drop=True),
            out_file=None,
            completeness="none",
        )[name]
        np.testing.assert_array_equal(result.compute().values.ravel(), [expected])

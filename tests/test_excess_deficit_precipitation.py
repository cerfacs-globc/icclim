"""
Excess and deficit of a precipitation (issue #644).

``icclim.excess`` and ``icclim.deficit`` raised ``KeyError: 'units'`` with xarray 2026.2
and later: the subtraction of the threshold dropped the units of the result because the
texts of the units of the data ("mm/day") and of the threshold ("mm d-1") differ.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.units import convert_units_to

import icclim

TIME = pd.date_range("2000-01-01", "2001-12-31")
THRESHOLD_MM_PER_DAY = 1.0


def _values() -> np.ndarray:
    rng = np.random.default_rng(3)
    wet = rng.random((len(TIME), 2)) > 0.45
    return np.where(wet, rng.gamma(0.8, 7.0, (len(TIME), 2)) + 0.05, 0.0)


def _oracle(values: np.ndarray, kind: str) -> np.ndarray:
    """Sum of the excess (or deficit) in mm for 2000 and 2001, day by day."""
    result = np.zeros((2, values.shape[1]))
    for i, day in enumerate(TIME):
        for j in range(values.shape[1]):
            p = values[i, j]
            gap = (
                p - THRESHOLD_MM_PER_DAY
                if kind == "excess"
                else (THRESHOLD_MM_PER_DAY - p)
            )
            result[day.year - 2000, j] += max(gap, 0.0)
    return result


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", ["mm/day", "kg m-2 s-1"])
@pytest.mark.parametrize("kind", ["excess", "deficit"])
def test_excess_and_deficit_of_a_precipitation(
    kind: str, unit: str, chunked: bool
) -> None:
    values = _values()
    data = values / 86400 if unit == "kg m-2 s-1" else values
    pr = xr.DataArray(
        data,
        dims=("time", "x"),
        coords={"time": TIME, "x": [0, 1]},
        name="pr",
        attrs={"units": unit},
    )
    if chunked:
        pr = pr.chunk({"x": 1})
    result = getattr(icclim, kind)(
        pr, threshold="1 mm/day", out_file=None, completeness="none"
    )
    da = result[next(iter(result.data_vars))].compute()
    assert "units" in da.attrs
    in_mm = convert_units_to(da, "mm", context="hydro")
    np.testing.assert_allclose(in_mm.values, _oracle(values, kind), rtol=1e-6)

"""
DCSC PQ90 and PQ99 (issue #643): the percentile of the daily precipitation, in mm/day.

They were declared with the output unit "%", so any call raised ``DimensionalityError``
(from mm/day to percent). DRIAS: "q90 (q99) des précipitations totales quotidiennes",
a precipitation, not a percentage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.units import convert_units_to

import icclim

TIME = pd.date_range("1999-01-01", "2001-12-31")
BASE = ("1999-01-01", "1999-12-31")
STUDY = ("2000-01-01", "2001-12-31")


def _values() -> np.ndarray:
    rng = np.random.default_rng(0)
    values = rng.gamma(0.8, 7.0, (len(TIME), 2))
    values[rng.random(values.shape) > 0.6] = 0.0
    return values


@pytest.mark.parametrize("chunked", [False, True], ids=["eager", "chunked"])
@pytest.mark.parametrize("unit", ["mm/day", "kg m-2 s-1"])
@pytest.mark.parametrize(
    ("function", "quantile"), [(icclim.dcsc.pq90, 0.90), (icclim.dcsc.pq99, 0.99)]
)
def test_pq_is_the_percentile_of_the_daily_precipitation_in_mm_per_day(
    function, quantile: float, unit: str, chunked: bool
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
    result = function(
        pr,
        base_period_time_range=BASE,
        time_range=STUDY,
        out_file=None,
        completeness="none",
    )
    da = result[next(k for k in result.data_vars if k.upper().startswith("PQ"))]
    da = da.compute()
    # Years 2000 and 2001, all the days, the interpolation of icclim by default.
    expected = np.array(
        [
            np.quantile(
                values[TIME.year == year], quantile, axis=0, method="median_unbiased"
            )
            for year in (2000, 2001)
        ]
    )
    in_mm_per_day = convert_units_to(da, "mm/day", context="hydro")
    np.testing.assert_allclose(in_mm_per_day.values, expected, rtol=1e-6)

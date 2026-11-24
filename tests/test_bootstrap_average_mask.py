"""In-base years of single-threshold percentile counts keep the replicate average.

The bootstrapped exceedance of an in-base year is the average over the replicates
(fractional values). It must be summed as such, whatever the execution mode.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold

pytestmark = pytest.mark.filterwarnings("ignore")

MODES = ("compiled", "default", "safe")


def _dataset(seed: int = 5) -> xr.Dataset:
    time = pd.date_range("1988-01-01", "2007-12-31", freq="D")
    rng = np.random.default_rng(seed)
    doy = time.dayofyear.to_numpy()[:, None, None]
    seasonal = 8 * np.sin(2 * np.pi * (doy - 100) / 365.25)
    tas = (285 + seasonal + rng.normal(0, 3, (len(time), 2, 2))).astype("float32")
    da = xr.DataArray(
        tas,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0, 2.0], "lon": [1.0, 2.0]},
        attrs={"units": "K"},
        name="tasmax",
    )
    # chunked so that the compiled path can be used
    return da.to_dataset().chunk({"time": 730})


def _run(monkeypatch, mode, call):
    if mode == "compiled":
        monkeypatch.delenv("ICCLIM_BOOTSTRAP_MODE", raising=False)
    else:
        monkeypatch.setenv("ICCLIM_BOOTSTRAP_MODE", mode)
    return call().compute()


def _base(n_years):
    return ["1993-01-01", f"{1993 + n_years - 1}-12-31"]


def _count(slice_mode, n_years, window):
    def call():
        thr = build_threshold(
            "> 90 doy_per", reference_period=_base(n_years), doy_window_width=window
        )
        return icclim.count_occurrences(
            in_files=_dataset(),
            var_name="tasmax",
            threshold=thr,
            slice_mode=slice_mode,
        )

    return call


def _tx90p(slice_mode, n_years, out_unit=None):
    def call():
        return icclim.index(
            index_name="TX90p",
            in_files=_dataset(),
            var_name="tasmax",
            base_period_time_range=_base(n_years),
            slice_mode=slice_mode,
            out_unit=out_unit,
        )

    return call


def _first_var(ds):
    return ds[next(iter(ds.data_vars))]


@pytest.mark.parametrize("mode", ["default", "safe"])
@pytest.mark.parametrize(("n_years", "window"), [(3, 5), (3, 1), (10, 5), (10, 1)])
def test_count_occurrences_matches_compiled(monkeypatch, mode, n_years, window):
    expected = _first_var(
        _run(monkeypatch, "compiled", _count("year", n_years, window))
    )
    got = _first_var(_run(monkeypatch, mode, _count("year", n_years, window)))
    # With a 5 day window the compiled path and xclim can differ by a fraction of
    # a day around the year boundaries (not related to the averaging, which is
    # what is tested here: the error it caused is of several days).
    xr.testing.assert_allclose(got, expected, atol=0 if window == 1 else 1.0)


@pytest.mark.parametrize("mode", ["default", "safe"])
@pytest.mark.parametrize("n_years", [3, 10])
@pytest.mark.parametrize("out_unit", [None, "%"])
def test_tx90p_matches_compiled(monkeypatch, mode, n_years, out_unit):
    expected = _first_var(
        _run(monkeypatch, "compiled", _tx90p("year", n_years, out_unit))
    )
    got = _first_var(_run(monkeypatch, mode, _tx90p("year", n_years, out_unit)))
    xr.testing.assert_allclose(got, expected, atol=0.3 if out_unit else 1.0)
    assert got.dtype == expected.dtype
    assert got.attrs["units"] == expected.attrs["units"]


@pytest.mark.parametrize("mode", MODES)
def test_monthly_slice_mode_is_consistent(monkeypatch, mode):
    ref = _first_var(_run(monkeypatch, "default", _count("month", 3, 5)))
    got = _first_var(_run(monkeypatch, mode, _count("month", 3, 5)))
    # the averaged replicates give halves in the base period, as in the year mode
    assert np.any(got.sel(time=slice("1993", "1995")).values % 1 == 0.5)
    # months away from the year boundaries match exactly
    inner = got.time.dt.month.isin(range(2, 12))
    xr.testing.assert_allclose(got.where(inner, drop=True), ref.where(inner, drop=True))
    xr.testing.assert_allclose(got, ref, atol=1.0)
    # the months of an in-base year add up to the averaged yearly count
    yearly = _first_var(_run(monkeypatch, "default", _count("year", 3, 5)))
    monthly_sum = got.groupby("time.year").sum("time")
    for year in (1993, 1994, 1995):
        np.testing.assert_allclose(
            monthly_sum.sel(year=year).values,
            yearly.sel(time=str(year)).squeeze().values,
            atol=1.0,
        )


@pytest.mark.parametrize("mode", MODES)
def test_in_base_count_is_the_replicate_average(monkeypatch, mode):
    res = _first_var(_run(monkeypatch, mode, _count("year", 3, 5)))
    in_base = res.sel(time=slice("1993", "1995")).values
    out_base = res.sel(time=slice("1996", "2007")).values
    # a base of 3 years gives 2 replicates: halves appear and must be kept
    assert np.any(in_base % 1 == 0.5)
    # years outside the base period are plain integer counts
    np.testing.assert_array_equal(out_base, np.round(out_base))


@pytest.mark.parametrize("mode", MODES)
def test_spells_keep_the_union(monkeypatch, mode):
    def call():
        thr = build_threshold(
            "> 90 doy_per", reference_period=_base(3), doy_window_width=5
        )
        return icclim.max_consecutive_occurrence(
            in_files=_dataset(), var_name="tasmax", threshold=thr, slice_mode="year"
        )

    ref = _first_var(_run(monkeypatch, "default", call))
    got = _first_var(_run(monkeypatch, mode, call))
    xr.testing.assert_allclose(got, ref)
    np.testing.assert_array_equal(got.values, np.round(got.values))

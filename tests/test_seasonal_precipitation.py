from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

import icclim


def test_rr_jja_matches_manual_daily_sum() -> None:
    time = pd.date_range("2001-01-01", "2001-12-31", freq="D")
    values = np.linspace(0.0, 9.0, len(time))
    pr = xr.DataArray(
        values,
        coords={"time": time},
        dims=["time"],
        name="pr",
        attrs={"units": "mm/day"},
    )

    result = icclim.rr(
        in_files=pr,
        var_name="pr",
        slice_mode="JJA",
        logs_verbosity="silent",
    ).RR
    expected = pr.sel(time=pr.time.dt.month.isin([6, 7, 8])).sum(dim="time")

    np.testing.assert_allclose(result.values, [expected.item()])
    assert result.attrs["units"] == "mm"


def test_generic_sum_multi_year_mam_matches_manual_daily_sum() -> None:
    time = pd.date_range("2001-01-01", "2002-12-31", freq="D")
    pr = xr.DataArray(
        np.full(len(time), 1.0),
        coords={"time": time},
        dims=["time"],
        name="pr",
        attrs={"units": "mm/day"},
    )

    result = icclim.sum(
        in_files=pr,
        var_name="pr",
        slice_mode="MAM",
        logs_verbosity="silent",
    )["sum"].load()
    expected = (
        pr.sel(time=pr.time.dt.month.isin([3, 4, 5]))
        .resample(time="YS-MAR")
        .sum(dim="time")
        .assign_coords(time=result.time)
    )

    np.testing.assert_allclose(result.values, expected.values)
    assert result.attrs["units"] == "mm"


def test_prcptot_custom_season_matches_manual_wet_day_sum() -> None:
    time = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    values = np.full(len(time), 2.0)
    values[10:20] = 0.5
    values[380:390] = 0.25
    pr = xr.DataArray(
        values,
        coords={"time": time},
        dims=["time"],
        name="pr",
        attrs={"units": "mm/day"},
    )

    slice_mode = ("season", ("1 november", "31 march"))
    result = icclim.prcptot(
        in_files=pr,
        var_name="pr",
        slice_mode=slice_mode,
        logs_verbosity="silent",
    ).PRCPTOT.load()

    season_mask = (
        (pr.time.dt.month == 11)
        | (pr.time.dt.month == 12)
        | (pr.time.dt.month <= 3)
    )
    expected = (
        pr.where(season_mask)
        .where(pr >= 1, 0)
        .resample(time="YS-NOV")
        .sum(dim="time")
        .dropna(dim="time", how="all")
    )

    np.testing.assert_allclose(result.isel(time=1).item(), expected.isel(time=1).item())
    assert np.isnan(result.isel(time=0).item())
    assert np.isnan(result.isel(time=2).item())


def test_su_jja_matches_manual_count() -> None:
    time = pd.date_range("2001-01-01", "2001-12-31", freq="D")
    tasmax = xr.DataArray(
        np.full(len(time), 20.0),
        coords={"time": time},
        dims=["time"],
        name="tasmax",
        attrs={"units": "degree_Celsius"},
    )
    tasmax.loc[{"time": slice("2001-06-01", "2001-08-31")}] = 30.0

    result = icclim.su(
        in_files=tasmax,
        var_name="tasmax",
        slice_mode="JJA",
        logs_verbosity="silent",
    ).SU.load()
    expected = (tasmax.sel(time=tasmax.time.dt.month.isin([6, 7, 8])) > 25).sum()

    np.testing.assert_allclose(result.values, [expected.item()])
    assert result.attrs["units"] in {"d", "day"}

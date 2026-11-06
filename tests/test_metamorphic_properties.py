"""Metamorphic property tests.

Each test transforms the input or the call in a way whose effect on the result
is known (same data chunked differently, same quantity in other units, a period
computed in pieces, ...) and checks that the result follows. They need no
hand-written expected values, so they catch wrong results that only appear for
some layouts or options.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

BASE_INDICES = [
    ("sum", {}),
    ("average", {}),
    ("maximum", {}),
    ("minimum", {}),
    ("count_occurrences", {"threshold": ">= 288 K"}),
    ("max_consecutive_occurrence", {"threshold": ">= 288 K"}),
]
IDS = [name for name, _ in BASE_INDICES]
SLICES = ["month", "year"]


def make_tas(
    start: str = "2001-01-01",
    end: str = "2003-12-31",
    units: str = "K",
    seed: int = 3,
) -> xr.DataArray:
    time = pd.date_range(start, end, freq="D")
    rng = np.random.default_rng(seed)
    season = 8 * np.sin(2 * np.pi * np.arange(time.size) / 365.25)[:, None, None]
    kelvin = 288 + season + 3 * rng.standard_normal((time.size, 3, 2))
    if units == "degC":
        values, attrs_units = kelvin - 273.15, "degC"
    elif units == "degF":
        values, attrs_units = (kelvin - 273.15) * 9 / 5 + 32, "degF"
    else:
        values, attrs_units = kelvin, "K"
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [0.0, 1.0, 2.0], "lon": [0.0, 1.0]},
        name="tas",
        attrs={"units": attrs_units, "standard_name": "air_temperature"},
    )


def compute(da: xr.DataArray | xr.Dataset, name: str, **kwargs) -> xr.DataArray:
    ds = da.to_dataset() if isinstance(da, xr.DataArray) else da
    kwargs.setdefault("slice_mode", "month")
    result = icclim.index(
        index_name=name, in_files=ds, var_name="tas", out_file=None, **kwargs
    )
    var = next(v for v in result.data_vars if not v.endswith("_thresholds"))
    out = result[var].compute()
    return out.drop_vars([c for c in out.coords if c not in out.dims])


def assert_same(a: xr.DataArray, b: xr.DataArray, **tol) -> None:
    b = b.transpose(*a.dims)
    xr.testing.assert_allclose(
        a.reset_coords(drop=True), b.reset_coords(drop=True), **tol
    )


# --- chunking invariance -----------------------------------------------------


@pytest.mark.parametrize("chunks", [{"time": 1}, {"time": 37, "lat": 1}, {"time": -1}])
@pytest.mark.parametrize("slice_mode", SLICES)
@pytest.mark.parametrize(("name", "kwargs"), BASE_INDICES, ids=IDS)
def test_result_does_not_depend_on_dask_chunks(name, kwargs, slice_mode, chunks):
    tas = make_tas()
    expected = compute(tas, name, slice_mode=slice_mode, **kwargs)
    actual = compute(tas.chunk(chunks), name, slice_mode=slice_mode, **kwargs)
    assert_same(expected, actual)


@pytest.mark.parametrize("chunks", [{"time": 1}, {"time": 3}, {"time": 200}])
def test_rolling_window_does_not_depend_on_dask_chunks(chunks):
    tas = make_tas()
    expected = compute(tas, "sum", rolling_window_width=5)
    actual = compute(tas.chunk(chunks), "sum", rolling_window_width=5)
    assert_same(expected, actual)


@pytest.mark.parametrize("chunks", [{"time": 1}, {"time": 37, "lat": 1}])
@pytest.mark.parametrize(
    ("name", "kwargs"),
    [
        ("maximum", {}),
        ("count_occurrences", {"threshold": ">= 288 K"}),
        ("max_consecutive_occurrence", {"threshold": ">= 288 K"}),
    ],
)
def test_event_dates_do_not_depend_on_dask_chunks(name, kwargs, chunks):
    tas = make_tas()

    def dates(da):
        result = icclim.index(
            index_name=name,
            in_files=da.to_dataset(),
            var_name="tas",
            slice_mode="month",
            date_event=True,
            out_file=None,
            **kwargs,
        )
        names = sorted(c for c in result.coords if c.startswith("event_date"))
        names += sorted(v for v in result.data_vars if v.startswith("event_date"))
        return {n: result[n].transpose("time", "lat", "lon").values for n in names}

    expected, actual = dates(tas), dates(tas.chunk(chunks))
    assert expected.keys() == actual.keys()
    for key in expected:
        np.testing.assert_array_equal(expected[key], actual[key])


# --- dimension order ----------------------------------------------------------


@pytest.mark.parametrize("slice_mode", SLICES)
@pytest.mark.parametrize(("name", "kwargs"), BASE_INDICES, ids=IDS)
def test_result_does_not_depend_on_dimension_order(name, kwargs, slice_mode):
    tas = make_tas()
    expected = compute(tas, name, slice_mode=slice_mode, **kwargs)
    actual = compute(
        tas.transpose("lat", "lon", "time"), name, slice_mode=slice_mode, **kwargs
    )
    assert_same(expected, actual)


# --- units -------------------------------------------------------------------


@pytest.mark.parametrize("units", ["degC", "degF"])
@pytest.mark.parametrize(
    "name", ["count_occurrences", "max_consecutive_occurrence"]
)
def test_counts_do_not_depend_on_the_unit_of_the_data(name, units):
    threshold = ">= 15 degC"
    expected = compute(make_tas(units="K"), name, threshold=threshold)
    actual = compute(make_tas(units=units), name, threshold=threshold)
    assert_same(expected, actual)


@pytest.mark.parametrize("threshold", [">= 15 degC", ">= 288.15 K", ">= 59 degF"])
def test_counts_do_not_depend_on_the_unit_of_the_threshold(threshold):
    expected = compute(make_tas(), "count_occurrences", threshold=">= 15 degC")
    actual = compute(make_tas(), "count_occurrences", threshold=threshold)
    assert_same(expected, actual)


# --- affine transformations --------------------------------------------------


@pytest.mark.parametrize("name", ["maximum", "minimum", "average"])
def test_shifting_the_data_shifts_these_statistics(name):
    tas = make_tas()
    shifted = (tas + 10.0).assign_attrs(tas.attrs)
    base = compute(tas, name)
    out = compute(shifted, name)
    assert_same(base + 10.0, out, atol=1e-9)


def test_minimum_is_below_average_is_below_maximum():
    tas = make_tas()
    low, mid, high = (compute(tas, n) for n in ("minimum", "average", "maximum"))
    assert bool((low <= mid + 1e-9).all())
    assert bool((mid <= high + 1e-9).all())


# --- thresholds --------------------------------------------------------------


def test_count_does_not_increase_when_the_threshold_increases():
    tas = make_tas()
    counts = [
        compute(tas, "count_occurrences", threshold=f">= {t} K")
        for t in (276, 282, 288, 294, 300)
    ]
    for lower, higher in zip(counts, counts[1:]):
        assert bool((higher <= lower).all())
    assert bool((counts[0] >= counts[-1]).all())


def test_greater_and_less_than_counts_add_up_to_the_period_length():
    tas = make_tas()
    above = compute(tas, "count_occurrences", threshold=">= 288 K")
    below = compute(tas, "count_occurrences", threshold="< 288 K")
    days = tas.isel(lat=0, lon=0).resample(time="MS").count().values
    total = above + below
    expected = total.copy(data=np.broadcast_to(days[:, None, None], total.shape))
    assert_same(expected, total)


def test_longest_run_is_never_longer_than_the_count():
    tas = make_tas()
    run = compute(
        tas, "max_consecutive_occurrence", slice_mode="year", threshold=">= 288 K"
    )
    count = compute(tas, "count_occurrences", slice_mode="year", threshold=">= 288 K")
    assert bool((run <= count).all())


@pytest.mark.xfail(
    strict=True,
    reason="A run crossing a period boundary is attributed to the period where it "
    "starts and the following periods are NaN (design question, issue 543)",
)
def test_monthly_longest_run_stays_within_its_month_and_is_never_missing():
    tas = make_tas()
    run = compute(tas, "max_consecutive_occurrence", threshold=">= 288 K")
    days = tas.isel(lat=0, lon=0).resample(time="MS").count().values
    assert bool(run.notnull().all())
    assert bool((run <= days[:, None, None]).all())


# --- splitting a period ------------------------------------------------------


@pytest.mark.parametrize("year", [2001, 2002, 2003])
@pytest.mark.parametrize(("name", "kwargs"), BASE_INDICES, ids=IDS)
def test_yearly_result_is_the_same_on_a_subset_of_the_period(name, kwargs, year):
    tas = make_tas()
    full = compute(tas, name, slice_mode="year", **kwargs)
    part = compute(
        tas,
        name,
        slice_mode="year",
        time_range=[f"{year}-01-01", f"{year}-12-31"],
        **kwargs,
    )
    assert_same(full.sel(time=str(year)), part)


def test_monthly_counts_add_up_to_the_yearly_count():
    tas = make_tas()
    monthly = compute(tas, "count_occurrences", threshold=">= 288 K")
    yearly = compute(
        tas, "count_occurrences", slice_mode="year", threshold=">= 288 K"
    )
    summed = monthly.groupby("time.year").sum("time")
    assert_same(
        yearly.assign_coords(time=yearly.time.dt.year).rename(time="year"),
        summed,
    )


def test_monthly_sums_add_up_to_the_yearly_sum():
    tas = make_tas()
    monthly = compute(tas, "sum")
    yearly = compute(tas, "sum", slice_mode="year")
    summed = monthly.groupby("time.year").sum("time")
    assert_same(
        yearly.assign_coords(time=yearly.time.dt.year).rename(time="year"),
        summed,
        rtol=1e-9,
    )


# --- calendar type -----------------------------------------------------------


def _as_noleap(tas: xr.DataArray) -> xr.DataArray:
    time = xr.date_range(
        "2001-01-01", "2003-12-31", freq="D", calendar="noleap", use_cftime=True
    )
    assert time.size == tas.time.size  # 2001-2003 has no leap day
    return tas.assign_coords(time=time)


@pytest.mark.parametrize("slice_mode", SLICES)
@pytest.mark.parametrize(("name", "kwargs"), BASE_INDICES, ids=IDS)
def test_result_does_not_depend_on_the_time_index_type(name, kwargs, slice_mode):
    tas = make_tas()
    expected = compute(tas, name, slice_mode=slice_mode, **kwargs)
    actual = compute(_as_noleap(tas), name, slice_mode=slice_mode, **kwargs)
    np.testing.assert_allclose(
        expected.transpose("time", ...).values,
        actual.transpose("time", ...).values,
    )


# --- missing values ----------------------------------------------------------


def _with_missing_day(tas: xr.DataArray) -> tuple[xr.DataArray, str]:
    month = "2002-03"
    out = tas.copy()
    out.loc[{"time": f"{month}-10", "lat": 0.0, "lon": 0.0}] = np.nan
    return out, month


def test_a_missing_day_masks_only_its_period_and_cell_by_default():
    tas = make_tas()
    holed, month = _with_missing_day(tas)
    full = compute(tas, "count_occurrences", threshold=">= 288 K")
    masked = compute(
        holed, "count_occurrences", threshold=">= 288 K", completeness="strict"
    )
    hit = masked.sel(time=month).isel(lat=0, lon=0)
    assert bool(np.isnan(hit).all())
    untouched = masked.where(
        ~((masked.time.dt.strftime("%Y-%m") == month) & (masked.lat == 0.0)
          & (masked.lon == 0.0))
    )
    assert_same(
        full.where(untouched.notnull()), untouched.where(untouched.notnull())
    )


def test_a_missing_day_that_cannot_count_does_not_change_the_count_without_masking():
    # NaN is never >= threshold, so replacing a value that is below the
    # threshold by NaN must not change the count once masking is disabled.
    cell = {"time": "2002-03-10", "lat": 0.0, "lon": 0.0}
    below = make_tas()
    below.loc[cell] = 280.0
    holed = below.copy()
    holed.loc[cell] = np.nan
    expected = compute(below, "count_occurrences", threshold=">= 288 K")
    actual = compute(
        holed, "count_occurrences", threshold=">= 288 K", completeness="none"
    )
    assert_same(expected, actual)


@pytest.mark.parametrize(
    ("name", "slice_mode"),
    [
        ("count_occurrences", "month"),
        ("count_occurrences", "year"),
        ("max_consecutive_occurrence", "year"),
        pytest.param(
            "max_consecutive_occurrence",
            "month",
            marks=pytest.mark.xfail(
                strict=True, reason="Run attribution across periods (issue 543)"
            ),
        ),
    ],
)
def test_complete_data_is_never_masked_by_default(name, slice_mode):
    tas = make_tas()
    default = compute(tas, name, slice_mode=slice_mode, threshold=">= 288 K")
    unmasked = compute(
        tas, name, slice_mode=slice_mode, threshold=">= 288 K", completeness="none"
    )
    assert bool(default.notnull().all())
    assert_same(default, unmasked)


def test_a_cell_without_any_data_is_missing_for_every_index():
    tas = make_tas()
    tas = tas.copy()
    tas[:, 0, 0] = np.nan
    for name, kwargs in BASE_INDICES:
        slice_mode = "year" if name == "max_consecutive_occurrence" else "month"
        out = compute(tas, name, slice_mode=slice_mode, **kwargs)
        assert bool(np.isnan(out.isel(lat=0, lon=0)).all()), name
        assert bool(out.isel(lat=1, lon=0).notnull().all()), name


# --- periods without events, dated outputs ------------------------------------


def _one_short_warm_spell() -> xr.DataArray:
    tas = make_tas()
    tas[:] = 280.0
    tas.loc[{"time": slice("2002-02-10", "2002-02-20")}] = 295.0
    return tas


@pytest.mark.parametrize("name", ["count_occurrences", "max_consecutive_occurrence"])
def test_a_period_without_any_event_counts_zero_and_is_not_missing(name):
    result = compute(_one_short_warm_spell(), name, threshold=">= 290 K")
    assert bool(result.notnull().all())
    assert float(result.sel(time="2002-02").max()) == 11.0
    assert float(result.sel(time="2002-01").max()) == 0.0
    assert float(result.sel(time="2002-03").max()) == 0.0


@pytest.mark.parametrize(
    ("name", "kwargs"),
    [
        ("maximum", {}),
        ("minimum", {}),
        ("count_occurrences", {"threshold": ">= 288 K"}),
        ("max_consecutive_occurrence", {"threshold": ">= 288 K"}),
    ],
)
def test_dated_results_keep_time_first_whatever_the_input_order(name, kwargs):
    def dims(da):
        result = icclim.index(
            index_name=name,
            in_files=da.to_dataset(),
            var_name="tas",
            slice_mode="month",
            date_event=True,
            out_file=None,
            **kwargs,
        )
        var = next(v for v in result.data_vars if not v.endswith("_thresholds"))
        dates = [c for c in result.coords if str(c).startswith("event_date")]
        assert dates
        return result[var].dims, {d: result[d].dims for d in dates}

    tas = make_tas()
    expected = dims(tas)
    actual = dims(tas.transpose("lat", "lon", "time"))
    assert expected[0][0] == "time"
    assert actual == expected


@pytest.mark.parametrize(
    ("name", "kwargs"),
    [
        ("sum", {}),
        ("maximum", {"date_event": True}),
        ("minimum", {"date_event": True}),
        ("count_occurrences", {"threshold": ">= 288 K", "date_event": True}),
        pytest.param(
            "max_consecutive_occurrence",
            {"threshold": ">= 288 K", "date_event": True},
            marks=pytest.mark.xfail(
                strict=False,
                reason="Event dates inherit the variable attributes, which breaks "
                "NetCDF encoding (fixed with the vectorized period reducers)",
            ),
        ),
    ],
)
def test_every_result_can_be_written_to_netcdf_and_read_back(name, kwargs, tmp_path):
    out_file = tmp_path / "out.nc"
    result = icclim.index(
        index_name=name,
        in_files=make_tas().to_dataset(),
        var_name="tas",
        slice_mode="month",
        out_file=str(out_file),
        **kwargs,
    )
    var = next(v for v in result.data_vars if not v.endswith("_thresholds"))
    with xr.open_dataset(out_file) as written:
        np.testing.assert_allclose(
            written[var].transpose(*result[var].dims).values,
            result[var].compute().values,
        )

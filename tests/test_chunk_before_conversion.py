"""
Data that is not backed by dask is chunked before the unit conversions.

``xclim.core.units.convert_units_to`` loads non-dask data eagerly. For a threshold, icclim
also converts the whole original data (not only ``time_range``), so an unchunked dataset
(``xr.open_dataset(path)``) or in-memory data needed the whole file in memory for a
threshold index. The results do not change.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core import input_parsing
from icclim.threshold.factory import build_threshold


def _write(path) -> str:
    time = pd.date_range("1990-01-01", "2001-12-31")
    rng = np.random.default_rng(11)
    phase = 2 * np.pi * (time.day_of_year.to_numpy() - 80) / 365.25
    tmax = 288 + 12 * np.sin(phase)[:, None, None] + rng.normal(0, 3, (len(time), 3, 4))
    tmin = tmax - 8 - rng.uniform(0, 2, tmax.shape)
    coords = {
        "time": time,
        "lat": ("lat", [10.0, 20.0, 30.0], {"units": "degrees_north"}),
        "lon": ("lon", [1.0, 2.0, 3.0, 4.0], {"units": "degrees_east"}),
    }
    ds = xr.Dataset(
        {
            "tasmax": xr.DataArray(
                tmax.astype("float32"),
                dims=("time", "lat", "lon"),
                attrs={"units": "K"},
            ),
            "tasmin": xr.DataArray(
                tmin.astype("float32"),
                dims=("time", "lat", "lon"),
                attrs={"units": "K"},
            ),
        },
        coords=coords,
    )
    out = str(path / "data.nc")
    ds.to_netcdf(out)
    return out


@pytest.fixture
def nc_path(tmp_path) -> str:
    return _write(tmp_path)


OPTIONS = {
    "out_file": None,
    "slice_mode": "year",
    "time_range": ["1996-01-01", "1999-12-31"],
    "logs_verbosity": "SILENT",
}
BASE = ["1990-01-01", "1994-12-31"]  # outside of the study period


def _su(ds):
    return icclim.su(ds, **OPTIONS).SU


def _tr(ds):
    return icclim.tr(ds, **OPTIONS).TR


def _count(ds):
    return icclim.count_occurrences(
        ds, var_name="tasmax", threshold="> 20 degC", **OPTIONS
    ).count_occurrences


def _count_between(ds):
    return icclim.count_occurrences(
        ds, var_name="tasmax", threshold="> 15 degC", **OPTIONS
    ).count_occurrences


def _tg(ds):
    return icclim.tx(ds, var_name="tasmax", **OPTIONS).TX


def _txx_date(ds):
    return icclim.txx(ds, date_event=True, **OPTIONS)["TXx"]


def _tx90p_base_outside_study_period(ds):
    return icclim.tx90p(ds, base_period_time_range=BASE, **OPTIONS).TX90p


def _tx90p_doy_per_threshold(ds):
    threshold = build_threshold(
        "> 90 doy_per", doy_window_width=5, reference_period=BASE
    )
    return icclim.count_occurrences(
        ds, var_name="tasmax", threshold=threshold, **OPTIONS
    ).count_occurrences


EXACT = {
    "SU": _su,
    "TR": _tr,
    "count": _count,
    "count-15": _count_between,
    "TX90p-base-outside": _tx90p_base_outside_study_period,
    "doy_per": _tx90p_doy_per_threshold,
}
FLOAT = {"TX": _tg}


def _forms(path: str) -> dict[str, object]:
    return {
        "str": path,
        "list": [path],
        "unchunked": xr.open_dataset(path),
        "numpy": xr.open_dataset(path).load(),
        "chunked": xr.open_dataset(path, chunks="auto"),
    }


@pytest.fixture
def without_the_early_chunk(monkeypatch: pytest.MonkeyPatch):
    """Restore the previous order: the unit conversions come before the chunking."""
    monkeypatch.setattr(input_parsing, "_chunk_before_conversion", lambda data: data)


@pytest.mark.parametrize("form", ["str", "list", "unchunked", "numpy", "chunked"])
@pytest.mark.parametrize("name", list(EXACT))
def test_counts_are_identical_with_and_without_the_early_chunk(
    nc_path: str, form: str, name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    compute = EXACT[name]
    with_it = compute(_forms(nc_path)[form]).compute()
    with monkeypatch.context() as ctx:
        ctx.setattr(input_parsing, "_chunk_before_conversion", lambda data: data)
        without_it = compute(_forms(nc_path)[form]).compute()
    np.testing.assert_array_equal(with_it.values, without_it.values)
    assert with_it.dtype == without_it.dtype
    assert with_it.attrs == without_it.attrs


@pytest.mark.parametrize("form", ["str", "list", "unchunked", "numpy", "chunked"])
@pytest.mark.parametrize("name", list(FLOAT))
def test_float_results_are_identical_within_rounding(
    nc_path: str, form: str, name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    compute = FLOAT[name]
    with_it = compute(_forms(nc_path)[form]).compute()
    with monkeypatch.context() as ctx:
        ctx.setattr(input_parsing, "_chunk_before_conversion", lambda data: data)
        without_it = compute(_forms(nc_path)[form]).compute()
    np.testing.assert_allclose(with_it.values, without_it.values, rtol=1e-6)
    assert with_it.attrs == without_it.attrs


@pytest.mark.parametrize("name", ["SU", "count", "TX90p-base-outside"])
def test_an_unchunked_dataset_gives_the_result_of_a_chunked_one(
    nc_path: str, name: str
) -> None:
    forms = _forms(nc_path)
    compute = EXACT[name]
    reference = compute(forms["chunked"]).compute()
    for form in ("str", "list", "unchunked", "numpy"):
        np.testing.assert_array_equal(compute(forms[form]).compute(), reference)


def test_a_date_result_is_identical(nc_path: str, monkeypatch) -> None:
    ds = xr.open_dataset(nc_path)
    with_it = _txx_date(ds).compute()
    with monkeypatch.context() as ctx:
        ctx.setattr(input_parsing, "_chunk_before_conversion", lambda data: data)
        without_it = _txx_date(xr.open_dataset(nc_path)).compute()
    np.testing.assert_array_equal(with_it.values, without_it.values)


def _longest_time_loaded(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Record the length of the time axis of every lazily indexed array that is loaded."""
    from xarray.core import indexing  # noqa: PLC0415

    lengths: list[int] = []
    original = indexing.MemoryCachedArray.get_duck_array

    def spy(self):
        if not isinstance(self.array, indexing.NumpyIndexingAdapter):
            lengths.append(self.array.shape[0])
        return original(self)

    monkeypatch.setattr(indexing.MemoryCachedArray, "get_duck_array", spy)
    return lengths


def test_a_threshold_index_does_not_load_the_years_outside_time_range(
    nc_path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    ds = xr.open_dataset(nc_path)
    lengths = _longest_time_loaded(monkeypatch)
    _su(ds).compute()
    study_period = 1461  # 1996 to 1999
    assert all(length <= study_period for length in lengths)


def test_without_the_early_chunk_the_whole_variable_is_loaded(
    nc_path: str, monkeypatch: pytest.MonkeyPatch, without_the_early_chunk
) -> None:
    """Documents the previous behavior that the early chunk removes."""
    ds = xr.open_dataset(nc_path)
    lengths = _longest_time_loaded(monkeypatch)
    _su(ds).compute()
    assert max(lengths) == ds.sizes["time"]


def test_dask_backed_data_is_untouched() -> None:
    data = xr.DataArray(
        np.zeros((10, 2, 2), dtype="float32"),
        dims=("time", "lat", "lon"),
    ).chunk({"time": 5})
    assert input_parsing._chunk_before_conversion(data) is data

"""
Guard for time-contiguous chunks of dask-backed inputs.

icclim keeps the chunks given by the user, except when the largest chunk is below 1/8
of dask's ``array.chunk-size`` (rechunked to "auto") or above 8 times it (the time axis
is rechunked to "auto" and a notice is printed once per process). Rechunking never
changes the values.
"""

from __future__ import annotations

import dask
import dask.array as dka
import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core import input_parsing
from icclim._core.input_parsing import (
    _chunk_eager_data,
    _largest_chunk_nbytes,
    _reset_time_rechunk_notice,
)

NOTICE = "icclim rechunked the time axis of the input"


@pytest.fixture(autouse=True)
def _fresh_notice():
    _reset_time_rechunk_notice()
    yield
    _reset_time_rechunk_notice()


def _array(chunks, shape=(10957, 128, 256), dtype="float32") -> xr.DataArray:
    return xr.DataArray(
        dka.zeros(shape, chunks=chunks, dtype=dtype),
        dims=("time", "lat", "lon"),
        coords={"time": pd.date_range("1985-01-01", periods=shape[0])},
    )


# With dask's default chunk-size (128 MiB): small below 16 MiB, large above 1 GiB.


def test_a_single_time_chunk_of_30_years_is_rechunked_with_a_notice(capsys) -> None:
    data = _array((10957, 128, 256))
    assert _largest_chunk_nbytes(data) > 2**30
    out = _chunk_eager_data(data)
    assert len(out.chunks[0]) > 1
    assert out.chunks[1] == data.chunks[1]
    assert out.chunks[2] == data.chunks[2]
    assert _largest_chunk_nbytes(out) <= 128 * 2**20
    assert sum(out.chunks[0]) == 10957
    assert capsys.readouterr().out.count(NOTICE) == 1


def test_a_single_time_chunk_of_165_years_is_rechunked(capsys) -> None:
    out = _chunk_eager_data(_array((60265, 128, 256), shape=(60265, 128, 256)))
    assert max(out.chunks[0]) <= 1024
    assert capsys.readouterr().out.count(NOTICE) == 1


@pytest.mark.parametrize("days", [365, 1024])
def test_chunks_between_the_limits_are_untouched(days: int, capsys) -> None:
    data = _array((days, 128, 256))
    assert _chunk_eager_data(data).chunks == data.chunks
    assert capsys.readouterr().out == ""


def test_small_chunks_keep_the_existing_rule(capsys) -> None:
    data = _array((1, 128, 256))
    out = _chunk_eager_data(data)
    assert out.chunks == data.chunk("auto").chunks
    assert max(out.chunks[0]) == 1024
    assert capsys.readouterr().out == ""


def test_numpy_data_is_untouched_by_the_guard(capsys) -> None:
    data = xr.DataArray(
        np.zeros((400, 8, 8), dtype="float32"),
        dims=("time", "lat", "lon"),
        coords={"time": pd.date_range("2000-01-01", periods=400)},
    )
    out = _chunk_eager_data(data)
    assert out.chunks is not None  # numpy data is chunked "auto", as before
    assert len(out.chunks[0]) == 1
    assert capsys.readouterr().out == ""


def test_the_notice_is_printed_once(capsys) -> None:
    _chunk_eager_data(_array((10957, 128, 256)))
    _chunk_eager_data(_array((10957, 128, 256)))
    assert capsys.readouterr().out.count(NOTICE) == 1


# Computations on a small case, with a small chunk-size so that the guard acts.


def _dataset(chunks) -> xr.Dataset:
    time = pd.date_range("2000-01-01", "2004-12-31")
    rng = np.random.default_rng(683)
    phase = 2 * np.pi * (time.day_of_year.to_numpy() - 80) / 365.25
    tmax = 15 + 12 * np.sin(phase)[:, None, None] + rng.normal(0, 3, (len(time), 4, 4))
    tmin = tmax - 8 - rng.uniform(0, 2, tmax.shape)
    coords = {"time": time, "lat": np.arange(4.0), "lon": np.arange(4.0)}
    return xr.Dataset(
        {
            "tasmax": xr.DataArray(
                tmax.astype("float32"),
                dims=("time", "lat", "lon"),
                coords=coords,
                attrs={"units": "degC"},
            ),
            "tasmin": xr.DataArray(
                tmin.astype("float32"),
                dims=("time", "lat", "lon"),
                coords=coords,
                attrs={"units": "degC"},
            ),
        }
    ).chunk(chunks)


OPTIONS = {"out_file": None, "slice_mode": "year", "logs_verbosity": "SILENT"}
SINGLE = {"time": -1, "lat": 4, "lon": 4}


def _su(ds):
    return icclim.su(ds, **OPTIONS).SU


def _txx_date(ds):
    return icclim.txx(ds, date_event=True, **OPTIONS)["TXx"]


def _tx90p(ds):
    return icclim.tx90p(
        ds, base_period_time_range=["2000-01-01", "2002-12-31"], **OPTIONS
    ).TX90p


def _count(ds):
    return icclim.count_occurrences(
        ds, var_name="tasmax", threshold="> 20 degC", **OPTIONS
    ).count_occurrences


def _rolling(ds):
    return icclim.max_of_rolling_sum(
        ds, var_name="tasmax", rolling_window_width=5, **OPTIONS
    ).max_of_rolling_sum


CASES = {"count": _count, "rolling": _rolling, "date": _txx_date, "percentile": _tx90p}


@pytest.mark.parametrize("name", list(CASES))
def test_results_are_identical_with_and_without_the_guard(
    name: str, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    compute = CASES[name]
    ds = _dataset(SINGLE)
    with dask.config.set({"array.chunk-size": "2KiB"}):
        monkeypatch.setattr(input_parsing, "_MAX_PRESERVED_CHUNK_MULTIPLE", 10**9)
        unguarded = compute(ds).compute()
        assert NOTICE not in capsys.readouterr().out
        monkeypatch.setattr(input_parsing, "_MAX_PRESERVED_CHUNK_MULTIPLE", 8)
        guarded = compute(ds).compute()
        assert NOTICE in capsys.readouterr().out
    if name == "count" or guarded.dtype.kind == "M":
        np.testing.assert_array_equal(guarded.values, unguarded.values)
    else:
        # float32 sums depend on the order of the chunks: 1e-5 is far above 1 ULP.
        np.testing.assert_allclose(
            guarded.values, unguarded.values, rtol=1e-5, equal_nan=True
        )


def test_two_indices_and_two_variables_print_one_notice(capsys) -> None:
    ds = _dataset(SINGLE)
    with dask.config.set({"array.chunk-size": "2KiB"}):
        icclim.dtr(ds, var_name=["tasmax", "tasmin"], **OPTIONS)
        _su(ds)
        _count(ds)
    assert capsys.readouterr().out.count(NOTICE) == 1


def test_small_chunks_are_still_rechunked_to_auto_without_notice(capsys) -> None:
    ds = _dataset({"time": 1, "lat": 4, "lon": 4})
    with dask.config.set({"array.chunk-size": "2KiB"}):
        value = _su(ds).compute()
    assert value.sizes["time"] == 5
    assert NOTICE not in capsys.readouterr().out


def test_chunks_between_the_limits_print_no_notice(capsys) -> None:
    ds = _dataset({"time": 100, "lat": 4, "lon": 4})
    with dask.config.set({"array.chunk-size": "2KiB"}):
        _su(ds).compute()
    assert NOTICE not in capsys.readouterr().out


def test_numpy_input_prints_no_notice(capsys) -> None:
    ds = _dataset(SINGLE).compute()
    with dask.config.set({"array.chunk-size": "2KiB"}):
        _su(ds).compute()
    assert NOTICE not in capsys.readouterr().out

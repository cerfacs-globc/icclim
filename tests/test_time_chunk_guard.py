"""
Notice for time-contiguous chunks of dask-backed inputs.

icclim keeps the chunks given by the user, except when the largest chunk is below 1/8
of dask's ``array.chunk-size`` (rechunked to "auto"). When the largest chunk is above 8
times ``array.chunk-size`` along time (a single time chunk, or a few very long ones),
the chunks are kept as they are and a notice advising other chunks is printed once per
process.
"""

from __future__ import annotations

import dask
import dask.array as dka
import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.input_parsing import (
    _chunk_eager_data,
    _largest_chunk_nbytes,
    _reset_time_chunks_notice,
)

NOTICE = "icclim: the input has one chunk, or very long chunks, along time"


@pytest.fixture(autouse=True)
def _fresh_notice():
    _reset_time_chunks_notice()
    yield
    _reset_time_chunks_notice()


def _array(chunks, shape=(10957, 128, 256), dtype="float32") -> xr.DataArray:
    return xr.DataArray(
        dka.zeros(shape, chunks=chunks, dtype=dtype),
        dims=("time", "lat", "lon"),
        coords={"time": pd.date_range("1985-01-01", periods=shape[0])},
    )


# With dask's default chunk-size (128 MiB): small below 16 MiB, large above 1 GiB.


@pytest.mark.parametrize("years", [30, 165])
def test_a_single_time_chunk_prints_the_notice_and_is_kept(years: int, capsys) -> None:
    n = int(years * 365.25)
    data = _array((n, 128, 256), shape=(n, 128, 256))
    assert _largest_chunk_nbytes(data) > 2**30
    out = _chunk_eager_data(data)
    assert out.chunks == data.chunks
    assert out is data
    printed = capsys.readouterr().out
    assert printed.count(NOTICE) == 1
    assert "GiB" in printed
    assert 'chunks="auto"' in printed
    assert 'chunks={"time": 1024}' in printed
    assert "select the period before chunking" in printed
    assert "1,855 s" in printed


def test_a_few_very_long_time_chunks_print_the_notice(capsys) -> None:
    data = _array((9000, 128, 256))
    out = _chunk_eager_data(data)
    assert out.chunks == data.chunks
    assert capsys.readouterr().out.count(NOTICE) == 1


@pytest.mark.parametrize("days", [365, 1024])
def test_chunks_between_the_limits_are_untouched_without_notice(
    days: int, capsys
) -> None:
    data = _array((days, 128, 256))
    assert _chunk_eager_data(data).chunks == data.chunks
    assert capsys.readouterr().out == ""


def test_small_chunks_keep_the_existing_rule_without_notice(capsys) -> None:
    data = _array((1, 128, 256))
    out = _chunk_eager_data(data)
    assert out.chunks == data.chunk("auto").chunks
    assert max(out.chunks[0]) == 1024
    assert capsys.readouterr().out == ""


def test_numpy_data_is_untouched_without_notice(capsys) -> None:
    data = xr.DataArray(
        np.zeros((400, 8, 8), dtype="float32"),
        dims=("time", "lat", "lon"),
        coords={"time": pd.date_range("2000-01-01", periods=400)},
    )
    out = _chunk_eager_data(data)
    assert len(out.chunks[0]) == 1
    assert capsys.readouterr().out == ""


def test_the_notice_is_printed_once(capsys) -> None:
    _chunk_eager_data(_array((10957, 128, 256)))
    _chunk_eager_data(_array((10957, 128, 256)))
    assert capsys.readouterr().out.count(NOTICE) == 1


# Computations on a small case, with a small chunk-size so that the notice applies.


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


def _count(ds):
    return icclim.count_occurrences(
        ds, var_name="tasmax", threshold="> 20 degC", **OPTIONS
    ).count_occurrences


def test_the_result_does_not_depend_on_the_notice(capsys) -> None:
    """The notice only advises: the result of a single chunk equals the in-memory one."""
    ds = _dataset(SINGLE)
    with dask.config.set({"array.chunk-size": "2KiB"}):
        chunked = _count(ds).compute()
    assert NOTICE in capsys.readouterr().out
    in_memory = _count(ds.compute()).compute()
    np.testing.assert_array_equal(chunked.values, in_memory.values)


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

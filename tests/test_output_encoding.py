from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim._core.model.netcdf_version import NetcdfVersionRegistry
from icclim.exception import InvalidIcclimArgumentError
from icclim.main import (
    OUTPUT_CHUNKS_ENV,
    OUTPUT_COMPRESSION_LEVEL_ENV,
    _build_output_encoding,
    _write_output_file,
)

if TYPE_CHECKING:
    from pathlib import Path


def _dataset() -> xr.Dataset:
    return xr.Dataset(
        {
            "index": (
                ("time", "lat", "lon"),
                np.zeros((100, 32, 32), dtype=np.float32),
            ),
        },
        coords={
            "time": pd.date_range("2000-01-01", periods=100),
            "lat": np.arange(32),
            "lon": np.arange(32),
        },
    ).chunk({"time": 20, "lat": 16, "lon": 16})


def test_output_encoding_defaults_remain_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(OUTPUT_COMPRESSION_LEVEL_ENV, raising=False)
    monkeypatch.delenv(OUTPUT_CHUNKS_ENV, raising=False)

    encoding = _build_output_encoding(
        _dataset(),
        input_time_encoding=None,
        netcdf_version=NetcdfVersionRegistry.NETCDF4,
    )

    assert encoding == {
        "time": {"units": "days since 1850-1-1", "dtype": np.float64},
    }


def test_output_encoding_supports_opt_in_compression_and_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(OUTPUT_COMPRESSION_LEVEL_ENV, "4")
    monkeypatch.setenv(OUTPUT_CHUNKS_ENV, '{"time": 10, "lat": 8}')

    encoding = _build_output_encoding(
        _dataset(),
        input_time_encoding=None,
        netcdf_version=NetcdfVersionRegistry.NETCDF4,
    )

    assert encoding["index"] == {
        "zlib": True,
        "complevel": 4,
        "chunksizes": (10, 8, 16),
    }


@pytest.mark.parametrize(
    ("name", "value"),
    [
        (OUTPUT_COMPRESSION_LEVEL_ENV, "10"),
        (OUTPUT_COMPRESSION_LEVEL_ENV, "fast"),
        (OUTPUT_CHUNKS_ENV, "not-json"),
        (OUTPUT_CHUNKS_ENV, '{"time": 0}'),
    ],
)
def test_output_encoding_rejects_invalid_environment(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: str,
) -> None:
    monkeypatch.setenv(name, value)

    with pytest.raises(InvalidIcclimArgumentError):
        _build_output_encoding(
            _dataset(),
            input_time_encoding=None,
            netcdf_version=NetcdfVersionRegistry.NETCDF4,
        )


def test_output_compression_requires_netcdf4(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(OUTPUT_COMPRESSION_LEVEL_ENV, "4")

    with pytest.raises(InvalidIcclimArgumentError, match="requires a NETCDF4"):
        _build_output_encoding(
            _dataset(),
            input_time_encoding=None,
            netcdf_version=NetcdfVersionRegistry.NETCDF3_CLASSIC,
        )


def test_opt_in_compression_reduces_repetitive_output_size(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uncompressed = tmp_path / "uncompressed.nc"
    compressed = tmp_path / "compressed.nc"
    dataset = _dataset()
    monkeypatch.delenv(OUTPUT_COMPRESSION_LEVEL_ENV, raising=False)
    monkeypatch.delenv(OUTPUT_CHUNKS_ENV, raising=False)
    _write_output_file(
        dataset,
        input_time_encoding=None,
        netcdf_version=NetcdfVersionRegistry.NETCDF4,
        file_path=str(uncompressed),
    )
    monkeypatch.setenv(OUTPUT_COMPRESSION_LEVEL_ENV, "4")
    monkeypatch.setenv(OUTPUT_CHUNKS_ENV, '{"time": 20, "lat": 16, "lon": 16}')
    _write_output_file(
        dataset,
        input_time_encoding=None,
        netcdf_version=NetcdfVersionRegistry.NETCDF4,
        file_path=str(compressed),
    )

    assert compressed.stat().st_size < uncompressed.stat().st_size
    with xr.open_dataset(compressed) as actual:
        xr.testing.assert_equal(actual, dataset.compute())

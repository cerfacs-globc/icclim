"""
Warnings of xarray that the user cannot act on do not reach the caller (issue #735).

icclim opens a list of paths with ``xarray.open_mfdataset``, and re-opens the files
for some bootstrap computations. Recent xarray versions warn about the coming change
of the defaults of ``data_vars`` and ``compat`` (icclim now gives the current values
explicitly) and about chunks that do not line up with the stored chunks of the files
(ignored around the re-open only). The other warnings still reach the user.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
import icclim.main as icclim_main
from icclim._core.generic import bootstrap_primitives
from icclim._core.input_parsing import read_dataset

BASE = ["2000-01-01", "2003-12-31"]
COMBINE_DEFAULTS = "In a future version of xarray the default value for"
CHUNK_SPLIT = "The specified chunks separate the stored chunks"


@pytest.fixture
def path_list(tmp_path) -> list[str]:
    """Two files with bounds variables and stored chunks that the re-open splits."""
    rng = np.random.default_rng(1)
    lat = np.arange(8.0)
    lon = np.arange(10.0)
    lat_bnds = np.stack([lat - 0.5, lat + 0.5], axis=1)
    paths = []
    for first_year in (2000, 2004):
        time = pd.date_range(f"{first_year}-01-01", f"{first_year + 3}-12-31")
        values = 290 + rng.normal(0, 3, (len(time), 8, 10)).astype("float32")
        ds = xr.Dataset(
            {
                "tasmax": (("time", "lat", "lon"), values, {"units": "K"}),
                "lat_bnds": (("lat", "bnds"), lat_bnds),
            },
            coords={"time": time, "lat": lat, "lon": lon},
        )
        ds["tasmax"].encoding["chunksizes"] = (400, 4, 5)
        path = tmp_path / f"tasmax_{first_year}.nc"
        ds.to_netcdf(path)
        paths.append(str(path))
    return paths


def _recorded(call) -> list[warnings.WarningMessage]:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        call()
    return caught


def _messages(caught, text: str) -> list[str]:
    return [str(w.message) for w in caught if text in str(w.message)]


def _su(files):
    return icclim.index(
        index_name="SU", in_files=files, var_name="tasmax", slice_mode="year"
    )


def _wsdi(files):
    return icclim.index(
        index_name="WSDI",
        in_files=files,
        var_name="tasmax",
        slice_mode="year",
        base_period_time_range=BASE,
    )


def test_path_list_does_not_show_the_xarray_combine_defaults_warning(path_list):
    assert _messages(_recorded(lambda: _su(path_list)), COMBINE_DEFAULTS) == []


def test_bootstrap_reopen_does_not_show_the_xarray_warnings(path_list, monkeypatch):
    reopened = []
    original = bootstrap_primitives._reopen_file_backed_study

    def spy(study):
        reopened.append(True)
        return original(study)

    monkeypatch.setattr(bootstrap_primitives, "_reopen_file_backed_study", spy)
    caught = _recorded(lambda: _wsdi(path_list))
    assert reopened, "the bootstrap did not re-open the files"
    assert _messages(caught, COMBINE_DEFAULTS) == []
    assert _messages(caught, CHUNK_SPLIT) == []


def test_chunk_split_warning_is_ignored_only_around_the_reopen(path_list):
    def direct_open():
        xr.open_mfdataset(path_list, chunks={"time": 365})

    per_open = len(_messages(_recorded(direct_open), CHUNK_SPLIT))
    assert per_open > 0

    def sandwich():
        direct_open()
        _wsdi(path_list)
        direct_open()

    # The warnings of the two direct opens are kept, the bootstrap adds none.
    assert len(_messages(_recorded(sandwich), CHUNK_SPLIT)) == 2 * per_open


def test_dataset_read_from_a_path_list_is_unchanged(path_list):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        before = xr.open_mfdataset(path_list, parallel=False, join="override")
    after = read_dataset(path_list)
    assert list(after.data_vars) == list(before.data_vars)
    xr.testing.assert_equal(after.drop_attrs(), before.drop_attrs())
    for name in before.variables:
        assert after[name].attrs == before[name].attrs
        assert after[name].dims == before[name].dims


def test_results_are_identical_to_those_of_the_previous_defaults(path_list):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        previous = xr.open_mfdataset(path_list, parallel=False, join="override")
        expected = _wsdi(previous)
        actual = _wsdi(path_list)
    xr.testing.assert_equal(actual, expected)
    assert list(actual.data_vars) == list(expected.data_vars)
    for name in expected.data_vars:
        assert actual[name].attrs == expected[name].attrs


def test_other_warnings_still_reach_the_user(path_list, monkeypatch):
    original = icclim_main._run_index_workflow
    message = "a warning raised by the computation"

    def patched(*args, **kwargs):
        warnings.warn(message, UserWarning, stacklevel=1)
        return original(*args, **kwargs)

    monkeypatch.setattr(icclim_main, "_run_index_workflow", patched)
    caught = _recorded(lambda: _su(path_list))
    assert len(_messages(caught, message)) == 1

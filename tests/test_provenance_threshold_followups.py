"""
Follow-ups of the provenance record of a threshold (#744).

The reference period of a threshold is recorded in one format (ISO), whatever the way
the threshold was built, and the file a threshold was read from is recorded.
"""

from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.calendar import percentile_doy

import icclim
from icclim import build_threshold

BASE = ["2000-01-01", "2002-12-31"]
ISO = ["2000-01-01", "2002-12-31"]


def _da() -> xr.DataArray:
    time = pd.date_range("2000-01-01", "2005-12-31")
    rng = np.random.default_rng(1)
    doy = time.day_of_year.to_numpy()
    values = 285 + 10 * np.sin(2 * np.pi * (doy - 110) / 365.25)[:, None, None]
    values = values + rng.normal(0, 3, (len(time), 2, 3))
    return xr.DataArray(
        values.astype("float32"),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0, 2.0], "lon": [1.0, 2.0, 3.0]},
        attrs={"units": "K"},
        name="tasmax",
    )


def _provenance(tmp_path, name: str = "out", **kwargs) -> tuple[dict, xr.Dataset]:
    out = tmp_path / f"{name}.nc"
    result = icclim.index(
        in_files=_da().to_dataset(),
        var_name="tasmax",
        slice_mode="year",
        out_file=str(out),
        **kwargs,
    )
    return json.loads((tmp_path / f"{name}.prov.json").read_text()), result


@pytest.fixture
def files(tmp_path):
    """A per-grid-point threshold file and a day-of-year percentile file."""
    basic = tmp_path / "thr.nc"
    xr.Dataset(
        {
            "tasmax_thr": (
                ("lat", "lon"),
                np.full((2, 3), 290.0, "float32"),
                {"units": "K"},
            )
        },
        coords={"lat": [1.0, 2.0], "lon": [1.0, 2.0, 3.0]},
    ).to_netcdf(basic)
    per = tmp_path / "per.nc"
    percentile_doy(_da().sel(time=slice("2000", "2002")), per=90).compute().to_dataset(
        name="tasmax_per"
    ).to_netcdf(per)
    return basic, per


# --- (a) one format for the reference period ------------------------------------

PERIODS = {
    "ISO strings": BASE,
    "tuple of strings": tuple(BASE),
    "datetimes": [dt.datetime(2000, 1, 1), dt.datetime(2002, 12, 31)],  # noqa: DTZ001
    "month-day-year strings": ["01-01-2000", "12-31-2002"],
}


@pytest.mark.parametrize("period", PERIODS.values(), ids=PERIODS.keys())
def test_reference_period_is_iso_whatever_the_way_it_is_given(tmp_path, period):
    prov, _ = _provenance(
        tmp_path,
        index_name="count_occurrences",
        threshold=build_threshold("> 90 doy_per", reference_period=period),
    )
    assert prov["inputs"][0]["threshold"]["reference_period"] == ISO
    assert prov["user_parameters"]["threshold"]["reference_period"] == ISO


@pytest.mark.parametrize(
    "period",
    [BASE, [dt.datetime(2000, 1, 1), dt.datetime(2002, 12, 31)]],  # noqa: DTZ001
    ids=["strings", "datetimes"],
)
def test_reference_period_of_a_standard_index_is_iso(tmp_path, period):
    prov, _ = _provenance(tmp_path, index_name="TX90p", base_period_time_range=period)
    assert prov["inputs"][0]["threshold"]["reference_period"] == ISO


def test_reference_period_is_iso_for_both_parts_of_a_bounded_threshold(tmp_path):
    prov, _ = _provenance(
        tmp_path,
        index_name="count_occurrences",
        threshold=build_threshold(
            "> 90 doy_per AND < 99 doy_per",
            reference_period=["01-01-2000", "12-31-2002"],
        ),
    )
    threshold = prov["inputs"][0]["threshold"]
    assert threshold["left_threshold"]["reference_period"] == ISO
    assert threshold["right_threshold"]["reference_period"] == ISO


def test_basic_threshold_has_no_reference_period(tmp_path):
    prov, _ = _provenance(
        tmp_path, index_name="count_occurrences", threshold=build_threshold("> 20 degC")
    )
    assert prov["inputs"][0]["threshold"]["reference_period"] is None


# --- (b) the file of a threshold read from a file -------------------------------


def _thresholds(files):
    basic, per = files
    return {
        "basic, path": (
            lambda: build_threshold(operator=">", value=str(basic), unit="K"),
            str(basic),
        ),
        "basic, Dataset": (
            lambda: build_threshold(
                operator=">", value=xr.open_dataset(basic), unit="K"
            ),
            str(basic),
        ),
        "percentile, path": (
            lambda: build_threshold(
                operator=">",
                value=str(per),
                threshold_var_name="tasmax_per",
                reference_period=BASE,
            ),
            str(per),
        ),
        "percentile, Dataset": (
            lambda: build_threshold(
                operator=">",
                value=xr.open_dataset(per),
                threshold_var_name="tasmax_per",
                reference_period=BASE,
            ),
            str(per),
        ),
        "percentile, DataArray": (
            lambda: build_threshold(
                operator=">",
                value=xr.open_dataset(per).tasmax_per,
                reference_period=BASE,
            ),
            str(per),
        ),
    }


KINDS = [
    "basic, path",
    "basic, Dataset",
    "percentile, path",
    "percentile, Dataset",
    "percentile, DataArray",
]


@pytest.mark.parametrize("kind", KINDS)
def test_file_of_a_threshold_is_recorded(tmp_path, files, kind):
    build, expected = _thresholds(files)[kind]
    prov, _ = _provenance(tmp_path, index_name="count_occurrences", threshold=build())
    assert prov["inputs"][0]["threshold"]["source_file"] == expected
    assert prov["user_parameters"]["threshold"]["source_file"] == expected
    assert build().to_dict()["source_file"] == expected


def test_no_file_for_a_threshold_that_is_not_read_from_a_file(tmp_path):
    for threshold in (
        build_threshold("> 290 K"),
        build_threshold("> 90 doy_per", reference_period=BASE),
        build_threshold(operator=">", value=[280.0, 290.0], unit="K"),
    ):
        assert threshold.source_file is None
        assert threshold.to_dict()["source_file"] is None


def test_file_name_does_not_change_the_equality_or_the_hash(files, tmp_path):
    _basic, per = files
    copy = tmp_path / "per_copy.nc"
    xr.open_dataset(per).load().to_netcdf(copy)
    first = build_threshold(
        operator=">",
        value=str(per),
        threshold_var_name="tasmax_per",
        reference_period=BASE,
    )
    second = build_threshold(
        operator=">",
        value=str(copy),
        threshold_var_name="tasmax_per",
        reference_period=BASE,
    )
    assert first.source_file != second.source_file
    assert first == second
    assert hash(first) == hash(second)


@pytest.mark.parametrize("kind", ["basic, path", "percentile, path"])
def test_output_metadata_does_not_mention_the_file(tmp_path, files, kind):
    build, expected = _thresholds(files)[kind]
    _, result = _provenance(tmp_path, index_name="count_occurrences", threshold=build())
    texts = [str(v) for v in result.attrs.values()]
    texts += [str(v) for var in result.data_vars for v in result[var].attrs.values()]
    assert not any(expected in text or "thr.nc" in text for text in texts)

"""
The provenance records a readable and stable description of each threshold (issue #718).

``user_parameters.threshold`` used to hold the default object text of the threshold
(``<... PercentileThreshold object at 0x...>``), which changes at every run.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold
from icclim.main import _serialize_provenance_value

BASE = ["2000-01-01", "2002-12-31"]


def _ds() -> xr.Dataset:
    time = pd.date_range("2000-01-01", "2004-12-31")
    rng = np.random.default_rng(1)
    values = (285 + rng.normal(0, 3, len(time))).astype("float32").reshape(-1, 1, 1)
    da = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0], "lon": [2.0]},
        attrs={"units": "K"},
    )
    return xr.Dataset({"tasmax": da, "tasmin": da - 5})


def _recorded(tmp_path, name="out", **kwargs):
    out = tmp_path / f"{name}.nc"
    icclim.index(in_files=_ds(), slice_mode="year", out_file=str(out), **kwargs)
    prov = json.loads((tmp_path / f"{name}.prov.json").read_text())
    return prov["user_parameters"]["threshold"]


def _count(threshold, tmp_path, name="out"):
    return _recorded(
        tmp_path,
        name,
        index_name="count_occurrences",
        var_name="tasmax",
        threshold=threshold,
    )


def test_percentile_threshold_is_described(tmp_path):
    thr = _count(build_threshold("> 90 doy_per", reference_period=BASE), tmp_path)
    assert thr["class"] == "PercentileThreshold"
    assert thr["operator"] == "gt"
    assert thr["percentiles"] == [90.0]
    assert thr["unit"] == "degC"
    assert thr["kind"] == "day_of_year_percentile_threshold"
    assert thr["reference_period"] == ["2000-01-01", "2002-12-31"]
    assert thr["doy_window_width"] == 5
    assert thr["interpolation"] == "median_unbiased"
    assert thr["only_leap_years"] is False
    assert thr["threshold_min_value"] is None
    assert "object at 0x" not in json.dumps(thr)


def test_basic_threshold_is_described(tmp_path):
    thr = _count(build_threshold("> 20 degC"), tmp_path)
    assert thr["class"] == "BasicThreshold"
    assert thr["operator"] == "gt"
    assert thr["value"] == 20.0
    assert thr["unit"] == "degC"
    assert thr["kind"] == "basic_threshold"


def test_bounded_threshold_has_link_and_both_parts(tmp_path):
    bounded = build_threshold("> 90 doy_per", reference_period=BASE) & build_threshold(
        "< 99 doy_per", reference_period=BASE
    )
    thr = _count(bounded, tmp_path)
    assert thr["class"] == "BoundedThreshold"
    assert thr["logical_link"] == "and"
    assert thr["left_threshold"]["percentiles"] == [90.0]
    assert thr["left_threshold"]["operator"] == "gt"
    assert thr["right_threshold"]["percentiles"] == [99.0]
    assert thr["right_threshold"]["operator"] == "lt"
    assert "object at 0x" not in json.dumps(thr)


def test_same_record_in_two_runs(tmp_path):
    def build():
        return build_threshold("> 90 doy_per", reference_period=BASE)

    assert _count(build(), tmp_path, "a") == _count(build(), tmp_path, "b")


def test_different_thresholds_give_different_records(tmp_path):
    a = _count(build_threshold("> 90 doy_per", reference_period=BASE), tmp_path, "a")
    b = _count(build_threshold("> 95 doy_per", reference_period=BASE), tmp_path, "b")
    assert a != b


def test_list_and_tuple_reference_period_give_same_record(tmp_path):
    as_list = build_threshold("> 90 doy_per", reference_period=list(BASE))
    as_tuple = build_threshold("> 90 doy_per", reference_period=tuple(BASE))
    assert _count(as_list, tmp_path, "a") == _count(as_tuple, tmp_path, "b")


def test_dictionary_and_list_of_thresholds_are_described():
    first = build_threshold("> 90 doy_per", reference_period=BASE)
    second = build_threshold("< 10 degC")
    record = _serialize_provenance_value({"tasmax": first, "tasmin": [second]})
    assert record["tasmax"]["percentiles"] == [90.0]
    assert record["tasmin"][0]["value"] == 10.0
    assert "object at 0x" not in json.dumps(record)


def test_indices_records_the_threshold_of_its_kwargs(tmp_path):
    out = tmp_path / "grp.nc"
    icclim.indices(
        "tasmax",
        in_files=_ds(),
        ignore_error=True,
        slice_mode="year",
        base_period_time_range=BASE,
        out_file=str(out),
        threshold=build_threshold("> 20 degC"),
    )
    prov = json.loads((tmp_path / "grp.prov.json").read_text())
    thr = prov["user_parameters"]["kwargs"]["threshold"]
    assert thr["class"] == "BasicThreshold"
    assert thr["value"] == 20.0


@pytest.mark.parametrize("query", ["> 20 degC", "> 90 doy_per"])
def test_to_dict_is_json_serialisable(query):
    thr = build_threshold(query, reference_period=BASE)
    json.dumps(thr.to_dict())

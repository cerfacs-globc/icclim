"""
The keyword arguments of ``build_threshold`` reach both parts of a bounded query (#725).

``build_threshold("> 90 doy_per AND < 99 doy_per", reference_period=...)`` used to drop
every keyword argument: the two percentile thresholds kept a reference period of
None, so a later computation failed with "needs a base period". The list form
(``thresholds=[...]``) passed them correctly.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold

REF = ["2000-01-01", "2002-12-31"]
QUERY = "> 90 doy_per AND < 99 doy_per"
PARTS = ["> 90 doy_per", "< 99 doy_per"]

# keyword, value, attribute of the percentile thresholds, expected attribute value
KWARGS = [
    ("reference_period", REF, "reference_period", tuple(REF)),
    ("doy_window_width", 7, "doy_window_width", 7),
    ("interpolation", "linear", "interpolation", "linear"),
    ("only_leap_years", True, "only_leap_years", True),
    ("threshold_min_value", "1 mm/day", "threshold_min_value", 1.0),
]


def _value(threshold, attribute):
    value = getattr(threshold, attribute)
    if attribute == "interpolation":
        return value.name
    if attribute == "threshold_min_value":
        # compared by value: the text of a pint quantity depends on the formatting
        # that other code set on the unit registry
        return float(value.to("mm/day").magnitude)
    return value


def _ds() -> xr.Dataset:
    time = pd.date_range("2000-01-01", "2005-12-31")
    rng = np.random.default_rng(1)
    values = (290 + rng.normal(0, 3, len(time))).astype("float32")
    da = xr.DataArray(
        values.reshape(-1, 1, 1),
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0], "lon": [2.0]},
        attrs={"units": "K"},
    )
    return xr.Dataset({"tasmax": da})


@pytest.mark.parametrize(
    ("keyword", "value", "attribute", "expected"),
    KWARGS,
    ids=[k[0] for k in KWARGS],
)
def test_each_keyword_reaches_both_parts_of_a_bounded_query(
    keyword, value, attribute, expected
):
    bounded = build_threshold(QUERY, **{keyword: value})
    assert _value(bounded.left_threshold, attribute) == expected
    assert _value(bounded.right_threshold, attribute) == expected


@pytest.mark.parametrize(
    ("keyword", "value", "attribute", "expected"),
    KWARGS,
    ids=[k[0] for k in KWARGS],
)
def test_the_query_form_gives_the_same_parts_as_the_list_form(
    keyword, value, attribute, expected
):
    from_query = build_threshold(QUERY, **{keyword: value})
    from_list = build_threshold(
        thresholds=PARTS, logical_link="and", **{keyword: value}
    )
    assert from_query.left_threshold == from_list.left_threshold
    assert from_query.right_threshold == from_list.right_threshold
    assert from_query.logical_link == from_list.logical_link


def test_exact_call_of_the_issue_can_be_computed():
    threshold = build_threshold(QUERY, reference_period=REF)
    result = icclim.index(
        index_name="count_occurrences",
        in_files=_ds(),
        var_name="tasmax",
        slice_mode="year",
        threshold=threshold,
    )
    assert "count_occurrences" in result


def test_result_is_the_same_with_the_query_form_and_the_list_form():
    kwargs = {"reference_period": REF, "doy_window_width": 7}
    from_query = build_threshold(QUERY, **kwargs)
    from_list = build_threshold(thresholds=PARTS, logical_link="and", **kwargs)

    def count(threshold):
        return icclim.index(
            index_name="count_occurrences",
            in_files=_ds(),
            var_name="tasmax",
            slice_mode="year",
            threshold=threshold,
        ).count_occurrences

    xr.testing.assert_equal(count(from_query), count(from_list))


def test_basic_part_of_a_mixed_query_is_unchanged():
    bounded = build_threshold(
        "> 90 doy_per AND > 20 degC", reference_period=REF, doy_window_width=7
    )
    assert bounded.left_threshold.reference_period == tuple(REF)
    assert bounded.left_threshold.doy_window_width == 7
    assert bounded.right_threshold == build_threshold("> 20 degC")


def test_defaults_are_unchanged_without_keywords():
    bounded = build_threshold(QUERY)
    for part in (bounded.left_threshold, bounded.right_threshold):
        assert part.reference_period is None
        assert part.doy_window_width == 5
        assert part.interpolation.name == "median_unbiased"
        assert part.only_leap_years is False
        assert part.threshold_min_value is None


def test_provenance_records_the_keywords_of_a_bounded_query(tmp_path):
    out = tmp_path / "out.nc"
    icclim.index(
        index_name="count_occurrences",
        in_files=_ds(),
        var_name="tasmax",
        slice_mode="year",
        threshold=build_threshold(QUERY, reference_period=REF, doy_window_width=7),
        out_file=str(out),
    )
    prov = json.loads((tmp_path / "out.prov.json").read_text())
    threshold = prov["user_parameters"]["threshold"]
    assert threshold["class"] == "BoundedThreshold"
    for side in ("left_threshold", "right_threshold"):
        assert threshold[side]["reference_period"] == REF
        assert threshold[side]["doy_window_width"] == 7

"""
The thresholds can be hashed, and equal thresholds have the same hash (issue #716).

``hash(threshold)`` used to raise "TypeError: unhashable type: 'Operator'": the
operator, the logical link and the quantile interpolation are dataclasses with
``eq=True``, which are unhashable unless they define ``__hash__``.
"""

from __future__ import annotations

import numpy as np
import pytest
import xarray as xr

from icclim import build_threshold
from icclim._core.generic.threshold.basic import BasicThreshold
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.operator import OperatorRegistry
from icclim._core.model.quantile_interpolation import QuantileInterpolationRegistry
from icclim.dcsc.registry import DcscIndexRegistry
from icclim.ecad.registry import EcadIndexRegistry

REFERENCE = ["2000-01-01", "2004-12-31"]

QUERIES = {
    "basic": "> 25 degC",
    "doy percentile": "> 90 doy_per",
    "period percentile": "> 75 period_per",
    "bounded and": ">= 18 degC AND <= 30 degC",
    "bounded or": "< 0 degC OR > 35 degC",
}


def _build(query: str):
    if "per" in query and "AND" not in query and "OR" not in query:
        return build_threshold(query, reference_period=REFERENCE)
    return build_threshold(query)


@pytest.mark.parametrize("query", QUERIES.values(), ids=QUERIES.keys())
def test_a_threshold_can_be_hashed(query: str) -> None:
    assert isinstance(hash(_build(query)), int)


def test_the_threshold_classes_are_the_ones_checked() -> None:
    classes = {type(_build(query)) for query in QUERIES.values()}
    assert classes == {BasicThreshold, PercentileThreshold, BoundedThreshold}


@pytest.mark.parametrize("query", QUERIES.values(), ids=QUERIES.keys())
def test_equal_thresholds_have_the_same_hash(query: str) -> None:
    first, second = _build(query), _build(query)
    assert first is not second
    assert first == second
    assert hash(first) == hash(second)


def test_a_percentile_threshold_with_a_list_and_a_tuple_has_the_same_hash() -> None:
    from_list = build_threshold("> 90 doy_per", reference_period=REFERENCE)
    from_tuple = build_threshold("> 90 doy_per", reference_period=tuple(REFERENCE))
    assert from_list == from_tuple
    assert hash(from_list) == hash(from_tuple)


def test_a_percentile_threshold_with_a_minimum_value_can_be_hashed() -> None:
    first = build_threshold(
        "> 95 period_per", threshold_min_value="1 mm/day", reference_period=REFERENCE
    )
    second = build_threshold(
        "> 95 period_per", threshold_min_value="1 mm/day", reference_period=REFERENCE
    )
    assert first == second
    assert hash(first) == hash(second)


def test_a_threshold_of_values_is_hashed_with_its_dimensions() -> None:
    values = xr.DataArray(
        np.full((2, 3), 300.0), dims=("lat", "lon"), attrs={"units": "K"}
    )
    first = build_threshold(operator=">", value=values, unit="K")
    second = build_threshold(operator=">", value=values.copy(), unit="K")
    assert first == second
    assert hash(first) == hash(second)


def test_different_thresholds_are_different_keys() -> None:
    thresholds = [_build(query) for query in QUERIES.values()]
    assert len(set(thresholds)) == len(thresholds)
    assert len({hash(t) for t in thresholds}) > 1


@pytest.mark.parametrize("query", QUERIES.values(), ids=QUERIES.keys())
def test_a_threshold_is_a_dictionary_key_and_a_set_member(query: str) -> None:
    threshold = _build(query)
    by_threshold = {threshold: "found"}
    assert by_threshold[_build(query)] == "found"
    members = {threshold, _build(query)}
    assert len(members) == 1
    assert _build(query) in members


def test_the_operator_the_logical_link_and_the_interpolation_can_be_hashed() -> None:
    for item in (
        OperatorRegistry.GREATER,
        LogicalLinkRegistry.LOGICAL_AND,
        QuantileInterpolationRegistry.MEDIAN_UNBIASED,
    ):
        assert hash(item) == hash(item)
    assert hash(OperatorRegistry.GREATER) != hash(OperatorRegistry.LOWER)
    assert OperatorRegistry.lookup(">") == OperatorRegistry.GREATER
    assert hash(OperatorRegistry.lookup(">")) == hash(OperatorRegistry.GREATER)


def test_the_equality_of_thresholds_is_not_changed() -> None:
    assert _build("> 25 degC") != _build("> 30 degC")
    assert _build("> 90 doy_per") != _build("> 91 doy_per")
    assert build_threshold("> 90 doy_per", reference_period=REFERENCE) != (
        build_threshold("> 90 doy_per", reference_period=["1990-01-01", "1999-12-31"])
    )
    assert _build(QUERIES["bounded and"]) != _build(QUERIES["bounded or"])


def _hashable_indices():
    for index in [*EcadIndexRegistry.values(), *DcscIndexRegistry.values()]:
        try:
            hash(index.indicator)
        except TypeError:
            # xclim proxies that define ``__hash__ = None`` on purpose
            continue
        yield index


@pytest.mark.parametrize("index", list(_hashable_indices()), ids=lambda i: i.short_name)
def test_an_index_with_a_threshold_can_be_hashed(index) -> None:
    assert hash(index) == hash(index.clone())
    assert index == index.clone()

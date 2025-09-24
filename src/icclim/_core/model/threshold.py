"""Threshold abstract class and ThresholdBuilderInput type."""

from __future__ import annotations

import abc
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, TypedDict, Union

import xarray as xr
from xarray import DataArray, Dataset

from icclim._core.model.logical_link import LogicalLink, LogicalLinkRegistry

if TYPE_CHECKING:
    from datetime import datetime

    import jinja2
    import pint

    from icclim._core.generic.threshold.bounded import BoundedThreshold
    from icclim._core.generic.threshold.threshold_templates import (
        ThresholdMetadata,
    )
    from icclim._core.model.operator import Operator
    from icclim._core.model.quantile_interpolation import (
        QuantileInterpolation,
    )


ThresholdValueType = Union[
    str,
    float,
    int,
    Dataset,
    DataArray,
    Sequence[float | int | str],
    None,
]


class ThresholdBuilderInput(TypedDict, total=False):
    """Threshold building configuration.

    Data transfert object mapping all possible configuration to build any threshold.
    """

    operator: Operator
    value: ThresholdValueType
    unit: str | None
    threshold_var_name: str | None
    initial_query: str | None
    threshold_min_value: pint.Quantity | None
    offset: pint.Quantity | None
    # percentile conf:
    doy_window_width: int | None
    only_leap_years: bool | None
    interpolation: str | QuantileInterpolation | None
    reference_period: Sequence[datetime | str] | None
    # bounded conf:
    thresholds: (
        tuple[
            ThresholdBuilderInput | Threshold,
            ThresholdBuilderInput | Threshold,
        ]
        | None
    )
    logical_link: LogicalLink


class Threshold(abc.ABC):
    """
    Abstract class for all thresholds.

    See :ref:`generic_indices_recipes` for how to use custom thresholds.
    """

    operator: Operator | str
    value: ThresholdValueType
    unit: str | None = None
    initial_query: str | None
    threshold_min_value: pint.Quantity | None = None
    threshold_var_name: str | None
    prepare: Callable | None = None
    is_ready: bool | None = None

    @abc.abstractmethod
    def format_metadata(
        self,
        *,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
        **kwargs,
    ) -> ThresholdMetadata:
        """Get a dictionary of standardized threshold metadata."""
        ...

    @abc.abstractmethod
    def __eq__(self, other: Threshold) -> bool:
        """Check if two Threshold are equal."""
        ...

    def __and__(self, other: Threshold) -> BoundedThreshold:
        """Build a BoundedThreshold from two existing Threshold with a "AND" LogicalLink."""  # noqa: E501
        from icclim._core.generic.threshold.bounded import BoundedThreshold

        return BoundedThreshold(
            thresholds=[self, other],
            logical_link=LogicalLinkRegistry.LOGICAL_AND,
            initial_query=None,
        )

    def __or__(self, other: Threshold) -> BoundedThreshold:
        """Build a BoundedThreshold from two existing Threshold with a "OR" LogicalLink."""  # noqa: E501
        from icclim._core.generic.threshold.bounded import BoundedThreshold

        return BoundedThreshold(
            thresholds=[self, other],
            logical_link=LogicalLinkRegistry.LOGICAL_OR,
            initial_query=None,
        )

    @abc.abstractmethod
    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,
    ) -> DataArray:
        """
        Compute the exceedance of the threshold.

        For example, if the threshold is 10 and the comparison_data is [5, 10, 15],
        with a ">" operator, the exceedance will be [False, False, True].
        The operator can be overridden by `override_op`.
        This is needed when self.operator is REACH.

        Parameters
        ----------
        comparison_data: xr.DataArray
            Data that must be compared to self threshold
        override_op: Callable[[DataArray, DataArray], DataArray] | None
            Operator to override self.operator compute function.
            Optional.
        kwargs:
            Keyword arguments passed to the concrete `compute` implementations.
            This makes the `compute` interface contract unreliable.
            So we accept to not respected LSP here.
        """
        ...

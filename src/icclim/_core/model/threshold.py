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

    def to_dict(self) -> dict[str, Any]:
        """
        Describe the threshold with a structured, JSON-serialisable dictionary.

        The description is stable: the same threshold gives the same dictionary in
        every run (no memory address, no timestamp). It is meant for the provenance
        record, ``repr`` and ``str`` are not changed.
        """
        from icclim._core.generic.bootstrap_capability import (  # noqa: PLC0415
            classify_threshold_kind,
        )

        operator = self.operator
        threshold_min_value = self.threshold_min_value
        return {
            "class": type(self).__name__,
            "operator": getattr(operator, "short_name", operator),
            "kind": str(getattr(classify_threshold_kind(self), "value", None)),
            "value": _value_description(self),
            "unit": self.unit,
            "threshold_min_value": None
            if threshold_min_value is None
            else str(threshold_min_value),
            "initial_query": self.initial_query,
            "threshold_var_name": self.threshold_var_name,
        }

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
    def __eq__(self, other: object) -> bool:
        """Check if two Threshold are equal."""
        ...

    @abc.abstractmethod
    def __hash__(self) -> int:
        """Return the hash of the threshold."""
        ...

    def __and__(self, other: Threshold) -> BoundedThreshold:
        """Build a BoundedThreshold from two existing Threshold with a "AND" LogicalLink."""
        from icclim._core.generic.threshold.bounded import (  # noqa: PLC0415
            BoundedThreshold,
        )

        return BoundedThreshold(
            thresholds=[self, other],
            logical_link=LogicalLinkRegistry.LOGICAL_AND,
            initial_query=None,
        )

    def __or__(self, other: Threshold) -> BoundedThreshold:
        """Build a BoundedThreshold from two existing Threshold with a "OR" LogicalLink."""
        from icclim._core.generic.threshold.bounded import (  # noqa: PLC0415
            BoundedThreshold,
        )

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


def _value_description(
    threshold: Threshold,
) -> float | list[float] | dict[str, Any] | None:
    """Value of a threshold as plain numbers, or a summary of its array."""
    if getattr(threshold, "is_ready", True) is False:
        initial_value = getattr(threshold, "initial_value", None)
        return None if initial_value is None else [float(v) for v in initial_value]
    value = getattr(threshold, "value", None)
    if not isinstance(value, DataArray):
        return None
    if value.ndim == 0:
        return float(value.values)
    if value.ndim == 1 and value.dims == ("threshold",):
        return [float(v) for v in value.values]
    return {"kind": "DataArray", "dims": list(value.dims), "shape": list(value.shape)}

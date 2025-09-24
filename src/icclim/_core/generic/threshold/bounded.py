"""
BoundedThreshold module.

A `BoundedThreshold` is a composite threshold that binds two other thresholds
for example "> 95 doy_per AND >= 30 deg_C".
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from icclim._core.generic.threshold.threshold_templates import (
    EN_THRESHOLD_TEMPLATE,
    ThresholdMetadata,
)
from icclim._core.model.threshold import (
    Threshold,
    ThresholdBuilderInput,
)
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    from collections.abc import Sequence

    import jinja2
    import xarray as xr
    from xarray import DataArray

    from icclim._core.model.logical_link import LogicalLink


class BoundedThreshold(Threshold):
    """
    Threshold that binds two other thresholds (e.g. "> 95 doy_per AND >= 30 deg_C").

    The logical link must be either "and" or "or".
    """

    left_threshold: Threshold
    right_threshold: Threshold
    logical_link: LogicalLink

    @property
    def unit(self) -> str | None:
        """
        The unit of the bounded threshold.

        Returns
        -------
        str | None
            The unit of the threshold if both thresholds have the same unit,
            otherwise None.
        """
        if self.left_threshold.unit == self.right_threshold.unit:
            return self.left_threshold.unit
        return None

    @unit.setter
    def unit(self, unit: str) -> None:
        """
        Set the unit on each of the thresholds.

        Parameters
        ----------
        unit : str
            The unit to set.

        Notes
        -----
        This setter will attempt a unit conversion using units found in xclim's pint
        registry.
        """
        self.left_threshold.unit = unit
        self.right_threshold.unit = unit

    def __init__(
        self,
        thresholds: Sequence[Threshold | str | ThresholdBuilderInput],
        logical_link: LogicalLink,
        initial_query: str | None,
        **kwargs,  # noqa: ARG002
    ) -> None:
        if len(thresholds) != 2:
            msg = (
                f"BoundedThreshold can only be built on 2 thresholds, {len(thresholds)}"
                f" were found."
            )
            raise InvalidIcclimArgumentError(msg)
        self.left_threshold = self._build_thresh(thresholds[0])
        self.right_threshold = self._build_thresh(thresholds[1])
        if self.left_threshold == self.right_threshold:
            msg = (
                f"BoundedThreshold must be built on 2 **different** thresholds, here"
                f" both were {self.left_threshold.initial_query}"
            )
            raise InvalidIcclimArgumentError(msg)
        self.logical_link = logical_link
        self.initial_query = initial_query

    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,
    ) -> DataArray:
        """
        Compute the threshold exceedance value.

        Uses the logical link to combine the result of both thresholds.

        Parameters
        ----------
        comparison_data : xr.DataArray
            The data array to compare with the threshold value.
        override_op : Callable[[DataArray, DataArray], DataArray] | None, optional
            A custom override function to compute the threshold value.
            If provided, this function will be used instead of the default operator.
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        DataArray
            The computed threshold value.

        Notes
        -----
        If `override_op` is not None, the `override_op` function will be used to
        compute the thresholds exceedances on both thresholds.
        """
        left_res = self.left_threshold.compute(
            comparison_data,
            override_op=override_op,
            **kwargs,
        )
        right_res = self.right_threshold.compute(
            comparison_data,
            override_op=override_op,
            **kwargs,
        )
        return self.logical_link.compute([left_res, right_res])

    def format_metadata(
        self,
        *,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
        **kwargs,
    ) -> ThresholdMetadata:
        """
        Generate the metadata for the bounded threshold.

        These metadata are used to fill the generic template.

        Parameters
        ----------
        jinja_scope : dict
            The jinja scope, it contains the variables to be used in the jinja template.
        jinja_env : jinja2.Environment
            The jinja environment, it contains the jinja rendering engine.
        **kwargs
            Additional keyword arguments, ignored for compatibility with other
            `format_metadata` methods.

        Returns
        -------
        ThresholdMetadata
            The metadata for the threshold.

        """
        templates = self._get_metadata_templates()
        conf = {
            "left_threshold": self.left_threshold.format_metadata(
                jinja_scope=jinja_scope,
                jinja_env=jinja_env,
                **kwargs,
            ),
            "logical_link": self.logical_link,
            "right_threshold": self.right_threshold.format_metadata(
                jinja_scope=jinja_scope,
                jinja_env=jinja_env,
                **kwargs,
            ),
        }
        conf.update(jinja_scope)
        return {
            k: jinja_env.from_string(v, globals=conf).render()
            for k, v in templates.items()
        }

    def __eq__(self, other: BoundedThreshold) -> bool:
        """
        Check if the comparison threshold is equivalent to `self`.

        BoundedThreshold equality is based on the reflexive property of logical links (
        and/or).
        Thus, the left_threshold of `self` can be either equal to the
        left_threshold or the right_threshold of `other`.
        Same goes for right_threshold of self.

        Parameters
        ----------
        other : BoundedThreshold
            The comparison threshold.

        Returns
        -------
            True if the the comparison threshold `other` is equivalent to `self`.
        """
        return (
            isinstance(other, BoundedThreshold)
            and self.initial_query == other.initial_query
            and (self.left_threshold in (other.left_threshold, other.right_threshold))
            and (self.right_threshold in (other.left_threshold, other.right_threshold))
            and self.logical_link == other.logical_link
        )

    def _build_thresh(
        self,
        thresh_input: Threshold | str | ThresholdBuilderInput,
    ) -> Threshold:
        from icclim.threshold.factory import build_threshold

        if isinstance(thresh_input, Threshold):
            return thresh_input
        if isinstance(thresh_input, str):
            return build_threshold(thresh_input)
        return build_threshold(**thresh_input)

    def _get_metadata_templates(self) -> ThresholdMetadata:
        return EN_THRESHOLD_TEMPLATE["bounded_threshold"]

"""BasicThreshold module."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import numpy as np
import xarray as xr
from xarray import DataArray, Dataset
from xclim.core.units import convert_units_to, str2pint

from icclim._core.constants import (
    UNITS_KEY,
)
from icclim._core.generic.threshold.threshold_templates import (
    EN_THRESHOLD_TEMPLATE,
    ThresholdMetadata,
)
from icclim._core.input_parsing import (
    get_dataarray_from_dataset,
    is_dataset_path,
)
from icclim._core.model.threshold import (
    Threshold,
    ThresholdValueType,
)
from icclim._core.utils import is_number_sequence
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    import jinja2
    import pint

    from icclim._core.model.operator import Operator


class BasicThreshold(Threshold):
    """
    Pint ready simple threshold (e.g. "> 300 K").

    Parameters
    ----------
    operator : Operator or str
        The operator used for the threshold comparison.
    value : ThresholdValueType
        The threshold value(s) to compare against.
    unit : str, optional
        The unit of the threshold value(s).
    initial_query : str, optional
        The initial query used to build the threshold.
    threshold_min_value : pint.Quantity, optional
        The minimum value for the threshold.
    threshold_var_name : str, optional
        The name of the threshold variable.
    offset : pint.Quantity, optional
        The offset to be applied to the threshold value(s).

    Notes
    -----
    When built, `value` is always turned into a `xarray.DataArray`.
    The `unit` property has a setter that will attempt a unit conversion using
    units found in xclim's pint registry.

    The actual unit can be overridden by modifying `value.attrs["units"]` directly.
    """

    @property
    def unit(self) -> str | None:
        """The unit of the threshold value(s)."""
        if self.value is not None:
            return self.value.attrs[UNITS_KEY]
        return self._unit

    @unit.setter
    def unit(self, unit: str) -> None:
        """
        Set the unit of the threshold value(s).

        Parameters
        ----------
        unit : str
            The unit to set.

        Notes
        -----
        This setter will attempt a unit conversion using units found in xclim's pint
        registry.
        """
        if self.value is not None:
            if self.value.attrs.get(UNITS_KEY, None) is not None and unit is not None:
                self.value = convert_units_to(self.value, unit, context="hydro")
            self.value.attrs[UNITS_KEY] = unit
        else:
            self._unit = unit

    def __init__(
        self,
        operator: Operator | str,
        value: ThresholdValueType,
        unit: str | None = None,
        initial_query: str | None = None,
        threshold_min_value: pint.Quantity | None = None,
        threshold_var_name: str | None = None,
        offset: pint.Quantity | None = None,
        **kwargs,  # noqa: ARG002
    ) -> None:
        """
        Initialize a Threshold object.

        Parameters
        ----------
        operator : Operator or str
            The operator used for comparison. Can be an Operator object or a string
            representation of the operator.
        value : ThresholdValueType
            The threshold value. Can be a scalar, a sequence of numbers, a Dataset, or a
            DataArray.
        unit : str or None, optional
            The unit of the threshold value. Defaults to None.
        initial_query : str or None, optional
            The initial query string. Defaults to None.
        threshold_min_value : pint.Quantity or None, optional
            The minimum threshold value. Defaults to None.
        threshold_var_name : str or None, optional
            The name of the threshold variable. Defaults to None.
        offset : pint.Quantity or None, optional
            The offset value. Defaults to None.
        **kwargs
            Additional keyword arguments.

        Raises
        ------
        InvalidIcclimArgumentError
            If threshold_min_value is used with scalar thresholds.
        NotImplementedError
            If the threshold value type is not supported.

        """
        if (
            is_number_sequence(value) or isinstance(value, (float, int))
        ) and threshold_min_value is not None:
            msg = "Cannot use threshold_min_value with scalar thresholds."
            raise InvalidIcclimArgumentError(msg)
        if is_dataset_path(value) or isinstance(value, Dataset):
            # e.g. build_threshold(">", "thresh*.nc" , "degC") noqa: ERA001
            thresh_da = get_dataarray_from_dataset(threshold_var_name, value)
            self.value = self._prepare_da(thresh_da, threshold_min_value, offset, unit)
            unit = self.value.attrs.get(UNITS_KEY, None)
        elif isinstance(value, DataArray):
            self.value = self._prepare_da(value, threshold_min_value, offset, unit)
            unit = self.value.attrs.get(UNITS_KEY, None)
        elif is_number_sequence(value):
            self.value = DataArray(
                name="threshold",
                data=value,
                attrs={UNITS_KEY: unit},
                dims="threshold",
                coords={"threshold": value},
            )
        elif isinstance(value, (float, int)):
            # e.g. build_threshold(">", [2,3,4], "degC") noqa: ERA001
            self.value = DataArray(
                name="threshold",
                data=value,
                attrs={UNITS_KEY: unit},
            )
        elif value is None:
            self.prepare = self._partial_prepare_da(threshold_min_value, offset, unit)
            self.is_ready = False
            self.value = None
        else:
            msg = f"Cannot build threshold from a {type(value)}."
            raise NotImplementedError(msg)
        self.operator = operator
        self.unit = unit
        self.is_ready = True
        self.threshold_var_name = threshold_var_name
        self.initial_query = initial_query
        self.offset = offset
        if threshold_min_value is not None and threshold_min_value.dimensionless:
            self.threshold_min_value = float(threshold_min_value.m) * str2pint(unit)
        else:
            self.threshold_min_value = threshold_min_value

    def __eq__(self, other: object) -> bool:
        """Check if two BasicThreshold objects are equal."""
        return (
            isinstance(other, BasicThreshold)
            and self.operator == other.operator
            and self.value == other.value
            and self.unit == other.unit
            and self.initial_query == other.initial_query
            and self.threshold_min_value == other.threshold_min_value
        )

    def __str__(self) -> str:
        """Return a string representation of the threshold."""
        return f"""Threshold:
        Operator: {self.operator}
        Value: {self.value}
        Unit: {self.unit}
        Initial Query: {self.initial_query}
        Threshold Min Value: {self.threshold_min_value}
        Offset: {self.offset}
        """

    def format_metadata(
        self,
        jinja_scope: dict[str, Any],
        jinja_env: jinja2.Environment,
        **kwargs,  # noqa: ARG002
    ) -> ThresholdMetadata:
        """
        Generate the metadata for the threshold.

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
            "operator": self.operator,
            "unit": self.unit,
            "threshold_min_value": self.threshold_min_value,
            "has_offset": self.offset is not None,
            "offset": self.offset,
            "must_run_bootstrap": True,
            "value": self.value,
        }
        conf.update(jinja_scope)
        return {
            k: jinja_env.from_string(v, globals=conf).render()
            for k, v in templates.items()
        }

    def compute(
        self,
        comparison_data: xr.DataArray,
        override_op: Callable[[DataArray, DataArray], DataArray] | None = None,
        **kwargs,  # noqa: ARG002
    ) -> DataArray:
        """
        Compute the threshold exceedance value.

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
        compute the threshold exceedance using the `comparison_data` and `self.value`
        as inputs.
        If `override_op` is None, the default operator defined in `self.operator`
        will be used to compute the threshold exceedance.

        """
        if override_op is not None:
            return override_op(comparison_data, self.value)
        return self.operator.compute(comparison_data, self.value)

    def _partial_prepare_da(
        self,
        min_val: pint.Quantity | None,
        offset: pint.Quantity | None,
        unit: str | None,
    ) -> Callable[[xr.DataArray], xr.DataArray]:
        def _final_prepare_da(value: xr.DataArray) -> xr.DataArray:
            result = self._prepare_da(value, min_val, offset, unit)
            self.value = result
            return result

        return _final_prepare_da

    def _get_metadata_templates(self) -> ThresholdMetadata:
        if self.value.size == 1:
            return EN_THRESHOLD_TEMPLATE["single_value"]
        return EN_THRESHOLD_TEMPLATE["multiple_values"]

    def _prepare_da(
        self,
        value: xr.DataArray,
        min_value: pint.Quantity | None,
        offset: pint.Quantity | None,
        unit: str | None,
    ) -> xr.DataArray:
        built_value = _apply_min_value(value, min_value)
        built_value = _apply_offset(built_value, offset)
        if unit is not None:
            built_value = convert_units_to(built_value, unit, context="hydro")
        self.is_ready = True
        return built_value


def _apply_offset(da: DataArray, offset: pint.Quantity | None) -> xr.DataArray:
    if offset is not None:
        if offset.dimensionless:
            # We assume the same unit as `da` if it's dimensionless
            offset = offset.m
        else:
            offset = convert_units_to(str(offset), da, context="hydro")
        with xr.set_options(keep_attrs=True):
            return da + offset
    return da


def _apply_min_value(da: DataArray, min_value: pint.Quantity | None) -> xr.DataArray:
    if min_value is not None:
        if min_value.dimensionless:
            # We assume min_value use the same unit as thresh_da if it's dimensionless
            min_value = min_value.m
        else:
            min_value = convert_units_to(str(min_value), da, context="hydro")
        return da.where(da > min_value, np.nan)
    return da

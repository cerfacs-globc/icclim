:py:mod:`icclim._core.generic.threshold.basic`
==============================================

.. py:module:: icclim._core.generic.threshold.basic

.. autoapi-nested-parse::

   BasicThreshold module.



Module Contents
---------------

.. py:class:: BasicThreshold(operator: icclim._core.model.operator.Operator | str, value: icclim._core.model.threshold.ThresholdValueType, unit: str | None = None, initial_query: str | None = None, threshold_min_value: pint.Quantity | None = None, threshold_var_name: str | None = None, offset: pint.Quantity | None = None, **kwargs)




   Pint ready simple threshold (e.g. "> 300 K").

   :param operator: The operator used for the threshold comparison.
   :type operator: Operator or str
   :param value: The threshold value(s) to compare against.
   :type value: ThresholdValueType
   :param unit: The unit of the threshold value(s).
   :type unit: str, optional
   :param initial_query: The initial query used to build the threshold.
   :type initial_query: str, optional
   :param threshold_min_value: The minimum value for the threshold.
   :type threshold_min_value: pint.Quantity, optional
   :param threshold_var_name: The name of the threshold variable.
   :type threshold_var_name: str, optional
   :param offset: The offset to be applied to the threshold value(s).
   :type offset: pint.Quantity, optional

   .. rubric:: Notes

   When built, `value` is always turned into a `xarray.DataArray`.
   The `unit` property has a setter that will attempt a unit conversion using
   units found in xclim's pint registry.

   The actual unit can be overridden by modifying `value.attrs["units"]` directly.

   .. py:property:: unit
      :type: str | None

      The unit of the threshold value(s).

   .. py:method:: format_metadata(jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, **kwargs) -> icclim._core.generic.threshold.threshold_templates.ThresholdMetadata

      Generate the metadata for the threshold.

      These metadata are used to fill the generic template.

      :param jinja_scope: The jinja scope, it contains the variables to be used in the jinja template.
      :type jinja_scope: dict
      :param jinja_env: The jinja environment, it contains the jinja rendering engine.
      :type jinja_env: jinja2.Environment
      :param \*\*kwargs: Additional keyword arguments, ignored for compatibility with other
                         `format_metadata` methods.

      :returns: The metadata for the threshold.
      :rtype: ThresholdMetadata


   .. py:method:: compute(comparison_data: xarray.DataArray, override_op: Callable[[xarray.DataArray, xarray.DataArray], xarray.DataArray] | None = None, **kwargs) -> xarray.DataArray

      Compute the threshold exceedance value.

      :param comparison_data: The data array to compare with the threshold value.
      :type comparison_data: xr.DataArray
      :param override_op: A custom override function to compute the threshold value.
                          If provided, this function will be used instead of the default operator.
      :type override_op: Callable[[DataArray, DataArray], DataArray] | None, optional
      :param \*\*kwargs: Additional keyword arguments.

      :returns: The computed threshold value.
      :rtype: DataArray

      .. rubric:: Notes

      If `override_op` is not None, the `override_op` function will be used to
      compute the threshold exceedance using the `comparison_data` and `self.value`
      as inputs.
      If `override_op` is None, the default operator defined in `self.operator`
      will be used to compute the threshold exceedance.

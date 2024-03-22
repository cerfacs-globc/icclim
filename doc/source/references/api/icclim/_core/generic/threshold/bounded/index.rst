:py:mod:`icclim._core.generic.threshold.bounded`
================================================

.. py:module:: icclim._core.generic.threshold.bounded

.. autoapi-nested-parse::

   BoundedThreshold module.

   A `BoundedThreshold` is a composite threshold that binds two other thresholds
   for example "> 95 doy_per AND >= 30 deg_C".



Module Contents
---------------

.. py:class:: BoundedThreshold(thresholds: collections.abc.Sequence[icclim._core.model.threshold.Threshold | str | icclim._core.model.threshold.ThresholdBuilderInput], logical_link: icclim._core.model.logical_link.LogicalLink, initial_query: str | None, **kwargs)




   Threshold that binds two other thresholds (e.g. "> 95 doy_per AND >= 30 deg_C").

   The logical link must be either "and" or "or".

   .. py:property:: unit
      :type: str | None

      The unit of the bounded threshold.

      :returns: The unit of the threshold if both thresholds have the same unit,
                otherwise None.
      :rtype: str | None

   .. py:method:: compute(comparison_data: xarray.DataArray, override_op: Callable[[xarray.DataArray, xarray.DataArray], xarray.DataArray] | None = None, **kwargs) -> xarray.DataArray

      Compute the threshold exceedance value.

      Uses the logical link to combine the result of both thresholds.

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
      compute the thresholds exceedances on both thresholds.


   .. py:method:: format_metadata(*, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, **kwargs) -> icclim._core.generic.threshold.threshold_templates.ThresholdMetadata

      Generate the metadata for the bounded threshold.

      These metadata are used to fill the generic template.

      :param jinja_scope: The jinja scope, it contains the variables to be used in the jinja template.
      :type jinja_scope: dict
      :param jinja_env: The jinja environment, it contains the jinja rendering engine.
      :type jinja_env: jinja2.Environment
      :param \*\*kwargs: Additional keyword arguments, ignored for compatibility with other
                         `format_metadata` methods.

      :returns: The metadata for the threshold.
      :rtype: ThresholdMetadata

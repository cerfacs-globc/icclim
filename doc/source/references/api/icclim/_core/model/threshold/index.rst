:py:mod:`icclim._core.model.threshold`
======================================

.. py:module:: icclim._core.model.threshold

.. autoapi-nested-parse::

   Threshold abstract class and ThresholdBuilderInput type.



Module Contents
---------------

.. py:class:: ThresholdBuilderInput




   Threshold building configuration.

   Data transfert object mapping all possible configuration to build any threshold.


.. py:class:: Threshold




   Abstract class for all thresholds.

   See :ref:`generic_indices_recipes` for how to use custom thresholds.

   .. py:method:: format_metadata(*, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, **kwargs) -> icclim._core.generic.threshold.threshold_templates.ThresholdMetadata
      :abstractmethod:

      Get a dictionary of standardized threshold metadata.


   .. py:method:: compute(comparison_data: xarray.DataArray, override_op: Callable[[xarray.DataArray, xarray.DataArray], xarray.DataArray] | None = None, **kwargs) -> xarray.DataArray
      :abstractmethod:

      Compute the exceedance of the threshold.

      For example, if the threshold is 10 and the comparison_data is [5, 10, 15],
      with a ">" operator, the exceedance will be [False, False, True].
      The operator can be overridden by `override_op`.
      This is needed when self.operator is REACH.

      :param comparison_data: Data that must be compared to self threshold
      :type comparison_data: xr.DataArray
      :param override_op: Operator to override self.operator compute function.
                          Optional.
      :type override_op: Callable[[DataArray, DataArray], DataArray] | None
      :param kwargs: Keyword arguments passed to the concrete `compute` implementations.
                     This makes the `compute` interface contract unreliable.
                     So we accept to not respected LSP here.

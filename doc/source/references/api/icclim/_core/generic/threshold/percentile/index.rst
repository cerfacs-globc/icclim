:py:mod:`icclim._core.generic.threshold.percentile`
===================================================

.. py:module:: icclim._core.generic.threshold.percentile

.. autoapi-nested-parse::

   Percentile based threshold module.



Module Contents
---------------

.. py:class:: PercentileThreshold(operator: str | icclim._core.model.operator.Operator, value: xarray.DataArray | float | collections.abc.Sequence[float], unit: str | None = None, doy_window_width: int = DEFAULT_DOY_WINDOW, only_leap_years: bool = False, interpolation: icclim._core.model.quantile_interpolation.QuantileInterpolation | str = QuantileInterpolationRegistry.MEDIAN_UNBIASED, reference_period: collections.abc.Sequence[datetime.datetime | str] | None = None, threshold_min_value: pint.Quantity | None = None, initial_query: str | None = None, threshold_var_name: str | None = None, **kwargs)




   Percentile based threshold (e.g. "<= 10 doy_per").

   The percentiles to be computed are expected to be either:

   * "doy percentiles" (unit: "doy_per"). They are usually used for temperatures
     indices such as the ECAD :ref:`tx90p <ecad_functions_api>`.
     These percentiles are computed per day of year (doy) and by aggregating
     values on the time axis ranged by ``reference_period``, using the
     ``doy_window_width`` parameter to control the time axis window of aggregation.
     The resulting `value` is a DataArray with a "dayofyear" dimension ranging from
     0 to 365 with one value per day of the year.
   * "period percentiles" (unit: "period_per"). They are usually used for liquide
     precipitation indices such as the ECAD :ref:`r75p <ecad_functions_api>`
     or even :ref:`r75ptot <ecad_functions_api>`.
     These percentiles are computed per grid cell on the period ranged by
     ``reference_period``.
     The resulting ``value`` is a DataArray with per grid cell values and no time axis.

   ``is_ready`` becomes True when `prepare` method has been called, the actual
   percentiles are then computed and accessible in ``value`` property.
   Once ``is_ready`` is True, ``unit`` property can be set and will attempt a pint unit
   conversion similar to what is done on ``BasicThreshold``.
   Before that, setting unit has no effect.

   .. py:property:: unit
      :type: str | None

      The unit of the threshold.

   .. py:property:: value
      :type: icclim._core.input_parsing.PercentileDataArray

      The computed percentile threshold.

      :raises RuntimeError: If the threshold is not ready (prepare has not been called).

   .. py:method:: prepare(studied_data: xarray.DataArray) -> None

      Prepare the data for calculating percentiles.

      :param studied_data: The input data to be prepared.
      :type studied_data: DataArray

      :raises NotImplementedError: If the percentile unit is unknown.

      :rtype: None


   .. py:method:: format_metadata(*, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment, src_freq: icclim._core.frequency.Frequency, must_run_bootstrap: bool = False, **kwargs) -> icclim._core.generic.threshold.threshold_templates.ThresholdMetadata

      Generate the metadata for the threshold.

      These metadata are used to fill the generic template.

      :param jinja_scope: The jinja scope, it contains the variables to be used in the jinja template.
      :type jinja_scope: dict
      :param jinja_env: The jinja environment, it contains the jinja rendering engine.
      :type jinja_env: jinja2.Environment
      :param src_freq: The frequency of the source data.
      :type src_freq: Frequency
      :param must_run_bootstrap: Whether to run bootstrap, by default False.
      :type must_run_bootstrap: bool, optional

      :returns: The metadata for the threshold.
      :rtype: ThresholdMetadata


   .. py:method:: compute(comparison_data: xarray.DataArray, override_op: Callable[[xarray.DataArray, xarray.DataArray], xarray.DataArray] | None = None, **kwargs) -> xarray.DataArray

      Compute the percentile threshold.

      :param comparison_data: The data array to compare with the threshold.
      :type comparison_data: xr.DataArray
      :param override_op: An optional override operator to use instead of the default operator.
      :type override_op: Callable[[DataArray, DataArray], DataArray] | None, optional
      :param \*\*kwargs: Additional keyword arguments.
                         The `freq` parameter is used to specify the frequency of the data.
                         The `bootstrap` parameter is used to specify whether to run bootstrap.

      :returns: The computed percentile threshold.
      :rtype: DataArray

      :raises RuntimeError: If the PercentileThreshold is not ready. You must first call `.prepare`
          with a `studied_data` parameter in order to prepare the threshold
          for computation.

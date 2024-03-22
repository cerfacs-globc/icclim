:py:mod:`icclim._core.generic.indicator`
========================================

.. py:module:: icclim._core.generic.indicator

.. autoapi-nested-parse::

   Contain the GenericIndicator class.



Module Contents
---------------

.. py:class:: GenericIndicator(name: str, process: Callable[Ellipsis, xarray.DataArray], definition: str, check_vars: Callable[[list[icclim._core.climate_variable.ClimateVariable], GenericIndicator], None] | None = None, sampling_methods: list[str] | None = None, missing: str = 'from_context', missing_options: dict | None = None, qualifiers: tuple = ())




   GenericIndicator are climate indicators wich are not specific to a particular domain.

   They can be computed from any climate variable and are combined with `Threshold` objects
   to create personalized indicators.

   :param name: The name of the indicator.
   :type name: str
   :param process: The function that processes the indicator.
   :type process: Callable[..., DataArray]
   :param definition: The definition of the indicator.
   :type definition: str
   :param check_vars: A function that checks if the variables meet the indicator requirements.
                      Defaults to None.
   :type check_vars: Callable[[list[ClimateVariable], GenericIndicator], None], optional
   :param sampling_methods: A list of sampling methods that can be used with the indicator.
                            Defaults to None.
   :type sampling_methods: list[str], optional
   :param missing: The method for handling missing values. Defaults to "from_context".
   :type missing: str, optional
   :param missing_options: Additional options for handling missing values. Defaults to None.
   :type missing_options: dict, optional
   :param qualifiers: Additional qualifiers for the indicator. Defaults to ().
   :type qualifiers: tuple, optional

   .. attribute:: missing

      The method for handling missing values.

      :type: str

   .. attribute:: missing_options

      Additional options for handling missing values.

      :type: dict | None

   .. py:method:: preprocess(climate_vars: list[icclim._core.climate_variable.ClimateVariable], jinja_scope: dict[str, Any], output_frequency: icclim._core.frequency.Frequency, src_freq: icclim._core.frequency.Frequency, output_unit: str | None, coef: float | None, sampling_method: str) -> list[icclim._core.climate_variable.ClimateVariable]

      Preprocesses the climate variables before computing the indicator.

      :param climate_vars: The list of climate variables to be preprocessed.
      :type climate_vars: list[ClimateVariable]
      :param jinja_scope: The Jinja scope used for formatting the template.
      :type jinja_scope: dict[str, Any]
      :param output_frequency: The desired frequency of the output.
      :type output_frequency: Frequency
      :param src_freq: The source frequency of the climate variables.
      :type src_freq: Frequency
      :param output_unit: The desired output unit of the indicator. If None, no unit conversion is
                          performed.
      :type output_unit: str | None
      :param coef: The coefficient to multiply the climate variable data with. If None,
                   no multiplication is performed.
      :type coef: float | None
      :param sampling_method: The sampling method used for some specific indicators.
                              See `difference_of_means` for example.
      :type sampling_method: str

      :returns: The preprocessed climate variables.
      :rtype: list[ClimateVariable]


   .. py:method:: postprocess(result: xarray.DataArray, climate_vars: list[icclim._core.climate_variable.ClimateVariable], output_freq: str, src_freq: str, indexer: dict, out_unit: str | None) -> xarray.DataArray

      Postprocesses the result of the indicator computation.

      :param result: The result of the indicator computation.
      :type result: DataArray
      :param climate_vars: The list of climate variables used for the computation.
      :type climate_vars: list[ClimateVariable]
      :param output_freq: The desired output frequency of the postprocessed result.
      :type output_freq: str
      :param src_freq: The source frequency of the input data.
      :type src_freq: str
      :param indexer: The indexer used to subset the input data.
      :type indexer: dict
      :param out_unit: The desired output unit of the postprocessed result.
                       If None, no unit conversion is performed.
      :type out_unit: str | None

      :returns: The postprocessed result.
      :rtype: DataArray



.. py:function:: _check_cf(climate_vars: list[icclim._core.climate_variable.ClimateVariable]) -> None

   Compare metadata attributes to CF-Convention standards.

   Default cfchecks use the specifications in `xclim.core.utils.VARIABLES`,
   assuming the indicator's inputs are using the CMIP6/xclim variable names
   correctly.
   Variables absent from these default specs are silently ignored.

   When subclassing this method, use functions decorated using
   `xclim.core.options.cfcheck`.

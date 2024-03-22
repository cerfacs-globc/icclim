:py:mod:`icclim._core.climate_variable`
=======================================

.. py:module:: icclim._core.climate_variable

.. autoapi-nested-parse::

   Contain the ClimateVariable class and its related functions.

   A climate variable is a structure that contains all the pre-processed input varaible to
   compute a climate index.
   A climate index may require one or more climate variables to be computed.



Module Contents
---------------

.. py:class:: ClimateVariable


   ClimateVariable is a dataclass that represents a climate variable used to compute a climate index.

   It groups together the input variable (studied_data), its associated metadata
   (standard_var) if any, the threshold it must be compared to.

   .. attribute:: name

      Name of the variable.

      :type: str

   .. attribute:: standard_var

      CF metadata bounded to the standard variable used for this ClimateVariable.

      :type: StandardVariable

   .. attribute:: studied_data

      The variable studied.

      :type: DataArray

   .. attribute:: threshold

      thresholds for this variable

      :type: Threshold | None

   .. py:method:: build_indicator_metadata(src_freq: icclim._core.frequency.Frequency, must_run_bootstrap: bool, jinja_scope: dict[str, Any], jinja_env: jinja2.Environment) -> dict[str, str | dict]

      Build the metadata for the indicator that will be computed with this variable.

      :param src_freq: The frequency of the source data.
      :type src_freq: Frequency
      :param must_run_bootstrap: Whether the bootstrap method must be run.
      :type must_run_bootstrap: bool
      :param jinja_scope: The scope to use for jinja templating.
      :type jinja_scope: dict
      :param jinja_env: The environment to use for jinja templating.
      :type jinja_env: jinja2.Environment

      :returns: The metadata for the indicator.
      :rtype: dict of str, str | dict



.. py:function:: build_climate_vars(climate_vars_dict: dict[str, icclim._core.model.in_file_dictionary.InFileDictionary], ignore_Feb29th: bool, time_range: collections.abc.Sequence[datetime.datetime | str] | None, base_period: collections.abc.Sequence[str] | None, standard_index: icclim._core.model.standard_index.StandardIndex | None, is_compared_to_reference: bool) -> list[ClimateVariable]

   Build a list of ClimateVariable from a dictionary of input files.

   :param climate_vars_dict: The dictionary of input files.
   :type climate_vars_dict: dict of str, InFileDictionary
   :param ignore_Feb29th: Whether to ignore February 29th.
   :type ignore_Feb29th: bool
   :param time_range: The time range to consider.
   :type time_range: Sequence of datetime | str | None
   :param base_period:
                       The base period to consider, used to build a reference variable for indices such
                        as anomaly.
   :type base_period: Sequence of str | None
   :param standard_index: The standard index to compute.
   :type standard_index: StandardIndex | None

   :rtype: list of ClimateVariable that will be used to compute the climate index.


.. py:function:: build_climate_var(climate_var_name: str, climate_var_data: icclim._core.model.in_file_dictionary.InFileDictionary | icclim._core.model.icclim_types.InFileBaseType, ignore_Feb29th: bool, time_range: collections.abc.Sequence[datetime.datetime | str] | None, standard_var: icclim._core.model.standard_variable.StandardVariable | None) -> ClimateVariable

   Build a ClimateVariable object.

   :param climate_var_name: The name of the climate variable.
   :type climate_var_name: str
   :param climate_var_data: The input data for the climate variable. It can be either a dictionary
                            or a file.
   :type climate_var_data: InFileDictionary | InFileBaseType
   :param ignore_Feb29th: Flag indicating whether to ignore February 29th in the time range.
   :type ignore_Feb29th: bool
   :param time_range: The time range to consider for the climate variable. It can be a sequence
                      of datetime objects or strings, or None to consider the entire time range.
   :type time_range: Sequence[datetime | str] | None
   :param standard_var: The standard variable to use for the climate variable. If None, the input
                        data will be used to guess the standard variable.
   :type standard_var: StandardVariable | None

   :returns: The built ClimateVariable object.
   :rtype: ClimateVariable

   .. rubric:: Notes

   This function builds a ClimateVariable object based on the provided inputs.
   It reads the input data, determines the standard variable, builds the studied
   data, and sets the threshold and global metadata.

   If the input data is a dictionary, it is assumed to have a 'study' key
   containing the study data and an optional 'thresholds' key containing the
   threshold data.

   If the input data is a file, it is assumed to contain the study data.

   The standard variable is used to determine the conversion unit for the
   threshold data.

   The studied data is built based on the study data, time range, ignore_Feb29th
   flag, and standard variable.

   If a threshold is provided in the dictionary, it is added to the ClimateVariable.

   .. rubric:: Examples

   >>> climate_var_name = "tas"
   >>> climate_var_data = {"study": "/path/to/data.nc", "thresholds": ">= 27 degC"}
   >>> ignore_Feb29th = False
   >>> time_range = ["2000-01-01", "2010-12-31"]
   >>> standard_var = StandardVariableRegistry.TAS
   >>> climate_var = build_climate_var(
   ...     climate_var_name, climate_var_data, ignore_Feb29th, time_range, standard_var
   ... )


.. py:function:: must_run_bootstrap(da: xarray.core.dataarray.DataArray, threshold: icclim._core.model.threshold.Threshold | None) -> bool

   Determine whether to run the bootstrap method.

   :param da: The studied data.
   :type da: DataArray
   :param threshold: The threshold that contains the reference period.
   :type threshold: Threshold | None

   :returns: Whether to run the bootstrap method.
   :rtype: bool

   .. rubric:: Notes

   This function is used to avoid bootstrapping if there is one single year
   overlapping or no year overlapping or all year overlapping between the studied
   data `da` and the reference period defined by the threshold.


.. py:function:: _build_reference_variable(reference_period: collections.abc.Sequence[str] | None, in_files: dict[str, icclim._core.model.in_file_dictionary.InFileDictionary], standard_var: icclim._core.model.standard_variable.StandardVariable) -> ClimateVariable

   Add a secondary variable for indices such as anomaly.

   This kind of indices require exactly two variables, but the second variable can
   just be a subset of the first one.

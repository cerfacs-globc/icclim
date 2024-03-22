:py:mod:`icclim._core.model.index_config`
=========================================

.. py:module:: icclim._core.model.index_config

.. autoapi-nested-parse::

   Contain the IndexConfig class.

   It holds the compiled configuration for the computation of climate indices.



Module Contents
---------------

.. py:class:: IndexConfig


   Configuration class for defining climate index parameters.

   :param frequency: The time frequency of the output. Built from ``slice_mode``.
   :type frequency: Frequency
   :param climate_variables: The list of climate variables used in the index calculation.
   :type climate_variables: list[ClimateVariable]
   :param min_spell_length: The minimum spell length for the index calculation.
                            None if the index is not a spell index.
   :type min_spell_length: int | None
   :param rolling_window_width: The width of the rolling window for the index calculation.
                                None if the index is not a rolling index.
   :type rolling_window_width: int | None
   :param out_unit: The output unit for the index calculation.
                    Optional, used to override the default unit.
   :type out_unit: str | None
   :param callback: The callback function for progress updates during the index calculation.
                    Deprecated.
   :type callback: Callable[[int], None] | None
   :param netcdf_version: The version of the NetCDF file format to use for saving the index results.
                          Default is NetcdfVersion.NETCDF4.
   :type netcdf_version: NetcdfVersion
   :param save_thresholds: Flag indicating whether to save the threshold values used in the index
                           calculation.
   :type save_thresholds: bool
   :param interpolation: The interpolation method to use for calculating quantiles/percentiles.
   :type interpolation: QuantileInterpolation
   :param is_compared_to_reference: Flag indicating whether the index is compared to a reference period.
   :type is_compared_to_reference: bool
   :param reference_period: The reference period for the index calculation.
   :type reference_period: tuple[str, str] | None
   :param indicator_name: The name of the index.
   :type indicator_name: str
   :param logical_link: The logical link to use for combining multiple indices.
   :type logical_link: LogicalLink
   :param coef: The coefficient to apply to the index values.
   :type coef: float | None
   :param date_event: Flag indicating whether the index represents a date or an event.
   :type date_event: bool
   :param sampling_method: The sampling method to use for the index calculation.
                           In conjonction with the Frequency, it is used on specific indices such as the
                           anomaly (a.k.a diff_of_means) to determine if the reference period and the
                           studied period should be grouped by or resampled.
                           It can be either 'group_by', 'resample', or
                           'group_by_ref_and_resample_study'.
                           'group_by' will group the data by the specified frequency, for example every
                           data of every January together.
                           'resample' will resample the data to the specified frequency, for example every
                           days of each month independently together.
                           'group_by_ref_and_resample_study' will group the reference data by the specified
                           frequency and resample the study data to the same frequency.
                           This last method allows for example to compare each January, independently, of
                           the study period to every January of the reference period.
                           This is typically used to compare the each month of the studied period
                           to a normal (the reference) of many aggregated years.
   :type sampling_method: str
   :param rename: The new name for the output variable.
                  Optional, used to override the default index name.
   :type rename: str | None
   :param indicator: The indicator to be computed.
   :type indicator: Indicator
   :param reference: The reference value for the index calculation.
   :type reference: str

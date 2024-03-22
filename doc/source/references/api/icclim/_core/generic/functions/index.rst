:py:mod:`icclim._core.generic.functions`
========================================

.. py:module:: icclim._core.generic.functions

.. autoapi-nested-parse::

   Implementations of the generic indices computation methods.

   These functions are not meant to be called directly, they are used by the
   `GenericIndicatorRegistry` class to create the generic indices.
   Each function is a reducer that takes a list of `ClimateVariable` instances and returns
   a `DataArray` instance.
   The `ClimateVariable` instances are used to extract the data and the thresholds needed
   to compute the generic index.
   The `DataArray` instance is the result of the computation of the generic index.

   .. note::

      You can call the respective generic index from icclim module, for example:
      `icclim.count_occurrences(...)`.



Module Contents
---------------

.. py:function:: count_occurrences(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, logical_link: icclim._core.model.logical_link.LogicalLink, date_event: bool, to_percent: bool, **kwargs) -> xarray.DataArray

   Count the occurrences of exceedances of the threshold(s).

   :param climate_vars: The list of climate variables containing the data and the threshold(s).
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The time frequency of the output.
   :type resample_freq: Frequency
   :param logical_link: The logical link to apply to the exceedances if multiple thresholds are
                        provided.
   :type logical_link: LogicalLink
   :param date_event: Whether to return the date of the event.
   :type date_event: bool
   :param to_percent: Whether to return the result in percent.
   :type to_percent: bool
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The count of occurrences of exceedances.
   :rtype: DataArray


.. py:function:: max_consecutive_occurrence(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, logical_link: icclim._core.model.logical_link.LogicalLink, date_event: bool, source_freq_delta: datetime.timedelta, **kwargs) -> xarray.DataArray

   Calculate the maximum number of consecutive occurrences of exceedances for a given set of climate variables.

   :param climate_vars: The list of climate variables containing the data and the threshold(s).
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The time frequency of the output.
   :type resample_freq: Frequency
   :param logical_link: The logical link to apply when merging the exceedances.
   :type logical_link: LogicalLink
   :param date_event: Whether to include the dates of the exceedances in the result.
   :type date_event: bool
   :param source_freq_delta: The time difference between consecutive data points in the source data.
   :type source_freq_delta: timedelta
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The maximum number of consecutive occurrences of exceedances.
   :rtype: DataArray


.. py:function:: sum_of_spell_lengths(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, logical_link: icclim._core.model.logical_link.LogicalLink, min_spell_length: int, **kwargs) -> xarray.DataArray

   Calculate the sum of the lengths of all spells in the data.

   This function calculates the sum of the lengths of all spells in the data,
   where a spell is defined as a consecutive occurrence of exceedances.

   :param climate_vars: The list of climate variables containing the data and the threshold(s).
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The time frequency of the output.
   :type resample_freq: Frequency
   :param logical_link: The logical link to apply when merging the exceedances.
   :type logical_link: LogicalLink
   :param min_spell_length: The minimum length of a spell to consider.
   :type min_spell_length: int
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The sum of the lengths of all spells in the data.
   :rtype: DataArray


.. py:function:: excess(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Compute the excess of a climate variable above a threshold using the 'reach' operator.

   :param climate_vars: List of climate variables. Only the first variable is used.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The time frequency of the output.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: DataArray containing the computed excess values.
   :rtype: DataArray

   :raises InvalidIcclimArgumentError: If the threshold operator is not 'reach'.

   .. rubric:: Notes

   The excess is computed by subtracting the threshold from the climate variable data.
   Only the values above the threshold are considered, and negative values are set to
   zero.
   The resulting excess values are then summed over the specified resample frequency.


.. py:function:: deficit(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Compute the deficit of a climate variable below a threshold using the 'reach' operator.

   :param climate_vars: List of climate variables. Only the first variable is used.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The time frequency of the output.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: DataArray containing the computed deficit values.
   :rtype: DataArray

   .. rubric:: Notes

   The deficit is computed by subtracting the climate variable data from the threshold.
   Only the values below the threshold are considered, and negative values are set to
   zero.
   The resulting deficit values are then summed over the specified resample frequency.


.. py:function:: fraction_of_total(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, to_percent: bool, **kwargs) -> xarray.DataArray

   Calculate the fraction of total for a given set of climate variables.

   :param climate_vars: The list of climate variables containing the data and the threshold(s).
                        Only one variable is expected in the list.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The resampling frequency.
   :type resample_freq: Frequency
   :param to_percent: Flag indicating whether to convert the result to percentage.
   :type to_percent: bool
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The fraction of total as a DataArray.
   :rtype: DataArray

   .. rubric:: Notes

   This function calculates the fraction of total for a given set of climate variables.
   The fraction of total is calculated by dividing the sum of values exceeding a
   threshold by the total sum of values.

   If the `to_percent` flag is set to True, the result will be multiplied by 100 and
   the units will be set to "%". Otherwise, the units will be set to the value of
   PART_OF_A_WHOLE_UNIT, which is 1.


.. py:function:: maximum(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, date_event: bool, **kwargs) -> xarray.DataArray

   Calculate the maximum value of the given climate variables.

   :param climate_vars: List of climate variables to calculate the maximum value for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param date_event: Flag indicating whether the output should include the date of the events.
   :type date_event: bool
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The maximum value of the climate variables.
   :rtype: DataArray


.. py:function:: minimum(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, date_event: bool, **kwargs) -> xarray.DataArray

   Calculate the minimum value of the given climate variables.

   :param climate_vars: List of climate variables to calculate the minimum value for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param date_event: Flag indicating whether the output should include the date of the events.
   :type date_event: bool
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The minimum value of the climate variables.
   :rtype: DataArray


.. py:function:: average(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Compute the average of the given climate variables.

   :param climate_vars: List of climate variables to compute the average for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed average as a DataArray.
   :rtype: DataArray


.. py:function:: generic_sum(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Compute the sum of the given climate variables.

   :param climate_vars: List of climate variables to compute the sum for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed sum as a DataArray.
   :rtype: DataArray


.. py:function:: standard_deviation(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Compute the standard deviation of the given climate variables.

   This function calculates the standard deviation of the provided climate variables.
   The standard deviation is a measure of the amount of variation or dispersion in the
   data.
   It quantifies the amount of variation or spread in the values of the climate
   variables.

   :param climate_vars: List of climate variables to compute the standard deviation for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed standard deviation as a DataArray.
   :rtype: DataArray


.. py:function:: max_of_rolling_sum(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, rolling_window_width: int, date_event: bool, source_freq_delta: datetime.timedelta, **kwargs) -> xarray.DataArray

   Compute the maximum value of the rolling sum of the given climate variables.

   The rolling sum is the sum of values over a specified rolling window width.
   The maximum value is the highest value obtained from the rolling sum.

   :param climate_vars: List of climate variables to compute the maximum value of the rolling sum for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param rolling_window_width: The width of the rolling window, i.e., the number of values to include in each
                                rolling sum.
   :type rolling_window_width: int
   :param date_event: A flag indicating whether the date of the events should be included in the
                      output.
   :type date_event: bool
   :param source_freq_delta: The time difference between consecutive data points in the source data.
                             For daily data this is 1 day, for monthly data this is 1 month, etc.
   :type source_freq_delta: timedelta
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed maximum value of the rolling sum as a DataArray.
   :rtype: DataArray


.. py:function:: min_of_rolling_sum(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, rolling_window_width: int, date_event: bool, source_freq_delta: datetime.timedelta, **kwargs) -> xarray.DataArray

   Compute the minimum value of the rolling sum of the given climate variables.

   The rolling sum is the sum of values over a specified rolling window width.
   The minimum value is the lowest value obtained from the rolling sum.

   :param climate_vars: List of climate variables to compute the minimum value of the rolling sum for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param rolling_window_width: The width of the rolling window, i.e., the number of values to include in each
                                rolling sum.
   :type rolling_window_width: int
   :param date_event: A flag indicating whether the date of the events should be included in the
                      output.
   :type date_event: bool
   :param source_freq_delta: The time difference between consecutive data points in the source data.
                             For daily data this is 1 day, for monthly data this is 1 month, etc.
   :type source_freq_delta: timedelta
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed minimum value of the rolling sum as a DataArray.
   :rtype: DataArray


.. py:function:: min_of_rolling_average(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, rolling_window_width: int, date_event: bool, source_freq_delta: datetime.timedelta, **kwargs) -> xarray.DataArray

   Compute the minimum value of the rolling average of the given climate variables.

   The rolling average is the average of values over a specified rolling window width.
   The minimum value is the lowest value obtained from the rolling average.

   :param climate_vars: List of climate variables to compute the minimum value of the rolling average
                        for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param rolling_window_width: The width of the rolling window, i.e., the number of values to include in each
                                rolling average.
   :type rolling_window_width: int
   :param date_event: A flag indicating whether the date of the events should be included in the
                      output.
   :type date_event: bool
   :param source_freq_delta: The time difference between consecutive data points in the source data.
                             For daily data this is 1 day, for monthly data this is 1 month, etc.
   :type source_freq_delta: timedelta
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed minimum value of the rolling average as a DataArray.
   :rtype: DataArray


.. py:function:: max_of_rolling_average(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, rolling_window_width: int, date_event: bool, source_freq_delta: datetime.timedelta, **kwargs) -> xarray.DataArray

   Compute the minimum value of the rolling average of the given climate variables.

   The rolling average is the average of values over a specified rolling window width.
   The minimum value is the lowest value obtained from the rolling average.

   :param climate_vars: List of climate variables to compute the minimum value of the rolling average
                        for.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param rolling_window_width: The width of the rolling window, i.e., the number of values to include in each
                                rolling average.
   :type rolling_window_width: int
   :param date_event: A flag indicating whether the date of the events should be included in the
                      output.
   :type date_event: bool
   :param source_freq_delta: The time difference between consecutive data points in the source data.
                             For daily data this is 1 day, for monthly data this is 1 month, etc.
   :type source_freq_delta: timedelta
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The computed minimum value of the rolling average as a DataArray.
   :rtype: DataArray


.. py:function:: mean_of_difference(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Calculate the mean of the difference between two climate variables.

   This function calculates the mean of the difference between two climate variables
   for each time step, and then resamples the resulting data based on the specified
   frequency.
   The resulting data array will have the same units as the study variable.

   :param climate_vars: The two climate variables necessary to compute the indicator.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: Resampling frequency of the output.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The mean of the difference as a xarray.DataArray.
   :rtype: DataArray

   .. rubric:: Notes

   This is a generification of ECAD's DTR climate index.


.. py:function:: difference_of_extremes(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Calculate the difference of extremes between two climate variables.

   :param climate_vars: A list of climate variables.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: The frequency at which to resample the data.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The difference of extremes between the two climate variables.
   :rtype: DataArray

   .. rubric:: Notes

   This function calculates the difference of extremes between two climate variables.
   It first resamples the study variable to the specified frequency and take the
   maximum per resampled chunk.
   Then it resamples the reference variable to the same frequency and take the minimum
   per resampled chunk.
   Finally, for each chunk, it calculates the differences of theses maximum and
   minimum values.
   This is a generification of ECAD's ETR climate index.


.. py:function:: mean_of_absolute_one_time_step_difference(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Mean of the absolute one-time-step difference between two climate variables.

   This function calculates the mean of the absolute difference between two climate
   variables
   for each time step, and then resamples the resulting data based on the specified
   frequency.
   The resulting data array will have the same units as the study variable.

   :param climate_vars: The two climate variables necessary to compute the indicator.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: Resampling frequency of the output.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).
   :type \*\*kwargs: dict

   :returns: The mean of the absolute one-time-step difference as a xarray.DataArray.
   :rtype: DataArray

   .. rubric:: Notes

   This is a generification of ECAD's vDTR climate index.


.. py:function:: difference_of_means(climate_vars: list[icclim._core.climate_variable.ClimateVariable], to_percent: bool, resample_freq: icclim._core.frequency.Frequency, sampling_method: str, is_compared_to_reference: bool, **kwargs) -> xarray.DataArray

   Calculate the difference of means between two climate variables.

   :param climate_vars: A studied climate variable and a reference climate variable.
   :type climate_vars: list[ClimateVariable]
   :param to_percent: If True, the result will be converted to percentage.
   :type to_percent: bool
   :param resample_freq: Resampling frequency of the output.
   :type resample_freq: Frequency
   :param sampling_method: The method used for resampling. It can be either 'group_by', 'resample', or
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
   :param is_compared_to_reference: If True, check if the sampling method is 'resample' and raise an error if it is.
                                    It does not make sense to resample the reference variable if it is already a
                                    subsample of the studied variable.
   :type is_compared_to_reference: bool
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The difference of means between the two climate variables.
   :rtype: DataArray

   .. rubric:: Notes

   This is a generification of the anomaly climate index.


.. py:function:: percentile(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, **kwargs) -> xarray.DataArray

   Calculate the percentile of the given climate variable.

   :param climate_vars: A single climate variable within a list.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: Resampling frequency of the output.
   :type resample_freq: Frequency
   :param \*\*kwargs: Ignored keyword arguments (for compatibility).

   :returns: The calculated percentile as a DataArray.
   :rtype: DataArray

   .. rubric:: Notes

   This function calculates the percentile of the given climate variables
   by resampling the data based on the provided frequency and then
   calculating the corresponding quantile using the specified interpolation method.

   The resulting DataArray contains the percentiles as the 'percentiles'
   coordinate variable.


.. py:function:: get_couple_of_var(climate_vars: list[icclim._core.climate_variable.ClimateVariable], indicator: str) -> tuple[xarray.DataArray, xarray.DataArray]

   Get exactly two climate variables to compute a climate indicator.

   :param climate_vars: A list of climate variables.
   :type climate_vars: list[ClimateVariable]
   :param indicator: The name of the indicator to be computed.
   :type indicator: str

   :returns: A tuple containing two DataArray objects representing the study variable and
             the reference variable.
   :rtype: tuple[DataArray, DataArray]

   :raises InvalidIcclimArgumentError: If the number of climate variables is not equal to 2.
       If any of the two variable has a threshold.

   .. rubric:: Notes

   This function is used to extract a couple of climate variables needed for computing
   an indicator.
   The function checks the number of climate variables and raises an error
   if it is not equal to 2 or if thresholds are present.


.. py:function:: _run_simple_reducer(climate_vars: list[icclim._core.climate_variable.ClimateVariable], resample_freq: icclim._core.frequency.Frequency, reducer_op: Callable[Ellipsis, xarray.DataArray], date_event: bool, must_convert_rate: bool = False) -> xarray.DataArray

   Apply a simple reducer operation on climate variables.

   :param climate_vars: List of climate variables to be processed.
   :type climate_vars: list[ClimateVariable]
   :param resample_freq: Frequency at which the data should be resampled.
   :type resample_freq: Frequency
   :param reducer_op: Reducer operation to be applied on the data.
   :type reducer_op: Callable[..., DataArray]
   :param date_event: Flag indicating whether the date when the event occurred should be added
                      as a coordinate variable.
                      Only works for `max` and `min` reducers.
                      Defaults to False.
   :type date_event: bool
   :param must_convert_rate: Flag indicating whether the data should be converted from rate to amount.
                             Defaults to False.
   :type must_convert_rate: bool, optional

   :returns: Result of the reducer operation applied on the climate variables.
   :rtype: DataArray


.. py:function:: get_single_var(climate_vars: list[icclim._core.climate_variable.ClimateVariable]) -> tuple[xarray.DataArray, icclim._core.model.threshold.Threshold | None]

   Get the single variable and its threshold (if available).

   :param climate_vars: A list of ClimateVariable objects.
   :type climate_vars: list[ClimateVariable]

   :returns: A tuple containing the single variable's data array and its threshold
             (if available).
   :rtype: tuple[DataArray, Threshold | None]

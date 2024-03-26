:py:mod:`icclim._core.frequency`
================================

.. py:module:: icclim._core.frequency

.. autoapi-nested-parse::

   Contain the Frequency class and the FrequencyRegistry class.

   Frequency wraps the concept of pandas frequency in order to resample
   time series. ``slice_mode`` parameter of `icclim.index` is always converted to a
   `Frequency`.



Module Contents
---------------

.. py:function:: get_seasonal_time_updater(start_month: int, end_month: int, start_day: int = 1, end_day: int | None = None) -> Callable[[xarray.core.dataarray.DataArray], tuple[xarray.core.dataarray.DataArray, xarray.core.dataarray.DataArray]]

   Seasonal time updater and time bounds creator method generator.

   Returns a callable of DataArray which will rewrite the time dimension to
   the season composed of the given months. The data must have been computed on this
   season beforehand.
   It also create the corresponding time_bounds.

   :param start_month: The season starting month, it must be between 1 and 12.
   :type start_month: int
   :param end_month: The season ending month, it must be between 1 and 12.
   :type end_month: int
   :param start_day: The season starting day, it must be between 1 and 31.
   :type start_day: int
   :param end_day: The season ending day, it must be between 1 and 31.
   :type end_day: int

   :returns: **function** -- A function that will update the time dimension of a DataArray to the season
             composed of the given months and create the corresponding time_bounds.
   :rtype: Callable[[DataArray], tuple[DataArray, DataArray]]


.. py:function:: get_time_bounds_updater(freq: str) -> Callable[[xarray.core.dataarray.DataArray], tuple[xarray.core.dataarray.DataArray, xarray.core.dataarray.DataArray]]

   Return a function that adds time bounds to a given DataArray.

   :param freq: The frequency at which the DataArray should be resampled.
   :type freq: str

   :returns: A function that takes a DataArray as input and returns a tuple
             containing the modified DataArray and the time
             bounds as a separate DataArray.
   :rtype: Callable[[DataArray], tuple[DataArray, DataArray]]

   .. rubric:: Notes

   The returned function assumes that the input DataArray has already
   been resampled to the specified frequency.

   The time axis values in the modified DataArray will be set to the
   middle of the calculated time bounds.


.. py:class:: Frequency


   Time sampling frequency.

   This acts as a wrapper around the pandas frequency string.
   ``icclim.index`` will always convert the ``slice_mode`` parameter to a
   ``Frequency``.

   :param pandas_freq: The frequency string used by pandas to resample the time series.
   :type pandas_freq: str
   :param accepted_values: The list of aliases for the frequency.
   :type accepted_values: list[str]
   :param adjective: The adjective form of the frequency. Used when templating the output's metadata.
   :type adjective: str
   :param post_processing: The function to apply for post-processing the resampled data.
   :type post_processing: Callable[[DataArray], tuple[DataArray, DataArray]] | None
   :param units: The units of the frequency.
   :type units: str
   :param indexer: The indexer to use for grouping the data.
   :type indexer: Indexer | None
   :param long_name: The long name of the frequency.
   :type long_name: str
   :param group_by_key: The key to use for grouping the data.
   :type group_by_key: str | None
   :param delta: The time delta for the frequency.
   :type delta: np.timedelta64

   :returns: The frequency object.
   :rtype: Frequency

   .. rubric:: Notes

   This class represents a time sampling frequency.

   .. rubric:: Examples

   >>> freq = Frequency(
   ...     pandas_freq="D",
   ...     accepted_values=["daily", "day", "days", "d"],
   ...     adjective="daily",
   ...     indexer=None,
   ...     post_processing=get_time_bounds_updater("D"),
   ...     units="days",
   ...     long_name="day",
   ...     group_by_key="time.dayofyear",
   ...     delta=np.timedelta64(1, "D"),
   ... )

   .. py:method:: build_frequency_kwargs() -> dict[str, Any]

      Build kwargs with possible keys in {"freq", "month", "date_bounds"}.



.. py:class:: FrequencyRegistry




   Registry class for Frequency objects.

   .. py:attribute:: NO_RESAMPLE

      Does not resample

   .. py:attribute:: HOUR

      Resample to hourly values

   .. py:attribute:: DAY

      Resample to daily values

   .. py:attribute:: MONTH

      Resample to monthly values

   .. py:attribute:: YEAR

      Resample to yearly values.

   .. py:attribute:: AMJJAS

      Resample to summer half-year, from April to September included.

   .. py:attribute:: ONDJFM

      Resample to winter half-year, from October to March included.

   .. py:attribute:: DJF

      Resample to winter season, from December to February included.

   .. py:attribute:: MAM

      Resample to spring season, from March to May included.

   .. py:attribute:: JJA

      Resample to summer season, from June to Agust included.

   .. py:attribute:: SON

      Resample to fall season, from September to November included.

   .. py:method:: lookup(query: icclim._core.model.icclim_types.FrequencyLike | Frequency) -> Frequency
      :classmethod:

      Look up a Frequency object based on the query.

      :param query: The query to look up the Frequency object. Typically a string.
      :type query: FrequencyLike or Frequency

      :returns: The Frequency object that matches the query.
      :rtype: Frequency

      :raises InvalidIcclimArgumentError: If the query is not a valid frequency.

      .. rubric:: Notes

      The query can be a Frequency object, a string representing a frequency,
      or a list/tuple representing a frequency.

      If the query is a string, it will be converted to a Frequency object first by
      looking in the FrequencyRegistry then by assuming it's a pandas frequency and
      building a Frequency object from it.

      If the query is a list/tuple, it needs a keyword as its first element and a list
      of months or a list of two date strings as its second element. The keyword can
      be either "month" or "season".
      In "month" case, the second element must be a list of months and the Frequency
      will filter the data by these months.
      In "season" case, the second element must be a list of months or a list of two
      date and the Frequency will resample the data to the season composed of these
      months.


   .. py:method:: get_item_aliases(item: Frequency) -> list[str]
      :staticmethod:

      Get the aliases of a Frequency object.

      :param item: The Frequency object.
      :type item: Frequency

      :returns: The aliases of the Frequency object.
      :rtype: list[str]



.. py:function:: _get_delta(pandas_freq: str) -> numpy.timedelta64

   Build timedelta from a "pandas frequency" string.

   A "pandas frequency" string may look like ["2YS-DEC", "3W-TUE", "M", ... ]
   The anchor, such as "DEC" in "YS-DEC", does not modify the delta.

   :param pandas_freq:
   :type pandas_freq: str
   :param The frequency query.:

   :returns: * *The timedelta corresponding to this frequency.*
             * *For example, "2YS-DEC" would return a 2 years delta.*

:py:mod:`icclim.main`
=====================

.. py:module:: icclim.main

.. autoapi-nested-parse::

   Main entry point of icclim.

   This module expose icclim principal function, notably `index` which is use by the
   generated API.
   A convenience function `indices` is also exposed to compute multiple indices at once.



Module Contents
---------------

.. py:function:: indices(index_group: collections.abc.Sequence[str] | str | icclim._core.model.index_group.IndexGroup | icclim._core.model.standard_index.StandardIndex, *, ignore_error: bool = False, **kwargs) -> xarray.core.dataset.Dataset

   Compute multiple indices at the same time.

   The input dataset(s) must include all the necessary variables.
   It can only be used with keyword arguments (kwargs).

   :param index_group: Either the name of an IndexGroup or an instance of IndexGroup or a list
                       of index short names or the name(s) of standard variable(s) (such as 'tasmax').
                       The value "all" can also be used to compute every indices.
                       Note that the input given by ``in_files`` must include all the necessary
                       variables to compute the indices of this group.
   :type index_group: "all" | str | IndexGroup | list[str]
   :param ignore_error: When True, ignore indices that fails to compute. This is option is particularly
                        useful when used with `index_group='all'` to compute everything that can be
                        computed given the input.
   :type ignore_error: bool
   :param kwargs: ``icclim.index`` keyword arguments.
   :type kwargs: Dict

   :returns: A Dataset with one data variable per index.
   :rtype: xr.Dataset

   .. rubric:: Notes

   If ``output_file`` is part of kwargs, the result is written in a single netCDF
   file, which will contain all the index results of this group.


.. py:function:: indice(*args, **kwargs) -> xarray.core.dataset.Dataset

   Proxy for `icclim.index` function.

   Deprecated: to be deleted in a future release.


.. py:function:: index(in_files: icclim._core.model.icclim_types.InFileLike, index_name: str | icclim._core.generic.indicator.GenericIndicator | icclim._core.model.standard_index.StandardIndex | None = None, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, callback: Callable[[int], None] = log.callback, callback_percentage_start_value: int = 0, callback_percentage_total: int = 100, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, doy_window_width: int = 5, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', user_index: icclim._core.legacy.user_index.model.UserIndexDict | None = None, save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, min_spell_length: int | None = 6, rolling_window_width: int | None = 5, sampling_method: icclim._core.model.icclim_types.SamplingMethodLike = RESAMPLE_METHOD, *, window_width: int | None = None, save_percentile: bool | None = None, indice_name: str | None = None, user_indice: icclim._core.legacy.user_index.model.UserIndexDict | None = None, transfer_limit_Mbytes: float | None = None) -> xarray.core.dataset.Dataset

   Compute climate index.

   This is the main entry point for icclim.

   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
   :param index_name: Climate index name.
                      For ECA&D index, case insensitive name used to lookup the index.
                      For user index, it's the name of the output variable.
   :type index_name: str | StandardIndex
   :param var_name: ``optional`` Target variable name to process corresponding to ``in_files``.
                    If None (default) on ECA&D index, the variable is guessed based on the
                    climate index wanted.
                    Mandatory for a user index.
   :type var_name: str | list[str] | None
   :param slice_mode: Type of temporal aggregation:
                      The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
                      "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
                      (where season and month lists can be customized) or any valid pandas
                      frequency.
                      A season can also be defined between two exact dates:
                      ``("season", ("19 july", "14 august"))``.
                      Default is "year".
                      See :ref:`slice_mode` for details.
   :type slice_mode: FrequencyLike | Frequency
   :param time_range: ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
                      If ``None``, whole period of input files will be processed.
                      The dates can either be given as instance of datetime.datetime or as string
                      values. For strings, many format are accepted.
                      Default is ``None``.
   :type time_range: list[datetime.datetime ] | list[str]  | tuple[str, str] | None
   :param out_file: Output NetCDF file name (default: "icclim_out.nc" in the current directory).
                    Default is "icclim_out.nc".
                    If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
                    Use the function returned value instead to retrieve the computed value.
                    If ``out_file`` already exists, icclim will overwrite it!
   :type out_file: str | None
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param transfer_limit_Mbytes: Deprecated, does not have any effect.
   :type transfer_limit_Mbytes: float
   :param callback: ``optional`` Progress bar printing. If ``None``, progress bar will not be
                    printed.
   :type callback: Callable[[int], None]
   :param callback_percentage_start_value: ``optional`` Initial value of percentage of the progress bar (default: 0).
   :type callback_percentage_start_value: int
   :param callback_percentage_total: ``optional`` Total percentage value (default: 100).
   :type callback_percentage_total: int
   :param base_period_time_range: ``optional`` Temporal range of the reference period.
                                  The dates can either be given as instance of datetime.datetime or as string
                                  values.
                                  It is used either:
                                  #. to compute percentiles if threshold is filled.
                                  When missing, the studied period is used to compute percentiles.
                                  The study period is either the dataset filtered by `time_range` or the whole
                                  dataset if `time_range` is missing.
                                  For day of year percentiles (doy_per), on extreme percentiles the
                                  overlapping period between `base_period_time_range` and the study period is
                                  bootstrapped.
                                  #. to compute a reference period for indices such as difference_of_mean
                                  (a.k.a anomaly) if a single variable is given in input.
   :type base_period_time_range: list[datetime.datetime ] | list[str] | tuple[str, str] | None
   :param doy_window_width: ``optional`` Window width used to aggreagte day of year values when computing
                            day of year percentiles (doy_per)
                            Default: 5 (5 days).
   :type doy_window_width: int
   :param min_spell_length: ``optional`` Minimum spell duration to be taken into account when computing
                            the sum_of_spell_lengths.
   :type min_spell_length: int
   :param rolling_window_width: ``optional`` Window width of the rolling window for indicators such as
                                `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
   :type rolling_window_width: int
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param user_index: ``optional`` A dictionary with parameters for user defined index.
                      See :ref:`Custom indices`.
                      Ignored for ECA&D indices.
   :type user_index: UserIndexDict
   :param save_thresholds: ``optional`` True if the thresholds should be saved within the resulting
                           netcdf file (default: False).
   :type save_thresholds: bool
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity
   :param sampling_method: Choose whether the output sampling configured in `slice_mode` is a
                           `groupby` operation or a `resample` operation (as per xarray definitions).
                           Possible values:
                           ``{"groupby", "resample", "groupby_ref_and_resample_study"}``
                           (default: "resample")
                           `groupby_ref_and_resample_study` may only be used when computing the
                           `difference_of_means` (a.k.a the anomaly).
   :type sampling_method: str
   :param indice_name: DEPRECATED, use index_name instead.
   :type indice_name: str | None
   :param user_indice: DEPRECATED, use user_index instead.
   :type user_indice: dict | None
   :param window_width: DEPRECATED, use doy_window_width, min_spell_length or rolling_window_width
                        instead.
   :type window_width: int
   :param save_percentile: DEPRECATED, use save_thresholds instead.
   :type save_percentile: bool


.. py:function:: _write_output_file(result_ds: xarray.Dataset, input_time_encoding: dict | None, netcdf_version: icclim._core.model.netcdf_version.NetcdfVersion, file_path: str) -> None

   Write `result_ds` to a netCDF file on `out_file` path.


.. py:function:: _must_add_reference_var(climate_vars_dict: dict[str, icclim._core.model.in_file_dictionary.InFileDictionary], reference_period: collections.abc.Sequence[str] | None) -> bool

   Check if the reference variable must be added to the input variables.

   Return True whenever the input has no threshold and only one studied variable but
   there is a reference period.
   Example case: the anomaly of tx(1960-2100) by tx(1960-1990).

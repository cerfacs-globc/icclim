:py:mod:`icclim`
================

.. py:module:: icclim

.. autoapi-nested-parse::

   Python library for climate indices calculation.



Subpackages
-----------
.. toctree::
   :titlesonly:
   :maxdepth: 3

   _core/index.rst
   dcsc/index.rst
   ecad/index.rst
   generic/index.rst
   threshold/index.rst


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   exception/index.rst
   main/index.rst
   rechunk/index.rst


Package Contents
----------------

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


.. py:function:: indice(*args, **kwargs) -> xarray.core.dataset.Dataset

   Proxy for `icclim.index` function.

   Deprecated: to be deleted in a future release.


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


.. py:function:: create_optimized_zarr_store(in_files: str | list[str] | xarray.core.dataset.Dataset | xarray.core.dataarray.DataArray, var_names: str | list[str], target_zarr_store_name: str = 'icclim-target-store.zarr', keep_target_store: bool = False, chunking: dict[str, int] | None = None, filesystem: str | fsspec.AbstractFileSystem = LOCAL_FILE_SYSTEM) -> collections.abc.Generator[xarray.core.dataset.Dataset]

   Context manager to create an zarr store given an input netcdf or xarray structure.

   -- EXPERIMENTAL FEATURE --
   API may changes without deprecation warning!

   The execution may take a long time.

   The result is rechunked according to `chunking` schema provided.
   By default, when leaving `chunking` to None, the resulting zarr store is NOT chunked
   on time dimension.
   This kind of chunking will significantly speed up the bootstrapping of
   percentiles for indices such as Tx90p, Tx10p, TN90p...
   But such chunking will most likely result in suboptimal performances for other
   indices.
   Actually, when computing indices where no bootstrap is needed,
   you should first try the computation without using `create_optimized_zarr_store`.
   If there are performance issues, you may want to use `create_optimized_zarr_store`
   with a dictionary of a better chunking schema than your current storage chunking.

   By default, `keep_target_store` being False, the resulting zarr store is destroyed
   when the context manager is exit.
   To keep the zarr store for futur uses set `keep_target_store` to True.

   The output is the resulting zarr store as a xarray Dataset.

   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray
   :param var_names: List of data variable to include in the target zarr store.
                     All other data variable are dropped.
                     The coordinate variable are untouched and are part of the target zarr store.
   :type var_names: str | list[str]
   :param target_zarr_store_name: Name of the target zarr store.
                                  Used to avoid overriding an existing zarr store.
   :type target_zarr_store_name: str
   :param chunking: The target chunking schema.
   :type chunking: dict
   :param keep_target_store: Set to True to keep the target zarr store after the execution of the context
                             manager.
                             Set to False to remove the target zarr store once execution is finished.
                             Default is False.
   :type keep_target_store: bool
   :param filesystem: A fsspec filesystem where the zarr store will be created.

   :rtype: returns Dataset opened on the newly created target zarr store.

   .. rubric:: Examples

   .. code-block:: python

       import icclim

       with icclim.create_optimized_zarr_store(
           in_files="tasmax.nc",
           var_names="tasmax",
           target_zarr_store_name="tasmax-store.zarr",
           chunking={"time": 42, "lat": 42, "lon": 42},
       ) as tasmax_opti:
           su_out = icclim.index(in_files=tasmax_opti, index_name="su")


.. py:function:: build_threshold(query: str | None = None, *, operator: icclim._core.model.operator.Operator | str | None = None, value: icclim._core.model.threshold.ThresholdValueType = None, unit: str | None = None, threshold_min_value: str | float | pint.Quantity | None = None, thresholds: collections.abc.Sequence[icclim._core.model.threshold.Threshold | str] | None = None, logical_link: str | icclim._core.model.logical_link.LogicalLink | None = None, offset: str | float | pint.Quantity | None = None, **kwargs) -> icclim._core.generic.threshold.bounded.BoundedThreshold | icclim._core.generic.threshold.percentile.PercentileThreshold | icclim._core.generic.threshold.basic.BasicThreshold

   Build a `Threshold`.

   This function is a factory for `Threshold` instances.
   It can build a `BasicThreshold`, a `PercentileThreshold` or a `BoundedThreshold`.
   See :ref:`generic_indices_recipes` for how to combine thresholds with generic
   indices.

   :param query: string query describing a threshold.
                 It must include: an operator, a threshold value and optionally a unit
                 such as "> 10 degC".
                 It acts as a shorthand for ``operator``, ``value`` and ``unit`` parameters for
                 simple threshold.
                 Don't use ``query`` when value is a DataArray, a Dataset or a path to a
                 netcdf/zarr storage, instead use ``operator``, ``value`` and ``unit``.
                 ``query`` supersede `operator`, `value` and `unit` parameters.
   :type query: str | None = None
   :param operator: keyword argument only.
                    The operator either as an instance of Operator or as a compatible string.
                    See :py:class:`OperatorRegistry` for the list of all operators.
                    When ``query`` is None and operator is None, the default ``Operator.REACH`` is
                    used.
   :type operator: Operator | str = None
   :param value: keyword argument only.
                 The threshold value(s), default to None.
                 It can be:
                 * a simple scalar threshold
                 * a percentile that will be computed per-grid cell (in combinaison with `unit`)
                 * per-grid cell thresholds defined by a DataArray, a Dataset or a string path to
                 a netcdf/zarr.
                 * a sequence of scalars, the indicator will then be computed for each value and
                 a specific dimension will be created (also work with percentiles).
   :type value: str | float | int | Dataset | DataArray | Sequence[float | int | str] | None
   :param unit: Keyword argument only.
                The threshold unit.
                When ``unit`` is None, if ``value`` is a dataset and a "units"
                can be read from its `attrs`, this unit will be used. If value is a scalar or
                a sequence of scalar, the exceedance will be computed by assuming threshold has
                the same unit as the studied value is it compared to.
                When unit is a string it must be a valid unit of our shared pint registry with
                xclim or a special percentile unit:
                * "doy_per" for day of year percentiles (in ECAD, used for temperature indices
                such as TX90p)
                * "period_per" for per period percentiles (in ECAD, used for rain indices such
                as R75p)
   :type unit: str | None = None
   :param threshold_min_value: A minimum value used to pre-filter computed threshold values.
                               This is particularly useful to compute a percentile threshold for rain where
                               dry days are usually ignored. In that case threshold_min_value would be set to
                               "1 mm/day".
                               If threshold_min_value is a number, ``unit`` is used to quantify
                               ``threshold_min_value``.
   :type threshold_min_value: str | float | pint.Quantity
   :param offset: Optional. An offset applied to the threshold. This is particularly useful when
                  the threshold is an existing dataset (netcdf file or zarr store) and the data
                  should be compared to this dataset + an offset
                  (e.g. to compute days when T > 5 degC above normal)
   :type offset: float | None
   :param kwargs: Additional arguments to build a PercentileThreshold.
                  See :py:class:`PercentileThreshold` constructor for the complete list
                  of possible arguments.

   .. rubric:: Examples

   .. code-block:: python

       # -- Scalar threshold
       scalar_t = build_threshold(">= 30 degC")
       assert isinstance(scalar_t, BasicThreshold)

       # -- Daily percentile threshold
       doy_t = build_threshold(">= 30 doy_per")
       assert isinstance(doy_t, PercentileThreshold)

       # -- Per grid-cell threshold, with offset
       grided_t = build_threshold(
           operator=">=", value="path/to/tasmax_thresholds.nc", unit="K", offset=5
       )
       assert isinstance(grided_t, BasicThreshold)

       # -- Daily percentile threshold, from a file
       tasmax = xarray.open_dataset("path/to/tasmax_thresholds.nc").tasmax
       doys = xclim.core.calendar.percentile_doy(tasmax)
       doy_file_t = build_threshold(operator=">=", value=doys)
       assert isinstance(doy_file_t, PercentileThreshold)

       # -- Bounded threshold
       bounded_t = build_threshold(">= -20 degree AND <= 20 degree ")
       # equivalent to:
       x = build_threshold(">= -20 degree")
       y = build_threshold("<= 20 degree")
       bounded_t2 = x & y
       assert bounded_t == bounded_t2
       # equivalent to:
       bounded_t3 = build_threshold(thresholds=[x, y], logical_link="AND")
       assert bounded_t == bounded_t3
       assert isinstance(bounded_t, BoundedThreshold)

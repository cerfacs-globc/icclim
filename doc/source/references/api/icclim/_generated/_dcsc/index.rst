:py:mod:`icclim._generated._dcsc`
=================================

.. py:module:: icclim._generated._dcsc

.. autoapi-nested-parse::

   icclim's API for dcsc indices.

   This module has been auto-generated.
   To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
   This module exposes each climate index as individual functions for convenience.



Module Contents
---------------

.. py:function:: tav(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TAV.

       Moyenne de la température moyenne
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: txav(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TXAV.

       Moyenne de la température maximale
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: trav(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TRAV.

       Moyenne de l'amplitude thermique
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tx10(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TX10.

       Extrême froid de la température maximale journalière (10e centile de la température maximale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tx90(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TX90.

       Extrême chaud de la température maximale journalière (90e centile de la température maximale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tn10(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TN10.

       Extrême froid de la température minimale  journalière (10e centile de la température minimale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tn90(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TN90.

       Extrême chaud de la température minimale journalière (90e centile de la température minimale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tnfd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TNFD.

       Nombre de jours de gel (température minimale <= 0°C)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: txfd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TXFD.

       Nombre de jours sans dégel (température maximale <= 0°C)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: sd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SD.

       Nombre de journées d'été (température maximale > 25°C)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tx35(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TX35.

       Nombre de jours de forte chaleur (température maximale > 35°C)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tr(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TR.

       Nombre de nuits tropicales (température minimale > 20°C)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: txnd(in_files: icclim._core.model.icclim_types.InFileLike, normal: str | collections.abc.Sequence[str] | xarray.Dataset | xarray.DataArray, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, normal_var_name: str | None = None) -> xarray.Dataset

   TXND.

       Nombre de jours anormalement chauds (température maximale supérieure de plus de 5°C à la normale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity
   :param normal: The normal to be compared to
   :type normal: Union[str, Sequence[str], Dataset, DataArray]
   :param normal_var_name: The name of the normal's variable.
                           If missing, icclim will try to guess which variable must beused in the
                           `normal` dataset.
   :type normal_var_name: str | None, optional

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tnht(in_files: icclim._core.model.icclim_types.InFileLike, normal: str | collections.abc.Sequence[str] | xarray.Dataset | xarray.DataArray, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, normal_var_name: str | None = None) -> xarray.Dataset

   TNHT.

       Nombre de nuits anormalement chaudes (température minimale supérieure de plus de 5°C à la normale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity
   :param normal: The normal to be compared to
   :type normal: Union[str, Sequence[str], Dataset, DataArray]
   :param normal_var_name: The name of the normal's variable.
                           If missing, icclim will try to guess which variable must beused in the
                           `normal` dataset.
   :type normal_var_name: str | None, optional

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tnnd(in_files: icclim._core.model.icclim_types.InFileLike, normal: str | collections.abc.Sequence[str] | xarray.Dataset | xarray.DataArray, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, normal_var_name: str | None = None) -> xarray.Dataset

   TNND.

       Nombre de jours anormalement froids (température minimale inférieure de plus de 5°C à la normale)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity
   :param normal: The normal to be compared to
   :type normal: Union[str, Sequence[str], Dataset, DataArray]
   :param normal_var_name: The name of the normal's variable.
                           If missing, icclim will try to guess which variable must beused in the
                           `normal` dataset.
   :type normal_var_name: str | None, optional

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: tncwd(in_files: icclim._core.model.icclim_types.InFileLike, normal: str | collections.abc.Sequence[str] | xarray.Dataset | xarray.DataArray, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, normal_var_name: str | None = None) -> xarray.Dataset

   TNCWD.

       Nombre de jours d'une vague de froid (température min < de plus de 5°C à la normale pdt au moins 5j consécutifs)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity
   :param normal: The normal to be compared to
   :type normal: Union[str, Sequence[str], Dataset, DataArray]
   :param normal_var_name: The name of the normal's variable.
                           If missing, icclim will try to guess which variable must beused in the
                           `normal` dataset.
   :type normal_var_name: str | None, optional

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: txhwd(in_files: icclim._core.model.icclim_types.InFileLike, normal: str | collections.abc.Sequence[str] | xarray.Dataset | xarray.DataArray, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, normal_var_name: str | None = None) -> xarray.Dataset

   TXHWD.

       Nombre de jours d'une vague de chaleur (température max > de plus de 5°C à la normale pdt au moins 5j consécutifs)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity
   :param normal: The normal to be compared to
   :type normal: Union[str, Sequence[str], Dataset, DataArray]
   :param normal_var_name: The name of the normal's variable.
                           If missing, icclim will try to guess which variable must beused in the
                           `normal` dataset.
   :type normal_var_name: str | None, optional

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: hdd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   HDD.

       Degrés-jours de chauffage (Cumul sur la période des écarts négatifs au seuil de < 17°C par la température qt moyenne)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: cdd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CDD.

       Degrés-jours de climatisation(Cumul sur la période des dépassements du seuil de > 18°C par la température qt moyenne)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pav(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PAV.

       Précipitations quotidiennes moyennes
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pint(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PINT.

       Précipitation moyenne des jours pluvieux (RR > 1 mm)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: rr(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   RR.

       Cumul de précipitation
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: rr1mm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   RR1MM.

       Nombre de jours de pluie (précipitations >= 1 mm)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pn20mm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PN20MM.

       Nombre de jours de fortes précipitations (précipitations >= 20 mm)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pxcdd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PXCDD.

       Période de sécheresse (Max [Nbj consécutifs RR < 1 mm])
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pxcwd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PXCWD.

       Nombre maximum de jours pluvieux consécutifs (Max [Nbj consécutifs RR > 1 mm])
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: r99(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R99.

       Nombre de jours de précipitations extrêmes
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pfl90(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PFL90.

       Fraction des précipitations journalières intenses
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pq90(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PQ90.

       Précipitation quotidienne intense (90e centile des précipitations)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: pq99(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PQ99.

       Précipitation quotidienne extrême (99e centile des précipitations)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: ffav(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FFAV.

       Écart de la vitesse du vent moyenne journalière (par rapport à une periode de référence)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
   :param date_event: When True the date of the event (such as when a maximum is reached) will be
                      stored in coordinates variables.
                      **warning** This option may significantly slow down computation.
   :type date_event: bool
   :param logs_verbosity: ``optional`` Configure how verbose icclim is.
                          Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
   :type logs_verbosity: str | Verbosity

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: ff98(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FF98.

       Nombre de jours de vent fort (vent ≥ 98e centile de la période de référence)
       Source: Portail DRIAS, DCSC, MeteoFrance.


   :param in_files: Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
                    or path to zarr store, or xarray.Dataset or xarray.DataArray.
   :type in_files: str | list[str] | Dataset | DataArray | InputDictionary
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
   :param only_leap_years: ``optional`` Option for February 29th (default: False).
   :type only_leap_years: bool
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param interpolation: ``optional`` Interpolation method to compute percentile values:
                         ``{"linear", "median_unbiased"}``
                         Default is "median_unbiased", a.k.a type 8 or method 8.
                         Ignored for non percentile based indices.
   :type interpolation: str | QuantileInterpolation | None
   :param netcdf_version: ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
   :type netcdf_version: str | NetcdfVersion
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

   .. rubric:: Notes

   This function has been auto-generated.

:py:mod:`icclim._generated._ecad`
=================================

.. py:module:: icclim._generated._ecad

.. autoapi-nested-parse::

   icclim's API for ECAD indices.

   This module has been auto-generated.
   To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
   This module exposes each climate index as individual functions for convenience.



Module Contents
---------------

.. py:function:: tg(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TG.

       Mean of daily mean temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tn(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TN.

       Mean of daily minimum temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tx(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TX.

       Mean of daily maximum temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: dtr(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   DTR.

       Mean Diurnal Temperature Range.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: etr(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   ETR.

       Intra-period extreme temperature range.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: vdtr(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   vDTR.

       Mean day-to-day variation in Diurnal Temperature Range.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: su(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SU.

       Number of Summer Days (Tmax > 25C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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

       Number of Tropical Nights (Tmin > 20C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: wsdi(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   WSDI.

       Warm-spell duration index (days).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tg90p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TG90p.

       Days when Tmean > 90th percentile.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tn90p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TN90p.

       Days when Tmin > 90th percentile.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tx90p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TX90p.

       Days when Tmax > 90th daily percentile.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: txx(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TXx.

       Maximum daily maximum temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tnx(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TNx.

       Maximum daily minimum temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: csu(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CSU.

       Maximum number of consecutive summer days (Tmax >25 C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: gd4(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   GD4.

       Growing degree days (sum of Tmean > 4 C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: fd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FD.

       Number of Frost Days (Tmin < 0C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: cfd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CFD.

       Maximum number of consecutive frost days (Tmin < 0 C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: hd17(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   HD17.

       Heating degree days (sum of Tmean < 17 C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: id(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   ID.

       Number of sharp Ice Days (Tmax < 0C).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tg10p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TG10p.

       Days when Tmean < 10th percentile.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tn10p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TN10p.

       Days when Tmin < 10th percentile.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tx10p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TX10p.

       Days when Tmax < 10th percentile.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: txn(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TXn.

       Minimum daily maximum temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: tnn(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   TNn.

       Minimum daily minimum temperature.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: csdi(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CSDI.

       Cold-spell duration index (days).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: cdd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CDD.

       Maximum consecutive dry days (Precip < 1mm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: prcptot(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PRCPTOT.

       Total precipitation during Wet Days.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: rr1(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   RR1.

       Number of Wet Days (precip >= 1 mm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: sdii(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SDII.

       Average precipitation during Wet Days (SDII).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: cwd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CWD.

       Maximum consecutive wet days (Precip >= 1mm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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

       Precipitation sum (mm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r10mm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R10mm.

       Number of heavy precipitation days (Precip >=10mm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r20mm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R20mm.

       Number of very heavy precipitation days (Precip >= 20mm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: rx1day(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   RX1day.

       maximum 1-day total precipitation.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: rx5day(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   RX5day.

       maximum 5-day total precipitation.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r75p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R75p.

       Days with RR > 75th percentile of daily amounts. (moderate wet days) (d)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r75ptot(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R75pTOT.

       Precipitation fraction due to moderate wet days. (> 75th percentile)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r95p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R95p.

       Days with RR > 95th percentile of daily amounts. (very wet days) (days)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r95ptot(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R95pTOT.

       Precipitation fraction due to very wet days (> 95th percentile).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r99p(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R99p.

       Days with RR > 99th percentile of daily amounts. (extremely wet days)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: r99ptot(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   R99pTOT.

       Precipitation fraction due to extremely wet days. (> 99th percentile)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: sd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SD.

       Mean of daily snow depth.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: sd1(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SD1.

       Snow days (SD >= 1 cm).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: sd5cm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SD5cm.

       Number of days with snow depth >= 5 cm.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: sd50cm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SD50cm.

       Number of days with snow depth >= 50 cm.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: cd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CD.

       Days with TG < 25th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (cold/dry days).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: cw(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   CW.

       Days with TG < 25th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (cold/wet days).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: wd(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   WD.

       Days with TG > 75th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (warm/dry days).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: ww(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   WW.

       Days with TG > 75th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (warm/wet days).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: fxx(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FXx.

       Maximum value of daily maximum wind gust.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: fg6bft(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FG6Bft.

       Days with daily averaged wind ≥ 6 Bft (10.8 m s-1).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: fgcalm(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FGcalm.

       Calm days, days with daily averaged wind <= 2 m s-1.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: fg(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   FG.

       Mean of daily mean wind strength.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: ddnorth(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   DDnorth.

       Days with northerly winds (DD > 315° or DD ≤ 45°).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: ddeast(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   DDeast.

       Days with easterly winds (45° < DD <= 135°).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: ddsouth(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   DDsouth.

       Days with southerly winds (135° < DD <= 225°).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: ddwest(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   DDwest.

       Days with westerly winds (225° < DD <= 315°).
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: gsl(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   GSL.

       Growing season length.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: spi6(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SPI6.

       6-Month Standardized Precipitation Index.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: spi3(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SPI3.

       3-Month Standardized Precipitation Index.
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: pp(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   PP.

       Mean of daily sea level pressure (hPa)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: ss(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   SS.

       Sunshine duration (hours)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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


.. py:function:: rh(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, ignore_Feb29th: bool = False, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   RH.

       Mean of daily relative humidity (%)
       Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11.


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

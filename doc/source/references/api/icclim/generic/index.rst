:py:mod:`icclim.generic`
========================

.. py:module:: icclim.generic

.. autoapi-nested-parse::

   Generic indices.

   The generic indices public API, via `icclim.generic` package, is generated from the
   `icclim.generic.registry.GenericIndicatorRegistry` registry definitions.
   icclim's generic indices are a generalization of the climate indices found in
   ECAD and DCSC's registries.
   They can be computed on any dataset and make use of the `Threshold` interface
   to enable the creation of personalized indices.
   The parameters of the functions are specialized to each index but are all taken from
   `icclim.main.index` general function.
   In other words, the generic indices in `icclim.generic` package are specializations
   of `icclim.main.index` for ECAD indices.

   .. rubric:: Examples

   >>> from icclim.generic import count_occurrences
   >>> from icclim import build_threshold
   >>> thresh = build_threshold(">= 25 °C and <= 30 °C")
   >>> result = count_occurrences("tas.nc", thresh).compute()
   >>> print(result.count_occurrences)



Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   registry/index.rst


Package Contents
----------------

.. py:function:: count_occurrences(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   Count occurrences where threshold(s) are met (e.g. SU, Tx90p, RR1).

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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: max_consecutive_occurrence(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   max_consecutive_occurrence.

       Count the maximum number of consecutive occurrences when threshold(s) are met (e.g. CDD, CSU, CWD).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: sum_of_spell_lengths(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, min_spell_length: int | None = 6) -> xarray.Dataset

   sum_of_spell_lengths.

       Sum the lengths of each consecutive occurrence spell when threshold(s) are met. The minimum spell length is controlled by `min_spell_length` (e.g. WSDI, CSDI).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param min_spell_length: ``optional`` Minimum spell duration to be taken into account when computing
                            the sum_of_spell_lengths.
   :type min_spell_length: int
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: excess(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   excess.

       Compute the excess over the given threshold. The excess is `sum(x[x>t] - t)` where x is the studied variable and t the threshold (e.g. GD4).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: deficit(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   deficit.

       Compute the deficit below the given threshold. The deficit is `sum(t - x[x<t])` where x is the studied variable and t the threshold (e.g. HD17).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: fraction_of_total(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   fraction_of_total.

       Compute the fraction of values meeting threshold(s) over the sum of every values (e.g. R75pTOT, R95pTOT).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: maximum(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   maximum.

       Maximum of values that met threshold(s), if threshold(s) are given (e.g. Txx, Tnx).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: minimum(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   minimum.

       Minimum of values that met threshold(s), if threshold(s) are given (e.g. Txn, Tnn).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: average(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   average.

       Average of values that met threshold(s), if threshold(s) are given (e.g. Tx, Tn)


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: sum(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   sum.

       Sum of values that met threshold(s), if threshold(s) are given (e.g. PRCPTOT, RR).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: standard_deviation(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   standard_deviation.

       Standard deviation of values that met threshold(s), if threshold(s) are given.


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: max_of_rolling_sum(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, rolling_window_width: int | None = 5) -> xarray.Dataset

   max_of_rolling_sum.

       Maximum of rolling sum over time dimension (e.g. RX5DAY: maximum 5 days window of precipitation accumulation).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param rolling_window_width: ``optional`` Window width of the rolling window for indicators such as
                                `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
   :type rolling_window_width: int
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: min_of_rolling_sum(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, rolling_window_width: int | None = 5) -> xarray.Dataset

   min_of_rolling_sum.

       Minimum of rolling sum over time dimension.


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param rolling_window_width: ``optional`` Window width of the rolling window for indicators such as
                                `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
   :type rolling_window_width: int
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: max_of_rolling_average(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, rolling_window_width: int | None = 5) -> xarray.Dataset

   max_of_rolling_average.

       Maximum of rolling average over time dimension.


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param rolling_window_width: ``optional`` Window width of the rolling window for indicators such as
                                `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
   :type rolling_window_width: int
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: min_of_rolling_average(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, rolling_window_width: int | None = 5) -> xarray.Dataset

   min_of_rolling_average.

       Minimum of rolling average over time dimension.


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param rolling_window_width: ``optional`` Window width of the rolling window for indicators such as
                                `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
   :type rolling_window_width: int
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: mean_of_difference(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   mean_of_difference.

       Average of the difference between two variables, or one variable and it's reference period values (e.g. DTR: `mean(tasmax - tasmin)`).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: difference_of_extremes(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   difference_of_extremes.

       Difference of extremes between two variables, or one variable and it's reference period values. The extremes are always `maximum` for the first variable and `minimum` for the second variable (e.g. ETR: `max(tasmax) - min(tasmin)`).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: mean_of_absolute_one_time_step_difference(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   mean_of_absolute_one_time_step_difference.

       Average of the absolute one time step by one time step difference between two variables, or one variable and it's reference period values (e.g. vDTR: `mean((tasmax[i] - tasmin[i]) - (tasmax[i-1] - tasmin[i-1])` ; where i is the day of measure).


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: difference_of_means(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, sampling_method: icclim._core.model.icclim_types.SamplingMethodLike = 'resample') -> xarray.Dataset

   difference_of_means.

       Difference of the average between two variables, or one variable and it's reference period values (e.g. anomaly: `mean(tasmax) - mean(tasmax_ref]))`.


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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
   :param sampling_method: Choose whether the output sampling configured in `slice_mode` is a
                           `groupby` operation or a `resample` operation (as per xarray definitions).
                           Possible values:
                           ``{"groupby", "resample", "groupby_ref_and_resample_study"}``
                           (default: "resample")
                           `groupby_ref_and_resample_study` may only be used when computing the
                           `difference_of_means` (a.k.a the anomaly).
   :type sampling_method: str

   .. rubric:: Notes

   This function has been auto-generated.


.. py:function:: percentile(in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, threshold: str | icclim._core.model.threshold.Threshold | collections.abc.Sequence[str | icclim._core.model.threshold.Threshold] | None = None, ignore_Feb29th: bool = False, out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False) -> xarray.Dataset

   percentile.

       Percentile of a variable.


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
   :param threshold: ``optional`` User defined threshold for certain indices.
                     Default depend on the index, see their individual definition.
                     When a list of threshold is provided, the index will be computed for each
                     thresholds.
   :type threshold: float | list[float] | None
   :param ignore_Feb29th: ``optional`` Ignoring or not February 29th (default: False).
   :type ignore_Feb29th: bool
   :param out_unit: ``optional`` Output unit for certain indices: "days" or "%"
                    (default: "days").
   :type out_unit: str | None
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


.. py:function:: custom_index(user_index: icclim._core.legacy.user_index.model.UserIndexDict, in_files: icclim._core.model.icclim_types.InFileLike, var_name: str | collections.abc.Sequence[str] | None = None, slice_mode: icclim._core.model.icclim_types.FrequencyLike | icclim._core.frequency.Frequency = 'year', time_range: collections.abc.Sequence[datetime.datetime | str] | None = None, out_file: str | None = None, base_period_time_range: collections.abc.Sequence[datetime.datetime] | collections.abc.Sequence[str] | None = None, doy_window_width: int = 5, only_leap_years: bool = False, ignore_Feb29th: bool = False, interpolation: str | icclim._core.model.quantile_interpolation.QuantileInterpolation = 'median_unbiased', out_unit: str | None = None, netcdf_version: str | icclim._core.model.netcdf_version.NetcdfVersion = 'NETCDF4', save_thresholds: bool = False, logs_verbosity: icclim.logger.Verbosity | str = 'LOW', date_event: bool = False, min_spell_length: int | None = 6, rolling_window_width: int | None = 5, sampling_method: icclim._core.model.icclim_types.SamplingMethodLike = 'resample') -> xarray.Dataset

   Compute custom indices using simple operators.

       Use the `user_index` parameter to describe how the index should be computed.
       You can find some examples in icclim documentation at :ref:`custom indices`


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

   .. rubric:: Notes

   This function has been auto-generated.

:py:mod:`icclim._core.input_parsing`
====================================

.. py:module:: icclim._core.input_parsing

.. autoapi-nested-parse::

   Module to parse input data and make it usable for icclim.



Module Contents
---------------

.. py:class:: PercentileDataArray(data: Any = dtypes.NA, coords: collections.abc.Sequence[collections.abc.Sequence | pandas.Index | DataArray] | collections.abc.Mapping | None = None, dims: str | collections.abc.Iterable[collections.abc.Hashable] | None = None, name: collections.abc.Hashable | None = None, attrs: collections.abc.Mapping | None = None, indexes: collections.abc.Mapping[Any, xarray.core.indexes.Index] | None = None, fastpath: bool = False)




   Wrap xarray DataArray for percentiles values.

   .. py:method:: is_compatible(source: xarray.DataArray) -> bool
      :classmethod:

      Evaluate whether PecentileDataArray is conformant with expected fields.

      A PercentileDataArray must have climatology_bounds attributes and either a
      quantile or percentiles coordinate, the window is not mandatory.


   .. py:method:: from_da(source: xarray.DataArray, climatology_bounds: list[str] | None = None) -> PercentileDataArray
      :classmethod:

      Create a PercentileDataArray from a xarray.DataArray.

      :param source: A DataArray with its content containing percentiles values.
                     It must also have a coordinate variable percentiles or quantile.
      :type source: xr.DataArray
      :param climatology_bounds: Optional. A List of size two which contains the period on which the
                                 percentiles were computed. See
                                 `xclim.core.calendar.build_climatology_bounds`
                                 to build this list from a DataArray.
      :type climatology_bounds: list[str]

      :returns: The initial `source` DataArray but wrap by PercentileDataArray class.
                The data is unchanged and only climatology_bounds attributes is overridden
                if q new value is given in inputs.
      :rtype: PercentileDataArray



.. py:function:: guess_var_names(ds: xarray.core.dataset.Dataset, var_names: str | collections.abc.Sequence[str] | None, standard_index: icclim._core.model.standard_index.StandardIndex | None) -> list[collections.abc.Hashable]

   Attempt to guess the variable names from the dataset and the standard index.

   :param ds: The dataset to guess the variable names from.
   :type ds: Dataset
   :param var_names: The variable names to use. If None, the function will attempt to guess the
                     variable names.
   :type var_names: str | Sequence[str] | None
   :param standard_index: The standard index to use to guess the variable names.
   :type standard_index: StandardIndex | None

   :returns: The list of guessed variable names.
   :rtype: list[Hashable]


.. py:function:: read_dataset(in_files: icclim._core.model.icclim_types.InFileBaseType, standard_var: icclim._core.model.standard_variable.StandardVariable | None = None, var_name: str | collections.abc.Sequence[str] | None = None) -> xarray.core.dataset.Dataset

   Read a dataset from input files.

   :param in_files: The input files to read the dataset from. It can be a single file path,
                    a list of file paths, a glob pattern, a netCDF file, or a Zarr store.
   :type in_files: InFileBaseType
   :param standard_var: The standard variable to use for parsing the dataset, by default None.
   :type standard_var: StandardVariable | None, optional
   :param var_name: The variable name(s) to extract from the dataset, by default None.
   :type var_name: str | Sequence[str] | None, optional

   :returns: The parsed dataset.
   :rtype: Dataset

   :raises NotImplementedError: If the format of `in_files` is not recognized.

   .. rubric:: Notes

   This function supports reading datasets from various file formats, including
   netCDF and Zarr. It can handle single files, multiple files, and glob patterns.
   If `standard_var` is provided, it will use the specified standard variable for
   parsing the dataset. If `var_name` is provided, it will extract the specified
   variable(s) from the dataset.

   .. rubric:: Examples

   >>> files = ["data1.nc", "data2.nc"]
   >>> ds = read_dataset(files, standard_var="temperature", var_name="temp")


.. py:function:: update_to_standard_coords(ds: xarray.core.dataset.Dataset) -> xarray.core.dataset.Dataset

   Mutate input ds to use more icclim friendly coordinate names.


.. py:function:: is_zarr_path(path: icclim._core.model.icclim_types.InFileBaseType) -> bool

   Check if the input path is a Zarr store.


.. py:function:: is_netcdf_path(path: icclim._core.model.icclim_types.InFileBaseType) -> bool

   Check if the input path is a netCDF file.


.. py:function:: is_glob_path(path: icclim._core.model.icclim_types.InFileBaseType) -> bool

   Check if the input path is a glob pattern.


.. py:function:: standardize_percentile_dim_name(per_da: xarray.core.dataarray.DataArray) -> xarray.core.dataarray.DataArray

   Standardizes the name of the percentile dimension in the input DataArray.

   :param per_da: The input DataArray containing percentile data.
   :type per_da: DataArray

   :returns: The input DataArray with the percentile dimension standardized.
   :rtype: DataArray

   :raises InvalidIcclimArgumentError: If the percentile data does not contain a recognizable percentiles dimension.

   .. rubric:: Notes

   This function standardizes the name of the percentile dimension in the input
   DataArray to "percentiles".

   If the percentile dimension name contains the word "quantile", the values in the
   "percentiles" coordinate are multiplied by 100.


.. py:function:: get_date_to_iso_format(in_date: str | datetime.datetime) -> str

   Get a date in ISO format from a string or a datetime object.

   :param in_date: A string representing a date or a datetime object.
   :type in_date: str | datetime

   :returns: A string representing a date in ISO format.
   :rtype: str


.. py:function:: read_clim_bounds(climatology_bounds: collections.abc.Sequence[str, str] | None, per_da: xarray.DataArray) -> list[str]

   Read climatology bounds from input.

   The climatology bounds represent the start and end dates of the climatology period.

   :param climatology_bounds: The climatology bounds as a sequence of two strings representing the start and
                              end dates.
                              If None, the climatology bounds will be retrieved from the `climatology_bounds`
                              attribute of `per_da`.
   :type climatology_bounds: sequence of str or None
   :param per_da: The input data array.
   :type per_da: xr.DataArray

   :returns: A list of climatology bounds converted to ISO format.
   :rtype: list of str

   :raises InvalidIcclimArgumentError: If the length of `climatology_bounds` is not equal to 2.

   .. rubric:: Notes

   If `climatology_bounds` is None, the function will attempt to retrieve the
   climatology bounds from the `climatology_bounds` attribute of `per_da`.


.. py:function:: build_input_dict(in_files: icclim._core.model.icclim_types.InFileLike, var_names: collections.abc.Sequence[str] | None, threshold: icclim._core.model.threshold.Threshold | collections.abc.Sequence[icclim._core.model.threshold.Threshold] | None, standard_index: icclim._core.model.standard_index.StandardIndex | None) -> dict[str, icclim._core.model.in_file_dictionary.InFileDictionary]

   Build an input dictionary based on the provided input files and variables.

   The input dictionary is used to map which input files correspond to which variables.

   :param in_files: The input files. It can be a dictionary where the keys represent the variable
                    names and the values represent the file paths, or a single file path.
   :type in_files: InFileLike
   :param var_names: The variable names. If `in_files` is a dictionary, this parameter must be None.
                     Otherwise, it should be a sequence of variable names corresponding to the single
                     file path.
   :type var_names: Sequence[str] | None
   :param threshold: The threshold values. It can be a single threshold value, a sequence of
                     threshold values, or None.
   :type threshold: Threshold | Sequence[Threshold] | None
   :param standard_index: The standard index. It can be a standard index value or None.
   :type standard_index: StandardIndex | None

   :returns: The built input dictionary.
   :rtype: dict[str, InFileDictionary]

   :raises InvalidIcclimArgumentError: If `var_names` is not None when `in_files` is a dictionary.

   .. rubric:: Notes

   - If `in_files` is a dictionary, the dictionary keys are used as variable names.
   - If `in_files` is a dictionary and the dictionary values are also dictionaries,
     the input dictionary is returned as is.
   - If `in_files` is a dictionary and the dictionary values are file paths,
     the input dictionary is built using the file paths and variable names.
   - If `in_files` is a single file path and `var_names` is a single variable name,
     the input dictionary is built using the file path and variable name.


.. py:function:: find_standard_vars(ds: xarray.core.dataset.Dataset) -> list[collections.abc.Hashable]

   Find standard variables in a dataset.

   :param ds: The input dataset.
   :type ds: Dataset

   :returns: A list of standard variables found in the dataset.
   :rtype: list[Hashable]


.. py:function:: guess_standard_variable(data: xarray.core.dataarray.DataArray) -> icclim._core.model.standard_variable.StandardVariable | None

   Guesses the standard variable based on the metadata of `data`.

   :param data: The input data.
   :type data: DataArray

   :returns: The guessed standard variable, or None if no standard variable is found.
   :rtype: StandardVariable or None

   .. rubric:: Notes

   StandardVariableRegistry is used as a lookup table to find the standard variable
   using the dataarray name or standard name attribute.


.. py:function:: is_precipitation_amount(source: xarray.DataArray) -> bool

   Return True if the source is a precipitation amount.

   :param source: A DataArray object.
   :type source: xr.DataArray

   :returns: True if the source is a precipitation amount, False otherwise.
   :rtype: bool

   .. rubric:: Notes

   Using pint, the rate is a quantity with a dimensionality of [time]^-1.


.. py:function:: build_studied_data(original_da: xarray.core.dataarray.DataArray, time_range: collections.abc.Sequence[datetime.datetime | str] | None, ignore_Feb29th: bool, default_units: str | None) -> xarray.core.dataarray.DataArray

   Preprocesss the input data to select the period of interest.

   :param original_da: The original data array.
   :type original_da: DataArray
   :param time_range: The time range to select from the data array. If None, the entire time range is
                      used.
   :type time_range: Sequence[datetime | str] | None
   :param ignore_Feb29th: Whether to ignore February 29th when processing the data.
   :type ignore_Feb29th: bool
   :param default_units: The default units to use for the data array if it is uniteless.
                         If None and the data array is uniteless, "units" attribute remains unset.
   :type default_units: str | None

   :returns: The processed data array.
   :rtype: DataArray

   :raises InvalidIcclimArgumentError: If the given `time_range` is out of the dataset time period.


.. py:function:: get_name_of_first_var(ds: xarray.core.dataset.Dataset) -> str

   Get the name of the first variable in the given Dataset.

   :param ds: The input Dataset.
   :type ds: Dataset

   :returns: The name of the first variable in the Dataset.
   :rtype: str

   :raises IndexError: If the Dataset is empty.


.. py:function:: is_dataset_path(query: icclim._core.model.icclim_types.InFileBaseType) -> bool

   Check if the given query is a valid dataset path.

   :param query: The query to check. It can be a single path or a list/tuple of paths.
   :type query: InFileBaseType

   :returns: True if the query is a valid dataset path, False otherwise.
   :rtype: bool

   .. rubric:: Notes

   A valid dataset path can be either a NetCDF path, a Zarr path, a glob path, or a
   list/tuple of valid paths.


.. py:function:: build_reference_da(original_da: xarray.core.dataarray.DataArray, base_period_time_range: collections.abc.Sequence[datetime.datetime | str] | None, only_leap_years: bool, percentile_min_value: pint.Quantity | None) -> xarray.core.dataarray.DataArray

   Build a reference DataArray to be used for percentile doy computation.

   :param original_da: The DataArray used as a base.
   :type original_da: DataArray
   :param base_period_time_range: The period to slice in the base DataArray.
   :type base_period_time_range: Sequence[datetime | str] | None
   :param only_leap_years: Flag to only use leap years (years with 366 days).
   :type only_leap_years: bool
   :param percentile_min_value: Optional, if set will replace every value from the base DataArray that are below
                                the `percentile_min_value` with np.nan.
   :type percentile_min_value: Quantity | None


.. py:function:: get_dataarray_from_dataset(var_name: str | None, value: xarray.Dataset | str, standard_var: icclim._core.model.standard_variable.StandardVariable | None = None) -> xarray.DataArray

   Extract a DataArray from a Dataset based on the provided variable name.

   :param var_name: The name of the variable to extract from the Dataset. If None, the function
                    will try to guess the variable based on the Dataset's contents.
   :type var_name: str or None
   :param value: The Dataset object or the path to the Dataset file.
   :type value: xr.Dataset or str
   :param standard_var: The standard variable used to find a matching variable in the Dataset.
   :type standard_var: StandardVariable

   :returns: The extracted DataArray.
   :rtype: xr.DataArray

   :raises InvalidIcclimArgumentError: If the variable name cannot be guessed and `var_name` is None.

   .. rubric:: Notes

   This function can be used to extract a specific variable from a Dataset object
   or a Dataset file. If `var_name` is None, the function will try to guess the
   variable based on the Dataset's contents.


.. py:function:: _guess_dataset_var_names(standard_index: icclim._core.model.standard_index.StandardIndex, ds: xarray.core.dataset.Dataset) -> list[collections.abc.Hashable]

   Try to guess the variable names.

   The expected kind of variable of the index is used to guess the variable names.

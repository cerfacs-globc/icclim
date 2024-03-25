:py:mod:`icclim.rechunk`
========================

.. py:module:: icclim.rechunk

.. autoapi-nested-parse::

   Contain the create_optimized_zarr_store context manager.

   This context manager is used to create an "optimized" zarr store from a given input
   dataset. The optimization is done by rechunking the input dataset according to a
   given chunking schema.



Module Contents
---------------

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

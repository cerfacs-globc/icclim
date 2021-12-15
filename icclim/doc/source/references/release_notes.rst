Release history
===============

5.0.0rc2
--------

* Make HD17 expect tas instead of tas_min

5.0.0
-----
We fully rewrote Icclim to benefit from Xclim, Xarray, Numpy and Dask.
A lot of effort has been to minimize the API changes. Thus for all scripts using a former version of icclim
updating to this new version should be smooth.
In fact a few improvements were made on the API:
- We replaced everywhere the french singular word "indice" by the proper english "index". You should get a warning if you still use "indice" such as in "indice_name".
- When ``save_percentile`` is used, the resulting percentiles are saved within the same netcdf file as the climate index.
- Most of the keywords (such as slice_mode, index_name, are now case insensitive to avoid unnecessary errors.
- When ``in_files`` is a list the netcdf are combined to lookup them all the necessary variables.
- When multiple variables are stored into a single ``in_files``, there is no more need to use a list.
- ``in_files`` parameter can now be a Xarray.Dataset directly. In that case, ``out_file`` is ignored.
- ``var_name`` parameter is now optional for ECA&D indices, icclim will try to look for a valid variable depending on the index wanted
- ``transfer_limit_Mbytes`` parameter is now used to adjust how Dask should chunk the dataset.
- The output of ``icclim.index()`` is now the resulting Xarray Dataset of the index computation. ``out_file`` can still be used to write output to a netcdf.
- `logs_verbosity` parameter can now control how much logs icclim will produce. The possible values are {"HIGH", "LOW", "SILENT"}.

Icclim C code has been removed. This makes the installation and maintenance much easier.
Climate indices metadata has benn enriched with Xclim metadata.
With this rewrite a few indices were fixed as they were giving improper results.
Performances have been significantly improved, especially thanks to Dask.

Notes
~~~~~
It is highly recommended to use Dask distributed scheduler to fully benefit from the performance improvements of version
5.0.0.

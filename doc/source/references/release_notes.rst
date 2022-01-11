Release history
===============

5.0.0rc3 (not released)
-----------------------
* [maint] Add github templates for issues and pull requests.
* [maint] Simplify ecad functions output to a single DataArray in most cases.
* [fix] Fix lint for doc conf.
* [fix] Add all requirements to requirements_dev.txt
* [doc] Update Readme from md to rst format. Also changed content.
* [doc] Add a dev documentation article "how to release".
* [doc] Add a dev documentation article "continuous integration".
* [doc] Update installation tutorial.
* [doc] Various improvements in doc wording and display.
* [doc] Start to documente ECA&D indices functions.
* [doc] Add article to distinguish icclim from xclim.

5.0.0rc2
--------

* [fix] Make HD17 expect tas instead of tas_min.
* [fix] Fix performance issue with indices computed on consecutive days such as CDD.
* [maint] Add Github action CI to run unit tests.
* [maint] Add pre-commit CI to fix lint issues on PRs.
* [maint] Update sphinx and remove old static files.
* [doc] Restructure documentation to follow diataxis principles.
* [doc] Add some articles to documentation.

5.0.0rc1
--------
We fully rewrote icclim to benefit from Xclim, Xarray, Numpy and Dask.
A lot of effort has been to minimize the API changes.
Thus for all scripts using a former version of icclim updating to this new version should be smooth.

In fact, we made a few improvements on the API
    - We replaced everywhere the french singular word "indice" by the proper english "index". You should get a warning if you still use "indice" such as in "indice_name".
    - When ``save_percentile`` is used, the resulting percentiles are saved within the same netcdf file as the climate index.
    - Most of the keywords (such as slice_mode, index_name, are now case insensitive to avoid unnecessary errors.
    - When ``in_files`` is a list the netcdf are combined to lookup them all the necessary variables.
    - When multiple variables are stored into a single ``in_files``, there is no more need to use a list.
    - ``in_files`` parameter can now be a Xarray.Dataset directly. In that case, ``out_file`` is ignored.
    - ``var_name`` parameter is now optional for ECA&D indices, icclim will try to look for a valid variable depending on the index wanted
    - ``transfer_limit_Mbytes`` parameter is now used to adjust how Dask should chunk the dataset.
    - The output of ``icclim.index()`` is now the resulting Xarray Dataset of the index computation. ``out_file`` can still be used to write output to a netcdf.
    - `logs_verbosity` parameter can now control how much logs icclim will produce. The possible values are ``{"HIGH", "LOW", "SILENT"}``.

Additionally
    - icclim C code has also been removed. This makes the installation and maintenance much easier.
    - Climate indices metadata has been enriched with Xclim metadata.
    - With this rewrite a few indices were fixed as they were giving improper results.
    - Performances have been significantly improved, especially thanks to Dask.

Breaking changes
~~~~~~~~~~~~~~~~
Some utility features of icclim has been removed in 5.0.0.
This include `util.regrid` module as well as `util.spatial_stat` module.
For regridding, users are encouraged to try  `xESMF <https://pangeo-xesmf.readthedocs.io/en/latest>`_.
For spatial stats, Xarray provides a `DataArrayWeighted <https://xarray.pydata.org/en/stable/generated/xarray.DataArray.weighted.html>`_


Notes
~~~~~
It is highly recommended to use Dask distributed scheduler to fully benefit from the performance improvements of version
5.0.0.

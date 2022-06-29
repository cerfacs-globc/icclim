Release history
===============

5.2.2
-----
* [maint] Remove constraint on numpy version as numba is now working with numpy 1.22
* [maint] Upgrade to xclim 0.37

5.2.1
-----
* [maint] Made Frequency part of SliceMode union.
* [fix] slice_mode seasonal samplings was giving wrong results for quite a few indices. This has been fixed and the performances should also be improved by the fix.
However, now seasonal slice_mode does not allow to use xclim missing values mechanisms.
* [fix] user_index ExtremeMode config was not properly parsed when a string was used.
* [fix] user_index Anomaly operator was not properly using the `ref_time_range` to setup a reference period as it should.
* [fix] user_index Sum and Mean operators were broken due to a previous refactoring and a lack of unit tests, it is now fixed and tested.
* [maint] Changed how `rechunker` dependency is pinned to add flexibility. We want a version above '0.3' but not the '0.4'.
* [maint] For the newly generate API, on `custom_index` function, the parameter `user_index` is now mandatory.


5.2.0
-----
* [maint] Update release process.
* [enh] Improve `create_optimized_zarr_store` to accept a chunking schema instead of a single dim.
* [enh] Make use of `fsspec` to generalize the storages where `create_optimized_zarr_store` can create its zarr stores.
* [enh] Make CSDI and WSDI threshold configurable using the `threshold` parameter of icclim.index.
* [enh] Add a function in `icclim` namespace for each ECA&D index for convenience.
* [doc] Improve documentation about chunking.
* [fix] `create_optimized_zarr_store` would throw an error when creating the first temp store if the chunks were not unified.

5.1.0
-----
* [maint] **BREAKING CHANGE** Parameter ``out_file`` of icclim.index default value is now ``None``. When None, ``icclim.index`` only returns a xarray.Dataset and does not write to a default netcdf file.
* [enh] Add code coverage in CI. This writes a comment with the full report in the PR.
* [enh] Add coverage and conda badges in Readme.
* [tst] Add unit test for modules ``main``, ``dispatcher``, ``cf_calendar``.
* [fix] Rework ``cf_calendar`` following unit test writing.
* [tst] Add simple integration test for ``icclim.index`` using index "SU".
* [maint] Remove old, unmaintained integration tests and auxiliary tools. See `9ac35c2f`_ for details.
* [maint] Upgrade to xclim 0.34.
* [fix] WSDI and CSDI percentile were computed on the studied period instead of the reference period.
* [maint] Internal refactoring ``icclim.main`` module to ease maintainability.
* [doc] Add contribution guide.
* [enh] Add API endpoint ``icclim.create_optimized_zarr_store``. It is a context manager wrapping `rechunker` in order to rechunk a dataset without any chunk a given `dim` dimension.
* [fix] Add zarr dependency, needed to update zarr store metadata after rechunking.
* [fix] Fix installation from sources. The import in setup.py to get ``__version__`` meant we needed to have the whole environment installed before the moment it is actually installed by ``setup.py``.
* [enh] Add API endpoint ``icclim.indices``. This allows to compute multiple indices at once.
* [maint] Pin `dask` to its versions before `2022.01.1`. This is necessary for rechunker 0.3.3 to work.
* [maint] Update types to use modern python typing syntax.
* [fix] CI was passing even when tests were in failure. This has been fixed.

.. _`9ac35c2f`: https://github.com/cerfacs-globc/icclim/commit/9ac35c2f7bda76b26427fd433a79f7b4334776e7

5.0.2
-----
* [fix] Update extracting script for C3S. imports were broken.
* [doc] Update release process doc.
* [fix] Bug on windows breaking unit tests.
* [fix] Bug on windows unable to get the timezone in our logger.
* [fix] Pin to numpy 1.21 for now. Numba seems to dislike version 1.22
* [fix] LICENCE was still not exactly following Apache guidelines. NOTICE has been removed.


5.0.1
-----
* [fix] Modify LICENCE and NOTICE to follow Apache guidelines. LICENCE has also been renamed to english LICENSE.


5.0.0
-----
We fully rewrote icclim to benefit from Xclim, Xarray, Numpy and Dask.
A lot of effort has been to minimize the API changes.
Thus for all scripts using a former version of icclim updating to this new version should be smooth.

We made a few improvements on the API
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
For regridding, users are encouraged to try `xESMF <https://pangeo-xesmf.readthedocs.io/en/latest>`_ or to use xarray
selection directly.
For spatial stats, Xarray provides a `DataArrayWeighted <https://xarray.pydata.org/en/stable/generated/xarray.DataArray.weighted.html>`_

.. note::
    It is highly recommended to use Dask (eventually with the distributed scheduler) to fully benefit from the performance
    improvements of version 5.0.0.


Release candidates (rc1, rc2, rc3) change logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* [fix] Make HD17 expect tas instead of tas_min.
* [fix] Fix performance issue with indices computed on consecutive days such as CDD.
* [maint] Add Github action CI to run unit tests.
* [maint] Add pre-commit CI to fix lint issues on PRs.
* [maint] Update sphinx and remove old static files.
* [doc] Restructure documentation to follow diataxis principles.
* [doc] Add some articles to documentation.
* [maint] Drop support for python 3.7
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
* [maint] Refactored ecad_functions (removed duplicated code, simplified function signatures...)
* [maint] Refactored IndexConfig to hide some technical knowledge which was leaked to other modules.
* [enh] Made a basic integration of clix-meta yaml to populate the generated docstring for c3s.
* [maint] This makes pyyaml an required dependency of icclim.
* [fix] Fixed an issue with aliasing of "icclim" module and "icclim" package
* [maint] Added some metadata to qualify the ecad_indices and recognize the arguments necessary to compute them.
* [maint] Added readthedocs CI configuration. This is necessary to use python 3.8.
* [enh] Added `tools/extract-icclim-funs.py` script to extract from icclim stand-alone function for each indices.
* [enh] Added `icclim.indices` function (notice plural) to list the available indices.

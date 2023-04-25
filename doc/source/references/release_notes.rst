Release history
===============

6.3.0
-----
* [maint] Upgrade to xclim 0.42 (released on 04/04/2023).

* [fix] **BREAKING CHANGE** The indicators based on the difference between two variables (ecad: DTR, ETR, vDTR and anomaly) gave wrong values due to a bad unit conversion of the output.
  This was for example the case when the input variables are in Kelvin, the difference between the two variables is still in Kelvin but it cannot be converted to degree Celsius with the ususal `+273.15`.
  To workaround this issue, we first convert inputs to the expected output unit and then we compute the index.

* [fix] **BREAKING CHANGE** Indices based on both a percentile threshold and a `threshold_min_value` (for ecad: r75p, r75pTOT, r95p, r95pTOT, r99p, r99pTOT)
  are now computing the exceedance rate on values above `threshold_min_value` as well. Previously this `threshold_min_value` was used to compute the percentile and the total (for rxxpTOT indices)
  but not the exceedance rate.

6.2.0
-----
* [maint] Upgrade and adapt to xclim 0.40.
  Moved PercentileDataArray from xclim to icclim.
  Adapted the unit cenversion to use the hydro context.

* [fix] Pin xclim to exact 0.40 to avoid breaking changes.


6.1.5
-----
* [fix] Bug fix: not assuming longitude and latitude are lon and lat with respect to output metadata. Fix needed to work on E-OBS and other datasets.

6.1.3
-----
* [fix] Bug fix for TNx.

6.1.2
-----
* [fix] Add missing file to properly identify user_indices as a package.

6.1.0
-----
* [fix] Add unit getter/setter for BoundedThreshold.
* [enh] Add ECAD wind indices ``{fxx, fg6bft, fgcalm, fg, ddnorth, ddeast, ddsouth, ddwest}``.
  `ddnorth` and `ddsouth` do not follow the ECAD's ATBD v11 requirements as their definition seems to be wrong in the document.
* [enh] Add generic indicators as stand-alone functions in `icclim` namespace.
* [doc] Add documentation for generic indicators stand-alone functions.
* [doc] Add a recipe "how to" documentation for generic indicators.
* [enh] Add ECAD's indices GSL, SPI3, SPI6 by binding them to xclim's indicators.
* [maint] Upgrade to xclim 0.39.0


6.0.0
-----
* [enh] Add generic indices
* [enh] Make in_files.var.threshold and threshold parameters work with string values (a value with a unit or a percentile stamp)
* [maint] **BREAKING CHANGE** ECAD indices are no longer configurable! Use generic indices instead.
* [fix] **BREAKING CHANGE** ECAD indices CW, CD, WW, WD were computing the precipitation percentiles on day of year
  values where it should have been percentiles of the whole period (excluding dry days). This has been fixed.
* [maint] icclim no longer carries a version of the clix-meta yml file.
  Previously it was used to generate the doc string and a few metadata of ECAD indices.
  It's no longer needed as we have put these metadata within StandardIndex declaration.
* [maint] **BREAKING CHANGE** Removed the `clipped_season` option from `slice_mode`.
  With generic indices, `season` can be used with every indices.
  In particular, spell based indices (e.g. wsdi, cdd) are mapped to `max_consecutive_occurrence` or `sum_of_spell_lengths`
  generic indicators. Both compute the spell length before doing the resampling operation.
  So a spell that start and end outside the output frequency interval is properly accounted for its whole duration.
  That's for example the case of `slice_mode="month"`, a spell that would start in january and end in March,
  would be accounted in january results.
  However, when `slice_mode` is set to a season, where time is clipped and thus where xclim `select_time` is called,
  the behavior is similar to the former `clipped_season`, we first clip the time to the expected season, then we compute the index.
  Thus, events of spells that are before the season bound will be ignored in the results.
* [maint] **BREAKING CHANGE** User index `max_nb_consecutive_events` is also mapped to `max_consecutive_occurrence`, consequently spells are also counted for their whole duration.
* [enh] Make it possible to pass a simple dictionary in `in_files`, merging together basic `in_files` and `var_name` features.
  It looks like `in_files={"tasmax": "tasmax.nc", "tasmin": "tasmin.zarr"}`
* [enh] Add `min_spell_length` parameter to index API in order to control the minimum duration of spells in `sum_of_spell_lengths`.
* [enh] Add `rolling_window_width` parameter to index API in order to control the width of the rolling window in `max|min_of_rolling_sum|average`.
* [enh] Add `doy_window_width` parameter to index API in order to control the width of aggregation windows when computing doy percentiles.
* [maint] Deprecate `window_width` parameter. When filled, it is mapped to it is still mapped to `doy_window_width`.
* [maint] Upgrade to xclim 0.38 and to xarray 2022.6.
* [maint] Add BlackDoc to C.I (github actions) to keep or doc code example clean.
* [enh] Add ECAD's RR index. It computes the sum of precipitations over days.
* [enh] Add icclim logo and auto-update its inner version number.
* [maint] Enable git lfs (large file storage) for `.svg` files to minimise the impact on storage of logo updates.
* [enh] Improve icclim.indices to enable multi indices computation based on variable names `icclim.indices(index_group='tasmax',in_files=data)`
* [fix] **BREAKING CHANGE** ECAD snow indices now expect a snow (snd) variable instead of a precipitation one.
* [enh] Add `build_threshold` function that acts as a factory to create different kind of Threshold.
* [enh] Add BoundedThreshold class. It allows to compute multiple threshold for a single variable.
  This feature is necessary for indices such as ECAD's "DDnorth".
  Instances of BoundedThreshold are created with the `build_threshold` factory function, E.G. `build_threshold(">= -20 degree AND <= 20 degree ")`
* [enh] Make it possible to compute multiple percentiles at once.
* [maint] Update coverage computation. Now tests files are ignored when calculating the code coverage, thus it dropped a little (by 3%).
* [enh] Convert input data that are recognized as a precipitation amount into precipitation rate.
  This is necessary to handle e-obs precipitation datasets.

5.4.0
-----
* [fix] When giving input as a list of netcdf files, the coordinate values are now merged using the `override` strategy, thus the first file with a given dimension define this dimension for all the files.
* [fix] Fix the output unit of some indices (from "°C" to "degree_Celsius")
* [fix] Fixed issued where dataset having a time_bds variable could not be processed by chunking the DataArray(s) instead of the Dataset.

5.3.0
-----
* [enh] Add icclim version to history in outputted metadata.
* [maint] **breaking change** Pin minimal pandas version to 1.3 to have the fix for https://github.com/pandas-dev/pandas/issues/24539
* [enh] ``slice_mode``: seasons can now be defined to be between two exact dates.
* [enh] ``slice_mode`` type can now be tuple[str, list], it works similarly to the list in input of seasons but, it enforces a length of 2.
* [enh] ``slice_mode``: Added `clipped_season` keyword which ignores events starting before the season bounds (original behavior of ``season``).
* [maint] ``slice_mode``: Modified `season` keyword to take into account events (such as in CDD) starting before the season bounds.
  This should improve the scientific validity of these seasonal computations. Plus it is in accordance to xclim way of doing this.
* [maint] Added dataclass ClimateIndex to ease the introduction of new indices not in the ECAD standard.
* [maint] Made use the new typing syntax thanks to ``from __future__ import annotations``.
* [maint] Add docstring validation into flake8 checks.
* [enh] Improve API for date related parameters ``{time_range, base_period_time_range, ref_time_range}``
  They can still be filled with a datetime object but additionally various string format are now available.
  This comes with dateparser library.
* [doc] Update callback doc as its outputted value is very inaccurate when dask is enable.
* [enh] T(X/N/G)(10/90)p indices threshold is now configurable with `threshold` parameter.
  Example of use: `icclim.tx90p(in_files=data, threshold=[42, 99])`
* [enh|maint] threshold, history and source metadata have been updated to better describe what happens during icclim process.
* [fix/doc] The documentation of the generated API for T(X/N/G)(10/90)p indices now properly use thier ECAD definitions instead of those from ETCCDI.
* [enh/doc] Add [WSDI, CSDI, rxxp, rxxpTOT, CW, CD, WW, WD] indices in yaml definition.
  Note: We no longer strictly follow the yaml given by clix-meta.
* [fix] custom seasonal slice_mode was broken when it ended in december. It's now fixed and unit tested.
* [enh] Make ``in_file`` accept a dictionary merging together ``var_name`` and ``in_file`` features.
* [enh] ``in_file`` dictionary can now be used to pass percentiles thresholds. These thresholds will be used instead of computing them on relevant indices.
* [maint/internal] Refactored IndexConfig and moved all the logic to input_parsing.
* [fix] Add auto detection of variables [prAdjust, tasAdjust, tasmaxAdjust, tasminAdjust]

5.2.2
-----
[maint] Remove constraint on numpy version as numba is now working with np 1.22.

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


Release candidates for 5.0 change logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

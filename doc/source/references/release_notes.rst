#################
 Release history
#################

**********
Unreleased
**********

-  [doc] Document the run attribution of the periods that no run starts or ends in
   (issue #580). With ``run_index="first"`` or ``"last"`` a period without any event is
   ``0``, while a period wholly traversed by one continuous run attributed to another
   period is ``NaN`` (not reported), as in ETCCDI and the ATBD for ``CDD`` and ``CWD``;
   with ``split_runs_at_period_boundary=True`` every period gets a value, and the value of
   a period can exceed its length under ``"first"`` and ``"last"``. The docstrings and the
   how-to page "Attribute or split longest runs" say it, and tests lock the behaviour in.
   No change of the results.
-  [doc] The logo of the README no longer shows a version number (issue #659). The PyPI
   page of a release showed the logo of 7.3.4, because the logo with the version is
   regenerated only on master, whose version did not change for 7.3.5 to 7.3.7, while the
   text of the page is fixed at upload. The README uses a copy of the logo without the
   version; the logos of the documentation are unchanged.
-  [fix] The DCSC indices ``PQ90`` and ``PQ99`` no longer raise ``DimensionalityError``
   (issue #643). They are the 90th and 99th percentile of the daily precipitation, in
   mm/day (DRIAS: "q90 des précipitations totales quotidiennes"); their output unit was
   declared as a percent, which a precipitation cannot be converted to.
   Affected: every release since 7.0.0 that has the DCSC indices.
-  [fix] The generic ``excess`` and ``deficit`` no longer raise ``KeyError: 'units'`` on a
   precipitation with xarray 2026.2 and later (issue #644). The units of the result are
   taken from the studied variable instead of from the subtraction of the threshold,
   whose attributes recent xarray versions drop when the texts of the units differ
   ("mm/day" and "mm d-1").
   Affected: every release with ``excess`` and ``deficit``, with xarray 2026.2 or later.
-  [fix] The DCSC indices that use a normal (``TXND``, ``TNHT``, ``TNND``, ``TNCWD`` and
   ``TXHWD``) no longer raise ``DimensionalityError`` ("cannot convert from
   delta_degree_Celsius to degree_Celsius") when the input is in degrees Celsius or
   Fahrenheit (issue #617). The offset of 5 degrees is now converted as a temperature
   difference of the input unit, so input in K, degC and degF gives the same result.
   Affected: every release since 7.0.0 that has the DCSC indices, with input not in K.
-  [fix] The new ECA&D index ``HI`` is now missing at latitudes below 0 (issue #653). Its
   daylength coefficient started at minus infinity, so the southern hemisphere got
   K = 1.00 and a value that has no meaning: the index is defined for the northern
   hemisphere only, and the result is missing below 0 and above 50 degrees north. Each
   latitude band includes its upper boundary (K = 1.02 at 42 N); the docstring and the
   documentation give the six values of K, and the tests cover the boundaries of the
   bands.
-  [enh] Added the ECA&D index ``HI`` (Huglin Index) of the ATBD v11 (issue #637,
   part of #204): the sum, from 1 April to 30 September, of
   ``((TG - 10) + (TX - 10)) / 2 * K`` in degree_Celsius day, with ``K`` the daylength
   coefficient of the latitude of the ATBD (1.00 up to 40 N and 1.06 for 48-50 N).
   ``icclim.hi`` needs the daily mean and maximum temperature and reads the latitude
   from the coordinates of the data. It differs from xclim's ``huglin_index``, which
   clips each day at 0 and caps the coefficient above 50 N: the ATBD sum has no
   clipping and gives no value above 50 N, where the result is missing.
-  [enh] Added the ECA&D index ``BEDD`` (Biologically Effective Degree Days) of the
   ATBD v11 (issue #638, part of #204): the sum, from 1 April to 30 September, of
   ``min(max((TX + TN) / 2 - 10, 0), 9)`` in degree_Celsius day. ``icclim.bedd`` needs
   the daily minimum and maximum temperature and no latitude. It is the definition of
   xclim's ``biologically_effective_degree_days`` with ``method="icclim"``, except that
   a period without any valid day from April to September is missing instead of 0.
-  [enh] The notice about the new default ``run_index="last"`` (``CDD``, ``CWD``, ``CFD``,
   ``CSU``, ``PXCDD``, ``PXCWD`` and ``max_consecutive_occurrence``) is now printed
   once per process for each index, on stdout, instead of at every call, and starts
   with "Since icclim 7.4.0, <index> defaults to run_index="last"". Passing
   ``run_index`` explicitly prints nothing.
   Affected: scripts that read the standard output of these indices.
-  [fix] ``date_event=True`` now works with ``max_consecutive_occurrence`` and the indices
   built on it (``CDD``, ``CWD``, ``CFD``, ``CSU``) on non-standard calendars such as
   ``noleap``, ``360_day`` or ``all_leap`` (issue #574). It raised ``TypeError: operand
   type(s) all returned NotImplemented from __array_ufunc__``.
   Affected: 7.2.0 and later, for input with a cftime calendar.
-  [maint] **Python 3.10 is no longer supported and the minimum versions of the
   dependencies are raised** (issue #586). icclim now requires Python 3.11 or later.
   The previous minimums could not be installed together or did not work. The new
   minimums are the versions the test suite works with, measured with the lowest
   versions the resolver can pick on Python 3.11: ``numpy>=1.24`` (was 1.21),
   ``pandas>=2.2.0`` (was 1.3.0), ``xarray>=2024.11.0`` (was 2022.6.0),
   ``xclim>=0.56.0`` (was 0.45.0), ``dask[array]>=2024.11.1`` (was 2022.2.0),
   ``zarr>=2.12.0`` (was 2.11.0), ``cftime>=1.6.2`` (was 1.5.0),
   ``dateparser>=1.1.4`` (was 1.1.0), ``pint>=0.25`` (was 0.20) and
   ``typing-extensions>=4.5.0`` (was 4.0). ``pint`` older than 0.25 converts
   1 mm/day to ``kg m-2 s-1`` with an error of one ulp, so a daily value exactly equal
   to a converted threshold could be lost; ``pint`` 0.25 needs Python 3.11.
   Affected: installations on Python 3.10 or that pin a dependency below the new
   minimums.
-  [fix] The DCSC indices ``TXHWD``, ``TNCWD`` and ``TNND`` returned wrong values
   (issue #616). They are now defined as in the DRIAS catalogue: ``TXHWD`` counts the
   days with ``Tx >= normal + 5°C`` and ``TNCWD`` the days with ``Tn <= normal - 5°C``,
   both in spells of more than 5 consecutive days (at least 6 days), and ``TNND`` the
   days with ``Tn <= normal - 5°C``. They were declared with the operator ``<`` and the
   offset +5°C, so ``TXHWD`` counted the days that were not warm and ``TNCWD`` and
   ``TNND`` counted almost every day. The French definitions were corrected too.
   Affected: every release since 7.0.0 that has the DCSC indices.
-  [fix] The DCSC indices ``TXND`` and ``TNHT`` now count the days with
   ``Tx >= normal + 5°C`` and ``Tn >= normal + 5°C`` as in the DRIAS catalogue
   (issue #620). They used a strict ``>``, so days exactly at the threshold were not
   counted. The French definitions were corrected too.
   Affected: every release since 7.0.0 that has the DCSC indices.
-  [fix] ``split_runs_at_period_boundary`` is now applied by ``WSDI``, ``CSDI``,
   ``TXHWD``, ``TNCWD`` and ``sum_of_spell_lengths`` (issue #614). It was accepted by
   ``icclim.index`` and ignored. With the option, runs are cut at every output period
   boundary first, then only the pieces of at least the minimum spell length (6 days
   for ``WSDI`` and ``CSDI``) are kept: a 10-day spell from 28 December to 6 January
   gives ``[0, 6]`` with yearly output instead of ``[10, 0]``. The option is now an
   argument of ``icclim.wsdi``, ``icclim.csdi``, ``icclim.sum_of_spell_lengths``,
   ``icclim.dcsc.txhwd`` and ``icclim.dcsc.tncwd``. The default behaviour is
   unchanged.
-  [fix] Percentile thresholds are now adjusted to the calendar with icclim's exact
   interpolation (issue #603). With SciPy 1.18.1 (Python 3.12 or later) the previous
   code, present since 7.0.0, could return different exceedance counts for
   non-bootstrapped percentile indices and for the legacy bootstrap path: in a test
   case the monthly ``TX90p`` went from 6 to 9 days, and the legacy bootstrap from 0 to
   30 days. The default bootstrap path of 7.2 and 7.3 was not affected. The exact
   interpolation is not used inside xclim's own bootstrap: with the diagnostic setting
   ``ICCLIM_BOOTSTRAP_MODE=default`` and SciPy 1.18.1, the percentile bootstrap still
   uses xclim's own interpolation, which is affected. Results with SciPy 1.17.x are
   unchanged. Users of earlier
   versions on that stack should upgrade.
-  [fix] ``vDTR`` now excludes the difference between the last day of one output
   period and the first day of the next, as required by ECA&D ATBD v11 section
   5.3.11 (issue #599). This causes a small value change for every period after
   the first. icclim continues to average over the number of valid within-period
   differences; it does not use the ATBD formula's denominator of all days in
   the period.
-  [Behaviour change] Since 7.4.0, ``CDD``, ``CWD``, ``CFD``, ``CSU``,
   ``PXCDD``, ``PXCWD`` and ``max_consecutive_occurrence`` default to
   ``run_index="last"``: a run crossing an output-period boundary is counted in
   the period where it ends (issue #580). This applies to every output frequency,
   including months and seasons, not only years: a January 25--February 5 run is
   ``[12, 0]`` with ``run_index="first"``, ``[0, 12]`` by default, and ``[7, 5]``
   when split. The ECA&D example of a dry spell from
   December 2000 to January 2001 therefore counts toward 2001. With yearly output,
   a dry spell from 2001-10-01 through 2002-04-30 changes from ``[212, 0]`` under
   the old default to ``[0, 212]``. Pass ``run_index="first"`` for the pre-7.4.0
   result, or ``split_runs_at_period_boundary=True`` to cut the spell at the year
   boundary and get ``[92, 120]``. ECA&D ATBD v11, pp. 20--21, the RClimDex
   manual (Appendix C), and climdex.pcic use end-period attribution for CDD/CWD.
   The same convention is applied to CFD, CSU, PXCDD, PXCWD and the generic
   function for consistency; the ATBD does not require it for those indices.
-  [fix] ``CDD``, ``CWD``, ``CFD``, ``CSU`` and ``max_consecutive_occurrence``
   return their dimensions in the order of the input (issue #542, PR #550).
   Behaviour change in the layout only, the values do not change. With
   xclim 0.60.0 and later these results had ``time`` after the spatial
   dimensions, whatever the input; xclim 0.45.0 already kept the order of the
   input. Before: an input ordered ``(time, lat, lon)`` gave
   ``(lat, lon, time)`` and an input ordered ``(lat, lon, time)`` gave
   ``(lat, lon, time)``. Now: ``(time, lat, lon)`` and ``(lat, lon, time)``.
   Results computed with ``date_event=True`` are not concerned: ``time`` stays
   the first dimension whatever the order of the input. Code that selects these
   results by axis position instead of by dimension name has to be updated.
   Affected: 7.1.10, 7.2.0, 7.3.1 and 7.3.3 (run with xclim 0.60.0), and 7.3.4.

*****
7.4.0
*****

date: TBD


-  [Behaviour change] Run-length indices now credit a run to the period where it ends.
   ``CDD``, ``CWD``, ``CFD``, ``CSU``, ``PXCDD``, ``PXCWD`` and
   ``max_consecutive_occurrence`` default to ``run_index="last"``. Until 7.3.x a run was
   credited to the period where it starts. For ``CDD`` and ``CWD`` this follows the ECA&D
   ATBD v11 (section 5.1) and the ETCCDI definitions; for ``CFD``, ``CSU`` and the
   generic function it is icclim's own convention, applied for consistency (issue #580).
   ``run_index="first"`` gives the previous behaviour, and
   ``split_runs_at_period_boundary=True`` cuts the runs at the period boundaries. A
   notice is printed once per process and per index (PR #633).
-  [Behaviour change] Size of the change, on CMIP6 data (1976-2014, global grid;
   ACCESS-CM2 for ``CDD`` and ``CWD``, CNRM-CM6-1 for ``CFD`` and ``CSU``): the share of
   values that differ between ``"first"`` and ``"last"`` is, for yearly and monthly
   output, 22% and 46% for ``CDD``, 5% and 19% for ``CWD``, 28% and 10% for ``CFD``, and
   12% and 11% for ``CSU`` and ``max_consecutive_occurrence``. Between 80% and 99% of the
   changed values differ by more than one day.
-  [Behaviour change] Periods wholly crossed by a run: a period with no event is 0; a
   period entirely covered by a run credited to another period is ``NaN`` with
   ``"first"`` and ``"last"`` (as in ETCCDI for ``CDD`` and ``CWD``); with the split
   option every period has a value. With ``"first"`` and ``"last"`` a value can be longer
   than its period: at a polar grid point with frost on every day of 1976-2014, ``CFD``
   is a single run of 14,245 days credited to one period, while with the split option it
   is 365 days per year (366 in a leap year). The share of values longer than their
   period is, for yearly and monthly output, 0.75% and 7.9% for ``CDD``, 2.9% and 3.7%
   for ``CFD``, and 1.3% and 4.2% for ``CSU`` (PR #661).
-  [change] Python 3.10 is no longer supported (``requires-python >=3.11``). The new
   minimum versions are numpy 1.24, pandas 2.2.0, xarray 2024.11.0, xclim 0.56.0, dask
   2024.11.1, zarr 2.12.0, cftime 1.6.2, dateparser 1.1.4, typing-extensions 4.5.0 and
   pint 0.25 (PR #630).
-  [enh] ``HI`` and ``BEDD`` follow the ATBD v11: they sum from 1 April to 30 September,
   and the coefficient of ``HI`` is 1.00 up to 40 N and 1.02 to 1.06 for each band of two
   degrees up to 50 N, with a missing result above 50 N and below the equator (PRs #640,
   #641 and #655). 66 of the 75 ECA&D indices are implemented; the others are followed in
   issue #204.
-  [compat] Tested with xclim 0.56 (lowest), 0.60 and 1.0, xarray 2026.2 or later, and
   pint 0.25 or later (PR #631). SciPy is not a direct dependency; with
   ``ICCLIM_BOOTSTRAP_MODE=default``, the bootstrap interpolation of xclim is still
   affected by the SciPy 1.18.1 behaviour change described in the 7.3.5 notes.
-  [compat] Validation: the results on CMIP6 data are identical to those of 7.3.3 and
   7.3.6, with xclim 0.60 and 1.0, except for the changes above (see "How the indices are
   validated", PR #657). This comparison will be repeated on the release candidate before
   the tag.

   .. CHECK: rerun this comparison on the 7.4.0 candidate before the tag.
-  [perf] The speed of the ordinary indices on a full CMIP6 grid is unchanged since 7.3.3
   (59 s against 62 s for the yearly ``TG``, 45 s against 44 s for ``rx5day``, same input
   and node).
-  [perf] Peak memory and speed depend on how the input is opened. On a 128x256 grid of
   daily data, on one node, for 30 to 165 years: opening the files with their own chunks
   (one time step each in this test, ``chunks={}``; icclim then rechunks them to auto-sized
   chunks) used less memory and was 1.4 to 1.7 times slower than opening them with
   ``chunks="auto"``, and the difference in memory grows with the length of the series
   (count index, 165 years: 44 s and 3.9 GiB with ``"auto"``, 73 s and 1.7 GiB with the
   file chunks). Input held in a single chunk along time is left as it is by icclim and
   needed 18 to 32 GiB; the count, rolling and date indices took about 30 minutes, against
   less than 90 s with ``"auto"``.
-  [perf] Percentile indices with a bootstrap over the years outside the base period are
   the slowest case. The time is proportional to the number of grid points and grows with
   the number of years outside the base period: on a full 128x256 grid, about 45 minutes
   for 60 years and 2.2 hours for 165 years (annual ``TX90p``, 30-year base period,
   auto-sized chunks).
-  [perf] Memory guard and chunk policy: to be decided before the release.

   .. CHECK: any memory guard or change of the chunk policy is not decided for 7.4.0.
-  [test] Independent reference calculations now cover all 66 implemented indices (PR #539
   and the following pull requests); a registry-wide test checks the equivalence of
   inputs in K, degC and degF, and in kg m-2 s-1 and mm/day (PR #642).
-  [meta] ``environment.yml`` and the installation notes match ``pyproject.toml`` (PR
   #664); citation metadata and the concept DOI badge (PRs #588, #591, #592 and #593).

*****
7.3.7
*****

date: 2026-11-12


-  [fix] The DCSC indices that use a normal (``TXND``, ``TNHT``, ``TNND``, ``TNCWD`` and
   ``TXHWD``) no longer raise ``DimensionalityError`` ("cannot convert from
   delta_degree_Celsius to degree_Celsius") when the input is in degrees Celsius or
   Fahrenheit (issue #617). The offset of 5 degrees is now converted as a temperature
   difference of the input unit, so input in K, degC and degF gives the same result.
   Affected: every release since 7.0.0 that has the DCSC indices, with input not in K.
-  [fix] The generic ``excess`` and ``deficit`` no longer raise ``KeyError: 'units'`` on a
   precipitation with xarray 2026.2 and later (issue #644). The units of the result are
   taken from the studied variable instead of from the subtraction of the threshold,
   whose attributes recent xarray versions drop when the texts of the units differ
   ("mm/day" and "mm d-1").
   Affected: every release with ``excess`` and ``deficit``, with xarray 2026.2 or later.
-  [fix] The DCSC indices ``PQ90`` and ``PQ99`` no longer raise ``DimensionalityError``
   (issue #643). They are the 90th and 99th percentile of the daily precipitation, in
   mm/day (DRIAS: "q90 des précipitations totales quotidiennes"); their output unit was
   declared as a percent, which a precipitation cannot be converted to.
   Affected: every release since 7.0.0 that has the DCSC indices.

*****
7.3.6
*****

date: 2026-11-10


-  [fix] The DCSC indices ``TXHWD``, ``TNCWD`` and ``TNND`` returned wrong values
   (issue #616). They are now defined as in the DRIAS catalogue: ``TXHWD`` counts the
   days with ``Tx >= normal + 5°C`` and ``TNCWD`` the days with ``Tn <= normal - 5°C``,
   both in spells of more than 5 consecutive days (at least 6 days), and ``TNND`` the
   days with ``Tn <= normal - 5°C``. They were declared with the operator ``<`` and the
   offset +5°C, so ``TXHWD`` counted the days that were not warm and ``TNCWD`` and
   ``TNND`` counted almost every day. The French definitions were corrected too.
   Affected: every release since 7.0.0 that has the DCSC indices.
-  [fix] The DCSC indices ``TXND`` and ``TNHT`` now count the days with
   ``Tx >= normal + 5°C`` and ``Tn >= normal + 5°C`` as in the DRIAS catalogue
   (issue #620). They used a strict ``>``, so days exactly at the threshold were not
   counted. The French definitions were corrected too.
   Affected: every release since 7.0.0 that has the DCSC indices.

*****
7.3.5
*****

date: 2026-11-10


-  [fix] Percentile thresholds are now adjusted to the calendar with icclim's exact
   interpolation (issue #603). With SciPy 1.18.1 (Python 3.12 or later) the previous
   code, present since 7.0.0, could return different exceedance counts for
   non-bootstrapped percentile indices and for the legacy bootstrap path: in a test
   case the monthly ``TX90p`` went from 6 to 9 days, and the legacy bootstrap from 0 to
   30 days. The default bootstrap path of 7.2 and 7.3 was not affected. The exact
   interpolation is not used inside xclim's own bootstrap: with the diagnostic setting
   ``ICCLIM_BOOTSTRAP_MODE=default`` and SciPy 1.18.1, the percentile bootstrap still
   uses xclim's own interpolation, which is affected. Results with SciPy 1.17.x are
   unchanged. Users of earlier
   versions on that stack should upgrade.

*****
7.3.4
*****

date: 2026-11-08


-  [fix] Support xclim 1.0 (PR #579). xclim 1.0.0 removed ``xclim.indices``
   (moved to ``xclim.compute``), renamed the ``op`` argument of
   ``growing_season_length`` to ``condition``, and returns a ``Dataset`` from
   its indicators. icclim 7.3.3 and earlier declare ``xclim>=0.45.0`` without
   an upper bound, so a fresh install picks up xclim 1.0.0. With it, ``CDD``
   raised ``ModuleNotFoundError: No module named 'xclim.indices'`` and ``GSL``
   raised ``TypeError: select_time() got an unexpected keyword argument 'op'``
   (run on 7.3.3 with xclim 1.0.0). The other 7.x releases were not tested with
   xclim 1.0.0. The test suite passes with xclim 0.60.0 and xclim 1.0.0.
-  [fix] ``difference_of_means`` no longer returns NaN everywhere when
   ``sampling_method="groupby_ref_and_resample_study"`` is used with a
   reference given as a separate input that covers another period (issue #571,
   PR #572). The completeness check combined the masks of the study and of the
   reference, so with disjoint periods every output period was masked, without
   any error or warning. Now only the study variable decides which output
   periods are complete. Affected: 7.2.0, 7.3.0, 7.3.1, 7.3.2 and 7.3.3 (run on
   a study 2002-2003 against a reference 2000-2001; 7.1.10 returns the expected
   values). Results computed with these releases for such a call should be
   recomputed; ``allow_missing_periods=True`` restored the values.
-  [fix] Threshold queries that cannot be tokenized, such as
   ``"Coco l'asticot"``, now raise ``InvalidIcclimArgumentError`` on
   Python 3.13. The tokenizer of Python 3.13 makes pint raise
   ``tokenize.TokenError``, which was not caught (PR #570).
-  [perf] Keep the Dask chunks of caller-provided arrays when they are
   reasonably large, instead of rechunking with ``"auto"`` (PR #518). Arrays
   whose largest chunk is smaller than 1/8 of ``array.chunk-size`` (16 MiB with
   the default), and eager arrays, are still chunked with ``"auto"``: with
   one chunk per daily file the preserved chunks made some indices 3 to 7 times
   slower. Results are unchanged.
-  [enh] Add opt-in NetCDF4 compression and stored chunk encoding through
   ``ICCLIM_OUTPUT_COMPRESSION_LEVEL`` and ``ICCLIM_OUTPUT_CHUNKS``. The default
   output is unchanged (PR #518).
-  [perf] Compute the per-period reducers with vectorized reductions instead of
   Python loops over the periods: maximum and minimum with ``date_event``,
   count with ``date_event`` and consecutive occurrences with dates (PR #573).
   On the ACCESS-CM2 benchmark the date-event indices go from about 2 hours to
   about 1 minute, with identical results. ``date_event`` with ``txx`` and
   ``tnn`` now also works on non-standard (cftime) calendars. The dated
   ``max_consecutive_occurrence`` on cftime calendars still fails (issue #574).
-  [enh] New option ``split_runs_at_period_boundary`` for ``max_consecutive_occurrence``
   and the ECA&D indices ``CDD``, ``CWD``, ``CFD`` and ``CSU`` (issue #543, PRs #547 and #585).
   No change by default (``False``): a run of consecutive days that crosses the end
   of an output period is still counted whole in the period where it starts
   (``run_index="first"``, the default) or where it ends (``run_index="last"``), and
   the other period gets no credit for the days of that run, so its value can be 0.
   With ``split_runs_at_period_boundary=True`` the runs are cut at the boundary of
   every output period and each period gets the longest run found inside it. For
   daily data from 2001 to 2002 with frost days from 2001-10-01 to 2002-04-30 and a
   yearly output, ``CFD`` is ``[212, 0]`` by default (``[0, 212]`` with
   ``run_index="last"``) and ``[92, 120]`` with the option. The output dimension
   order is the same with and without the option. ``sum_of_spell_lengths`` and the
   indices built on it (``WSDI``, ``CSDI``) are not concerned by the option.
-  [doc] Explain in the completeness how-to why counting indices returned 0 over
   cells without any data before 7.2 (a comparison with NaN is never true), why
   they now return NaN, and how to keep the old behaviour with
   ``completeness="none"`` (PR #575).
-  [test] Add an isolated non-bootstrap performance matrix reporting graph
   construction, task count, scheduler calls, wall time and peak RSS across
   workloads, input layouts and chunking policies.
-  [test] Add matching Kraken real-data workloads and a slow synthetic-cube
   memory regression test.
-  [test] Add metamorphic property tests (PR #578).

*****
7.3.3
*****

date: 2026-11-04


-  [fix] Make the interpolation of calendar-day percentile thresholds from 365
   to 366 days exact (PR #566). With SciPy 1.18.1, ``interp1d`` returns
   inexact values for constant multi-dimensional data (scipy/scipy#26609), so
   ``DataArray.interp``, which icclim used through xclim's
   ``adjust_doy_calendar``, turned neighbouring thresholds of exactly 10.0 into
   values such as 10.000000000000002 or 9.999999999999998. Observations that tie
   with a threshold, for example temperatures reported to 0.1 degC, were then
   counted as exceeding it in count-type percentile indices such as ``TX90p``.
   In a test with temperatures rounded to 0.1 degC over 30 years, the summed
   ``TX90p`` and ``TX10p`` counts were 25970 instead of 25926 (44 additional
   exceedance days). Affected: 7.2.0, 7.3.0, 7.3.1 and 7.3.2 installed with
   SciPy 1.18.1 (run on a day-of-year percentile count test; SciPy 1.17.1 gives
   the exact result). Results computed with SciPy 1.18.x should be recomputed.
   Other SciPy 1.18 releases were not tested.
-  [fix] Compute the calendar-day percentile windows with wrap-around at the
   edges of the percentile base period, for nominal and bootstrap thresholds,
   with the same thresholds in eager and chunked execution (issue #559,
   PR #564). Before, the 5-day window of the first and last days of the base
   period was truncated, which left ``CD``, ``WD`` and ``WW`` one day off in the
   independent check. Behaviour change: thresholds for the first and last days
   of the year can change slightly, and day-of-year percentile indices with
   them; period percentiles do not change. Affected: 7.3.2 (run, listed there
   as a known issue); earlier releases were not checked.
-  [fix] Rolling-window indices such as ``RX5day`` no longer fail when a Dask
   time chunk is shorter than the rolling window: only the chunks that are too
   short are merged, other chunk layouts are kept (issue #526, PR #565).
   Confirmed failing with xarray 2026.2.0 and dask 2026.1.2 (run); it did not
   reproduce with xarray 2026.9.0 and dask 2026.8.0, so the affected releases
   are not determined.
-  [doc] Add the behaviour-change, ambiguity and change-detector rules to the
   release process (PR #563).

*****
7.3.2
*****

date: 2026-11-03


-  [fix] Honour every percentile requested from generic ``percentile`` while
   preserving the 7.3.1 single-percentile output shape (issue #557). From at
   least 7.2.0 through 7.3.1, the source used only the first requested value
   (7.2.0 source read).
-  [fix] Average the ECA&D leave-one-year-out bootstrap index estimates for
   temperature percentile counts TG10p/TG90p, TN10p/TN90p, and TX10p/TX90p
   (issue #540, PR #545). This is a
   7.3.0 regression: running 7.2.0 gives the correct ATBD value, while 7.3.0
   and 7.3.1 are affected.
-  [fix] Restrict the precipitation operand of ``CD`` and ``WD`` to wet days
   (RR >= 1 mm) (issue #541, PR #546). Affected in 7.2.0 and 7.3.1 (run).
-  [fix] Apply the requested percentile base period, interpolation,
   day-of-year window and ``only_leap_years`` setting to the default compound
   thresholds used by ``CD``, ``CW``, ``WD`` and ``WW`` (issue #560,
   PR #546). Affected in 7.2.0 and 7.3.1 (run).
-  [fix] Use the strict ECA&D ``TG > 5 degC`` GSL onset and honor disabled
   completeness for isolated missing values (issues #537 and #538, PR #548).
   Affected since at least 7.2.0 through 7.3.1; the 7.2.0 source was read, not
   run.
-  [fix] Accept CF precipitation-flux units in ``RX5day`` (issue #544,
   PR #549). Verified by running 7.3.1; the 7.2.0 source was read, but no
   earlier range is claimed.
-  [known issue] ``CD``, ``WD`` and ``WW`` can differ by one day at the edges
   of a subset percentile base period because the five-day calendar window is
   truncated instead of wrapped (issue #559).

*****
7.3.1
*****

date: 2026-11-02


-  [fix] Restrict ``only_leap_years`` percentile bootstrap calculations to the
   percentile base period (PR #514).
-  [fix] Correct the 7.3.0 ``date_event`` extrema regression that returned the
   period sum instead of the requested maximum or minimum. Chunked inputs no
   longer fail, and rolling extrema now return event dates (PR #517).
-  [fix] Non-monthly percent results have been wrong since at least 6.2.0
   (verified in 6.2.0, 7.0.0, and 7.2.0):
   ``count_occurrences(out_unit="%")`` returned fractions or raw counts instead
   of percentages, making common results 100 times too small (issue #520,
   PR #527).
-  [fix] Use the year containing February for the ``ONDJFM`` percentage
   denominator. Since at least 7.0.0, leap status was taken from the output
   timestamp year (verified in the 7.0.0 and 7.2.0 source; issue #521,
   PR #530).
-  [fix] Prevent annual percentage output from crashing across multiple years
   on fixed CF calendars (issue #522, PR #531), and use a 360-day denominator
   for ``360_day`` years. Since at least 7.0.0, annual denominators were
   hard-coded to 365 or 366 days (verified in the 7.0.0 and 7.2.0 source;
   issue #523, PR #531).
-  [fix] Report missing event dates when a consecutive-run period contains no
   event (issue #524, PR #529).
-  [fix] Include values equal to the 1 mm wet-day floor in
   ``R75pTOT``, ``R95pTOT``, ``R99pTOT``, and ``fraction_of_total``
   calculations. Since at least 7.0.0, the floor used the percentile
   threshold's strict ``>`` operator (verified in the 7.0.0 and 7.2.0 source;
   issue #525, PR #528).
-  [test] Record non-bootstrap performance invariants (PR #515).

*****
7.3.0
*****

date: 2026-10-30


-  [change] Use the ECA&D ATBD section 5.1 minimum valid-day rules by default,
   resolving the threshold automatically from annual, half-yearly, seasonal, or
   monthly output frequency.
-  [enh] Add ``completeness`` with explicit ``"ecad"``, ``"wmo"``,
   ``"strict"``, and ``"none"`` profiles or an inclusive configurable minimum
   valid fraction. The WMO profile distinguishes means and counts, sums, simple
   extrema, and conservatively unclassified operations.
-  [compat] Keep explicitly supplied ``allow_missing_periods`` values as a 7.2
   compatibility bridge. Spatially varying seasons and output period types not
   defined by ECA&D retain strict completeness.
-  [meta] Record the resolved period class, reference, policy version, execution
   options, aggregation class, and configured fraction in output provenance.
-  [doc] Add a migration guide for workflows created before 7.2, including the
   explicit setting needed to preserve calculate-from-available behavior.
-  [perf] Keep WMO completeness lazy and document its additional compute cost.
   The five-consecutive-missing-day rule runs only when the WMO profile is
   explicitly selected; the default ECA&D path does not pay that cost.
-  [fix] Keep built-in seasonal WMO checks limited to their selected months and
   preserve ``allow_partial_seasons`` behavior at cross-year boundaries.
-  [fix] Keep custom date-bounded seasons on strict completeness instead of
   applying calendar-month WMO thresholds.
-  [fix] Correct ``AMJJAS`` to include September, consistently with its documented
   April-to-September half-year definition.
-  [meta] Label absolute-temperature outputs as ``temperature: on_scale`` and
   temperature ranges and standard deviations as ``temperature: difference``.
   Reject physically incompatible metadata inference for dimensionless variables,
   such as a variable named ``RH`` whose declared unit is ``mm``.
-  [perf] Extend exact percentile-bootstrap execution to aggregate and compound
   spell indices, including aligned multivariable ``cftime`` inputs, while keeping
   safe reference fallbacks for unsupported or unaligned workloads.
-  [fix] Expose ``allow_missing_periods`` consistently from the generated ECA&D,
   DCSC and generic convenience functions.
-  [doc] Add a station-workflow performance guide covering vectorized station
   dimensions, memory-bounded batches, grouped index output and correct timing
   of lazy calculations.
-  [security] Refresh the development and documentation lockfile to patched
   ``certifi``, ``filelock``, ``nbconvert``, ``tornado`` and ``virtualenv``
   releases.

*****
7.2.1
*****

date: 2026-09-30


-  [fix] Keep completeness masking lazy for dask-backed inputs. The optional
   missing-period diagnostic no longer executes the dask graph before returning
   the result.
-  [fix] Distinguish intentionally out-of-season cells from missing observations
   when applying strict completeness checks to spatially varying seasons.
-  [enh] Record the resolved completeness policy, implementation method and
   options in output variable metadata in preparation for configurable ECA&D
   and WMO policies in icclim 7.3.

*****
7.2.0
*****

date: 2026-09-25


-  [change] **Behavioral change**: icclim now masks output periods to ``NaN``
   by default when the source time series is incomplete for that period. Previously,
   yearly or monthly indices could be computed from available timesteps only, even
   when some source timesteps were missing.
-  [enh] Add ``allow_missing_periods=True`` to preserve the previous behavior and
   compute incomplete periods from available timesteps.
-  [enh] Add ``allow_partial_final_period=True`` to compute only the final
   incomplete output period, useful for ongoing months or years, while keeping
   older incomplete periods masked.
-  [enh] Regenerate the public index-specific API wrappers so the new
   missing-period options are available on individual index functions.

******
7.1.11
******

date: 2026-09-18


-  [enh] Add JSON provenance sidecars for file outputs, including input fingerprints, index definitions, execution context and reproducibility metadata.
-  [fix] Restore the MAINT API after the provenance integration and keep provenance collection resilient when optional Git or runtime metadata is unavailable.
-  [doc] Stabilize Read the Docs builds by installing Git LFS through the build image, fetching LFS assets before Sphinx runs and avoiding execution of data-dependent tutorial notebooks.
-  [maint] Refresh generated API and coverage documentation, project logos, pre-commit hooks and documentation dependency locks.

*******
7.1.10
*******

date: 2026-08-23


-  [fix] Pin workflow-installed ``flit`` and ``flit_core`` to the same ``3.12.0`` release so PyPI publish jobs build with a compatible toolchain and avoid the failed ``v7.1.9`` release path.
-  [enh] Restore the optimized exact bootstrap route for ``cftime`` day-of-year percentile count indices after integrating the compiled order-stat count path into the public routing.
-  [fix] Preserve exact leap-year behavior for non-reference ``cftime`` study years by reusing the prepared 366-day nominal threshold field where needed.
-  [doc] Add real-data Kraken validation and exact-count redesign archive notes for the ``cftime`` bootstrap workflow.

******
7.1.9
******

date: 2026-08-23


-  [fix] Pin workflow-installed ``flit`` to a 3.x release so PyPI publish jobs do not emit the unsupported ``Import-Name`` metadata field.
-  [enh] Restore the optimized exact bootstrap route for ``cftime`` day-of-year percentile count indices after integrating the compiled order-stat count path into the public routing.
-  [fix] Preserve exact leap-year behavior for non-reference ``cftime`` study years by reusing the prepared 366-day nominal threshold field where needed.
-  [doc] Add real-data Kraken validation and exact-count redesign archive notes for the ``cftime`` bootstrap workflow.

******
7.1.8
******

date: 2026-08-23


-  [enh] Restore the optimized exact bootstrap route for ``cftime`` day-of-year percentile count indices after integrating the compiled order-stat count path into the public routing.
-  [fix] Preserve exact leap-year behavior for non-reference ``cftime`` study years by reusing the prepared 366-day nominal threshold field where needed.
-  [doc] Add real-data Kraken validation and exact-count redesign archive notes for the ``cftime`` bootstrap workflow.

******
7.1.7
******

date: 2026-07-29


-  [perf] Defer percentile-threshold materialization until a bootstrap path actually needs the threshold field, reducing setup overhead for dask-backed day-of-year percentile count indices.
-  [fix] Keep percentile bootstrap cases using ``threshold_min_value`` on the exact safe tiled path after Kraken validation showed the experimental fast path was not field-identical on real precipitation data.
-  [fix] Keep ``cftime`` percentile bootstrap cases on the exact safe tiled path after Kraken validation found a remaining one-cell mismatch in the experimental fast path.
-  [doc] Add maintainer notes for bootstrap architecture, readable implementation boundaries and the validated fast-path support matrix.

******
7.1.6
******

date: 2026-07-22


-  [enh] Extend the compiled percentile bootstrap count path to anchored annual seasonal outputs such as ``JJA`` and ``ONDJFM``.
-  [fix] Support the latest ``xclim`` missing-value method API during seasonal post-processing.
-  [doc] Add seasonal bootstrap validation results showing exact agreement against eager references on Kraken.

******
7.1.5
******

date: 2026-07-22


-  [enh] Extend the compiled percentile bootstrap count path to monthly outputs, so day-of-year percentile count indices such as ``TG90p``, ``TX90p`` and ``TN90p`` can avoid multi-million-task dask graphs for both annual and monthly frequencies.
-  [perf] Reuse each yearly bootstrap threshold across all output groups in the same year and avoid materializing nominal percentile thresholds, preserving the fast annual performance validated in ``v7.1.4``.
-  [doc] Document the percentile bootstrap strategy, supported cases, validation rules and Kraken benchmark results for future maintainers.

******
7.1.4
******

date: 2026-07-22


-  [enh] Speed up annual percentile bootstrap counts with a compiled rank-select path for day-of-year percentile count indices such as ``TG90p``, ``TX90p`` and ``TN90p``. Unsupported cases keep using the existing safe tiled bootstrap path.
-  [enh] Add separate memory-based tiling controls for the compiled bootstrap path, while preserving the reliable xclim-based fallback and ``ICCLIM_BOOTSTRAP_MODE=safe`` escape hatch.
-  [fix] Prepare temperature percentile thresholds from the full Celsius-normalized input series, so Kelvin input and explicitly Celsius input follow the same scientific path and produce identical saved thresholds.
-  [maint] Update generated API documentation after the bootstrap reliability changes.

******
7.1.3
******

date: 2026-07-20


Details
=======

-  [fix] Restore compatibility with latest ``xclim`` releases by adapting ``to_agg_units`` calls to the installed API signature instead of always passing ``deffreq``.
-  [enh] Add bootstrap reliability controls for day-of-year percentile thresholds. For dask-backed percentile count indices, icclim now uses a memory-budgeted tiled bootstrap path by default to avoid oversized dask graphs and reduce peak memory risk. ``bootstrap=False`` remains an explicit user shortcut for fast exploratory assessment only, because it disables the overlap correction and can bias percentile-based results.
-  [maint] Keep the existing bootstrap implementation as the release path while follow-up work continues on a native replacement. The experimental prepared-state optimization is not included in ``v7.1.3``.
-  [maint] Bump ``peter-evans/create-pull-request`` from ``v7`` to ``v8`` in CI maintenance workflows to avoid GitHub Actions Node 20 deprecation warnings.

******
7.1.2
******

date: 2026-07-20


Details
=======

-  [fix] Fix inflated seasonal totals in ``icclim.sum(...)`` when converting filtered daily rate data such as precipitation in ``mm/day`` to amounts. Seasonal selections like ``MAM`` no longer integrate across inter-season gaps, so reproduced cases such as ``4228.6`` now correctly return ``310.4``.
-  [enh] Add a faster daily-source conversion path for seasonal rate-to-amount handling, preserving the bug fix without paying the full cost of rebuilding sparse seasonal timelines.
-  [enh] Add generalized reference-verification scripts and regression tests covering seasonal precipitation and non-precipitation cases, plus a developer protocol for broader Climpact/manual comparisons.
-  [fix] Tighten reference-verification summaries so mismatched period coordinates raise an error instead of being compared positionally.

******
7.1.1
******

date: 2026-06-22


Details
=======

-  [maint] Publish release metadata for ``v7.1.1``. The seasonal rate-conversion fix and its associated verification tooling ship in ``v7.1.2``.

******
7.1.0
******

date: 2026-03-17


Details
=======

-  [maint] Use pull requests for automated maintenance tasks (coverage, API, logos) in CI to support protected ``master`` branch.

-  [fix] Standardize degree Celsius representation to ``degC`` throughout core threshold logic to resolve metadata inconsistencies and assertion errors in tests.
-  [fix] Resolve critical ``UnboundLocalError`` and ``TypeError`` regressions in ``threshold/factory.py``.
-  [maint] Improve code quality and type safety by resolving dozens of Ruff lints in 21 core files.
-  [maint] Refactor core modules for **Ruff compliance** (PLR0915, PLR2004, ARG, PD, N), improve modularity in ``icclim.main.index``, and ensure backward compatibility for ``ignore_Feb29th`` parameter (#186).
-  [maint] Improve **CI robustness** by restricting automated commits (coverage, API, logos) to the ``master`` branch, preventing recurring merge conflicts in PRs.
-  [maint] Expand Ruff ``per-file-ignores`` to white-list conventional patterns (magic numbers, prints) in notebooks, tests, and utility scripts.
-  [fix] Increase viewBox width of SVG logos to prevent version text cropping (#269).
-  [maint] Integrate and update external notebooks from C3S and C4I, fixing path handling issues and updating to latest API (#354).
-  [enh] Add GitHub Action to automatically synchronize tutorials to external GitLab/GitHub repositories.
-  [doc] Update tutorials index and add icclim version compatibility notes to all notebooks.

-  [fix] Add automatic rate-to-amount conversion for snow depth indices (``SND``)
   to resolve ``DimensionalityError`` when input units are in ``mm/s`` (#320).
-  [maint] Drop support for **Python 3.9** and require **Python 3.10+**.
-  [maint] Update development status in ``pyproject.toml`` to **Production/Stable**.
-  [enh] Implement **lazy loading** for ``xclim`` imports to improve startup time.
-  [fix] Fix bootstrapping logic in ``percentile.py`` and resolve regressions in generated API.
-  [fix] Move ``time_bounds`` to coordinates in the resulting Dataset to avoid
   errors when calling ``.sum()`` on the entire Dataset (#340).
-  [enh] Add ``run_index`` parameter to RLE-based indices to allow specifying RLE indexing behavior (e.g., "first" vs "last") (#321).
-  [fix] Fix ``sum_of_spell_lengths`` (used by ``WSDI`` and ``CSDI``) to correctly sum all spells instead of only returning the maximum spell length.
-  [fix] Fix date calculation (``event_date_start``, ``event_date_end``) when using ``run_index="last"``.
- [fix] Resolve UnboundLocalError during snow depth index calculation in certain configurations.
- [doc] Add conda-forge installation instructions to ``README.rst`` and ``installation.rst``.
-  [doc] Rewrite ``release_process.rst`` with up-to-date conda-forge bot behavior, rerender procedure and automerge instructions.
-  [maint] Add ``typing-extensions>=4.0`` to dependencies for Python 3.10/3.11 compatibility.
-  [maint] Add ``CI`` URL to ``pyproject.toml`` project URLs for PyPI badge display.
-  [enh] Add inline doctests to CI test suite and expand test coverage for generic reducers (#109).
-  [doc] Remove deprecated ``create_optimized_zarr_store`` from API documentation (#138).
-  [enh] Add support for spatially varying seasons in all indices by allowing
   ``slice_mode`` to accept a tuple of ``DataArray`` objects representing
   day-of-year bounds (#170).
-  [enh] Add ``allow_partial_seasons`` parameter to ``icclim.index`` to include
   incomplete seasons at the beginning or end of a time series. It supports
   granular control: ``True`` (both), ``False`` (none), ``"start"`` (first only),
   or ``"end"`` (last only) (#350).
-  [fix] Suppress ``UserWarning`` from ``xclim`` regarding frequency inference by explicitly setting the ``freq`` attribute on time coordinates and using a warning filter during aggregation.
-  [change] **Behavioral change**: Temperature variables recognized via ``standard_name`` (e.g., ``air_temperature``) are now automatically converted to ``degree_Celsius`` before computation when units differ. This ensures correct ECA&D index computation regardless of the input unit (e.g., Kelvin). Users who previously managed unit conversion manually may see different output values if ``out_unit`` was not explicitly set.
-  [fix] Fix ``RuntimeError: cannot cache function '_keetch_byram_drought_index'`` that occurred on ``import icclim`` in conda environments where xclim is installed from a compiled package. The fix defers access to ``xclim.atmos`` attributes in ``ecad/binding.py`` from class definition time to first use via lazy ``@property`` definitions.

******
7.0.5
******

date: 2026-03-03

Details
=======

-  [maint] Relax dependency constraints in ``pyproject.toml`` (e.g., ``numpy>=1.21``,
   ``xarray>=2022.6.0``, ``xclim>=0.45.0``) while maintaining support for
   bleeding-edge versions (Zarr 3.x, Pandas 3.x, Xarray 2026.x).
-  [maint] Standardize all CI/CD workflows (``ci.yml``, ``publish-to-pipy.yml``) and
   pre-commit hooks on **Python 3.11**.
-  [maint] Drop support for **Python 3.9** and require **Python 3.10+**.
-  [maint] Update ``publish-to-pipy.yml`` to support PyPI trusted publishing.
-  [maint] Bump pre-commit hooks: ``ruff`` to ``v0.15.2+`` and ``toml-sort`` to
   ``v0.24.3``.
-  [maint] Refine API extraction tool (``extract_icclim_funs.py``) to handle circular
   imports and guarantee 100% Ruff compliance in all generated code.
-  [maint] Project-wide linting and formatting of core modules, tests, and tutorials.
-  [maint] Release 7.0.5.

******
 7.0.4
******

date: 2025-10-06

Details
=======

-  [maint] Adjust some pinned dependencies (numpy)
-  [maint] pypi bumped to 7.0.4

******
 7.0.3
******

date: 2025-09-25

Details
=======

-  [maint] pypi bump to 7.0.3

******
 7.0.2
******

date: 2025-09-24

Details
=======

-  [maint] Bumped all dependency packages according to latest xclim.
   Fixed the code to deal with breaking changes in xarray, pint, xclim.

******
 7.0.0
******

date: 2024-04-30

Breaking changes summary
========================

- New package architecture.
- New toolchain with flit and ruff.
- ``clt`` standard variable uint changed.
- ``clone`` method added to Indicators.

Details
=======

-  [maint] **BREAKING CHANGE**
   Created a `_core` package which should not be used outside icclim source.
   Its content may change without deprecation warnings.

-  [enh] Added DCSC indices under `icclim.dcsc` namespace.

-  [doc] Adapt Christian's notebooks from ISENES and add them as
   tutorials in our documentation.

-  [doc] Add nbshpinx extension to render jupyter notebooks in
   the online documentation.

-  [maint] Migrate from [black, blackdoc, flake8, isort, pyupgrade,
   pydocstyle] to ruff

-  [maint] Migrate from setup.py to pyproject.toml

-  [maint] Make readthedocs build fail when there are warnings

-  [maint] Fix warnings in doc build

-  [maint] **BREAKING CHANGE**
   Update architecture to have a `src/` and a `tests/` directory at root level

-  [maint] **BREAKING CHANGE**
   Migrate build toolchain from setuptools to flit

-  [maint] Remove version number from `constants` module as it was
   causing the build process to import icclim. The version number is now
   statically set in src/icclim/__init__.py

-  [fix] Force xarray to read dataset sequentially to avoid a netcdf-c
   threading issue causing seg faults.

-  [enh] Add `publish-to-pypi.yml` github action to automatically build
   and publish icclim to pypi. This action is triggered by a github
   release being published. This action requires a manual approval on
   github.

- [enh] Add the following ECAD indices: PP (average of pressure),
  SS (sum of sunshine) and RH (average of humidity).

- [fix] **BREAKING CHANGE**
  the default unit of ``clt`` standard variable is now % as expected
  (was a wind strenght unit).

- [maint] **BREAKING CHANGE**
  Rework architecture to have a ``_core`` **private** package
  containing the core logic of icclim. Idea taken from numpy 2.0.

- [doc] Add docstring to almost all functions, classes and modules.
  This has been done to improve the generated documentation.
  co-authored: Github's copilot.

- [maint] Add missing type hints.

- [doc] Make use of readthedocs' autoapi library to generate the API
  documentation.

- [maint] Improve maintainability of ``tools/extract-icclim-funs.py`` to
  ease adding new registries (still not perfect).

- [fix] **BREAKING CHANGE**
  Add ``clone`` method to Indicators to avoid modifying the original instance
  when setting templating metadata.


*******
 6.5.0
*******

date: 2023-12

-  [maint] Adapt generic indicators "excess" and "deficit" to xclim
   0.45.
-  [maint] Upgrade minimal python version to 3.9
-  [fix] Avoid resampling SPI* indices.

*******
 6.4.0
*******

date: 2023-05

-  [maint] Upgrade to xclim 0.43 (released on 09/05/2023).
-  [maint] Change how xclim is pinned to allow patch changes.

*******
 6.3.0
*******


date: 2023-04

-  [maint] Upgrade to xclim 0.42 (released on 04/04/2023).

-  [fix] **BREAKING CHANGE**
   The indicators based on the difference
   between two variables (ecad: DTR, ETR, vDTR and anomaly) gave wrong
   values due to a bad unit conversion of the output. This was for
   example the case when the input variables are in Kelvin, the
   difference between the two variables is still in Kelvin but it cannot
   be converted to degree Celsius with the ususal `+273.15`. To
   workaround this issue, we first convert inputs to the expected output
   unit and then we compute the index.

-  [fix] **BREAKING CHANGE**
   Indices based on both a percentile
   threshold and a `threshold_min_value` (for ecad: r75p, r75pTOT, r95p,
   r95pTOT, r99p, r99pTOT) are now computing the exceedance rate on
   values above `threshold_min_value` as well. Previously this
   `threshold_min_value` was used to compute the percentile and the
   total (for rxxpTOT indices) but not the exceedance rate.

*******
 6.2.0
*******

date: 2023-02

-  [maint] Upgrade and adapt to xclim 0.40. Moved PercentileDataArray
   from xclim to icclim. Adapted the unit cenversion to use the hydro
   context.

-  [fix] Pin xclim to exact 0.40 to avoid breaking changes.

*******
 6.1.5
*******

date: 2022-11

-  [fix] Bug fix: not assuming longitude and latitude are lon and lat
   with respect to output metadata. Fix needed to work on E-OBS and
   other datasets.

*******
 6.1.3
*******

date: 2022-11

-  [fix] Bug fix for TNx.

*******
 6.1.2
*******

date: 2022-11

-  [fix] Add missing file to properly identify user_indices as a
   package.

*******
 6.1.0
*******

date: ?

-  [fix] Add unit getter/setter for BoundedThreshold.

-  [enh] Add ECAD wind indices ``{fxx, fg6bft, fgcalm, fg, ddnorth,
   ddeast, ddsouth, ddwest}``. `ddnorth` and `ddsouth` do not follow the
   ECAD's ATBD v11 requirements as their definition seems to be wrong in
   the document.

-  [enh] Add generic indicators as stand-alone functions in `icclim`
   namespace.

-  [doc] Add documentation for generic indicators stand-alone functions.

-  [doc] Add a recipe "how to" documentation for generic indicators.

-  [enh] Add ECAD's indices GSL, SPI3, SPI6 by binding them to xclim's
   indicators.

-  [maint] Upgrade to xclim 0.39.0

*******
 6.0.0
*******


date: 2022-10

-  [enh] Add generic indices

-  [enh] Make in_files.var.threshold and threshold parameters work with
   string values (a value with a unit or a percentile stamp)

-  [maint] **BREAKING CHANGE**
   ECAD indices are no longer configurable!
   Use generic indices instead.

-  [fix] **BREAKING CHANGE**
   ECAD indices CW, CD, WW, WD were computing
   the precipitation percentiles on day of year values where it should
   have been percentiles of the whole period (excluding dry days). This
   has been fixed.

-  [maint] icclim no longer carries a version of the clix-meta yml file.
   Previously it was used to generate the doc string and a few metadata
   of ECAD indices. It's no longer needed as we have put these metadata
   within StandardIndex declaration.

-  [maint] **BREAKING CHANGE**
   Removed the `clipped_season` option from
   `slice_mode`. With generic indices, `season` can be used with every
   indices. In particular, spell based indices (e.g. wsdi, cdd) are
   mapped to `max_consecutive_occurrence` or `sum_of_spell_lengths`
   generic indicators. Both compute the spell length before doing the
   resampling operation. So a spell that start and end outside the
   output frequency interval is properly accounted for its whole
   duration. That's for example the case of `slice_mode="month"`, a
   spell that would start in january and end in March, would be
   accounted in january results. However, when `slice_mode` is set to a
   season, where time is clipped and thus where xclim `select_time` is
   called, the behavior is similar to the former `clipped_season`, we
   first clip the time to the expected season, then we compute the
   index. Thus, events of spells that are before the season bound will
   be ignored in the results.

-  [maint] **BREAKING CHANGE**
   User index `max_nb_consecutive_events` is
   also mapped to `max_consecutive_occurrence`, consequently spells are
   also counted for their whole duration.

-  [enh] Make it possible to pass a simple dictionary in `in_files`,
   merging together basic `in_files` and `var_name` features. It looks
   like `in_files={"tasmax": "tasmax.nc", "tasmin": "tasmin.zarr"}`

-  [enh] Add `min_spell_length` parameter to index API in order to
   control the minimum duration of spells in `sum_of_spell_lengths`.

-  [enh] Add `rolling_window_width` parameter to index API in order to
   control the width of the rolling window in
   `max|min_of_rolling_sum|average`.

-  [enh] Add `doy_window_width` parameter to index API in order to
   control the width of aggregation windows when computing doy
   percentiles.

-  [maint] Deprecate `window_width` parameter. When filled, it is mapped
   to it is still mapped to `doy_window_width`.

-  [maint] Upgrade to xclim 0.38 and to xarray 2022.6.

-  [maint] Add BlackDoc to C.I (github actions) to keep or doc code
   example clean.

-  [enh] Add ECAD's RR index. It computes the sum of precipitations over
   days.

-  [enh] Add icclim logo and auto-update its inner version number.

-  [maint] Enable git lfs (large file storage) for `.svg` files to
   minimise the impact on storage of logo updates.

-  [enh] Improve icclim.indices to enable multi indices computation
   based on variable names
   `icclim.indices(index_group='tasmax',in_files=data)`

-  [fix] **BREAKING CHANGE**
   ECAD snow indices now expect a snow (snd)
   variable instead of a precipitation one.

-  [enh] Add `build_threshold` function that acts as a factory to create
   different kind of Threshold.

-  [enh] Add BoundedThreshold class. It allows to compute multiple
   threshold for a single variable. This feature is necessary for
   indices such as ECAD's "DDnorth". Instances of BoundedThreshold are
   created with the `build_threshold` factory function, E.G.
   `build_threshold(">= -20 degree AND <= 20 degree ")`

-  [enh] Make it possible to compute multiple percentiles at once.

-  [maint] Update coverage computation. Now tests files are ignored when
   calculating the code coverage, thus it dropped a little (by 3%).

-  [enh] Convert input data that are recognized as a precipitation
   amount into precipitation rate. This is necessary to handle e-obs
   precipitation datasets.

*******
 5.4.0
*******

-  [fix] When giving input as a list of netcdf files, the coordinate
   values are now merged using the `override` strategy, thus the first
   file with a given dimension define this dimension for all the files.

-  [fix] Fix the output unit of some indices (from "°C" to
   "degree_Celsius")

-  [fix] Fixed issued where dataset having a time_bds variable could not
   be processed by chunking the DataArray(s) instead of the Dataset.

*******
 5.3.0
*******

-  [enh] Add icclim version to history in outputted metadata.

-  [maint] **BREAKING CHANGE**
   Pin minimal pandas version to 1.3 to have
   the fix for https://github.com/pandas-dev/pandas/issues/24539

-  [enh] ``slice_mode``: seasons can now be defined to be between two
   exact dates.

-  [enh] ``slice_mode`` type can now be tuple[str, list], it works
   similarly to the list in input of seasons but, it enforces a length
   of 2.

-  [enh] ``slice_mode``: Added `clipped_season` keyword which ignores
   events starting before the season bounds (original behavior of
   ``season``).

-  [maint] ``slice_mode``: Modified `season` keyword to take into
   account events (such as in CDD) starting before the season bounds.
   This should improve the scientific validity of these seasonal
   computations. Plus it is in accordance to xclim way of doing this.

-  [maint] Added dataclass ClimateIndex to ease the introduction of new
   indices not in the ECAD standard.

-  [maint] Made use the new typing syntax thanks to ``from __future__
   import annotations``.

-  [maint] Add docstring validation into flake8 checks.

-  [enh] Improve API for date related parameters ``{time_range,
   base_period_time_range, ref_time_range}`` They can still be filled
   with a datetime object but additionally various string format are now
   available. This comes with dateparser library.

-  [doc] Update callback doc as its outputted value is very inaccurate
   when dask is enable.

-  [enh] T(X/N/G)(10/90)p indices threshold is now configurable with
   `threshold` parameter. Example of use: `icclim.tx90p(in_files=data,
   threshold=[42, 99])`

-  [enh|maint] threshold, history and source metadata have been updated
   to better describe what happens during icclim process.

-  [fix/doc] The documentation of the generated API for T(X/N/G)(10/90)p
   indices now properly use thier ECAD definitions instead of those from
   ETCCDI.

-  [enh/doc] Add [WSDI, CSDI, rxxp, rxxpTOT, CW, CD, WW, WD] indices in
   yaml definition. Note: We no longer strictly follow the yaml given by
   clix-meta.

-  [fix] custom seasonal slice_mode was broken when it ended in
   december. It's now fixed and unit tested.

-  [enh] Make ``in_file`` accept a dictionary merging together
   ``var_name`` and ``in_file`` features.

-  [enh] ``in_file`` dictionary can now be used to pass percentiles
   thresholds. These thresholds will be used instead of computing them
   on relevant indices.

-  [maint/internal] Refactored IndexConfig and moved all the logic to
   input_parsing.

-  [fix] Add auto detection of variables [prAdjust, tasAdjust,
   tasmaxAdjust, tasminAdjust]

*******
 5.2.2
*******

[maint] Remove constraint on numpy version as numba is now working with
np 1.22.

*******
 5.2.1
*******

-  [maint] Made Frequency part of SliceMode union.

-  [fix] slice_mode seasonal samplings was giving wrong results for
   quite a few indices. This has been fixed and the performances should
   also be improved by the fix. However, now seasonal slice_mode does
   not allow to use xclim missing values mechanisms.

-  [fix] user_index ExtremeMode config was not properly parsed when a
   string was used.

-  [fix] user_index Anomaly operator was not properly using the
   `ref_time_range` to setup a reference period as it should.

-  [fix] user_index Sum and Mean operators were broken due to a previous
   refactoring and a lack of unit tests, it is now fixed and tested.

-  [maint] Changed how `rechunker` dependency is pinned to add
   flexibility. We want a version above '0.3' but not the '0.4'.

-  [maint] For the newly generate API, on `custom_index` function, the
   parameter `user_index` is now mandatory.

*******
 5.2.0
*******

-  [maint] Update release process.
-  [enh] Improve `create_optimized_zarr_store` to accept a chunking
   schema instead of a single dim.
-  [enh] Make use of `fsspec` to generalize the storages where
   `create_optimized_zarr_store` can create its zarr stores.
-  [enh] Make CSDI and WSDI threshold configurable using the `threshold`
   parameter of icclim.index.
-  [enh] Add a function in `icclim` namespace for each ECA&D index for
   convenience.
-  [doc] Improve documentation about chunking.
-  [fix] `create_optimized_zarr_store` would throw an error when
   creating the first temp store if the chunks were not unified.

*******
 5.1.0
*******

-  [maint] **BREAKING CHANGE**
   Parameter ``out_file`` of icclim.index
   default value is now ``None``. When None, ``icclim.index`` only
   returns a xarray.Dataset and does not write to a default netcdf file.

-  [enh] Add code coverage in CI. This writes a comment with the full
   report in the PR.

-  [enh] Add coverage and conda badges in Readme.

-  [tst] Add unit test for modules ``main``, ``dispatcher``,
   ``cf_calendar``.

-  [fix] Rework ``cf_calendar`` following unit test writing.

-  [tst] Add simple integration test for ``icclim.index`` using index
   "SU".

-  [maint] Remove old, unmaintained integration tests and auxiliary
   tools. See 9ac35c2f_ for details.

-  [maint] Upgrade to xclim 0.34.

-  [fix] WSDI and CSDI percentile were computed on the studied period
   instead of the reference period.

-  [maint] Internal refactoring ``icclim.main`` module to ease
   maintainability.

-  [doc] Add contribution guide.

-  [enh] Add API endpoint ``icclim.create_optimized_zarr_store``. It is
   a context manager wrapping `rechunker` in order to rechunk a dataset
   without any chunk a given `dim` dimension.

-  [fix] Add zarr dependency, needed to update zarr store metadata after
   rechunking.

-  [fix] Fix installation from sources. The import in setup.py to get
   ``__version__`` meant we needed to have the whole environment
   installed before the moment it is actually installed by ``setup.py``.

-  [enh] Add API endpoint ``icclim.indices``. This allows to compute
   multiple indices at once.

-  [maint] Pin `dask` to its versions before `2022.01.1`. This is
   necessary for rechunker 0.3.3 to work.

-  [maint] Update types to use modern python typing syntax.

-  [fix] CI was passing even when tests were in failure. This has been
   fixed.

.. _9ac35c2f: https://github.com/cerfacs-globc/icclim/commit/9ac35c2f7bda76b26427fd433a79f7b4334776e7

*******
 5.0.2
*******

-  [fix] Update extracting script for C3S. imports were broken.
-  [doc] Update release process doc.
-  [fix] Bug on windows breaking unit tests.
-  [fix] Bug on windows unable to get the timezone in our logger.
-  [fix] Pin to numpy 1.21 for now. Numba seems to dislike version 1.22
-  [fix] LICENCE was still not exactly following Apache guidelines.
   NOTICE has been removed.

*******
 5.0.1
*******

-  [fix] Modify LICENCE and NOTICE to follow Apache guidelines. LICENCE
   has also been renamed to english LICENSE.

*******
 5.0.0
*******

We fully rewrote icclim to benefit from Xclim, Xarray, Numpy and Dask. A
lot of effort has been to minimize the API changes. Thus for all scripts
using a former version of icclim updating to this new version should be
smooth.

We made a few improvements on the API
   -  We replaced everywhere the french singular word "indice" by the
      proper english "index". You should get a warning if you still use
      "indice" such as in "indice_name".

   -  When ``save_percentile`` is used, the resulting percentiles are
      saved within the same netcdf file as the climate index.

   -  Most of the keywords (such as slice_mode, index_name, are now case
      insensitive to avoid unnecessary errors.

   -  When ``in_files`` is a list the netcdf are combined to lookup them
      all the necessary variables.

   -  When multiple variables are stored into a single ``in_files``,
      there is no more need to use a list.

   -  ``in_files`` parameter can now be a Xarray.Dataset directly. In
      that case, ``out_file`` is ignored.

   -  ``var_name`` parameter is now optional for ECA&D indices, icclim
      will try to look for a valid variable depending on the index
      wanted

   -  ``transfer_limit_Mbytes`` parameter is now used to adjust how Dask
      should chunk the dataset.

   -  The output of ``icclim.index()`` is now the resulting Xarray
      Dataset of the index computation. ``out_file`` can still be used
      to write output to a netcdf.

   -  `logs_verbosity` parameter can now control how much logs icclim
      will produce. The possible values are ``{"HIGH", "LOW",
      "SILENT"}``.

Additionally
   -  icclim C code has also been removed. This makes the installation
      and maintenance much easier.
   -  Climate indices metadata has been enriched with Xclim metadata.
   -  With this rewrite a few indices were fixed as they were giving
      improper results.
   -  Performances have been significantly improved, especially thanks
      to Dask.

Breaking changes
================

Some utility features of icclim has been removed in 5.0.0. This include
`util.regrid` module as well as `util.spatial_stat` module. For
regridding, users are encouraged to try `xESMF
<https://pangeo-xesmf.readthedocs.io/en/latest>`_ or to use xarray
selection directly. For spatial stats, Xarray provides a
`DataArrayWeighted
<https://xarray.pydata.org/en/stable/generated/xarray.DataArray.weighted.html>`_

.. note::

   It is highly recommended to use Dask (eventually with the distributed
   scheduler) to fully benefit from the performance improvements of
   version 5.0.0.

Release candidates for 5.0 change logs
======================================

-  [fix] Make HD17 expect tas instead of tas_min.
-  [fix] Fix performance issue with indices computed on consecutive days
   such as CDD.
-  [maint] Add Github action CI to run unit tests.
-  [maint] Add pre-commit CI to fix lint issues on PRs.
-  [maint] Update sphinx and remove old static files.
-  [doc] Restructure documentation to follow diataxis principles.
-  [doc] Add some articles to documentation.
-  [maint] Drop support for python 3.7
-  [maint] Add github templates for issues and pull requests.
-  [maint] Simplify ecad functions output to a single DataArray in most
   cases.
-  [fix] Fix lint for doc conf.
-  [fix] Add all requirements to requirements_dev.txt
-  [doc] Update Readme from md to rst format. Also changed content.
-  [doc] Add a dev documentation article "how to release".
-  [doc] Add a dev documentation article "continuous integration".
-  [doc] Update installation tutorial.
-  [doc] Various improvements in doc wording and display.
-  [doc] Start to documente ECA&D indices functions.
-  [doc] Add article to distinguish icclim from xclim.
-  [maint] Refactored ecad_functions (removed duplicated code,
   simplified function signatures...)
-  [maint] Refactored IndexConfig to hide some technical knowledge which
   was leaked to other modules.
-  [enh] Made a basic integration of clix-meta yaml to populate the
   generated docstring for c3s.
-  [maint] This makes pyyaml a required dependency of icclim.
-  [fix] Fixed an issue with aliasing of "icclim" module and "icclim"
   package
-  [maint] Added some metadata to qualify the ecad_indices and recognize
   the arguments necessary to compute them.
-  [maint] Added readthedocs CI configuration. This is necessary to use
   python 3.8.
-  [enh] Added `tools/extract-icclim-funs.py` script to extract from
   icclim stand-alone function for each indices.
-  [enh] Added `icclim.indices` function (notice plural) to list the
   available indices.

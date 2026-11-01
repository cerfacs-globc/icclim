Post-7.3 correctness audit
==========================

Audit date: 2026-11-01.

Scope
-----

This audit ran against an integration branch containing the pending #517, #518,
and #519 changes plus the already identified leap-reference fix from #514.  It
looked for silent wrong values and crashes; it intentionally contains no fixes.

Confirmed findings
------------------

The findings are ranked by silent wrong values first, then crashes.  Every item
has a public-API reproducer in ``tests/test_bug_hunt_regressions.py`` and a
separate GitHub issue.

1. **Non-month percentage counts are 100 times too small**
   (`issue #520 <https://github.com/cerfacs-globc/icclim/issues/520>`__).
   A complete annual period returns ``1 %`` instead of ``100 %``.  YEAR,
   AMJJAS, ONDJFM, DJF, MAM, JJA and SON divide by the period length but do not
   multiply by 100.  Custom frequencies return raw counts which the caller then
   labels ``%``.  Public API: ``count_occurrences``.  Released 7.3.0: **yes**.
   Failing test:
   ``test_count_occurrences_percent_scales_annual_fraction_by_100``.

2. **ONDJFM uses the wrong year to choose its leap-day denominator**
   (`issue #521 <https://github.com/cerfacs-globc/icclim/issues/521>`__).
   October 1999--March 2000 contains 183 days, but the output timestamp lies in
   1999 and selects 182.  This remains independently wrong after correcting the
   general percent scaling.  Public API: ``count_occurrences``.  Released
   7.3.0: **yes**.  Failing test:
   ``test_count_occurrences_ondjfm_uses_february_year_for_denominator``.

3. **A 360-day annual percentage uses a 365-day denominator**
   (`issue #523 <https://github.com/cerfacs-globc/icclim/issues/523>`__).
   A complete year is calculated as ``360 / 365``.  Public API:
   ``count_occurrences``.  Released 7.3.0: **yes**.  Failing test:
   ``test_count_occurrences_percent_uses_360_day_year_length``.

4. **No-event consecutive runs report the first date as an event**
   (`issue #524 <https://github.com/cerfacs-globc/icclim/issues/524>`__).
   The value is correctly zero, but ``event_date_start`` and
   ``event_date_end`` both point at the period's first day rather than being
   missing.  Public API: ``max_consecutive_occurrence(date_event=True)``.
   Released 7.3.0: **yes**.  Failing test:
   ``test_max_consecutive_no_event_has_missing_event_dates``.

5. **Wet days equal to the percentile floor are omitted from fraction totals**
   (`issue #525 <https://github.com/cerfacs-globc/icclim/issues/525>`__).
   For ``[1, 1, 10, 10] mm/day`` and a 1 mm/day wet-day floor, the result is
   100% instead of ``20 / 22 * 100 = 90.909...%``.  The percentile comparison
   operator (``>``) is incorrectly reused for the inclusion floor.  Public
   APIs: ``fraction_of_total``, R75pTOT, R95pTOT and R99pTOT.  Released 7.3.0:
   **yes**.  Failing test:
   ``test_fraction_of_total_includes_values_equal_to_wet_day_minimum``.

6. **Multiple fixed-calendar years crash during annual percent conversion**
   (`issue #522 <https://github.com/cerfacs-globc/icclim/issues/522>`__).
   The fixed-calendar leap callbacks build ``np.full_like(da.shape, ...)``;
   three output years therefore produce a one-element boolean mask and an
   ``IndexError``.  Public API: ``count_occurrences`` on noleap, 360-day or
   all-leap cftime input.  Released 7.3.0: **yes**.  Failing test:
   ``test_count_occurrences_percent_supports_multiple_noleap_years``.

7. **Preserved Dask chunks can be too short for rolling windows**
   (`issue #526 <https://github.com/cerfacs-globc/icclim/issues/526>`__).
   A three-day rolling operation on two-day time chunks raises ``ValueError``.
   Public APIs: rolling sum/average extrema and RX5day.  Released 7.3.0:
   **no**; this is a regression in the #518 integration state.  Failing test:
   ``test_rolling_sum_accepts_dask_time_chunks_smaller_than_window``.

Oracle and option coverage
--------------------------

``tests/test_generic_numpy_oracles.py`` supplies independent NumPy or pandas
value oracles for all 20 public generic indicators.  Result: **20/20 passed**.
It covers simple extrema and moments, sums, four rolling reducers, threshold
counts/runs/spells, excess/deficit, fraction of total, all four two-variable
reducers, and percentile.

``tests/test_audit_option_metamorphic.py`` adds 19 checks.  Result: **19/19
passed**.  These compare eager and multiple Dask chunkings over month, year,
DJF and ONDJFM; compare eager/chunked results on standard, noleap, 360-day and
all-leap calendars; and check offset invariance, spatial-dimension permutation,
and isolated-period/full-run equivalence.

Independent ECAD value-oracle coverage is currently **0/64**.  The existing
suite invokes all ECAD indices and checks API routing/output existence, but it
does not compare all 64 values with an implementation independent of icclim or
xclim.  This is an important remaining audit gap, especially for GSL, SPI3 and
SPI6, which do not map directly to one of the generic reducers.

Branch coverage
---------------

The existing suite (excluding only the intentionally failing regression file)
completed with **686 passed**.  Branch coverage was:

* ``generic/functions.py``: 84% (1,110 statements, 142 missed; 412 branches,
  83 partial)
* ``input_parsing.py``: 73% (292 statements, 71 missed; 134 branches, 23
  partial)
* ``frequency.py``: 84% (246 statements, 31 missed; 64 branches, 8 partial)
* combined: 82%

Notably, the entire percent-conversion block at lines 3589--3624 was reported
uncovered by the instrumented baseline despite one existing monthly assertion.
The baseline required ``PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`` because automatic
plugin loading imported incompatible NumPy installations in the local Python
environment.

Mutation testing
----------------

Mutmut is configured in ``pyproject.toml`` for the three requested modules and
for covered lines only.  The intentionally failing regressions and two helper
test modules that depend on an uncopied top-level ``tools`` package are excluded
from mutation-test collection.  Dependency tracing selected 28 mutants: **7
killed, 2 had no covering tests, and 19 timed out** with the deliberately short
15-second limit.  No evaluated mutant survived a test that actually ran.

The two uncovered/surviving mutants both change the default ``dim`` argument of
``frequency.infer_input_frequency`` (from ``"time"`` to ``"XXtimeXX"`` or
``"TIME"``).  Mutmut found no test depending on that default.  The timed-out
mutants were in the path classifiers in ``input_parsing.py`` and in
``_profile_bootstrap_inc``, ``_reduce_and_diff``,
``_note_generic_bootstrap_capability``, ``_run_simple_reducer``,
``_compute_combined_exceedance_mask``,
``_compute_threshold_exceedance_mask`` and ``check_freq``.  Timeouts are
inconclusive and should not be counted as killed or survived.

Recommended order
-----------------

Fix #520 first because it masks the magnitude of #521 and #523.  Keep #521 and
#523 as independent denominator tests.  #525 is the most consequential ECAD
value error.  #522 and #526 are crashes; #526 should be resolved before #518 is
merged.  #524 is lower numerical impact but misleading metadata and should keep
its own regression test.

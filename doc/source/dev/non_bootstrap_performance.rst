.. _dev_non_bootstrap_performance:

####################################
Non-bootstrap performance invariants
####################################

This note records the behavior that must remain stable during the post-7.3.0
non-bootstrap performance work. The corresponding golden tests are in
``tests/test_non_bootstrap_golden.py``. They cover date-event reducers,
rolling reducers and reference-difference reducers at daily and monthly
frequencies.

Date-event semantics
====================

The current extreme date-event implementation has behavior that should not be
silently changed by a performance refactor. ``maximum`` and ``minimum`` attach
the date of the requested extreme but return the sum of the values in the
period. This conflicts with the public reducer definitions and is therefore
treated as a correctness defect, not intended semantics. The existing value is
golden-tested so that a later correction can be reviewed as its own behavioral
change.

Rolling reducers currently accept the public ``date_event`` option but raise
``NotImplementedError`` when it is enabled. The rolling functions pass a lambda
to the shared date-event helper, while that helper recognizes only the bound
``DataArrayResample.max`` and ``DataArrayResample.min`` methods. The golden
tests record this unsupported state; adding rolling event dates requires a
separate correctness decision.

Dask indexer compatibility
==========================

The xarray issue cited by the date-event TODO,
`xarray issue 2511 <https://github.com/pydata/xarray/issues/2511>`_, was closed
when `xarray pull request 5873
<https://github.com/pydata/xarray/pull/5873>`_ merged on March 15, 2023.
icclim still declares ``xarray>=2022.6.0``, which predates that fix, so the
minimum supported version cannot rely on it.

In addition, the public max/min date-event path still attempts vectorized
indexing with a Dask-backed ``argmax`` result and fails with current xarray and
Dask for auto-chunked input. Removing eager index materialization therefore
requires an explicit compatibility implementation and tests; closing the cited
upstream issue alone is not sufficient evidence.

Refactoring rule
================

Performance changes must preserve the successful golden results exactly. Known
incorrect or unsupported date-event behavior should be corrected deliberately
in a separately reviewed behavioral change rather than as a side effect of
vectorization.

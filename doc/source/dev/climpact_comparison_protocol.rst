#############################
 Climpact Comparison Protocol
#############################

Use this protocol when a user reports a discrepancy and can provide both the NetCDF
file and the exact ``icclim`` command they used.

Why this protocol exists
------------------------

Climpact is an external reference implementation for ET-SCI style indices, and its
official guidance is based on **daily** temperature and rainfall data. See:

- https://climpact-sci.org/
- https://climpact-sci.org/assets/climpact2-user-guide.pdf
- https://github.com/ARCCSS-extremes/climpact

For ``icclim``, the most useful verification chain is:

1. confirm the source data frequency and units,
2. compare ``icclim`` against a direct xarray manual calculation,
3. when the index is Climpact-compatible, export a point subset and compare against Climpact.

Assessment checklist
--------------------

Before comparing outputs, record:

- ``icclim`` version
- ``xclim`` version
- the full user command
- the input variable name and units
- the inferred source frequency
- whether the user is supplying daily data or already aggregated monthly/seasonal data

Important constraint
--------------------

Climpact's reference workflow is defined for **daily** rainfall data. If the source
dataset is already monthly or seasonal, do not treat a Climpact mismatch as evidence
of an ``icclim`` bug. In that case, first reduce the report to a daily-input
reproduction, or classify it as a non-daily-input limitation.

Repo workflow
-------------

Run the helper script with the user dataset and the same ``index_name`` and
``slice_mode`` used in their report.

Example:

.. code-block:: bash

   PYTHONPATH=src python scripts/verify_index_against_reference.py \
     --in-file /path/to/user.nc \
     --var-name pr \
     --index-name PRCPTOT \
     --slice-mode 'JJA' \
     --isel lat=10 \
     --isel lon=12 \
     --output-dir /tmp/icclim-climpact-check

The script writes:

- ``summary.json``: metadata, ``icclim`` values, manual xarray values, and max absolute difference
- ``reference_subset.nc``: a reduced NetCDF file that can be used for the external Climpact run when relevant

Supported manual comparators
----------------------------

The helper currently includes simple reference calculations for these common cases:

- precipitation: ``RR``, ``PRCPTOT``, ``RR1``, ``R10mm``, ``R20mm``
- temperature occurrence counts: ``SU``, ``TR``
- means: ``TG``, ``TX``, ``TN``
- extrema: ``TXx``, ``TNx``, ``TXn``, ``TNn``

This is intentionally conservative. If a new report lands outside this set, add the
manual comparator first, then use the same workflow.

How to interpret the result
---------------------------

- If ``icclim`` matches the manual xarray reference on daily input, the reducer is
  behaving as expected in ``icclim``.
- If both differ from Climpact, inspect calendar handling, wet-day threshold
  semantics, and Climpact input preparation.
- If ``icclim`` differs from manual xarray on daily input, treat that as a likely
  ``icclim`` bug and add a regression test before fixing it.

Recommended regression coverage
-------------------------------

Any confirmed bug report should add at least one test covering:

- a named season such as ``JJA`` or ``DJF``
- a custom season via ``("season", ...)``
- the reported index on daily input
- a manual xarray reference used as the expected value

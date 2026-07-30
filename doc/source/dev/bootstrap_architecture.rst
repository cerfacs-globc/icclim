.. _dev_bootstrap_architecture:

######################
Bootstrap architecture
######################

This note describes a maintainable design for percentile bootstrap work
after the July 29, 2026 Kraken validation round.

It complements :ref:`dev_percentile_bootstrap`, which records the
current production behavior and benchmark results. This document is
about structure: which bootstrap families exist, which reusable
functions they should share, and how to keep the implementation readable
as support grows.

Design goals
============

Bootstrap code should be:

- exact with respect to the safe reference bootstrap implementation;
- explicit about what is supported, what falls back, and what is still
  unsupported;
- organized around a small number of reusable calculations rather than a
  growing list of special cases;
- easy for maintainers to read, debug and extend.

Readability matters as much as raw performance. The implementation
should prefer clear control flow, descriptive variable names and small
helpers with stable responsibilities over clever compression of several
steps into one function.

This is also aligned with FAIR for Research Software (FAIR4RS). In this
context, readable code is not only a style preference. It directly
supports software reuse, inspection, onboarding and reliable extension
by future maintainers.

Guiding principles
==================

Use the following rules when extending bootstrap support:

- Separate threshold generation from result aggregation.
- Classify support by mathematical family, not by index short name.
- Keep the safe tiled path as the reference bootstrap implementation for every new optimized
  implementation.
- Prefer a small number of well-named helpers over large mixed-purpose
  functions.
- Make routing decisions explicit in one place rather than scattering
  eligibility checks across reducers.

Bootstrap families
==================

Bootstrap support should be described in terms of algorithm families.
Named indices and generic indices can then map onto those families.

Percentile count family
-----------------------

This family covers indices where bootstrap means:

- recompute a percentile threshold with substitute-year substitution;
- compare daily values to that threshold;
- aggregate the daily boolean mask as counts.

Examples:

- ``TG90p``, ``TN90p``, ``TX90p``;
- ``TG10p``, ``TN10p``, ``TX10p``;
- generic ``count_occurrences`` with one percentile threshold.

Percentile filtered-count family
--------------------------------

This family is similar to the count family, but the percentile sample is
filtered before percentile computation.

Examples:

- ``R75p``, ``R95p``, ``R99p``;
- generic percentile counts using ``threshold_min_value``.

The Kraken validation showed that this family cannot be treated as a
minor variant of the plain count family. Its substitute-year semantics must
be matched exactly before any compiled optimized path is enabled.

Percentile amount and fraction family
-------------------------------------

This family uses percentile bootstrap to define exceedance days, but the
final result is not a count. Instead it aggregates the values on those
days.

Examples:

- ``R75pTOT``, ``R95pTOT``, ``R99pTOT``;
- generic ``sum``, ``average``, ``fraction_of_total``, ``maximum`` or
  ``minimum`` with percentile thresholds.

Percentile spell family
-----------------------

This family depends on temporal structure after thresholding. It cannot
be reduced to independent daywise counts.

Examples:

- ``WSDI``, ``CSDI``;
- generic spell or consecutive-event indicators using percentile
  thresholds.

Percentile compound family
--------------------------

This family combines several threshold conditions, possibly across
variables and threshold types.

Examples:

- ``CD``, ``CW``, ``WD``, ``WW``;
- generic multi-threshold percentile compositions.

Non-bootstrap family
--------------------

Some indices do not need percentile bootstrap at all.

Examples:

- scalar-threshold counts such as ``SU``, ``TR``, ``RR1``;
- scalar-threshold spells such as ``CDD`` and ``CWD``;
- simple sums, means and extrema such as ``TG``, ``RR`` and
  ``RX1day``.

These should be classified as ``bootstrap_not_required`` rather than
mixed into unsupported cases.

Capability matrix
=================

Every percentile-based generic index should be routed through one
classifier that answers four questions:

1. Is bootstrap required?
2. If it is required, which family does the index belong to?
3. Can the optimized implementation be used?
4. If not, should icclim fall back to the safe tiled path or reject the
   request as unsupported?

The classifier should use explicit fields rather than index names:

- threshold kind:
  ``basic``, ``doy_percentile``, ``period_percentile``,
  ``multiple_thresholds``;
- threshold filter:
  none or ``threshold_min_value``;
- operator:
  ``>``, ``>=``, ``<``, ``<=`` or other;
- reducer family:
  count, masked-value aggregate, spell, consecutive-event, compound;
- number of input variables:
  one or many;
- calendar type:
  pandas-compatible, Gregorian-like ``cftime``, other ``cftime``;
- output frequency:
  annual, monthly, anchored seasonal, other;
- threshold count:
  one or many.

The classifier result should be a small explicit object rather than a
boolean. For example, it should carry:

- whether bootstrap is required;
- the bootstrap family;
- the chosen execution path:
  ``optimized_bootstrap``, ``exact_tiled_bootstrap``, ``unsupported``, ``not_required``;
- a short reason code for logs, tests and debugging.

As of July 30, 2026, this classifier exists in
``src/icclim/_core/generic/bootstrap_capability.py`` for the current
generic indicator families:

- day-of-year percentile count;
- filtered day-of-year percentile count;
- value aggregates such as ``fraction_of_total``;
- spell reducers such as ``sum_of_spell_lengths``;
- bounded percentile compositions that currently stay on the reference
  bootstrap path.

Reusable bootstrap primitives
=============================

The long-term goal is to make each bootstrap algorithm a composition of
shared primitives rather than a separate stack.

Reference sample preparation
----------------------------

One helper should own:

- extracting the reference-period subset;
- converting units needed for percentile computation;
- applying optional sample filtering such as ``threshold_min_value``;
- exposing year and day lookup data used by substitute-year logic.

Suggested names:

- ``reference_sample``
- ``filtered_reference_sample``
- ``reference_year_index``
- ``reference_day_of_year``

Avoid short names such as ``ref2`` or ``idx_map`` when the longer name
removes ambiguity.

As of July 30, 2026, this layer now starts to exist in
``src/icclim/_core/generic/bootstrap_primitives.py`` with explicit,
tested helpers for:

- ``build_bootstrap_reference_sample``;
- ``build_bootstrap_temporal_indexing``;
- ``build_bootstrap_array_inputs``.

Those helpers keep the bootstrap preparation workflow readable in code:

1. prepare the reference-period sample;
2. prepare year and resampling indexes;
3. prepare flattened arrays for an optimized kernel;
4. run the family-specific kernel;
5. rebuild xarray outputs.

That is still only a first step. Threshold generation itself is not yet
fully extracted into a reusable engine, but the preparation phases now
have a stable home and direct unit tests.

Bootstrap threshold generation
------------------------------

One threshold engine should own:

- substitute-year substitution rules;
- day-of-year percentile logic;
- period percentile logic;
- interpolation behavior;
- calendar-aware alignment between study days and reference days.

This is the most important reusable layer. Count, amount, fraction and
spell reducers should all consume the same threshold semantics.

Suggested helper responsibilities:

- ``build_bootstrap_thresholds_for_year``
- ``build_nominal_thresholds``
- ``build_substitute_thresholds``
- ``align_thresholds_to_study_days``

As of July 30, 2026, the optimized day-of-year percentile count path
now follows this separation inside
``src/icclim/_core/generic/bootstrap.py``:

- ``_build_bootstrap_threshold_series_for_cell`` computes one
  substitute-aware threshold series;
- ``_write_count_groups_for_cell`` and
  ``_accumulate_count_groups_for_cell`` apply the count reducer to that
  threshold series.

This is still specific to the current count implementation, but it is a
useful intermediate step because it makes the scientific boundary
visible in code before more bootstrap families reuse the same threshold
generation semantics.

Daily exceedance mask construction
----------------------------------

One helper should convert values and thresholds into a daily boolean
mask using a well-defined comparison operator.

Suggested names:

- ``compute_exceedance_mask``
- ``compare_values_to_thresholds``

This should be shared by all reducer families.

Reducer primitives
------------------

After a daily exceedance mask exists, the remaining work should be
handled by separate reducers.

Count reducer
^^^^^^^^^^^^^

Consumes a daily exceedance mask and returns counts per output period.

Suggested name:

- ``count_masked_days``

Masked value reducer
^^^^^^^^^^^^^^^^^^^^

Consumes a daily exceedance mask and studied values, then returns sums,
means or extrema over selected days.

Suggested names:

- ``sum_selected_values``
- ``mean_selected_values``
- ``maximum_selected_value``
- ``minimum_selected_value``

Fraction reducer
^^^^^^^^^^^^^^^^

Consumes a daily exceedance mask and studied values, then returns the
selected-value sum divided by the total sum over the same output period.

Suggested name:

- ``fraction_of_selected_values``

Spell reducer
^^^^^^^^^^^^^

Consumes a daily exceedance mask and computes spell or run-length
metrics.

Suggested names:

- ``sum_spell_lengths``
- ``maximum_spell_length``
- ``spell_event_dates``

Compound mask combiner
^^^^^^^^^^^^^^^^^^^^^^

Consumes several masks and combines them using explicit logical rules.

Suggested names:

- ``combine_exceedance_masks``
- ``apply_logical_link_to_masks``

Module boundaries
=================

The implementation should make it obvious where to look for each kind
of logic.

Suggested split:

- a capability module that classifies bootstrap requests;
- a threshold engine module that computes bootstrapped thresholds;
- a reducer module that turns daily masks into final outputs;
- a dispatch layer that chooses ``optimized_bootstrap`` or ``exact_tiled_bootstrap`` and wires
  the pieces together.

The important part is not the exact filenames. It is that the code
should avoid mixing all of these responsibilities in the same function.

Naming and readability rules
============================

To keep the code understandable for humans:

- prefer ``reference_sample`` over ``ref`` when the longer name makes
  the role clearer;
- prefer ``target_year_index`` and ``substitute_year_index`` over short loop
  names that require reading several surrounding lines;
- prefer ``study_day_of_year`` over ``study_doys`` in higher-level
  helpers, while compact local names are acceptable inside tight kernels;
- avoid helpers that both compute thresholds and aggregate results;
- keep data preparation, routing and numerical kernels visibly separate;
- write short comments for non-obvious scientific rules, not for obvious
  control flow.

Compiled kernels may still use shorter local variable names where that
substantially improves the shape of the loop, but the public Python
helpers around them should remain descriptive.

Readability beyond bootstrap
============================

These rules should apply to icclim more broadly, not only to bootstrap
code.

Function design
---------------

- Each function should have one main responsibility that can be stated
  in a short sentence.
- Functions should return data at a clear level of abstraction. Avoid
  helpers that partly prepare data, partly dispatch, and partly compute
  the final scientific result.
- If a helper needs several boolean flags to change behavior, it is
  often a sign that the responsibility is too broad.

Naming
------

- Names should reflect the scientific role of the object, not just its
  type.
- Prefer names such as ``reference_period_bounds``,
  ``bootstrap_thresholds`` or ``exceedance_mask`` over generic names
  such as ``data2``, ``tmp`` or ``result2``.
- Variable names should distinguish raw values, filtered values, masks
  and aggregated outputs.

Structure
---------

- Keep orchestration code in Python helpers and tight numerical work in
  focused kernels.
- Keep threshold semantics, mask semantics and aggregation semantics in
  different helpers or modules.
- Prefer explicit small intermediate values over deeply nested
  expressions when the intermediate names make the scientific meaning
  clearer.

Comments and documentation
--------------------------

- Use comments to explain scientific intent, edge cases and constraints.
- Do not use comments to restate obvious code.
- When behavior follows an external definition or guideline, reference
  that definition in a nearby docstring, comment or maintainer note.

Tests as readability support
----------------------------

- Tests should reveal the intended behavior, not only guard against
  regressions.
- Prefer test names that explain the scientific case and the expected
  routing decision.
- Where bootstrap dispatch matters, tests should state whether the case
  is expected to use the optimized path, exact tiled bootstrap, or no
  bootstrap at all.

FAIR4RS implications
====================

The FAIR4RS principles are broader than naming and formatting, but they
do have concrete implications for code structure.

Findable
--------

The relevant logic should be easy to locate. A maintainer should be able
to answer:

- where bootstrap routing happens;
- where percentile semantics are defined;
- where each reducer family is implemented;
- where real-data validation rules are documented.

This is much easier when responsibilities are split into explicit
modules, with stable names and maintainer notes.

Accessible
----------

The code should be understandable without hidden tribal knowledge.
Docstrings, developer notes and descriptive function names make the
implementation accessible to contributors who did not write the original
feature.

Interoperable
-------------

Interoperability is not only about file formats and APIs. Internally,
icclim code should use shared concepts and shared data shapes across
bootstrap families:

- threshold engine outputs should look consistent across day-of-year and
  period percentiles;
- exceedance masks should have one standard meaning;
- reducers should consume well-defined inputs rather than custom
  per-index structures.

Reusable
--------

Reusability is where readability and architecture meet most directly.
Code becomes easier to reuse when:

- helpers have narrow, stable responsibilities;
- the same threshold engine can feed several reducers;
- tests describe the support boundary clearly;
- capability routing is explicit and inspectable.

In practice, FAIR4RS for this part of icclim means that a future
maintainer should be able to add one new climate-index family by reusing
existing primitives rather than reverse-engineering a monolithic
bootstrap implementation.

Recommended implementation order
================================

The best coverage-per-effort order is:

1. implement the capability classifier;
2. extract the reusable threshold-generation layer;
3. keep the current count reducer on top of that shared layer;
4. add masked-value and fraction reducers for ``R*pTOT``-style indices;
5. add a spell reducer for ``WSDI`` and ``CSDI``;
6. add compound-mask composition for indices such as ``CD`` and ``CW``.

At each step:

- compare against the safe tiled reference path;
- validate on real data, not only synthetic examples;
- record both performance and field equality;
- widen dispatch only after Kraken validation is exact.

What success looks like
=======================

The target state is not a single giant bootstrap implementation. It is a
small architecture where:

- one classifier explains what path any generic index will take;
- one threshold engine defines percentile bootstrap semantics;
- several simple reducers reuse those semantics;
- optimized implementations can be added family by family without rewriting
  bootstrap logic.

If the code reaches that shape, adding support for new climate indices
should mostly mean mapping them to an existing family or adding one new
reducer, not inventing a new bootstrap system each time.

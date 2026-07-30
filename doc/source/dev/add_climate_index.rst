.. _dev_add_climate_index:

############################
Add A New Climate Index
############################

This note is for contributors who need to add or extend a climate index
in icclim.

It is written for maintainers who may be strong scientific developers
without being full-time software engineers. The goal is to make the
workflow easy to follow before looking at low-level implementation
details.

Read this together with:

- :ref:`dev_bootstrap_architecture` for percentile-bootstrap families;
- :ref:`dev_percentile_bootstrap` for the current production bootstrap
  boundary;
- :ref:`generic_indices_recipes` for the public generic-index API.

Workflow Overview
=================

The end-to-end path for one climate-index request is:

1. The user calls :func:`icclim.index`.
2. icclim normalizes deprecated parameters and builds an
   :class:`~icclim._core.model.index_config.IndexConfig`.
3. Input files and thresholds are converted into
   :class:`~icclim._core.climate_variable.ClimateVariable` objects.
4. The selected :class:`~icclim._core.model.indicator.Indicator`
   computes the result.
5. Post-processing renames the result, adds time bounds when needed,
   optionally exports thresholds, and adds metadata.

In code, the main entry points are:

- ``src/icclim/main.py``:
  :func:`icclim.index`
- ``src/icclim/main.py``:
  :func:`_run_index_workflow`
- ``src/icclim/_core/model/index_config.py``:
  :class:`IndexConfig`
- ``src/icclim/_core/climate_variable.py``:
  :func:`build_climate_vars`
- ``src/icclim/_core/generic/functions.py``:
  generic reducers
- ``src/icclim/ecad/registry.py``:
  standard-index declarations
- ``src/icclim/threshold/factory.py``:
  threshold construction

Before You Add Code
===================

Start by answering these scientific questions:

1. Is the new index already expressible as an existing generic
   indicator plus an existing threshold?
2. Is it a standard named index, or a generic composition built with the
   modern generic API?
3. Does it need percentile bootstrap?
4. If it needs bootstrap, which family does it belong to?
   Count, filtered count, amount/fraction, spell, or compound?

If the index already maps cleanly to an existing generic indicator and
threshold, prefer declaring it in a registry instead of adding new
computation code.

The deprecated ``user_index`` dictionary API is not the right extension
point for new work. Treat it as a migration bridge for old code, not as
part of the design center for new climate-index development.

Common Cases
============

Case 1: add a new standard index using existing machinery
---------------------------------------------------------

This is the most common and safest case.

You usually need to update:

- ``src/icclim/ecad/registry.py`` or another standard-index registry
- tests for the new index
- user-facing docs if the index should be documented explicitly

Typical pattern:

1. Pick the existing generic indicator.
2. Define the threshold string or threshold object.
3. Set units, variables, group, definition and qualifiers.
4. Add tests proving the new declaration maps to the expected result.

Example mental model:

- ``TX90p`` is not a special computation path by itself.
- It is a named standard index that reuses:
  - one input variable;
  - one generic indicator;
  - one percentile threshold;
  - optional bootstrap behavior already implemented elsewhere.

Case 2: add a new generic indicator
-----------------------------------

You need this only when the scientific calculation is not already
covered by the existing reducer functions.

You usually need to update:

- ``src/icclim/_core/generic/functions.py`` with the new reducer
- ``src/icclim/generic/registry.py`` to register it
- tests for direct generic use and any standard indices that reuse it

Keep the new reducer focused on one mathematical role:

- count a boolean mask
- sum values selected by a mask
- compute a fraction
- compute a spell metric

Avoid putting threshold construction, input loading and metadata logic
inside the reducer.

Case 3: add or extend bootstrap support
---------------------------------------

Do not start from a named index.

Instead:

1. identify the bootstrap family;
2. route the family explicitly in
   ``src/icclim/_core/generic/bootstrap_capability.py``;
3. keep the exact tiled path as the reference bootstrap implementation;
4. only enable the optimized path after exact validation.

For percentile-bootstrap work, read the bootstrap architecture note
first. It is easy to introduce a fast path that looks right on synthetic
data but diverges on real overlap-year cases.

Legacy user_index bridge
------------------------

The deprecated ``user_index`` API still exists for backward
compatibility, but it should not guide new code structure.

For contributors, that means:

- do not add new scientific features only to the ``user_index`` bridge;
- do not shape new internal APIs around old ``user_index`` constraints;
- prefer generic-index examples and tests when documenting custom index
  support;
- keep legacy support isolated near compatibility boundaries.

Where To Look
=============

When the question is “where is this behavior decided?”, use this map.

Request Normalization
---------------------

- ``src/icclim/main.py``:
  :func:`_normalize_index_request`
- ``src/icclim/main.py``:
  :func:`_get_ecad_indices_of_group`

Index Group Resolution
----------------------

When resolving ``icclim.indices(...)`` requests, ``main.py`` now checks
the query in this order:

1. wildcard request such as ``"all"``
2. explicit standard-index names
3. source-variable aliases such as ``tasmax``
4. named index groups such as ``HEAT`` or ``SNOW``

Keeping that order visible in code helps contributors understand why one
query shape expands to a list of indices while another is rejected.

Configuration Assembly
----------------------

- ``src/icclim/main.py``:
  :func:`_build_config`
- ``src/icclim/main.py``:
  :class:`ParsedIndicatorConfig`
- ``src/icclim/main.py``:
  :class:`ParsedLegacyUserIndexConfig`
- ``src/icclim/main.py``:
  :func:`_build_index_climate_variables`
- ``src/icclim/main.py``:
  :func:`_assemble_index_config`
- ``src/icclim/main.py``:
  :func:`_build_standard_index_config`
- ``src/icclim/main.py``:
  :func:`_build_legacy_user_index_config`
- ``src/icclim/main.py``:
  :func:`_parse_legacy_user_index_config`

Input Variables
---------------

- ``src/icclim/_core/climate_variable.py``:
  :func:`build_climate_vars`
- ``src/icclim/_core/climate_variable.py``:
  :func:`build_climate_var`
- ``src/icclim/_core/input_parsing.py``:
  :func:`build_studied_data`

Thresholds
----------

- ``src/icclim/threshold/factory.py``:
  :func:`build_threshold`
- ``src/icclim/main.py``:
  :func:`_build_request_threshold`
- ``src/icclim/_core/climate_variable.py``:
  :func:`_prepare_climate_variable_threshold`
- ``src/icclim/_core/generic/threshold/percentile.py``:
  percentile-threshold behavior

Threshold Construction Workflow
-------------------------------

When a contributor asks “where does this threshold really come from?”,
follow this path:

1. ``main.py`` injects request-wide percentile options such as
   ``reference_period`` and ``interpolation``.
2. ``threshold/factory.py`` decides whether the threshold comes from:
   - one query string such as ``"> 30 degC"``;
   - two thresholds plus a logical link;
   - explicit components such as ``operator``, ``value`` and ``unit``.
   Shared percentile options such as ``reference_period`` are now
   propagated to bounded-threshold children when the child threshold is a
   percentile query string.
3. The factory turns that specification into one threshold family:
   - :class:`~icclim._core.generic.threshold.basic.BasicThreshold`
   - :class:`~icclim._core.generic.threshold.percentile.PercentileThreshold`
   - :class:`~icclim._core.generic.threshold.bounded.BoundedThreshold`
4. ``_core/climate_variable.py`` prepares the threshold with the studied
   data when the threshold needs context before it can be used.

This is a good place to keep code explicit. Threshold construction is
part of the scientific workflow, so it should read as a sequence of
decisions rather than a chain of thin translators.

Reducers
--------

- ``src/icclim/_core/generic/functions.py``:
  generic computation functions
- ``src/icclim/generic/registry.py``:
  generic indicator declarations

Result Post-Processing
----------------------

- ``src/icclim/main.py``:
  :func:`_build_result_dataset`
- ``src/icclim/frequency.py``:
  time-bound updater helpers

Bootstrap Routing
-----------------

- ``src/icclim/_core/generic/bootstrap_capability.py``:
  explicit bootstrap routing decisions
- ``src/icclim/_core/generic/bootstrap.py``:
  optimized count-family implementation

Human-Readable Code Rules
=========================

When adding or refactoring an index, prefer code that explains the
scientific workflow directly.

Good practices:

- use names that reflect the scientific role, not just the data shape;
- separate policy decisions from array mechanics;
- keep one function responsible for one phase of the workflow;
- prefer explicit small objects over parallel loose arguments;
- write one clear guard block instead of relying on a chain of asserts;
- use comments only to mark phases that are otherwise hard to see.

Avoid:

- wrappers that only rename arguments and forward them;
- deeply nested conditionals when early returns would read better;
- “translation chains” where one helper converts inputs only so another
  helper can convert them again;
- mixing bootstrap policy with flattening, reshaping and tile sizing in
  the same helper unless the function is very small.

FAIR4RS In Practice
===================

For this part of icclim, FAIR4RS means:

- Findable:
  a contributor can quickly locate where routing, thresholds and
  reducers live.
- Accessible:
  a research developer can understand the workflow without hidden tribal
  knowledge.
- Interoperable:
  bootstrap families use shared concepts such as threshold kinds and
  exceedance masks.
- Reusable:
  adding a new index should mostly mean reusing an existing indicator,
  threshold family or bootstrap family.

Testing Checklist
=================

Every new climate-index contribution should answer these tests:

1. Does the named index or generic indicator produce the expected value?
2. If it uses thresholds, are unit conversions correct?
3. If it uses bootstrap, does routing pick the expected execution path?
4. If bootstrap semantics changed, is the exact tiled path still the
   reference bootstrap implementation?
5. If the change is performance-related, was it validated on real data
   rather than only synthetic arrays?

For bootstrap work, always prefer exact field comparison against the
reference path before trusting performance results.

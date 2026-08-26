.. _dev_provenance_plan:

###############################
 Provenance Implementation Plan
###############################

This note defines a concrete provenance design for ``icclim`` outputs.
The goal is not to add more runtime logging. The goal is to write a
stable, machine-readable record of what was computed, from which inputs,
with which scientific options, and under which software context.

Why this is needed
------------------

For climate-index production runs, users often need to answer questions
after the run has finished:

- which command or API call produced this output;
- which files and variables were used;
- which thresholds, reference periods, calendars and bootstrap options
  were applied;
- which software stack and code revision produced the result;
- whether important scientific warnings were emitted during the run.

Today, part of that information is present in NetCDF metadata such as
``history`` and ``source``, but not in a form that is complete enough for
systematic reconstruction of a run.

Design goals
------------

The provenance implementation should:

- stay aligned with the scientific workflow visible in ``icclim`` code;
- record both user-facing parameters and important resolved parameters;
- produce one stable JSON sidecar per written output;
- keep a short summary in NetCDF global attributes;
- degrade gracefully when some information is unavailable;
- avoid collecting sensitive or noisy environment state by default.

FAIR4RS Alignment
-----------------

This provenance work is part of a broader FAIR4RS-oriented maintenance
direction in ``icclim``.

The practical intent is:

- make software behavior easier to inspect and reuse;
- make generated outputs easier to interpret later;
- keep scientific workflow decisions visible in code and in exported
  artifacts;
- support reproducibility without requiring hidden terminal history or
  local memory of how a run was prepared.

In that sense, provenance is not an isolated utility feature. It is one
of the mechanisms used to make ``icclim`` outputs more reusable and
auditable as research software artifacts.

What to record
--------------

Each written output should have a provenance bundle with these sections.

``run_context``
   General execution context.

   - UTC timestamp
   - hostname
   - current working directory
   - process id
   - Python executable
   - API entrypoint used, for example ``icclim.index`` or
     ``icclim.indices``

``software``
   Software stack used for the run.

   - ``icclim`` version
   - Python version
   - versions of ``xarray``, ``numpy``, ``pandas``, ``dask``,
     ``netCDF4``, ``h5netcdf``, ``cftime``, ``zarr``, ``xclim``
   - optional numba version when present

``git``
   Repository state when available.

   - repository root
   - branch
   - commit SHA
   - dirty state
   - short status summary

``inputs``
   Input datasets and variable-level context.

   - input paths or URIs
   - variable names selected from each input
   - file size and modification time when the input is local
   - optional checksum for small enough local files

``outputs``
   Output artifact description.

   - NetCDF output path
   - output creation timestamp
   - optional checksum after write
   - provenance sidecar path

``user_parameters``
   Parameters explicitly supplied by the caller.

   - index name or generic indicator
   - threshold expression
   - output frequency or seasonal selector
   - time range
   - base period or reference period
   - rolling window width
   - minimum spell length
   - output unit
   - bootstrap requested or not
   - save-threshold flag
   - sampling method
   - run-index mode
   - partial-season handling

``resolved_parameters``
   Parameters and decisions resolved internally by ``icclim``.

   - resolved indicator name
   - parsed threshold kind
   - percentile interpolation
   - day-of-year window width
   - detected source frequency
   - resolved reference period
   - calendar handling choices
   - whether a reference variable was built
   - bootstrap routing family
   - bootstrap execution route

``execution``
   Runtime context that can affect performance or reproducibility.

   - CPU count
   - dask scheduler kind when present
   - chunking description for main inputs when available
   - SLURM job identifiers when present
   - active conda environment or virtual environment when present

``warnings``
   Structured warnings collected during the run.

   - scientific warnings
   - fallback warnings
   - calendar-conversion warnings
   - chunking or performance warnings

``warnings`` should remain concise and typed. It should not become a raw
dump of every Python warning emitted by dependencies.

``icclim``-specific mandatory fields
------------------------------------

The generic provenance idea must be specialized for climate-index runs.
These fields should be treated as mandatory whenever relevant.

- threshold semantics:

  - threshold string passed by the user;
  - resolved threshold class, for example bounded threshold, percentile
    threshold, fixed threshold;
  - percentile reference period;
  - percentile interpolation method;
  - day-of-year window width.

- calendar semantics:

  - source calendar;
  - whether ``ignore_feb29th`` or ``only_leap_years`` was applied;
  - whether any calendar coercion or alignment occurred.

- bootstrap semantics:

  - whether bootstrap was requested;
  - whether bootstrap was actually active;
  - bootstrap family, for example count, value aggregate, spell;
  - route kind, for example reference bootstrap, exact tiled bootstrap,
    compiled exact bootstrap;
  - fallback reason when optimized routing was not used.

- sampling semantics:

  - output frequency;
  - seasonal mode when relevant;
  - time subset supplied by the user;
  - resolved source frequency.

Without these fields, a later reviewer cannot reliably reconstruct the
scientific meaning of the output.

Output artifacts
----------------

For a written output

.. code-block:: text

   result.nc

the provenance implementation should write

.. code-block:: text

   result.prov.json

next to it.

NetCDF global attributes should also carry a compact summary:

- ``history``
- ``source``
- ``icclim_version``
- ``command`` when available
- ``git_commit`` when available
- ``provenance_file``

The JSON sidecar is the full artifact. NetCDF attributes only point to it
and keep the most useful summary fields close to the data.

Current implementation status
-----------------------------

The first implementation phase is now in place.

Current behavior:

- ``icclim.index(..., out_file=...)`` writes a ``.prov.json`` sidecar;
- NetCDF global attributes include compact provenance pointers:

  - ``icclim_version``
  - ``provenance_file``
  - ``command``
  - ``git_commit`` when available

- the sidecar currently records:

  - run context
  - software versions
  - git context when available
  - input variable summaries
  - output paths
  - resolved runtime parameters
  - execution context such as chunk shapes and HPC job identifiers when
    present

This is intentionally a small first phase. It already makes output files
more reusable and inspectable, but it does not yet capture every
scientific decision listed below.

Why the main output path is the right integration point
-------------------------------------------------------

The current write path in :mod:`src.icclim.main` already has a clean
separation:

1. ``_build_config_from_request`` resolves the scientific request into an
   ``IndexConfig``.
2. ``_compute_climate_index`` computes the result and assembles standard
   metadata.
3. ``_write_output_file`` writes the NetCDF output.

That makes ``_run_index_workflow`` the right orchestration point for
provenance:

- before the write, enough resolved scientific context is available from
  ``IndexConfig`` and the computed dataset;
- after the write, output file metadata and checksum can be collected;
- the feature stays tied to the real workflow instead of being spread
  through lower-level helpers.

Recommended implementation shape
--------------------------------

Create a small dedicated module:

.. code-block:: text

   src/icclim/provenance.py

Suggested helpers:

- ``collect_run_context(...)``
- ``collect_software_context()``
- ``collect_git_context()``
- ``describe_input_path(path)``
- ``describe_output_path(path)``
- ``collect_execution_context(dataset)``
- ``build_provenance_bundle(...)``
- ``write_provenance_json(path, bundle)``

Keep these helpers descriptive, not framework-heavy. The scientific
workflow should remain readable from the call site in ``main.py``.

Initial integration steps
-------------------------

Phase 1 should be deliberately small.

1. Add ``src/icclim/provenance.py`` with the data-collection helpers.
2. Extend ``_run_index_workflow`` so that when ``out_file`` is provided:

   - a provenance bundle is built from the normalized request, resolved
     ``IndexConfig``, the result dataset and the output path;
   - the NetCDF dataset gets compact provenance attributes before write;
   - the sidecar JSON is written after the NetCDF file is written.

3. Keep provenance optional for in-memory-only API calls with no
   ``out_file``.
4. Do not add a new public parameter in phase 1 unless it is strictly
   needed.

Remaining extensions
--------------------

The first phase is deliberately conservative. Useful next extensions are:

- extend the same provenance path to ``icclim.indices`` output writes;
- distinguish explicit user parameters from resolved defaults more fully;
- record richer bootstrap routing decisions in the sidecar;
- record stronger threshold semantics for compound and bounded cases;
- add typed scientific warnings when a fallback route is selected.

Schema guidance
---------------

The JSON schema should stay explicit and stable. A practical shape is:

.. code-block:: json

   {
     "schema_version": 1,
     "run_context": {},
     "software": {},
     "git": {},
     "inputs": [],
     "outputs": {},
     "user_parameters": {},
     "resolved_parameters": {},
     "execution": {},
     "warnings": []
   }

Prefer explicit keys over opaque blobs. Downstream tools should not need
to scrape free-form text to reconstruct a run.

Guardrails
----------

- Hash local files only below a configurable size threshold.
- Record a filtered set of environment variables, not the full process
  environment.
- Treat missing git metadata as normal when running from an installed
  package or export.
- Do not fail the climate-index run if provenance collection is partial.
- Emit typed warnings when scientifically important defaults are used
  implicitly.

Tests to add
------------

Unit coverage should include:

- sidecar JSON written next to a NetCDF output;
- expected top-level sections present;
- git metadata present in a repository and absent gracefully otherwise;
- key package versions recorded;
- user parameters and resolved parameters both present;
- bootstrap routing recorded for a bootstrap workload;
- SLURM metadata captured when corresponding environment variables are set;
- large-file hashing fallback behaves as expected.

Scientific regression coverage should include at least one percentile
bootstrap case to verify that provenance captures:

- threshold class;
- reference period;
- calendar choices;
- bootstrap route chosen by the runtime.

What was learned from ``idownscale``
------------------------------------

The ``idownscale`` repository currently contains useful workflow
reconstruction notes and explicit entrypoints, but not a first-class
provenance module that can be reused directly here.

The main transferable lesson is architectural rather than code-level:
keep one visible orchestration entrypoint, and record enough information
there that a later engineer can reconstruct the run without hidden shell
history.

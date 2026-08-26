.. _dev_provenance_integration:

#################################
 Provenance Integration Guide
#################################

This note explains how frontend or orchestration layers should consume
``icclim`` provenance outputs.

It is written for integration points such as Climate4Impact-style
portals, workflow services, and application backends that use
``icclim`` as a computation engine.

Why this exists
---------------

``icclim`` now writes provenance as part of the output artifact when
``out_file`` is used:

- the NetCDF file contains compact provenance pointers in global
  attributes;
- a sidecar JSON file stores the fuller structured record.

Frontend and service layers should use that provenance directly instead
of reconstructing run metadata from logs after the fact.

Relation to SWIRRL-style provenance
-----------------------------------

SWIRRL already treats provenance as a first-class service concern rather
than a side effect of logging.

The public SWIRRL material currently shows that:

- provenance is captured for API methods affecting a session;
- provenance templates are expanded by dedicated provenance services;
- provenance is stored through dedicated components such as a Neo4j-based
  graph store;
- SWIRRL exposes provenance-oriented query and export paths, including
  JSON-LD or RDF-oriented flows;
- reproducibility and recovery actions are driven from that provenance
  layer rather than from ad hoc notebook notes or operator memory.

For ``icclim``, that means the right compatibility goal is not to
reimplement SWIRRL's provenance stack inside ``icclim``. The right goal
is to emit output provenance in a form that SWIRRL or similar systems can
ingest, preserve, link and display cleanly.

Produced artifacts
------------------

For an output such as:

.. code-block:: text

   result.nc

``icclim`` writes:

.. code-block:: text

   result.prov.json

The NetCDF global attributes also include:

- ``history``
- ``source``
- ``icclim_version``
- ``provenance_file``
- ``command``
- ``git_commit`` when available

Recommended integration pattern
-------------------------------

For a frontend or backend service, the safest integration pattern is:

1. treat the NetCDF file as the scientific result;
2. treat the ``.prov.json`` file as its machine-readable run record;
3. keep both files together in storage and download flows;
4. surface a compact human summary in the user interface;
5. preserve the raw JSON for audit, support and reproducibility tasks.

Do not rely on NetCDF global attributes alone when the sidecar is
available. The attributes are a pointer layer, not the full record.

What frontends should display
-----------------------------

At minimum, a frontend should be able to show:

- ``icclim`` version
- command or API entrypoint
- output frequency
- index name
- threshold summary
- reference period
- calendar
- bootstrap routing when relevant
- git commit when available
- output generation timestamp

This is the practical minimum for support and scientific traceability.

What backend services should persist
------------------------------------

Backend systems should persist, or at least archive together:

- the NetCDF output;
- the ``.prov.json`` sidecar;
- the job or request identifier used by the service layer;
- any higher-level workflow metadata not owned by ``icclim`` itself.

Examples of service-layer metadata that remain outside ``icclim``:

- authenticated user identifier;
- project or workspace identifier;
- portal-specific form identifiers;
- queue ticket or external workflow run id;
- access-control metadata.

Those service-level fields should not replace the ``icclim`` provenance
record. They should complement it.

Recommended mapping for portal backends
---------------------------------------

For systems such as Climate4Impact or Swirrl-style service layers, a
useful separation is:

``icclim`` provenance
   Scientific and runtime facts produced by the computation backend.

service provenance
   Portal, workflow and user-session facts produced by the caller.

A robust storage shape is:

.. code-block:: text

   result.nc
   result.prov.json
   result.service.json

where:

- ``result.prov.json`` comes from ``icclim`` unchanged;
- ``result.service.json`` is owned by the integrating application.

For a SWIRRL-style deployment, an additional provenance-graph layer may
exist beyond those files. In that case, the recommended model is:

- keep ``result.prov.json`` as the original file-level provenance
  artifact;
- store portal or workflow provenance in the SWIRRL provenance graph;
- add graph links that point to the output artifact and its sidecar,
  instead of flattening the ``icclim`` sidecar into unrelated session
  fields.

That separation avoids mixing portal concerns into scientific metadata,
while still keeping the full workflow reconstructable.

Using provenance in user support
--------------------------------

When a user reports a discrepancy, the frontend or backend support flow
should collect:

- the NetCDF output;
- the ``.prov.json`` sidecar;
- the original user-facing request parameters if the portal stores them;
- any external workflow id from the service layer.

In most cases, the provenance sidecar should answer:

- which index ran;
- with which threshold or reference-period setup;
- whether bootstrap was involved;
- under which software and git revision the result was produced.

This reduces the need to reconstruct the run from partial logs.

Using provenance in SWIRRL-style traceability views
---------------------------------------------------

SWIRRL-oriented interfaces tend to expose provenance as an actionable
traceability layer, not merely as hidden metadata.

For that kind of interface, ``icclim`` provenance is most useful when it
is surfaced as:

- a result-level provenance panel for a produced artifact;
- a link from the workspace or workflow activity to the output file;
- a compact scientific summary derived from ``user_parameters`` and
  ``resolved_parameters``;
- a downloadable raw sidecar for deeper inspection.

In other words, the sidecar should support both:

- machine ingestion into a broader provenance system;
- direct inspection by users and support engineers.

Using provenance for result catalogs
------------------------------------

Catalog or search layers may index selected provenance fields such as:

- index name
- output frequency
- temporal coverage
- reference period
- threshold kind
- calendar
- ``icclim`` version
- git commit

However, they should index copies of those fields rather than rewriting
the original provenance file.

Handling missing fields
-----------------------

Integrators should expect some provenance fields to be absent.

Examples:

- ``git_commit`` may be unavailable in installed-package contexts;
- HPC job identifiers may be absent outside batch environments;
- command reconstruction may be less informative when ``icclim`` is
  invoked through a Python service layer rather than a CLI wrapper.

Missing fields should not be treated as provenance failure. The
integration should degrade gracefully and surface what is available.

Adapter guidance for graph-based provenance systems
---------------------------------------------------

If the integrating platform stores provenance in a graph-oriented system
such as SWIRRL's provenance services, use an adapter layer rather than
changing ``icclim`` output files.

Recommended adapter behavior:

1. ingest ``result.prov.json`` as a file-level provenance object;
2. create links from the portal session, workflow or activity node to
   the produced NetCDF artifact;
3. attach selected fields for indexing or UI display;
4. preserve the original sidecar unchanged for export and audit.

This avoids schema drift and keeps ``icclim`` provenance usable outside
the SWIRRL ecosystem as well.

Explicit graph-mapping examples
-------------------------------

The goal of the adapter is to map ``icclim`` file-level provenance into a
broader provenance graph without rewriting the original sidecar.

Example 1: minimal result graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given:

.. code-block:: text

   result.nc
   result.prov.json

with sidecar fields such as:

.. code-block:: json

   {
     "run_context": {
       "utc_timestamp": "2026-08-26T09:15:00+00:00",
       "entrypoint": "icclim.index"
     },
     "software": {
       "icclim": "7.1.10"
     },
     "git": {
       "commit": "abc123"
     },
     "user_parameters": {
       "index_name": "TX90p",
       "slice_mode": "year"
     },
     "resolved_parameters": {
       "bootstrap": {
         "family": "day_of_year_percentile_count",
         "execution_kind": "optimized_bootstrap"
       }
     },
     "outputs": {
       "netcdf_path": "/data/result.nc",
       "provenance_path": "/data/result.prov.json"
     }
   }

one reasonable graph projection is:

- ``Activity`` node:
  ``icclim.index`` run at ``2026-08-26T09:15:00+00:00``
- ``Entity`` node:
  ``/data/result.nc``
- ``Entity`` node:
  ``/data/result.prov.json``
- ``SoftwareAgent`` node:
  ``icclim 7.1.10``
- ``Version`` or ``Revision`` node:
  git commit ``abc123``

with edges such as:

- activity ``usedSoftware`` software-agent
- activity ``usedRevision`` revision
- activity ``generated`` result NetCDF
- activity ``generatedMetadata`` provenance sidecar
- sidecar ``describes`` result NetCDF

Example 2: session-aware SWIRRL-style mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the platform already models workspace or session activity, keep that
layer separate.

Example graph:

- ``Session`` node:
  portal session or workspace action
- ``WorkflowRun`` node:
  backend task launched by the session
- ``Activity`` node:
  ``icclim.index`` computation
- ``Entity`` node:
  output NetCDF
- ``Entity`` node:
  output provenance JSON

Recommended links:

- session ``triggered`` workflow-run
- workflow-run ``invoked`` icclim activity
- icclim activity ``generated`` output NetCDF
- icclim activity ``generatedMetadata`` provenance JSON
- provenance JSON ``describes`` output NetCDF

This keeps:

- portal lifecycle provenance in the graph layer;
- scientific output provenance in the sidecar;
- a clean bridge between the two.

Example 3: selected field projection for UI queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do not push every JSON field into first-class graph properties.

Good initial projection:

- activity properties:

  - ``entrypoint``
  - ``timestamp``
  - ``icclim_version``
  - ``git_commit``

- result entity properties:

  - ``path``
  - ``index_name``
  - ``slice_mode``
  - ``reference_period``
  - ``calendar``
  - ``bootstrap_family``
  - ``bootstrap_execution_kind``

- provenance entity properties:

  - ``path``
  - ``schema_version``

Keep the rest in the raw sidecar.

That pattern usually gives enough graph-level searchability without
creating a second uncontrolled provenance schema in the platform.

Example pseudo-adapter
~~~~~~~~~~~~~~~~~~~~~~

The adapter logic can stay simple:

.. code-block:: python

   payload = load_json("result.prov.json")

   activity = create_activity(
       entrypoint=payload["run_context"]["entrypoint"],
       timestamp=payload["run_context"]["utc_timestamp"],
       icclim_version=payload["software"]["icclim"],
       git_commit=payload["git"]["commit"],
   )

   result_entity = create_entity(
       path=payload["outputs"]["netcdf_path"],
       index_name=payload["user_parameters"].get("index_name"),
       slice_mode=payload["user_parameters"].get("slice_mode"),
       bootstrap_kind=payload["resolved_parameters"]
       .get("bootstrap", {})
       .get("execution_kind"),
   )

   provenance_entity = create_entity(
       path=payload["outputs"]["provenance_path"],
       schema_version=payload["schema_version"],
   )

   link(activity, "generated", result_entity)
   link(activity, "generatedMetadata", provenance_entity)
   link(provenance_entity, "describes", result_entity)

This is intentionally file-oriented and adapter-driven.

What not to do
--------------

Avoid these patterns:

- flatten the full sidecar into one graph node with dozens of unstable
  properties;
- drop the raw ``result.prov.json`` after ingesting it into the graph;
- rewrite ``icclim`` provenance keys to portal-specific names inside the
  original sidecar;
- merge portal-session provenance and scientific output provenance into
  one undifferentiated JSON record.

Those patterns make later interoperability and support harder.

Field priorities for SWIRRL or Climate4Impact integration
---------------------------------------------------------

If only a subset of ``icclim`` provenance fields is surfaced at first,
prioritize:

- ``run_context.utc_timestamp``
- ``software.icclim``
- ``git.commit``
- ``user_parameters.index_name``
- ``user_parameters.slice_mode``
- ``user_parameters.threshold``
- ``resolved_parameters.reference_period``
- ``resolved_parameters.bootstrap``
- ``inputs[].calendar``
- ``outputs.netcdf_path``

These are the fields most likely to matter in support, scientific
validation and reproducibility views.

Why the sidecar should remain file-oriented
-------------------------------------------

SWIRRL's provenance model is broader than one output file. It spans
sessions, services, workflows, updates and recovery operations.

``icclim`` should remain narrower in scope:

- it describes the scientific output it produced;
- it does not attempt to model the whole workspace lifecycle;
- it emits provenance that larger systems can compose into their own
  broader traceability graph.

That separation keeps ``icclim`` reusable both inside and outside a
SWIRRL deployment.

Frontend guidance for FAIR4RS-oriented reuse
--------------------------------------------

To support reuse and reproducibility in practice:

- keep provenance files downloadable with the scientific result;
- show stable field labels in the UI rather than rewriting meanings
  between releases;
- avoid stripping ``icclim`` provenance fields when copying or
  repackaging outputs;
- prefer linking user-visible summaries back to the raw sidecar content;
- preserve original timestamps, versions and routing information.

This helps downstream users treat the produced files as reusable
research-software artifacts, not just opaque downloads.

Current schema areas most useful to integrators
-----------------------------------------------

The most useful current top-level sections are:

- ``run_context``
- ``software``
- ``git``
- ``inputs``
- ``outputs``
- ``user_parameters``
- ``resolved_parameters``
- ``execution``
- ``warnings``

Frontend code should treat the schema as explicit and versioned through
``schema_version``.

Practical next step for integrators
-----------------------------------

If you are wiring ``icclim`` into a frontend or service backend now,
implement this first:

1. store ``result.nc`` and ``result.prov.json`` together;
2. display a short provenance summary in the UI;
3. keep the raw JSON downloadable;
4. add service-level metadata in a separate companion record if needed.

That already gives a clean foundation for support, audit and scientific
traceability.

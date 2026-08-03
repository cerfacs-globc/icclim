.. _dev_code_audit_since_abel:

#####################################
Code audit since Abel's last commits
#####################################

This note records a maintainability audit of the codebase after the
bootstrap work merged between July 29 and August 3, 2026.

The audit uses Abel Aoun's last commit period as a historical boundary,
but it is not an author-based judgement. The goal is to assess the
current code against the rules maintainers agreed on:

- scientific workflow must stay visible in code;
- naming must prefer climate and research-software semantics over
  imported software jargon;
- readable and reusable code matters as much as raw performance;
- abstractions must be justified by clarity, correctness or validated
  performance;
- the code should remain aligned with FAIR for Research Software
  (FAIR4RS).

This note is meant to guide future work so maintainers do not need to
repeat the same broad audit after every bootstrap extension.

Scope and method
================

The audit considers:

- the code and documentation state after the merge of
  ``feature/bootstrap-chunk-performance`` on Monday, August 3, 2026;
- workflow and readability concerns raised during the recent bootstrap
  work;
- both older architect-led patterns and newer AI-era changes.

The audit does **not** assume:

- older code is automatically better;
- newer code is automatically worse;
- technically elegant structure is enough if the scientific workflow
  becomes harder to follow.

Instead, the central questions are:

1. Can a scientific maintainer understand how an index is computed?
2. Are abstractions helping reuse and clarity, or hiding the workflow?
3. Is the code proportionate to the scientific problem?
4. Is the result more FAIR4RS-aligned than before?

High-level verdict
==================

The recent direction is good.

Compared with the state before the July 29 to August 3, 2026 bootstrap
series, the code is now:

- more explicit about bootstrap routing and support boundaries;
- better documented for maintainers;
- better validated on real data and chunk-profile variation;
- better aligned with climate-domain wording;
- less dependent on hidden workflow spread across many small wrappers.

However, some structural risks remain:

- a few core files are still too large;
- some policy and mechanics are still mixed together;
- low-level bootstrap kernels are necessarily dense and must stay boxed
  in by readable surrounding code;
- some older architect-style indirection still makes scientific
  workflow harder to discover than it should be.

Areas that are in good shape
============================

Bootstrap capability routing
----------------------------

``src/icclim/_core/generic/bootstrap_capability.py`` is a strong part of
the current design.

Why it works:

- routing is explicit;
- reason codes make behavior observable;
- support is classified by mathematical family rather than by index
  short name;
- the code is readable enough for maintainers to extend carefully.

Bootstrap primitives
--------------------

``src/icclim/_core/generic/bootstrap_primitives.py`` is a good step
toward reusable threshold-engine logic.

Why it works:

- responsibilities are reasonably stable;
- the scientific phases are visible;
- future optimized reducers have a clear place to reuse shared work.

Developer documentation
-----------------------

The recent developer notes are a meaningful improvement:

- ``bootstrap_architecture.rst``
- ``percentile_bootstrap.rst``
- ``add_climate_index.rst``

Why this matters:

- maintainers can now find the intended support boundary;
- workflow and implementation intent are less dependent on tribal
  knowledge;
- this is directly helpful for FAIR4RS reuse and onboarding.

Validation tooling
------------------

The real-data validation and profiling tools are now useful
infrastructure rather than ad hoc scripts.

Why this matters:

- exact comparisons against a trusted baseline are now standard;
- performance diagnostics are reproducible;
- chunk-profile stability can be verified explicitly.

Areas that still need care
==========================

``bootstrap.py``
----------------

``src/icclim/_core/generic/bootstrap.py`` is still a major hotspot.

Current assessment:

- much better than before;
- still too large;
- still dense in the compiled-kernel section;
- acceptable only because the surrounding routing, docs and tests are
  now much stronger.

Rule going forward:

- do not let this file grow casually;
- any substantial new feature should first ask whether one more
  meaningful extraction is needed.

``functions.py``
----------------

``src/icclim/_core/generic/functions.py`` remains too large and still
mixes several reducer families.

Current assessment:

- readable in local sections;
- hard to navigate globally;
- still carries too much responsibility in one file.

Rule going forward:

- new reducer-family work should prefer extracting stable helper layers
  instead of adding yet more branching into this file.

``main.py``
-----------

``src/icclim/main.py`` is more explicit than before, but it is still
oversized for a scientific entrypoint.

Current assessment:

- much improved workflow clarity;
- still a large surface for one module;
- still more orchestration than ideal in one place.

Rule going forward:

- avoid letting bootstrap-specific policy leak back into ``main.py``;
- keep it as a readable orchestration layer, not a second routing hub.

``input_parsing.py`` and ``threshold/factory.py``
-------------------------------------------------

These modules improved, but still mix policy and mechanics more than is
ideal for research-software readability.

Rule going forward:

- when modifying them, prefer explicit phase helpers over expanding
  existing mixed-purpose builders.

What this audit says about older architect-led patterns
=======================================================

Some older design choices were technically solid, but not always ideal
for scientific workflow clarity or FAIR4RS.

Examples of patterns to avoid repeating:

- factory/registry chains that hide the climate-index workflow;
- thin translation helpers that only rename and forward arguments;
- elegant dispatch that makes onboarding harder for research
  contributors;
- abstractions that compress several scientific steps into one generic
  builder.

This does **not** mean those choices were wrong in context. It means the
current standard should be:

- scientific workflow visibility first;
- architecture second;
- micro-elegance only when it does not hide meaning.

Working rules for the next branches
===================================

Use these as hard constraints for future bootstrap work.

Readability rules
-----------------

- Prefer domain language over generic software jargon.
- Keep substitute-year, reference-period and threshold semantics
  explicit.
- Avoid adding wrappers that only rename arguments and forward calls.
- Prefer one readable control flow over several abstract layers.
- Keep optimized kernels boxed behind readable orchestration.

Structure rules
---------------

- One file should not become the default home for every new bootstrap
  feature.
- Extract by stable responsibility, not by convenience.
- Keep routing in dedicated routing code.
- Keep low-level numeric mechanics separate from scientific policy.
- Keep validation utilities separate from production routing logic.

Scientific rules
----------------

- Do not add a new optimized route without trusted-baseline real-data
  validation.
- Do not add a new family unless it corresponds to a real scientific
  need.
- Do not introduce special cases that make the support matrix harder to
  understand than the underlying climate-index family.
- Keep the exact tiled bootstrap implementation as the reference path
  until the optimized path is field-identical.

FAIR4RS rules
-------------

- Make the code easier to find by keeping responsibilities and names
  obvious.
- Make the code easier to access by keeping the workflow visible in
  source and docs.
- Make the code easier to interoperate with by keeping assumptions
  explicit.
- Make the code easier to reuse by preferring stable primitives over
  hidden special cases.

Over-engineering checklist
==========================

Run this checklist before merging any substantial bootstrap change.

Technical over-engineering
--------------------------

Ask:

- Did this change add a new abstraction that mainly forwards calls?
- Did it add a new helper whose responsibility is not stable?
- Did it make the control flow harder to follow than before?
- Did it improve performance only marginally while making code harder to
  understand?

If the answer is yes, simplify before merging.

Scientific over-engineering
---------------------------

Ask:

- Is this a real bootstrap family, or just a one-off special case?
- Did we add support before proving a real scientific need?
- Did we make the support matrix harder to understand than the climate
  concept itself?
- Did we increase validation burden without proportionate scientific
  value?

If the answer is yes, simplify or postpone.

Implementation plan
===================

The next implementation steps should preserve the gains from the recent
bootstrap work while reducing the risk of architectural drift.

1. Keep using small, reviewable bootstrap branches.
   Each branch should add one scientifically meaningful support
   extension or one clearly scoped maintainability improvement.

2. Treat ``bootstrap.py`` and ``functions.py`` as controlled-growth
   files.
   Before adding more code there, check whether a stable extraction is
   justified.

3. Require a short post-change audit for every substantial bootstrap
   branch.
   The branch close-out should answer:

   - what became clearer?
   - what became more complex?
   - is the complexity justified?

4. Keep docs aligned with support boundaries.
   If a new optimized family or fallback rule is added, update the
   maintainer notes in the same branch.

5. Keep trusted-baseline Kraken validation as the release gate for
   meaningful bootstrap changes.
   Unit tests are necessary, but not sufficient, for this part of the
   codebase.

6. Prefer removing obsolete complexity over keeping all historical
   layers alive.
   When a newer design makes an older bootstrap path or explanation
   stale, clean it up instead of letting both remain in parallel.

Definition of success
=====================

Future bootstrap work is succeeding if it does all of the following:

- expands scientifically useful support;
- stays exact against the reference bootstrap implementation;
- keeps performance gains only where they are validated;
- leaves the workflow easier to understand, not harder;
- improves reuse without building a hidden framework;
- reduces the need for broad corrective audits later.

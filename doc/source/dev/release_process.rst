#################
 Release process
#################

*******************
 Automatic Release
*******************

As of icclim 6.6.0, a GitHub Action
(`.github/workflows/publish-to-pipy.yml`) publishes icclim to PyPI
whenever a `GitHub release <https://github.com/cerfacs-globc/icclim/releases>`_
is published. This action requires a manual approval via a dedicated ``release``
GitHub environment.

The ``regro-cf-autotick-bot`` then watches PyPI and automatically creates a PR
on `icclim-feedstock <https://github.com/conda-forge/icclim-feedstock>`_
to update the version and SHA256. Under normal conditions, the bot PR should
pass CI and only require a review + merge.

The full process is:

#. Merge everything to the icclim ``master`` branch.
#. Bump ``__version__`` in ``src/icclim/__init__.py`` (flit reads the version
   from it) before creating the release.
#. Create a `GitHub release <https://github.com/cerfacs-globc/icclim/releases>`_
   with a version tag (e.g. ``v7.0.5``).
#. Wait for the GitHub Action to build the package and approve it to publish to PyPI.
#. Wait for the bot to create a PR on ``icclim-feedstock`` (usually within a few hours).
#. Review the bot PR. If dependencies have changed, manually update ``requirements/run``
   in ``recipe/meta.yaml`` (the bot only bumps version and sha256).
#. Merge the bot PR.

.. note::

   If the bot PR queue on the feedstock grows beyond 3 open PRs, the bot will
   **stop creating new PRs**. Close stale bot PRs to unblock it.

.. warning::

   If the Python version support range changes (e.g., dropping Python 3.9),
   you must trigger a **rerender** of the feedstock to regenerate CI scripts.
   To do this, comment ``@conda-forge-admin, rerender`` on the feedstock PR
   **from a fork** (not from a branch within the feedstock itself).

*************************
 Verification Checklist
*************************

The 7.3.1 release fixed value errors that had been released for years (for example
percentages 100 times too small for non-monthly periods, wrong leap-day
denominators and a wet-day floor applied with the wrong comparison). The existing
tests only checked that indices ran, not that their numbers were right. This
checklist exists so that a change cannot reach a release in the same way.

For every pull request
======================

#. **A bug fix has a regression test that fails before the fix and passes after it.**
   Show the failure on the base branch in the PR description. Keep the test and the
   fix in the same commit so that every commit on ``master`` passes the test suite
   (bisectable history).
#. **Compare values with an independent calculation.** A new or changed index, reducer
   or unit conversion needs a test whose expected values come from plain numpy or
   pandas written from the index definition (ECA&D ATBD), not from icclim or xclim
   code. Cover at least: all affected output frequencies (month, year, seasons,
   seasons crossing the year end), NaN periods, and the calendars involved
   (standard, noleap, 360_day, all_leap).
#. **Eager and chunked results must be equal.** Run the same call on in-memory data and
   on Dask data with several time chunkings (including chunks shorter than any
   rolling window) and assert the results are identical.
#. **Golden or snapshot tests never pin behaviour that is known to be wrong.** If one
   must record a defect, mark it ``xfail(strict=True)`` with the issue number so it
   fails loudly once the defect is fixed.
#. **Performance changes include before/after numbers** from
   ``tools/benchmark_non_bootstrap.py`` (wall time and peak RSS), and the audit and
   oracle tests must pass unchanged on the new code: a refactor must not change values.
#. **State behaviour changes explicitly in the release notes**, with the affected
   versions. Verify the range by reading (or running) the older releases, and say
   which was done. Do not claim a range that was not checked.
#. **List every behaviour change in the pull request description.** A pull request
   can change more than its title says: results, output shape or dimension order,
   defaults, error behaviour, including side effects of a refactor. The description
   must list every such change, and reviewers read the full diff of ``src/``, not only
   the description. A pull request labelled as a test or documentation change must
   not change ``src/``; if it has to, say so in the title and open an issue. *Example:*
   a pull request titled as tests changed the generic ``percentile`` function so that
   it honoured all requested percentiles, which also changed the output shape for a
   single percentile. It was found only by the pre-release audit.
#. **Decide ambiguous definitions in writing.** When the ATBD (or ETCCDI) definition can
   be read in more than one way, do not choose silently. Put the options and the
   reading you propose in the pull request or issue and in the docstring of the test,
   and let a maintainer decide. *Example:* whether a run of consecutive days that
   crosses 31 December is counted whole in the period where it starts, as icclim does
   by default for CDD and CWD, or is cut at the period boundary
   (``split_runs_at_period_boundary``, issues #543 and #580).

Before every release
====================

#. Run the full test suite on the **oldest supported** versions of the key
   dependencies (xarray, dask, xclim, numpy, pandas) and on the **latest** ones. A bug
   can appear on only one of them (an earlier rolling-window bug reproduced only
   with xarray 2026.2). The continuous integration currently runs a single
   Python/dependency set; adding a minimum-versions job is recommended.
#. Run the three families of value tests below. All must pass, with no unexplained
   new warnings.

   - **Independent value tests ("oracles").** Each test builds a small input where
     the correct answer can be worked out by hand or with a few lines of plain
     numpy/pandas, written from the index definition and never from icclim or xclim
     code, then compares icclim's result with it. *Example:* for SU (summer days,
     daily maximum temperature above 25 °C), build three years of daily values,
     count the days above 25 °C per year with ``(tx > 25).groupby("time.year").sum()``,
     and require icclim to return exactly those numbers. A test like this would have
     caught the annual percentage returning 1 instead of 100.
   - **Eager versus chunked option matrix.** icclim usually runs on Dask arrays, where
     a large file is cut into chunks along time and space and processed piece by
     piece. The result must not depend on how the data are cut. *Example:* RX5day
     (maximum 5-day precipitation) on a daily series loaded in memory must equal the
     result when the same series is cut into 1-day, 7-day or 1-year time chunks,
     including when a 5-day window straddles a chunk boundary. The matrix repeats
     this across output frequencies (month, year, seasons), thresholds, NaN patterns
     and calendars (standard, noleap, 360_day).
   - **Golden tests.** These store the output of a trusted earlier run (for example
     the monthly TG values of a small reference dataset) and fail if a later change
     moves any number. They protect against accidental changes, for instance during
     a performance refactor, but they are only as good as the stored reference: a
     golden test must never freeze a number known to be wrong.
#. **Compare with the previous release, as a change detector only.** Run the same calls
   on the previous release and on the candidate (all indices, with and without
   bootstrap, in memory and chunked, several calendars, base periods that overlap the
   study period or not) and list every difference. Each difference must be explained
   by an issue or a documented change; an unexplained difference blocks the release.
   The previous release is **not a reference for correctness**: it can be wrong too
   (percentages were 100 times too small in every version since at least 6.2.0). The
   reference for what is correct is the definition (ECA&D ATBD, ETCCDI) together with
   the independent value tests above and, where possible, a second independent
   implementation or published index values for the same input (for example ECA&D
   published station indices, computed with the same completeness rules, or another
   package such as the R package ``climdex.pcic`` for the ETCCDI indices).
#. For releases that touch performance, chunking, percentiles or bootstrap, run the
   real-data validation (``tools/run_real_data_validation.py``, Kraken scripts in
   ``tools/``) and compare against the previous release.
#. Check the release notes mention every behaviour change and bug fix with its issue
   number, and state plainly when earlier results were wrong.
#. Bump ``__version__`` and set the release date in the notes.
#. After publishing, verify the install in a **fresh virtual environment with a
   supported Python (>= 3.10)**: ``pip install icclim==X.Y.Z`` and print
   ``icclim.__version__``.

Periodically
============

#. **Mutation testing.** A tool (``mutmut``) makes small deliberate changes to the
   code, one at a time, such as turning ``>`` into ``>=``, replacing ``100`` by ``10``
   or removing a line, and reruns the tests. A good test suite fails for each change
   (the change is "killed"). If the tests still pass (the change "survives"), no test
   checks the value that line produces. *Example:* the wet-day floor of R95pTOT was
   applied with ``>`` instead of ``>=``. A surviving ``>`` to ``>=`` mutation in that
   code would have shown, before any user did, that no test distinguished a value
   exactly equal to 1 mm/day. Run it on ``generic/functions.py``, ``input_parsing.py``
   and ``frequency.py`` with a generous time limit per mutant (at least 120 s; with
   15 s most mutants simply time out and tell us nothing), and treat every
   survivor as a missing test.
#. **ECAD value coverage.** Keep an independent value test (see "oracles" above) for
   every one of the 64 ECA&D indices, and extend it whenever an index is added. The
   target is 64/64. Before the 7.3.1 audit it was 0/64: the existing tests only
   checked that, for example, TX90p or GSL ran and returned a result, not that the
   numbers matched the ECA&D definition.

Merging
=======

#. **Squash-merge each pull request.** The pull request becomes a single commit on
   ``master`` that contains both the change and its tests, so every commit on
   ``master`` passes the test suite. This keeps ``git bisect`` and ``git blame`` useful
   when looking for the origin of a wrong value.
#. **Wait for the required checks** (tests, and the Read the Docs build) to be green.
#. **Rebase dependent pull requests** onto the updated ``master`` after each merge, so
   that a pull request stacked on another does not drag the already merged commits
   along (``git rebase --onto origin/master <old head of the merged PR> <branch>``).
#. **Give every issue its own closing keyword.** ``Fixes #522, fixes #523`` closes both
   issues; ``Fixes #522 and #523`` closes only the first. (This is what happened with
   #523, which stayed open after its fix was merged.)

***********************
 Conda-forge Checklist
***********************

Use this checklist when the bot PR requires manual intervention:

#. Make sure no stale bot PRs are open (close them with a "Superseded by X.Y.Z" comment).
#. Fork `icclim-feedstock <https://github.com/conda-forge/icclim-feedstock>`_ to your account
   (or sync your existing fork: *Sync fork → Update branch*).
#. Edit ``recipe/meta.yaml`` in your fork:

   - Update ``version``.
   - Update ``sha256`` (get it from `PyPI <https://pypi.org/project/icclim/#files>`_ → *view hashes*).
   - Add/remove dependencies in ``requirements/run`` to match ``pyproject.toml``.
   - Use ``python {{ python_min }}`` in ``host`` and ``test.requires``.
   - Use ``https://pypi.org/...`` (not ``pypi.io``) in the source URL.

#. Open a Pull Request from your fork to ``conda-forge/icclim-feedstock:main``.
#. If Python support bounds changed, comment: ``@conda-forge-admin, rerender``.
#. Wait for CI to pass, then merge.

*************************************
 Enabling Auto-merge on Bot PRs
*************************************

To make routine patch releases fully automatic (no manual merge needed),
add the following to ``conda-forge.yml`` in the feedstock:

.. code:: yaml

   bot:
     automerge: true

With this setting, the bot will merge its own version-bump PRs automatically
once the CI passes.

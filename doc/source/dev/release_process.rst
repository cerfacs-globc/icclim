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

Before every release
====================

#. Run the full test suite on the **oldest supported** versions of the key
   dependencies (xarray, dask, xclim, numpy, pandas) and on the **latest** ones. A bug
   can appear on only one of them (an earlier rolling-window bug reproduced only
   with xarray 2026.2). The continuous integration currently runs a single
   Python/dependency set; adding a minimum-versions job is recommended.
#. Run the independent value tests (generic indicators and ECAD indices), the
   eager-versus-chunked option matrix, and the golden tests. All must pass, with no
   unexplained new warnings.
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

#. Rerun mutation testing on ``generic/functions.py``, ``input_parsing.py`` and
   ``frequency.py`` with a generous timeout (at least 120 s per mutant) and look at
   surviving mutants: they mark code whose values no test checks.
#. Keep independent value coverage of the ECAD indices at 64/64 and extend it when an
   index is added.

Merging
=======

Squash-merge each pull request so that every commit on ``master`` is one change with
its test, after the required checks (including the Read the Docs build) are green.
Rebase dependent pull requests onto the new ``master`` before merging them. Link the
issue with its own closing keyword (``Fixes #1, fixes #2``), because one keyword closes
only the first issue.

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

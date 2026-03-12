#################
 Release process
#################

*******************
 Automatic Release
*******************

As of icclim 6.6.0, a GitHub Action
(`.github/workflows/publish-to-pypi.yml`) publishes icclim to PyPI
whenever a `GitHub release <https://github.com/cerfacs-globc/icclim/releases>`_
is published. This action requires a manual approval via a dedicated ``release``
GitHub environment.

The ``regro-cf-autotick-bot`` then watches PyPI and automatically creates a PR
on `icclim-feedstock <https://github.com/conda-forge/icclim-feedstock>`_
to update the version and SHA256. Under normal conditions, the bot PR should
pass CI and only require a review + merge.

The full process is:

#. Merge everything to the icclim ``master`` branch.
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

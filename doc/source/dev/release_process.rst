#################
 Release process
#################

*******************
 Automatic Release
*******************

As of icclim 6.6.0, a github action
(`.github/workflows/publish-to-pypi.yml`) publishes icclim to pypi
whenever a (github
release)[https://github.com/cerfacs-globc/icclim/releases] is published.
This github action requires a manual approuval. A dedicated `release`
github environment has been created to manage the permission for this
github action.

Then an automatic process on conda-forge pick the new release from pypi,
create a pull request on icclim-feedstock and wait for our review and
approval to publish the release to conda-forge.

Hence, the process is as follow:

#. Merge everything on icclim master branch
#. Create a (github
   release)[https://github.com/cerfacs-globc/icclim/releases]
#. Wait for the github action to build the package
#. Approve the github action to release to pypi
#. Wait for conda-forge to create a PR on icclim-feedstock
#. Edit and approve PR on icclim-feedstock

***************************
 Manual release (outdated)
***************************

The Automatic approach

#. Make sure all tests pass.

#. Create and checkout a release branch.

#. Update version number of icclim in ``src/icclim/__init__.py``.

#. Update release notes in ``doc/source/references/release_notes.rst``.

#. Merge release branch to master with a PR.

#. Clean dist directory content.

#. Create wheel file on master and source archive.

      .. code:: sh

         python3 -m build

#. Upload to pypi.

      .. code:: sh

         flit publish

#. Update conda-forge feedstock at
   https://github.com/conda-forge/icclim-feedstock

      The recipe `recipe/meta.yml` must be updated:
         -  Fork the repository in with your own account.

         -  Update icclim version number at the top.

         -  Update `source.sha256` value with the tar.gz sha256.
               You can get the tar.gz hash from `pypi
               <https://pypi.org/project/icclim/#files>`_ using `view
               hashes` link.

         -  Add any new dependency in `requirements`.

         -  Create a pull request with these changes, targeting the main
            fork on main branch

         -  Wait for the CI feedback and correct things if needed.

         -  Merge the pull request

#. Update `icclim github release <https://github.com/cerfacs-globc/icclim/releases>`_
      -  You should add a tag similar to the new version number.
      -  You should enter a short description of the changes, with a
         highlight on breaking changes.
      -  There is no need to fill the assets with anything as the
         release assets are already on conda-forge and pypi.

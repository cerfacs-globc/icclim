Release process
===============

#. Make sure all tests pass.
#. Create and checkout a release branch.
#. Update version number of ICCLIM_VERSION in ``icclim/models/constants.py`` and in ``setup.py``.
#. Update release notes in ``doc/source/references/release_notes.rst``.
#. Merge release branch to master with a PR.
#. Clean dist directory content.
#. Create wheel file on master.

    .. code-block:: sh

        python3 -m setup bdist_wheel

#. Create source archive.

    .. code-block:: sh

        python3 -m setup sdist

#. Try to upload on testpypi first. ``twine`` must be installed in your env beforehand.

    .. code-block:: sh

        python3 -m twine upload --repository testpypi dist/*

#. Try to install testpypi version on a clean virtual environment.

    .. code-block:: sh

        python3 -m pip install --index-url https://test.pypi.org/simple/ icclim

    .. note::

        It may fail due to missing dependencies in test.pypi.
        In that case, create the environment from icclim environment.yml file to
        pull all needed dependencies from conda.

#. Upload to pypi for real.

    .. code-block:: sh

        python3 -m twine upload dist/*

#. Update conda-forge feedstock at https://github.com/conda-forge/icclim-feedstock

    The recipe `recipe/meta.yml` must be updated:
        - Fork the repository in with your own account.
        - Update icclim version number at the top.
        - Update `source.sha256` value with the tar.gz sha256.
            You can get the tar.gz hash from `pypi <https://pypi.org/project/icclim/#files>`_ using `view hashes` link.
        - Add any new dependency in `requirements`.
        - Create a pull request with these changes, targeting the main fork on main branch
        - Wait for the CI feedback and correct things if needed.
        - Merge the pull request

#. Update `icclim github release <https://github.com/cerfacs-globc/icclim/releases>`_
    - You should add a tag similar to the new version number.
    - You should enter a short description of the changes, with a highlight on breaking changes.
    - There is no need to fill the assets with anything as the release assets are already on conda-forge and pypi.

Release process
===============

#. Make sure all tests pass
#. Create and checkout a release branch
#. Bump version in ``/icclim/__init__.py``
#. Update release_notes in ``doc/source/references/release_notes.rst``
#. Merge release branch to master with a PR
#. Clean dist directory content
#. Create wheel file on master

    .. code-block:: sh

        python3 setup.py bdist_wheel

#. Create source archive

    .. code-block:: sh

        python3 -m setup.py sdist

#. Try to upload on testpypi first

    .. code-block:: sh

        python3 -m twine upload --repository testpypi dist/*

#. Try to install testpypi version on a clean virtual environment

    .. code-block:: sh

        python3 -m pip install --index-url https://test.pypi.org/simple/ icclim

.. note::

    It may fail due to missing dependencies in test.pypi.
    In that case, create the environment from icclim environment.yml file to
    pull all needed dependencies from conda.

#. Upload to pypi for real

    .. code-block:: sh

        python3 -m twine upload dist/*

.. note::

    Conda artifact should be updated automatically from pypi.

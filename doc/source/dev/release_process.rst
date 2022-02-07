Release process
===============

# Make sure all tests pass
# Create and checkout release branch
# Bump version

Files where to update icclim version number: ``{/icclim/__init__.py, doc/source/references/release_notes.rst }

# Update release_notes in doc
# Merge release branch to master
# Create wheel file on master

.. code-block:: sh

    python3 setup.py bdist_wheel

# Create source archive

.. code-block:: sh

    python3 -m setup.py sdist

# Try to upload on testpypi first

.. code-block:: sh

    python3 -m twine upload --repository testpypi dist/*

# Try to install testpypi version on a clean virtual environment

.. code-block:: sh

    python3 -m pip install --index-url https://test.pypi.org/simple/ icclim

# Upload to pypi for real

.. code-block:: sh

    python3 -m twine upload dist/*

Conda artifact should be updated automatically

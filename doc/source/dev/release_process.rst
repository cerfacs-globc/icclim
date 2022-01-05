.. _release_process:

Release process
===============

1. Make sure all tests pass
2. Bump version
3. Update release_notes in doc
4. Create wheel file

.. code-block:: sh

    python3 setup bdist_wheel

5. Create source archive

.. code-block:: sh

    python3 -m setup sdist

6. Try to upload on testpypi first

.. code-block:: sh

    python3 -m twine upload --repository testpypi dist/*

7. Try to install testpypi version on a clean virtual environment

.. code-block:: sh

    python3 -m pip install --index-url https://test.pypi.org/simple/ your-package

8. Upload to pypi for real

.. code-block:: sh

    python3 -m twine upload dist/*

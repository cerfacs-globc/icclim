##############
 Installation
##############

.. note::

   Make sure you have **Python 3.10+**.

****************************
 Installation (Linux, OS X)
****************************

To install from conda-forge (recommended)
==========================================

The easiest way to install icclim is via `conda-forge <https://conda-forge.org/>`_,
which also installs all dependencies automatically:

.. code:: sh

   conda install -c conda-forge icclim

Or, if you are using ``mamba``:

.. code:: sh

   mamba install -c conda-forge icclim

To install from pip
===================

.. code:: sh

   pip install icclim

To install from sources
=======================

With git:

#. ``git clone https://github.com/cerfacs-globc/icclim.git``
#. ``cd icclim``
#. ``pip install .``

Or without git:

#. Go to https://github.com/cerfacs-globc/icclim/releases/.
#. Download the last release: click **Source code (zip)** or **Source code (tar.gz)**.
#. Extract the archive and go to the extracted directory.
#. ``pip install .``

Check the installation
=======================

.. code:: python

   import icclim
   print(icclim.__version__)

.. note::

   icclim was not tested on Windows platform.

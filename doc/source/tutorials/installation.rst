##############
 Installation
##############

**************
 Dependencies
**************

The dependencies to run icclim are listed under our `requirements.txt
<https://github.com/cerfacs-globc/icclim/blob/master/requirements.txt>`_
file.

****************************
 Installation (Linux, OS X)
****************************

.. note::

   Make sure you have **Python 3.9+**.

To install from pip
===================

.. code:: sh

   pip install icclim

To install from sources
=======================

With git:

#. ``git clone git://github.com/cerfacs-globc/icclim``
#. ``cd icclim``

Or without git:

#. Go to https://github.com/cerfacs-globc/icclim/releases/.
#. you can download the last release: click to **Source code (zip)** or
   **Source code (tar.gz)**.
#. Extract the file.
#. Go to extracted directory.

Then run the following commands:

.. code:: sh

   [sudo] python setup.py install

or if you don't have root or sudo access, as a normal user:

.. code:: sh

   python setup.py install --user

6. Check if the library is installed correctly:

.. code:: sh

   >>> import icclim

To get the version of installed library, do the following:

.. code:: sh

   >>> icclim.__version__
   5.0.0

.. note::

   icclim was not tested on Windows platform...

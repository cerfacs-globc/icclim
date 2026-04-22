*************************
Cold-Spell Duration Index
*************************

About
=====
In this tutorial, we will show you haw to calculate the :ref:`Cold-Spell Duration Index<csdi>` (CSDI), using data provided by Copernicus Climate Change Service (`C3S`_).

After preparing our environment, we will download the daily minimum temperature data from C3S `Climate Data Store`_, inspect them and use the :mod:`icclim` library to calculate the CSDI. Finally, we will display the CSDI using :mod:`matplotlib` to end up with the following map.

.. image:: E_OBS_csdi_index.png
    :align: center
    :alt: European map of the Cold-Spell Duration Index

.. _C3S: https://climate.copernicus.eu/
.. _Climate Data Store: https://cds.climate.copernicus.eu/

Required libraries
==================
.. important::
    Before anything, we need to have a Python virtual environment set up. If necessary, :ref:`here<pyVirtualEnv>` is how to set it up.

Additionally to :mod:`icclim`, to work the following example, we will need:

.. code-block:: python

    # to download data
    import urllib3 # will disable warning for data download though API
    import cdsapi # Climate Data Store API
    
    # to extract data from archive file
    from zipfile import ZipFile
    
    # of course:
    import icclim

    # to enable plotting
    import matplotlib.pyplot as plt
    import cartopy

If some of these libraries miss in our virtual environment, we need to run the following install commands in the console:

.. code-block:: python

    %pip install cartopy
    %pip install matplotlib
    %pip install cdsapi
    %pip install icclim
    %pip install utllib3

.. note::
    ``%`` ensures that the libraries installation occurs in our virtual environment.

.. note::
    ZipFile is Python Standard Library which is installed with Python installation.

Data download and data call
===========================
Climate Data Store API key set-up
---------------------------------
Since we will work with the minimum temperature data from C3S `Climate Data Store`_ (CDS), we will need first to `log in, or register`_, to the CDS. Once logged in, we retrieve can retrieve the API URL, as well as our CDS API key:

.. _log in, or register: https://accounts.ecmwf.int/auth/realms/ecmwf/protocol/openid-connect/auth?client_id=cds&scope=openid%20email&response_type=code&redirect_uri=https%3A%2F%2Fcds.climate.copernicus.eu%2Fapi%2Fauth%2Fcallback%2Fkeycloak&state=nyS6TnhZ00Dp6WUovTTWs3rDWLoAbV0-TsmZjH678L8&code_challenge=y49Rc-vRJVxgVgQ56tWI2dQGIuRBSkQw8EzlE2Zugso&code_challenge_method=S256

.. image:: Screenshot_C3S_CDS.png
    :align: center
    :alt: URL and the API key from C3S CDS

We copy and paste them into a URL and KEY variable respectively.

.. code-block:: python

    URL = 'https://cds.climate.copernicus.eu/api'
    KEY = '<PERSONAL-ACCESS-TOKEN>'

Data download
-------------
As we saw it at the beginning of this tutorial, we will need daily minimum temperature data. Data for this parameter are available as part of the E-OBS daily gridded meteorological data for Europe from 1950 to present. For this exercise we select a shorter period to allow a faster download: we will pick the period from 2011 to 2021.
In the frame of this tutorial, we will specifically use the **E-OBS daily gridded meteorological data for Europe from 1950 to present derived from in-situ observations** data set, which can be found using the search bar from CDS `home page <Climate Data Store>`__.
Having selected the data set from the search results page, we now need to specify what product type, variables, temporal and geographic coverage we are interested in. These can all be selected in the **"Download data"** tab (see picture below).

.. image:: Screenshot_E-OBS_daily_gridded_data_download_tab.png
    :align: center
    :alt: Download tab of the E-OBS daily gridded meteorological data for Europe from 1950 to present derived from in-situ observations


We select the following parameters to refine our data selection :

* Product type: **Ensemble mean**
* Variable: **Minimum temperature**
* Grid resolution: **0.1deg** 
* Period: **2011-2021**
* Version: **25.0e** (in "All other available versions")

Then at the bottom of the form appears a code block which we can copy and paste in our script.

.. code-block:: python

    dataset = "insitu-gridded-observations-europe"
    request = {
        "period": "2011_2021"
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download()

.. note::
    Since we already imported :mod:`cdsapi` library, we can skip that code line in the generated code block.

Before running the code block, we need to accept the terms and conditions of this specific data set. When the code is run in our environment, we will receive the daily minimum temperature in a zip archive.
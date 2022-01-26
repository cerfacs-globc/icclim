.. _clix-meta: https://github.com/clix-meta/clix-meta
.. _xclim: https://github.com/Ouranosinc/xclim

Disambiguation on xclim and icclim
==================================

At first glance it seems `xclim`_ and icclim serve the same purpose but their differences are in the details.
With version 5 of icclim, xclim became a building block of icclim. xclim handles some of the core features, notably
the calculation of climate indices. icclim also make use of xclim capabilities to handle i/o units and to check
input data and metadata validity.

While developing icclim v5, we tried to integrate all relevant features directly in xclim.
This is for example the case for the bootstrapping of percentiles, which is a key feature of icclim and
its development was a collaborative work from both parties.
This way, xclim gains new features and users and icclim can rely on all the efforts that was already put into xclim.
We also benefits from the knowledge of xclim developers thanks to code reviews and discussions on their repository.

This joint effort helped tremendously to create what icclim is today and we believe it strengthens the collaborative
ecosystem of geo sciences.

--------

On the other side, we had to clarify what would be the purpose of icclim without its internal climate index computation
feature.
Thus, icclim is now a library which wraps index calculation in a familiar API while **pre-processing** inputs and
decorates output with **metadata**.

Pre-processing includes:

- Handling of multiple input formats (netcdf files, xarray.Dataset, text file (TBD))
- Simple automated data chunking
- Variable detection in input (based on the work done in `clix-meta`_)
- Wet day filtering for precipitation indices
- Simple unit handling (rely on xclim pint registry)
- Time sub-setting of data
- Custom sampling frequency of output
- Index configuration, such as threshold values or output unit

Output metadata includes:

- History
- Title
- Units
- time_bounds
- provenance (TBD)
- ...

Beside, icclim v5 still provides a way to write **user defined indices** using a simili JSON data structure
(actually a python dictionary) with ``icclim.index(user_index=...)``.
The output metadata is however not as rich as with ECA&D indices.

One of the goal of icclim is also to provide an API which require zero knowledge of xarray letting user new to python
and its ecosystem reliably compute climate indices.
This is one of the reason why icclim exposes a single entry point for all it's features with ``icclim.index``.
It means users new to xarray might prefer icclim while experts could find xclim more convenient.

xclim' scope is larger than the one of icclim. xclim add metadata to the computed index in multiple languages (currently
FR and EN), it computes many indices not part of the ECA&D specification, it provides biais adjustment and downscaling
algorithms and is capable of detecting many common errors which can be found in netCDF files through health checks.
All those features make `xclim`_ a very good tool by itself and we encourage the reader to check `xclim documentation
<https://xclim.readthedocs.io/en/stable/index.html>`_ for more information on it's features.

.. note::
    xclim provides a virtual module named ``icclim`` which exposes in a xclim style the ECA&D indices that were
    historically provided by icclim. But this module **does not** use our library icclim directly, otherwise we would
    have a weird circular dependency.

We are very grateful for the work done on xclim and we hope to continue the collaboration while both libraries grow in
users and maturity.

Disambiguation on xclim and icclim
==================================

On a first glance it seems xclim and icclim serve the same purpose but the difference is in the details.
With version 5 of icclim, xclim became a building block of icclim. xclim handles some the core features, notably
the calculation climate indices. Beside, we also make use of xclim capabilities to handle i/o units and to check
input data and metadata validity.

This relationship between the two libraries means they can benefit from one another.
While developing icclim v5, we decided to integrate as much as possible relevant features in xclim directly, instead of
keeping them on our code base. This is for example the case for the bootstrapping of percentile which was a
collaborative work from both party. This way, xclim gains new features and users through us and we can rely on all the
work they have already accomplished. Plus, we benefit from their knowledge thanks to code reviews and discussions on
their repository.
This joint effort helped tremendously to create what icclim is today and we believe it strengthens a collaborative
ecosystem.

On the other side, we had to clarify what would be the purpose of icclim without its internal climate index computation.
Thus, icclim now wraps index calculation in a familiar API while pre-processing inputs and dress output with
metadata.
Pre-processing includes:

- Handling of multiple input formats (netcdf files, xarray.Dataset, text file (TBD)).
- Simple automated data chunking, then fed to Dask.
- Variable detection in input based on the work done in :ref:`clix-meta`.
- Wet day filtering for precipitation indices.
- Simple unit handling (rely xclim pint registry).
- Time sub-setting of data.

Output metadata includes:

- History
- Title
- Units
- time_bounds
- provenance (TBD)

Beside, icclim still provides a way to write user defined indices using a simili JSON data structure
(actually a python dictionary) with ``icclim.index(user_index=...)``.
The metadata is however not as rich as with ECA&D indices.

One of the goal of icclim is to provide an API which require zero knowledge of xarray letting user new to python and
its ecosystem reliably compute climate indices.
This is one of the reason why icclim exposes a single entry point for all it's features with ``icclim.index``.
It means users new to xarray might prefer icclim while experts could find xclim more convenient.

We are very grateful for the work done on xclim and we hope to continue the collaboration while both libraries grow in
users and maturity.

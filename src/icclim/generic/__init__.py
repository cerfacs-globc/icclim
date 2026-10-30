"""Generic indices.

The generic indices public API, via `icclim.generic` package, is generated from the
`icclim.generic.registry.GenericIndicatorRegistry` registry definitions.
icclim's generic indices are a generalization of the climate indices found in
ECAD and DCSC's registries.
They can be computed on any dataset and make use of the `Threshold` interface
to enable the creation of personalized indices.
The parameters of the functions are specialized to each index but are all taken from
`icclim.main.index` general function.
The generic indices exposed by `icclim.generic` are specialized entry points
built from `icclim.main.index` for generic indicator definitions.

Examples
--------
>>> import numpy as np
>>> import pandas as pd
>>> import xarray as xr
>>> from icclim.generic import count_occurrences
>>> from icclim import build_threshold
>>> tas = xr.DataArray(
...     np.full(365, 303.15),
...     coords={"time": pd.date_range("2001-01-01", periods=365)},
...     dims="time",
...     name="tas",
...     attrs={"units": "K"},
... )
>>> thresh = build_threshold(">= 25 °C and <= 30 °C")
>>> result = count_occurrences(
...     tas, var_name="tas", threshold=thresh, completeness="none"
... ).compute()
>>> int(result.count_occurrences.item())
365

"""

from icclim._generated._generic import *  # noqa: F403

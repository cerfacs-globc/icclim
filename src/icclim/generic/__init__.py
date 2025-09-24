"""Generic indices.

The generic indices public API, via `icclim.generic` package, is generated from the
`icclim.generic.registry.GenericIndicatorRegistry` registry definitions.
icclim's generic indices are a generalization of the climate indices found in
ECAD and DCSC's registries.
They can be computed on any dataset and make use of the `Threshold` interface
to enable the creation of personalized indices.
The parameters of the functions are specialized to each index but are all taken from
`icclim.main.index` general function.
In other words, the generic indices in `icclim.generic` package are specializations
of `icclim.main.index` for ECAD indices.

Examples
--------
>>> from icclim.generic import count_occurrences
>>> from icclim import build_threshold
>>> thresh = build_threshold(">= 25 °C and <= 30 °C")
>>> result = count_occurrences("tas.nc", thresh).compute()
>>> print(result.count_occurrences)

"""

# from icclim._generated._generic import *

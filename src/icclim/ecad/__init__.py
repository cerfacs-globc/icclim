"""European Climate Assesment & Dataset (ECAD) indices.

The ECAD indices public API, via `icclim.ecad` package, is generated from the
`icclim.ecad.registry.EcadIndexRegistry` registry definitions.
The parameters of the functions are specialized to each index but are all taken from
`icclim.main.index` general function.
The ECAD indices exposed by `icclim.ecad` are specialized entry points built
from `icclim.main.index` for ECAD indices.
"""

from icclim._generated._ecad import *  # noqa: F403

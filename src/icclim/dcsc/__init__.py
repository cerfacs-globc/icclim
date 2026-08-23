"""Direction de la Climatologie et des Services Climatiques (DCSC) indices.

Meteo France's Direction de la Climatologie et des Services Climatiques (DCSC)
specialized indices.

The DCSC indices public API, via the `icclim.dcsc` package, is generated from the
`icclim.dcsc.registry.DcscIndexRegistry` registry definitions.
The parameters  of the functions are specialized to each index but are all taken from
`icclim.main.index` general function.
The DCSC indices exposed by `icclim.dcsc` are specialized entry points built
from `icclim.main.index` for DCSC indices.
"""

from icclim._generated._dcsc import *  # noqa: F403

"""Direction de la Climatologie et des Services Climatiques (DCSC) indices.

Meteo France's Direction de la Climatologie et des Services Climatiques (DCSC)
specialized indices.

The DCSC indices public API, via the `icclim.dcsc` package, is generated from the
`icclim.dcsc.registry.DcscIndexRegistry` registry definitions.
The parameters  of the functions are specialized to each index but are all taken from
`icclim.main.index` general function.
The DCSC indices exposed by `icclim.dcsc` are specialized entry points built
from `icclim.main.index` for DCSC indices.

The DRIAS normal (reference period 1976-2005) used by the indices that need a normal
is not set by icclim: the user supplies it with the ``normal`` argument.
"""

from icclim._generated._dcsc import *  # noqa: F403

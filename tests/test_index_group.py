from __future__ import annotations

import pytest

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.index_group import IndexGroupRegistry


@pytest.mark.parametrize(
    "gr",
    [
        ("temperature", IndexGroupRegistry.TEMPERATURE),
        ("heat", IndexGroupRegistry.HEAT),
        ("cold", IndexGroupRegistry.COLD),
        ("drought", IndexGroupRegistry.DROUGHT),
        ("rain", IndexGroupRegistry.RAIN),
        ("snow", IndexGroupRegistry.SNOW),
    ],
)
def test_lookup_success(gr):
    assert IndexGroupRegistry.lookup(gr[0]) == gr[1]


def test_lookup_error():
    with pytest.raises(InvalidIcclimArgumentError):
        IndexGroupRegistry.lookup("coin coin le canard")


def test_union():
    x = IndexGroupRegistry.RAIN | IndexGroupRegistry.SNOW
    assert x.name == "rain_snow"
    assert x.values[0] == IndexGroupRegistry.RAIN
    assert x.values[1] == IndexGroupRegistry.SNOW

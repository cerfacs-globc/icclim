from __future__ import annotations

import pytest

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
        ("compound", IndexGroupRegistry.COMPOUND),
    ],
)
def test_lookup_success(gr):
    assert IndexGroupRegistry.lookup(gr[0]) is gr[1]


def test_lookup_error():
    with pytest.raises(NotImplementedError):
        IndexGroupRegistry.lookup("coin coin le canard")

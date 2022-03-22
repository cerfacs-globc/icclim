import pytest

from icclim.models.index_group import IndexGroup


@pytest.mark.parametrize(
    "gr",
    [
        ("temperature", IndexGroup.TEMPERATURE),
        ("heat", IndexGroup.HEAT),
        ("cold", IndexGroup.COLD),
        ("drought", IndexGroup.DROUGHT),
        ("rain", IndexGroup.RAIN),
        ("snow", IndexGroup.SNOW),
        ("compound", IndexGroup.COMPOUND),
    ],
)
def test_lookup_success(gr):
    assert IndexGroup.lookup(gr[0]) is gr[1]


def test_lookup_error():
    with pytest.raises(NotImplementedError):
        IndexGroup.lookup("coin coin le canard")

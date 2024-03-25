from __future__ import annotations

import pytest
from icclim._core.model.standard_index import StandardIndex
from icclim.ecad.registry import EcadIndexRegistry
from icclim.exception import InvalidIcclimArgumentError


def test_listing() -> None:
    res = EcadIndexRegistry.to_list()
    indices = [
        k for k, v in EcadIndexRegistry.__dict__.items() if isinstance(v, StandardIndex)
    ]
    assert len(res) == len(indices)


class TestIndexFromString:
    def test_simple(self) -> None:
        res = EcadIndexRegistry.lookup("SU")
        assert res == EcadIndexRegistry.SU

    def test_lowercase(self) -> None:
        res = EcadIndexRegistry.lookup("tx90p")
        assert res == EcadIndexRegistry.TX90P

    def test_error(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            EcadIndexRegistry.lookup("cacahuête")

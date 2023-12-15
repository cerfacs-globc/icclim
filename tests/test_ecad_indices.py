from __future__ import annotations

import pytest

from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.standard_index import StandardIndex


def test_listing():
    res = EcadIndexRegistry.list()
    indices = [
        k for k, v in EcadIndexRegistry.__dict__.items() if isinstance(v, StandardIndex)
    ]
    assert len(res) == len(indices)


class Test_index_from_string:
    def test_simple(self):
        res = EcadIndexRegistry.lookup("SU")
        assert res == EcadIndexRegistry.SU

    def test_lowercase(self):
        res = EcadIndexRegistry.lookup("tx90p")
        assert res == EcadIndexRegistry.TX90P

    def test_error(self):
        with pytest.raises(InvalidIcclimArgumentError):
            EcadIndexRegistry.lookup("cacahuête")

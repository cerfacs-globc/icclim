from __future__ import annotations

import pytest

from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.icclim_exceptions import InvalidIcclimArgumentError


def test_listing():
    res = EcadIndexRegistry.list()
    assert len(res) == 49


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

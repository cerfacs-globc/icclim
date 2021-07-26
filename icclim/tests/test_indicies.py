from icclim.indices import Indice, indice_from_string, su, tx90p

import pytest


class Test_indice_from_string:
    def test_simple(self):
        res = indice_from_string("SU")
        assert res == Indice.SU

    def test_lowercase(self):
        res = indice_from_string("tx90p")
        assert res == Indice.TX90P

    def test_error(self):
        with pytest.raises(Exception):
            indice_from_string("cacahuête")

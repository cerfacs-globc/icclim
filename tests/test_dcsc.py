from icclim.dcsc import txnd

from tests.testing_utils import stub_tas


def test_txnd() -> None:
    tas = stub_tas(20)
    normal = stub_tas(10)
    tas[0:10] = 12
    res = txnd(in_files=tas, normal=normal, slice_mode="month").load()
    # 21 days with tas > normal + 5 deg_C
    assert res.TXND.isel(time=0) == 21

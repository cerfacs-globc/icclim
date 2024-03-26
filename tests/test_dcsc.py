from icclim.dcsc import txnd

from tests.testing_utils import stub_tas


def test_txnd() -> None:
    tas = stub_tas(10, lat_length=10, lon_length=10)
    normal = tas.mean(dim="time", keep_attrs=True)
    tas = tas.where(tas.time.dt.dayofyear > 10, 42)
    res = txnd(in_files=tas, normal=normal, slice_mode="month").load()
    # 21 days with tas > normal + 5 deg_C
    assert res.TXND[0, 0, 0] == 10

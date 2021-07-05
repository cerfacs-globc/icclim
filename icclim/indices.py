from enum import Enum
from xclim import atmos
from xarray import DataArray

from xclim.core.calendar import percentile_doy

def to_celcius(threshold)->str:
    f"{threshold} degC"

def gd4( **kwargs)-> DataArray :
    return atmos.growing_degree_days(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def cfd( **kwargs)-> DataArray :
    return atmos.consecutive_frost_days(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def fd( **kwargs)-> DataArray :
    return atmos.frost_days(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def hd17( **kwargs)-> DataArray :
    return atmos.heating_degree_days(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def id( **kwargs)-> DataArray :
    return atmos.ice_days(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def csdi( **kwargs)-> DataArray :
    return atmos.cold_spell_duration_index(**kwargs['da'], percentile_doy(**kwargs['percentile_da'], **kwargs['window'], 10),6, **kwargs['freq'], True)  

def tg10p( **kwargs)-> DataArray :
    return atmos.tg10p(**kwargs['da'], percentile_doy(**kwargs['percentile_da'], **kwargs['window'], 10), **kwargs['freq'], True)  

def tn10p( **kwargs)-> DataArray :
    return atmos. tn10p(**kwargs['da'], percentile_doy(**kwargs['percentile_da'], **kwargs['window'], 10), **kwargs['freq'], True)  

def tx10p( **kwargs)-> DataArray :
    return atmos.tx10p(**kwargs['da'], percentile_doy(**kwargs['percentile_da'], **kwargs['window'], 10), **kwargs['freq'], True)  

def txn( **kwargs)-> DataArray :
    return atmos.tx_min(**kwargs['da'], **kwargs['freq'])  

def tnn( **kwargs)-> DataArray :
    return atmos.tn_min(**kwargs['da'], **kwargs['freq'])  

def cdd(**kwargs)-> DataArray :
    # TODO does not exist on xclim atmos module
    raise NotImplemented('nope')

def su( **kwargs)-> DataArray :
    return atmos.tx_days_above(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tr( **kwargs)-> DataArray :
    return atmos.tropical_nights(**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def wsdi( **kwargs)-> DataArray :
    return atmos.warm_spell_duration_index(**kwargs['da'],percentile_doy(**kwargs['percentile_da'], **kwargs['window'], 90), 6, **kwargs['freq'], True)  

def tg90p( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tn90p( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tx90p( **kwargs)-> DataArray :
    return atmos.tx90p(        **kwargs['da'], percentile_doy(**kwargs['percentile_da'], **kwargs['window'], 90), **kwargs['freq'], True    )  

def txx( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tnx( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def csu( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def prcptot( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def rr1( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def sdii( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def cwd( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r10mm( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r20mm( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def rx1day( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def rx5day( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r75p( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r75ptot( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r95p( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r95ptot( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r99p( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def r99ptot( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def sd( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def sd1( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def sd5cm( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def sd50cm( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tg( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tn( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def tx( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def dtr( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def etr( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def vdtr( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def cd( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def cw( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def wd( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

def ww( **kwargs)-> DataArray :
    return atmos. (**kwargs['da'], to_celcius( **kwargs['threshold']), **kwargs['freq'])  

class Indice(Enum):
    GD4 = gd4
    CFD = cfd
    FD = fd
    HD17 = hd17
    ID = id
    CSDI = csdi
    TG10p = tg10p
    TN10p = tn10p
    TX10p = tx10p
    TXn = txn
    TNn = tnn
    CDD = cdd
    SU = su
    TR = tr
    WSDI = wsdi
    TG90p = tg90p
    TN90p = tn90p
    TX90p = tx90p
    TXx = txx
    TNx = tnx
    CSU = csu
    PRCPTOT = prcptot
    RR1 = rr1
    SDII = sdii
    CWD = cwd
    R10mm = r10mm
    R20mm = r20mm
    RX1day = rx1day
    RX5day = rx5day
    R75p = r75p
    R75pTOT = r75ptot
    R95p = r95p
    R95pTOT = r95ptot
    R99p = r99p
    R99pTOT = r99ptot
    SD = sd
    SD1 = sd1
    SD5cm = sd5cm
    SD50cm = sd50cm
    TG = tg
    TN = tn
    TX = tx
    DTR = dtr
    ETR = etr
    vDTR = vdtr
    CD = cd
    CW = cw
    WD = wd
    WW = ww


def indice_from_string(s: str) -> Indice:
    for e in Indice:
        if e.name == s:
            return e
    raise Exception(f"Unknown indice {s}")


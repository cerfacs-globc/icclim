from enum import Enum

TEMPERATURE_GROUP = "temperature"
HEAT_GROUP = "heat"
COLD_GROUP = "cold"
DROUGHT_GROUP = "drought"
RAIN_GROUP = "rain"
SNOW_GROUP = "snow"
COMPOUND_GROUP = "compound"

# Aliases of input variables names. Source: clix-meta
PR = "precip"
TAS = "tas"
TASMAX = "tmax"
TASMIN = "tmin"


class Indice(Enum):

    TG = ("tg", TEMPERATURE_GROUP, [TAS])
    TN = ("tn", TEMPERATURE_GROUP, [TASMIN])
    TX = ("tx", TEMPERATURE_GROUP, [TASMAX])

    SU = ("su", HEAT_GROUP, [TASMAX])
    TR = ("tr", HEAT_GROUP, [TASMIN])
    WSDI = ("wsdi", HEAT_GROUP, [TASMAX])
    TG90p = ("tg90p", HEAT_GROUP, [TAS])
    TN90p = ("tn90p", HEAT_GROUP, [TASMIN])
    TX90p = ("TX90p", HEAT_GROUP, [TASMAX])
    TXx = ("txx", HEAT_GROUP, [TASMAX])
    TNx = ("tnx", HEAT_GROUP, [TASMIN])
    CSU = ("csu", HEAT_GROUP, [TASMAX])

    GD4 = ("gd4", COLD_GROUP, [TAS])
    FD = ("fd", COLD_GROUP, [TASMIN])
    CFD = ("cfd", COLD_GROUP, [TASMIN])
    HD17 = ("hd17", COLD_GROUP, [TASMIN])
    ID = ("id", COLD_GROUP, [TASMAX])
    TG10p = ("tg10p", COLD_GROUP, [TAS])
    TN10p = ("tn10p", COLD_GROUP, [TASMIN])
    TX10p = ("tx10p", COLD_GROUP, [TASMAX])
    TXn = ("txn", COLD_GROUP, [TASMAX])
    TNn = ("tnn", COLD_GROUP, [TASMIN])
    CSDI = ("csdi", COLD_GROUP, [TASMIN])

    CDD = ("cdd", DROUGHT_GROUP, [PR])

    PRCPTOT = ("prcptot", RAIN_GROUP, [PR])
    RR1 = ("rr1", RAIN_GROUP, [PR])
    SDII = ("sdii", RAIN_GROUP, [PR])
    CWD = ("cwd", RAIN_GROUP, [PR])
    R10mm = ("r10mm", RAIN_GROUP, [PR])
    R20mm = ("r20mm", RAIN_GROUP, [PR])
    RX1day = ("rx1day", RAIN_GROUP, [PR])
    RX5day = ("rx5day", RAIN_GROUP, [PR])
    R75p = ("r75p", RAIN_GROUP, [PR])
    R75pTOT = ("r75ptot", RAIN_GROUP, [PR])
    R95p = ("r95p", RAIN_GROUP, [PR])
    R95pTOT = ("r95ptot", RAIN_GROUP, [PR])
    R99p = ("r99p", RAIN_GROUP, [PR])
    R99pTOT = ("r99ptot", RAIN_GROUP, [PR])

    SD = ("sd", SNOW_GROUP, [PR])
    SD1 = ("sd1", SNOW_GROUP, [PR])
    SD5cm = ("sd5cm", SNOW_GROUP, [PR])
    SD50cm = ("sd50cm", SNOW_GROUP, [PR])

    # compound
    DTR = ("dtr", TEMPERATURE_GROUP, [TASMAX, TASMIN])
    ETR = ("etr", TEMPERATURE_GROUP, [TASMAX, TASMIN])
    vDTR = ("vdtr", TEMPERATURE_GROUP, [TASMAX, TASMIN])

    def __init__(
        self, indice_name: str, group: str, variables,
    ):
        self.indice_name = indice_name
        self.group = group
        self.variables = variables

# fmt: off
# flake8: noqa

# ECA&D indices groups
TEMPERATURE_GROUP = "temperature"
HEAT_GROUP = "heat"
COLD_GROUP = "cold"
DROUGHT_GROUP = "drought"
RAIN_GROUP = "rain"
SNOW_GROUP = "snow"
COMPOUND_GROUP = "compound"

# placeholder for user_indices
PERCENTILE_THRESHOLD_STAMP = "p"
WET_DAY_THRESHOLD = 1  # 1mm
PRECIPITATION = "p"
TEMPERATURE = "t"

# percentiles dimension from percentile_doy
PERCENTILES_COORD = "percentiles"
# attribut holding the in_base time bounds
IN_BASE_IDENTIFIER = "reference_epoch"

# Aliases of input variables names. Source: clix-meta
PR = ["pr", "pradjust", "prec", "rr", "precip", "PREC", "Prec", "RR", "PRECIP", "Precip"]
TAS = ["tas", "tavg", "ta", "tasadjust", "tmean", "tm", "tg", "meant", "TMEAN", "Tmean", "TM", "TG", "MEANT", "meanT", "tasmidpoint"]
TAS_MAX = ["tasmax", "tasmaxadjust", "tmax", "tx", "maxt", "TMAX", "Tmax", "TX", "MAXT", "maxT"]
TAS_MIN = ["tasmin", "tasminadjust", "tmin", "tn", "mint", "TMIN", "Tmin", "TN", "MINT", "minT"]

# Source of index definition
ECAD_ATBD = "Source: ECA&D, Algorithm Theoretical Basis Document (ATBD) v11"

# Index qualifiers
QUANTILE_BASED = "QUANTILE_BASED"  # fields: QUANTILE_INDEX_FIELDS
MODIFIABLE_UNIT = "MODIFIABLE_UNIT"  # fields: out_unit
MODIFIABLE_THRESHOLD = "MODIFIABLE_THRESHOLD"  # fields: threshold
MODIFIABLE_QUANTILE_WINDOW = "MODIFIABLE_QUANTILE_WINDOW"  # fields: window_width

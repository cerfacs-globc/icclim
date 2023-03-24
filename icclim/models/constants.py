from __future__ import annotations

# fmt: off
# flake8: noqa

ICCLIM_VERSION = "6.3.0"

# placeholders for user_index
PERCENTILE_THRESHOLD_STAMP = "p"
WET_DAY_THRESHOLD = 1  # 1mm
USER_INDEX_PRECIPITATION_STAMP = "p"
USER_INDEX_TEMPERATURE_STAMP = "t"

# percentiles dimension from percentile_doy
PERCENTILES_COORD = "percentiles"
# attribut holding the in_base time bounds
REFERENCE_PERIOD_ID = "reference_epoch"
# coordinate of day of year values (usually from 1 to 365/366)
DOY_COORDINATE = "dayofyear"
# Units attribute key for DataArray(s)
UNITS_KEY = "units"


# Aliases of input percentiles variables names
# Source icclim dev
VALID_PERCENTILE_DIMENSION = ["quantile", "percentile", "per", "centile"]

# Source of ECA&D indices definition
ECAD_ATBD = "ECA&D, Algorithm Theoretical Basis Document (ATBD) v11"

# Index qualifiers (needed to generate the API)
QUANTILE_BASED = "QUANTILE_BASED"
REFERENCE_PERIOD_INDEX = "REFERENCE_PERIOD_INDEX"


# Map of months index to their short name, used to get a pandas frequency anchor
MONTHS_MAP = {1:"JAN",  2:"FEB", 3:"MAR", 4:"APR", 5:"MAY", 6:"JUN", 7:"JUL", 8:"AUG", 9:"SEP", 10:"OCT", 11:"NOV", 12:"DEC" }

# Season defined by their month numbers
AMJJAS_MONTHS:list[int] = [*range(4, 9)]
ONDJFM_MONTHS:list[int] = [10, 11, 12, 1, 2, 3]
DJF_MONTHS:list[int] = [12, 1, 2]
MAM_MONTHS:list[int] = [*range(3, 6)]
JJA_MONTHS:list[int] = [*range(6, 9)]
SON_MONTHS:list[int] = [*range(9, 12)]

# pseudo units used with Threshold class (not in Pint)
PERIOD_PERCENTILE_UNIT = "period_per"
DOY_PERCENTILE_UNIT = "doy_per"

# Mapping of frequencies to generate metadata
# copied from xclim and updated.
# todo: we should probably turn that mapping to jinja templates to make it easier to maintain
EN_FREQ_MAPPING = {
    "YS": "year(s)", "Y": "year(s)", "AS": "year(s)", "A": "year(s)",
    "QS": "season(s)", "Q": "season(s)",
    "MS": "month(s)", "M": "month(s)",
    "W": "week(s)",
    "D": "day(s)",
    "H": "hour(s)",
    "JAN": "January starting", "FEB": "February starting", "MAR": "March starting", "APR": "April starting", "MAY": "May starting", "JUN": "June starting", "JUL": "July starting", "AUG": "August starting", "SEP": "September starting", "OCT": "October starting", "NOV": "November starting", "DEC": "December starting",
    # Arguments to "indexer"
    "DJF": "wintry", "MAM": "springlong", "JJA": "summery", "SON": "autumnal",
    "norm": "Normal",
    "m1": "january",  "m2": "february",  "m3": "march",  "m4": "april",  "m5": "may",  "m6": "june",  "m7": "july",  "m8": "august",  "m9": "september",  "m10": "october",  "m11": "november",  "m12": "december",
    "MON": "monday starting", "TUE": "tuesday starting", "WED": "wednesday starting", "THU": "thursday starting", "FRI": "friday starting", "SAT": "saturday starting", "SUN": "sunday starting"
}
FREQ_DELTA_MAPPING = {
    "YS": (1, "Y" ), "Y": (1, "Y" ), "AS": (1, "Y" ), "A": (1, "Y" ),
    "QS": (3, "M" ), "Q": (3, "M" ),
    "MS": (1, "M" ), "M": (1, "M" ),
    "W": (7, "D" ),
    "D": (1, "D" ),
    "H": (1, "H" ),
}

# Special CF unit
PART_OF_A_WHOLE_UNIT = "1"

# companion parameter to slice_mode
GROUP_BY_METHOD = "groupby"
RESAMPLE_METHOD = "resample"
GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD = "groupby_ref_and_resample_study"

DEFAULT_DOY_WINDOW = 5

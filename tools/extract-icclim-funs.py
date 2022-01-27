"""
Icclim indices extractor.
It creates a new python module which wraps each icclim indices as a function.
These functions signature is coherent with icclim.index with all the unnecessary
parameters trimmed from it.

To use is from icclim root do:
.. code-block:: sh

    python3 -m ./tool/extract-icclim-funs.py
"""

import inspect
import re
from typing import List

from models.constants import (
    MODIFIABLE_QUANTILE_WINDOW,
    MODIFIABLE_THRESHOLD,
    MODIFIABLE_UNIT,
    QUANTILE_BASED,
)
from models.ecad_indices import EcadIndex

import icclim

ICCLIM_MANDATORY_FIELDS = ["in_files", "index_name"]
# Note: callback args are not included below
ICCLIM_OPTIONAL_FIELDS = [
    "slice_mode",
    "netcdf_version",
    "out_file",
    "transfer_limit_Mbytes",
    "ignore_Feb29th",
    "var_name",
    "time_range",
]
QUANTILE_INDEX_FIELDS = [
    "base_period_time_range",
    "only_leap_years",
    "interpolation",
    "save_percentile",
]

MODIFIABLE_QUANTILE_WINDOW_FIELD = "window_width"
MODIFIABLE_THRESHOLD_FIELD = "threshold"
MODIFIABLE_UNIT_FIELD = "out_unit"

TAB = "    "


def run():
    with open("../icclim_wrapped.py", "w") as f:
        acc = '''"""
This module has been auto-generated.
It exposes convenient index functions proxying to icclim.index function.
"""
import icclim
import xarray
import typing
import datetime
from icclim.icclim_logger import Verbosity\n
from icclim.models.frequency import Frequency
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation


'''
        for index in EcadIndex:
            acc += get_ecad_index_declaration(index)
        f.write(acc)


def get_ecad_index_declaration(index: EcadIndex):
    arguments = dict(inspect.signature(icclim.index).parameters)
    pop_args = []
    # Pop deprecated args
    pop_args.append("indice_name")
    pop_args.append("user_indice")
    # Pop unnecessary args
    pop_args.append("user_index")
    pop_args.append("callback")
    pop_args.append("callback_percentage_start_value")
    pop_args.append("callback_percentage_total")
    pop_args.append("index_name")  # specified with function name
    if QUANTILE_BASED not in index.qualifiers:
        for arg in QUANTILE_INDEX_FIELDS:
            pop_args.append(arg)
    if MODIFIABLE_QUANTILE_WINDOW not in index.qualifiers:
        pop_args.append(MODIFIABLE_QUANTILE_WINDOW_FIELD)
    if MODIFIABLE_THRESHOLD not in index.qualifiers:
        pop_args.append(MODIFIABLE_THRESHOLD_FIELD)
    if MODIFIABLE_UNIT not in index.qualifiers:
        pop_args.append(MODIFIABLE_UNIT_FIELD)

    for pop_arg in pop_args:
        arguments.pop(pop_arg)
    # TODO replace these concatenation mess with a proper template (jinja or similar)...
    fun_signature_args = f"\n{TAB}" + f",\n{TAB}".join(map(get_arg, arguments.values()))
    fun_signature = (
        f"\n\ndef {index.name.lower()}({fun_signature_args}) -> xarray.Dataset:\n"
    )
    params = get_params_docstring(list(arguments.keys()), icclim.index.__doc__)
    end_note = """
    Notes:
    ------
    This function has been auto-generated."""
    docstring = (
        f'{TAB}"""\n'
        f"{TAB}{index.definition}\n"
        f"{TAB}Source: {index.source}\n\n"
        f"{params}"
        f"{end_note}\n"
        f'{TAB}"""\n'
    )
    index_name_arg = f'\n{TAB}{TAB}index_name="{index.name}",\n{TAB}{TAB}'
    fun_call_args = index_name_arg + f",\n{TAB}{TAB}".join(
        [a + "=" + a for a in arguments]
    )
    fun_call = f"{TAB}return icclim.index({fun_call_args})\n"
    return f"{fun_signature}{docstring}{fun_call}"


def get_arg(a: inspect.Parameter):
    annotation = a.annotation
    if type(annotation) is type:
        annotation = annotation.__name__
    annotation = annotation.__str__().replace("NoneType", "None")
    annotation = annotation.__str__().replace(
        "xarray.core.dataset.Dataset", "xarray.Dataset"
    )
    prefix = f"{a.name}: {annotation}"
    if a.default is inspect._empty:
        return prefix
    default = a.default
    if type(default) is str:
        default = f'"{default.__str__()}"'
    return f"{prefix} = {default}"


def get_params_docstring(args: List[str], index_docstring: str):
    result = f"{TAB}Parameters\n{TAB}----------\n"
    matches = list(re.compile(".+ : .*").finditer(index_docstring))
    for arg in args:
        for i in range(0, len(matches) - 2):
            if matches[i].group().strip().startswith(arg):
                result += index_docstring[matches[i].start() : matches[i + 1].start()]
        if matches[-1].group().strip().startswith(arg):
            result += index_docstring[matches[-1].start() :]
    return result


if __name__ == "__main__":
    run()
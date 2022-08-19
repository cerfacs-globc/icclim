"""
Icclim indices extractor.
It creates a new python module which wraps each icclim index as a function.
Each generated functions signature is consistent with icclim.index signature but, all
the unused parameters are trimmed from the signature.

To generate the functions first icclim must be installed in the environment.
To install icclim from sources run:
>>> python -m setup install

Then the script can be run with:
>>> python ./tools/extract-icclim-funs.py
"""

from __future__ import annotations

import inspect
import os
import re
import sys
from pathlib import Path

from models.climate_index import StandardIndex

import icclim
from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.models.constants import (
    DOY_WINDOW,
    MIN_SPELL_WINDOW,
    QUANTILE_BASED,
    ROLLING_WINDOW,
)

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
    "save_thresholds",
]

WINDOW_FIELD = "window_width"
MODIFIABLE_THRESHOLD_FIELD = "threshold"
MODIFIABLE_UNIT_FIELD = "out_unit"

TAB = "    "

END_NOTE = """
    Notes
    -----
    This function has been auto-generated.

"""

DEFAULT_OUTPUT_PATH = Path(os.path.dirname(os.path.abspath(__file__))) / "pouet.py"


def run(path):
    with open(path, "w") as f:
        acc = '''"""
This module has been auto-generated.
To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
This module exposes each climate index as individual functions for convenience.
"""
# flake8: noqa E501
from __future__ import annotations

import datetime
from typing import Sequence

from xarray.core.dataset import Dataset

import icclim
from icclim.icclim_logger import Verbosity
from icclim.models.frequency import Frequency, FrequencyLike
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.user_index_dict import UserIndexDict
from icclim.pre_processing.input_parsing import InFileType

__all__ = [
'''
        ecad_indices = EcadIndexRegistry.values()
        acc += ",\n".join(
            list(map(lambda x: f'{TAB}"{x.short_name.lower()}"', ecad_indices))
        )
        acc += f',\n{TAB}"custom_index",\n]\n'
        for index in ecad_indices:
            acc += get_standard_index_declaration(index)
        acc += get_user_index_declaration()
        f.write(acc)


def get_user_index_declaration() -> str:
    icclim_index_args = dict(inspect.signature(icclim.index).parameters)
    pop_args = []
    # Pop deprecated args
    pop_args.append("indice_name")
    pop_args.append("user_indice")
    pop_args.append("transfer_limit_Mbytes")
    # Pop unnecessary args
    pop_args.append("callback")
    pop_args.append("callback_percentage_start_value")
    pop_args.append("callback_percentage_total")
    pop_args.append("index_name")
    pop_args.append("threshold")
    pop_args.append("window_width")
    # Pop not implemented yet
    pop_args.append("interpolation")
    # Pop manually added arg
    pop_args.append("user_index")  # for `custom_index`, user_index is mandatory
    for pop_arg in pop_args:
        icclim_index_args.pop(pop_arg)
    fun_signature_args = build_fun_signature_args(icclim_index_args)
    fun_signature = (
        f"\n\ndef custom_index(\n"
        f"user_index: UserIndexDict,"
        f"{fun_signature_args},\n"
        f") -> Dataset:\n"
    )
    args_docs = get_params_docstring(
        list(icclim_index_args.keys()), icclim.index.__doc__
    )
    docstring = (
        f'{TAB}"""\n'
        f"{TAB}This function can be used to create indices using simple operators.\n"
        f"{TAB}Use the `user_index` parameter to describe how the index should be "
        f"computed.\n"
        f"{TAB}You can find some examples in our documentation at :ref:`custom_indices`"
        f".\n\n"
        f"{args_docs}"
        f"{END_NOTE}"
        f'"""\n'
    )
    fun_call_args = f",\n{TAB}{TAB}".join([a + "=" + a for a in icclim_index_args])
    fun_call = (
        f"{TAB}return icclim.index(\n"
        f"{TAB}{TAB}user_index=user_index,\n"
        f"{TAB}{TAB}{fun_call_args},"
        f"\n{TAB})\n"
    )
    return f"{fun_signature}{docstring}{fun_call}"


def build_fun_signature_args(args) -> str:
    return f"\n{TAB}" + f",\n{TAB}".join(map(get_parameter_declaration, args.values()))


def get_standard_index_declaration(index: StandardIndex) -> str:
    icclim_index_args = dict(inspect.signature(icclim.index).parameters)
    pop_args = []
    # Pop deprecated args
    pop_args.append("indice_name")
    pop_args.append("user_indice")
    pop_args.append("transfer_limit_Mbytes")
    # Pop unnecessary args
    pop_args.append("user_index")
    pop_args.append("callback")
    pop_args.append("callback_percentage_start_value")
    pop_args.append("callback_percentage_total")
    pop_args.append("index_name")  # specified with function name
    pop_args.append("threshold")
    pop_args.append("out_unit")
    qualifiers = [] if index.qualifiers is None else index.qualifiers
    if QUANTILE_BASED not in qualifiers:
        for arg in QUANTILE_INDEX_FIELDS:
            pop_args.append(arg)
    if (
        ROLLING_WINDOW not in qualifiers
        or MIN_SPELL_WINDOW not in qualifiers
        or DOY_WINDOW not in qualifiers
    ):
        pop_args.append(WINDOW_FIELD)
    #     todo put default arg instead,
    #          disallow configuration of those for standard indices
    for pop_arg in pop_args:
        icclim_index_args.pop(pop_arg)
    fun_signature_args = build_fun_signature_args(icclim_index_args)
    fun_signature = (
        f"\n\ndef {index.short_name.lower()}({fun_signature_args},\n) -> Dataset:\n"
    )
    args_docs = get_params_docstring(
        list(icclim_index_args.keys()), icclim.index.__doc__
    )
    docstring = (
        f'{TAB}"""\n'
        f"{TAB}{index.short_name}: {index.definition}\n\n"
        f"{TAB}Source: {index.source}.\n\n"
        f"{args_docs}"
        f"{END_NOTE}"
        f'{TAB}"""\n'
    )
    index_name_arg = f'\n{TAB}{TAB}index_name="{index.short_name.upper()}",\n{TAB}{TAB}'

    fun_call_args = index_name_arg + f",\n{TAB}{TAB}".join(
        [a + "=" + a for a in icclim_index_args]
    )
    if isinstance(index.threshold, str):
        fun_call_args += f',\n{TAB}{TAB}threshold="{index.threshold}"'
    elif isinstance(index.threshold, list):
        fun_call_args += f",\n{TAB}{TAB}threshold={index.threshold}"
    if index.output_unit is not None:
        fun_call_args += f',\n{TAB}{TAB}out_unit="{index.output_unit}"'
    fun_call = f"{TAB}return icclim.index({fun_call_args},\n{TAB})\n"
    return f"{fun_signature}{docstring}{fun_call}"


def get_parameter_declaration(param: inspect.Parameter) -> str:
    annotation = param.annotation
    if type(annotation) is type:
        annotation = annotation.__name__
    annotation = annotation.__str__().replace("NoneType", "None")
    annotation = annotation.__str__().replace("xarray.core.dataset.Dataset", "Dataset")
    prefix = f"{param.name}: {annotation}"
    if param.default is inspect._empty:
        return prefix
    default = param.default
    if type(default) is str:
        default = f'"{default.__str__()}"'
    return f"{prefix} = {default}"


def get_params_docstring(args: list[str], index_docstring: str) -> str:
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
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_PATH
    run(file_path)

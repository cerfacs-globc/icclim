"""
Icclim indices extractor.
It creates a new python module which wraps each icclim index as a function.
Each generated functions signature is consistent with icclim.index signature but, all
the unused parameters are trimmed from the signature.

To generate the functions first icclim must be installed in the environment.
To install icclim from sources run:

.. code-block:: console

    python -m setup install

Then the script can be run with:
.. code-block:: console

     python ./tools/extract-icclim-funs.py
"""

from __future__ import annotations

import inspect
import os
import re
import sys
from pathlib import Path

import icclim
from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.icclim_logger import Verbosity
from icclim.models.constants import QUANTILE_BASED
from icclim.models.frequency import Frequency
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.standard_index import StandardIndex
from icclim.models.threshold import PercentileThreshold, Threshold, build_threshold
from icclim.models.user_index_dict import UserIndexDict

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
    "save_thresholds",
]

TAB = "    "

END_NOTE = """
    Notes
    -----
    This function has been auto-generated.

"""

DEFAULT_OUTPUT_PATH = Path(os.path.dirname(os.path.abspath(__file__))) / "pouet.py"
PATH_TO_DOC_FILE = (
    Path(os.path.dirname(os.path.abspath(__file__)))
    / "../doc/source/references"
    / "ecad_functions_api.rst"
)
DOC_START_PLACEHOLDER = ".. Generated API comment:Begin\n"
DOC_END_PLACEHOLDER = f"{TAB}{TAB}.. Generated API comment:End"


def generate_api(path):
    with open(path, "w") as f:
        acc = f'''"""
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
from {Verbosity.__module__} import {Verbosity.__name__}
from icclim.icclim_types import InFileLike, SamplingMethodLike
from {Frequency.__module__} import {Frequency.__name__}, FrequencyLike
from {NetcdfVersion.__module__} import {NetcdfVersion.__name__}
from {QuantileInterpolation.__module__} import {QuantileInterpolation.__name__}
from {build_threshold.__module__} import {build_threshold.__name__}
from {UserIndexDict.__module__} import {UserIndexDict.__name__}

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
    pop_args.append("save_percentile")
    pop_args.append("window_width")
    # Pop unnecessary args
    pop_args.append("callback")
    pop_args.append("callback_percentage_start_value")
    pop_args.append("callback_percentage_total")
    pop_args.append("index_name")
    pop_args.append("threshold")
    # Pop manually added args
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
    pop_args.append("save_percentile")
    pop_args.append("window_width")
    # Pop unnecessary args
    pop_args.append("user_index")
    pop_args.append("callback")
    pop_args.append("callback_percentage_start_value")
    pop_args.append("callback_percentage_total")
    # index_name -> specified with function name
    pop_args.append("index_name")
    # threshold;
    # popped because not configurable on StandardIndices
    # (ECAD requires specific thresholds)
    pop_args.append("threshold")
    # out_unit;
    # popped because not configurable on StandardIndices
    # (ECAD requires specific untis)
    pop_args.append("out_unit")
    # doy_window_width -> doy per window;
    # popped because not configurable on StandardIndices
    # (ECAD requires 5)
    pop_args.append("doy_window_width")
    # rolling_window_width; popped because no standard index rely on rolling window
    pop_args.append("rolling_window_width")
    # min_spell_length
    # -> min spell length to be taken into account for `sum_of_spell_length` indices;
    # popped because not configurable on StandardIndices (ECAD requires 6)
    pop_args.append("min_spell_length")
    # pop not implemented yet args
    pop_args.append("sampling_method")

    qualifiers = [] if index.qualifiers is None else index.qualifiers
    is_per_based = QUANTILE_BASED in qualifiers
    if not is_per_based:
        for arg in QUANTILE_INDEX_FIELDS:
            pop_args.append(arg)
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
    if isinstance(index.threshold, (str, Threshold)):
        fun_call_args += f",\n{TAB}{TAB}threshold={format_thresh(index.threshold)}"
    elif isinstance(index.threshold, (list, tuple)):
        fun_call_args += f",\n{TAB}{TAB}threshold=["
        for t in index.threshold:
            fun_call_args += format_thresh(t) + ","
        fun_call_args += "]"
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
    args_declaration = list(re.compile(r"\n\s{4}\w+.*: .*").finditer(index_docstring))
    for arg in args:
        for i in range(0, len(args_declaration) - 2):
            if args_declaration[i].group().strip().startswith(arg):
                result += index_docstring[
                    args_declaration[i].start() : args_declaration[i + 1].start()
                ]
        if args_declaration[-1].group().strip().startswith(arg):
            # Add everything after the last argument
            result += index_docstring[args_declaration[-1].start() :]
    return result


def format_thresh(t: str | Threshold) -> str:
    params = {}
    if isinstance(t, str):
        t = build_threshold(t)
    params["query"] = f'"{t.initial_query}"'
    if isinstance(t, PercentileThreshold):
        params["doy_window_width"] = t.doy_window_width
        params["only_leap_years"] = "only_leap_years"
        params["interpolation"] = "interpolation"
        params["reference_period"] = "base_period_time_range"
    if t.threshold_min_value is not None:
        params["threshold_min_value"] = f'"{t.threshold_min_value}"'
    acc = f"{build_threshold.__name__}("
    for k, v in params.items():
        acc += f"{k}={v},\n"
    acc += ")"
    return acc


def generate_doc(doc_path):
    with open(doc_path) as f:
        content = "".join(f.readlines())
        replace_start_index = (
            content.find(DOC_START_PLACEHOLDER) + len(DOC_START_PLACEHOLDER) + 1
        )
        replace_end_index = content.find(DOC_END_PLACEHOLDER)
    with open(doc_path, "w") as f:
        replacing_content = ""
        replacing_content += "\n".join(
            list(
                map(
                    lambda x: f"{TAB}{TAB}{x.short_name.lower()}",
                    EcadIndexRegistry.values(),
                )
            )
        )
        replacing_content += f"\n{TAB}{TAB}custom_index\n\n"
        replaced_centent = content[replace_start_index:replace_end_index]
        res = content.replace(replaced_centent, replacing_content)
        f.write(res)


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_PATH
    generate_api(file_path)
    generate_doc(PATH_TO_DOC_FILE)

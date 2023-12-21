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

import copy
import inspect
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import icclim
from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.generic_indices.generic_indicators import (
    GenericIndicator,
    GenericIndicatorRegistry,
)
from icclim.generic_indices.threshold import (
    PercentileThreshold,
    Threshold,
    build_threshold,
)
from icclim.icclim_logger import Verbosity
from icclim.models.constants import QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from icclim.models.frequency import Frequency
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.user_index_dict import UserIndexDict

if TYPE_CHECKING:
    from icclim.models.standard_index import StandardIndex


QUANTILE_INDEX_FIELDS = [
    "base_period_time_range",
    "only_leap_years",
    "interpolation",
    "save_thresholds",
]

NON_REFERENCE_FIELDS = [
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

DEFAULT_OUTPUT_PATH = Path(__file__).parent / "pouet.py"
PATH_TO_ECAD_DOC_FILE = (
    Path(__file__).parent / "../doc/source/references" / "ecad_functions_api.rst"
)
PATH_TO_GENERIC_DOC_FILE = (
    Path(__file__).parent / "../doc/source/references" / "generic_functions_api.rst"
)
DOC_START_PLACEHOLDER = ".. Generated API comment:Begin\n"
DOC_END_PLACEHOLDER = f"{TAB}{TAB}.. Generated API comment:End"
MODULE_HEADER = f'''
# ruff: noqa: A001
"""
This module has been auto-generated.
To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
This module exposes each climate index as individual functions for convenience.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import icclim
from {Threshold.__module__} import {Threshold.__name__}, {build_threshold.__name__}

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence

    from xarray.core.dataset import Dataset

    from {Verbosity.__module__} import {Verbosity.__name__}
    from icclim.icclim_types import FrequencyLike, InFileLike, SamplingMethodLike
    from {Frequency.__module__} import {Frequency.__name__}
    from {NetcdfVersion.__module__} import {NetcdfVersion.__name__}
    from {QuantileInterpolation.__module__} import {QuantileInterpolation.__name__}
    from {UserIndexDict.__module__} import {UserIndexDict.__name__}

'''

DEPRECATED_ARGS = [
    "indice_name",
    "user_indice",
    "transfer_limit_Mbytes",
    "save_percentile",
    "window_width",
]
UNNECESSARY_ARGS = [
    "callback",
    "callback_percentage_start_value",
    "callback_percentage_total",
    "index_name",
    "user_index",
]

ECAD_POP_ARGS = (
    DEPRECATED_ARGS
    + UNNECESSARY_ARGS
    + [
        "threshold",
        "out_unit",
        "doy_window_width",
        "min_spell_length",
        # rolling_window_width; popped because no standard index rely on rolling window
        "rolling_window_width",
        # pop not implemented yet sampling_method
        "sampling_method",
    ]
)

GENERIC_POP_ARGS = (
    DEPRECATED_ARGS
    + UNNECESSARY_ARGS
    + [
        # These are configured at `threshold` level
        "doy_window_width",
        "base_period_time_range",
        "only_leap_years",
        "interpolation",
    ]
)


def _generate_api(path: Path) -> None:
    ecad_indices = EcadIndexRegistry.values()
    generic_indices = GenericIndicatorRegistry.values()
    with Path.open(path, "w") as f:
        acc = MODULE_HEADER
        acc += "__all__ = [\n"
        ecad_index_names = [x.short_name for x in ecad_indices]
        generic_index_names = [x.name for x in generic_indices]
        names = generic_index_names + ecad_index_names + ["custom_index"]
        formatted_names = (f'{TAB}"{x.lower()}"' for x in names)
        acc += ",\n".join(formatted_names)
        acc += ",\n]\n\n"
        standard_indices = [
            _get_standard_index_declaration(index) for index in ecad_indices
        ]
        custom_index = [_get_user_index_declaration()]
        generic_indices = [
            _get_generic_index_declaration(generic_index)
            for generic_index in generic_indices
        ]
        indices_to_write = generic_indices + standard_indices + custom_index
        acc += "\n".join(indices_to_write)
        f.write(acc)


def _get_user_index_declaration() -> str:
    icclim_index_args = dict(inspect.signature(icclim.index).parameters)
    pop_args = DEPRECATED_ARGS + UNNECESSARY_ARGS
    # User indices have their own way of writing thresholds
    pop_args.append("threshold")
    for pop_arg in pop_args:
        icclim_index_args.pop(pop_arg)
    fun_signature_args = _build_fun_signature_args(icclim_index_args)
    args_docs = _get_params_docstring(
        list(icclim_index_args.keys()),
        icclim.index.__doc__,
    )
    common_args = (f"{arg}={arg}" for arg in icclim_index_args)
    formatted_common_args = f",\n{TAB}{TAB}".join(common_args)
    return f"""
def custom_index(
        user_index: UserIndexDict,
        {fun_signature_args},
) -> Dataset:
        \"\"\"
        Compute custom indices using simple operators.

        Use the `user_index` parameter to describe how the index should be computed.
        You can find some examples in icclim documentation at :ref:`custom_indices`
        {args_docs}
        {END_NOTE}
        \"\"\"
        return icclim.index(
            user_index=user_index,
            {formatted_common_args}
        )
    """


def _build_fun_signature_args(args: dict) -> str:
    return f",\n{TAB}".join(map(_get_parameter_declaration, args.values()))


def _get_generic_index_declaration(index: GenericIndicator) -> str:
    pop_args = copy.copy(GENERIC_POP_ARGS)
    if index is not GenericIndicatorRegistry.SumOfSpellLengths:
        pop_args += ["min_spell_length"]
    if index is not GenericIndicatorRegistry.DifferenceOfMeans:
        pop_args += ["sampling_method"]
    if index not in [
        GenericIndicatorRegistry.MaxOfRollingSum,
        GenericIndicatorRegistry.MinOfRollingSum,
        GenericIndicatorRegistry.MaxOfRollingAverage,
        GenericIndicatorRegistry.MinOfRollingAverage,
    ]:
        pop_args += ["rolling_window_width"]
    index_args = _get_arguments(pop_args)
    fun_signature_args = _build_fun_signature_args(index_args)
    args_docs = _get_params_docstring(list(index_args.keys()), icclim.index.__doc__)
    args = (f"{arg}={arg}" for arg in index_args)
    formatted_args = f",\n{TAB}{TAB}".join(list(args))
    return f"""
def {index.name.lower()}(
    {fun_signature_args},
    ) -> Dataset:
    \"\"\"
    {index.definition}

    {args_docs}
    {END_NOTE}
    \"\"\"
    return icclim.index(
        index_name="{index.name.upper()}",
        {formatted_args},
    )
    """


def _get_standard_index_declaration(index: StandardIndex) -> str:
    if _is_quantile_based(index):
        index_args = _get_arguments(ECAD_POP_ARGS)
    elif _can_have_reference_period(index):
        index_args = _get_arguments(ECAD_POP_ARGS + NON_REFERENCE_FIELDS)
    else:
        index_args = _get_arguments(ECAD_POP_ARGS + QUANTILE_INDEX_FIELDS)
    fun_signature_args = _build_fun_signature_args(index_args)
    args_docs = _get_params_docstring(list(index_args.keys()), icclim.index.__doc__)
    common_args = (f"{arg}={arg}" for arg in index_args)
    args = list(common_args)
    thresh_arg = _get_threshold_argument(index)
    output_unit_arg = _get_output_unit_argument(index)
    if thresh_arg:
        args += [thresh_arg]
    if output_unit_arg:
        args += [output_unit_arg]
    formatted_args = f",\n{TAB}{TAB}".join(args)
    return f"""
def {index.short_name.lower()}(
    {fun_signature_args},
) -> Dataset:
    \"\"\"
    {index.short_name}: {index.definition}
    Source: {index.source}.

    {args_docs}
    {END_NOTE}
    \"\"\"
    return icclim.index(
        index_name="{index.short_name.upper()}",
        {formatted_args},
    )
"""


def _is_quantile_based(index: StandardIndex) -> bool:
    return index.qualifiers is not None and QUANTILE_BASED in index.qualifiers


def _can_have_reference_period(index: StandardIndex) -> bool:
    return index.qualifiers is not None and REFERENCE_PERIOD_INDEX in index.qualifiers


def _get_arguments(pop_args: list[str]) -> dict[str, inspect.Parameter]:
    icclim_index_args = dict(inspect.signature(icclim.index).parameters)
    for pop_arg in pop_args:
        icclim_index_args.pop(pop_arg)
    return icclim_index_args


def _get_output_unit_argument(index: StandardIndex) -> str:
    if index.output_unit is not None:
        return f'out_unit="{index.output_unit}"'
    return ""


def _get_threshold_argument(index: StandardIndex) -> str:
    if isinstance(index.threshold, (str, Threshold)):
        return f"threshold={_format_thresh(index.threshold)}"
    if isinstance(index.threshold, (list, tuple)):
        result = "threshold=["
        for t in index.threshold:
            result += _format_thresh(t) + ","
        result += "]"
        return result
    return ""


def _get_parameter_declaration(param: inspect.Parameter) -> str:
    annotation = param.annotation
    if type(annotation) is type:
        annotation = annotation.__name__
    annotation = annotation.__str__().replace("NoneType", "None")
    annotation = annotation.__str__().replace("xarray.core.dataset.Dataset", "Dataset")
    prefix = f"{param.name}: {annotation}"
    if param.default is inspect.Parameter.empty:
        return prefix
    default = param.default
    if isinstance(default, str):
        default = f'"{default.__str__()}"'
    return f"{prefix} = {default}"


def _get_params_docstring(args: list[str], index_docstring: str) -> str:
    result = f"Parameters\n{TAB}----------\n"
    # regex to find `\n   toto: str` or similar declaration of argument
    regex = re.compile(r"\n\s{4}\w+.*: .*")
    args_declaration = list(regex.finditer(index_docstring))
    for arg in args:
        for i in range(len(args_declaration) - 2):
            # `-2` because we have specific handler for the last argument
            if args_declaration[i].group().strip().startswith(arg):
                result += index_docstring[
                    args_declaration[i].start() : args_declaration[i + 1].start()
                ]
        if args_declaration[-1].group().strip().startswith(arg):
            # Add everything after the last argument
            result += index_docstring[args_declaration[-1].start() :]
    return result


def _format_thresh(t: str | Threshold) -> str:
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
    acc = f"{build_threshold.__name__}(\n"
    for k, v in params.items():
        acc += f"{TAB}{TAB}{TAB}{k}={v},\n"
    acc += f"{TAB}{TAB})"
    return acc


def _generate_doc(doc_path: Path, replacing_content: str) -> None:
    with Path.open(doc_path) as f:
        content = "".join(f.readlines())
        replace_start_index = (
            content.find(DOC_START_PLACEHOLDER) + len(DOC_START_PLACEHOLDER) + 1
        )
        replace_end_index = content.find(DOC_END_PLACEHOLDER)
    with Path.open(doc_path, "w") as f:
        replaced_content = content[replace_start_index:replace_end_index]
        res = content.replace(replaced_content, replacing_content)
        f.write(res)


def _get_ecad_doc() -> str:
    names = (x.short_name for x in EcadIndexRegistry.values())
    names = [*list(names), "custom_index"]
    formatted_names = (f"{TAB}{TAB}{x.lower()}" for x in names)
    replacing_content = ""
    replacing_content += "\n".join(formatted_names)
    replacing_content += "\n\n"
    return replacing_content


def _get_generic_doc() -> str:
    names = (x.name for x in GenericIndicatorRegistry.values())
    formatted_names = (f"{TAB}{TAB}{x.lower()}" for x in names)
    replacing_content = ""
    replacing_content += "\n".join(formatted_names)
    replacing_content += "\n\n"
    return replacing_content


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_PATH
    _generate_api(file_path)
    _generate_doc(PATH_TO_ECAD_DOC_FILE, _get_ecad_doc())
    _generate_doc(PATH_TO_GENERIC_DOC_FILE, _get_generic_doc())

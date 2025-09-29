"""
Icclim indices extractor.

It creates a new python module which wraps each icclim index as a function.
Each generated function's signature is consistent with icclim.index signature but,
all the unused parameters are trimmed from the signature.
"""

from __future__ import annotations

import copy
import inspect
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

# import icclim
from docstring_parser import Docstring, DocstringParam, DocstringStyle, compose, parse

from icclim._core.constants import NEEDS_NORMAL, QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.model.threshold import Threshold
from icclim.threshold.factory import build_threshold

if TYPE_CHECKING:
    from icclim._core.generic.indicator import GenericIndicator
    from icclim._core.model.registry import Registry
    from icclim._core.model.standard_index import StandardIndex

# -----------------------
# Constants for argument trimming
# -----------------------
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

RELATIVE_ROOT = Path(__file__).parent.parent
DEFAULT_OUTPUT_PATH = RELATIVE_ROOT / "src/icclim/_generated"
PATH_TO_DCSC_DOC_FILE = (
    RELATIVE_ROOT / "doc/source/references/api/icclim/dcsc/index.rst"
)
PATH_TO_ECAD_DOC_FILE = (
    RELATIVE_ROOT / "doc/source/references/api/icclim/ecad/index.rst"
)
PATH_TO_GENERIC_DOC_FILE = (
    RELATIVE_ROOT / "doc/source/references/api/icclim/generic/index.rst"
)
DOC_START_PLACEHOLDER = ".. Generated API comment:Begin\n"
DOC_END_PLACEHOLDER = ".. Generated API comment:End"

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

STANDARD_INDEX_POP_ARGS = (
    DEPRECATED_ARGS
    + UNNECESSARY_ARGS
    + [
        "threshold",
        "out_unit",
        "doy_window_width",
        "min_spell_length",
        "rolling_window_width",
        "sampling_method",
    ]
)

GENERIC_POP_ARGS = (
    DEPRECATED_ARGS
    + UNNECESSARY_ARGS
    + [
        "doy_window_width",
        "base_period_time_range",
        "only_leap_years",
        "interpolation",
    ]
)

NORMAL_INDEX_POP_ARGS = (
    STANDARD_INDEX_POP_ARGS + NON_REFERENCE_FIELDS + ["base_period_time_range"]
)


# -----------------------
# Main entry point
# -----------------------
def main() -> None:
    dir_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_PATH
    dir_path = Path(dir_path)

    _generate_ecad_api(dir_path / "_ecad.py")
    _generate_dcsc_api(dir_path / "_dcsc.py")
    _generate_generic_api(dir_path / "_generic.py")

    _generate_doc(PATH_TO_ECAD_DOC_FILE, _get_ecad_doc())
    _generate_doc(PATH_TO_DCSC_DOC_FILE, _get_dcsc_doc())
    _generate_doc(PATH_TO_GENERIC_DOC_FILE, _get_generic_doc())


# -----------------------
# API generation functions
# -----------------------
def _generate_dcsc_api(file_path: Path) -> None:
    from icclim.dcsc.registry import DcscIndexRegistry

    dcsc_indices = DcscIndexRegistry.values()
    dcsc_index_names = [x.short_name for x in dcsc_indices]
    dcsc_indices = [
        _get_standard_index_declaration(index, DcscIndexRegistry)
        for index in dcsc_indices
    ]
    acc = _build_module_header("dcsc")
    acc += _build__all__(dcsc_index_names)
    acc += "\n".join(dcsc_indices)
    with Path.open(file_path, "w") as f:
        f.write(acc)


def _generate_generic_api(file_path: Path) -> None:
    from icclim.generic.registry import GenericIndicatorRegistry

    generic_indices = GenericIndicatorRegistry.values()
    generic_index_names = [x.name for x in generic_indices]
    names = [*generic_index_names, "custom_index"]
    custom_index = [_get_user_index_declaration()]
    generic_indices = [
        _get_generic_index_declaration(generic_index)
        for generic_index in generic_indices
    ]
    indices_to_write = generic_indices + custom_index
    acc = _build_module_header("generic")
    acc += _build__all__(names)
    acc += "\n".join(indices_to_write)
    with Path.open(file_path, "w") as f:
        f.write(acc)


def _generate_ecad_api(file_path: Path) -> None:
    from icclim.ecad.registry import EcadIndexRegistry

    ecad_indices = EcadIndexRegistry.values()
    ecad_index_names = [x.short_name for x in ecad_indices]
    ecad_indices = [
        _get_standard_index_declaration(index, EcadIndexRegistry)
        for index in ecad_indices
    ]
    acc = _build_module_header("ECAD")
    acc += _build__all__(ecad_index_names)
    acc += "\n".join(ecad_indices)
    with Path.open(file_path, "w") as f:
        f.write(acc)


# -----------------------
# Helper functions
# -----------------------
def _get_user_index_declaration() -> str:
    from icclim import index as icclim_index

    icclim_index_args = dict(inspect.signature(icclim_index).parameters)
    pop_args = DEPRECATED_ARGS + UNNECESSARY_ARGS
    pop_args.append("threshold")
    for pop_arg in pop_args:
        icclim_index_args.pop(pop_arg)
    fun_signature_args = _build_fun_signature_args(icclim_index_args)
    args_docs = _get_params_docstring(
        list(icclim_index_args.keys()), icclim_index.__doc__
    )
    common_args = (f"{arg}={arg}" for arg in icclim_index_args)
    formatted_common_args = f",\n{TAB}{TAB}".join(common_args)
    return f"""
def custom_index(
        user_index: UserIndexDict,
        {fun_signature_args},
) -> Dataset:
    \"\"\"Compute custom indices using simple operators.

    Use the `user_index` parameter to describe how the index should be computed.
    You can find some examples in icclim documentation at :ref:`custom indices`

    {args_docs}
    {END_NOTE}
    \"\"\"
    import icclim
    return icclim.index(
        user_index=user_index,
        {formatted_common_args}
    )
    """


def _get_standard_index_declaration(index: StandardIndex, registry: Registry) -> str:
    if _is_compared_to_normal(index):
        return _get_normal_based_declaration(index, registry)
    return _get_typical_index_declaration(index, registry)


def _get_typical_index_declaration(index: StandardIndex, registry: Registry) -> str:
    from icclim import index as icclim_index

    if _is_quantile_based(index):
        index_args = _get_arguments(STANDARD_INDEX_POP_ARGS)
    elif _can_have_reference_period(index):
        index_args = _get_arguments(STANDARD_INDEX_POP_ARGS + NON_REFERENCE_FIELDS)
    else:
        index_args = _get_arguments(STANDARD_INDEX_POP_ARGS + QUANTILE_INDEX_FIELDS)
    fun_signature_args = _build_fun_signature_args(index_args)
    doc_string = icclim_index.__doc__ or ""
    args_docs = _get_params_docstring(list(index_args.keys()), doc_string)
    args = [f"{arg}={arg}" for arg in index_args]
    thresh_arg = _get_threshold_argument(index)
    output_unit_arg = _get_output_unit_argument(index)
    if thresh_arg:
        args += [thresh_arg]
    if output_unit_arg:
        args += [output_unit_arg]
    formatted_args = f",\n{TAB}{TAB}".join(args)
    catalog = registry.catalog()
    index_name_arg = next(
        k for k in catalog if catalog[k].short_name == index.short_name
    )
    return f"""
def {index.short_name.lower()}(
    {fun_signature_args},
) -> Dataset:
    \"\"\"{index.definition}

    {index.short_name}: {index.definition}
    Source: {index.source}.

    {args_docs}
    {END_NOTE}
    \"\"\"  # noqa: D401
    import icclim
    return icclim.index(
        index_name={registry.__name__}.{index_name_arg},
        {formatted_args},
    )
"""


def _get_normal_based_declaration(index: StandardIndex, registry: Registry) -> str:
    from icclim import index as icclim_index

    def _normal_index_placeholder(normal, normal_var_name=None):
        """
        Parameters
        ----------
        normal: Union[str, Sequence[str], Dataset, DataArray]
            The normal to be compared to.
            Typically, the expected normal dataset should have one value per `lat, lon` couple.
            Can be a path or a list of paths to netCDF datasets or a xarray Dataset or DataArray.
        normal_var_name: str | None, optional
            The name of the normal variable.
            If missing, icclim will try to guess which variable must be used in the `normal` dataset.
        """
        raise NotImplementedError

    # Build index arguments
    index_args = _get_arguments(NORMAL_INDEX_POP_ARGS)
    normal_sig = inspect.signature(_normal_index_placeholder)
    passed_to_index_args = [f"{arg}={arg}" for arg in index_args]
    index_args["normal"] = normal_sig.parameters["normal"]
    index_args["normal_var_name"] = normal_sig.parameters["normal_var_name"]

    # Build function signature
    fun_signature_args = _build_fun_signature_args(index_args)

    # Combine docstrings
    base_doc_string = icclim_index.__doc__ or ""
    normal_doc_params = parse(_normal_index_placeholder.__doc__).params
    args_docs = _get_params_docstring(
        list(index_args.keys()), base_doc_string, normal_doc_params
    )

    # Add output unit argument if exists
    output_unit_arg = _get_output_unit_argument(index)
    if output_unit_arg:
        passed_to_index_args += [output_unit_arg]
    formatted_args = f",\n{TAB}{TAB}".join(passed_to_index_args)

    # Find catalog key
    catalog = registry.catalog()
    index_name_arg = next(
        k for k in catalog if catalog[k].short_name == index.short_name
    )

    return f"""
def {index.short_name.lower()}(
    {fun_signature_args},
) -> Dataset:
    \"\"\"{index.definition}

    {index.short_name}: {index.definition}
    Source: {index.source}.

    {args_docs}
    {END_NOTE}
    \"\"\"
    standard_index = DcscIndexRegistry.{index.short_name}
    normal_da = get_dataarray_from_dataset(
        normal_var_name, normal, standard_index.input_variables[0]
    )
    threshold = standard_index.threshold
    threshold.prepare(normal_da)
    import icclim
    return icclim.index(
        index_name={registry.__name__}.{index_name_arg},
        {formatted_args},
    )
"""


# -----------------------
# Common helper functions
# -----------------------
def _is_compared_to_normal(index) -> bool:
    return index.qualifiers is not None and NEEDS_NORMAL in index.qualifiers


def _is_quantile_based(index) -> bool:
    return index.qualifiers is not None and QUANTILE_BASED in index.qualifiers


def _can_have_reference_period(index) -> bool:
    return index.qualifiers is not None and REFERENCE_PERIOD_INDEX in index.qualifiers


def _get_arguments(pop_args: list[str]) -> dict[str, inspect.Parameter]:
    from icclim import index as icclim_index

    icclim_index_args = dict(inspect.signature(icclim_index).parameters)
    for pop_arg in pop_args:
        icclim_index_args.pop(pop_arg, None)
    return icclim_index_args


def _get_output_unit_argument(index) -> str:
    if index.output_unit is not None:
        return f'out_unit="{index.output_unit}"'
    return ""


def _get_threshold_argument(index) -> str:
    if isinstance(index.threshold, (str, Threshold)):
        return f"threshold={_format_thresh(index.threshold)}"
    if isinstance(index.threshold, (list, tuple)):
        result = "threshold=["
        for t in index.threshold:
            result += _format_thresh(t) + ","
        result += "]"
        return result
    return ""


def _get_generic_index_declaration(index: GenericIndicator) -> str:
    """
    Generate a string representing a function declaration for a GenericIndicator.

    Parameters
    ----------
    index : GenericIndicator
        The indicator to generate the function for.

    Returns
    -------
    str
        Python code defining a function for the given generic index.
    """
    from icclim import index as icclim_index
    from icclim.generic.registry import GenericIndicatorRegistry

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
    args_docs = _get_params_docstring(list(index_args.keys()), icclim_index.__doc__)
    args = (f"{arg}={arg}" for arg in index_args)
    formatted_args = f",\n{TAB}{TAB}".join(list(args))
    catalog = GenericIndicatorRegistry.catalog()
    index_name_arg = next(k for k in catalog if catalog[k].name == index.name)

    return f"""
def {index.name.lower()}(
    {fun_signature_args},
    ) -> Dataset:
    \"\"\"{index.definition}

    {index.name}: {index.definition}

    {args_docs}
    {END_NOTE}
    \"\"\"
    import icclim
    return icclim.index(
        index_name={GenericIndicatorRegistry.__name__}.{index_name_arg},
        {formatted_args},
    )
    """


def _build_fun_signature_args(args: dict[str, inspect.Parameter]) -> str:
    sorted_params = sorted(
        args.values(), key=lambda y: y.default is not inspect.Parameter.empty
    )
    return f",\n{TAB}".join(map(_get_parameter_declaration, sorted_params))


def _get_parameter_declaration(param: inspect.Parameter) -> str:
    annotation = param.annotation
    if type(annotation) is type:
        annotation = annotation.__name__
    annotation = str(annotation).replace("NoneType", "None")
    annotation = annotation.replace("xarray.core.dataset.Dataset", "Dataset")
    prefix = f"{param.name}: {annotation}"
    if param.default is inspect.Parameter.empty:
        return prefix
    default = param.default
    if isinstance(default, str):
        default = f'"{default}"'
    return f"{prefix} = {default}"


def _get_params_docstring(
    args: list[str],
    index_docstring: str,
    params_to_add: list[DocstringParam] | None = None,
) -> str:
    parsed = parse(index_docstring)
    filtered = [p for p in parsed.params if p.arg_name in args]
    if params_to_add is not None:
        filtered += params_to_add
    parsed.long_description = ""
    param_str = Docstring(style=DocstringStyle.NUMPYDOC)
    param_str.meta = filtered
    param_str = compose(param_str)
    return f"\n{TAB}".join(param_str.splitlines())


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
    if getattr(t, "threshold_min_value", None) is not None:
        params["threshold_min_value"] = f'"{t.threshold_min_value}"'
    acc = f"{build_threshold.__name__}(\n"
    for k, v in params.items():
        acc += f"{TAB}{TAB}{TAB}{k}={v},\n"
    acc += f"{TAB}{TAB})"
    return acc


def _generate_doc(doc_path: Path, replacing_content: str) -> None:
    with Path.open(doc_path) as f:
        content = "".join(f.readlines())
    replace_start_index = content.find(DOC_START_PLACEHOLDER) + len(
        DOC_START_PLACEHOLDER
    )
    replace_end_index = content.find(DOC_END_PLACEHOLDER)
    replaced_content = content[replace_start_index:replace_end_index]
    res = content.replace(replaced_content, replacing_content)
    with Path.open(doc_path, "w") as f:
        f.write(res)


def _get_ecad_doc() -> str:
    from icclim.ecad.registry import EcadIndexRegistry

    names = [x.short_name for x in EcadIndexRegistry.values()]
    return "\n".join(f"{TAB}{x.lower()}" for x in names) + "\n\n"


def _get_dcsc_doc() -> str:
    from icclim.dcsc.registry import DcscIndexRegistry

    names = [x.short_name for x in DcscIndexRegistry.values()]
    return "\n".join(f"{TAB}{x.lower()}" for x in names) + "\n\n"


def _get_generic_doc() -> str:
    from icclim.generic.registry import GenericIndicatorRegistry

    names = [x.name for x in GenericIndicatorRegistry.values()] + ["custom_index"]
    return "\n".join(f"{TAB}{x.lower()}" for x in names) + "\n\n"


def _build_module_header(kind: str) -> str:
    header = f'''\
# ruff: noqa: A001, E501, N803
"""
icclim's API for {kind} indices.

This module has been auto-generated.
To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
This module exposes each climate index as individual functions for convenience.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xarray import Dataset, DataArray
from icclim._core.input_parsing import get_dataarray_from_dataset
from icclim.threshold.factory import build_threshold
'''

    # Registry import depending on module type
    if kind.lower() == "dcsc":
        header += "from icclim.dcsc.registry import DcscIndexRegistry\n"
    elif kind.lower() == "ecad":
        header += "from icclim.ecad.registry import EcadIndexRegistry\n"
    elif kind.lower() == "generic":
        header += "from icclim.generic.registry import GenericIndicatorRegistry\n"

    # TYPE_CHECKING imports for type hints
    header += """
if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence

    from icclim.logger import Verbosity
    from icclim._core.model.icclim_types import FrequencyLike, InFileLike, SamplingMethodLike
    from icclim.frequency import Frequency
    from icclim._core.model.netcdf_version import NetcdfVersion
    from icclim._core.model.quantile_interpolation import QuantileInterpolation
    from icclim._core.legacy.user_index.model import UserIndexDict
    from icclim._core.model.threshold import Threshold
"""

    return header


def _build__all__(index_names: Sequence[str]) -> str:
    formatted_names = (f'{TAB}"{x.lower()}"' for x in index_names)
    prefix = "__all__ = [\n"
    names = ",\n".join(formatted_names)
    suffix = ",\n]\n\n"
    return f"{prefix}{names}{suffix}"


if __name__ == "__main__":
    main()

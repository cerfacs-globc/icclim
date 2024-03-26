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
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import icclim
from docstring_parser import Docstring, DocstringParam, DocstringStyle, compose, parse
from icclim._core.constants import NEEDS_NORMAL, QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.input_parsing import get_dataarray_from_dataset
from icclim._core.legacy.user_index.model import UserIndexDict
from icclim._core.model.icclim_types import FrequencyLike
from icclim._core.model.netcdf_version import NetcdfVersion
from icclim._core.model.quantile_interpolation import QuantileInterpolation
from icclim._core.model.threshold import Threshold
from icclim.dcsc.registry import DcscIndexRegistry
from icclim.ecad.registry import EcadIndexRegistry
from icclim.frequency import Frequency
from icclim.generic.registry import GenericIndicatorRegistry
from icclim.logger import Verbosity
from icclim.threshold.factory import build_threshold

if TYPE_CHECKING:
    from collections.abc import Sequence

    from icclim._core.generic.indicator import GenericIndicator
    from icclim._core.model.registry import Registry
    from icclim._core.model.standard_index import StandardIndex
    from xarray import DataArray, Dataset


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
    RELATIVE_ROOT / "doc/source/references/api/icclim/dcsc" / "index.rst"
)
PATH_TO_ECAD_DOC_FILE = (
    RELATIVE_ROOT / "doc/source/references/api/icclim/ecad" / "index.rst"
)
PATH_TO_GENERIC_DOC_FILE = (
    RELATIVE_ROOT / "doc/source/references/api/icclim/generic" / "index.rst"
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

NORMAL_INDEX_POP_ARGS = (
    STANDARD_INDEX_POP_ARGS + NON_REFERENCE_FIELDS + ["base_period_time_range"]
)


def main() -> None:
    """
    Generate icclim's API functions from the Indicators registries.

    Notes
    -----
    The generated functions are written in the `_generated` directory.
    Each registry produce its own module.
    For now the following registries are supported: ECAD, DCSC and Generic.
    Additionally, the user can define custom indices using the `custom_index` function
    exposed in the generic module.
    """
    dir_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_PATH
    dir_path = Path(dir_path)
    _generate_ecad_api(dir_path / "_ecad.py")
    _generate_dcsc_api(dir_path / "_dcsc.py")
    _generate_generic_api(dir_path / "_generic.py")
    _generate_doc(PATH_TO_ECAD_DOC_FILE, _get_ecad_doc())
    _generate_doc(PATH_TO_DCSC_DOC_FILE, _get_dcsc_doc())
    _generate_doc(PATH_TO_GENERIC_DOC_FILE, _get_generic_doc())


def _generate_dcsc_api(file_path: Path) -> None:
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
    \"\"\"Compute custom indices using simple operators.

    Use the `user_index` parameter to describe how the index should be computed.
    You can find some examples in icclim documentation at :ref:`custom indices`

    {args_docs}
    {END_NOTE}
    \"\"\"
    return icclim.index(
        user_index=user_index,
        {formatted_common_args}
    )
    """


def _build_fun_signature_args(args: dict[str, inspect.Parameter]) -> str:
    sorted_params = sorted(
        args.values(), key=lambda y: y.default is not inspect.Parameter.empty
    )
    return f",\n{TAB}".join(map(_get_parameter_declaration, sorted_params))


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
    \"\"\"  # noqa: D401
    return icclim.index(
        index_name={GenericIndicatorRegistry.__name__}.{index_name_arg},
        {formatted_args},
    )
    """


def _normal_index_placeholder(  # noqa: ANN202
    normal: str | Sequence[str] | Dataset | DataArray,  # noqa: ARG001
    normal_var_name: str | None = None,  # noqa: ARG001
):
    """
    Parameters
    ----------
    normal: Union[str, Sequence[str], Dataset, DataArray, None]
        The normal to be compared to.
        Typically, the expected normal dataset should have one value per `lat, lon`
        couple.
        Can be a path or a list of paths to netCDF datasets or a xarray Dataset or
        DataArray.
    normal_var_name: str | None, optional
        The name of the normal variable.
        If missing, icclim will try to guess which variable must be used in the
        `normal` dataset.
        Ignored if ``normal`` is a
    """  # noqa: D205 (placeholder function used for generating docstrings)
    raise NotImplementedError


def _get_normal_based_declaration(index: StandardIndex, registry: Registry) -> str:
    index_args = _get_arguments(NORMAL_INDEX_POP_ARGS)
    normal_sig = inspect.signature(_normal_index_placeholder)
    passed_to_index_args = [f"{arg}={arg}" for arg in index_args]
    index_args["normal"] = normal_sig.parameters["normal"]
    index_args["normal_var_name"] = normal_sig.parameters["normal_var_name"]
    normal_doc = _normal_index_placeholder.__doc__ or ""
    params_to_add = parse(normal_doc).params
    fun_signature_args = _build_fun_signature_args(index_args)
    base_doc_string = icclim.index.__doc__ or ""
    args_docs = _get_params_docstring(
        list(index_args.keys()), base_doc_string, params_to_add
    )
    output_unit_arg = _get_output_unit_argument(index)
    if output_unit_arg:
        passed_to_index_args += [output_unit_arg]
    formatted_args = f",\n{TAB}{TAB}".join(passed_to_index_args)
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
    return icclim.index(
        index_name={registry.__name__}.{index_name_arg },
        {formatted_args},
    )
"""


def _get_typical_index_declaration(index: StandardIndex, registry: Registry) -> str:
    if _is_quantile_based(index):
        index_args = _get_arguments(STANDARD_INDEX_POP_ARGS)
    elif _can_have_reference_period(index):
        index_args = _get_arguments(STANDARD_INDEX_POP_ARGS + NON_REFERENCE_FIELDS)
    else:
        index_args = _get_arguments(STANDARD_INDEX_POP_ARGS + QUANTILE_INDEX_FIELDS)
    fun_signature_args = _build_fun_signature_args(index_args)
    doc_string = icclim.index.__doc__
    if doc_string is None:
        msg = "icclim::index doc string does not exist."
        raise ValueError(msg)
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
    return icclim.index(
        index_name={registry.__name__}.{index_name_arg },
        {formatted_args},
    )
"""


def _get_standard_index_declaration(index: StandardIndex, registry: Registry) -> str:
    if _is_compared_to_normal(index):
        return _get_normal_based_declaration(index, registry)
    return _get_typical_index_declaration(index, registry)


def _is_compared_to_normal(index: StandardIndex) -> bool:
    return index.qualifiers is not None and NEEDS_NORMAL in index.qualifiers


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
    replaced_content = content[replace_start_index:replace_end_index]
    res = content.replace(replaced_content, replacing_content)
    with Path.open(doc_path, "w") as f:
        f.write(res)


def _get_ecad_doc() -> str:
    names = [x.short_name for x in EcadIndexRegistry.values()]
    formatted_names = (f"{TAB} {x.lower()}" for x in names)
    replacing_content = ""
    replacing_content += "\n".join(formatted_names)
    replacing_content += "\n\n"
    return replacing_content


def _get_dcsc_doc() -> str:
    names = (x.short_name for x in DcscIndexRegistry.values())
    formatted_names = (f"{TAB} {x.lower()}" for x in names)
    replacing_content = ""
    replacing_content += "\n".join(formatted_names)
    replacing_content += "\n\n"
    return replacing_content


def _get_generic_doc() -> str:
    names = (x.name for x in GenericIndicatorRegistry.values())
    names = [*list(names), "custom_index"]
    formatted_names = (f"{TAB}{x.lower()}" for x in names)
    replacing_content = ""
    replacing_content += "\n".join(formatted_names)
    replacing_content += "\n\n"
    return replacing_content


def _build_module_header(kind: str) -> str:
    return f'''
# ruff: noqa: A001, E501, N803
"""
icclim's API for {kind} indices.

This module has been auto-generated.
To modify these, edit the extractor tool in `tools/extract-icclim-funs.py`.
This module exposes each climate index as individual functions for convenience.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import icclim
from {EcadIndexRegistry.__module__} import {EcadIndexRegistry.__name__}
from {DcscIndexRegistry.__module__} import {DcscIndexRegistry.__name__}
from {GenericIndicatorRegistry.__module__} import {GenericIndicatorRegistry.__name__}
from {build_threshold.__module__} import {build_threshold.__name__}

from {get_dataarray_from_dataset.__module__} import (
     {get_dataarray_from_dataset.__name__}
     )

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence

    from xarray import Dataset
    from xarray import DataArray

    from {Verbosity.__module__} import {Verbosity.__name__}
    from {FrequencyLike.__module__} import (
         FrequencyLike, InFileLike, SamplingMethodLike
        )

    from {Frequency.__module__} import {Frequency.__name__}
    from {NetcdfVersion.__module__} import {NetcdfVersion.__name__}
    from {QuantileInterpolation.__module__} import {QuantileInterpolation.__name__}
    from {UserIndexDict.__module__} import {UserIndexDict.__name__}
    from {Threshold.__module__} import {Threshold.__name__}

'''


def _build__all__(index_names: Sequence[str]) -> str:
    formatted_names = (f'{TAB}"{x.lower()}"' for x in index_names)
    prefix = "__all__ = [\n"
    names = ",\n".join(formatted_names)
    suffix = ",\n]\n\n"
    return f"{prefix}{names}{suffix}"


if __name__ == "__main__":
    main()

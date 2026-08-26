"""Helpers for writing output provenance sidecars."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import platform
import shlex
import socket
import subprocess
import sys
import warnings
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any

from icclim._core.generic.bootstrap_capability import (
    BootstrapExecutionKind,
    BootstrapThresholdKind,
    classify_generic_indicator_bootstrap,
    classify_threshold_kind,
)
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold

if TYPE_CHECKING:
    from xarray import Dataset

    from icclim._core.climate_variable import ClimateVariable
    from icclim._core.model.index_config import IndexConfig
    from icclim._core.model.threshold import Threshold

DEFAULT_MAX_HASH_BYTES = 16 * 1024 * 1024
FILTERED_ENV_VARS = (
    "CONDA_DEFAULT_ENV",
    "VIRTUAL_ENV",
    "SLURM_JOB_ID",
    "SLURM_ARRAY_JOB_ID",
    "SLURM_ARRAY_TASK_ID",
    "OMP_NUM_THREADS",
)


def provenance_sidecar_path(file_path: str | Path) -> Path:
    output_path = Path(file_path)
    return output_path.with_name(f"{output_path.stem}.prov.json")


def build_output_provenance(
    *,
    config: IndexConfig | None,
    result_ds: Dataset,
    out_file: str | Path,
    entrypoint: str,
    user_parameters: dict[str, Any] | None = None,
    resolved_overrides: dict[str, Any] | None = None,
    climate_variables: list[ClimateVariable] | None = None,
    captured_warnings: list[warnings.WarningMessage] | None = None,
) -> dict[str, Any]:
    sidecar_path = provenance_sidecar_path(out_file)
    git_context = collect_git_context()
    effective_climate_variables = (
        config.climate_variables if config is not None else (climate_variables or [])
    )
    return {
        "schema_version": 1,
        "fair4rs_alignment": {
            "goal": (
                "Record enough structured runtime and scientific metadata to"
                " support reuse, reproducibility and later inspection of an"
                " icclim output."
            )
        },
        "run_context": collect_run_context(entrypoint),
        "software": collect_software_context(),
        "git": git_context,
        "inputs": [
            describe_climate_variable(climate_var)
            for climate_var in effective_climate_variables
        ],
        "outputs": describe_output_path(Path(out_file), sidecar_path),
        "user_parameters": _json_ready(user_parameters or {}),
        "resolved_parameters": collect_resolved_parameters(
            config,
            result_ds,
            climate_variables=effective_climate_variables,
            overrides=resolved_overrides or {},
        ),
        "execution": collect_execution_context(result_ds),
        "warnings": collect_warnings(captured_warnings or []),
    }


def add_provenance_attrs(result_ds: Dataset, provenance: dict[str, Any]) -> Dataset:
    software = provenance.get("software", {})
    git_context = provenance.get("git", {})
    run_context = provenance.get("run_context", {})
    outputs = provenance.get("outputs", {})
    result_ds.attrs["icclim_version"] = software.get("icclim", "")
    result_ds.attrs["provenance_file"] = outputs.get("provenance_path", "")
    command = run_context.get("command")
    if command:
        result_ds.attrs["command"] = command
    git_commit = git_context.get("commit")
    if git_commit:
        result_ds.attrs["git_commit"] = git_commit
    return result_ds


def write_provenance_json(file_path: str | Path, provenance: dict[str, Any]) -> None:
    sidecar_path = provenance_sidecar_path(file_path)
    sidecar_path.write_text(
        json.dumps(_json_ready(provenance), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def finalize_written_output_provenance(
    file_path: str | Path,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(provenance)
    updated["outputs"] = describe_output_path(
        Path(file_path),
        provenance_sidecar_path(file_path),
    )
    return updated


def collect_run_context(entrypoint: str) -> dict[str, Any]:
    return {
        "utc_timestamp": dt.datetime.now(tz=dt.timezone.utc).isoformat(),
        "entrypoint": entrypoint,
        "command": shlex.join(sys.argv) if sys.argv else "",
        "cwd": str(Path.cwd()),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "python_executable": sys.executable,
    }


def collect_software_context() -> dict[str, Any]:
    return {
        "icclim": _package_version("icclim"),
        "python": platform.python_version(),
        "xarray": _package_version("xarray"),
        "numpy": _package_version("numpy"),
        "pandas": _package_version("pandas"),
        "dask": _package_version("dask"),
        "netCDF4": _package_version("netCDF4"),
        "h5netcdf": _package_version("h5netcdf"),
        "cftime": _package_version("cftime"),
        "zarr": _package_version("zarr"),
        "xclim": _package_version("xclim"),
        "numba": _package_version("numba"),
    }


def collect_git_context() -> dict[str, Any]:
    commit = _git_output("rev-parse", "HEAD")
    branch = _git_output("rev-parse", "--abbrev-ref", "HEAD")
    repo_root = _git_output("rev-parse", "--show-toplevel")
    status = _git_output("status", "--short")
    return {
        "repository_root": repo_root,
        "branch": branch,
        "commit": commit,
        "dirty": bool(status) if status is not None else None,
        "status_summary": status,
    }


def describe_climate_variable(climate_var: ClimateVariable) -> dict[str, Any]:
    studied_data = climate_var.studied_data
    input_path = studied_data.encoding.get("source")
    return {
        "name": climate_var.name,
        "data_name": studied_data.name,
        "input_path": input_path,
        "input_file": describe_file_artifact(input_path),
        "units": studied_data.attrs.get("units"),
        "calendar": _calendar_name(studied_data),
        "source_frequency": getattr(climate_var.source_frequency, "pandas_freq", None),
        "is_reference": climate_var.is_reference,
        "bootstrap_requested": climate_var.bootstrap,
        "reference_period": list(climate_var.reference_period)
        if climate_var.reference_period is not None
        else None,
        "threshold": describe_threshold(climate_var.threshold),
    }


def describe_threshold(threshold: Threshold | Any) -> dict[str, Any] | None:
    if threshold is None:
        return None
    reference_period = getattr(threshold, "reference_period", None)
    interpolation = getattr(threshold, "interpolation", None)
    description = {
        "class": threshold.__class__.__name__,
        "operator": getattr(getattr(threshold, "operator", None), "short_name", None),
        "initial_query": getattr(threshold, "initial_query", None),
        "unit": getattr(threshold, "unit", None),
        "threshold_kind": _threshold_kind_value(threshold),
        "threshold_min_value": _quantity_string(
            getattr(threshold, "threshold_min_value", None)
        ),
        "value": _serialize_threshold_value(_threshold_value_for_provenance(threshold)),
        "doy_window_width": getattr(threshold, "doy_window_width", None),
        "reference_period": list(reference_period) if reference_period is not None else None,
        "interpolation": interpolation.__class__.__name__
        if interpolation is not None
        else None,
    }
    if isinstance(threshold, PercentileThreshold):
        description["is_day_of_year_percentile"] = threshold.is_doy_per_threshold
        description["only_leap_years"] = threshold.only_leap_years
    if isinstance(threshold, BoundedThreshold):
        description["logical_link"] = getattr(threshold.logical_link, "name", None)
        description["left_threshold"] = describe_threshold(threshold.left_threshold)
        description["right_threshold"] = describe_threshold(threshold.right_threshold)
    return description


def describe_output_path(output_path: Path, sidecar_path: Path) -> dict[str, Any]:
    return {
        "netcdf_path": str(output_path),
        "netcdf_file": describe_file_artifact(output_path),
        "provenance_path": str(sidecar_path),
    }


def collect_resolved_parameters(
    config: IndexConfig | None,
    result_ds: Dataset,
    *,
    climate_variables: list[ClimateVariable],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "output_variables": list(result_ds.data_vars),
        "climate_variables_count": len(climate_variables),
        "calendars": [
            _calendar_name(climate_var.studied_data) for climate_var in climate_variables
        ],
    }
    if config is not None:
        payload.update(
            {
                "indicator_name": config.indicator_name,
                "output_frequency": getattr(config.frequency, "pandas_freq", None),
                "save_thresholds": config.save_thresholds,
                "reference_period": list(config.reference_period)
                if config.reference_period is not None
                else None,
                "sampling_method": config.sampling_method,
                "run_index": config.run_index,
                "min_spell_length": config.min_spell_length,
                "rolling_window_width": config.rolling_window_width,
                "allow_partial_seasons": config.allow_partial_seasons,
                "date_event": config.date_event,
                "is_compared_to_reference": config.is_compared_to_reference,
                "bootstrap": describe_bootstrap(config, climate_variables),
            }
        )
    payload.update(_json_ready(overrides))
    return payload


def collect_execution_context(result_ds: Dataset) -> dict[str, Any]:
    return {
        "cpu_count": os.cpu_count(),
        "conda_default_env": os.environ.get("CONDA_DEFAULT_ENV"),
        "virtual_env": os.environ.get("VIRTUAL_ENV"),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_job_id": os.environ.get("SLURM_ARRAY_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "data_var_chunks": {
            name: _serialize_chunks(getattr(data_array.data, "chunks", None))
            for name, data_array in result_ds.data_vars.items()
        },
        "environment": {
            key: os.environ.get(key) for key in FILTERED_ENV_VARS if os.environ.get(key)
        },
    }


def _calendar_name(data_array: Any) -> str | None:
    time_index = getattr(data_array, "indexes", {}).get("time")
    if time_index is None:
        return None
    calendar = getattr(time_index, "calendar", None)
    if calendar is not None:
        return str(calendar)
    if len(time_index) == 0:
        return None
    sample = time_index[0]
    return getattr(sample, "calendar", None)


def _serialize_chunks(chunks: Any) -> list[list[int]] | None:
    if chunks is None:
        return None
    return [list(chunk_group) for chunk_group in chunks]


def _package_version(package_name: str) -> str | None:
    if package_name == "icclim":
        from icclim import __version__ as icclim_version  # noqa: PLC0415

        return icclim_version
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return None


def _git_output(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return None


def describe_bootstrap(
    config: IndexConfig,
    climate_variables: list[ClimateVariable],
) -> dict[str, Any]:
    thresholds = [climate_var.threshold for climate_var in climate_variables]
    bootstrap_requested = any(
        climate_var.bootstrap is not None for climate_var in climate_variables
    )
    bootstrap_enabled = any(_threshold_requires_bootstrap(threshold) for threshold in thresholds)
    description: dict[str, Any] = {
        "requested": bootstrap_requested,
        "threshold_requires_bootstrap": bootstrap_enabled,
        "threshold_kinds": [_threshold_kind_value(threshold) for threshold in thresholds],
    }
    capability = _classify_bootstrap_capability(config, climate_variables)
    if capability is not None:
        description.update(
            {
                "family": capability.family.value,
                "execution_kind": capability.execution_kind.value,
                "reason_code": capability.reason_code,
                "optimized": capability.execution_kind
                == BootstrapExecutionKind.OPTIMIZED_BOOTSTRAP,
            }
        )
    return description


def _classify_bootstrap_capability(
    config: IndexConfig,
    climate_variables: list[ClimateVariable],
):
    try:
        return classify_generic_indicator_bootstrap(
            indicator_name=config.indicator.name,
            climate_vars=climate_variables,
            resample_frequency=config.frequency,
            date_event=config.date_event,
        )
    except Exception:
        return None


def _threshold_requires_bootstrap(threshold: Threshold | Any) -> bool:
    if not isinstance(threshold, PercentileThreshold):
        return False
    return threshold.is_doy_per_threshold


def _threshold_kind_value(threshold: Threshold | Any) -> str | None:
    if threshold is None:
        return None
    try:
        kind = classify_threshold_kind(threshold)
    except Exception:
        return None
    if isinstance(kind, BootstrapThresholdKind):
        return kind.value
    return str(kind)


def _quantity_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def collect_warnings(
    captured_warnings: list[warnings.WarningMessage],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in captured_warnings:
        category_name = getattr(item.category, "__name__", str(item.category))
        warning_type = "runtime_warning"
        if "deprecat" in category_name.lower():
            warning_type = "deprecation_warning"
        elif "userwarning" in category_name.lower():
            warning_type = "scientific_warning"
        entries.append(
            {
                "type": warning_type,
                "category": category_name,
                "message": str(item.message),
                "filename": item.filename,
                "lineno": item.lineno,
            }
        )
    return entries


def describe_file_artifact(file_path: str | Path | None) -> dict[str, Any] | None:
    if file_path is None:
        return None
    path = Path(file_path)
    artifact: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        return artifact
    try:
        stat = path.stat()
    except OSError:
        return artifact
    artifact.update(
        {
            "size_bytes": stat.st_size,
            "mtime_utc": dt.datetime.fromtimestamp(
                stat.st_mtime,
                tz=dt.timezone.utc,
            ).isoformat(),
        }
    )
    checksum = _sha256_if_small_enough(path, stat.st_size)
    if checksum is not None:
        artifact["sha256"] = checksum
    return artifact


def _sha256_if_small_enough(path: Path, size_bytes: int) -> str | None:
    max_hash_bytes = int(
        os.environ.get("ICCLIM_PROVENANCE_MAX_HASH_BYTES", DEFAULT_MAX_HASH_BYTES)
    )
    if size_bytes > max_hash_bytes:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _serialize_threshold_value(value: Any) -> Any:
    if value is None:
        return None
    dims = getattr(value, "dims", None)
    shape = getattr(value, "shape", None)
    if dims is not None or shape is not None:
        return {
            "kind": value.__class__.__name__,
            "dims": list(dims) if dims is not None else None,
            "shape": list(shape) if shape is not None else None,
        }
    return _json_ready(value)


def _threshold_value_for_provenance(threshold: Threshold | Any) -> Any:
    if getattr(threshold, "is_ready", True) is False:
        initial_value = getattr(threshold, "initial_value", None)
        if initial_value is not None:
            return {
                "kind": "unprepared_percentile_threshold",
                "initial_value": _json_ready(initial_value),
            }
        return None
    return getattr(threshold, "value", None)


def _json_ready(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): _json_ready(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return str(value)

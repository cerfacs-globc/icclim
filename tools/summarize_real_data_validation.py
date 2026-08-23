from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunSummary:
    workload: str
    label: str
    duration_seconds: float
    path: Path


@dataclass(frozen=True)
class ComparisonSummary:
    current_label: str
    baseline_label: str
    workload: str
    path: Path
    all_data_vars_equal: bool
    total_changed_cells: int
    max_abs_diff: float


def _parse_summary_file(path: Path) -> RunSummary:
    payload = json.loads(path.read_text())
    return RunSummary(
        workload=payload["workload"],
        label=payload["label"],
        duration_seconds=float(payload["duration_seconds"]),
        path=path,
    )


def _remove_suffix(text: str, suffix: str) -> str:
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def _parse_compare_file(path: Path) -> ComparisonSummary:
    payload = json.loads(path.read_text())
    filename = _remove_suffix(path.name, ".compare.json")
    current_prefix = "current-vs-"
    current_debug_prefix = "current-debug-vs-"
    if filename.startswith(current_prefix):
        remainder = filename.removeprefix(current_prefix)
        if remainder.startswith("master-bounded-hotfix-"):
            baseline_label = "master"
            workload = remainder.removeprefix("master-bounded-hotfix-")
        elif remainder.startswith("v717-bounded-hotfix-"):
            baseline_label = "v717"
            workload = remainder.removeprefix("v717-bounded-hotfix-")
        elif remainder.startswith("baseline717-"):
            baseline_label = "v717"
            workload = remainder.removeprefix("baseline717-")
        elif remainder.startswith("master-"):
            baseline_label = "master"
            workload = remainder.removeprefix("master-")
        elif remainder.startswith("v717-"):
            baseline_label = "v717"
            workload = remainder.removeprefix("v717-")
        else:
            msg = f"Unsupported compare filename: {path.name}"
            raise ValueError(msg)
        current_label = "current"
    elif filename.startswith(current_debug_prefix):
        remainder = filename.removeprefix(current_debug_prefix)
        if remainder.startswith("master-debug-"):
            baseline_label = "master-debug"
            workload = remainder.removeprefix("master-debug-")
        else:
            msg = f"Unsupported compare filename: {path.name}"
            raise ValueError(msg)
        current_label = "current-debug"
    elif filename.startswith("master-vs-v717-"):
        current_label = "master"
        baseline_label = "v717"
        workload = filename.removeprefix("master-vs-v717-")
    else:
        msg = f"Unsupported compare filename: {path.name}"
        raise ValueError(msg)
    data_var_results = payload.get("data_var_comparison", {})
    all_equal = True
    total_changed_cells = 0
    max_abs_diff = 0.0
    for result in data_var_results.values():
        equal = bool(result.get("equal", False))
        all_equal = all_equal and equal
        total_changed_cells += int(result.get("changed_cells", 0))
        max_abs_diff = max(max_abs_diff, float(result.get("max_abs_diff", 0.0) or 0.0))
    return ComparisonSummary(
        current_label=current_label,
        baseline_label=baseline_label,
        workload=workload,
        path=path,
        all_data_vars_equal=all_equal,
        total_changed_cells=total_changed_cells,
        max_abs_diff=max_abs_diff,
    )


def _load_run_summaries(result_dir: Path) -> dict[tuple[str, str], RunSummary]:
    return {
        (summary.label, summary.workload): summary
        for summary in (
            _parse_summary_file(path)
            for path in sorted(result_dir.glob("*.summary.json"))
        )
    }


def _load_compare_summaries(
    result_dir: Path,
) -> dict[tuple[str, str, str], ComparisonSummary]:
    return {
        (summary.current_label, summary.baseline_label, summary.workload): summary
        for summary in (
            _parse_compare_file(path)
            for path in sorted(result_dir.glob("*.compare.json"))
        )
    }


def _format_seconds(value: float | None) -> str:
    if value is None:
        return "pending"
    return f"{value:.2f}"


def _format_ratio(current: float | None, baseline: float | None) -> str:
    if current is None or baseline is None or current == 0:
        return "pending"
    return f"{baseline / current:.2f}x"


def _format_percent_change(current: float | None, baseline: float | None) -> str:
    if current is None or baseline is None or baseline == 0:
        return "pending"
    change = ((current - baseline) / baseline) * 100
    return f"{change:+.1f}%"


def _format_validation_status(
    comparison: ComparisonSummary | None,
) -> tuple[str, str, str]:
    if comparison is None:
        return ("pending", "pending", "pending")
    if comparison.all_data_vars_equal:
        return ("exact", "0", "0.0")
    return (
        "differs",
        str(comparison.total_changed_cells),
        f"{comparison.max_abs_diff:g}",
    )


def _workload_notes(workload: str) -> str:
    notes = {
        "generic_tas_bounded_count_yearly": (
            "bounded scalar-guard count; dedicated compiled path validated"
            " on Kraken real data"
        ),
        "generic_tas_bounded_average_yearly": (
            "bounded scalar-guard average; dedicated compiled path validated"
            " on Kraken real data"
        ),
        "generic_tas_bounded_sum_yearly": (
            "bounded scalar-guard sum; dedicated compiled path validated"
            " on Kraken real data"
        ),
        "generic_tas_bounded_fraction_yearly": (
            "bounded scalar-guard fraction_of_total; dedicated compiled path"
            " validated on Kraken real data"
        ),
        "generic_tas_bounded_or_count_yearly": (
            "bounded scalar-guard count with OR composition; dedicated compiled"
            " path validated on Kraken real data"
        ),
        "generic_tas_bounded_or_average_yearly": (
            "bounded scalar-guard average with OR composition; dedicated"
            " compiled path validated on Kraken real data"
        ),
        "generic_tas_bounded_or_sum_yearly": (
            "bounded scalar-guard sum with OR composition; dedicated compiled"
            " path validated on Kraken real data"
        ),
        "generic_tas_bounded_or_fraction_yearly": (
            "bounded scalar-guard fraction_of_total with OR composition;"
            " dedicated compiled path validated on Kraken real data"
        ),
        "generic_tas_compound_percentile_count_yearly": (
            "same-variable compound percentile count; composed from bootstrap"
            " leaf masks on Kraken real data"
        ),
        "generic_tas_compound_percentile_average_yearly": (
            "same-variable compound percentile average; composed from bootstrap"
            " leaf masks on Kraken real data"
        ),
        "generic_tas_compound_percentile_sum_yearly": (
            "same-variable compound percentile sum; composed from bootstrap"
            " leaf masks on Kraken real data"
        ),
        "generic_tas_compound_percentile_fraction_yearly": (
            "same-variable compound percentile fraction_of_total; composed"
            " from bootstrap leaf masks on Kraken real data"
        ),
        "generic_tas_compound_percentile_or_count_yearly": (
            "same-variable compound percentile OR count; composed from"
            " bootstrap leaf masks on Kraken real data"
        ),
        "generic_tas_compound_percentile_or_fraction_yearly": (
            "same-variable compound percentile OR fraction_of_total;"
            " composed from bootstrap leaf masks on Kraken real data"
        ),
        "generic_pr_fraction_bootstrap_yearly": (
            "filtered value aggregate; wet-day style threshold_min_value"
        ),
        "generic_pr_count_bootstrap_yearly": (
            "filtered count; wet-day style threshold_min_value"
        ),
        "generic_pr_sum_bootstrap_yearly": (
            "filtered value aggregate; wet-day style threshold_min_value"
        ),
        "generic_pr_average_bootstrap_yearly": (
            "filtered value aggregate; wet-day style threshold_min_value"
        ),
        "generic_pr_average_bootstrap_monthly": (
            "filtered value aggregate monthly; wet-day style threshold_min_value"
        ),
        "generic_pr_average_bootstrap_dry_yearly": (
            "filtered value aggregate on a drier regional subset; wet-day style"
            " threshold_min_value"
        ),
        "generic_pr_average_bootstrap_99_yearly": (
            "filtered value aggregate with a rarer 99th-percentile threshold"
        ),
        "generic_tas_fraction_bootstrap_yearly": (
            "unfiltered value aggregate; optimized fraction_of_total candidate"
        ),
        "generic_tas_sum_bootstrap_yearly": (
            "unfiltered value aggregate; optimized sum candidate"
        ),
        "generic_tas_average_bootstrap_yearly": (
            "unfiltered value aggregate; optimized average candidate"
        ),
        "generic_tas_spell_bootstrap_yearly": (
            "spell reducer; raw v7.1.7 differs from current and master"
        ),
        "wsdi_yearly": "standard warm-spell duration index",
        "tx90p_cftime_yearly": ("Gregorian-like cftime validation on real tas values"),
        "tx90p_cftime_monthly": (
            "Gregorian-like cftime monthly validation on real tas values"
        ),
        "generic_tas_count_date_event_monthly": "date_event count control path",
        "combined_cd_yearly": (
            "compound tas+pr count; combines specialized leaf masks through"
            " logical-link composition"
        ),
    }
    return notes.get(workload, "")


def _historical_validation_note(
    workload: str,
    comparisons: dict[tuple[str, str, str], ComparisonSummary],
) -> str:
    current_vs_master = comparisons.get(("current", "master", workload))
    current_vs_v717 = comparisons.get(("current", "v717", workload))
    master_vs_v717 = comparisons.get(("master", "v717", workload))
    if (
        current_vs_master is not None
        and current_vs_master.all_data_vars_equal
        and current_vs_v717 is not None
        and not current_vs_v717.all_data_vars_equal
        and master_vs_v717 is not None
        and not master_vs_v717.all_data_vars_equal
    ):
        return "historical master/v7.1.7 difference confirmed"
    return ""


def _build_validation_table(
    workloads: list[str],
    comparisons: dict[tuple[str, str, str], ComparisonSummary],
) -> str:
    lines = [
        "| Workload | Current vs master | Changed cells | Max abs diff | Current vs v7.1.7 | Changed cells | Max abs diff | Notes |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for workload in workloads:
        master_status = _format_validation_status(
            comparisons.get(("current", "master", workload))
        )
        v717_status = _format_validation_status(
            comparisons.get(("current", "v717", workload))
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    workload,
                    master_status[0],
                    master_status[1],
                    master_status[2],
                    v717_status[0],
                    v717_status[1],
                    v717_status[2],
                    " ; ".join(
                        part
                        for part in [
                            _workload_notes(workload),
                            _historical_validation_note(workload, comparisons),
                        ]
                        if part
                    ),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _build_performance_table(
    workloads: list[str],
    runs: dict[tuple[str, str], RunSummary],
) -> str:
    lines = [
        "| Workload | Current (s) | Master (s) | Delta vs master | Speedup vs master | v7.1.7 (s) | Delta vs v7.1.7 | Speedup vs v7.1.7 | Notes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for workload in workloads:
        current = runs.get(("current", workload))
        master = runs.get(("baseline-master", workload))
        v717 = runs.get(("baseline717", workload))
        if workload == "generic_tas_bounded_count_yearly":
            master = runs.get(("baseline-master-bounded-hotfix", workload), master)
            v717 = runs.get(("baseline717-bounded-hotfix", workload), v717)
        current_s = current.duration_seconds if current is not None else None
        master_s = master.duration_seconds if master is not None else None
        v717_s = v717.duration_seconds if v717 is not None else None
        lines.append(
            "| "
            + " | ".join(
                [
                    workload,
                    _format_seconds(current_s),
                    _format_seconds(master_s),
                    _format_percent_change(current_s, master_s),
                    _format_ratio(current_s, master_s),
                    _format_seconds(v717_s),
                    _format_percent_change(current_s, v717_s),
                    _format_ratio(current_s, v717_s),
                    _workload_notes(workload),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def _build_summary_document(result_dir: Path, expected_workloads: list[str]) -> str:
    runs = _load_run_summaries(result_dir)
    comparisons = _load_compare_summaries(result_dir)
    workloads = sorted({workload for _, workload in runs} | set(expected_workloads))
    validation_table = _build_validation_table(workloads, comparisons)
    performance_table = _build_performance_table(workloads, runs)
    return (
        "# Real-data bootstrap validation summary\n\n"
        "## Validation\n\n"
        f"{validation_table}\n\n"
        "## Performance\n\n"
        f"{performance_table}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--expected-workload", action="append", default=[])
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    out = Path(args.out)
    summary = _build_summary_document(result_dir, args.expected_workload)
    out.write_text(summary)
    print(summary)


if __name__ == "__main__":
    main()

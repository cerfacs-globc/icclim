from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path


def _load_validation_module() -> object:
    script_path = Path(__file__).with_name("run_real_data_validation.py")
    spec = importlib.util.spec_from_file_location(
        "run_real_data_validation", script_path
    )
    if spec is None or spec.loader is None:
        msg = f"Cannot load validation module from {script_path}"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--workload", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    sys.path.insert(0, str(repo / "src"))

    started = time.time()
    payload: dict[str, object] = {
        "repo": str(repo),
        "workload": args.workload,
    }
    try:
        import icclim

        validation_module = _load_validation_module()

        validation_module._warmup(icclim)
        ds = validation_module._build_workload(
            icclim,
            args.workload,
            chunks=validation_module.DEFAULT_CHUNKS,
        )
        payload["data_vars"] = list(ds.data_vars)
        payload["coords"] = list(ds.coords)
        payload["sizes"] = {name: int(size) for name, size in ds.sizes.items()}
        ds.load()
        payload["status"] = "completed"
    except Exception as exc:
        payload["status"] = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error_message"] = str(exc)
        payload["traceback"] = traceback.format_exc()
    finally:
        payload["elapsed_seconds"] = time.time() - started
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

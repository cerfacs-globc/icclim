"""
Icclim Logo updater.

This update the version number within icclim svg logo.
It should only be used in our CI pipeline (github action).
For testing purposes if you wish to run it locally you must first enable the git LFS
feature, otherwise you won't have access to the svg logos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import icclim

VERSION_PLACEHOLDER = "{{icclim.__version__}}"

MAX_ARGS_COUNT = 2


def _run(inpath: Path, outpath: Path) -> None:
    with inpath.open() as in_file, outpath.open("w") as out_file:
        lines = in_file.readlines()
        for line in lines:
            if VERSION_PLACEHOLDER in line:
                updated_line = line.replace(
                    VERSION_PLACEHOLDER,
                    str(icclim.__version__),
                )
            else:
                updated_line = line
            out_file.write(updated_line)


if __name__ == "__main__":
    if len(sys.argv) <= MAX_ARGS_COUNT:
        error_msg = (
            "This script needs 2 arguments,"
            " the input file path where a placeholder exists"
            " and the output file path"
        )
        raise NotImplementedError(error_msg)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    _run(in_path, out_path)

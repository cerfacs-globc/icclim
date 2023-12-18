"""
Icclim Logo updater.
This update the version number within icclim svg logo.
It should only be used in our CI pipeline (github action).
For testing purposes if you wish to run it locally you must first enable the git LFS
feature, otherwise you won't have access to the svg logos.
"""

from __future__ import annotations

import sys

import icclim

VERSION_PLACEHOLDER = "{{icclim.__version__}}"


def run(inpath, outpath):
    with open(inpath) as in_file, open(outpath, "w") as out_file:
        for line in in_file:
            if VERSION_PLACEHOLDER in line:
                line = line.replace(VERSION_PLACEHOLDER, str(icclim.__version__))
            out_file.write(line)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise NotImplementedError(
            "This script needs 2 arguments,"
            " the input file path where a placeholder exists"
            " and the output file path",
        )
    run(sys.argv[1], sys.argv[2])

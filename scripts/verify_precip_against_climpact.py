"""Backward-compatible entry point for precipitation reference checks."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    from verify_index_against_reference import main

    main()

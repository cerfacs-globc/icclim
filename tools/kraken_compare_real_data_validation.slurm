#!/bin/bash
#SBATCH --job-name=icclim-compare
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G

set -euo pipefail

PYTHON_BIN=/scratch/globc/page/.conda/envs/icclimv7/bin/python
SCRIPT=/scratch/globc/page/icclim-bench/compare_real_data_validation.py

mkdir -p "$(dirname "$OUT_PATH")"
cd "$(dirname "$OUT_PATH")"

"$PYTHON_BIN" "$SCRIPT" \
  --current "$CURRENT_PATH" \
  --baseline "$BASELINE_PATH" \
  --out "$OUT_PATH"

#!/bin/bash
#SBATCH --job-name=icclim-realval
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

PYTHON_BIN=/scratch/globc/page/.conda/envs/icclimv7/bin/python
SCRIPT=/scratch/globc/page/icclim-bench/run_real_data_validation.py

mkdir -p "$OUT_DIR"
cd "$OUT_DIR"

"$PYTHON_BIN" "$SCRIPT" \
  --repo "$REPO_PATH" \
  --workload "$WORKLOAD" \
  --label "$LABEL" \
  --out-dir "$OUT_DIR"

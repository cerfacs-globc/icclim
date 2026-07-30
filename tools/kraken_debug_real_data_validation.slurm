#!/bin/bash
#SBATCH --job-name=icclim-realval-debug
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

set -euo pipefail

PYTHON_BIN=/scratch/globc/page/.conda/envs/icclimv7/bin/python
SCRIPT=/scratch/globc/page/icclim-bench/debug_real_data_validation.py

mkdir -p "$OUT_DIR"
cd "$OUT_DIR"

"$PYTHON_BIN" "$SCRIPT" \
  --repo "$REPO_PATH" \
  --workload "$WORKLOAD" \
  | tee "$OUT_DIR/$LABEL-$WORKLOAD.debug.json"

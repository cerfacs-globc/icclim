#!/bin/bash
#SBATCH --job-name=icclim-realval
#SBATCH --partition=miniprod
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G

set -euo pipefail

PYTHON_BIN=/scratch/globc/page/.conda/envs/icclimv7/bin/python
SCRIPT="$REPO_PATH/tools/run_real_data_validation.py"

mkdir -p "$OUT_DIR"
cd "$OUT_DIR"

"$PYTHON_BIN" "$SCRIPT" \
  --repo "$REPO_PATH" \
  --workload "$WORKLOAD" \
  --label "$LABEL" \
  --out-dir "$OUT_DIR"

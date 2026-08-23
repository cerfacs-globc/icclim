#!/bin/bash
#SBATCH --job-name=icclim-realval-debug
#SBATCH --partition=debug
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -euo pipefail

PYTHON_BIN=/scratch/globc/page/.conda/envs/icclimv7/bin/python
SCRIPT="$REPO_PATH/tools/debug_real_data_validation.py"

mkdir -p "$OUT_DIR"
cd "$OUT_DIR"

"$PYTHON_BIN" "$SCRIPT" \
  --repo "$REPO_PATH" \
  --workload "$WORKLOAD" \
  | tee "$OUT_DIR/$LABEL-$WORKLOAD.debug.json"

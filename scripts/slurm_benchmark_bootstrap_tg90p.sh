#!/bin/bash
#SBATCH --job-name=icclim-tg90p-bench
#SBATCH --output=icclim-tg90p-bench-%j.out
#SBATCH --error=icclim-tg90p-bench-%j.err
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

REPO_PATH="${REPO_PATH:-$PWD}"
FILE_GLOB="${FILE_GLOB:-/path/to/data/tas_day_ACCESS-CM2_historical_*.nc}"
SCHEDULER="${SCHEDULER:-threads}"
TIME_CHUNK="${TIME_CHUNK:-365}"
LAT_CHUNK="${LAT_CHUNK:-24}"
LON_CHUNK="${LON_CHUNK:-32}"
BOOTSTRAP="${BOOTSTRAP:-auto}"
CACHE_DIR="${CACHE_DIR:-}"
CACHE_KEY="${CACHE_KEY:-}"
SAVE_OUTPUT="${SAVE_OUTPUT:-true}"
FORCE="${FORCE:-false}"

cd "$REPO_PATH"

CMD=(
  python scripts/benchmark_bootstrap_tg90p.py
  --repo "$REPO_PATH"
  --file-glob "$FILE_GLOB"
  --scheduler "$SCHEDULER"
  --time-chunk "$TIME_CHUNK"
  --lat-chunk "$LAT_CHUNK"
  --lon-chunk "$LON_CHUNK"
  --bootstrap "$BOOTSTRAP"
)

if [ -n "$CACHE_DIR" ]; then
  CMD+=(--cache-dir "$CACHE_DIR")
fi

if [ -n "$CACHE_KEY" ]; then
  CMD+=(--cache-key "$CACHE_KEY")
fi

if [ "$SAVE_OUTPUT" = "true" ]; then
  CMD+=(--save-output)
fi

if [ "$FORCE" = "true" ]; then
  CMD+=(--force)
fi

echo "Running: ${CMD[*]}"
"${CMD[@]}"

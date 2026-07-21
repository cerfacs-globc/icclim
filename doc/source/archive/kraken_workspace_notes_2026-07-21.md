# Kraken Workspace Notes (2026-07-21)

## Purpose

Persistent note to avoid losing track of the Kraken bootstrap benchmarking
workspace layout.

## Source Checkout

Use this as the actual git checkout on Kraken:

- `/scratch/globc/page/src/icclim`

State observed on Tuesday, July 21, 2026:

- branch: `fix/bootstrap-next`
- head: `8c145f1`
- remote `origin`: `git@github.com:pagecp/icclim.git`

## Benchmark / Cache Directories

These directories were used on Monday, July 20, 2026 for bootstrap benchmark
artifacts and cached results:

- `/scratch/globc/page/icclim-bench/current`
- `/scratch/globc/page/icclim-bench/next`
- `/scratch/globc/page/icclim-bench/master`
- `/scratch/globc/page/icclim-bench/prestate`
- `/scratch/globc/page/icclim-bench/old-bootstrap`

These are benchmark workspaces/artifact directories, not git repositories.

## Important Reminder

Do not confuse:

- `/scratch/globc/page/src/icclim` : real git checkout
- `/scratch/globc/page/icclim-bench/*` : benchmark outputs / cached runs
- `/scratch/globc/page/icclim` : old virtualenv-like directory, not the repo

## Conda Environment

Available environment observed on Kraken:

- `/scratch/globc/page/.conda/envs/icclimv7`

Use that interpreter directly in batch jobs when shell activation is unreliable.

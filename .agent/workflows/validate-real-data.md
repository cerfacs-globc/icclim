---
description: how to perform real data validation using CMIP6 and ERA5 datasets with numerical comparison
---

This workflow describes how to validate icclim changes using real datasets and ensuring numerical consistency with the previous stable release.

### Prerequisites
- Assets are located at `/Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/data/latest`
- The validation script is `/Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/run_icclim.py`
- Comparison utility: `scripts/compare_stats.py`

### Steps

1. **Verify Environment**
   Ensure data and scripts are present:
   ```bash
   ls run_icclim.py scripts/compare_stats.py
   ls ../data/latest
   ```

2. **Compute Statistics for Current Branch**
   // turbo
   Calculate statistics (Mean, Min, Max, Std) for standard indices on the current version:
   ```bash
   env PYTHONPATH=src python3 scripts/compare_stats.py ../current_stats.json ../data/latest
   ```

3. **Compute Statistics for Previous Release**
   // turbo
   Extract the previous stable tag (e.g., `v7.0.5`) and run the same calculation:
   ```bash
   mkdir -p /tmp/icclim_stable
   git archive v7.0.5 | tar -x -C /tmp/icclim_stable
   env PYTHONPATH=/tmp/icclim_stable/src python3 scripts/compare_stats.py ../stable_stats.json ../data/latest
   ```

4. **Numerical Comparison**
   // turbo
   Compare the two resulting JSON files and report deltas:
   ```bash
   python3 -c "
   import json
   with open('../current_stats.json') as f: current = json.load(f)
   with open('../stable_stats.json') as f: stable = json.load(f)
   for k in current:
       print(f'--- {k} ---')
       for stat in ['mean', 'min', 'max', 'std']:
           c_val, s_val = current[k][stat], stable[k][stat]
           print(f'{stat}: {c_val:.5f} vs {s_val:.5f} (diff: {c_val - s_val:.5e})')
   "
   ```

5. **Legacy Validation (Optional)**
   Verify full NetCDF generation:
   ```bash
   env PYTHONPATH=src python3 run_icclim.py ../data/latest ../output/validation_run
   ```

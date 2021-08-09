[Read-the-docs-example-18] # Read the docs - example 18
user_indice: {'indice_name': 'my_indice', 'calc_operation': 'nb_events', 'logical_operation': ['gt', 'get', 'lt'], 'thresh': ['p90', 283.15, 'p30'], 'var_type': ['t', '-', 'p'], 'link_logical_operations': 'and'}
in_files: [['tasmax_day_MPI-ESM-LR_historical_r1i1p1_19900101-19991231.nc'], ['tasmin_day_MPI-ESM-LR_historical_r1i1p1_19900101-19991231.nc'], ['pr_day_MPI-ESM-LR_historical_r1i1p1_19900101-19991231.nc']]
dt1: 1990-01-01
dt2: 1992-12-31
base_dt1: 1991-01-01
base_dt2: 1992-12-31
out_unit: days
slice_mode: SON
callback: callback.defaultCallback2

[Read-the-docs-example-10] # Read the docs - example 10
user_indice: {'indice_name': 'my_indice', 'calc_operation': 'nb_events', 'calc_operation': 'max_nb_consecutive_events', 'logical_operation': 'gt', 'thresh': 'p85', 'var_type': 'p'}
in_files: ['pr_day_CNRM-CM5_historical_r1i1p1_19700101-19741231.nc','pr_day_CNRM-CM5_historical_r1i1p1_19750101-19791231.nc','pr_day_CNRM-CM5_historical_r1i1p1_19800101-19841231.nc']
base_dt1: 1970-01-01
base_dt2: 1975-12-31
slice_mode: year
out_unit: days
callback: callback.defaultCallback2

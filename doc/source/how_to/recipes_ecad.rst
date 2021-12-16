Examples
---------
>>> import icclim
>>> import datetime

Example 1: index SU
~~~~~~~~~~~~~~~~~~~~~
>>> files = ['tasmax_day_CNRM-CM5_historical_r1i1p1_19950101-19991231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_20000101-20041231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_20050101-20051231.nc']
>>>
>>> dt1 = datetime.datetime(1998,1,1)
>>> dt2 = datetime.datetime(2005,12,31)
>>>
>>> out_f = 'SU_JJA_CNRM-CM5_historical_r1i1p1_1998-2005.nc' # OUTPUT FILE: summer season values of SU
>>>
>>> icclim.index(index_name='SU', in_files=files, var_name='tasmax', time_range=[dt1, dt2], slice_mode='JJA', out_file=out_f)
>>>
>>> dt1 = datetime.datetime(1998,1,1)
>>> dt2 = datetime.datetime(2005,12,31)
>>>
>>> out_f = 'SU_JJA_CNRM-CM5_historical_r1i1p1_1998-2005.nc' # OUTPUT FILE: summer season values of SU
>>>
>>> icclim.index(index_name='SU', in_files=files, var_name='tasmax', time_range=[dt1, dt2], slice_mode='JJA', out_file=out_f)


Example 2: index ETR
~~~~~~~~~~~~~~~~~~~~~~
>>> files_tasmax = ['tasmax_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc']
>>> files_tasmin = ['tasmin_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc', 'tasmin_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc']
>>>
>>> out_f = 'ETR_year_CNRM-CM5_historical_r1i1p1_1930-1939.nc' # OUTPUT FILE: annual values of ETR
>>>
>>> icclim.index(index_name='ETR', in_files=[files_tasmax, files_tasmin], var_name=['tasmax', 'tasmin'], slice_mode='year', out_file=out_f)
>>> files_tasmin = ['tasmin_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc', 'tasmin_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc']
>>>
>>> out_f = 'ETR_year_CNRM-CM5_historical_r1i1p1_1930-1939.nc' # OUTPUT FILE: annual values of ETR
>>>
>>> icclim.index(index_name='ETR', in_files=[files_tasmax, files_tasmin], var_name=['tasmax', 'tasmin'], slice_mode='year', out_file=out_f)

.. warning:: The order of `var_name` must be ['tasmax', 'tasmin'] and NOT ['tasmin', 'tasmax']. The same for `in_files`.


Example 3: index TG90p with callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>>> from icclim.util import callback
>>>
>>> f = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>>
>>> # base period
>>> base_dt1 = datetime.datetime(1961,1,1)
>>> base_dt2 = datetime.datetime(1970,12,31)
>>>
>>> # studied period
>>> dt1 = datetime.datetime(1980,1,1)
>>> dt2 = datetime.datetime(2000,12,31)
>>>
>>> out_f = 'TG90p_AMJJAS_CNRM-CM5_historical_r1i1p1_1980-2000.nc' # OUTPUT FILE: summer half-year values of TG90p
>>>
>>> icclim.index(index_name='TG90p',
                in_files=f,
                var_name='tas',
                slice_mode='AMJJAS',
                time_range=[dt1, dt2],
                base_period_time_range=[base_dt1, base_dt2],
                out_file=out_f,
                out_unit='%',
                callback=callback.defaultCallback2)
>>>
>>> f = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>>
>>> # base period
>>> base_dt1 = datetime.datetime(1961,1,1)
>>> base_dt2 = datetime.datetime(1970,12,31)
>>>
>>> # studied period
>>> dt1 = datetime.datetime(1980,1,1)
>>> dt2 = datetime.datetime(2000,12,31)
>>>
>>> out_f = 'TG90p_AMJJAS_CNRM-CM5_historical_r1i1p1_1980-2000.nc' # OUTPUT FILE: summer half-year values of TG90p
>>>
>>> icclim.index(index_name='TG90p', in_files=f, var_name='tas', slice_mode='AMJJAS', time_range=[dt1, dt2], base_period_time_range=[base_dt1, base_dt2], out_file=out_f, out_unit='%', callback=callback.defaultCallback2)



Example 4: multivariable indices CD, CW, WD, WW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>>> from icclim.util import callback
>>>
>>> f = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>>
>>> # base period
>>> base_dt1 = datetime.datetime(1961,1,1)
>>> base_dt2 = datetime.datetime(1970,12,31)
>>>
>>> # studied period
>>> dt1 = datetime.datetime(1980,1,1)
>>> dt2 = datetime.datetime(2000,12,31)
>>>
>>> out_f = 'TG90p_AMJJAS_CNRM-CM5_historical_r1i1p1_1980-2000.nc' # OUTPUT FILE: summer half-year values of TG90p
>>>
>>> icclim.index(index_name='TG90p',
                in_files=f,
                var_name='tas',
                slice_mode='AMJJAS',
                time_range=[dt1, dt2],
                base_period_time_range=[base_dt1, base_dt2],
                out_file=out_f,
                out_unit='%',
                callback=callback.defaultCallback2)
>>>
>>> f = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>>
>>> # base period
>>> base_dt1 = datetime.datetime(1961,1,1)
>>> base_dt2 = datetime.datetime(1970,12,31)
>>>
>>> # studied period
>>> dt1 = datetime.datetime(1980,1,1)
>>> dt2 = datetime.datetime(2000,12,31)
>>>
>>> out_f = 'TG90p_AMJJAS_CNRM-CM5_historical_r1i1p1_1980-2000.nc' # OUTPUT FILE: summer half-year values of TG90p
>>>
>>> icclim.index(index_name='TG90p', in_files=f, var_name='tas', slice_mode='AMJJAS', time_range=[dt1, dt2], base_period_time_range=[base_dt1, base_dt2], out_file=out_f, out_unit='%', callback=callback.defaultCallback2)

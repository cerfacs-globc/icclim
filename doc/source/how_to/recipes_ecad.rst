Examples
---------
>>> import icclim
>>> import datetime

Example 1: index SU
~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


Multi index computation
~~~~~~~~~~~~~~~~~~~~~~~~

New in 5.1.0.
This feature allows you to compute multiple indices at the same time.
There is no special optimization done to reduce computation costs.
A futur optimization would be to group common computations between indices, such as the computation of percentiles for
WSDI and TX90p and to reuse the results when on both indices.

.. note::
    The input ``in_files`` must include all the necessary variables.
    When computing all indices it needs "tas", "tasmin", "tasmax" and 2 precipitation variables such as "pr" and
    "precip".
    One of the precipitation variable must be reprensent snow precipitation and . The snow variable must have a unit "cm" or an equivalent length unit.

Compute every HEAT indices [SU,TR,WSDI,TG90p,TN90p,TX90p,TXx,TNx,CSU]
_____________________________________________________________________


>>> bp = [datetime.datetime(1991, 1, 1), datetime.datetime(1999, 12, 31)]
>>> tr = [datetime.datetime(1991, 1, 1), datetime.datetime(2010, 12, 31)]
>>> # The file must include all necessary variable for HEAT indices i
>>> file = "./netcdf_files/sampledata.1991-2010.nc"
>>> res = icclim.indices(index_group=IndexGroup.HEAT,
>>>                      in_files=file,
>>>                      base_period_time_range=bp,
>>>                      time_range=tr,
>>>                      out_file="heat_indices.nc")

Compute every indices at the same time
______________________________________

>>> bp = [datetime.datetime(1991, 1, 1), datetime.datetime(1999, 12, 31)]
>>> tr = [datetime.datetime(1991, 1, 1), datetime.datetime(2010, 12, 31)]
>>> file = "./netcdf_files/sampledata.1991-2010.nc"
>>> res = icclim.indices(index_group="all",
>>>                      in_files=file,
>>>                      base_period_time_range=bp,
>>>                      time_range=tr,
>>>                      out_file="heat_indices.nc")

# to calculate indices ETR, DTR, vDTR

file_tasmin1 = '/data/tatarinova/CMIP5/tasmin_day/tasmin_day_CNRM-CM5_historical_r1i1p1_19050101-19091231.nc'
file_tasmin2 = '/data/tatarinova/CMIP5/tasmin_day/tasmin_day_CNRM-CM5_historical_r1i1p1_19100101-19141231.nc'
file_tasmin3 = '/data/tatarinova/CMIP5/tasmin_day/tasmin_day_CNRM-CM5_historical_r1i1p1_19150101-19191231.nc'


file_tasmax1 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_19050101-19091231.nc'
file_tasmax2 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_19100101-19141231.nc'
file_tasmax3 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_19150101-19191231.nc'


import icclim
import datetime

dt1 = datetime.datetime(1905,01,01)
dt2 = datetime.datetime(1919,12,31)

icclim.indice_multivar(in_files1=[file_tasmax1, file_tasmax2, file_tasmax3],
                       var1='tasmax',
                    in_files2=[file_tasmin1, file_tasmin2, file_tasmin3],
                    var2='tasmin',
                    out_file='indiceETR.nc',
                    indice_name='ETR',
                    time_range=[dt1, dt2],
                    slice_mode='year',
                    project='CMIP5',
                    N_lev=None,
                    callback=None)

from icclim import icclim
import pdb
from icclim.util import callback
import datetime
import glob
def netcdf_processing():

    #pr_1m_185101_201412_NOAA_20CR_V2C.nc
    #tas_day_CNRM-CM5_historical_r1i1p1_19950101-19991231.nc
    varname = 'tasmax'
    user_indice = {'indice_name': 'TG',
                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
                    'logical_operation': 'gt',
                    'thresh': 'p80',
                    'var_type': 't',
                    'date_event': True
                    }


    save_path = '/Users/xavier/Projets/data/test/results/'

    #list_file = ["tas_1d_19480101_20161231_NCEP.nc", "tas_day_IPSL-CM5A-LR_historical_r1i1p1_18500101_20051231.nc", "tas_day_CMCC-CM_historical_r1i1p1_18500101_20051231.nc"]
    list_file = ["tasmax_day_CNRM-CM6-1_highresSST-present_r21i1p1f2_gr_19500101-19991231_version_3.nc"]#"test_tas_1d_19480101_20161231_NCEP.nc"]
    slice_mode = ['DJF','year','MAM','JJA','SON']
    indice_2_test = ['TX','TN']
    for file in list_file:
        for slice_ in slice_mode:
            #for indice_2 in indice_2_test:
            if varname=='pr':
                user_indice = {'indice_name': 'RX5day',
                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
                    'logical_operation': 'gt',
                    'thresh': 'p85',
                    'var_type': 'p'
                }
                bp = [datetime.datetime(1950,1,1), datetime.datetime(1952,12,31)]
                in_file = '/Users/xavier/Projets/data/test/pr_day_CNRM-CM6-1_highresSST-present_r21i1p1f2_gr_19500101-19991231_netcdf3.nc'
                out_file = save_path+'pr_eur11_mean.nc'
                icclim.indice(user_indice=user_indice, slice_mode='MAM', base_period_time_range=bp, in_files=in_file, var_name='pr', out_unit='%', out_file=out_file, callback=callback.defaultCallback2)

            else:
                path_in_file = '/Users/xavier/Projets/data/test/v20170906/*.nc'
                in_file = glob.glob(path_in_file)
                in_file = "/Users/xavier/Projets/data/test/tasmax_day_CNRM-CM6-1_highresSST-present_r21i1p1f2_gr_19500101-19991231_version_3.nc"
                #pdb.set_trace()
                out_file = save_path+file[:-3]+"_"+slice_+"tete.nc"
                bp = [datetime.datetime(1950,1,1), datetime.datetime(1953,12,31)]
                #tr = [datetime.datetime(1970,1,1), datetime.datetime(1999,12,31)]
                icclim.indice(user_indice=user_indice, slice_mode='year', base_period_time_range=bp, in_files=in_file, var_name='tasmax', out_unit='%', ignore_Feb29th=True, out_file=out_file, callback=callback.defaultCallback2, save_percentile=True)
                #icclim.indice(indice_name=indice_2, slice_mode=slice_, time_range=tr, in_files=in_file, var_name='tasmax', ignore_Feb29th=True, out_file=out_file, callback=callback.defaultCallback2)

if __name__ == "__main__":
    netcdf_processing()

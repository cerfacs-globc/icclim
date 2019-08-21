from icclim import icclim
import pdb
import datetime
import glob
import json
from icclim.util import read

def netcdf_processing():

    save_path = '/Users/xavier/Projets/data/test/results/'
    path_json = "icclim/config_indice.json"

    with open(path_json) as json_data:
            data = json.load(json_data)

    #varname = 'tasmax'
    #slice_mode = 'year'
    out_file = save_path+"outfile_test.nc"
    list_indice = data['icclim']['indice'] 
    
    for indice_param in list_indice:
        print('Calulation: '+str(indice_param))
        if list_indice[indice_param]['indice_type']=='simple':
            tr = [datetime.datetime(1960,1,1), datetime.datetime(1980,12,31,13)]

            indice_param='HD17'
            if 'tas' in list_indice[indice_param]['var_name']:
                path_in_file='/Users/xavier/Projets/data/tasmax_day_CNRM-CM6-1-HR_highresSST-present_r1i1p1f2_gr_19500101-19591231.nc'
                #path_in_file = '/Users/xavier/Projets/data/test/tas_day_CMCC-CM_historical_r1i1p1_18500101_20051231.nc'#'/Users/xavier/Projets/data/usecase/tasmax_day_CSIRO-Mk3L-1-2_historical_r1i2p1_18510101_20051231.nc'
                icclim.indice(indice_name=indice_param,
                in_files=path_in_file, slice_mode='month', var_name='tasmax', ignore_Feb29th=False, 
                out_file=out_file)
            else:
                path_in_file = "/Users/xavier/Projets/data/test/pr_day_CNRM-CM6-1_highresSST-present_r21i1p1f2_gr_19500101-19991231.nc"

                icclim.indice(indice_name=indice_param, time_range = tr, base_period_time_range = tr,
                in_files=path_in_file, slice_mode='month', var_name='pr', ignore_Feb29th=False, 
                out_file=out_file)

if __name__ == "__main__":
    netcdf_processing()



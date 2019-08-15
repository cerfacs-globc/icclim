import numpy as np
from .. import maps
from .. import subset
import xarray as xr


def icclim_output_file_defaults(arg):
    # first embryo towards collecting certain stuff at a central place

    defaults = {'file_name'          : './icclim_out.nc',
                'netcdf_version'     : 'NETCDF3_CLASSIC',
                'variable_type_str'  : 'f4',
                'variable_calender'  : 'gregorian'}

    if defaults['variable_type_str'] in ['f', 'f4']:
        # 1.e20 is used by CMIP, otherwise the netCDF4 library default is preferrable 
        # as it can be recasted back and forth between float32 and float64
        # defaults['_FillValue'] = netCDF4.default_fillvals['f4']
        defaults['_FillValue'] = np.float32(1.e20)  
        defaults['missing_value'] = defaults['_FillValue']
        defaults['variable_type_name'] = 'float32' 
    else:
        # what goes here should be patterned from above, e.g.:
        # if defaults['variable_type'] in ['d', 'f8']:
        #     # defaults['_FillValue'] = netCDF4.default_fillvals['f8']
        #     defaults['_FillValue'] = numpy.float64(1.e20)  
        #     defaults['missing_value'] = defaults['_FillValue']
        #     defaults['variable_type_name'] = 'float64' 
        # else

        raise NotImplementedError('Coding error in function icclim_output_file_defaults: '
                                  + 'only "f" / "f4" / "float32" output is implemented')

    return defaults[arg]

def formatting_before_calculation(ds, var_name, indice_name, slice_mode):

    #TODO list all the check 
    if indice_name in maps.consecutive_days_indice:
        return subset.vectorize(ds, var_name, indice_name, slice_mode)    

    #check the system unit and convert it to the official unit from SU
    ds[indice_name] = check_system_unit(ds, indice_name)
    ds = xr.decode_cf(ds)
    da = ds[indice_name]

    if slice_mode in maps.season:
        da = ds[indice_name]
        return da[da.groupby(da['time.season']).groups[slice_mode]]
    else:
        return da


def check_system_unit(ds, indice_name):
    if ds[indice_name].units == 'degC' or ds[indice_name].units == 'Celsius': #Kelvin
        return ds[indice_name] + 273.15
    elif ds[indice_name].units in ["mm/s", "mm/sec", "kg m-2 s-1"]: # mm/s --> mm/day
        return ds[indice_name] * 86400.0
    else:
        return ds[indice_name]

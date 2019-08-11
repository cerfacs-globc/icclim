import xarray as xr
from collections import OrderedDict
from datetime import datetime
from icclim.util import read
import pdb

def copy_metadata(ds, ds_new, indice_name, slice_mode, time_range, var_name):

    #Extract the metadata related to the coordinate (time, lon, lat...)
    for coords in [*ds.coords]:
        ds_new[coords].attrs = ds[coords].attrs

    ds_new[indice_name].attrs = ds[var_name].attrs

    #Provide a description of the selected slice_mode
    if slice_mode == 'year':
        mode = 'annual time series'
    elif slice_mode == 'month':
        mode = 'monthly time series'
    elif slice_mode == 'DJF':
        mode = 'winter time series'
    elif slice_mode == 'MAM':
        mode = 'spring time series'
    elif slice_mode == 'JJA':
        mode = 'summer time series'
    elif slice_mode == 'SON':
        mode = 'autumn time series'
    elif slice_mode == 'ONDJFM':
        mode = 'winter half-year time series'
    elif slice_mode == 'AMJJAS':
        mode = 'summer half-year time series'

    #Get current date and formatting the time range
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    dt1 = time_range[0]
    dt2 = time_range[1]
    
    dt1_str = '{0}-{1}-{2}'.format(dt1.year, dt1.month, dt1.day)
    dt2_str = '{0}-{1}-{2}'.format(dt2.year, dt2.month, dt2.day)

    #Filling the metadata Orderdict for the netcdf creation
    new_attrs = OrderedDict()
    new_attrs['title'] = 'Index {0} with user defined threshold'.format(indice_name)
    new_attrs['reference']= 'ATBD of the ECA indices calculation (http://eca.knmi.nl/documents/atbd.pdf)'
    new_attrs['comment'] = ''
    new_attrs['institution']= 'Climate impact portal (http://climate4impact.eu)'
    new_attrs['history'] = '{0} Calculation of {1} indice ({2}) from {3} to {4}.'.format(current_time, indice_name, mode, dt1_str, dt2_str)
    new_attrs['Conventions'] = 'CF-1.6'

    str_origin = str(ds.attrs)
    str_origin = str_origin.replace("OrderedDict", "")
    new_attrs['source'] = str_origin

    ds_new.attrs = new_attrs

    return ds_new
     
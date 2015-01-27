from netCDF4 import MFDataset
import numpy
import util_dt

def get_total_array_size_bytes_and_tile_dimension(in_files, var_name, transfer_limit_bytes, time_range=None):
    '''
    Returns the total size of 3D variable array in bytes and the optimal tile dimension for spatial chunking.
    
    :param in_files: absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs)
    :type in_files: list
    
    :param var_name: variable name to process
    :type var_name: str
    
    :param transfer_limit_bytes: maximum OPeNDAP/THREDDS transfer limit in bytes to load OPeNDAP datasets (default: None) 
    :type transfer_limit_bytes: float
    
    :param time_range: time range
    :type time_range: list of 2 datetime objects: [dt1, dt2]
    
    rtype: tuple of float and int

    .. warning:: only for 3D variables
    
    '''
    
    in_files.sort()
    mfnc = MFDataset(in_files, 'r')
    
    ndim = mfnc.variables[var_name].ndim
    if ndim != 3:
        print "ERROR: The variable to process must be 3D"
        
    v = mfnc.variables[var_name]
    v_dtype = v.dtype
    v_nb_bytes = v_dtype.itemsize 
    if time_range == None:
        v_shape = v.shape
        
        total_array_size_bytes = v.shape[0] * v.shape[1] * v.shape[2] * v_nb_bytes
        optimal_tile_dimension = int(   numpy.sqrt( transfer_limit_bytes / (v.shape[0] * v_nb_bytes)  )   )
        
    else:
        var_time =  mfnc.variables['time']
        try:
           time_calend = var_time.calendar
        except:
            time_calend = 'gregorian'
        
        time_units = var_time.units
        time_arr = var_time[:]
        dt_arr = numpy.array([util_dt.num2date(dt, calend=time_calend, units=time_units) for dt in time_arr])
        indices_subset = util_dt.get_indices_subset(dt_arr, time_range)
        
        nb_time_steps_after_subset = len(indices_subset)
        total_array_size_bytes = nb_time_steps_after_subset * v.shape[1] * v.shape[2] * v_nb_bytes
        
        optimal_tile_dimension = int(   numpy.sqrt( transfer_limit_bytes / (nb_time_steps_after_subset * v_nb_bytes)  )   )
    
    mfnc.close()
    
    return (total_array_size_bytes, optimal_tile_dimension)

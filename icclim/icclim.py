# -*- coding: latin-1 -*-

'''
Python library "Index Calculation CLIMate"
Natalia Tatarinova: natalia.tatarinova@cerfacs.fr
'''


# sphinx-apidoc -o . ../test/sphinx    ## ->indices_v2.rst, modules.rst
# make html

import numpy
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num, Dataset
from netcdftime import utime
#from progressbar import ProgressBar,Percentage,Bar
import time


import ctypes
from numpy.ctypeslib import ndpointer



import os

my_rep = os.path.dirname(os.path.abspath(__file__)) + os.sep

libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')


def test():
    print my_rep




def get_list_dates_from_nc(nc, type_dates):
    
    '''
    Returns list of dates from NetCDF dataset.
    
    :param nc: NetCDF dataset
    :type nc: netCDF4.Dataset
    :param type_dates: type of dates ('dt' for datetime objects, 'num' for float objects) 
    :type type_dates: str

    :rtype: list of datetime/float 
    
    '''
    
    var_time = nc.variables['time']
    time_units = var_time.units # str (ex.: 'days since 1850-01-01 00:00:00')
    time_calend = var_time.calendar # str (ex.: 'standard'/'gregorian'/...)
    
    if type_dates == 'num':
        arr_dt = var_time[:]
        list_dt = arr_dt.tolist() # numpy array -> list
        
    if type_dates == 'dt':
        t = utime(time_units, time_calend) # <netcdftime.utime instance at 0xecae18>
        arr_dt = t.num2date(var_time[:]) # arr_dt: numpy array of dates datetime; var_time[:]: time values (ex.: [49323.5, 49353, 49382.5, ...])
        list_dt = arr_dt.tolist() # numpy array -> list
    del arr_dt
    
    return list_dt



def get_list_dates(ifile, type_dates):
    
    '''
    Returns list of dates from one file.
    
    :param ifile: NetCDF file
    :type ifile: str
    :param type_dates: type of dates ('dt' for datetime objects, 'num' for float objects) 
    :type type_dates: str

    :rtype: list of datetime/float 
    
    '''
    
    nc = Dataset(ifile, 'r')
    var_time = nc.variables['time']
    time_units = var_time.units # str (ex.: 'days since 1850-01-01 00:00:00')
    time_calend = var_time.calendar # str (ex.: 'standard'/'gregorian'/...)
    
    if type_dates == 'num':
        arr_dt = var_time[:]
        list_dt = arr_dt.tolist() # numpy array -> list
        
    if type_dates == 'dt':
        t = utime(time_units, time_calend) # <netcdftime.utime instance at 0xecae18>
        arr_dt = t.num2date(var_time[:]) # arr_dt: numpy array of dates datetime; var_time[:]: time values (ex.: [49323.5, 49353, 49382.5, ...])
        list_dt = arr_dt.tolist() # numpy array -> list
    del arr_dt
    
    nc.close()
    
    return list_dt


def get_list_dates2(ifile_list, type_dates):
    
    '''
    Returns list of dates from a list of files.
    
    :param ifile_list: list of NetCDF files
    :type ifile: list of str
    :param type_dates: type of dates ('dt' for datetime objects, 'num' for float objects) 
    :type type_dates: str

    :rtype: list of datetime/float 
    
    '''
    
    list_dates_glob = []
    for filename in ifile_list:
        list_dates_current = get_list_dates(filename, type_dates)
        list_dates_glob = list_dates_glob + list_dates_current
    list_dates_glob.sort()
    
    return list_dates_glob


def check_att(nc, att):
    
    '''    
    Checks if a global attribut exists in a dataset.
    
    :param nc: NetCDF dataset
    :type nc: netCDF4.Dataset 
    :param att: attribut name
    :type att: str
    
    :rtype: int (1 if attribut exists, 0 else)
    
    '''
    
    try:
        nc.__getattribute__(att)
        a = 1 # attribut exists
    except AttributeError:
        a = 0 # attribut doesn't exist
    return a


def copy_att(nc1, nc2, att):
    
    '''
    Copies a global attribut from one dataset (nc1) to another (nc2).
    
    :param nc1: from
    :type nc1: netCDF4.Dataset
    :param nc2: to
    :type nc2: netCDF4.Dataset

    '''
    
    nc2.__setattr__(att, '')
    if (check_att(nc1,att)==1):
        nc2.__setattr__(att, nc1.__getattribute__(att))
        

#def get_fill_value(nc, var):
#
#    v = nc.variables[var]
#    #print v.ncattrs()
#    fill_value =  v.getncattr('_FillValue')
#    return fill_value
#
#def get_calend_time(nc, var):
#    
#    v = nc.variables[var]
#    calend =  v.getncattr('calendar')
#    return calend
#
#def get_units_time(nc, var):
#    
#    v = nc.variables[var]
#    units =  v.getncattr('units')
#    return units

def get_att_value(nc, var, att):
    '''
    Returns an attribut value of a variable in dataset.
    
    :param nc: NetCDF dataset
    :type nc: netCDF4.Dataset
    :param var: variable name
    :type var: str
    :param att: attribut name
    :type var: str
    
    '''
    v = nc.variables[var]
    att_val = v.getncattr(att)
    return att_val



def date2num(dt, calend, units):
    '''
    type dt: datetime object
    '''
    t = utime(units, calend)
    dt_num = t.date2num(dt)
    return dt_num

def num2date(num, calend, units):
    '''
    type num: float date
    '''   
    t = utime(units, calend) 
    dt = t.num2date(num) 
    return dt



def set_time_values(nc, time_steps_arr_dt, calend, units):
    '''
    param time_steps_arr_dt: numpy array of datetime objects
    '''
    time_steps_num = numpy.array([date2num(i, calend, units) for i in time_steps_arr_dt])
    nc.variables['time'][:] = time_steps_num[:]


def set_timebnds_values(nc, time_bnds_dt, calend, units):    
    time_bnds_num = numpy.array([date2num(i, calend, units) for i in time_bnds_dt])
    nc.variables['time_bnds'][:,:] = time_bnds_num[:,:] 


#############
def copy_var_dim(inc, onc, var, project): 
    '''
    Copies the spacial coordinate variables (e.g.: lat, lon) of a variable (var) from one NetCDF file (ifile) to another (ofile)
    and returns list of coordinates variables.
    
    :param inc: input dataset
    :type inc: netCDF4.Dataset
    :param onc: output dataset
    :type onc: netCDF4.Dataset
    :param var: variable name to process
    :type var: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type project: str
    
    :rtype: tuple of str (coordinate variables: 'time', 'lat', 'lon')
    '''


    v = inc.variables[var]

    v_dim = v.dimensions # (e.g.: u'time', u'lat', u'lon')


    glob_att = ['title', 'institution', 'source', 'reference', 'comment', 'history']

    # Note: it needs to do it BEFORE the creation of var/dim
    for att in glob_att:
        copy_att(inc,onc,att)
       
    if v.ndim == 3: # (time, lat, lon)
        
        inc_dim0 = inc.variables[str(v_dim[0])]
        inc_dim1 = inc.variables[str(v_dim[1])]
        inc_dim2 = inc.variables[str(v_dim[2])]
        
        onc.createDimension(str(v_dim[0]), 0) # time       
        onc.createDimension(str(v_dim[1]), v.shape[1]) # lat
        onc.createDimension(str(v_dim[2]), v.shape[2]) # lon        
        onc.createDimension('tbnds', 2) # tbnds
        
        onc_dim0 = onc.createVariable( str(v_dim[0]), inc.variables[str(v_dim[0])].dtype, (str(v_dim[0])) ) # time
        onc_dim1 = onc.createVariable( str(v_dim[1]), inc.variables[str(v_dim[1])].dtype, (str(v_dim[1])) ) # lat
        onc_dim2 = onc.createVariable( str(v_dim[2]), inc.variables[str(v_dim[2])].dtype, (str(v_dim[2])) ) # lon
        
        
        
        onc_time_bnds = onc.createVariable( 'time_bnds', inc.variables[str(v_dim[0])].dtype, (str(v_dim[0]), 'tbnds') ) # time_bnds



        # time 
        for j in range(len(inc_dim0.ncattrs())): # set attributs of current variable       
            onc_dim0.__setattr__(  inc_dim0.__dict__.items()[j][0]  , inc_dim0.__dict__.items()[j][1])          
        # lat
        for j in range(len(inc_dim1.ncattrs())): # set attributs of current variable       
            onc_dim1.__setattr__(  inc_dim1.__dict__.items()[j][0]  , inc_dim1.__dict__.items()[j][1])  
        # lon
        for j in range(len(inc_dim2.ncattrs())): # set attributs of current variable       
            onc_dim2.__setattr__(  inc_dim2.__dict__.items()[j][0]  , inc_dim2.__dict__.items()[j][1])
        
        # for time_bnds, we copy only 2 attributs of time: 'units' and 'calendar' ( => var 'time' must have these 2 attributs)
        onc_time_bnds.__setattr__( 'units', inc_dim0.__getattribute__('units') )
        onc_time_bnds.__setattr__( 'calendar', inc_dim0.__getattribute__('calendar') )
        
        
        onc_dim1[:] = inc_dim1[:]
        onc_dim2[:] = inc_dim2[:]
        
        
        #######################
        if project == 'CORDEX':
        
            if check_att(v, 'coordinates')==1:
                a = str(v.__getattribute__('coordinates').split()[0])
                b = str(v.__getattribute__('coordinates').split()[1])
                
                inc_a = inc.variables[a]
                inc_b = inc.variables[b]
                
                onc_a = onc.createVariable( a, inc.variables[a].dtype, ( str(v_dim[1]), str(v_dim[2]) ) )
                onc_b = onc.createVariable( b, inc.variables[b].dtype, ( str(v_dim[1]), str(v_dim[2]) ) )
            
                for j in range(len(inc_a.ncattrs())): # set attributs of current variable       
                    onc_a.__setattr__(  inc_a.__dict__.items()[j][0]  , inc_a.__dict__.items()[j][1])
                    
                for j in range(len(inc_b.ncattrs())): # set attributs of current variable       
                    onc_b.__setattr__(  inc_b.__dict__.items()[j][0]  , inc_b.__dict__.items()[j][1])  
            
            if check_att(v, 'grid_mapping')==1:
                c = str(v.__getattribute__('grid_mapping'))
                inc_c = inc.variables[c]
                
                onc_c = onc.createVariable( c, inc.variables[c].dtype )
                
                for j in range(len(inc_c.ncattrs())): # set attributs of current variable       
                    onc_c.__setattr__(  inc_c.__dict__.items()[j][0]  , inc_c.__dict__.items()[j][1])
                    
                    
            onc_a[:,:] = inc_a[:,:]
            onc_b[:,:] = inc_b[:,:]
        
            onc_c = inc_c # ????        
                    
            
                
    return (str(v_dim[0]), str(v_dim[1]), str(v_dim[2])) # tuple ('time', 'lat', 'lon')


def max_sum_window(arr_1d, w_width):
    max_sum = -1
    for i in range(len(arr_1d)-w_width+1):
        w_current = a[i:i+w_width]
        sum_w_current =  w_current.sum()
        if sum_w_current >= max_sum:
            max_sum = sum_w_current
            
    return max_sum


#####################################################"
######### temperature indices

def TG_calculation(a, fill_val):
    
    '''    
    Calculates the TG indice: mean of daily mean temperature.
    
    :param a: daily mean temperature (e.g. "tas")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def TN_calculation(a, fill_val):
    
    '''    
    Calculates the TN indice: mean of daily min temperature.
    
    :param a: daily min temperature (e.g. "tasmin")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def TX_calculation(a, fill_val):
    
    '''    
    Calculates the TX indice: mean of daily max temperature.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice



def TXx_calculation(a, fill_val):
    
    '''    
    Calculates the TXx indice: max of daily max temperature.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.max(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice

def TNx_calculation(a, fill_val):
    
    '''    
    Calculates the TNx indice: max of daily min temperature.
    
    :param a: daily min temperature (e.g. "tasmin")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.max(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def TXn_calculation(a, fill_val):    
    '''    
    Calculates the TXn indice: min of daily max temperature.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''    
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.min(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice

def TNn_calculation(a, fill_val):    
    '''    
    Calculates the TNn indice: min of daily min temperature.
    
    :param a: daily min temperature (e.g. "tasmin")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''    
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.min(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def DTR_calculation(a, b, fill_val_a, fill_val_b):
    
    '''    
    Calculates the DTR indice: mean of diurnal temperature range.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param b: daily min temperature (e.g. "tasmin")
    :type b: numpy.ndarray (3D)
    
    :param fill_val_a: fill value of a (ref.: function "get_att_value")
    :type fill_val_a: float
    :param fill_val_b: fill value of b (ref.: function "get_att_value")
    :type fill_val_b: float
    
    :rtype: numpy.ndarray (2D)
    '''   
      
    mask_a = (a==fill_val_a)
    mask_b = (b==fill_val_b)
    mask_ab = mask_a | mask_b           # combined mask 
    
    # we mask each array with the combined mask
    a_masked = numpy.ma.masked_array(a, mask = mask_ab)
    b_masked = numpy.ma.masked_array(b, mask = mask_ab)
    
    range_ab = a_masked - b_masked 
    indice = range_ab.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val_a)               # <type 'numpy.ndarray'>
    return indice


def ETR_calculation(a, b, fill_val_a, fill_val_b):  
    '''    
    Calculates the ETR indice: intra-period extreme temperature range.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param b: daily min temperature (e.g. "tasmin")
    :type b: numpy.ndarray (3D)
    
    :param fill_val_a: fill value of a (ref.: function "get_att_value")
    :type fill_val_a: float
    :param fill_val_b: fill value of b (ref.: function "get_att_value")
    :type fill_val_b: float
    
    :rtype: numpy.ndarray (2D)
    '''   
    
    mask_a = (a==fill_val_a)
    mask_b = (b==fill_val_b)
    mask_ab = mask_a | mask_b           # combined mask 
    
    # we mask each array with the combined mask
    a_masked = numpy.ma.masked_array(a, mask = mask_ab)
    b_masked = numpy.ma.masked_array(b, mask = mask_ab)
    
    a_masked_max = a_masked.max(axis=0)
    b_masked_min = b_masked.min(axis=0)
    indice = a_masked_max - b_masked_min                        # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val_a)               # <type 'numpy.ndarray'>
    return indice


def vDTR_calculation(a, b, fill_val_a, fill_val_b):
    '''    
    Calculates the vDTR indice: mean absolute day-to-day difference in DTR.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param b: daily min temperature (e.g. "tasmin")
    :type b: numpy.ndarray (3D)
    
    :param fill_val_a: fill value of a (ref.: function "get_att_value")
    :type fill_val_a: float
    :param fill_val_b: fill value of b (ref.: function "get_att_value")
    :type fill_val_b: float
    
    :rtype: numpy.ndarray (2D)
    '''   
    
    mask_a = (a==fill_val_a)
    mask_b = (b==fill_val_b)
    mask_ab = mask_a | mask_b           # combined mask 
    
    # we mask each array with the combined mask
    a_masked = numpy.ma.masked_array(a, mask = mask_ab)
    b_masked = numpy.ma.masked_array(b, mask = mask_ab)
    
    c = a_masked[1:] - b_masked[1:]
    d = a_masked[:-1] - b_masked[:-1]
    e = abs(c-d)
    indice = e.mean(axis=0)                                     # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val_a)               # <type 'numpy.ndarray'>
    return indice


###### heat indices
def SU_calculation(a, fill_val):
    '''
    Calculates the SU indice: summer days (daily maximum temperature > 25 degrees Celsius) [days].
    
    :param a: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    t = 25          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]>T) # values>T -> 1, values<=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice
    
   
def CSU_calculation(a, fill_val):

    '''
    Calculates the CSU indice: maximum number of consecutive summer days (daily maximum temperature > 25 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''

    t = 25          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
    C_find_max_len_consec_sequence_3d.restype = None
    C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_char_p] 
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(a, a.shape[0], a.shape[1], a.shape[2], indice, T, fill_val, 'gt')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice    
    

def TR_calculation(a, fill_val):
    '''
    Calculates the TR indice: tropical nights (daily minimum temperature > 20 degrees Celsius) [days]. 
    
    :param a: daily min temperature (e.g. "tasmin") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    t = 20          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]>T) # values>T -> 1, values<=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


###### cold indices
def FD_calculation(a, fill_val):
    '''
    Calculates the FD indice: frost days (daily minimum temperature < 0 degrees Celsius) [days].
    
    :param a: daily min temperature (e.g. "tasmin") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 0           # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]<T) # values<T -> 1, values>=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice
    


def CFD_calculation(a, fill_val):

    '''
    Calculates the CFD indice: maximum number of consecutive frost days (daily minimum temperature < 0 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily min temperature (e.g. "tasmin") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''

    t = 0
    T = t + 273.15  # Celsius -> Kelvin
    
    C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
    C_find_max_len_consec_sequence_3d.restype = None
    C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_char_p] 
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(a, a.shape[0], a.shape[1], a.shape[2], indice, T, fill_val, 'lt')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice




def ID_calculation(a, fill_val):
    '''
    Calculates the ID indice: ice days (daily maximum temperature < 0 degrees Celsius) [days].
    
    :param a: daily max temperature (e.g. "tasmax") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 0           # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]<T) # values<T -> 1, values>=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def HD17_calculation(a, fill_val):
    '''
    Calculates the HD indice: heating degree days (sum of (17 degrees Celsius - daily mean temperature)).
    
    :param a: daily mean temperature (e.g. "tas") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 17          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    mask_a = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    a_masked = T - a_masked
    a_masked[a_masked<0]=0  # on annule les valeur qui etait < 0, i.e. tas_arr > T
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    indice[indice==0]=fill_val
    return indice


# !!! 
def GD4_calculation(a, fill_val):
    '''
    Calculates the GD indice: growing degree days (sum of daily mean temperature > 4 degrees Celsius).
    
    :param a: daily mean temperature (e.g. "tas") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 4          # temperature threshold (degree Celsius)    
    T = t + 273.15  # Celsius -> Kelvin
    b = a - T
    b[b<0]=0   
    indice = b.sum(axis=0)
    indice[indice==0]=fill_val
    return indice


### the GSL indice calculation is very slow => I will optimize with C #####
################################################################### GSL #################################
#
#def find_first_index_consecutive(a, min_len, threshold, operation):
#    '''
#    find the first index of a consecutive sequence (for the given condition)
#    in 1D numpy array
#    
#    : a                     1D numpy array
#    : min_len               minimum length of the consecutive sequence
#    : threshold             threshold value for a condition (units must be the same as in array)
#    : operation             logical operation ('e', 'gt', 'get', 'lt', 'let')
#    
#    : return                first index of a consecutive sequence
#    '''
#
#    first_ind = -1    
#    
#    if operation == 'e': # >
#        for i in range(len(a)-min_len+1):
#            if (a[i:i+min_len] == threshold).all() :
#                first_ind = i
#                break
#       
#    if operation == 'gt': # >
#        for i in range(len(a)-min_len+1):
#            if (a[i:i+min_len] > threshold).all() :
#                first_ind = i
#                break
#    
#    elif operation == 'get': # >=
#        for i in range(len(a)-min_len+1):
#            if (a[i:i+min_len] >= threshold).all() :
#                first_ind = i
#                break
#
#    elif operation == 'lt': # <
#        for i in range(len(a)-min_len+1):
#            if (a[i:i+min_len] < threshold).all() :
#                first_ind = i
#                break
#        
#    elif operation == 'let': # <
#        for i in range(len(a)-min_len+1):
#            if (a[i:i+min_len] <= threshold).all() :
#                first_ind = i
#                break    
#
#    return first_ind
#
#def count_nb_days(time_arr, index_from, index_to):
#    '''
#    count number of days between time_arr[index_from] and time_arr[index_to] 
#    
#    '''
#    dt_from = time_arr[index_from]
#    dt_to = time_arr[index_to]
#    
#    nb_days = (dt_to - dt_from).days
#    
#    return nb_days
#
#def GSL_point(a, time_arr, fill_val, t, ndays):
#    '''
#    growing season length (days) for one year
#    
#    : a                     1D numpy array of floats (temperature in Kelvin)
#    : time_arr              1D numpy array with datetime.datetime objects (must be for one year)
#    : t                     temperature threshold (degree Celsius, default: t = 5 Celsius)                        
#                            len(a)=len(time_arr)
#    : ndays                 number of consecutif days (default: ndays = 6)
#    '''
#    
#    time_arr.sort()
#    
#    # we want to find index of the first day of a consecutive sequence (>=6 days) where tempereture > 5 Celsius degrees  
#    index_from = find_first_index_consecutive(a, ndays, t+273.15, 'gt') # threshold = 5C + 273.15 [Kelvin]
#    #print index_from
#    
#    
#    # we want to find index of the first day of a consecutive sequence (>=6 days) where tempereture < 5 Celsius degrees
#    # after the 1st July
#    
#    current_year = time_arr[0].year # we get the year
#    time_arr2 = time_arr[ time_arr>=datetime(current_year, 07,1) ] # time_arr2 must be from 1st July
#    
#    # we want to find index (where time = 1st July) for subsetting of a
#    ind = len(time_arr) - len(time_arr2)
#    
#    # subsetting of a from ind: a = ([x x x x x ind x x x x])
#    a2 = a[ind:] # a2 = ([ind x x x x]) 
#
#    # index of the first day of a consecutive sequence (>=6 days) where tempereture < 5 Celsius degrees
#    # in a2 
#    index_a2 = find_first_index_consecutive(a2, ndays, t+273.15, 'lt') # if a2 == [] -> index_a2 = -1
#    
#    # index of the first day of a consecutive sequence (>=6 days) where tempereture < 5 Celsius degrees
#    # in a
#    if index_a2 == -1 or index_from == -1:
#        GSL = fill_val
#    
#    else:    
#        index_to = len(a) - len(a2) + index_a2
#        #print index_to
#
#        GSL = count_nb_days(time_arr, index_from, index_to)
#    
#    return GSL
#
#
#
#def GSL_calculation(a, time_arr, fill_val, t=5, ndays=6):
#    '''
#    : a                 3d array (here: tas mean)
#    : fill_val          fill value (usually: 1.0e+20)
#    : t                 temperature threshold (degree Celsius, default: t = 5 Celsius)
#    : ndays             number of consecutif days (default: ndays = 6)
#    
#    : return            2d array
#    '''
#    
#    T = t + 273.15 # Celsius -> Kelvin
#    
#    indice = numpy.empty(shape = (a.shape[1],a.shape[2]))
#
#    for i in range(indice.shape[0]):
#        for j in range(indice.shape[1]):
#            indice[i,j] = GSL_point(a[:,i,j], time_arr, fill_val, t, ndays)
#    return indice
#
######################################################################## end GSL ##################################

def GSL_calculation(a, fill_val):

    '''
    Calculates the GSL indice: ...
    '''

    t = 5 # temperature threshold (degree Celsius)
    T = t + 273.15 # Celsius -> Kelvin
    indexMiddleOfYear=181 # this should be calculated, this value is the normal value when size of time vector is 365. In this case, it corresponds to the 1st of July
    
    C_find_GSL_3d = libraryC.find_GSL_3d
    C_find_GSL_3d.restype = None
    C_find_GSL_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_int]
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_GSL_3d(a, a.shape[0], a.shape[1], a.shape[2], indice, T, fill_val, indexMiddleOfYear)
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice 
   
###### rain indices
def RR_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    indice = prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def RR1_calculation(prr_arr, fill_val, precip_thresh_mm=1):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    prr_daily[prr_daily<precip_thresh_mm]=0
    prr_daily[prr_daily>=precip_thresh_mm]=1
    indice=prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()


# ?
def SDII_calculation(prr_arr, fill_val, precip_thresh_mm=1):
    prr_arr[prr_arr==fill_val]=0
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    a = prr_daily
    a[prr_daily<precip_thresh_mm]=0
    
    b = a.sum(axis=0)
    c = (prr_daily>=precip_thresh_mm).sum(axis=0)
    indice = b/(c*1.0)
    return indice


def CDD_calculation(a, fill_val, precip_thresh=1):

    '''
    Calculates the indice CDD.
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily precipitation [mm/s]
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param precip_thresh: precipitation threshold (mm, default: precip_thresh = 1 mm)
    :type precip_thresh: float
    
    :rtype: numpy.ndarray (2D)
    '''

    
    b = a*60*60*24      # [mm/s] -> [mm/day]
    
    C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
    C_find_max_len_consec_sequence_3d.restype = None
    C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_char_p] 
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(b, a.shape[0], a.shape[1], a.shape[2], indice, precip_thresh, fill_val, 'lt')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice


def CWD_calculation(a, fill_val, precip_thresh=1):

    '''
    Calculates the indice CWD: maximum number of consecutive wet days (daily precipitation >= 1 mm).
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily precipitation (liquide phase) [mm/s]
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param precip_thresh: precipitation threshold [mm] (default: precip_thresh = 1 mm)
    :type precip_thresh: float
    
    :rtype: numpy.ndarray (2D)
    '''

    
    b = a*60*60*24      # [mm/s] -> [mm/day]
    
    C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
    C_find_max_len_consec_sequence_3d.restype = None
    C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_char_p] 
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(b, a.shape[0], a.shape[1], a.shape[2], indice, precip_thresh, fill_val, 'get')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice


def R10mm_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    prr_daily[prr_daily<10]=0
    prr_daily[prr_daily>=10]=1
    indice=prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def R20mm_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    prr_daily[prr_daily<20]=0
    prr_daily[prr_daily>=20]=1
    indice=prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def RX1day_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    indice = prr_daily.max(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()


def RX5day_calculation(prr_arr, fill_val):
    print "COUCOU!!!"
    #prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    #
    #indice = numpy.empty(shape = (prr_arr.shape[1],prr_arr.shape[2]))
    #
    #for i in range(indice.shape[1]):
    #    for j in range(indice.shape[2]):
    #        indice[i,j] = max_sum_window(prr_daily[:,i,j], 5)
    #### 
    #mask_fill_val = (prr_arr==fill_val).any(axis=0)
    #indice = numpy.ma.array(indice, mask=mask_fill_val)
    ####
    #return indice.filled()


###### snow indices    
def SD_calculation(prsn_arr, fill_val):
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    indice = prsn_daily.mean(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def SD1_calculation(prsn_arr, fill_val, thresh=1):
    '''
    :param thresh: snow deph threshold [cm]
    '''
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    prsn_daily[prsn_daily<thresh]=0
    prsn_daily[prsn_daily>=thresh]=1
    indice=prsn_daily.sum(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def SD5_calculation(prsn_arr, fill_val, thresh=5):
    '''
    :param thresh: snow deph threshold [cm]
    '''
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    prsn_daily[prsn_daily<thresh]=0
    prsn_daily[prsn_daily>=thresh]=1
    indice=prsn_daily.sum(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def SD50_calculation(prsn_arr, fill_val, thresh=50):
    '''
    :param thresh: snow deph threshold [cm]
    '''
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    prsn_daily[prsn_daily<thresh]=0
    prsn_daily[prsn_daily>=thresh]=1
    indice=prsn_daily.sum(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()



#### 

def TG_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily mean temperature')
    var_nc.setncattr('units', 'K')
    
def TN_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily minimum temperature')
    var_nc.setncattr('units', 'K')
    
def TX_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily maximum temperature')
    var_nc.setncattr('units', 'K')

def TXx_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Max of daily maximum temperature')
    var_nc.setncattr('units', 'K')

def TNx_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Max of daily minimum temperature')
    var_nc.setncattr('units', 'K')

def TXn_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Min of daily maximum temperature')
    var_nc.setncattr('units', 'K')

def TNn_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Min of daily minimum temperature')
    var_nc.setncattr('units', 'K')
    
def DTR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of diurnal temperature range')
    var_nc.setncattr('units', 'K')
    
def ETR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Intra-period extreme temperature range')
    var_nc.setncattr('units', 'K')
    
def vDTR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean absolute day-to-day difference in DTR (DTR: mean of diurnal temperature range)')
    var_nc.setncattr('units', 'K')

def SU_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Summer days (number of days where daily maximum temperature > 25 degrees)')
    var_nc.setncattr('units', 'days')

def TR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Tropical nights (number of days where daily minimum temperature > 20 degrees)')
    var_nc.setncattr('units', 'days')

def CSU_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive summer days(temperature > 25 degrees)')
    var_nc.setncattr('units', 'days')

def RR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Precipitation sum)')
    var_nc.setncattr('units', 'mm')

def RR1_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Wet days (precipitation >= 1 mm)')
    var_nc.setncattr('units', 'days')

def CWD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive wet days (precipitation >= 1 mm)')
    var_nc.setncattr('units', 'days')

def CDD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive dry days (precipitation < 1 mm)')
    var_nc.setncattr('units', 'days')

def SDII_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Simple daily intensity index for wet days (mm/wet day)')
    var_nc.setncattr('units', 'mm')

def R10mm_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Heavy precipitation days (precipitation >= 10 mm)')
    var_nc.setncattr('units', 'days')
    
def R20mm_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Very heavy precipitation days (precipitation >= 20 mm)')
    var_nc.setncattr('units', 'days')

def RX1day_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Highest 1-day precipitation amount')
    var_nc.setncattr('units', 'mm')

def RX5day_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Highest 5-day precipitation amount')
    var_nc.setncattr('units', 'mm')

def SD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily snow depth')
    var_nc.setncattr('units', 'cm')

def SD1_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of days where the snow depth >= 1 cm')
    var_nc.setncattr('units', 'days')
    
def SD5_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of days where the snow depth >= 5 cm')
    var_nc.setncattr('units', 'days')
    
def SD50_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of days where the snow depth >= 50 cm')
    var_nc.setncattr('units', 'days')

def FD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Frost days (minimum temperature < 0 degrees)')
    var_nc.setncattr('units', 'days')

def CFD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive frost days (minimum temperature < 0 degrees)')
    var_nc.setncattr('units', 'days')

def ID_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Ice days (maximum temperature < 0 degrees)')
    var_nc.setncattr('units', 'days')
    
def HD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Heating degree days (sum of 17 degrees - mean temperature)')
    var_nc.setncattr('units', 'K')
    
def GD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Growing degree days (sum of TG > 4 degrees)')
    var_nc.setncattr('units', 'K')    

def GSL_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Growing season length')
    var_nc.setncattr('units', 'days') 

####

def TG_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TG')

    
def TN_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TN')

    
def TX_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TX')


def TXx_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TXx')


def TNx_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TNx')


def TXn_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TXn')


def TNn_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice TNn')


def DTR_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice DTR')


def ETR_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice ETR')

    
def vDTR_setglobattr(onc):
    onc.setncattr('title', 'Temperature indice vDTR')


def SU_setglobattr(onc):
    onc.setncattr('title', 'Heat indice SU')


def TR_setglobattr(onc):
    onc.setncattr('title', 'Heat indice TR')

    
def CSU_setglobattr(onc):
    onc.setncattr('title', 'Heat indice CSU')

    
def RR_setglobattr(onc):
    onc.setncattr('title', 'Rain indice RR')

    
def RR1_setglobattr(onc):
    onc.setncattr('title', 'Rain indice RR1')
      

def CWD_setglobattr(onc):
    onc.setncattr('title', 'Rain indice CWD')


def CDD_setglobattr(onc):
    onc.setncattr('title', 'Drought indice CDD')


def SDII_setglobattr(onc):
    onc.setncattr('title', 'Rain indice SDII')


def R10mm_setglobattr(onc):
    onc.setncattr('title', 'Rain indice R10mm')

    
def R20mm_setglobattr(onc):
    onc.setncattr('title', 'Rain indice R20mm')
   

def RX1day_setglobattr(onc):
    onc.setncattr('title', 'Rain indice RX1day')


def RX5day_setglobattr(onc):
    onc.setncattr('title', 'Rain indice RX5day')


def SD_setglobattr(onc):
    onc.setncattr('title', 'Snow indice SD')


def SD1_setglobattr(onc):
    onc.setncattr('title', 'Snow indice SD1')


def SD5_setglobattr(onc):
    onc.setncattr('title', 'Snow indice SD5')


def SD50_setglobattr(onc):
    onc.setncattr('title', 'Snow indice SD50')


def FD_setglobattr(onc):
    onc.setncattr('title', 'Cold indice FD')


def CFD_setglobattr(onc):
    onc.setncattr('title', 'Cold indice CFD')


def ID_setglobattr(onc):
    onc.setncattr('title', 'Cold indice ID')
    
    
def HD_setglobattr(onc):
    onc.setncattr('title', 'Cold indice HD')

    
def GD_setglobattr(onc):
    onc.setncattr('title', 'Cold indice GD')

    
def GSL_setglobattr(onc):
    onc.setncattr('title', 'Cold indice GSL')


#########################################################################################

def get_all_years(time_steps_list):
    
    '''
    This function creates a list of all years from the input list of time steps.
    
    :param time_steps_list: time steps vector
    :type time_steps_list: list of datetime objects
    
    :rtype: list of datetime objects
    
    '''
    
    all_years = []
    for i in range(len(time_steps_list)):
        #new_date = datetime(time_steps_list[i].year,1,1) # begining of year date: 1st January
        new_date = datetime(time_steps_list[i].year,6,30) # middle of year date: 30th July
        if new_date not in all_years:
            all_years.append(new_date)
    return all_years


def get_all_months(time_steps_list):
    
    
    '''
    This function creates a list of all months from the input list of time steps.
    
    :param time_steps_list: time steps vector
    :type time_steps_list: list of datetime objects
    
    :rtype: list of datetime objects
    
    '''
    
    all_months = []
    for i in range(len(time_steps_list)):
        #new_date = datetime(dates[i].year,dates[i].month,1) # begining of month: 1st day
        new_date = datetime(time_steps_list[i].year,time_steps_list[i].month,15) # middle of month: 15th day
        if new_date not in all_months:
            all_months.append(new_date)
    return all_months

def get_time_bnds(time_step_dt, mode):
    
    '''
    This function returns an array with 2 time bounds (begin and end dates) of the input time step.
    
    :param time_step_dt: time step
    :type time_step_dt: datetime object
    :param mode: "year" or "month"
    :type mode: str
    
    :rtype: 1D numpy.ndarray with 2 datetime objects
    
    '''
    
    if (mode=='year'):
        time1= datetime(time_step_dt.year, 1,1) # 1st January
        time2= datetime(time_step_dt.year, 12,31,23,59,59) # 31th December
    elif (mode=='month'):
        if time_step_dt.month<12:
            next_month=datetime(time_step_dt.year, time_step_dt.month+1,1,23,59,59)
        else:
            #next_month=datetime(time_step_dt.year.year+1,1,1)
            next_month=datetime(time_step_dt.year+1,1,1,23,59,59)
        
        DD = timedelta(days=1)
        time1= datetime(time_step_dt.year, time_step_dt.month,1)
        time2= next_month- DD
        
    time_bnds = numpy.array([time1,time2])
    return time_bnds

def get_glob_time_bnds(time_steps_arr, mode):
    
    '''
    This function returns an array with time bounds (begin and end dates) of each time step from time_steps_arr.
    
    :param time_step_dt: time step
    :type time_step_dt: datetime object
    :param mode: "year" or "month"
    :type mode: str
    
    :rtype: 2D numpy.ndarray with datetime objects
    
    '''
    
    glob_time_bnds = numpy.array([])
    
    if (mode=='year'):
        for time_step in time_steps_arr:
            time_bnds_current = get_time_bnds(time_step,'year')
            glob_time_bnds = numpy.concatenate([glob_time_bnds, time_bnds_current])
    
    elif (mode=='month'):
        for time_step in time_steps_arr:
            time_bnds_current = get_time_bnds(time_step,'month')
            glob_time_bnds = numpy.concatenate([glob_time_bnds, time_bnds_current])
    
    glob_time_bnds = glob_time_bnds.reshape(-1,2)
    
    return glob_time_bnds

# on cree un dictionnaire : (annee -> sous-array3D avec seulement les donnees de cette annee)
def get_dict_year_3Darr(glob_3Darr, time_steps_list):
    
    '''
    This function returns a dictionary, where keys = years, and values = sub 3D arrays of glob_3Darr.
    
    :param glob_3Darr: global 3D array of values
    :type glob_3Darr: numpy.ndarray
    :param time_steps_list: global list of time steps
    :type time_steps_list: list of datetimeobjects
    
    :rtype: dictionary (keys: datetime object, values: numpy.ndarray)
    
    '''
    
    all_years=get_all_years(time_steps_list)
    mydict_years={}
    for i in range(len(all_years)):
        key = all_years[i] 
        bounds =get_time_bnds(all_years[i],'year')
        mask = (time_steps_list>=bounds[0]) & (time_steps_list<=bounds[1])
        value = glob_3Darr[mask,:,:]
        mydict_years[key]=value
    return mydict_years


# on cree un dictionnaire : (month -> sous-array3D avec seulement les donnees de ce month)
def get_dict_month_3Darr(glob_3Darr, time_steps_list):
    
    '''
    This function returns a dictionary, where keys = months, and values = sub 3D arrays of glob_3Darr.
    
    :param glob_3Darr: global 3D array of values
    :type glob_3Darr: numpy.ndarray
    :param time_steps_list: global list of time steps
    :type time_steps_list: list of datetimeobjects
    
    :rtype: dictionary (keys: datetime object, values: numpy.ndarray)
    
    '''
    
    all_months=get_all_months(time_steps_list)
    mydict_months={}
    for i in range(len(all_months)):
        key = all_months[i] 
        bounds =get_time_bnds(all_months[i],'month')
        mask = (time_steps_list>=bounds[0]) & (time_steps_list<=bounds[1])
        value = glob_3Darr[mask,:,:]
        mydict_months[key]=value
    return mydict_months


#def get_globindice(dict_indice, glob_3Darr):
#    glob_2Darr_indice = numpy.array([]) # 2D array = result of concatenation 
#    i=0
#    for key in sorted(dict_indice.keys()):
#        #print key.year
#        if i == 0:
#            glob_2Darr_indice = dict_indice[key]
#        else:
#            glob_2Darr_indice = numpy.concatenate([glob_2Darr_indice, dict_indice[key]], axis = 0)    
#        i+=1
#    glob_indice_3Darr= glob_2Darr_indice.reshape(len(dict_indice.keys()), glob_3Darr[0].shape[0],glob_3Darr[0].shape[1])
#        
#    glob_timeSteps_arr = sorted(dict_indice.keys())
#    
#    glob_timeSteps_arr = numpy.array(glob_timeSteps_arr) # list -> numpy array
#    
#    glob_indice = (glob_indice_3Darr,glob_timeSteps_arr) # tuple
#    
#    return glob_indice

def get_globindice(dict_indice, nb_rows, nb_columns):
    glob_2Darr_indice = numpy.array([]) # 2D array = result of concatenation 
    i=0
    for key in sorted(dict_indice.keys()):
        #print key.year
        if i == 0:
            glob_2Darr_indice = dict_indice[key]
        else:
            glob_2Darr_indice = numpy.concatenate([glob_2Darr_indice, dict_indice[key]], axis = 0)    
        i+=1
    glob_indice_3Darr= glob_2Darr_indice.reshape(len(dict_indice.keys()), nb_rows, nb_columns)
        
    glob_timeSteps_arr = sorted(dict_indice.keys())
    
    glob_timeSteps_arr = numpy.array(glob_timeSteps_arr) # list -> numpy array
    
    glob_indice = (glob_indice_3Darr,glob_timeSteps_arr) # tuple
    
    return glob_indice

def get_dict_timeStep_indice(dict_timeStep_sub3Darr,indice_name, fill_val, ind, onc):
    
    '''
    This function returns a dictionary, where keys = time step, and values = calculated indice (2D array).
    
    :param dict_timeStep_sub3Darr: dictionary where a sub 3D array associated for one time step
    :type dict_timeStep_sub3Darr: dict
    :param indice_name: name of an indice
    :type indice_name: str
    
    :rtype: dict (keys: datetime object, values: numpy.ndarray)
    
    '''
  
    mydict_indice={}
    
    for key in dict_timeStep_sub3Darr.keys():
        tab2D = eval(indice_name+'_calculation(dict_timeStep_sub3Darr[key], fill_val)')
        mydict_indice[key]=tab2D
    
    return mydict_indice


#def get_globValuesArr_sourceTimeArr_ocgis(ifiles_list, var, time_range, time_steps_type, N_lev):
#    # OCGIS    
#    
#    # attention: dt2 n'est pas inclue !!!
#    rd = ocgis.RequestDataset(ifiles_list, var, time_range=time_range)
#    arrs = ocgis.OcgOperations(dataset=rd, calc=None, output_format='numpy').execute()
#    
#    values = arrs[1].variables[var].value # attention! 4D (time, lev, lat, lon), next release -> 5D
#    if N_lev == None:
#        values = values.reshape(values.shape[0], values.shape[2], values.shape[3])
#    else:
#        values = values[:,N_lev,:,:]
#    
#    if time_steps_type=='dt':
#        time_steps = arrs[1].variables[var].temporal.value_datetime    # for datetime objects
#    elif time_steps_type=='num':
#        time_steps = arrs[1].variables[var].temporal.value                # for float objects
#   
#    valuesArr_sourceTimeArr = (values, time_steps)
#    
#    return valuesArr_sourceTimeArr # tuple with 2 numpy arr (values, time steps)
#



#def get_globValuesArr_sourceTimeArr_ja(ifiles_list, var, var_time, N_lev):
#    
#    '''
#    There is no yet time subsetting...
#    '''
#    
#    
#    v_glob = numpy.array([])
#
#    i=0
#    for filename in ifiles_list:
#        inc = Dataset(filename, 'r')
#        v_current = inc.variables[var]
#
#        if v_current.ndim == 3:
#            v_current_arr = v_current[:,:,:]
#        if v_current.ndim == 4:
#            v_current_arr = v_current[:,N_lev, :,:] # 4D -> 3D
#        
#        time_current = inc.variables[var_time]
#        time_current_arr = time_current[:]
#        
#        #print i
#        
#        if i == 0:
#            v_glob = v_current_arr
#            time_glob = time_current_arr
#        else:
#            v_glob = numpy.concatenate([v_glob, v_current_arr], axis = 0)
#            time_glob = numpy.concatenate([time_glob, time_current_arr])
#        #print v_glob.shape
#
#        i+=1
#        
#        inc.close()
#    
#    
#    #print v_glob.shape
#    #print time_glob.shape
#    
#    # now to convert time_glob from num to dt
#    
#    return (v_glob, time_glob)
    
def setglobattr_history(onc, indice_name, slice_mode, dt1, dt2):
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if slice_mode == 'year':
        mode = 'annual'
    if slice_mode == 'month':
        mode = 'monthly'
    
    # example of history_str_value: 2012-10-02 15:30:20 Calculation of SU indice (annual) from 1960-01-01 to 1990-12-31.
    history_str_value = current_time + ' Calculation of ' + indice_name + ' indice (' + mode + ') from ' + dt1.strftime('%Y-%m-%d') + ' to ' + dt2.strftime('%Y-%m-%d') + '.'

    onc.setncattr('history', history_str_value) 


def get_dict_year_chunk(time_steps_vect):
    
    '''    
    This function return a dictionnary with keys = year and tuple = (index1, index2) to chunk a global values array in years.
    index1 is begin index of chunk 
    index2 is end index of chunk
    
    For example, if we have have a values array for [2056, 2057, ... 2100] years,
    then the dictionnaly will look like: {2056: (0, 365), 2057: (366, 730), ... 2100: (16071, 16435)}
    
     :param time_steps_vect: 1d array
    :type time_steps_vect: numpy.ndarray    
    
    '''
    
    
    mydict = {}
    i = 0
    for time_step in time_steps_vect:
        if time_step.year not in mydict.keys():
            i1=i2=i
            mydict[time_step.year]=(i1,i2)
        else:
            i1 = mydict[time_step.year][0]
            i2 = mydict[time_step.year][1]+1
            mydict[time_step.year]=(i1,i2)
        i+=1
    return mydict
    



# GLOBAL FUNCTION       
def indice(ifiles_list, ofile, var, indice_name, time_range, slice_mode, project, N_lev=None):
    
    '''
    This function returns result NetCDF file containing a simple climate indice (based on one variable).
    
    
    :param ifiles_list: input NetCDF files
    :type ifiles_list: list of str
    :param ofile: output NetCDF file
    :type ofile: str
    :param var: variable name to process
    :type var: str
    :param indice_name: climate indice name
    :type indice_name: str
    :param time_range: time range (dt1 should be the first day of year/month, dt2 - the last day of year/month). Note: to include dt2 -> add in datetime hour/minute (HH=23, mm=59).
    :type time_range: list of 2 datetime objects [dt1, dt2]  
    :param slice_mode: "year" or "month" (soon: every month: "1", "2", "3",...; seasons: "DJF", "MAM", ...; winter half-year: "ONDJFM"; summer half-year: "AMMJJAS")
    :type slice_mode: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type slice_mode: str
    
    :rtype: output NetCDF file name (str)
    
    '''
    
    #print 'HUJ'
       
    inc = Dataset(ifiles_list[0], 'r')
    onc = Dataset(ofile, 'w')
    
    fill_val = get_att_value(inc, var, '_FillValue')

    indice_dim = copy_var_dim(inc, onc, var, project) # tuple ('time', 'lat', 'lon')
    
    nb_rows = inc.variables[indice_dim[1]].shape[0]
    #print nb_rows
    nb_columns = inc.variables[indice_dim[2]].shape[0]
    #print nb_columns

    
    calend = get_att_value(inc, indice_dim[0], 'calendar')
    units = get_att_value(inc, indice_dim[0], 'units')
    
    inc.close()

    ind_type = 'f'    
    ind = onc.createVariable(indice_name, ind_type, (indice_dim[0], indice_dim[1], indice_dim[2]), fill_value = fill_val)
    
    
    
    dt_begin = time_range[0] # datetime object
    dt_end = time_range[1]
    
    ############################
    glob_dict_timeStep_indice = {}
    ############################
    
    #j=0
    #pbar_files = ProgressBar(widgets=[Percentage(),' ', Bar()], maxval=len(ifiles_list)).start()
    
    for ifile in ifiles_list:
        
        
        #pbar_files.widgets[1]= ' processing file ' +str(j+1)
        #time.sleep(1.01)
        #pbar_files.update(j+1)
        #j+=1
        
        nc = Dataset(ifile, 'r')
        
        time_steps_vect = get_list_dates_from_nc(nc, 'dt') 
        
        dict_year_chunk = get_dict_year_chunk(time_steps_vect)   
        #print dict_year_chunk
        
        if N_lev==None:
            values = nc.variables[var]
        else:
            values = nc.variables[var][:,N_lev,:,:]
        
        
        #pbar = ProgressBar(widgets=['',Percentage(), Bar()], maxval=len(dict_year_chunk.keys())).start()
        #i=0
        
        for year in sorted(dict_year_chunk.keys()):
            
            #pbar.widgets[0]= ' <'+str(year)+' processed> '
            
            if year>=dt_begin.year and year<=dt_end.year:
                i1 = dict_year_chunk[year][0]
                i2 = dict_year_chunk[year][1]
                #print i1, i2
                values_current_chunk = values[i1:i2+1,:,:] # on charge les donnees (pour 1 annee) pour faire le traitement
                time_steps_current_chunk = numpy.array(time_steps_vect[i1:i2+1])
                
                
                if (slice_mode=='year'):
                    mydict_TimeStep_3DArray=get_dict_year_3Darr(values_current_chunk, time_steps_current_chunk)
                elif (slice_mode=='month'):
                    mydict_TimeStep_3DArray=get_dict_month_3Darr(values_current_chunk, time_steps_current_chunk)
                    
                
                mydict_indice=get_dict_timeStep_indice(mydict_TimeStep_3DArray, indice_name, fill_val, ind, onc)
                
                glob_dict_timeStep_indice.update(mydict_indice)
  
                del values_current_chunk, time_steps_current_chunk
  
  
  
                print "data processed ", year
                
            else:
                print "data not processed ", year


        #    time.sleep(0.01)
        #    #time.sleep(1.01)
        #    pbar.update(i+1)
        #    i+=1
        #
        #pbar.finish()
        
        nc.close()
        
        

    #pbar_files.finish()
        
    #print '---'    
    #print sorted(glob_dict_timeStep_indice.keys())
    #print '---'     
    
    glob_indice = get_globindice(glob_dict_timeStep_indice, nb_rows, nb_columns) # tuple (time_step_vect, indice_2D_arr)
    
    ind[:,:,:] = glob_indice[0][:,:,:]
    
    # set global attributs
    eval(indice_name + '_setglobattr(onc)')
    # for all:
    setglobattr_history(onc, indice_name, slice_mode, dt_begin, dt_end)
    onc.setncattr('institution', '')
    onc.setncattr('source', '')
    onc.setncattr('comment', '')   
    onc.setncattr('reference', '')
    
    # set variable attributs
    eval(indice_name + '_setvarattr(ind)')
    # for all:
    ind.missing_value = fill_val
    
    
    
    #print indice[1][:] # must be float or str!    
    #time_steps = [str(i) for i in indice[1][:]]
    
    time_steps_indice_dt = glob_indice[1][:]
    time_bnds_dt = get_glob_time_bnds(time_steps_indice_dt, slice_mode)
    
    set_time_values(onc, time_steps_indice_dt, calend, units)
    set_timebnds_values(onc, time_bnds_dt, calend, units)
    
    onc.close()
    
    return ofile

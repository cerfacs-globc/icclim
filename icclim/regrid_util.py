# coding=utf-8

import numpy
import ESMF
from netCDF4 import Dataset
from os.path import basename
import icclim

#esmpy = ESMF.Manager(logkind=ESMF.LogKind.MULTI, debug=True)

def get_regrided_var(f_src, f_dst, varname):
    '''
    :param f_src: netCDF file containing the variable to be regridded
    :type f_src: str
    
    :param f_dst: netCDF file containing the destination grid
    :type f_src: str
    
    :rtype: numpy.ndarra (3D)
    
    .. note:: If the variable has dimensions (a, b, c) and the destination grid is (d, e), then the output array will have the dimensions (a, d, e)
    '''


    esmpy = ESMF.Manager(logkind=ESMF.LogKind.MULTI, debug=True)
    
    #------------------------------------------------
    # Creating srcgrid and dstgrid
    #------------------------------------------------
    grid_src = ESMF.Grid(filename=f_src, 
                        filetype=ESMF.FileFormat.GRIDSPEC, add_corner_stagger=True)
    
    grid_dst = ESMF.Grid(filename=f_dst, 
                        filetype=ESMF.FileFormat.GRIDSPEC, add_corner_stagger=True)

    #------------------------------------------------
    # Creating srcfield and dstfield
    #------------------------------------------------
    field_src = ESMF.Field(grid_src, 'gridFrom')
    field_dst = ESMF.Field(grid_dst, 'gridTo')
    
    srcfracfield = ESMF.Field(grid_src, 'srcfracfield')
    dstfracfield = ESMF.Field(grid_dst, 'dstfracfield')
    
    srcareafield = ESMF.Field(grid_src, 'srcareaield')
    dstareafield = ESMF.Field(grid_dst, 'dstareafield')

    #------------------------------------------------
    # Create the regrid object ONLY ONCE
    #------------------------------------------------
    regridSrc2Dst = ESMF.Regrid(field_src, field_dst, 
                                    regrid_method=ESMF.RegridMethod.CONSERVE, 
                                    unmapped_action=ESMF.UnmappedAction.ERROR, 
                                    src_frac_field=srcfracfield, 
                                    dst_frac_field=dstfracfield)

    srcareafield.get_area()
    dstareafield.get_area()

    nc_src = Dataset(f_src, 'r')
    src_data = nc_src.variables[varname][:,:,:] # (time, lat, lon)
    nc_src.close()
    src_data_t = numpy.transpose(src_data, axes=[0,2,1]) # (time, lon, lat)

    time_steps_src = src_data_t.shape[0]
    
    dst_data = numpy.zeros((time_steps_src, field_dst.shape[0], field_dst.shape[1]))
    dst_data[:,:,:] = 1e20
       
    for time_step in range(time_steps_src):
        field_src.data[:,:] = src_data_t[time_step,:,:]
        dst_data[time_step,:,:] = regridSrc2Dst(field_src, field_dst)

    dst_data_t = numpy.transpose(dst_data, axes=[0,2,1])


    return dst_data_t


def write2netCDF_after_regridding(arr, f_src, f_dst, f_out, var_src, var_dst=None):

    '''
    Creates the f_out netCDF file with the variable "var_src" with "arr" values. 
    '''
    
    inc1 = Dataset(f_src, 'r')
    inc2 = Dataset(f_dst, 'r')
    
    if var_dst == None:
        var_dst = var_src
    
    var_f1 = inc1.variables[var_src]
    var_f2 = inc2.variables[var_dst]
    
    v1_dim = var_f1.dimensions   # (u'time', u'lat', u'lon')
    v2_dim = var_f2.dimensions   # (u'time', u'lat', u'lon')
    
    inc1_temporal = inc1.variables[str(v1_dim[0])]
    inc1_lat = inc1.variables[str(v1_dim[1])]
    inc1_lon = inc1.variables[str(v1_dim[2])]
    inc1_time_bnds = inc1.variables[str(inc1_temporal.__getattribute__('bounds'))]
    inc1_lat_bnds = inc1.variables[str(inc1_lat.__getattribute__('bounds'))]
    inc1_lon_bnds = inc1.variables[str(inc1_lon.__getattribute__('bounds'))]
    
    inc2_temporal = inc2.variables[str(v2_dim[0])]
    inc2_lat = inc2.variables[str(v2_dim[1])]
    inc2_lon = inc2.variables[str(v2_dim[2])]
    inc2_time_bnds = inc2.variables[str(inc2_temporal.__getattribute__('bounds'))]
    inc2_lat_bnds = inc2.variables[str(inc2_lat.__getattribute__('bounds'))]
    inc2_lon_bnds = inc2.variables[str(inc2_lon.__getattribute__('bounds'))]
    
    
    onc = Dataset(f_out, 'w')
    
    # create dimentions
    
    onc.createDimension(str(v1_dim[0]), 0) # 'time': the same as in src
    onc.createDimension(str(v1_dim[1]), var_f2.shape[1]) # 'lat': the same as in dst (after regridding)
    onc.createDimension(str(v1_dim[2]), var_f2.shape[2]) # 'lon': the same as in dst (after regridding)
    onc.createDimension('tbnds', 2) # tbnds
    onc.createDimension('nv', 2) # nv
    
    # create variables 
    onc_dim_temporal    = onc.createVariable(str(v1_dim[0]), inc1_temporal.dtype, (str(v1_dim[0])))
    onc_dim_lat         = onc.createVariable(str(v1_dim[1]), inc1_lat.dtype, (str(v1_dim[1])))
    onc_dim_lon         = onc.createVariable(str(v1_dim[2]), inc1_lon.dtype, (str(v1_dim[2])))
    onc_bnds_temporal   = onc.createVariable(str(inc1_temporal.__getattribute__('bounds')), inc1_time_bnds.dtype, (str(v1_dim[0]), 'tbnds'))
    onc_bnds_lat        = onc.createVariable(str(inc1_lat.__getattribute__('bounds')), inc1_lat_bnds.dtype, (str(v1_dim[1]), 'nv'))
    onc_bnds_lon        = onc.createVariable(str(inc1_lon.__getattribute__('bounds')), inc1_lon_bnds.dtype, (str(v1_dim[2]), 'nv'))
    
    onc_var             = onc.createVariable(var_src, var_f1.dtype, (str(v1_dim[0]), str(v1_dim[1]), str(v1_dim[2])) )
    
    onc_list_vars_temporal = [onc_dim_temporal, onc_bnds_temporal] # will be copied from the src dataset ( the same )
    inc1_list_vars_temporal = [inc1_temporal, inc1_time_bnds] 
    
    list_var_lat_lon = [onc_dim_lat, onc_dim_lon, onc_bnds_lat, onc_bnds_lon] # will be copied from the destination dataset ( after regridding )

    
    icclim.copy_var_attrs(inc1_temporal, onc_dim_temporal)
    onc_dim_temporal[:] = inc1_temporal[:]
    
    icclim.copy_var_attrs(inc1_time_bnds, onc_bnds_temporal)
    onc_bnds_temporal[:,:] = inc1_time_bnds[:,:]
    
    icclim.copy_var_attrs(inc2_lat, onc_dim_lat)
    onc_dim_lat[:] = inc2_lat[:]
    
    icclim.copy_var_attrs(inc2_lon, onc_dim_lon)
    onc_dim_lon[:] = inc2_lon[:]
    
    icclim.copy_var_attrs(inc2_lat_bnds, onc_bnds_lat)
    onc_bnds_lat[:,:] = inc2_lat_bnds[:,:]
    
    icclim.copy_var_attrs(inc2_lon_bnds, onc_bnds_lon)
    onc_bnds_lon[:,:] = inc2_lon_bnds[:,:]
    
    icclim.copy_var_attrs(var_f1, onc_var)
    onc_var[:,:,:] = arr
    
    
    #copy global attributes
    for att in inc1.ncattrs():
        icclim.copy_att(inc1, onc, att)
    
    
    onc.close()
    inc1.close()
    inc2.close()
    
    
    
def get_dst_resolution(file_list, resolution_type=1):
    
    '''
    Search the highest or lowest resolution.
    
    :param file_list: input netCDF files
    :type file_list: list of str
    
    :param resolution_type: if 1, function searchs the file with the highest resolution, if 0 - with the lowest resolution (default: 1)
    :type resolution_type: bool
    
    :rtype: tuple (nb_rows, nb_columns)
    
    '''
    
    # we open the first file in list
    nc = Dataset(file_list[0], 'r')
    v = nc.variables[varname]
    v_shape = v.shape
    nb_rows_prev = v_shape[-2]
    nb_columns_prev = v_shape[-1]
    
    res = (nb_rows_prev, nb_columns_prev)
    
    nc.close()
    
    # we check other files in list
    for f in file_list[1:]:
        nc = Dataset(f, 'r')
        v = nc.variables[varname]
        v_shape = v.shape
        nb_rows = v_shape[-2]
        nb_columns = v_shape[-1]

        
        if resolution_type == 0:
            if (nb_rows <= nb_rows_prev) and (nb_columns <= nb_columns_prev):
                res = (nb_rows, nb_columns)
                nb_rows_prev = nb_rows
                nb_columns_prev = nb_columns
            else:
                pass
            
            
        elif resolution_type == 1:
            if (nb_rows >= nb_rows_prev) and (nb_columns >= nb_columns_prev):
                res = (nb_rows, nb_columns)
                nb_rows_prev = nb_rows
                nb_columns_prev = nb_columns
            else:
                pass
        
                
        nc.close()
    
    return res



def get_dst_src_files(file_list, resolution_type):
    
    '''
    Create a tuple with 2 files lists: ([src_grid_files], [dst_grid_files])
    
    :param file_list: input netCDF files
    :type file_list: list
    
    :param resolution_type: if 1, function searchs the file with the highest resolution, if 0 - with the lowest resolution (default: 1)
    :type resolution_type: bool
    
    :rtype: tuple of 2 lists of files
    '''
    
    dst_res = get_dst_resolution(file_list, resolution_type=resolution_type) # (nb_rows, nb_columns)
    
    
    src_grid_files = []
    dst_grid_files = []

    
    for f in file_list:
        nc = Dataset(f, 'r')
        v = nc.variables[varname]
        v_shape = v.shape
        nb_rows = v_shape[-2]
        nb_columns = v_shape[-1]
        
        
        if (nb_rows != dst_res[0]) and (nb_columns != dst_res[1]):
            src_grid_files.append(f)
            
        elif (nb_rows == dst_res[0]) and (nb_columns == dst_res[1]):
            dst_grid_files.append(f)
               
                
        nc.close()
    
    #print src_grid_files
    #print dst_grid_files
    return (src_grid_files, dst_grid_files)

'''
# EXAMPLE
# WARNING: there will be bugs if "time", "lat", "lon" varibales have no the "bounds" attributes
# WARNING all files must have the same variable name

>>> f1 = '/home/globc/tatarinova/Downloads/tasmax_day_EC-EARTH_rcp26_r8i1p1_2077.nc'                    # 160 x 320
>>> f2 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_18550101-18591231.nc' # 128 x 256
>>> f3 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_20050101-20051231.nc' # 128 x 256
>>> f4 = '/home/globc/tatarinova/Downloads/tasmax_day_EC-EARTH_rcp26_r8i1p1_20770401_20770410.nc'       # 160 x 320
>>> 
>>> varname = 'tasmax'
>>> 
>>> # step 1: we are looking for the files which will be regridded
>>> a = get_dst_src_files(file_list=[f1, f3, f4, f2], resolution_type=1)
>>> 
>>> files_src_grid = a[0] # these files will be regridded (files with source grid)
>>> files_dst_grid = a[1] # these files will not be regridded (files with destination grid)
>>> 
>>> 
>>> # step 2: we regrid each file
>>> 
>>> f_dst = files_dst_grid[0]
>>> 
>>> regridded_files = []
>>> 
>>> for f in files_src_grid:
>>> 
>>>     arr = get_regrided_var(f_src=f, f_dst=f_dst, varname=varname)
>>>     
>>>     
>>>     # Where we will safe the regridded file: for example, in the current directory, and the name of regridded file is the same as source file + "_regridded"
>>>     
>>>     result_file_name = basename(f)+'_regridded'
>>> 
>>>     write2netCDF_after_regridding(arr, f_src=f, f_dst=f_dst, f_out=result_file_name, var_src=varname)
>>> 
>>>     regridded_files.append(result_file_name)
>>>         
>>>     print f, ' regridded !!!'
>>>     
>>> 
>>> # step 3: finally we get the list of files with the same grid
>>> file_list_final = files_dst_grid + regridded_files
>>> 
>>> print file_list_final

'''


f1 = '/data/tatarinova/tasmax_day_EC-EARTH_rcp26_r8i1p1_2077.nc'                                    # 160 x 320
f2 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_18550101-18591231.nc' # 128 x 256
f3 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_20050101-20051231.nc' # 128 x 256
f4 = '/data/tatarinova/tasmax_day_EC-EARTH_rcp26_r8i1p1_20770401-20770410.nc'                       # 160 x 320
f5 = '/home/globc/tatarinova/Downloads/tasmax_Amon_bcc-csm1-1_historical_r1i1p1_185001-201212.nc'   # 64 x 128

varname = 'tasmax'

# step 1: we are looking for the files which will be regridded
a = get_dst_src_files(file_list=[f1, f3, f4, f5, f2], resolution_type=1)

#a = get_dst_src_files(file_list=[f1, f3, f4, f2], resolution_type=1)

files_src_grid = a[0] # these files will be regridded (files with source grid)
files_dst_grid = a[1] # these files will not be regridded (files with destination grid)


# step 2: we regrid each file

f_dst = files_dst_grid[0]

regridded_files = []

for f in files_src_grid:
    print "==="
    print f
    print "==="
    
    arr = get_regrided_var(f_src=f, f_dst=f_dst, varname=varname)
    
    
    # Where we will safe the regridded file: for example, in the current directory, and the name of regridded file is the same as source file + "_regridded"
    
    result_file_name = basename(f)+'_regridded'

    write2netCDF_after_regridding(arr, f_src=f, f_dst=f_dst, f_out=result_file_name, var_src=varname)

    regridded_files.append(result_file_name)
        
    print f, ' regridded !!!'
    

# step 3: finally we get the list of files with the same grid
file_list_final = files_dst_grid + regridded_files

print file_list_final
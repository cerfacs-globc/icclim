# coding=utf-8

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova


import sys
import numpy
import ESMF
from netCDF4 import Dataset
#from os.path import basename
if sys.version_info[0] < 3:
    import util.util_nc as util_nc
else:
    from icclim.util import util_nc

#esmpy = ESMF.Manager(logkind=ESMF.LogKind.MULTI, debug=True)

'''
.. warning:: Works only with rectangular "lat/lon" grid

'''



def get_regridded_var(f_src, f_dst, varname):
    '''
    Returns a result of regridding.    

    :param f_src: netCDF file containing the variable to be regridded
    :type f_src: str
    
    :param f_dst: netCDF file containing the destination grid
    :type f_src: str
    
    :param varname: name of variable to process
    :type varname: str
    
    :rtype: numpy.ndarray (3D)
    
    .. note:: If the variable has dimensions (a, b, c) with ``a`` as time dimention and the destination grid is (d, e), then the output array will have the dimensions (a, d, e)
    
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
                                    unmapped_action=ESMF.UnmappedAction.IGNORE, 
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
    Writes a regridded variable in new netCDF file.
    
    :param arr: array containing the result of regridding
    :type arr: numpy.ndarray (3D)
    
    :param f_src: netCDF file containing the variable to be regridded
    :type f_src: str 
    
    :param f_dst: netCDF file containing the destination grid
    :type f_dst: str
    
    :param f_out: new netCDF file name containing the regridded variable
    :type f_out: str
    
    :param var_src: variable name in ``f_src``
    :type var src: str
    
    :param var_dst: name of the regridded variable in ``f_out``, if ``None`` then it will be the same as ``var_src`` 
    :type var_dst: str
    
    
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
    onc.createDimension('bnds', 2) # bnds
    onc.createDimension('nv', 2) # nv
    
    # create variables 
    onc_dim_temporal    = onc.createVariable(str(v1_dim[0]), inc1_temporal.dtype, (str(v1_dim[0])))
    onc_dim_lat         = onc.createVariable(str(v1_dim[1]), inc1_lat.dtype, (str(v1_dim[1])))
    onc_dim_lon         = onc.createVariable(str(v1_dim[2]), inc1_lon.dtype, (str(v1_dim[2])))
    onc_bnds_temporal   = onc.createVariable(str(inc1_temporal.__getattribute__('bounds')), inc1_time_bnds.dtype, (str(v1_dim[0]), 'bnds'))
    onc_bnds_lat        = onc.createVariable(str(inc1_lat.__getattribute__('bounds')), inc1_lat_bnds.dtype, (str(v1_dim[1]), 'nv'))
    onc_bnds_lon        = onc.createVariable(str(inc1_lon.__getattribute__('bounds')), inc1_lon_bnds.dtype, (str(v1_dim[2]), 'nv'))
    
    onc_var             = onc.createVariable(var_src, var_f1.dtype, (str(v1_dim[0]), str(v1_dim[1]), str(v1_dim[2])) )
    
    onc_list_vars_temporal = [onc_dim_temporal, onc_bnds_temporal] # will be copied from the src dataset ( the same )
    inc1_list_vars_temporal = [inc1_temporal, inc1_time_bnds] 
    
    list_var_lat_lon = [onc_dim_lat, onc_dim_lon, onc_bnds_lat, onc_bnds_lon] # will be copied from the destination dataset ( after regridding )

    
    util_nc.copy_var_attrs(inc1_temporal, onc_dim_temporal)
    onc_dim_temporal[:] = inc1_temporal[:]
    
    util_nc.copy_var_attrs(inc1_time_bnds, onc_bnds_temporal)
    onc_bnds_temporal[:,:] = inc1_time_bnds[:,:]
    
    util_nc.copy_var_attrs(inc2_lat, onc_dim_lat)
    onc_dim_lat[:] = inc2_lat[:]
    
    util_nc.copy_var_attrs(inc2_lon, onc_dim_lon)
    onc_dim_lon[:] = inc2_lon[:]
    
    util_nc.copy_var_attrs(inc2_lat_bnds, onc_bnds_lat)
    onc_bnds_lat[:,:] = inc2_lat_bnds[:,:]
    
    util_nc.copy_var_attrs(inc2_lon_bnds, onc_bnds_lon)
    onc_bnds_lon[:,:] = inc2_lon_bnds[:,:]
    
    util_nc.copy_var_attrs(var_f1, onc_var)
    onc_var[:,:,:] = arr
    
    
    #copy global attributes
    for att in inc1.ncattrs():
        util_nc.copy_att(inc1, onc, att)
    
    
    onc.close()
    inc1.close()
    inc2.close()
    
    
    
def get_dst_resolution(file_list, varname, resolution_type):
    
    '''
    Returns the destination grid.
    
    :param file_list: input netCDF files
    :type file_list: list of str
    
    :param resolution_type: if 1, the destination grid will be the highest resolution, if 0 - the lowest resolution
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



def get_dst_src_files(file_list, varname, resolution_type=1):
    
    '''
    Returns a tuple with 2 files lists: ([src_grid_files], [dst_grid_files])
    
    :param file_list: input netCDF files
    :type file_list: list
    
    :param resolution_type: if 1, the destination grid will be the highest resolution, if 0 - the lowest resolution (default: 1)
    :type resolution_type: bool
    
    :rtype: tuple of 2 lists of files
    '''
    
    dst_res = get_dst_resolution(file_list, varname, resolution_type=resolution_type) # (nb_rows, nb_columns)
    
    
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


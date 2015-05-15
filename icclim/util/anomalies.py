#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

import numpy
from netCDF4 import Dataset, MFDataset
from datetime import datetime

import icclim
import icclim.calc_indice as calc_indice


def defaultCallback(message,percentage):
    print ("[%s] %d" % (message,percentage))

# TODO: remove the "verbose" parameter
def get_mean_arr(in_files, var_name, time_range=None, transfer_limit_bytes=None, callback=None, mode=0):
    '''
    :param in_files: absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs)
    :type in_files: list of str
    
    :param var_name: variable name to process
    :type var_name: str
       
    :param time_range: time range 
    :type time_range: list of 2 datetime objects: [dt1, dt2]
    
    :param transfer_limit_bytes: maximum OPeNDAP/THREDDS request limit in bytes (default: None) 
    :type transfer_limit_bytes: float
    
    :param callback: callback print 
    :type callback: :func:`icclim.defaultCallback`
    
    :rtype: numpy.ndarray

    '''   
    
    percentage_anomalies_one_period = 50.
    
    in_files.sort()
    
    ###### to get fill value
    nc = Dataset(in_files[0], 'r')
    fill_val = icclim.get_att_value(nc, var_name, '_FillValue').astype('float32')
    nc.close()
    
    
    if transfer_limit_bytes == None: # i.e. we work with local files
        nc = MFDataset(in_files, 'r')
    
        var = nc.variables[var_name]    
        var_time = nc.variables['time']
        
        try:
           time_calend = var_time.calendar
        except:
            time_calend = 'gregorian'
        time_units = var_time.units    
    
        if time_range == None:
            arr = var[:,:,:]
            
        else:
            time_arr = var_time[:]
            dt_arr = numpy.array([icclim.num2date(dt, calend=time_calend, units=time_units) for dt in time_arr])
    
            indices_subset = icclim.get_indices_subset(dt_arr, time_range)
    
            #arr = var[indices_subset,:,:].squeeze()
            arr = var[indices_subset,:,:]
                    
        nc.close()
        
        

        arr_masked = calc_indice.get_masked_arr(arr, fill_val)        
        mean_arr_masked = numpy.ma.mean(arr_masked, axis=0)
        mean_arr = numpy.ma.filled(mean_arr_masked, fill_value=fill_val)
        
        if callback != None:
            if mode == 0:
                callback("Computing anomalies" , percentage_anomalies_one_period ) 
            elif mode == 1:
                callback("Computing anomalies" , percentage_anomalies_one_period + percentage_anomalies_one_period )
        
        del arr

    
    else: # i.e. we work with OPeNDAP datasets
        total_array_size_bytes_and_tile_dimension = icclim.get_total_array_size_bytes_and_tile_dimension(in_files, var_name, transfer_limit_bytes, time_range=time_range)
        array_total_size = total_array_size_bytes_and_tile_dimension[0]
        
        if array_total_size < transfer_limit_bytes: # the same as for the "if transfer_limit_bytes == None" case
            
            nc = MFDataset(in_files, 'r')
        
            var = nc.variables[var_name]    
            var_time = nc.variables['time']
            
            try:
               time_calend = var_time.calendar
            except:
                time_calend = 'gregorian'   
            time_units = var_time.units    
            
            print "Data transfer... "
            
            if time_range == None:
                arr = var[:,:,:]
                
            else:
                time_arr = var_time[:]
                dt_arr = numpy.array([icclim.num2date(dt, calend=time_calend, units=time_units) for dt in time_arr])
        
                indices_subset = icclim.get_indices_subset(dt_arr, time_range)
        
                arr = var[indices_subset,:,:].squeeze()

                        
            nc.close()
            
            arr_masked = calc_indice.get_masked_arr(arr, fill_val)        
            mean_arr_masked = numpy.ma.mean(arr_masked, axis=0)
            mean_arr = numpy.ma.filled(mean_arr_masked, fill_value=fill_val)
            
            
            if callback != None:
                if mode == 0:
                    callback("Computing anomalies" , percentage_anomalies_one_period ) 
                elif mode == 1:
                    callback("Computing anomalies" , percentage_anomalies_one_period + percentage_anomalies_one_period )
            
            
            del arr
            
        
        
        
            
        else:
            # then we do chunking in space
            tile_dimension = total_array_size_bytes_and_tile_dimension[1]
            #print tile_dimension
            nc = MFDataset(in_files, 'r')
            var = nc.variables[var_name]
            var_shape = var.shape
            var_shap1 = var_shape[1]
            var_shap2 = var_shape[2]
            
            var_time = nc.variables['time']
                
            try:
               time_calend = var_time.calendar
            except:
                time_calend = 'gregorian'
            time_units = var_time.units
            
            time_arr = var_time[:]
            dt_arr = numpy.array([icclim.num2date(dt, calend=time_calend, units=time_units) for dt in time_arr])
            
            
            tile_map = OCGIS_tile.get_tile_schema(nrow=var_shap1, ncol=var_shap2, tdim=tile_dimension, origin=0)
            nb_chunks = len(tile_map)
            print str(nb_chunks) + " data chunks will be transfered."

            ############## we initialize a glob mean_arr
            ############# where we will add mean arr of each chunk
            mean_arr = numpy.zeros((var_shap1, var_shap2))
            
            percentage_per_chunk = percentage_anomalies_one_period/nb_chunks
            
            percentage_current_chunk = 0
            
            chunk = 1.0  # chunk counter
           
            for tile_id in tile_map:
                print "Data transfer: chunk " + str(int(chunk)) + '/'+ str(len(tile_map)) + " ..."
                
                i1_row_current_tile = tile_map.get(tile_id).get('row')[0]
                i2_row_current_tile = tile_map.get(tile_id).get('row')[1]
                
                i1_col_current_tile = tile_map.get(tile_id).get('col')[0]
                i2_col_current_tile = tile_map.get(tile_id).get('col')[1]

                if time_range == None:
                    arr_current_chunk = var[:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile]

                else:
            
                    indices_subset = icclim.get_indices_subset(dt_arr, time_range)
                    
                    arr_current_chunk = var[indices_subset, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile].squeeze()

                arr_current_chunk_masked = calc_indice.get_masked_arr(arr_current_chunk, fill_val)        
                mean_arr_current_chunk_masked = numpy.ma.mean(arr_current_chunk_masked, axis=0)
                mean_arr_current_chunk = numpy.ma.filled(mean_arr_current_chunk_masked, fill_value=fill_val)
                
                
                
                del arr_current_chunk
                
                
                if callback != None:
                    percentage_current_chunk = percentage_current_chunk + percentage_per_chunk
                    if mode == 0:
                        callback("Computing anomalies" , percentage_current_chunk ) 
                    elif mode == 1:
                        callback("Computing anomalies" , percentage_anomalies_one_period + percentage_current_chunk )
                
                ########### we fill our glob mean_arr (chunk by chunk)

                mean_arr[i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = mean_arr_current_chunk

                chunk += 1
                
                
                               
            nc.close()
            
            mean_arr = mean_arr
            
       
    return mean_arr


########### write to netCDF


def write2netCDF_anomalies(arr, f_src, f_dst, time_range_future, time_range_past, var_src_name):

    '''
    Creates the f_dst netCDF file with the variable "var_dst" conteining "arr" values.
    
    .. warning:: arr should be 3D
    '''
    
    var_dst = 'anom_'+var_src_name
    
    inc = Dataset(f_src, 'r')
    
    var_src = inc.variables[var_src_name]
   
    dim_var_src = var_src.dimensions   # (u'time', u'lat', u'lon')

    
    inc_temporal = inc.variables[str(dim_var_src[0])]
    inc_lat = inc.variables[str(dim_var_src[1])]
    inc_lon = inc.variables[str(dim_var_src[2])]
    inc_time_bnds = inc.variables[str(inc_temporal.__getattribute__('bounds'))]
    inc_lat_bnds = inc.variables[str(inc_lat.__getattribute__('bounds'))]
    inc_lon_bnds = inc.variables[str(inc_lon.__getattribute__('bounds'))]
   
    
    onc = Dataset(f_dst, 'w')
    
    # create dimentions
    
    onc.createDimension(str(dim_var_src[0]), 0) # 'time'
    onc.createDimension(str(dim_var_src[1]), var_src.shape[1]) # 'lat' 
    onc.createDimension(str(dim_var_src[2]), var_src.shape[2]) # 'lon'
    onc.createDimension('bnds', 2) # 'bnds'
    onc.createDimension('nv', 2) # 'nv'
    
    # create variables 
    onc_dim_temporal    = onc.createVariable(str(dim_var_src[0]), inc_temporal.dtype, (str(dim_var_src[0])))
    onc_dim_lat         = onc.createVariable(str(dim_var_src[1]), inc_lat.dtype, (str(dim_var_src[1])))
    onc_dim_lon         = onc.createVariable(str(dim_var_src[2]), inc_lon.dtype, (str(dim_var_src[2])))
    onc_bnds_temporal   = onc.createVariable(str(inc_temporal.__getattribute__('bounds')), inc_time_bnds.dtype, (str(dim_var_src[0]), 'bnds'))
    onc_bnds_lat        = onc.createVariable(str(inc_lat.__getattribute__('bounds')), inc_lat_bnds.dtype, (str(dim_var_src[1]), 'nv'))
    onc_bnds_lon        = onc.createVariable(str(inc_lon.__getattribute__('bounds')), inc_lon_bnds.dtype, (str(dim_var_src[2]), 'nv'))
    
    fill_val = icclim.get_att_value(inc, var_src_name, '_FillValue')
    onc_var             = onc.createVariable(var_dst, var_src.dtype, (str(dim_var_src[0]), str(dim_var_src[1]), str(dim_var_src[2])), fill_value = fill_val)
    
    
    onc_dim_temporal_ref    = onc.createVariable(str(dim_var_src[0])+"_ref", inc_temporal.dtype, (str(dim_var_src[0])))
    onc_bnds_temporal_ref   = onc.createVariable(str(inc_temporal.__getattribute__('bounds'))+"_ref", inc_time_bnds.dtype, (str(dim_var_src[0]), 'bnds'))
    
    
    
    ########### we convert time range to numerical values to write them to the bounds
    try:
        calend = inc_temporal.calendar
    except:
        calend = 'gregorian'
    
    units = inc_temporal.units
    
    time_range_future_num = numpy.array([icclim.date2num(i, calend, units) for i in time_range_future])
    time_range_past_num = numpy.array([icclim.date2num(i, calend, units) for i in time_range_past])
    
    time_range_future_num = numpy.expand_dims(time_range_future_num, axis=0)
    time_range_past_num = numpy.expand_dims(time_range_past_num, axis=0)
       
    # time
    icclim.copy_var_attrs(inc_temporal, onc_dim_temporal)
    onc_dim_temporal[:] = time_range_future_num[0,0] + (time_range_future_num[0,1] - time_range_future_num[0,0])/2   # middle of time_range 
    
    # time_bnds    
    icclim.copy_var_attrs(inc_time_bnds, onc_bnds_temporal)
    onc_bnds_temporal[:,:] = time_range_future_num[:,:]
    # in case if time_bnds has no attributes, we copy "units" and "calendar" attributes from "time" variable    
    onc_bnds_temporal.setncattr("units", inc_temporal.getncattr("units") )
    onc_bnds_temporal.setncattr("calendar", inc_temporal.getncattr("calendar") )
    
    # time_ref
    onc_dim_temporal_ref[:] = time_range_past_num[0,0] + (time_range_past_num[0,1] - time_range_past_num[0,0])/2   # middle of time_range
    
    onc_dim_temporal_ref.setncattr("long_name", "Time of the reference period")
    onc_dim_temporal_ref.setncattr("bounds", str(inc_temporal.__getattribute__('bounds'))+"_ref")
    # we copy "units" and "calendar" attributes from "time" variable    
    onc_dim_temporal_ref.setncattr("units", inc_temporal.getncattr("units") )
    onc_dim_temporal_ref.setncattr("calendar", inc_temporal.getncattr("calendar") )  
    
    # time_bnds_ref    
    onc_bnds_temporal_ref[:,:] = time_range_past_num[:,:]
    
    onc_bnds_temporal_ref.setncattr("long_name", "Time bounds of the reference period")
    # we copy "units" and "calendar" attributes from "time" variable    
    onc_bnds_temporal_ref.setncattr("units", inc_temporal.getncattr("units") )
    onc_bnds_temporal_ref.setncattr("calendar", inc_temporal.getncattr("calendar") )    
    
    
    
    icclim.copy_var_attrs(inc_lat, onc_dim_lat)
    onc_dim_lat[:] = inc_lat[:]
    
    icclim.copy_var_attrs(inc_lon, onc_dim_lon)
    onc_dim_lon[:] = inc_lon[:]
    
    icclim.copy_var_attrs(inc_lat_bnds, onc_bnds_lat)
    onc_bnds_lat[:,:] = inc_lat_bnds[:,:]
    
    icclim.copy_var_attrs(inc_lon_bnds, onc_bnds_lon)
    onc_bnds_lon[:,:] = inc_lon_bnds[:,:]
    
    #icclim.copy_var_attrs(var_src, onc_var)
    
    onc_var[:,:,:] = arr
    onc_var.setncattr("long_name", "Anomalies of " + var_src_name)
    onc_var.setncattr("units", var_src.getncattr("units") )
    onc_var.setncattr("reference_period", str(inc_temporal.__getattribute__('bounds'))+"_ref")    
    
    #copy global attributes
    for att in inc.ncattrs():
        icclim.copy_att(inc, onc, att)
    
    
    
    ############ update "history" global attribute
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    

    dt1f_year = time_range_future[0].year
    dt2f_year = time_range_future[1].year
    
    dt1p_year = time_range_past[0].year
    dt2p_year = time_range_past[1].year
    
    history_str = '{0} Computing of {1} anomalies over the period {2} - {3} with the reference period {4} - {5}.'.format(current_time, var_src_name, str(dt1f_year), str(dt2f_year), str(dt1p_year), str(dt2p_year))

    onc.setncattr('history', getattr(onc,'history') + ' \n ' + history_str)

    
    onc.close()
    inc.close()




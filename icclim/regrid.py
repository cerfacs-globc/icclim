# -*- coding: utf-8 -*-
import regrid_util
from os.path import basename

# Input files of different resolution

f1 = '/data/tatarinova/tasmax_day_EC-EARTH_rcp26_r8i1p1_2077.nc'                                    # 160 x 320
f2 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_18550101-18591231.nc' # 128 x 256
f3 = '/data/tatarinova/CMIP5/tasmax_day/tasmax_day_CNRM-CM5_historical_r1i1p1_20050101-20051231.nc' # 128 x 256
f4 = '/data/tatarinova/tasmax_day_EC-EARTH_rcp26_r8i1p1_20770401-20770410.nc'                       # 160 x 320
f5 = '/home/globc/tatarinova/Downloads/tasmax_Amon_bcc-csm1-1_historical_r1i1p1_185001-201212.nc'   # 64 x 128

var = 'tasmax'

# step 1: we are looking for the files which will be regridded:
# if resolution_type=1, then the highest resolution grid will be chosen from the input grids as a destination grid (in our case: 160 x 320)
# if resolution_type=0, then the lowest resolution grid will be chosen from the input grids as a destination grid (in our case: 64 x 128)
a = regrid_util.get_dst_src_files(file_list=[f1, f3, f4, f5, f2], varname=var, resolution_type=0) 


files_src_grid = a[0] # these files will be regridded (files with source grid)
files_dst_grid = a[1] # these files will not be regridded (files with destination grid)


# step 2: we regrid each file

file_dst = files_dst_grid[0]

regridded_files = [] # we initialize a list of regridded files

for f in files_src_grid:
    
    arr = regrid_util.get_regrided_var(f_src=f, f_dst=file_dst, varname=var)
    
    
    # Where we will safe the regridded file: for example, in the current directory, and the name of regridded file is the same as source file + "_regridded" before
    
    result_file_name = 'regridded_' + basename(f)

    regrid_util.write2netCDF_after_regridding(arr, f_src=f, f_dst=file_dst, f_out=result_file_name, var_src=var)

    regridded_files.append(result_file_name) # we add each regridded file to the list
        
    print f, ' regridded!'
    

# step 3: finally we get the list of files with the same grid
file_list_final = files_dst_grid + regridded_files

print file_list_final
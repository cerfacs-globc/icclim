# but: copier toutes les variables et leurs attributs sauf la variable qu'on va traiter
# dans le cas 4D -> 3D

# mettre dans le doc:
# Before the treatment ICCLIM prepares the output NetCDF file,
# i.e. it copies all the coordinate variables and their attributs


from icclim import *
from netCDF4 import *

# CMIP5
file_cmip5 = '/data/tatarinova/CMIP5/tas_day/tas_day_CNRM-CM5_historical_r1i1p1_18550101-18591231.nc'
#file_cmip5 = '/data/tatarinova/CMIP5/vas_day/vas_day_CNRM-CM5_historical_r1i1p1_19500101-19541231.nc'
#file_cmip5 = '/data/tatarinova/CMIP5/pr_day_CNRM-CM5_piControl_r1i1p1_18500101-18541231.nc'

# CORDEX
file_cordex = '/data/tatarinova/CORDEX/AFR/tas_day/tas_AFR-44_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_day_19910101-19951231.nc'
#file_cordex = '/data/tatarinova/CORDEX/AFR/tas_day/tas_AFR-44_ECMWF-ERAINT_evaluation_r1i1p1_SMHI-RCA4_v1_day_20010101-20051231.nc'

# 4D
file_4d = '/data/tatarinova/4d/ta_day_CNRM-CM5_rcp85_r1i1p1_20060101-20101231.nc'

infile = file_cmip5
outfile = '/data/tatarinova/tmp/res/test_copy_metadata.nc'

inc = Dataset(infile, 'r')
onc = Dataset(outfile, 'w')


def copy_metadata(inc, onc, var):
    t
    



############################################################################
############################################################################
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


    glob_att = ['title', 'institution', 'source', 'reference', 'comment', 'history', 'experiment']

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
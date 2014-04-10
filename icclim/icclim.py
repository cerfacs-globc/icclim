# -*- coding: latin-1 -*-

'''
Python library "Index Calculation CLIMate"
Natalia Tatarinova: natalia.tatarinova@cerfacs.fr
'''

import numpy
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num, Dataset
from netcdftime import utime
#from progressbar import ProgressBar,Percentage,Bar
import time

import calc_indice
import set_globattr
import set_longname_units



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
    Copies the spacial coordinate variables (e.g.: lat, lon) of a variable (var) from one NetCDF file (ifile) to another (out_file)
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


    glob_att = ['title', 'institution', 'source', 'references', 'comment', 'history']
    
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


def get_all_years(time_steps_list):
    
    '''
    This function creates a list of all years from the input list of time steps.
    
    :param time_steps_list: time steps vector
    :type time_steps_list: list of datetime objects
    
    :rtype: list of datetime objects (cenroid: 30th June of each year)
    
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
    
    :rtype: list of datetime objects (cenroid: 16th day of each month)
    
    '''
    
    all_months = []
    for i in range(len(time_steps_list)):
        #new_date = datetime(dates[i].year,dates[i].month,1) # begining of month: 1st day
        new_date = datetime(time_steps_list[i].year,time_steps_list[i].month,16) # middle of month: 16th day
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
        time_bnd1= datetime(time_step_dt.year, 1,1) # 1st January
        #time_bnd2= datetime(time_step_dt.year, 12,31,23,59,59) # 31th December
        time_bnd2= datetime(time_step_dt.year+1, 1,1) # 1st January next year (this time_bnd will be excluded)
    elif (mode=='month'):
        if time_step_dt.month<12:
            #next_month=datetime(time_step_dt.year, time_step_dt.month+1,1,23,59,59)
            next_month=datetime(time_step_dt.year, time_step_dt.month+1,1)
        else:
            #next_month=datetime(time_step_dt.year.year+1,1,1)
            #next_month=datetime(time_step_dt.year+1,1,1,23,59,59)
            next_month=datetime(time_step_dt.year+1,1,1) # i.e. if month = december => next_month = january of next year
        
        #DD = timedelta(days=1)
        #time_bnd1= datetime(time_step_dt.year, time_step_dt.month,1)
        #time_bnd2= next_month- DD
        time_bnd1 = datetime(time_step_dt.year, time_step_dt.month,1)
        time_bnd2 = next_month
        
    time_bnds = numpy.array([time_bnd1,time_bnd2])
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
        tab2D = eval('calc_indice.' + indice_name + '_calculation(dict_timeStep_sub3Darr[key], fill_val)')
        mydict_indice[key]=tab2D
    
    return mydict_indice


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

    
#def defaultCallback(message,percentage):
#    print ("[%s] %d" % (message,percentage))


# GLOBAL FUNCTION       
def indice(in_files,
           out_file,
           var,
           indice_name,
           time_range,
           slice_mode,
           project,
           N_lev=None,
           callback=None):
    
    '''
    This function returns result NetCDF file containing a simple climate indice (based on one variable).
    
    
    :param in_files: input NetCDF files
    :type in_files: list of str
    :param out_file: output file name
    :type out_file: str
    :param var: variable name to process
    :type var: str
    :param indice_name: climate indice name
    :type indice_name: str
    :param time_range: time range (dt1 should be the first day of year/month, dt2 - the last day of year/month). Note: to include dt2 -> add in datetime hour/minute (HH=23, mm=59).
    :type time_range: list of 2 datetime objects [dt1, dt2]  
    :param slice_mode: "year" or "month" 
    :type slice_mode: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type slice_mode: str
    
    :rtype: output NetCDF file name (str)
    
    '''
    
    #print "DADA"
       
    #callback("Init Opening "+in_files[0],0);
    inc = Dataset(in_files[0], 'r')
    #callback("Finished opening "+in_files[0],0);
    
    onc = Dataset(out_file, 'w' ,format="NETCDF3_CLASSIC")
    
    fill_val = get_att_value(inc, var, '_FillValue')

    indice_dim = copy_var_dim(inc, onc, var, project) # tuple ('time', 'lat', 'lon')
    
    nb_rows = inc.variables[indice_dim[1]].shape[0]
    nb_columns = inc.variables[indice_dim[2]].shape[0]
    
    calend = get_att_value(inc, indice_dim[0], 'calendar')
    units = get_att_value(inc, indice_dim[0], 'units')
    
    inc.close()

    ind_type = 'f'    
    ind = onc.createVariable(indice_name, ind_type, (indice_dim[0], indice_dim[1], indice_dim[2]), fill_value = fill_val)
       
    
    dt_begin = time_range[0] # datetime object
    dt_end = time_range[1] # datetime object
    
    ############################
    glob_dict_timeStep_indice = {}
    ############################
    
    #j=0
    #pbar_files = ProgressBar(widgets=[Percentage(),' ', Bar()], maxval=len(in_files)).start()
    
    total_nb_years_to_process = dt_end.year -dt_begin.year + 1
    
    for ifile in in_files:
        
        
        #pbar_files.widgets[1]= ' processing file ' +str(j+1)
        #time.sleep(1.01)
        #pbar_files.update(j+1)
        #j+=1
        
        #callback("Opening "+ifile,0);
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
        
        currentStep=1
        totalSteps=len(dict_year_chunk.keys())
        
        counter_year = 0
        for year in sorted(dict_year_chunk.keys()):
            
            #pbar.widgets[0]= ' <'+str(year)+' processed> '
            
            percentageComplete = (currentStep/totalSteps)*100
            #callback("Processing year %d/%d %d" % (currentStep,totalSteps,year),percentageComplete)
            
            if year>=dt_begin.year and year<=dt_end.year:
                
                #callback("Processing year %d/%d %d" % (currentStep,totalSteps,year),percentageComplete)
                
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
  
                print "Processed: ", year
                
                #counter_year = counter_year + 1
                #print counter_year, total_nb_years_to_process

                #status = "Year processed {0}/{1} ({3})".format(counter_year, total_nb_years_to_process, year)
                #print status
                
            #else:
                #print "data not processed ", year
                #callback("Skipping year %d" % year,percentageComplete)

            #time.sleep(0.01)
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
    #eval(indice_name + '_setglobattr(onc)')
    ## for all:
    #setglobattr_history(onc, indice_name, slice_mode, dt_begin, dt_end)
    #onc.setncattr('institution', '')
    onc.setncattr('source', '') # Here soon will be source meta data
    #onc.setncattr('comment', '')   
    #onc.setncattr('reference', '')
    
    # set global attributs
    set_globattr.title(onc, indice_name)
    set_globattr.references(onc)
    set_globattr.comment(onc, indice_name)
    set_globattr.institution(onc, institution_str='Climate impact portal (http://climate4impact.eu)')
    set_globattr.history2(onc, slice_mode, indice_name, time_range)

    # set variable attributs
    eval('set_longname_units.' + indice_name + '_setvarattr(ind)')
    # for all:
    ind.missing_value = fill_val
    

    #print indice[1][:] # must be float or str!    
    #time_steps = [str(i) for i in indice[1][:]]
    
    time_steps_indice_dt = glob_indice[1][:]
    time_bnds_dt = get_glob_time_bnds(time_steps_indice_dt, slice_mode)
    
    set_time_values(onc, time_steps_indice_dt, calend, units)
    set_timebnds_values(onc, time_bnds_dt, calend, units)
    
    onc.close()
    
    return out_file



####################################################

def get_dict_timeStep_indice_multivar(dict_timeStep_sub3Darr1, dict_timeStep_sub3Darr2, indice_name, fill_val1, fill_val2, ind, onc):
    
    '''
    This function returns a dictionary, where keys = time step, and values = calculated indice (2D array).
    
    :param dict_timeStep_sub3Darr1: dictionary where a sub 3D array associated for one time step
    :type dict_timeStep_sub3Darr1: dict
    :param dict_timeStep_sub3Darr2: dictionary where a sub 3D array associated for one time step
    :type dict_timeStep_sub3Darr2: dict
    :param indice_name: climate indice name
    :type indice_name: str
    
    :rtype: dict (keys: datetime object, values: numpy.ndarray)
    
    '''
  
    mydict_indice={}
    
    for key in dict_timeStep_sub3Darr1.keys():
        tab2D = eval('calc_indice.' + indice_name + '_calculation(dict_timeStep_sub3Darr1[key], dict_timeStep_sub3Darr2[key], fill_val1, fill_val2)')
        mydict_indice[key]=tab2D
    
    return mydict_indice


# GLOBAL FUNCTION       
def indice_multivar(in_files1, var1,
                    in_files2, var2,
                    out_file,
                    indice_name,
                    time_range,
                    slice_mode,
                    project,
                    N_lev=None,
                    callback=None):
    
    '''
    This function returns result NetCDF file containing a climate indice based on two variable (ETR, DTR, vDTR).
    
    
    :param in_files1: input NetCDF files corresponding to the first variable
    :type in_files1: list of str
    :param var1: first variable to process (e.g. "tasmax")
    :type var1: str
    
    :param in_files2: input NetCDF files corresponding to the second variable
    :type in_files2: list of str
    :param var2: second variable to process (e.g. "tasmin")
    :type var2: str
    
    :param out_file: output file name
    :type out_file: str
    :param indice_name: climate indice name
    :type indice_name: str
    :param time_range: time range (dt1 should be the first day of year/month, dt2 - the last day of year/month). Note: to include dt2 -> add in datetime hour/minute (HH=23, mm=59).
    :type time_range: list of 2 datetime objects [dt1, dt2]  
    :param slice_mode: "year" or "month" 
    :type slice_mode: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type slice_mode: str
    
    :rtype: output NetCDF file name (str)
    
    .. note:: Both file lists must contain the same number steps.
    .. note:: First variable is always bigger that the second variable (par ex. var1="tasmax" and var2="tasmin")
    '''

    inc1 = Dataset(in_files1[0], 'r')
    inc2 = Dataset(in_files2[0], 'r')
    
    onc = Dataset(out_file, 'w' ,format="NETCDF3_CLASSIC")
    
    fill_val1 = get_att_value(inc1, var1, '_FillValue')
    fill_val2 = get_att_value(inc2, var2, '_FillValue')
    
    indice_dim = copy_var_dim(inc1, onc, var1, project) # tuple ('time', 'lat', 'lon')
    
    nb_rows = inc1.variables[indice_dim[1]].shape[0]
    nb_columns = inc1.variables[indice_dim[2]].shape[0]
    
    calend = get_att_value(inc1, indice_dim[0], 'calendar')
    units = get_att_value(inc1, indice_dim[0], 'units')
    
    inc1.close()
    inc2.close()

    ind_type = 'f'    
    ind = onc.createVariable(indice_name, ind_type, (indice_dim[0], indice_dim[1], indice_dim[2]), fill_value = fill_val1)
       
    
    dt_begin = time_range[0] # datetime object
    dt_end = time_range[1] # datetime object
    
    ############################
    glob_dict_timeStep_indice = {}
    ############################

    
    for in_file1, in_file2  in zip(in_files1, in_files2):

        nc1 = Dataset(in_file1, 'r')
        nc2 = Dataset(in_file2, 'r')
        
        time_steps_vect1 = get_list_dates_from_nc(nc1, 'dt')
        time_steps_vect2 = get_list_dates_from_nc(nc2, 'dt') 

        if time_steps_vect1 != time_steps_vect2:
            print 'Error: ...........'
        else:     
        
            dict_year_chunk1 = get_dict_year_chunk(time_steps_vect1)   
            
            if N_lev==None:
                values1 = nc1.variables[var1]
                values2 = nc2.variables[var2]
            else:
                values1 = nc1.variables[var1][:,N_lev,:,:]
                values2 = nc2.variables[var2][:,N_lev,:,:]
            
    
            for year in sorted(dict_year_chunk1.keys()):
    
                if year>=dt_begin.year and year<=dt_end.year:
                    
                    i1 = dict_year_chunk1[year][0]
                    i2 = dict_year_chunk1[year][1]
    
                    values_current_chunk1 = values1[i1:i2+1,:,:] # on charge les donnees (pour 1 annee) pour faire le traitement
                    values_current_chunk2 = values2[i1:i2+1,:,:]
                    
                    time_steps_current_chunk1 = numpy.array(time_steps_vect1[i1:i2+1])
                       
                    
                    if (slice_mode=='year'):
                        mydict_TimeStep_3DArray1=get_dict_year_3Darr(values_current_chunk1, time_steps_current_chunk1)
                        mydict_TimeStep_3DArray2=get_dict_year_3Darr(values_current_chunk2, time_steps_current_chunk1)
                    elif (slice_mode=='month'):
                        mydict_TimeStep_3DArray1=get_dict_month_3Darr(values_current_chunk1, time_steps_current_chunk1)
                        mydict_TimeStep_3DArray2=get_dict_month_3Darr(values_current_chunk2, time_steps_current_chunk1)
                    
                    mydict_indice=get_dict_timeStep_indice_multivar(mydict_TimeStep_3DArray1, mydict_TimeStep_3DArray2, indice_name, fill_val1, fill_val2, ind, onc)
                    
                    glob_dict_timeStep_indice.update(mydict_indice)
      
                    del values_current_chunk1, values_current_chunk2, time_steps_current_chunk1
      
                    print "Processed: ", year
                    
                    #counter_year = counter_year + 1
                    #print counter_year, total_nb_years_to_process
    
                    #status = "Year processed {0}/{1} ({3})".format(counter_year, total_nb_years_to_process, year)
                    #print status
                    
                #else:
                    #print "data not processed ", year
                    #callback("Skipping year %d" % year,percentageComplete)
    
                #time.sleep(0.01)
            #    #time.sleep(1.01)
            #    pbar.update(i+1)
            #    i+=1
            #
            #pbar.finish()
            

            nc1.close()
            nc2.close()
    
        #pbar_files.finish()
            
        #print '---'    
        #print sorted(glob_dict_timeStep_indice.keys())
        #print '---'     
        
    glob_indice = get_globindice(glob_dict_timeStep_indice, nb_rows, nb_columns) # tuple (time_step_vect, indice_2D_arr)
    
    ind[:,:,:] = glob_indice[0][:,:,:]
    
    # set global attributs
    #eval(indice_name + '_setglobattr(onc)')
    ## for all:
    #setglobattr_history(onc, indice_name, slice_mode, dt_begin, dt_end)
    #onc.setncattr('institution', '')
    onc.setncattr('source', '') # Here soon will be source meta data
    #onc.setncattr('comment', '')   
    #onc.setncattr('reference', '')
    
    # set global attributs
    set_globattr.title(onc, indice_name)
    set_globattr.references(onc)
    set_globattr.comment(onc, indice_name)
    set_globattr.institution(onc, institution_str='Climate impact portal (http://climate4impact.eu)')
    set_globattr.history2(onc, slice_mode, indice_name, time_range)

    # set variable attributs
    eval('set_longname_units.' + indice_name + '_setvarattr(ind)')
    # for all:
    ind.missing_value = fill_val1
    

    #print indice[1][:] # must be float or str!    
    #time_steps = [str(i) for i in indice[1][:]]
    
    time_steps_indice_dt = glob_indice[1][:]
    time_bnds_dt = get_glob_time_bnds(time_steps_indice_dt, slice_mode)
    
    set_time_values(onc, time_steps_indice_dt, calend, units)
    set_timebnds_values(onc, time_bnds_dt, calend, units)
    
    onc.close()
    
    return out_file

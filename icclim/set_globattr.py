
def set_title_globattr(out_nc, indice_group, indice_name):
    '''
    Set the global attribute "title" in output meta data
    
    :param out_nc: out NetCDF dataset
    :type out: netCDF4.Dataset
    :param indice_group: group of indice (e.g.: temperature/precipitation/snow/...)
    :type indice_group: str
    :param indice_name: name of indice 
    :type indice_group: str
    
    '''
    
    # example: title: ECA heat indice SU
    out_nc.setncattr('title', 'ECA '+ indice_group + ' indice ' + indice_name)
    
def set_history_globattr(out_nc, calc_grouping, indice_name, time_range):
    '''
    Set the global attribute "title" in output meta data
    
    :param out_nc: out NetCDF dataset
    :type out: netCDF4.Dataset
    :param calc_grouping: temporal grouping to apply for calculations
    :type calc_grouping: list of str or int
    :param indice_name: name of indice 
    :type indice_group: str
    :param time_range: upper and lower bounds for time dimension subsetting
    :type time_range:[datetime.datetime, datetime.datetime]
    
    
    '''
    
    ## example: title: ECA heat indice SU
    #out_nc.setncattr('title', 'ECA '+ indice_group + ' indice ' + indice_name)
    #
    #
    #def setglobattr_history(onc, indice_name, slice_mode, dt1, dt2):
    #
    #current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #
    #if slice_mode == 'year':
    #    mode = 'annual'
    #if slice_mode == 'month':
    #    mode = 'monthly'
    #
    ## example of history_str_value: 2012-10-02 15:30:20 Calculation of SU indice (annual) from 1960-01-01 to 1990-12-31.
    #history_str_value = current_time + ' Calculation of ' + indice_name + ' indice (' + mode + ') from ' + dt1.strftime('%Y-%m-%d') + ' to ' + dt2.strftime('%Y-%m-%d') + '.'
    #
    #onc.setncattr('history', history_str_value) 
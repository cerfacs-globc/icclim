# set the global attributs "title" and "history" in output meta data


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
    
    # example:      title: ECA heat indice SU
    title_str = 'ECA {0} indice {1}'.format(indice_group, indice_name)
    out_nc.setncattr('title', title_str)
    
def set_history_globattr(out_nc, calc_grouping, indice_name, time_range):
    '''
    Set the global attribute "title" in output meta data
    
    :param out_nc: out NetCDF dataset
    :type out_nc: netCDF4.Dataset
    :param calc_grouping: temporal grouping to apply for calculations
    :type calc_grouping: list of str or int
    :param indice_name: name of indice 
    :type indice_group: str
    :param time_range: upper and lower bounds for time dimension subsetting
    :type time_range:[datetime.datetime, datetime.datetime]
    
    
    '''
    
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dt1 = time_range[0]
    dt2 = time_range[1]
    
    dt1_str = '{0}-{1}-{2}'.format(dt1.year, dt1.month, dt1.day)
    dt2_str = '{0}-{1}-{2}'.format(dt2.year, dt2.month, dt2.day)
    
    if calc_grouping == ['year','month']:
        mode = 'monthly'
    elif calc_grouping == ['year']:
        mode = 'annual'  
    # etc ...
    
    # example of history_str:     2012-10-02 15:30:20 Calculation of SU indice (monthly) from 1960-01-01 to 1990-12-31.
    history_str = '{0} Calculation of {1} indice ({2}) from {3} to {4}.'.format(current_time, indice_name, mode, dt1_str, dt2_str)
        
    out_nc.setncattr('history', history_str + '\n' + out_nc.__getattribute__('history')) # Problem: it displays the new-line caracter "\n" in the end of history_str !!!!!... 
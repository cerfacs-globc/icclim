#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

import calc

# map with required parameters (for user defined indices)  
map_calc_params_required = {
                              'max': [],
                              'min': [],
                              'sum': [],
                              'mean': [],
                              'nb_events': ['logical_operation', 'thresh'], # 'link_logical_operations' ('and' or 'or' ) is required if multivariable indice
                              'max_nb_consecutive_events': ['logical_operation', 'thresh'], # 'link_logical_operations' ('and' or 'or' ) is required if multivariable indice
                              'run_mean': ['extreme_mode', 'window_width'],
                              'run_sum': ['extreme_mode', 'window_width'],
                              'anomaly': ['ref_time_range'] # past period
                              }   

# map with optional parameters (for user defined indices)  
map_calc_params_optional = {
                              'max': ['coef', 'logical_operation', 'thresh', 'date_event'], 
                              'min': ['coef', 'logical_operation', 'thresh', 'date_event'],
                              'sum': ['coef', 'logical_operation', 'thresh'], 
                              'mean': ['coef', 'logical_operation', 'thresh'], 
                              'nb_events': ['coef', 'date_event'],
                              'max_nb_consecutive_events': ['coef', 'date_event'],
                              'run_mean': ['coef', 'date_event'],
                              'run_sum': ['coef', 'date_event'],
                              'anomaly': []
                              }   

def check_params(user_indice, time_range=None, vars=None):
    '''
    Checks if a set of user parameters is correct for selected calc_operation
    '''
    
    if 'indice_name' not in user_indice.keys():
        raise IOError(" 'indice_name' is required for a user defines indice")
    
    elif 'calc_operation' not in user_indice.keys():
        raise IOError(" 'calc_operation' is required for a user defines indice")

    given_params = get_given_params(user_indice)
    
    calc_op = user_indice['calc_operation']
    required_params = map_calc_params_required[calc_op]
    
    if (calc_op not in ['max', 'min', 'mean', 'sum']) and (set(required_params).intersection(given_params) != set(required_params)):
        raise IOError('All theses parameters are required: {0}'.format(required_params))
    
    if calc_op in ['nb_events','max_nb_consecutive_events'] and type(user_indice['thresh'])==str:
        if ('var_type') not in user_indice.keys():
            raise IOError("If threshold value is a percentile,  'var_type' is required.")
        
    if calc_op=='anomaly':
        if time_range==None:
            raise IOError(" 'time_range' is required for anomalies computing.")
        
    if type(vars) is list and len(vars)>1:
        if calc_op in ['nb_events','max_nb_consecutive_events']:
            if type(user_indice['logical_operation']) is not list    or    type(user_indice['thresh']) is not list:
                raise IOError("If indice is based on {0} variables, then {0} 'logical_operations' and {0} 'thresh' " 
                              "are required (each one must be a list with {0} elements).".format(len(vars)) )
            if type(user_indice['logical_operation']) is list and 'link_logical_operations' not in user_indice.keys():
                raise IOError("If indice is based on {0} variables, then 'link_logical_operations' ('or' or 'and') is required.".format(len(vars)))
            
        for i in range(len(vars)):
            if type(user_indice['thresh'][i]) is str:
                if ('var_type') not in user_indice.keys():
                    raise IOError("If at least one of thresholds is a percentile,  'var_type' "
                                    "is required ('var_type' could be a list).")


def get_given_params(user_indice):
    given_params_list = user_indice.keys()
    
    given_params_list.remove('indice_name')
    #given_params_list.remove('calc_operation') 

    return given_params_list


def set_params(user_indice):

    given_params = get_given_params(user_indice)
    
    class F:
        pass
    global obj
    obj = F()
    
    # we set all default parameters 
    setattr(obj, 'logical_operation', None)
    setattr(obj, 'thresh', None)
    setattr(obj, 'coef', 1.0)
    setattr(obj, 'date_event', False)
    setattr(obj, 'var_type', None)
    setattr(obj, 'ref_time_range', None)
    setattr(obj, 'link_logical_operation', 'and')
    
    
    for p in given_params:
        setattr(obj, p, user_indice[p])
        
    setattr(obj, p, user_indice[p])
    


def get_user_indice_params(user_indice, var_name, out_unit):
    
    if (('date_event' in user_indice) and user_indice['calc_operation'] in ['mean', 'sum']) or ('date_event' not in user_indice):
        user_indice['date_event']=False    
        
    ui = {}        
    
    if type(var_name) != list:
        var_name = [var_name]
    
    i=0    
    for v in var_name:
        
        user_indice_var = {}
        
        for param in user_indice.keys():
            if (type(user_indice[param]) is list) and param != 'ref_time_range':
                
                param_value = user_indice[param][i]
            else:
                param_value = user_indice[param]
            
            user_indice_var[param] = param_value

        
        ui[v] = user_indice_var
        i+=1
    

    if len(ui)>1:
        ui['type']='user_indice_multivariable' 
        
        for v in var_name:
            if type(ui[v]['thresh'])== str:
                ui['type']='user_indice_percentile_based_multivariable' 

           
    else:
        if 'thresh' in ui[ui.keys()[0]].keys():
            if type(ui[ui.keys()[0]]['thresh']) == str:
                ui['type']='user_indice_percentile_based'
            else:
                ui['type']='user_indice_simple'
        else:
            ui['type']='user_indice_simple'
    
    ####
    ui['indice_name']=ui[var_name[0]]['indice_name'] 
    ui['date_event']=ui[var_name[0]]['date_event']
    ui['calc_operation']=ui[var_name[0]]['calc_operation']
    
    if ui['calc_operation']=='anomaly':
        ui['ref_time_range']=ui[var_name[0]]['ref_time_range'] 
    
    
    
    
    return ui # If ui[var]['thresh'] is not string (i.e. not percentile threshold), then ui[var]['var_type'] is ignored




def get_user_indice(user_indice, arr, fill_val, vars, out_unit='days', dt_arr=None, pctl_thresh=None):
    ### 'dt_arr' and 'pctl_thresh' are required for percentile-based indices, i.e. when a threshold is a percentile
    ### 'pctl_thresh' could be a dictionary with daily percentiles (for temperature variables) 
    ### or an 2D array with percentiles (for precipitation variables)
    ### vars: list of target variable(s)
    
    
    ### for multivariable indices (e.g. TX > 25 and TN > 10; TX > 90p and TN > 20p; TG > 90p and RR > 75p; etc):
    ### user_indice, arr, fill_val et pctl_thresh are dictionaries
    
    
    ### for anomaly: arr is list with two arrays
    
    indice_type = user_indice['type']
    
    if indice_type not in ['user_indice_multivariable', 'user_indice_percentile_based_multivariable']:
    
        for v in vars:
    
            set_params(user_indice[v])  
       
            
            if obj.calc_operation in ['min', 'max', 'mean', 'sum']:
                # simple_stat(arr, stat_operation, logical_operation=None, thresh=None, coef=1.0, fill_val=None, index_event=False)
                res = calc.simple_stat(arr, 
                                stat_operation=obj.calc_operation,
                                logical_operation=obj.logical_operation,
                                thresh=obj.thresh,
                                coef=obj.coef,
                                fill_val=fill_val,
                                index_event=obj.date_event)
        
            elif obj.calc_operation in ['nb_events', 'max_nb_consecutive_events']:
                
                # WARNING: if precipitation var ===>  values < 1.0 mm must be filtered

                if type(obj.thresh) != str:
                    thresh_=obj.thresh # threshold is int or float
                else:          
                    thresh_=pctl_thresh
                
                if obj.calc_operation == 'nb_events':
                    # get_nb_events(arr, logical_operation, thresh, fill_val=None, index_event=False, out_unit="days", dt_arr=None, coef=1.0)
                    res = calc.get_nb_events(arr=arr, 
                                        logical_operation=obj.logical_operation, 
                                        thresh=thresh_, 
                                        fill_val=fill_val, 
                                        index_event=obj.date_event, 
                                        out_unit=out_unit, 
                                        dt_arr=dt_arr, 
                                        coef=obj.coef)
    
                                
                elif obj.calc_operation == 'max_nb_consecutive_events':
                    # get_max_nb_consecutive_days(arr, logical_operation, thresh, coef=1.0, fill_val=None, index_event=False)
                    
                    ### we create a binary array
                    bin_arr = calc.get_binary_arr(arr=arr, 
                                                 logical_operation=obj.logical_operation, 
                                                 thresh=thresh_, 
                                                 dt_arr=dt_arr,
                                                 fill_val = fill_val)
                   
                    
                    ### we pass it to C function with logical_operation='e' (==) and thresh=1 
                    ### to compute max sequence of 1
                    res = calc.get_max_nb_consecutive_days(bin_arr, 
                                                      logical_operation='e', 
                                                      thresh=1, 
                                                      coef=obj.coef, 
                                                      fill_val=fill_val, 
                                                      index_event=obj.date_event,
                                                      out_unit=out_unit)       
                
                
            elif obj.calc_operation in ['run_mean', 'run_sum']:
                if obj.calc_operation == 'run_mean':
                    stat_m = 'mean'
                elif obj.calc_operation == 'run_sum':
                    stat_m = 'sum'
                
                # get_run_stat(arr, window_width, stat_mode, extreme_mode, coef=1.0, fill_val=None, index_event=False)
                res = calc.get_run_stat(arr, 
                                   window_width=obj.window_width, 
                                   stat_mode=stat_m, 
                                   extreme_mode=obj.extreme_mode, 
                                   coef=obj.coef, 
                                   fill_val=fill_val, 
                                   index_event=obj.date_event)
                
            elif obj.calc_operation == 'anomaly':
                res = calc.get_anomaly(arr[0], # future
                                       arr[1], # past (ref)
                                       fill_val=fill_val,
                                       out_unit=out_unit)
    
    
    else: # if indice_type in ['user_indice_multivariable', 'user_indice_multivariable_percentile_based']:
        
        binary_arrs = []

        for v in vars:
            
            #check_params(user_indice) 
            set_params(user_indice[v])
            
            if type(obj.thresh) != str:
                thresh_=obj.thresh # threshold is int or float
            else:          
                thresh_=pctl_thresh[v]

                
            # get_binary_arr(arr, logical_operation, thresh, dt_arr=None)
            bin_arr = calc.get_binary_arr(arr=arr[v], 
                                     logical_operation=obj.logical_operation, 
                                     thresh=thresh_, 
                                     dt_arr=dt_arr,
                                     fill_val = fill_val[v])
            
            
            
            binary_arrs.append(bin_arr)


        # get_nb_events_multivar(bin_arrs, link_logical_operation, fill_val, index_event=False, out_unit="days", max_consecutive=False):
        if obj.calc_operation == 'nb_events':            
            mc = False
        
        elif  obj.calc_operation == 'max_nb_consecutive_events':
            mc = True
        
        res = calc.get_nb_events_multivar(bin_arrs=binary_arrs, 
                                  link_logical_operation=obj.link_logical_operation,
                                  fill_val = fill_val[vars[0]], ### fill_val is only to pass it to C function (for 'max_nb_consecutive_events')
                                  index_event=obj.date_event,
                                  out_unit=out_unit,
                                  max_consecutive=mc)      
    
    
    return res



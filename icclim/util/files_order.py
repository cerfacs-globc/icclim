#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

from collections import OrderedDict
import sys
import pdb

from . import util_dt

def get_dict_file_years_glob(files_list):
    dict_file_years = OrderedDict()
    
    for filename in files_list:
        dates_list_current_file = util_dt.get_list_dates(filename, 'dt')
        years_current_file = util_dt.get_year_list(dates_list_current_file)
        dict_file_years[filename] = years_current_file
        del dates_list_current_file, years_current_file

    return dict_file_years


def get_files_correct_order(files_list, time_range, slice_mode=None):
    '''
    Select only files to process (depending on the time_range) and put them in correct (chronological) order.    
    '''

    dict_file_years = get_dict_file_years_glob(files_list)
    
    #if slice_mode in ['DJF','ONDJFM']:
    #    years_to_process = range(time_range[0].year, time_range[1].year+2) #if time_range is [2000,2009] and season is 'DJF', then we need 2010 to take J and F of 2010
    #else:
    #    years_to_process = range(time_range[0].year, time_range[1].year+1)
    
    years_to_process = range(time_range[0].year, time_range[1].year+1)
    
    files_correct_ordre = []
    for y in years_to_process:
        for f in dict_file_years.keys():
            if y in dict_file_years[f]:
                if f not in files_correct_ordre:
                    files_correct_ordre.append(f)
        
    return files_correct_ordre


def get_dict_files_years_to_process_in_correct_order(files_list, time_range, slice_mode=None):
    

    #if slice_mode in ['DJF','ONDJFM']:
    #    years_to_process = range(time_range[0].year, time_range[1].year+2) #if time_range is [2000,2009] and season is 'DJF', then we need 2010 to take J and F of 2010
    #else:
    #    years_to_process = range(time_range[0].year, time_range[1].year+1)
    
    years_to_process = range(time_range[0].year, time_range[1].year+1)
    list_files_correct_order = get_files_correct_order(files_list, time_range)
    
    dict_glob_all_files_years = get_dict_file_years_glob(files_list)
    
    new_dic = OrderedDict()
    for f in list_files_correct_order:
        list_years_to_process_correct_order = []
        for y in dict_glob_all_files_years[f]:
            if y in years_to_process:
                list_years_to_process_correct_order.append(y)
        
        list_years_to_process_correct_order = sorted(list_years_to_process_correct_order)
        new_dic[f] = list_years_to_process_correct_order
    
    return new_dic



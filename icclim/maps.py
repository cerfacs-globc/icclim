

map_indice_type =   {
                        'simple': ['TG', 'TX', 'TN', 'TXx', 'TXn', 'TNx', 'TNn', 'SU', 'TR', 'CSU', 'GD4', 'FD', 'CFD',
                                   'ID', 'HD17', 'CDD', 'CWD', 'PRCPTOT', 'RR1', 'SDII', 'R10mm', 'R20mm', 'RX1day', 'RX5day',
                                   'SD', 'SD1', 'SD5cm', 'SD50cm'],
                            
                        'multivariable': ['DTR', 'ETR', 'vDTR'],

                        'multiperiod': ['SUB'],
                 
                        'simple_time_aggregation': ['TIMEAVG'],
                            
                        'percentile_based': ['TG10p', 'TX10p', 'TN10p', 'TG90p', 'TX90p', 'TN90p', 'WSDI', 'CSDI',
                                             'R75p', 'R75pTOT', 'R95p', 'R95pTOT', 'R99p', 'R99pTOT']


                    }

map_indice_percentile_value =   {
                                    'TG10p': [10],
                                    'TX10p': [10], 
                                    'TN10p': [10],
                                    'TG90p': [90],
                                    'TX90p': [90],
                                    'TN90p': [90],
                                    'WSDI': [90],
                                    'CSDI': [10],
                                    'R75p': [75],
                                    'R75pTOT': [75],
                                    'R95p': [95],
                                    'R95pTOT': [95],
                                    'R99p': [99],
                                    'R99pTOT': [99]
                   
                                }



### to know which method for computing pctl thresholds to use:
### if 't': calc_percentiles.get_percentile_dict(...) + bootstrapping
### if 'p': calc_percentiles.get_percentile_arr(...)
map_var_type =   {
                    'TG10p': 't',
                    'TX10p': 't', 
                    'TN10p': 't',
                    'TG90p': 't',
                    'TX90p': 't',
                    'TN90p': 't',
                    'WSDI': 't',
                    'CSDI': 't',
                    'R75p': 'p',
                    'R75pTOT': 'p',
                    'R95p': 'p',
                    'R95pTOT': 'p',
                    'R99p': 'p',
                    'R99pTOT': 'p'
                  
                }


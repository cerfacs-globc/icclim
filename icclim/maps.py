

map_indice_type =   {
                        'simple': ['TG', 'TX', 'TN', 'TXx', 'TXn', 'TNx', 'TNn', 'SU', 'TR', 'CSU', 'GD4', 'FD', 'CFD',
                                   'ID', 'HD17', 'CDD', 'CWD', 'PRCPTOT', 'RR1', 'SDII', 'R10mm', 'R20mm', 'RX1day', 'RX5day',
                                   'SD', 'SD1', 'SD5cm', 'SD50cm'],
                            
                        'multivariable': ['DTR', 'ETR', 'vDTR'],

                        'multiperiod': ['SUB'],
                 
                        'simple_time_aggregation': ['TIMEAVG'],
                            
                        'percentile_based': ['TG10p', 'TX10p', 'TN10p', 'TG90p', 'TX90p', 'TN90p', 'WSDI', 'CSDI',
                                             'R75p', 'R75pTOT', 'R95p', 'R95pTOT', 'R99p', 'R99pTOT'],
                            
                        'percentile_based_multivariable': ['CD', 'CW', 'WD', 'WW']
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
                                    'R99pTOT': [99],
                                    
                                    'CD': [25, 25],
                                    'CW': [25, 75],
                                    'WD': [75, 25],
                                    'WW': [75, 75],                    
                                }


map_variable_precipitation =    {
                                    'tas': False,
                                    'tasmin': False,
                                    'tasmax': False,
#                                     'pr': False                   
                                    'pr': True
                                }

# ETCCDI Climate Change Indices
# http://etccdi.pacificclimate.org/list_27_indices.shtml
map_indices_ETCCDI = {  'FD':  {'threshold': 0},       
                        'SU':  {'threshold': 25},       
                        'ID':  {'threshold': 0},       
                        'TR':  {'threshold': 20},  

                      }
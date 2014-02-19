
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
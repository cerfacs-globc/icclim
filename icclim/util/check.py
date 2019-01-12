import numpy as np

def icclim_output_file_defaults(arg):
    # first embryo towards collecting certain stuff at a central place

    defaults = {'file_name'          : './icclim_out.nc',
                'netcdf_version'     : 'NETCDF3_CLASSIC',
                'variable_type_str'  : 'f4',
                'variable_calender'  : 'gregorian'}

    if defaults['variable_type_str'] in ['f', 'f4']:
        # 1.e20 is used by CMIP, otherwise the netCDF4 library default is preferrable 
        # as it can be recasted back and forth between float32 and float64
        # defaults['_FillValue'] = netCDF4.default_fillvals['f4']
        defaults['_FillValue'] = np.float32(1.e20)  
        defaults['missing_value'] = defaults['_FillValue']
        defaults['variable_type_name'] = 'float32' 
    else:
        # what goes here should be patterned from above, e.g.:
        # if defaults['variable_type'] in ['d', 'f8']:
        #     # defaults['_FillValue'] = netCDF4.default_fillvals['f8']
        #     defaults['_FillValue'] = numpy.float64(1.e20)  
        #     defaults['missing_value'] = defaults['_FillValue']
        #     defaults['variable_type_name'] = 'float64' 
        # else

        raise NotImplementedError('Coding error in function icclim_output_file_defaults: '
                                  + 'only "f" / "f4" / "float32" output is implemented')

    return defaults[arg]

def check_ncVar(ncVar):
    try: 
        tmp = ncVar.valid_min
        in_valid = True
    except AttributeError:
        try:
            tmp = ncVar.valid_max
            in_valid = True
        except AttributeError:
            try:
                tmp = ncVar.valid_range
                in_valid = True
            except AttributeError:
                in_valid = False
    
    return in_valid

def check_fill_value(ncVar):
    #   1) Check if _FillValue and/or missing_value exist in the input file
    try:
        in_fillval = ncVar._FillValue
    except AttributeError:
        in_fillval = None
    try:
        in_missval = ncVar.missing_value
    except AttributeError: 
        in_missval = None

    if in_fillval is None and in_missval is None:
        #   2) If neither exist then assume that the default value is not used as a valid number in the input file(s)
        #      However, given the value this seems very (VERY!) unlikely
        fill_val = icclim_output_file_defaults('missing_value')
    else:
    #   3) _FillValue or missing_value is present in the input file ...
        if ncVar.dtype.name != icclim_output_file_defaults('missing_value').dtype.name:
            #   4) ... and input data type is not the same as the output data type
            #      This works out only if it is the netCDF4 default _FillValue, or we have a problem
            if in_fillval == netCDF4.default_fillvals[ncVar.dtype.str[1:]]:
                fill_val = in_fillval
            else:
                if in_missval == netCDF4.default_fillvals[ncVar.dtype.str[1:]]:
                    fill_val = in_missval
                else:
                    # Only error out here when really necessary...
                    # Above code is really to trying to avoid coming here
                    raise NotImplementedError('Input variable type <' 
                                            + ncVar.dtype.name 
                                            + '> not the same as output data type <' 
                                            + icclim_output_file_defaults('missing_value').dtype.name 
                                            + '>\\nThis is only possible if the input files are without missing values and _FillValue'
                                            + '\\nor the they (either one, or both) are exatly equal the netCDF4 default _FillValue')
        else:
            #   5) ... and the input data type is the same as the output data type
            #      so use the value fro mthe input file (missing_value thakes precedence over _FillValue)
            if in_missval is None:
                fill_val = in_fillval
            else:
                fill_val = in_missval

    return fill_val
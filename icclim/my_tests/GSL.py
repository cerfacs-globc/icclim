## the GSL indice calculation (very slow)
################################################################## GSL #################################

def find_first_index_consecutive(a, min_len, threshold, operation):
    '''
    find the first index of a consecutive sequence (for the given condition)
    in 1D numpy array
    
    : a                     1D numpy array
    : min_len               minimum length of the consecutive sequence
    : threshold             threshold value for a condition (units must be the same as in array)
    : operation             logical operation ('e', 'gt', 'get', 'lt', 'let')
    
    : return                first index of a consecutive sequence
    '''

    first_ind = -1    
    
    if operation == 'e': # >
        for i in range(len(a)-min_len+1):
            if (a[i:i+min_len] == threshold).all() :
                first_ind = i
                break
       
    if operation == 'gt': # >
        for i in range(len(a)-min_len+1):
            if (a[i:i+min_len] > threshold).all() :
                first_ind = i
                break
    
    elif operation == 'get': # >=
        for i in range(len(a)-min_len+1):
            if (a[i:i+min_len] >= threshold).all() :
                first_ind = i
                break

    elif operation == 'lt': # <
        for i in range(len(a)-min_len+1):
            if (a[i:i+min_len] < threshold).all() :
                first_ind = i
                break
        
    elif operation == 'let': # <
        for i in range(len(a)-min_len+1):
            if (a[i:i+min_len] <= threshold).all() :
                first_ind = i
                break    

    return first_ind

def count_nb_days(time_arr, index_from, index_to):
    '''
    count number of days between time_arr[index_from] and time_arr[index_to] 
    
    '''
    dt_from = time_arr[index_from]
    dt_to = time_arr[index_to]
    
    nb_days = (dt_to - dt_from).days
    
    return nb_days

def GSL_point(a, time_arr, fill_val, t, ndays):
    '''
    growing season length (days) for one year
    
    : a                     1D numpy array of floats (temperature in Kelvin)
    : time_arr              1D numpy array with datetime.datetime objects (must be for one year)
    : t                     temperature threshold (degree Celsius, default: t = 5 Celsius)                        
                            len(a)=len(time_arr)
    : ndays                 number of consecutif days (default: ndays = 6)
    '''
    
    time_arr.sort()
    
    # we want to find index of the first day of a consecutive sequence (>=6 days) where tempereture > 5 Celsius degrees  
    index_from = find_first_index_consecutive(a, ndays, t+273.15, 'gt') # threshold = 5C + 273.15 [Kelvin]
    #print index_from
    
    
    # we want to find index of the first day of a consecutive sequence (>=6 days) where tempereture < 5 Celsius degrees
    # after the 1st July
    
    current_year = time_arr[0].year # we get the year
    time_arr2 = time_arr[ time_arr>=datetime(current_year, 07,1) ] # time_arr2 must be from 1st July
    
    # we want to find index (where time = 1st July) for subsetting of a
    ind = len(time_arr) - len(time_arr2)
    
    # subsetting of a from ind: a = ([x x x x x ind x x x x])
    a2 = a[ind:] # a2 = ([ind x x x x]) 

    # index of the first day of a consecutive sequence (>=6 days) where tempereture < 5 Celsius degrees
    # in a2 
    index_a2 = find_first_index_consecutive(a2, ndays, t+273.15, 'lt') # if a2 == [] -> index_a2 = -1
    
    # index of the first day of a consecutive sequence (>=6 days) where tempereture < 5 Celsius degrees
    # in a
    if index_a2 == -1 or index_from == -1:
        GSL = fill_val
    
    else:    
        index_to = len(a) - len(a2) + index_a2
        #print index_to

        GSL = count_nb_days(time_arr, index_from, index_to)
    
    return GSL



def GSL_calculation(a, time_arr, fill_val, t=5, ndays=6):
    '''
    : a                 3d array (here: tas mean)
    : fill_val          fill value (usually: 1.0e+20)
    : t                 temperature threshold (degree Celsius, default: t = 5 Celsius)
    : ndays             number of consecutif days (default: ndays = 6)
    
    : return            2d array
    '''
    
    T = t + 273.15 # Celsius -> Kelvin
    
    indice = numpy.empty(shape = (a.shape[1],a.shape[2]))

    for i in range(indice.shape[0]):
        for j in range(indice.shape[1]):
            indice[i,j] = GSL_point(a[:,i,j], time_arr, fill_val, t, ndays)
    return indice

####################################################################### end GSL ##################################
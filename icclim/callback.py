# callback called from
# - icclim.indice(...)
# - icclim.indice_multivar(...)
# - icclim.indice_perc(...)
# - icclim.indice_compound(...)
# - icclim.get_percentile_dict(...)


def defaultCallback(message,percentage):
    print ("[%s] %d" % (message,percentage))
    
    
def defaultCallback2(message,percentage):
    print ("[%s] %0.2f" % (message,percentage))
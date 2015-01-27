# callback called from
# - icclim.indice(...)
# - icclim.get_percentile_dict(...)


#def defaultCallback(message,percentage):
#    print ("[%s] %d" % (message,percentage))
#    
#    
#def defaultCallback2(message,percentage):
#    print ("[%s] %0.2f" % (message,percentage))

def defaultCallback(percentage):
    print ("[%s] %d" % ('Processing: ', percentage))
    
    
def defaultCallback2(percentage):
    print ("[%s] %0.2f" % ('Processing: ', percentage))
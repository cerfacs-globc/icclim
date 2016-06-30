import logging
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
    logging.info("[%s] %d%s", 'Processing: ', percentage, '%')
    
    
def defaultCallback2(percentage):
    logging.info("[%s] %0.2f%s", 'Processing: ', percentage, '%')

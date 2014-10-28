# callback called from
# - icclim.indice(...)


def defaultCallback(message,percentage):
    print ("[%s] %d" % (message,percentage))
    
    
def defaultCallback2(message,percentage):
    print ("[%s] %0.2f" % (message,percentage))
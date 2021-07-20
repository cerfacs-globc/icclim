# Add the user custom indicies

# Make the Frequency work properly
Frequency aka **slice_mode** has multiple behavior :
    - When its value is "year" or "month" it is used as a resampling similar to what is done on xclim
    - When its value is anything else it resamples to month **and** it filters out some data
        In this case, the behavior is somewhat similar to what **time_range** does.
Do we simplify this ?

# See how to handle multiple thresholds
On doit calculer plusieurs fois l'indice pour chaque seuil de la liste

# See how to handle weird slice_mode, such as ['month',[4,5,11]] or ['season',[4,5,6,7]]


# Add unit tests

# Verify on climdex that they bootstrap precipitation as well as temperatures indices
--> ils ne le font pas !
A voir si ça a du sens de le garder et avertir ouranos dans tout les cas
ligne 435 de https://github.com/pacificclimate/climdex.pcic/blob/master/R/climdex.r 


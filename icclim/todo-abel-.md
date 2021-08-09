# Add the user custom indicies
    - Add integretion tests
    - use out_unit
    - tester avec dask.
        - on peut facilement tester en utilisant open_mfdataset plutot que open_dataset
        - nb_event ne marche pas

# /!\ [Fix] Let the indices construct the Dataset to have date_start, time_bounds, threshold, percentiles as variable or coords


# Add documentation

# Gérer fill_value surtout pour les user_indices

# Progress bar
A ne pas supprimer mais l'utiliser pour de faux

# Voir si on gère bien le multi fichier en entrée, notamment les URLs
# See how to go from size_limit to dask chunks

# Verify on climdex that they bootstrap precipitation as well as temperatures indices
--> ils ne le font pas !
A voir si ça a du sens de le garder et avertir ouranos dans tous les cas
ligne 435 de https://github.com/pacificclimate/climdex.pcic/blob/master/R/climdex.r

# Add dim in User_indice to do computation on another dim than time ?

# see how we can use bootstrapping for user indices with for example 90p as a threshold


# checkout IDEA IDE to see if it handles the tests better


# merge previous branch and create draft pr for user indices

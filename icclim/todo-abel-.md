# Add the user custom indices
- Add integretion tests
- tester avec dask.
    - on peut facilement tester en utilisant open_mfdataset plutot que open_dataset
    - nb_event ne marche pas

# Add documentation

# Update documentation generation to something like xarray or xclim ?

# Gérer fill_value surtout pour les user_indices

# Add dim in User_indice to do computation on another dim than time ?

# Add percentile interpolation method
    Numpy does not implement the definition 8 of Hyndman and Yanan Fan (https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf)
    like climdex and icclim v4 do.
    On numpy they choose to implement the method 7, we can see that ilstrated here:
        line 4115 of https://github.com/numpy/numpy/blob/main/numpy/lib/function_base.py
    They did this probably because methode 7 is the default of R for historical reason (see the doc here, just above "Details": https://www.rdocumentation.org/packages/stats/versions/3.5.0/topics/quantile)

    On climdex the Cpp code is on ::c_quantile here: https://github.com/pacificclimate/climdex.pcic/blob/master/src/zhang_running_quantile.cc
    On icclim v4 the code is in libC.c::get_percentile2

    Someone implemented all methods for numpy https://github.com/ricardoV94/stats/blob/master/percentile/percentile.py

# Add metadata
 - variable meta: auto generate the metadata from yml/excel from github or locally

# Add error codes

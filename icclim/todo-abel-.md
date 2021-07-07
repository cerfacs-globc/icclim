# Add the missing indicies in xclim or icclim

# Add the user custom indicies

# Make the Frequency work properly
Frequency (slice_mode) has multiple behavior :
    - When its value is "year" or "month", it is used as a resampling similar to what is done on xclim
    - When its value is anything else it resample to moth **and** it filters out some data
        In this case, this behavior is somewhat similar to what time_range do.

# See how to handle multiple thresholds

# See how to handle weird slice_mode, such as ['month',[4,5,11]] or ['season',[4,5,6,7]]


# Add unit tests

# Verify on climdex that they bootstrap precipitation as well as temperatures indices
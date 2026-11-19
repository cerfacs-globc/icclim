"""
User indices module for icclim.

User indices are a way of creating custom climate indices since icclim v4.
It allows to define a dictionary to describe the computation of a climate index.
Since icclim v6 it is reccomended to use generic indices instead, as they are more
flexible and have a better API.
See :ref:`generic_indices_recipes` for more information on generic indices.

User indices are deprecated since 7.1.8, emit a ``FutureWarning`` since 7.5.0 and
their support ends in icclim 7.6.0. They are kept only as a legacy compatibility
bridge for older code. New custom index work should use the generic API instead.
"""

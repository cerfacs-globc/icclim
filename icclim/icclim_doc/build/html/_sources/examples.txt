
Examples
===============================

First, import the ICCLIM library:

>>> from icclim import *



The following code will calculate the SU indice (annual time series):

>>> from glob import glob
>>> from datetime import datetime
>>> 
>>> input_path = '/data/tatarinova/CMIP5/tasmax_day/'
>>> files = glob(input_path + '*.nc')
>>> out_file = '/data/tatarinova/tmp/indice_SU_year_1860-1890.nc'
>>> 
>>> dt1 = datetime(1860,01,01)
>>> dt2 = datetime(1890,12,31)
>>> 
>>> indice(in_files=files, out_file=out_file, var='tasmax', indice_name='SU', time_range=[dt1, dt2], slice_mode='year', project='CMIP5')

The output dataset will contain the SU indice (3D array) of 31 time steps (31 years).


If you want to get a derived indice from SU, CSU or TR indices, set the "threshold" parameter:

>>> indice(in_files=files, out_file=out_file, var='tasmax', indice_name='SU', time_range=[dt1, dt2], slice_mode='year', project='CMIP5', threshold=30)







Check metadata of the output file with "ncdump" command:

.. code-block:: sh

    $ ncdump -h indice_SU_year_1860-1890.nc
    [...]

Check *time* and *time_bnds* variables:

.. code-block:: sh

    $ ncdump -v time indice_SU_year_1860-1890.nc -t
    [...]

.. code-block:: sh

    $ ncdump -v time_bnds indice_SU_year_1860-1890.nc -t
    [...]

See other example scripts inside "scripts_examples" folder.



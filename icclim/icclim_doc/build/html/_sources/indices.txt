.. _indices:

Indices
===============================

For the moment you can calculate only the indices in bold (the others are in development).   

- Temperature indices (based on the temperature variable, e.g. "tas"/"tasmax"/"tasmin") 
    * temperature
        - **TG**
        - **TX**
        - **TN**
        - **DTR**
        - **ETR**
        - **vDTR**        
    * heat
        - **SU**
        - **TR**
        - **CSU**
        - **TXx**
        - **TNx**
        - WSDI
        - TG90p
        - TX90p
        - TN90p        
    * cold
        - **GD4** 
        - GSL
        - **CFD**
        - **FD**
        - **HD17** 
        - **ID**
        - **TXn**
        - **TNn**
        - CSDI
        - TG10p
        - TX10p
        - TN10p
        
- Precipitation indices (based on the variable of precipitation) 
    * drought
        - **CDD**
        - SPI6
        - SPI3
        - PET        
    * rain
        - **RR**
        - **RR1**
        - **SDII**
        - **CWD**
        - **R10mm**
        - **R20mm**
        - **RX1day**
        - **RX5day**
        - R75p
        - R75pTOT
        - R95p
        - R95pTOT
        - R99p
        - R99pTOT    
    * snow
        - **SD**
        - **SD1**
        - **SD5cm** 
        - **SD50cm** 

- Compound indices (temperature + precipitation)
        - CD
        - CW
        - WD
        - WW


Each indice is calculated as annual or monthly values.



.. warning:: Needs to respect the correspondence between the variable to process and the indice to calculate. For example, the FD indice needs a '*daily minimum temperature*' variable (e.g. "tasmin"). See the correspondance table below.


+------------------------------------------------------------+---------------------------------------------+
|   Indice                                                   |   Variable                                  |
+============================================================+=============================================+
|TG, GD4, GSL, HD17                                          |  daily mean temperature                     |
+------------------------------------------------------------+---------------------------------------------+
|TN, TR, TNx, CFD, FD, TNn                                   |  daily minimum temperature                  |
+------------------------------------------------------------+---------------------------------------------+
|TX, SU, TXx, CSU, TXn                                       |  daily maximum temperature                  |
+------------------------------------------------------------+---------------------------------------------+
|DTR, ETR, vDTR                                              |  daily minimum + daily maimum temperature   |
+------------------------------------------------------------+---------------------------------------------+
|                                                            |                                             |
|RR, RR1, SDII, CWD, CDD, R10mm, R20mm, RX1day, RX5day       |  daily precipitation (liquide phase)        |
+------------------------------------------------------------+---------------------------------------------+
|SD, SD1, SD5cm, SD50cm                                      |  daily precipitation (solid phase)          |
+------------------------------------------------------------+---------------------------------------------+



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
        - **GD** (=GD4)
        - GSL
        - **CFD**
        - **FD**
        - **HD** (=HD17)
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


Each indice is calculated as annual or monthly values (soon: as seasonal values).

Indices are calculated for the
*mixed*
blended series only and over a time
span which is as long as the record allows. For an index to be ca
lculated
for a particular year, at least 350 days with valid daily data
must exist.
For an index to be calculated for a half-year period, at least
175 days with
valid daily data must exist. For an index to be calculated for
a seasonal
period, at least 85 days with valid daily data must exist. For
an index to be
calculated for a monthly period, at least 25 days with valid d
aily data must
exist. Indices results are stored in the database only if a se
ries contains at
least 10 years of valid data.
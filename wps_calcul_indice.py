# -*- coding: latin-1 -*- 
from datetime import datetime
from pywps.Process import WPSProcess 

import time

from icclim_v1 import *

#indice(ifiles_list, ofile, var, indice_name, time_range, slice_mode, project, N_lev=None)

                              
class ProcessIndice(WPSProcess):

    def __init__(self):
        WPSProcess.__init__(self,
                            identifier = 'process_indice',
                            title = 'Indice calculating',
                            version = "1.0",
                            storeSupported = True,
                            statusSupported = True,
                            grassLocation =False)
        
        # list of input files
        self.filesIn = self.addLiteralInput(identifier = 'input_files',
                                               title = 'Input netCDF files list', 
                                               type = 'StringType',
                                               default='/data/tatarinova/CMIP5/test/tas_day_EC-EARTH_rcp45_r2i1p1_20560101-21001231.nc')
        # output file name
        self.outFileIn = self.addLiteralInput(identifier = 'output_file_name',
                                               title = 'Output File Name', 
                                               type = 'StringType',
                                               default='/data/tatarinova/tmp/res/test_wps.nc')
     
        # tas/pr/psl                                       
        self.varIn = self.addLiteralInput(identifier = 'var',
                                               title = 'Variable',
                                               type = 'StringType',
                                               default='tas')        
        # indice name
        self.indiceIn = self.addLiteralInput(identifier = 'indice',
                                               title = 'Indice name',
                                               type = 'StringType',
                                               default='SU')
        # time begin
        self.timeBeginIn = self.addLiteralInput(identifier = 'time_begin',
                                               title = 'Time begin', 
                                               type = 'StringType',
                                               default='2060,01,01')
        # time end
        self.timeEndIn = self.addLiteralInput(identifier = 'time_end',
                                               title = 'Time end', 
                                               type = 'StringType',
                                               default='2090,12,31')
        
                                               
        # slice mode ('year', 'month')                                     
        self.sliceModeIn = self.addLiteralInput(identifier = 'slice_mode',
                                               title = 'Slice mode',
                                               type = 'StringType',
                                               default='year')
        
        # project name ('CMIP5', 'CORDEX')                                   
        self.projectIn = self.addLiteralInput(identifier = 'project',
                                               title = 'Project',
                                               type = 'StringType',
                                               default='CMIP5')
        
        ## level number                                   
        #self.levelIn = self.addLiteralInput(identifier = 'level',
        #                                       title = 'Level number',
        #                                       type = 'StringType',
        #                                       default='None')
        
        
        #A output netCDF file
        self.fileOut = self.addComplexOutput(identifier = 'output_file',
                                             title = 'Output netCDF file',
                                             formats = [
                                                        {"mimeType":"application/netcdf"} # application/x-netcdf
                                                      ])
 
    def execute(self):
        
        
        start = time.time()
        
        input_files_list = self.filesIn.getValue()
        output_file = self.outFileIn.getValue()
        var = self.varIn.getValue()
        indice_name = self.indiceIn.getValue()
        #time_range = self.timeRangeIn.getValue()
        
        dt1_str = self.timeBeginIn.getValue()
        dt2_str = self.timeEndIn.getValue()
        
        a = 'datetime('
        b = ')'
        
        dt1 = eval(a + dt1_str + b)
        dt2 = eval(a + dt2_str + b)
        time_range = [dt1, dt2]
        
        #print type(dt1)
        #print type(dt2)
        #
        #import sys
        #sys.exit()

        slice_mode = self.sliceModeIn.getValue()
        project = self.projectIn.getValue()
        #level = self.levelIn.getValue()


        res = self.fileOut.setValue
        res = indice(input_files_list, output_file, var, indice_name, time_range, slice_mode, project)

        stop = time.time()
        time1 = stop - start
        print 'time: ', time1
        
        #print 'Youhooo!!!'

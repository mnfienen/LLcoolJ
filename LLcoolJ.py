# LLcoolJ - a module to support 
# HYDROLOGIC BUDGET PROGRAM FOR SHELL LAKE, WISCONSIN

import numpy as np
from datetime import datetime as dt # pull the datetime module from datetime and call it dt

# initialize a class which will hold all properties and methods
class hydrologic_budget:
    def __init__(self,namfile,DA,LL_init):
        # start out with just the property of the name file
        self.namfile = namfile
        self.DA = DA
        self.DRYPPT = 0.0
        self.SUM = 0.0 # sum of snowmelt
        self.LL_init = LL_init
        self.I = 0
        self.NMA = 3
        
    def calc_next_lake_level(self):
        
        I = self.I
        # Calculate lake area in square feet
        self.AREA = -1890921920.41 + (1643379.95*self.LL[I])
        
        # Calculate precipitation in feet        
        self.DRYPPT = self.DRYPPT + self.PI[I] * self.DA

        # Sum precipitation for snowmelt
        # fortran: SUM=SUM+PI(I)        
        self.SUM = self.SUM + self.PI[I]
        
        # Calculate effective precipitation rate for runoff calculation
        # assuming 3-day moving average including current day        
        start_index = max(0,I - self.NMA + 1)
        end_index = I + 1
        self.EFFPPT = np.mean(self.PI[start_index:end_index])

        # Runoff for December, January, February, and mid-March
        if ( (self.DATES[I].month in (12,1,2) ) or (self.DATES[I] == 3 and self.DATES[I] < 16) ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[7]
            self.SUM = self.SUM - self.EFFPPT * self.ROCOEF[7]
            
#        elif (self.DATES[I] == 3 & self.DATES[I] < 16):
        
        
        # advance to the next day
        I = I + 1
        
    # method to read in the namefile information
    def read_namefile(self):
        try:
            indat = open(self.namfile,'r').readlines()
            self.outfilename = indat.pop(0).strip()
            self.datfilename = indat.pop(0).strip()
            self.calfilename = indat.pop(0).strip()
        except:
            raise(FileFail(self.namfile,'NameFile'))
    
    # method to read in Cal data
    def read_calfile(self):
        try:
            indat = open(self.calfilename,'r').readlines()
        except:
            raise(FileFail(self.calfilename,'CalFile'))
        # make a list of just the numbers from the file
        lines = []
        for cl in indat:
            lines.append(cl.strip().split()[0]) # strip gets rid of newline, etc. 
                                                # split breaks on whitespace
        if len(lines) != 13:
            raise(CalFail(len(lines),self.calfilename))
        # now pull out the ROcoeffs
        self.ROCOEF = np.array(lines[0:7]).astype(float)
        self.GWCOND = float(lines[7])
        self.GRAD = float(lines[8])
        self.EVCOEF = float(lines[9])
        self.NMA = float(lines[10])
        self.ADCT = float(lines[11])
        self.ADCF = float(lines[12])
        # now Calculate lake area at the Area-Dependent Conductance Trigger
        self.AAA=-1890921920.41+(1643379.95*self.ADCT)
        
    # method to read in time series data
    def read_datfile(self):
        try:
            indat = np.genfromtxt(self.datfilename,names=True,dtype=None)
            self.PRECIP = indat['Precip']
            self.PI = self.PRECIP/12.0 # converted to feet 
            self.EVAP = indat['Evap']
            self.EVAP[self.EVAP < 0.0 ] = 0.0
            self.E0 = self.EVAP / 12.0 * self.EVCOEF # calculate evaporation in feet
            self.DATES = []
            DATES = indat['Date']
            datefmt = '%m/%d/%Y' # format to read the dates as
            for cd in DATES:
                self.DATES.append(dt.strptime(cd,datefmt))
            self.LL = np.zeros_like(self.EVAP)
            self.RO = np.zeros_like(self.EVAP)            
            self.LL[0] = self.LL_init
            
        except:
            raise(FileFail(self.datfilename,'DatFile'))

        
# ####################### #
# Error Exception Classes #        
# ####################### #
# -- cannot read file
class FileFail(Exception):
    def __init__(self,filename,filetype):
        self.filename=filename
        self.ft = filetype
    def __str__(self):
        return('\n\nCould not read ' + self.ft +': ' + self.filename + ' \n' +
            "You looking at me?!? It's your problem fool!\n" + 
            "Either it can't be opened, can't be read, or doesn't exist") 
    
# -- wrong number of lines in cal file
class CalFail(Exception):
    def __init__(self,nlines,fn):
        self.nlines=nlines
        self.fn = fn
    def __str__(self):
        return('\n\nCal File: ' + self.fn + ' has wrong number of lines. \n' +
               'Read ' + str(self.nlines) + ' lines in the file')

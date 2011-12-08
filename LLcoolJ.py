# LLcoolJ - a module to support 
# HYDROLOGIC BUDGET PROGRAM FOR SHELL LAKE, WISCONSIN

import numpy as np
import copy
from datetime import datetime as dt # pull the datetime module from datetime and call it dt

def idx(fortran_index):
    return fortran_index - 1

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
        self.dateout_fmt = "%m/%d/%Y" # see http://docs.python.org/library/datetime.html

    # method to read in the namefile information
    def read_namefile(self):
        try:
            indat = open(self.namfile,'r').readlines()
            self.outfilename = indat.pop(0).strip()
            self.datfilename = indat.pop(0).strip()
            self.calfilename = indat.pop(0).strip()
        except:
            raise(FileFail(self.namfile,'name (*.NAM) file'))

    # method to open the output file
    def open_outputfile(self):
        try:
            self.output_file = open(self.outfilename,'w')
        except:
            raise(FileFail(self.outfilename,'output file'))

    # method to close the output file
    def close_outputfile(self):
        try:
            self.output_file.close()
        except:
            raise(FileFail(self.outfilename,'output file'))
        
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
            self.EO = self.EVAP / 12.0 * self.EVCOEF # calculate evaporation in feet
            self.DATES = []
            DATES = indat['Date']
            datefmt = '%m/%d/%Y' # format to read the dates as
            for cd in DATES:
                self.DATES.append(dt.strptime(cd,datefmt))
            self.LL = np.zeros(self.EVAP.size + 1)      
            self.RO = np.zeros_like(self.EVAP)
            self.GW = np.zeros_like(self.EVAP)            
            self.LL[0] = self.LL_init
            self.NumRecs = self.EVAP.size
            
        except:
            raise(FileFail(self.datfilename,'DatFile'))

    # Method to calculate the current days' lake level
    def calc_next_lake_level(self, echo=True):
        
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
        if ( (self.DATES[I].month in (12, 1, 2) ) or (self.DATES[I] == 3 and self.DATES[I] < 16) ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[idx(7)]
            self.SUM = self.SUM - self.EFFPPT * self.ROCOEF[idx(7)]
            
        # Runoff for latter half of March and April            
        elif ( (self.DATES[I].month == 4 ) or (self.DATES[I] == 3 and self.DATES[I] >= 16) ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[idx(1)]
        
        # Runoff for May
        elif (self.DATES[I].month == 5 ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[idx(2)]

        # Runoff for June, July and August
        elif (self.DATES[I].month in (6, 7, 8) ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[idx(3)]
            
        # Runoff for September and October
        elif (self.DATES[I].month in (9, 10) ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[idx(4)]
            
        # Runoff for November
        elif (self.DATES[I].month == 11 ):
            self.RO[I] = self.EFFPPT * self.DA * self.ROCOEF[idx(5)]

        # If there's still snow on the 15th of March, assume that it all melts. TODAY.
        if (self.DATES[I] == 3 and self.DATES[I] == 15):
            # It would seem that  the original code discards any precip-related runoff
            # perhaps this should read:
            # self.RO[I] = self.RO(I) + self.SUM * self.DA * self.ROCOEF[6]            
            self.RO[I] = self.SUM * self.DA * self.ROCOEF[idx(6)]
            self.SUM = 0.0
            
        # Calculate ground-water flow from lake
        self.GW[I] = self.GWCOND * self.GRAD
        COND = copy.deepcopy(self.GWCOND)
        if(self.LL[I] > self.ADCT):
            self.FACT = self.LL[I] - self.ADCT
            self.FACT = self.FACT * self.ADCF
            self.FCOND = self.GWCOND + self.GWCOND * self.FACT
            FAREA = self.AREA - self.AAA
            COND = (self.AAA / self.AREA * self.GWCOND ) + (self.FAREA / self.AREA * self.FCOND)
            self.GW[I] = COND * self.GRAD
           
        # Water balance and lake level calculations
        FLOWIN = self.RO[I] + self.PI[I] * self.AREA
        FLOWOT = self.EO[I] * self.AREA + self.GW[I] * self.AREA
        DVOL = FLOWIN - FLOWOT
        DSTAGE = DVOL / self.AREA
        self.LL[I+1] = self.LL[I] + DSTAGE            

        # format output for writing to disk and screen
        outstring = dt.strftime(self.DATES[I],self.dateout_fmt) + ': {0:.3f}'.format(self.LL[I])        
        
        if (echo):
            print outstring

        self.output_file.write(outstring)

        # advance to the next day
        self.I = self.I + 1

    def calc_lake_levels(self, echo=False):
        while(self.I < self.NumRecs):
            self.calc_next_lake_level(echo)
        self.close_outputfile()
    
# ####################### #
# Error Exception Classes #        
# ####################### #
# -- cannot read/write/open/close file
class FileFail(Exception):
    def __init__(self,filename,filetype):
        self.filename=filename
        self.ft = filetype
    def __str__(self):
        return('\n\nProblem with ' + self.ft +': ' + self.filename + ' \n' +
            "Either it can't be opened or closed, can't be read from or written to, or doesn't exist") 
    
# -- wrong number of lines in cal file
class CalFail(Exception):
    def __init__(self,nlines,fn):
        self.nlines=nlines
        self.fn = fn
    def __str__(self):
        return('\n\nCal File: ' + self.fn + ' has wrong number of lines. \n' +
               'Read ' + str(self.nlines) + ' lines in the file')

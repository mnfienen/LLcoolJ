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
        self.SUM = 0.0 # sum of snowmelt
        self.LL_init = LL_init
    # method to read in the namefile information
    def read_namefile(self):
        try:
            indat = open(self.namfile,'r').readlines()
            self.outfilename = indat.pop(0).strip()
            self.datfilename = indat.pop(0).strip()
            self.calfilename = indat.pop(0).strip()
        except:
            raise(FileFail(self.namfile),'NameFile')
    
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
        self.ROcoefs = np.array(lines[0:7]).astype(float)
        self.GWCOND = float(lines[7])
        self.GRAD = float(lines[8])
        self.EVCOEFF = float(lines[9])
        self.NMA = float(lines[10])
        self.ADCT = float(lines[11])
        self.ADCF = float(lines[12])
        # now Calculate lake area at the Area-Dependent Conductance Trigger
        self.AAA=-1890921920.41+(1643379.95*self.ADCT)

    # method to read in time series data
    def read_datfile(self):
       # try:
        indat = np.genfromtxt(self.datfilename,names=True,dtype=None)
        self.precip = indat['Precip']
        self.PI = self.precip/12.0 # converted to feet 
        self.evap = indat['Evap']
        self.evap[self.evap==-999] = 0
        self.dates = []
        dates = indat['Date']
        datefmt = '%m/%d/%Y' # format to read the dates as
        for cd in dates:
            self.dates.append(dt.strptime(cd,datefmt))
        self.LL = np.zeros_like(self.evap)
        self.LL[0] = self.LL_init
        
   #     except:
   #         raise(FileFail(self.datfilename,'DatFile'))
        
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

import numpy as np # import numpy bu call it np
import re
from datetime import datetime as dt # pull the datetime module from datetime and call it dt
import matplotlib.pyplot as plt
from LLcoolJ import * # import everything from LLcoolJ

# set the namefile
nf = 'NMOD0_new.NAM'
# set the Basin Area-Lake Area
DA = 3.7892e8
# set the initial lake level
LL_init = 1217.08

# make a hydrologic budget object
hbud = hydrologic_budget(nf,DA,LL_init)

# read in the namefile to get all the other filenames
hbud.read_namefile()

# read in and parse the Cal File
hbud.read_calfile()

# open output file
hbud.open_outputfile()

# read in and parse the Data File
hbud.read_datfile()

file = open('test.out')

fdate = []
fvalue = []
datefmt = '%m/%d/%Y' # format to read the dates as

for line in file:
    # simple regular expression: look for two numerical values
    # separated by one or more spaces
    mydate, myvalue =  re.split(r'\s\s+',line.strip())
    fdate.append(dt.strptime(mydate,datefmt))
    fvalue.append(myvalue)
    
hbud.calc_lake_levels()

plt.figure()
plt.plot(fdate, fvalue, 'g', hbud.DATES, hbud.LL[0:-1], 'r', label=['Fortran','Python'])
plt.legend( ('Fortran','Python'), loc='lower left')
plt.show()

i=-1
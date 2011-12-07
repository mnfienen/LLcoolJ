import numpy as np # import numpy bu call it np
from LLcoolJ import * # import everything from LLcoolJ

# set the namefile
nf = 'NMOD0.NAM'
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

# read in and parse the Data File
hbud.read_datfile()

hbud.calc_next_lake_level()

i=-1
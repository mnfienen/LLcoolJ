LL = 1217.08
DA = 3.7892e8
namfile = 'NMOD0.NAM'
echo = False


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

# -- Failure parsing the input data file
class ParseFail(Exception):
    def __init__(self,offending_line):
        self.offending_line = offending_line
    def __str__(self):
        return('\n\nThere was a problem parsing a line in your data file. \n' +
               'The offending line was:\n' +
               '"' + self.offending_line + '"')


try:
    lines = open(namfile,'r').readlines()
    outfilename = lines[0].strip()
    datfilename = lines[1].strip()
    calfilename = lines[2].strip()
except:
    raise(FileFail(namfile,'name (*.NAM) file'))

try:
    output_file = open(outfilename,'w')
except:
    raise(FileFail(outfilename,'output file'))

try:
    calib_file = open(calfilename,'r').readlines()
except:
    raise(FileFail(calfilename,'calibration parameter file'))

# make a list of just the numbers from the file
lines = []
for each_line in calib_file:
    line_stripped = each_line.strip()
    line_split = line_stripped.split()
    lines.append(line_split[0])

if len(lines) != 13:
    raise(CalFail(len(lines),calfilename))

# now pull out the ROcoeffs
ROCOEF_1 = float(lines[0])
ROCOEF_2 = float(lines[1])
ROCOEF_3 = float(lines[2])
ROCOEF_4 = float(lines[3])
ROCOEF_5 = float(lines[4])
ROCOEF_6 = float(lines[5])
ROCOEF_7 = float(lines[6])
GWCOND = float(lines[7])
GRAD = float(lines[8])
EVCOEF = float(lines[9])
NMA = float(lines[10])
ADCT = float(lines[11])
ADCF = float(lines[12])

# now Calculate lake area at the Area-Dependent Conductance Trigger
AAA = -1890921920.41 + (1643379.95 * ADCT)


try:
    data_file = open(datfilename,'r').readlines()
except:
    raise(FileFail(datfilename,'precipitation and evaporation data file'))

SUM = 0.0
I = 1

for each_line in data_file:

    DATA = each_line.split()
    DATE = DATA[0]
    PRECIP = float(DATA[1])
    try:
        EVAP = float(DATA[2])
    except:
        EVAP = 0.0

    try:
        MONTH, DAY, YEAR =  DATE.split("/")
    except:
        raise(ParseFail,each_line)
 

    # calculate the daily precipitation in feet
    PI = PRECIP / 12.0

    # Calculate effective precipitation rate for runoff calculation
    # assuming 3-day moving average including current day        
    if(I == 1):
        PI1 = PI
        PI2 = PI
        PI3 = PI
    else:
        PI1 = PI2
        PI2 = PI3
        PI3 = PI

    EFFPPT = (PI1 + PI2 + PI3) / 3.0
    
    # calculate the daily evaporation in feet
    EO = EVAP / 12.0 * EVCOEF

    # Calculate lake area in square feet
    AREA = -1890921920.41 + (1643379.95 * LL)
    
    # Sum precipitation for snowmelt
    # fortran: SUM=SUM+PI(I)        
    SUM = SUM + PI

    # Runoff for December, January, February, and mid-March
    if ( int(MONTH) in (12, 1, 2) ) or ( int(MONTH) == 3 and int(DAY) < 16) :
        RO = EFFPPT * DA * ROCOEF_7
        SUM = SUM - EFFPPT * ROCOEF_7
        
    # Runoff for latter half of March and April            
    elif ( (int(MONTH) == 4 ) or (int(MONTH) == 3 and int(DAY) > 15) ):
        RO = EFFPPT * DA * ROCOEF_1
    
    # Runoff for May
    elif (int(MONTH) == 5 ):
        RO = EFFPPT * DA * ROCOEF_2

    # Runoff for June, July and August
    elif (int(MONTH) in (6, 7, 8) ):
        RO = EFFPPT * DA * ROCOEF_3
        
    # Runoff for September and October
    elif (int(MONTH) in (9, 10) ):
        RO = EFFPPT * DA * ROCOEF_4
        
    # Runoff for November
    elif (int(MONTH) == 11 ):
        RO = EFFPPT * DA * ROCOEF_5

    # If there's still snow on the 15th of March, assume that it all melts. TODAY.
    if (int(MONTH) == 3 and int(DAY) == 15):
        # It would seem that  the original code discards any precip-related runoff
        # perhaps this should read:
        # RO = RO(I) + SUM * DA * ROCOEF[6]            
        RO = SUM * DA * ROCOEF_6
        RO = RO
        n = 0.

    # reset snow amount accumulator on November 30
    if (int(MONTH) == 11 and int(DAY) == 30):
        SUM = 0.0
        
    # Calculate ground-water flow from lake
    GW = GWCOND * GRAD
    COND = GWCOND
    if(LL > ADCT):
        FACT = LL - ADCT
        FACT = FACT * ADCF
        FCOND = GWCOND + GWCOND * FACT
        FAREA = AREA - AAA
        COND = ( (AAA / AREA )* GWCOND ) + ( (FAREA / AREA) * FCOND)
        GW = COND * GRAD
       
    # Water balance and lake level calculations
    FLOWIN = RO + PI * AREA
    FLOWOT = EO * AREA + GW * AREA
    DVOL = FLOWIN - FLOWOT
    DSTAGE = DVOL / AREA
    LL = LL + DSTAGE            

    # format output for writing to disk and screen
    outstring = '{0}/{1}/{2}'.format(MONTH,DAY,YEAR) + ': {0:.3f}'.format(LL) + '\n'
    
    I = I + 1
    
    if (echo):
        print outstring

    output_file.write(outstring)
    
try:
    output_file.close()
except:
    raise(FileFail(outfilename,'output file'))
        

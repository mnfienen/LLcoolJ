C     Last change:  JTK  31 Mar 99   12:32 pm
C HYDROLOGIC BUDGET PROGRAM FOR SHELL LAKE, WISCONSIN
C
C Declare and dimension varibles
C
      PARAMETER(NND=18444,NNAM=3)
      CHARACTER*12 FIL(NNAM)
      COMMON PI(NND),RO(NND),EO(NND),PRECIP(NND),
     &EVAP(NND),LL(NND),AREA(NND),
     &YEAR(NND),MONTH(NND),DAY(NND),
     &GW(NND),COND(NND),ROCOEF(7)
      REAL PI,RO,EO,PRECIP,EVAP,LL,AREA,GW,SUM,GWCOND,
     &GRAD,EVCOEF,ADCT,ADCF,DRYPPT,EFFPPT
      INTEGER YEAR,MONTH,DAY
C
C PRECIP is precipitation from Spooner or gage (inches)
C PI is direct precipitation on lake (feet)
C DRYPPT is the volume of precipitation falling on the basin
C EFFPPT is effective precipitation calculated as a moving average
C NMA is the number of days used to calculate the moving average of EFFPPT
C RO is runoff from basin area (cubic feet)
C EVAP is pan evaporation from Marshfield (inches)
C EVCOEF is the evaporation coeffcient
C EO is evaporation from lake surface (feet)
C ROCOEF is the runoff coefficient
C GWCOND is the vertical hydraulic conductivity of the lakebed (feet/day)
C GRAD is the gradient between the lake and groundwater system
C COND is the vertical hydraulic conductivy multiplied by the gradient
C GW is groundwater flow velocity based on Darcy's law (feet per day)
C SUM is the total precipitation used to calculate runoff
C from snowmelt (feet)
C AREA is lake area (square feet)
C AAA is lake area at the stage of the area-dependent conductance trigger (feet)
C ADCT is the area-dependent conductance trigger (feet)
C ADCF is the area-dependent conductance factor
C LL is daily lake stage (feet)
C FLOWIN is the total daily flow into the lake (cubic feet per day)
C FLOWOT is the total daily flow out of the lake (cubic feet per day)
C DVOL is the net daily volume (cubic feet per day)
C DSTAGE is the change in lake stage for the current day (feet)
C
C------------------------------------------------------------------
C------------------------------------------------------------------
C
C
C Open file containing file names of (1) output file,
C (2) input file, (3) parameter file,
C
      OPEN(UNIT=55,FILE='NMOD0.NAM')
      DO 550 K=1,NNAM
       READ(55,999) FIL(K)
  550 CONTINUE
  999 FORMAT(A12)
      CLOSE(55)
C
      OPEN(UNIT=13,FILE=FIL(1))
      OPEN(UNIT=11,FILE=FIL(2))
      OPEN(UNIT=10,FILE=FIL(3))
C
C Read in date and daily precipitation and evaporation in inches
C
      DO 3 I=1,NND
      READ(11,20)MONTH(I),DAY(I),YEAR(I),PRECIP(I),EVAP(I)
    3 CONTINUE
C
C
   20 FORMAT(2X,I2,1X,I2,1X,I4,2F10.2)
C
C Initialize sum of snowmelt
C
      SUM=0.0
C
C READ RUNOFF COEFFICIENTS
C
      DO 4 I=1,7
        READ(10,26)ROCOEF(I)
4     CONTINUE
   26 FORMAT(F10.5)
C
C Read vertical hydraulic conductivity
C
      READ(10,901) GWCOND
C
C Read lake/groundwater gradient
C
      READ(10,901) GRAD
C
C Read pan evaporation coefficent
C
      READ(10,901) EVCOEF
C
C Read number of days for moving average
C
      READ(10,905) NMA
C
C Read value for Area-Dependent Conductance Trigger
C
      READ(10,1906) ADCT
C
C Read value for Area-Dependent Conductance Factor
C
      READ(10,1906) ADCF
C
  901 FORMAT(F10.5)
  905 FORMAT(I10)
 1906 FORMAT(F10.2)
C
C DA is BASIN AREA-LAKE AREA
C
      DA=3.7892e8
C
C Initialize lake level
C
      LL(1)=1217.08
C
C Start loop to calculate daily lake stage
C
      DO 9 I=1,NND
C
C Calculate lake area in square feet
C
      AREA(I)=-1890921920.41+(1643379.95*LL(I))
C
C Calculate lake area at the Area-Dependent Conductance Trigger
C
      AAA=-1890921920.41+(1643379.95*ADCT)
C
C Calculate precipitation in feet
C
      PI(I)= PRECIP(I)/12
      DRYPPT=DRYPPT+PI(I)*DA
C
C Sum precipitation for snowmelt
C
      SUM=SUM+PI(I)
C
C Calculate effective precipitation rate for runoff calculation
C assuming 3-day moving average including current day
C
      SUMPPT=0.
      IF(I.LT.NMA) THEN
       EFFPPT=PI(I)
      ELSE
       DO 11 K=1,NMA    
        SUMPPT=SUMPPT + PI(I+1-K)    
   11  CONTINUE
       EFFPPT=SUMPPT/NMA
      ENDIF
C
C Calculate evaporation in feet
C
      EO(I)=(EVAP(I)/12)*EVCOEF
C
C Calculate runoff in cubic feet
C
C
C Runoff for December, January and, February
C
      IF(MONTH(I).GT.11.OR.MONTH(I).LT.3) THEN
       RO(I)=EFFPPT*DA*ROCOEF(7)
      END IF
      IF(MONTH(I).GT.11.OR.MONTH(I).LT.3) THEN
       SUM=SUM-ROCOEF(7)*EFFPPT
      ENDIF
C
C Runoff for March 1-15
C
      IF(MONTH(I).EQ.3.AND.DAY(I).LT.16) THEN
       RO(I)=EFFPPT*DA*ROCOEF(7)
      END IF
      IF(MONTH(I).EQ.3.AND.DAY(I).LT.16) THEN
         SUM=SUM-ROCOEF(7)*EFFPPT
      ENDIF
C
C Runoff for March (days greater then 15) and April
C
      IF(MONTH(I).EQ.3.AND.DAY(I).GT.15 .OR. MONTH(I).EQ.4) THEN
        RO(I)=EFFPPT*DA*ROCOEF(1)
      END IF
C
C Runoff for May
C
      IF(MONTH(I).EQ.5) THEN
        RO(I)=EFFPPT*DA*ROCOEF(2)
      END IF
C
C Runoff for June, July and August
C
      IF (MONTH(I).GT.5.AND.MONTH(I).LT.9) THEN
        RO(I)=EFFPPT*DA*ROCOEF(3)
      END IF
C
C Runoff for September and October
C
      IF(MONTH(I).GT.8.AND.MONTH(I).LT.11) THEN
        RO(I)=EFFPPT*DA*ROCOEF(4)
      END IF
C
C Runoff for November
C
      IF(MONTH(I).EQ.11) THEN
        RO(I)=EFFPPT*DA*ROCOEF(5)
      END IF

C
C Runoff from snowmelt (March 15)
C
      IF (MONTH(I).EQ.3.AND.DAY(I).EQ.15) THEN
        RO(I)=SUM*DA*ROCOEF(6)
      END IF
C
      IF (MONTH(I).EQ.11.AND.DAY(I).EQ.30) THEN
        SUM=0.0
      END IF
C
C Calculate ground-water flow from lake
C
      GW(I)=GWCOND*GRAD
      COND(I)=GWCOND
       IF(LL(I).GT.ADCT) THEN
         FACT=LL(I)-ADCT
         FACT=FACT*ADCF
         FCOND=GWCOND+GWCOND*FACT
         FAREA=AREA(I)-AAA
         COND(I)=(AAA/AREA(I))*GWCOND + (FAREA/AREA(I))*FCOND
         GW(I)=COND(I)*GRAD
      ENDIF
C
C Water balance and lake level calculations
C
      FLOWIN=RO(I)+PI(I)*AREA(I)
      FLOWOT=EO(I)*AREA(I)+GW(I)*AREA(I)
      DVOL=FLOWIN-FLOWOT
      DSTAGE=DVOL/AREA(I)
      LL(I+1)=LL(I)+DSTAGE
C
C
C
    9 CONTINUE
C
C Write date and lake level
C     
      DO 45 I=1,NND
      WRITE(13,21)MONTH(I),DAY(I),YEAR(I),LL(I)      
   21 FORMAT (I2,'/',I2,'/',I4,2X,F12.4)
   45 CONTINUE
C
C Program end
C
      STOP
      END

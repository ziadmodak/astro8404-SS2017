#This script was written by Ziad Modak for imaging the ALMA Data of NGC 1614 as part of the Master course astro8404: Radio Interferometry in SS 2017


###############################
# THE SCRIPT STARTS FROM HERE #
###############################


import os

# Convert the raw data to the CASA Measurement Set (MS) from the ALMA Science Data Model (ASDM) 

importasdm(asdm = 'uid___A002_X8a5fcf_X125f',
           asis = 'Antenna Station Receiver Source CalAtmosphere CalWVR',
           bdfflags = True)



# We have just one Execution Block (EB), we use listobs just once to get "introduced" to the data

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.listobs')                  #remove the previous listobs file, if any
listobs(vis = 'uid___A002_X8a5fcf_X125f.ms',                       
        listfile = 'uid___A002_X8a5fcf_X125f.ms.listobs')                #save the output from the listobs to this file



# We produce the antenna configuration for our data

plotants(vis = 'uid___A002_X8a5fcf_X125f.ms', figfile = 'uid___A002_X8a5fcf_X125f_plotants.png')              #generate a .png image of the plotants output


#######################################
# Beginning of "a priori" calibration #
#######################################


# A priori flagging

# The autocorrelation data
flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms',
         mode = 'manual',
         spw = '1~24',                                                  #all the Spectral Windows but the one with WVR measurements (SpW = 0)
         autocorr = T,
         flagbackup = F)

# The intents that wont be used
flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms',
         mode = 'manual',
         intent = '*POINTING*, *ATMOSPHERE*, *SIDEBAND_RATIO*',         #the scan intents that we can ignore and need to be flagged
         flagbackup = F)

# Antenna Shadowing data
flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms',
         mode = 'shadow',                                               #shadowed data, determined automatically by CASA
         flagbackup = F)




# WVR caltable generation

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.wvr')                     #remove the previously generated WVR caltable, if any
wvrgcal(vis = 'uid___A002_X8a5fcf_X125f.ms',
        caltable = 'uid___A002_X8a5fcf_X125f.ms.wvr',
        spw = [9, 11, 13, 15, 17, 19, 21, 23],                                         #the "science" SpWs to which we will apply this caltable
        smooth = '6.05s',                                               #the integration time of the science visibilities from listobs
        toffset = 0,
        segsource = True,
        tie = ['J0423-0120,ngc_1614'],                        #the sources for which the solution needs to be found
        statsource = 'ngc_1614')



# Tsys caltable generation

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.tsys')
gencal(vis = 'uid___A002_X8a5fcf_X125f.ms',
       caltable = 'uid___A002_X8a5fcf_X125f.ms.tsys',                  #name of the output caltable
       caltype = 'tsys')                                               #selecting the type of gencal to be "Tsys"


# Flagging of the edge channels of the SpWs

flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms',
         mode = 'manual',
         spw = '9:0~3;124~127,11:0~3;124~127,13:0~3;124~127,15:0~3;124~127,17:0~3;1916~1919,19:0~3;1916~1919,21:0~3;1916~1919,23:0~3;1916~1919',      #The edges of all the SpWs have been selected
         flagbackup = F)



# Inspection of the Tsys caltable

for spw in ['9','11','13','15']:
    plotbandpass(caltable = 'uid___A002_X8a5fcf_X125f.ms.tsys', xaxis = 'freq',
                 yaxis = 'amp', spw = spw,
                 overlay = 'time', plotrange = [0, 0, 10, 150],
                 figfile = 'cal_tsys_'+spw+'_uid___A002_X8a5fcf_X125f.png',
                 interactive = False)


for spw in ['9','11','13','15']:
    plotbandpass(caltable = 'uid___A002_X8a5fcf_X125f.ms.tsys', xaxis = 'freq',
                 yaxis = 'amp', spw = spw,
                 overlay = 'antenna', plotrange = [0, 0, 0, 180],
                 figfile = 'cal_tsys_'+spw+'_uid___A002_X8a5fcf_X125f.png',
                 interactive = False)



# We can see that the antenna DA50 is acting unexpectedly for all the YY correlations, we will flag the data accordingly

flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms',
         mode = 'manual',
         antenna = 'DA50',
         flagbackup = T)



flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms',
         mode = 'manual',
         antenna = 'DA41',
         flagbackup = T)




#Application of Tsys and WVR caltables

from recipes.almahelpers import tsysspwmap
tsysmap = tsysspwmap(vis = 'uid___A002_X8a5fcf_X125f.ms', tsystable = 'uid___A002_X8a5fcf_X125f.ms.tsys', tsysChanTol = 1)
applycal(vis = 'uid___A002_X8a5fcf_X125f.ms',
         field = '0',
         spw = '17,19,21,23',
         gaintable = ['uid___A002_X8a5fcf_X125f.ms.tsys', 'uid___A002_X8a5fcf_X125f.ms.wvr'],
         gainfield = ['0',''],
         interp = 'linear,linear',
         calwt = T,
         flagbackup = F,
         spwmap = [tsysmap,[]])
applycal(vis = 'uid___A002_X8a5fcf_X125f.ms',
         field = '1',
         spw = '17,19,21,23',
         gaintable = ['uid___A002_X8a5fcf_X125f.ms.tsys', 'uid___A002_X8a5fcf_X125f.ms.wvr'],
         gainfield = ['1',''],
         interp = 'linear,linear',
         calwt = T,
         flagbackup = F,
         spwmap = [tsysmap,[]])
applycal(vis = 'uid___A002_X8a5fcf_X125f.ms',
         field = '3',
         spw = '17,19,21,23',
         gaintable = ['uid___A002_X8a5fcf_X125f.ms.tsys', 'uid___A002_X8a5fcf_X125f.ms.wvr'],
         gainfield = ['2',''],
         interp = 'linear,linear',
         calwt = T,
         flagbackup = F,
         spwmap = [tsysmap,[]])



# Checking the results of the calibrations (1 and 2)

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms',
       xaxis = 'time',
       yaxis = 'phase',
       spw = '17:10~120',
       antenna = '',
       correlation = 'XX',
       avgchannel = '9999',
       coloraxis = 'baseline',
       avgscan = T,
       selectdata = T,
       field = 'J0423-0120')

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms',
       xaxis = 'time',
       yaxis = 'amp',
       spw = '17:10~120',
       antenna = '',
       correlation = 'XX',
       avgchannel = '9999',
       coloraxis = 'baseline',
       avgscan = T,
       selectdata = T,
       field = 'J0423-0120')



# We split out the Science SpWs

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split')
os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.flagversions')
split(vis = 'uid___A002_X8a5fcf_X125f.ms',
      outputvis = 'uid___A002_X8a5fcf_X125f.ms.split',
      datacolumn = 'corrected',                               # keeping only the corected column in the new MS
      spw = '17,19,21,23',                                    # The Target SpWs that will be used later
      keepflags = T)



# listobs of the new MS

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.listobs')
listobs(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
        listfile = 'uid___A002_X8a5fcf_X125f.ms.split.listobs')



# Saving the original flags

flagmanager(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
                mode = 'save',
                versionname = 'Original')




#Inspecting the Amp vs Freq (3)

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
       xaxis = 'channel',
       yaxis = 'amp',
       averagedata = T,
       avgbaseline = T,
       avgtime = '1e8',
       avgscan = T)



# Inspecting Amp vs Time (4)

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
       xaxis = 'time',
       yaxis = 'amp',
       averagedata = T,
       avgchannel = '128',
       coloraxis = 'field',
       iteraxis = 'spw')






#####################################################################
# We did not find any outliers at this stage and hence ther was no  #
# data that was flagged                                             #
#####################################################################

#####################################################
#########################
###################
#############
#####
####
##
#

flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
         mode = 'manual',
         antenna = 'DA42',   # from plot (a)
         spw = '0',
         flagbackup = T)


flagdata(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
         mode = 'manual',
         antenna = 'DA41',    # from plot (a)
         spw = '0',
         flagbackup = T)







#Phase vs Freq (5)

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
       xaxis = 'freq',
       yaxis = 'phase',
       selectdata = True,
       field = 'J0423-0120',
       avgtime = '1E6',
       avgscan = T,
       coloraxis = 'baseline',
       iteraxis = 'antenna')



# Correction for global phase variation with time

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.ap_pre_bandpass')
gaincal(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
        caltable = 'uid___A002_X8a5fcf_X125f.ms.split.ap_pre_bandpass',
        field = '0',                                #J0423-0120
        spw = '*:500~1400',
        solint = 'int',
        refant = 'DV22',      # from plotants, an antenna that is well-behaved and situated near the center 
        calmode = 'p')




# Next, we will inspect the caltable genrated in the previous step 

plotcal(caltable = 'uid___A002_X8a5fcf_X125f.ms.split.ap_pre_bandpass',
        xaxis = 'time',
        yaxis = 'phase',
        poln = 'X',
        plotsymbol = 'o',
        plotrange = [0,0,-180,180],
        iteration = 'spw',
        figfile = 'cal_phase_time_XX.ap_pre_bandpass.png',
        subplot = 221)


# We determine the bandpass solution for our observation

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.bandpass')
bandpass(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
         caltable = 'uid___A002_X8a5fcf_X125f.ms.split.bandpass',
         field = '0',
         solint = 'inf',
         scan = '4',          # only the scan that was used for bandpasss calibration
         refant = 'DV22',
         minblperant = 3,
         minsnr = 3,
         fillgaps = 1,
         solnorm = True,
         bandtype = 'B',
         gaintable = 'uid___A002_X8a5fcf_X125f.ms.split.ap_pre_bandpass')




# Inspecting the bandpass calibration table (a)

plotbandpass(caltable = 'uid___A002_X8a5fcf_X125f.ms.split.bandpass',
             xaxis = 'freq',
             yaxis = 'phase',
             plotrange = [0,0,-80,80],
             overlay = 'antenna',
             solutionTimeThresholdSeconds = 11118,
             interactive = False,
             figfile = 'phasefreq_bandpass.phase.png')
# Phase vs Freq

plotbandpass(caltable = 'uid___A002_X8a5fcf_X125f.ms.split.bandpass',
             xaxis = 'freq',
             yaxis = 'amp',
             overlay = 'antenna',
             solutionTimeThresholdSeconds = 11118,
             interactive = False,
             figfile = 'ampfreq_bandpass.phase.png')
# Amp vs Freq






# Model of the flux calibrator

setjy(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
      field = '1', 
      spw = '0,1,2,3',
      standard = 'manual',
      fluxdensity = [1.57,0,0,0])           #From ALMA Science Database




# Phase corrections needed for the amplitude corrections

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.phase_int')
gaincal(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
        caltable = 'uid___A002_X8a5fcf_X125f.ms.split.phase_int',
        field = '0~1',
        solint = 'int',
        refant = 'DV22',
        gaintype = 'G',
        calmode = 'p',
        gaintable = 'uid___A002_X8a5fcf_X125f.ms.split.bandpass')   # Applying the Bandpass caltable


#######################################################################################################################################
##############################################################################################
############################################################
##########################
#########
###
##
#

# Amplitude corrections

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.ampli_inf')
gaincal(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
        caltable = 'uid___A002_X8a5fcf_X125f.ms.split.ampli_inf',
        field = '0~1',
        solint = 'inf',
        refant = 'DV22',
        gaintype = 'T',
        calmode = 'a',
        gaintable = ['uid___A002_X8a5fcf_X125f.ms.split.bandpass', 'uid___A002_X8a5fcf_X125f.ms.split.phase_int'])   # Applying the Bandpass and Phase caltables




# Appying the Amplitude Corrections

fluxscale(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
          caltable = 'uid___A002_X8a5fcf_X125f.ms.split.ampli_inf',
          fluxtable = 'uid___A002_X8a5fcf_X125f.ms.split.flux_inf',
          reference = '1',
          refspwmap = [0,1,2,3])




# Measuring the Phase corrections at scan level

os.system('rm -rf uid___A002_X8a5fcf_X125f.ms.split.phase_inf')
gaincal(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
        caltable = 'uid___A002_X8a5fcf_X125f.ms.split.phase_inf',
        field = '0~1',
        solint = 'inf',
        refant = 'DV22',
        gaintype = 'G',
        calmode = 'p',
        gaintable = 'uid___A002_X8a5fcf_X125f.ms.split.bandpass')   # Applying the Bandpass caltable




# Inspecting the amplitude caltable

plotcal(caltable = 'uid___A002_X8a5fcf_X125f.ms.split.ampli_inf',
        xaxis = 'time',
        yaxis = 'amp',
        plotsymbol = 'o',
        plotrange = [],
        iteration = 'spw',
        figfile = 'cal_amp_time.png',
        subplot = 221)




# Inspecting the Phase caltable

plotcal(caltable = 'uid___A002_X8a5fcf_X125f.ms.split.phase_inf',
        xaxis = 'time',
        yaxis = 'phase',
        plotsymbol = 'o',
        plotrange = [0,0,-180,180],
        iteration = 'spw',
        figfile = 'cal_phase_time.png',
        subplot = 221)



# Applying the Bandpass, Phase and Flux calibrations to our flux calibrator

applycal(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
         field = '1',
         gaintable = ['uid___A002_X8a5fcf_X125f.ms.split.bandpass', 'uid___A002_X8a5fcf_X125f.ms.split.phase_int', 'uid___A002_X8a5fcf_X125f.ms.split.flux_inf'],
         gainfield = ['', '1', '1'],
         interp = 'linear,linear',
         calwt = T,
         flagbackup = F)




# Applying the Bandpass, Phase and Flux calibrations to our other two sources

applycal(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
         field = '0,3',
         gaintable = ['uid___A002_X8a5fcf_X125f.ms.split.bandpass', 'uid___A002_X8a5fcf_X125f.ms.split.phase_inf', 'uid___A002_X8a5fcf_X125f.ms.split.flux_inf'],
         gainfield = ['', '0', '0'],
         interp = 'linear,linear',
         calwt = T,
         flagbackup = F)




# Inspection of the calirated data

# Phase vs UVdist of J0423-013  (6)

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
       xaxis = 'uvdist',
       yaxis = 'phase',
       ydatacolumn = 'data',  # Uncalibrated data, 'corrected' for the calibrated data
       selectdata = True,
       field = 'J0423-013',
       averagedata = True,
       avgchannel = '9999',
       avgtime = '1e6s',
       avgscan = True,
       coloraxis = 'spw') 




# Phase vs Time of J0423-0120  (7)

plotms(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
       xaxis = 'time',
       yaxis = 'phase',
       ydatacolumn = 'data',  # Uncalibrated data, 'corrected' for the calibrated data
       selectdata = True,
       field = 'J0423-0120',
       averagedata = True,
       avgchannel = '9999',
       coloraxis = 'spw')



# Phase vs Frequency of J0423-0120  (8)


plotms(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
       xaxis = 'freq',
       yaxis = 'phase',
       ydatacolumn = 'data',  # Uncalibrated data, 'corrected' for the calibrated data
       selectdata = True,
       field = 'J0423-0120',
       averagedata = True,
       avgchannel = '',
       avgtime = '1e8',
       avgscan = True,
       coloraxis = 'spw')




# Imaging the Phase Calibrator


os.system('rm -rf phasecal_cont*')
clean(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
      imagename = 'phasecal_cont',
      field = 'J0423-0120',
      spw = '*:50~1870',
      selectdata = T,
      mode = 'mfs',
      niter = 300,
      threshold = '0.75mJy',
      psfmode = 'hogbom',
      interactive = False,
      mask = [118, 118, 138, 138],
      imsize = 256,                 
      cell = '0.15arcsec',         # FWHM_synthesizedbeam is approx 0.65arcsec
      weighting = 'briggs',
      robust = 0.0)


viewer()





 









	















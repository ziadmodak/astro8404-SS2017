

###############################
# THE SCRIPT STARTS FROM HERE #
###############################


import os


# splitting out the target field from the calibrated MS

os.system('rm -rf ngc1614_line_target.ms*')
split(vis = 'uid___A002_X8a5fcf_X125f.ms.split',
      outputvis = 'ngc1614_line_target.ms',
      field = 'ngc_1614')



# visual inspection to identify the emission line features of the target

plotms(vis='ngc1614_line_target.ms',
       spw='',
       xaxis='channel',
       yaxis='amp',
       avgtime='1e8',
       avgscan=T,
       iteraxis='spw')



# dirty map of the continuum emission

os.system('rm -rf result-ngc1614_cont_dirty.*')
clean(vis='ngc1614_line_target.ms',
      imagename='result-ngc1614_cont_dirty',
	   spw='0:100~800;1100~1800,1:100~1800,2:100~1800,3:100~1800',    # select the SpWs such that line emission is excluded
	   psfmode='hogbom',
	   mode='mfs',
	   niter=0,
	   imsize=128,                       # 128 by 128 pixels
	   cell='0.15arcsec',                # about 4 pixels per FWHM of the synthesized beam
	   weighting='briggs',
	   robust=0.0, 
	   interactive=False,
	   usescratch=False)

viewer()          # to ientify an emission free part in the image





# noise in an emission free corner of the image

stats_cont_dirty = imstat(imagename='result-ngc1614_cont_dirty.image',
                          axes=[0,1],
                          box='80,80,127,127') 

rms_cont_dirty=stats_cont_dirty["rms"][0]*1e3   #rms-noise of dirty continuum image in mJy/beam (sigma)

 
clthr_cont=1.5*rms_cont_dirty                   #maximum remaining residual when cleaning (1.5*sigma)
clthr_cont="{:.1f}".format(clthr_cont)+'mJy'

	     

     
# clean map of the continuum emission

os.system('rm -rf result-ngc1614_cont.*')
clean(vis='ngc1614_line_target.ms',
      imagename='result-ngc1614_cont',
	   spw='0:100~800;1100~1800,1:100~1800,2:100~1800,3:100~1800',
	   psfmode='hogbom',
	   mode='mfs',
	   niter=500,
	   threshold=clthr_cont, 
	   mask=[56,56,77,77],         # masking the part with the assumed galaxy emission
	   imsize=128,
	   cell='0.15arcsec',
	   weighting='briggs',
	   robust=0.0, 
	   interactive=False,
	   usescratch=False) 
	   
viewer()


# noise in an emission free corner of the image
stats_cont = imstat(imagename='result-ngc1614_cont.image',
                    axes=[0,1],
                    box='80,80,127,127')
rms_cont=stats_cont["rms"][0]   #rms-noise of continuum image in mJy/beam


# peak emission in the continuum image
stats_cont = imstat(imagename='result-ngc1614_cont.image',
                    axes=[0,1],
                    box='56,56,77,77')
peak_cont=stats_cont["max"][0]  #peak-flux of continuum image in mJy/beam


dyn_cont=peak_cont/rms_cont  #dynamic range in continuum image	   
	   
print rms_cont*1e3, peak_cont*1e3, dyn_cont






# dirty (robust) continuum map
os.system('rm -rf result-ngc1614_cont_dirty_uw.*')
clean(vis='ngc1614_line_target.ms',
      imagename='result-ngc1614_cont_dirty_uw',
	   spw='0:100~800;1100~1800,1:100~1800,2:100~1800,3:100~1800',
	   psfmode='hogbom',
	   mode='mfs',
	   niter=0,
	   imsize=128,
	   cell='0.15arcsec',
	   weighting='briggs',
	   robust=-2.0, 
	   interactive=False,
	   usescratch=False)

viewer()

	  

# noise in an emission free corner of the image
stats_cont_dirty_uw = imstat(imagename='result-ngc1614_cont_dirty.image',
                          axes=[0,1],
                          box='80,80,127,127') 

rms_cont_dirty_uw=stats_cont_dirty_uw["rms"][0]*1e3   # rms noise of dirty continuum image in mJy/beam 

 
clthr_cont_uw=1.5*rms_cont_dirty_uw                   # maximum remaining residual when cleaning
clthr_cont_uw="{:.1f}".format(clthr_cont_uw)+'mJy'



# robust continuum map
os.system('rm -rf result-ngc1614_cont_uw.*')
clean(vis='ngc1614_line_target.ms',
      imagename='result-ngc1614_cont_uw',
	   spw='0:100~800;1100~1800,1:100~1800,2:100~1800,3:100~1800',
	   psfmode='hogbom',
	   mode='mfs',
	   niter=500,
	   threshold=clthr_cont_uw, 
	   mask=[56,56,77,77],
	   imsize=128,
	   cell='0.15arcsec',
	   weighting='briggs',
	   robust=-2.0, 
	   interactive=False,
	   usescratch=False) 
	   
viewer()



stats_cont_uw = imstat(imagename='result-ngc1614_cont_uw.image',
                       axes=[0,1],
                       box='80,80,127,127')
rms_cont_uw=stats_cont_uw["rms"][0]   #rms-noise of continuum image in mJy/beam


stats_cont_uw = imstat(imagename='result-ngc1614_cont_uw.image',
                       axes=[0,1],
                       box='56,56,77,77')
peak_cont_uw=stats_cont_uw["max"][0]  #peak-flux of continuum image in mJy/beam


dyn_cont_uw=peak_cont_uw/rms_cont_uw  #dynamic range in continuum image	   
	   
print rms_cont_uw*1e3, peak_cont_uw*1e3, dyn_cont_uw


	     
#Output a png-image of the clean continuum maps using viewer()



#Subtract continuum emission from line channels (baseline fitting)                                 

uvcontsub(vis = 'ngc1614_line_target.ms',
	  fitspw='0:100~800;1100~1800,1:100~1800,2:100~1800,3:100~1800',
	  solint ='int', 
	  fitorder = 1,      # We fit a linear baseline
	  combine='spw')    






#dirty cube of the line emission	  
os.system('rm -rf result-ngc1614_line_CO_dirty.*')
clean(vis='ngc1614_line_target.ms.contsub',
      imagename='result-ngc1614_line_CO_dirty',
      spw='0:801~1099',                         # Selecting only the channels with the line emission
      mode='channel',
      start='',
      nchan=298,
      width='',
      psfmode='hogbom',
      outframe='LSRK',
      restfreq='115.271201800GHz',          # rest frequency of the CO line
      niter=0,
      interactive=F,
      imsize=256,
      cell='0.15arcsec', 
      weighting='briggs',
      robust=0.0,
      usescratch=False) 
      


stats_line = imstat(imagename='result-ngc1614_line_CO_dirty.image',
                    axes=[0,1],
                    box='160,160,255,255') 
rms_line=stats_line["rms"].mean()             # rms noise in an emission free region

rms_line_expect=rms_cont_dirty*sqrt(6500.)    # expected noise (6500 is the number of channels)

print rms_line*1e3, rms_line_expect

clthr_line=2.0*rms_line_expect                
clthr_line="{:.1f}".format(clthr_line)+'mJy'  # clean-threshold 




# clean data cube of the line emission
os.system('rm -rf result-ngc1614_line_CO.*')
clean(vis='ngc1614_line_target.ms.contsub',
      imagename='result-ngc1614_line_CO',
      spw='0:801~1099',
      mode='channel',
      start='',
      nchan=298,
      width='',
      psfmode='hogbom',
      outframe='LSRK',
      restfreq='115.271201800GHz',
      mask=[106,106,158,158],
      niter=2000,
      interactive=F,   
      imsize=256,
      cell='0.15arcsec', 
      weighting='briggs',
      robust=0.0,                # robust parameter 0.0
      threshold=clthr_line,
      usescratch=False) 	  
      

# Image analysis using immoments
# moment = 0 (Integrated flux image)
os.system('rm -rf result-ngc1614_CO1-0.mom0*')
immoments(imagename='result-ngc1614_line_CO.image',
          moments=[0],
          chans='75~234',
          axis='spectral',
          outfile='result-ngc1614_CO1-0.mom0')

# moment = 1 (velocity field)
os.system('rm -rf result-ngc1614_CO1-0.mom1*')
immoments(imagename='result-ngc1614_line_CO.image',
          moments=[1],
          chans='75~234',
          axis='spectral',
          includepix=[0.017, 10000],                 # using a lower threshold
          outfile='result-ngc1614_CO1-0.mom1')

# moment = 2 (velocity dispersion)
os.system('rm -rf result-ngc1614_CO1-0.mom2*')
immoments(imagename='result-ngc1614_line_CO.image',
          moments=[2],
          chans='75~234',
          axis='spectral',
          includepix=[0.017, 10000],
          outfile='result-ngc1614_CO1-0.mom2')



# PNG images were generated using viewer 
viewer()


#################
# End of script #
#################






	   
      


	   





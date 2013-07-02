;============================ GRAV_IMAGE_DISC ==========================
;Program to fit non-paramteric Kz force functions. 

PRO grav_image_disc

;Set up the common block:
setcommon
COMMON constants

;Set screen output for testing:
testplot = 'yes'
IF (testplot EQ 'yes') THEN devtype='X' $
ELSE devtype = 'PS'
set_plot,devtype

;Set truetype fonts:
!P.FONT=-1
!P.CHARSIZE = 1.5
!P.THICK = 4
!X.STYLE = 1
!Y.STYLE = 1

;TO DO:
;ANALYSE FIRST TEST RESULTS + UPDATE PAPER DRAFT 
;TIDY CODE + PUT ON GITHUB 
;IMPLEMENT CHANGES IN SPHERICAL CODE 

IF (devtype EQ 'X') THEN BEGIN 
   window,xsize=700,ysize=700
   device,decomposed=0
ENDIF
!P.multi=[0,2,2]

;Set up my colour pallette:
mymakecolour

;Units: 
G1 = 6.67d-11 * 1.989d30 / 3.086d19 / 1000.^2.

;Set which data to fit: 
dowhich = 'sim'

;Use Liklihood function, or binned data? 
uselike = 'yes'

;Priors:
gprior = -1                     ;Gradient [-1=no; not rec.]
cprior = -1                     ;Central pixel [-1=no]
bprior = 'yes'                  ;Bar. min surf.
sprior = 'no'                   ;Rising sig_z [not rec.]
mirror = 'yes'                  ;'Mirror' prior [red. if using log]
logprior = 'yes'                ;Log sample prior
lbprior = 'no'                  ;'Last bin' prior [not rec.]
lbtol = 0.25                    ;
constdm = 'yes'                 ;Constant DM density
rprior = 'yes'                  ;Regularize Nuz 
nutol = 3.0                     ;
kprior = 'yes'                  ;Regularize rho_dm
ktol = 3.0                      ;
quadratic = 'no'                ;Linear or quad interpol. 
monotonic = 'yes'               ;Mono-prior on nu(z)

;Initial parameters [-1 = set to default]:
norm1 = -1
nupars = -1
kzpars = -1

;Tilt correction [-1 = default = no] 
tparsRin = -1
tparsRt = -1

;Mean velocity/z correction [default = no]
vcorrect = 'no'
zcorrect = 'no'

;Step size [-1 = default]
nuparstep = -1
kzparstep = -1
normstep = -1

;Low/high-z range = min/max of data [-1 = default]: 
zpmin = -1 
zpmax = -1 

;Min/max Kz for MCMC search [only affects logprior].
;If positive assume constant; if negative take fraction
;of local baryonic value for that bin: 
kzmin = 0.0075 * (4.0 * !PI * G1) * 1000.^3.
kzmax = 100.*kzmin
numin = 1d-3
numax = 1d0
 
;Set number of terms for kz+tracer models:   
adderrors = 'no'
nusimpstart = 'no'
IF (dowhich EQ 'sim') THEN BEGIN
   ;Number of bins: 
   nbin = +12
   nt_kz = nbin
   patch = '45'
   datafile = '/home/ast/read/dark/sgarbari/Justin/FETTAden+vz_a'+patch+'_4p_R250_r85_vphi.txt'
   basename = '/home/ast/user/jread/Data/Local_dm/Met_data/6_6_'+patch+'/metdist_nolike'+$
              strcompress(string(nbin),/remove_all)
   surfsim = '/home/ast/user/jread/Data/Local_dm/Sim_data/Surfaceden/SigmaS_z_a'+patch+'.txt'

   zpmin = 1d-5
   zpmax = -1
   baryonmodel = 'sim'

   ;Load in the binned data:
   nufile = '/home/ast/user/jread/Data/Local_dm/Sim_data/j_den_'+patch+'.txt'
   sigfile = '/home/ast/user/jread/Data/Local_dm/Sim_data/j_sigma_'+patch+'.txt'
   surfsfile = '/home/ast/user/jread/Data/Local_dm/Sim_data/Surfaceden/SigmaS_z_a'+patch+'.txt'
   surfdmfile = '/home/ast/user/jread/Data/Local_dm/Sim_data/Surfaceden/SigmaDM_z_a'+patch+'.txt'
   readcol,nufile,z_bin,nu_bin,nu_err_bin
   readcol,sigfile,z_bin,sig_bin,sig_err_bin
   readcol,surfsfile,zsurf,sigs_surf,sigs_surferr
   readcol,surfdmfile,zsurfdm,sigdm_surf,sigdm_surferr

   ;Mean vel. correction: 
   vmpars = dblarr(nbin) + 1.0
   vmparst = vmpars
   vmparstep = dblarr(nbin) + 5.0
   zshift = double(0)
   zshiftt = zshift
   zshiftstep = double(0.01)

   ;Tilt:
   Rsun = 8.5
   hr = 3.0
   hsig = 3.0

;   tparsRin = [Rsun, hr, hsig]
   tparsRin = -1
   tparsRerr = [0., 0., 0.]
   ntparsR = n_elements(tparsRin) 

   ntpars = nbin
   tpars = dblarr(ntpars)
   tparsw = dblarr(ntpars)
   tparstep = -1
ENDIF

IF (dowhich EQ 'simple') THEN BEGIN 
   ;Set up simple population here using analytic formulae: 
   zmin = 0. 
   zmax = 1.2 
   zpnts = 5000 
   zth = dindgen(zpnts) * (zmax-zmin)/double(zpnts-1) + zmin 
   z0 = 0.25
   K = 1.0 * 1650.
   F = 0.1 * 1650.
   C = 17.^2.
   D = 0.25
   z02 = 0.4

   ;Draw mock data: 
   nu_zth = exp(-zth/z0)
   Kz_zth = -(K*zth/sqrt(zth^2.+D^2.) + 2.0 * F * zth)

   adddarkdisc = 'no'
   IF (adddarkdisc EQ 'yes') THEN BEGIN 
      DD = 0.6
      KD = 0.15 * 1650.
      Kz_zth = Kz_zth - KD*zth/sqrt(zth^2.+DD^2.)
   ENDIF 

   inti = dblarr(zpnts) 
   FOR i=1L,zpnts-1 DO $
      inti(i) = int_tabulated(zth(0:i),Kz_zth(0:i)*nu_zth(0:i))
   sigzth = sqrt(inti / nu_zth + C / nu_zth)

   nstars = 1e3
   ran = randomu(seed,/double,nstars)*z0
   zstar = -z0 * ALOG(1.0 - ran/z0)
   sigzstar = interpol(sigzth,zth,zstar) > 0
   ran2 = randomn(seed,/double,nstars,/normal)
   vzstar = ran2 * sigzstar

   ;Add second population [thick-disc like]: 
   addpoptwo = 'no'
   fac2 = 0.1
   IF (addpoptwo EQ 'yes') THEN BEGIN 
      nu_zth = exp(-zth/z0) + fac2 * exp(-zth/z02)
      inti = dblarr(zpnts)
      FOR i=1L,zpnts-1 DO $
         inti(i) = int_tabulated(zth(0:i),Kz_zth(0:i)*nu_zth(0:i))
      sigzth = sqrt(inti / nu_zth + C / nu_zth)
      nstars2 = nstars * fac2
      ran = randomu(seed,/double,nstars2)*z02
      zstar2 = -z02 * ALOG(1.0 - ran/z02)
      zstar = [zstar,zstar2]
      
      sigzstar = interpol(sigzth,zth,zstar) > 0
      ran2 = randomn(seed,/double,nstars+nstars2,/normal)
      vzstar = ran2 * sigzstar
   ENDIF

   ;Cut on zmax:
   z_dat = zstar(where(zstar LT zmax)) 
   vz_dat = vzstar(where(zstar LT zmax))

   ;Cut zero velocities: 
   z_dat = z_dat(where(abs(vz_dat) GT 0))
   vz_dat = vz_dat(where(abs(vz_dat) GT 0))

   ;Calulate binned data (for plots/binned anal.): 
   zbin = 0.05
   index = sort(z_dat)
   binsmooth,z_dat(index),vz_dat(index)^2.,zmin,zmax,zbin,$
             z_dat_bin,sig_dat_bin,0.,count_bin
   sig_dat_bin = sqrt(sig_dat_bin)
   sig_dat_err_bin = sig_dat_bin / sqrt(count_bin)

   bincount,z_dat(index),zmin,zmax,zbin,z_dat_bin,nu_dat_bin,count_bin
   nu_dat_err_bin = nu_dat_bin / sqrt(count_bin)
   renorm = max(nu_dat_bin)
   nu_dat_bin = nu_dat_bin / renorm
   nu_dat_err_bin = nu_dat_err_bin / renorm

   ;Parameters for the fitting routines: 
   nbin = +8
   nt_kz = nbin
   basename = '/home/ast/user/jread/Data/Local_dm/Met_data/Simple/metdist_2comp_1e3'+$
              strcompress(string(nbin),/remove_all)

   ;"simple" settings: 
   bprior = 'yes'
   baryonmodel = 'simple'
   zpmin = 1d-5

   ;If using vel./pos. shift correct: 
   vmpars = dblarr(nbin) + 1.0
   vmparst = vmpars
   vmparstep = dblarr(nbin) + 5.0
   zshift = double(0)
   zshiftt = zshift
   zshiftstep = double(0.01)
   
   IF (uselike EQ 'no') THEN BEGIN
      z_dat = z_dat_bin(where(z_dat_bin GT 0))
      nu_dat = nu_dat_bin(where(z_dat_bin GT 0))
      sig_dat = sig_dat_bin(where(z_dat_bin GT 0))
      nu_dat_err = nu_dat_err_bin(where(z_dat_bin GT 0))
      sig_dat_err = sig_dat_err_bin(where(z_dat_bin GT 0))
   ENDIF

   ;Kz-fix - TEST:
   kzsimpfix = 'no'
   nusimpfix = 'no'
   nusimpstart = 'no'
ENDIF 

IF (dowhich EQ 'kg') THEN BEGIN

   ;Needs to be finished!!!

ENDIF

;Iterations:
niter = LONG(50000)


;*************************************************************
;DATA

;Read in the data:
IF (dowhich EQ 'sim') THEN BEGIN 
   readcol,datafile,mass,x_dat,y_dat,z_dat,vz_dat,vx_dat,vy_dat,pot_dat
   IF (max(mass) NE min(mass)) THEN BEGIN 
      print,'**** Multimass data not yet supported ****'
      stop
   ENDIF

   z_mean = total(z_dat)/double(n_elements(z_dat))
   vz_mean = total(vz_dat)/double(n_elements(z_dat))
   
   print,'Zmean:',z_mean
   print,'Vzmean:',vz_mean

;   z_dat = z_dat - z_mean
;   vz_dat = vz_dat - vz_mean

   ;Add errors:
   adderrors = 'no'
   IF (adderrors EQ 'yes') THEN BEGIN
      ;Assume normal errors for now: 
      xerrfac = 10.0
      yerrfac = 10.0
      zerrfac = 10.0
      vxerrfac = 10.0
      vyerrfac = 10.0
      vzerrfac = 10.0
      x_dat_err = abs(x_dat / xerrfac)
      y_dat_err = abs(y_dat / yerrfac)
      z_dat_err = abs(z_dat / zerrfac)
      vx_dat_err = abs(vx_dat / vxerrfac)
      vy_dat_err = abs(vy_dat / vyerrfac)
      vz_dat_err = abs(vz_dat / vzerrfac)

      x_dat = x_dat + randomn(seed,/double,n_elements(z_dat),$
                              /normal) * x_dat_err
      y_dat = y_dat + randomn(seed,/double,n_elements(z_dat),$
                              /normal) * y_dat_err
      z_dat = z_dat + randomn(seed,/double,n_elements(z_dat),$
                              /normal) * z_dat_err
      vx_dat = vx_dat + randomn(seed,/double,n_elements(z_dat),$
                                /normal) * vx_dat_err
      vy_dat = vy_dat + randomn(seed,/double,n_elements(z_dat),$
                                /normal) * vy_dat_err
      vz_dat = vz_dat + randomn(seed,/double,n_elements(z_dat),$
                                /normal) * vz_dat_err
   ENDIF

   ;Slice and dice the data:
   slicedata = 'no'
   IF (slicedata EQ 'yes') THEN BEGIN 
      ;Cut in angle:
      R_dat = sqrt(x_dat^2. + y_dat^2.)
      theta = atan(y_dat,x_dat)
      theta = theta - total(theta)/double(n_elements(theta))
      angle = max(theta) / 4.0
      x_cut = x_dat(where(abs(theta) LT angle))
      y_cut = y_dat(where(abs(theta) LT angle))
      z_cut = z_dat(where(abs(theta) LT angle))
      vx_cut = vx_dat(where(abs(theta) LT angle))
      vy_cut = vy_dat(where(abs(theta) LT angle))
      vz_cut = vz_dat(where(abs(theta) LT angle))
      
      ;Cut in z:
;      zmin = min(z_cut)
      zmin = 0.
      x_cut = x_cut(where(z_cut GT zmin))
      y_cut = y_cut(where(z_cut GT zmin))
      z_cut = z_cut(where(z_cut GT zmin))
      vx_cut = vx_cut(where(z_cut GT zmin))
      vy_cut = vy_cut(where(z_cut GT zmin))
      vz_cut = vz_cut(where(z_cut GT zmin))

      ;Cut in R: 
      R_cut = sqrt(x_cut^2. + y_cut^2.)
      Rmin = min(R_cut)
      Rmax = max(R_cut)
      x_dat = x_cut(where(R_cut GT Rmin AND R_cut LT Rmax))
      y_dat = y_cut(where(R_cut GT Rmin AND R_cut LT Rmax))
      z_dat = z_cut(where(R_cut GT Rmin AND R_cut LT Rmax))
      vx_dat = vx_cut(where(R_cut GT Rmin AND R_cut LT Rmax))
      vy_dat = vy_cut(where(R_cut GT Rmin AND R_cut LT Rmax))
      vz_dat = vz_cut(where(R_cut GT Rmin AND R_cut LT Rmax))

      ;Downsample:
      nfrac = 1.0
      step = 1.0/nfrac
      nn = 0L
      FOR jj=0L,n_elements(z_dat)-1,step DO BEGIN 
         x_cut(nn) = x_dat(jj)
         y_cut(nn) = y_dat(jj)
         z_cut(nn) = z_dat(jj)
         vx_cut(nn) = vx_dat(jj)
         vy_cut(nn) = vy_dat(jj)
         vz_cut(nn) = vz_dat(jj)
         nn = nn + 1
      ENDFOR
      x_dat = x_cut(0:nn-1)
      y_dat = y_cut(0:nn-1)
      z_dat = z_cut(0:nn-1)
      vx_dat = vx_cut(0:nn-1)
      vy_dat = vy_cut(0:nn-1)
      vz_dat = vz_cut(0:nn-1)
   ENDIF
   R_dat = sqrt(x_dat^2.+y_dat^2.)
   vR_dat = (vx_dat*x_dat+vy_dat*y_dat)/R_dat
 
   IF (testplot EQ 'yes') THEN BEGIN 
      ;Test whether dist. are really Gaussian or not: 
      histvz = histogram(vz_dat,binsize=2.5,locations=binsvz)
      histz = histogram(z_dat,binsize=0.05,locations=binsz)
      histvzvR = histogram(vz_dat*vR_dat,binsize=25.0,locations=binsvzvR)
 
      ;Cut a zbin 
      zmin = 0.4
      zmax = 0.6
      zcut = z_dat(where(z_dat GT zmin AND z_dat LT zmax))
      vzcut = vz_dat(where(z_dat GT zmin AND z_dat LT zmax))
      vRcut = vR_dat(where(z_dat GT zmin AND z_dat LT zmax))

      histvzbin = histogram(vzcut,binsize=2.5,locations=binsvzcut)
      histzbin = histogram(zcut,binsize=0.05,locations=binszcut)
      histvzvRbin = histogram(vzcut*vRcut,binsize=100.0,locations=binsvzvRcut)
 
      plot,binsz,histz,psym=10
      oplot,binszcut,histzbin,psym=10,color=2
 
      plot,binsvz,histvz/double(max(histvz)),psym=10
      oplot,binsvzcut,histvzbin/double(max(histvzbin)),psym=10,color=2
      sigvz = 20.
      oplot,binsvzcut,exp(-binsvzcut^2./2./sigvz^2.),linestyle=1

      plot,binsvzvR,histvzvR/double(max(histvzvR)),psym=10,xrange=[-2000,2000]
      oplot,binsvzvRcut,histvzvRbin/double(max(histvzvRbin)),psym=10,color=2

      ;Assume "normal product" distribution [e.g. Wolfram Mathworld]: 
      sigRz = 2500. 
      meanbfunc = 100.
      tmin = -20001.
      tmax = 20001. 
      tpnts = 10000 
      test = dindgen(tpnts)*(tmax-tmin)/double(tpnts) + tmin
      bfunc = BESELK((abs(test-meanbfunc))/sigRz,0)
      oplot,test,bfunc/max(bfunc),linestyle=1

      mean = int_tabulated(test,bfunc*test) / int_tabulated(test,bfunc)
      print,'mean:',mean,meanbfunc

      ;Dummy plot to make it 4!
      plot,binsvzvR,histvzvR/double(max(histvzvR))
   ENDIF

   ;Calculate and output binned data:
   zbin = 0.05
   index = sort(z_dat)
   binsmooth,z_dat(index),vz_dat(index)^2.,-1.2,1.2,zbin,$
             z_dat_bin,sig_dat_bin,0.,count_bin
   sig_dat_bin = sqrt(sig_dat_bin)
   sig_dat_err_bin = sig_dat_bin / sqrt(count_bin)
   binsmooth,z_dat(index),vz_dat(index)*vR_dat(index),-1.2,1.2,zbin,$
             z_dat_bin,sigRz_dat_bin,0.,count_bin
   sigRz_dat_err_bin = sigRz_dat_bin / sqrt(count_bin)
   bincount,z_dat(index),-1.2,1.2,zbin,z_dat_bin,nu_dat_bin,count_bin
   nu_dat_err_bin = nu_dat_bin / sqrt(count_bin)
   renorm = max(nu_dat_bin)
   nu_dat_bin = nu_dat_bin / renorm
   nu_dat_err_bin = nu_dat_err_bin / renorm

   IF (uselike EQ 'no') THEN BEGIN
      z_dat = z_dat_bin(where(z_dat_bin GT 0))
      nu_dat = nu_dat_bin(where(z_dat_bin GT 0))
      sig_dat = sig_dat_bin(where(z_dat_bin GT 0))
      nu_dat_err = nu_dat_err_bin(where(z_dat_bin GT 0))
      sig_dat_err = sig_dat_err_bin(where(z_dat_bin GT 0))
      sigRz_dat = sigRz_dat_bin(where(z_dat_bin GT 0))
      sigRz_dat_err = sigRz_dat_err_bin(where(z_dat_bin GT 0))
   ENDIF
ENDIF

IF (dowhich EQ 'kg') THEN BEGIN 
   ;Need to specify data format here. TO BE DONE. 

   ;Don't forget to add error functions too! 

   ;Don't forget to think about separation of z and z,vz data! 

   IF (tparsRin(0) GT 0) THEN BEGIN 
   ;Need to load in "tilt" data file here. TO BE DONE. 
   ENDIF
ENDIF

;Flag + set up priors
IF (gprior GT 0) THEN basename = basename + '_gprior'
IF (gprior LT 0) THEN gprior = 1d30
IF (cprior GE 0) THEN basename = basename + '_cprior'
IF (cprior LT 0) THEN cprior = 1d30
IF (mirror EQ 'yes') THEN basename = basename + '_mirr'
IF (logprior EQ 'yes') THEN basename = basename + '_log'
IF (lbprior EQ 'yes') THEN basename = basename + '_lb'
IF (bprior EQ 'yes') THEN basename = basename + '_bprior'
IF (sprior EQ 'yes') THEN basename = basename + '_sprior'
IF (vcorrect EQ 'yes') THEN basename = basename + '_vcorrect'
IF (zcorrect EQ 'yes') THEN basename = basename + '_zcorrect'
IF (constdm EQ 'yes') THEN basename = basename + '_constdm'
IF (rprior EQ 'yes') THEN basename = basename + '_rprior'
IF (kprior EQ 'yes') THEN basename = basename + '_kprior'
IF (quadratic EQ 'yes') THEN basename = basename + '_quad'
IF (monotonic EQ 'yes') THEN basename = basename + '_mono'

;Output binned data (now that basename is fully specified): 
arraydump,basename+'_nu_dat_bin.txt',[[z_dat_bin],[nu_dat_bin],[nu_dat_err_bin]],3
arraydump,basename+'_sigz_dat_bin.txt',[[z_dat_bin],[sig_dat_bin],[sig_dat_err_bin]],3

;Bprior:
IF (bprior EQ 'yes') THEN BEGIN 
   ;Load the baryonic model: 
   IF (baryonmodel EQ 'silvia') THEN BEGIN 
      readcol,'/home/ast/user/jread/Data/Local_dm/Vis/Sigma_MM.txt',$
              zvis,sigexpvis,sigexpviserr,sigsecvis,sigsecviserr
      sigusevis = sigsecvis
      siguseviserr = sigsecviserr
   ENDIF
   IF (baryonmodel EQ 'sim') THEN BEGIN
      surfsfile = surfsim
      readcol,surfsfile,zvis,sigusevis,siguseviserr
   ENDIF   
   IF (baryonmodel EQ 'simple') THEN BEGIN 
      zvis = zth 
      sigusevis = K*zth/sqrt(zth^2.+D^2.) / (2.0*!PI*G1) / 1000^2.
      siguseviserr = sigusevis*0.01
   ENDIF
   sigvismin = sigusevis - siguseviserr
ENDIF

;Binning in z:
IF (zpmin LT 0) THEN zpmin = min(z_dat)
IF (zpmax LT 0) THEN zpmax = max(z_dat)
IF (nbin GT 0) THEN BEGIN
   zp_kz = dindgen(nt_kz) * (zpmax - zpmin) / double(nt_kz-1) + zpmin
ENDIF ELSE BEGIN
   ;Adaptive auto-binning here:
   zabs = abs(z_dat)
   index = sort(zabs)
   zsort = zabs(index)
   numperbin = abs(nbin) 
   ztmp = dblarr(n_elements(zsort))
   jl = 0L
   jr = 0L
   nbin = 0L
   WHILE (jr LT n_elements(zsort)-1) DO BEGIN 
      jr = jl + numperbin
      IF (jr GT n_elements(zsort)-1) THEN jr = n_elements(zsort)-1 
      ztmp(nbin) = total(zsort(jl:jr-1))/double(jr-jl)
      nbin = nbin + 1
      jl = jl + numperbin
   ENDWHILE
   nt_kz = nbin
   zp_kz = ztmp(0:nbin-1)
ENDELSE 

;Convert gprior into appropriate units: 
IF (gprior GT 0) THEN $
   gpriorconv = gprior * (2.*!PI*G1) * 1000.^2. $
ELSE gpriorconv = 1d30
IF (cprior GE 0) THEN $
   cpriorconv = cprior * (2.*!PI*G1) * 1000.^2. $
ELSE cpriorconv = 1d30

;Set up bprior:
IF (bprior EQ 'yes') THEN BEGIN
   bsurf = interpol(sigvismin,zvis,zp_kz) 
   blow = bsurf * (2.*!PI*G1) * 1000.^2.
ENDIF ELSE blow = dblarr(n_elements(zp_kz)) + 1d-5

;Set up kzmin/max arrays:
kzminarr = dblarr(nt_kz) + kzmin
kzmaxarr = dblarr(nt_kz) + kzmax

;Default Initial seed guess parameters [assume flat]:
IF (kzpars(0) LT 0) THEN BEGIN
   kzpars = dblarr(nt_kz) + kzmin/100.
;   kzpars(0) = kzmin
   kzpars(0) = kzmin * 2.0
ENDIF
IF (nupars(0) LT 0) THEN BEGIN 
   nupars = dblarr(nt_kz) + numin * 2.0
ENDIF
IF (norm1 LT 0) THEN norm1 = 20.^2.
IF (dowhich EQ 'simple') THEN BEGIN 
   IF (kzsimpfix EQ 'yes') THEN BEGIN 
      ;For test purposes:
      blow = interpol(abs(Kz_zth),zth,zp_kz)
      kzmin = 1d-2
      kzminarr = dblarr(n_elements(zp_kz)) + kzmin      
      kzpars = dblarr(n_elements(zp_kz)) + kzmin * 2.0
      constdm = 'no'
   ENDIF
   IF (nusimpfix EQ 'yes') THEN BEGIN
      ;For test purposes:
      nupars = interpol(abs(nu_zth),zth,zp_kz)
   ENDIF
ENDIF
IF (nusimpstart EQ 'yes') THEN BEGIN
   ;Seed "good" nupars: 
   nupars = interpol(nu_dat_bin/max(nu_dat_bin),z_dat_bin,zp_kz)
ENDIF


;*************************************************************
;Metropolis parameters here:
pars = [nupars,kzpars,norm1]
npars = n_elements(pars)        ;total number of parameters
metarray = $
  dblarr(npars+1,niter)
IF (nuparstep(0) LT 0) THEN nuparstep = dblarr(nt_kz) + 0.1
IF (kzparstep(0) LT 0) THEN kzparstep = dblarr(nt_kz) + 50.
IF (normstep LT 0) THEN normstep = 50.
parstep = [nuparstep,kzparstep,normstep]

IF (tparsRin(0) GT 0) THEN BEGIN
   IF (tparstep LT 0) THEN BEGIN 
      tparstep = dblarr(ntpars) + 50. 
      tparswstep = dblarr(ntpars) + 50.
   ENDIF
   mettpars = dblarr(ntpars+ntparsR,niter)
   tparsR = tparsRin
ENDIF

;Logarithmic prior: 
IF (logprior EQ 'yes') THEN BEGIN 
   lpars = alog10(pars) 
   lparstep = lpars 
   lparstep(0:nt_kz-1) = 1.0
   lparstep(nt_kz:nt_kz+nt_kz-1) = 2.0
   IF (dowhich EQ 'simple') THEN BEGIN 
      IF (kzsimpfix EQ 'yes') THEN lparstep(nt_kz:nt_kz+nt_kz-1) = 0.
      IF (nusimpfix EQ 'yes') THEN lparstep(0:nt_kz-1) = 0.
   ENDIF
   lparstep(nt_kz+nt_kz) = 1.0
   IF (tparsRin(0) GT 0) THEN BEGIN 
      ltpars = dblarr(n_elements(tpars)) + alog10(200)
      ltparsw = dblarr(n_elements(tpars)) + alog10(200)
      ltparstep = 1.0
      ltparswstep = 1.0
   ENDIF
ENDIF

;Output data files:
outfilemet = basename+'.dat'
outfiledat = basename+'.txt'
outfileprofkz = basename+'.profkz'

;Write the key data parameters to a corresponding file:
openw,12,outfiledat
printf,12,'Number of terms & iterations:'
printf,12,nt_kz,nt_kz,niter
printf,12,'Run parameters [gprior, cprior, bprior, lbprior]:'
printf,12,gprior,cprior,bprior,lbtol
close,12
arraydump,outfileprofkz,[[zp_kz]],1


;*************************************************************
;METROPOLIS
IF (zcorrect EQ 'no') THEN BEGIN 
   zshift = double(0)
   zshiftt = double(0)
ENDIF
IF (uselike EQ 'yes') THEN $
   prob = -1d300 $
ELSE prob = 1d300               ;Initial log likeli. [small]
n = 0L                          ;Counters
ini = 0L                        ;
inimax = 5000L                  ;
initphase = 'start'             ;Initialisation phase flag
rejcount = 0.                   ;Rejection count
acccount = 0.                   ;Acceptance count
accrejtollow = 0.24             ;Acceptance/rejection rate
accrejtolhigh = 0.26            ;
endgame = 'no'                  ;Ending flag

;z-array for plots:
zplmin = min(abs(z_dat))
zplmax = max(abs(z_dat))
zpnts = 50
zpl = dindgen(zpnts) * (zplmax-zplmin)/double(zpnts-1) + zplmin

WHILE (n LT niter-1) DO BEGIN
   ;Store the old parameters:
   IF (initphase EQ 'over') THEN BEGIN
      metarray(0:npars-1,n) = pars
      metarray(npars,n) = prob
   ENDIF 
   
   IF (tparsRin(0) GT 0) THEN BEGIN 
      mettpars(0:ntpars-1,n) = tpars
      mettpars(ntpars:ntpars+ntparsR-1,n) = tparsR
   ENDIF
   
AGAIN:
   ;Wiggle the parameters -> new parameters:
   IF (logprior EQ 'no') THEN BEGIN 
      ranarr = 2.0 * (0.5 - randomu(seed,/DOUBLE,npars))
      parst = pars + ranarr * parstep
   ENDIF ELSE BEGIN 
      ranarr = 2.0 * (0.5 - randomu(seed,/DOUBLE,npars))
      lparst = lpars + ranarr * lparstep
      parst = double(10)^lparst

      ;Extract parameters: 
      kzpars = parst(nt_kz:nt_kz+nt_kz-1) 
      kzparsu = abs(kzpars)
      denarr = dblarr(n_elements(kzparsu))
      denarr(0) = kzparsu(0)
      FOR i=1L,n_elements(kzparsu)-1 DO $
         denarr(i) = denarr(i-1) + kzparsu(i)
      denarr = reverse(denarr)
      nupars = parst(0:nt_kz-1) 

      IF (monotonic EQ 'no') THEN BEGIN 
         ;W.o.l.o.g. can fix norm:
         ;nupars(0) = 1.0
         ;parst(0) = 1.0
      ENDIF ELSE BEGIN 
         nupars = nupars / total(nupars) 
         parst(0:nt_kz-1) = nupars
      ENDELSE

      ;Kzmin/max and numin/max limiters: 
      FOR jj=0L,nt_kz-1 DO BEGIN
         IF (kzparsu(jj) LT kzminarr(jj)/100.) THEN GOTO,AGAIN
         IF (denarr(jj) LT kzminarr(jj)) THEN GOTO,AGAIN
         IF (denarr(jj) GT kzmaxarr(jj)) THEN GOTO,AGAIN
         IF (monotonic EQ 'yes') THEN BEGIN 
            nuparsu = dblarr(n_elements(nupars))
            nuparsu(0) = nupars(0)
            FOR kk=1L,n_elements(nuparsu)-1 DO $
               nuparsu(kk) = nuparsu(kk-1) + nupars(kk)
            nuparsu = reverse(nuparsu)
         ENDIF ELSE nuparsu = nupars
         IF (nuparsu(jj) LT numin) THEN GOTO,AGAIN
         IF (nuparsu(jj) GT numax) THEN GOTO,AGAIN
      ENDFOR
   ENDELSE
   
   ;Const-dm prior:
   IF (constdm EQ 'yes') THEN BEGIN
      parst(nt_kz+1:nt_kz+nt_kz-1) = 0.
      kzpars = parst(nt_kz:nt_kz+nt_kz-1)
   ENDIF

   ;Regularisation priors: 
   IF (rprior EQ 'yes') THEN BEGIN 
      FOR jj=1L,nt_kz-1 DO $
         IF (abs(nupars(jj) - nupars(jj-1))/nupars(jj) GT nutol) $
         THEN GOTO,AGAIN
   ENDIF 
   IF (kprior EQ 'yes') THEN BEGIN
      FOR jj=1L,nt_kz-1 DO $
         IF (abs(denarr(jj) - denarr(jj-1))/denarr(jj) GT ktol) $
         THEN GOTO,AGAIN
   ENDIF

   ;Lbprior 
   IF (lbprior EQ 'yes') THEN BEGIN
      jj = nt_kz-2
      totmlastb = total(kzpars(0:jj) + blow(0:jj))
      lastb = kzpars(jj+1) + blow(jj+1)
      IF (lastb / totmlastb GT lbtol) THEN GOTO,AGAIN
   ENDIF

   ;Ensure positivity --> monotinicity constraint:
   IF (mirror EQ 'no') THEN $
      FOR jj=0L,npars-1 DO $
         IF (parst(jj) LT 0.) THEN GOTO,AGAIN

   ;Extract parameters:
   nupars = parst(0:nt_kz-1)
   kzpars = parst(nt_kz:nt_kz+nt_kz-1)
   norm1 = parst(nt_kz+nt_kz)
   
   ;Apply "cprior" and "gprior" on kz function:
   IF (cpriorconv GT 0) THEN BEGIN
      IF (abs(kzpars(0)) GT cpriorconv) THEN GOTO,AGAIN
   ENDIF ELSE BEGIN 
      kzpars(0) = kzminarr(0)
      parst(nt_kz) = kzminarr(0)
   ENDELSE

   FOR jj=0L,nt_kz-1 DO $
      IF (abs(kzpars(jj)) GT gpriorconv) THEN BEGIN
      GOTO,AGAIN
   ENDIF
   
AGAINT:
   ;Wiggle tilt parameters [if needed]:
   IF (tparsRin(0) GT 0) THEN BEGIN 
      IF (logprior EQ 'no') THEN BEGIN
         ranarr = 2.0 * (0.5 - randomu(seed,/DOUBLE,ntpars))
         tparst = tpars + ranarr * tparstep
         ranarr = 2.0 * (0.5 - randomu(seed,/DOUBLE,ntpars))
         tparswt = tparsw + ranarr * tparswstep
      ENDIF ELSE BEGIN
         ranarr = 2.0 * (0.5 - randomu(seed,/DOUBLE,ntpars))
         ltparst = ltpars + ranarr * ltparstep
         tparst = double(10)^ltparst
         ranarr = 2.0 * (0.5 - randomu(seed,/DOUBLE,ntpars))
         ltparswt = ltparsw + ranarr * ltparswstep
         tparswt = double(10)^ltparswt
      ENDELSE

      IF (mirror EQ 'no') THEN BEGIN 
         FOR jj=0L,ntpars-1 DO $
            IF (tparst(jj) LT 0.) THEN GOTO,AGAINT
         FOR jj=0L,ntpars-1 DO $
            IF (tparswt(jj) LT 0.) THEN GOTO,AGAINT
      ENDIF
   ENDIF

   ;Additional tilt pars here for radial dependence: 
   IF (tparsRin(0) GT 0) THEN BEGIN
AGAINTR:
      rant = 2.0 * (0.5 - randomu(seed,/DOUBLE,ntparsR))
      tparsRt = tparsR + rant * tparsRerr

      FOR jj=0L,ntparsR-1 DO $
         IF (tparsRt(jj) LT tparsRin(jj) - tparsRerr(jj)) OR $
         (tparsRt(jj) GT (tparsRin(jj) + tparsRerr(jj))) THEN GOTO,AGAINTR
   ENDIF

   ;Vzmean/zmean correction: 
   IF (vcorrect EQ 'yes') THEN BEGIN 
      rant = 2.0 * (0.5 - randomu(seed,/DOUBLE,nt_kz))
      vmparst = vmpars + rant * vmparstep
   ENDIF
   IF (zcorrect EQ 'yes') THEN BEGIN
      rant = 2.0 * (0.5 - randomu(seed,/DOUBLE))
      zshiftt = zshiftt + rant * zshiftstep
   ENDIF

   ;Calculate theoretical values: 
   nu_z = nu(abs(z_dat - zshiftt),zp_kz,nupars,quadratic,monotonic)
   sig_z = sigma_z(abs(z_dat - zshiftt),zp_kz,$
                   kzpars,blow,nupars,norm1,tparst,tparsRt,quadratic,monotonic)
   kz_z = kz(abs(z_dat - zshiftt),zp_kz,$
             kzpars,blow,quadratic)

   ;Reject models with NaN sig_z: 
   IF (logprior EQ 'yes') THEN BEGIN 
      IF (max(sig_z) NE max(sig_z)) THEN GOTO, AGAIN 
      small = min(sig_z(where(sig_z GT 0)))
      FOR jj=0L,n_elements(sig_z)-1 DO $
         IF (sig_z(jj) NE sig_z(jj)) THEN sig_z(jj) = small
   ENDIF ELSE BEGIN
      ;Another problem with linear sampling (best avoided). 
      ;If I do the "right" thing here and reject NaN models, 
      ;the MCMC gets stuck. So we set sig_z = 0 where it
      ;is NaN and assume that this will be penalised by the 
      ;data. This assumption appears to be very good, 
      ;but still it's not ideal ): 
      small = min(sig_z(where(sig_z GT 0)))
      FOR jj=0L,n_elements(sig_z)-1 DO $
         IF (sig_z(jj) NE sig_z(jj)) THEN sig_z(jj) = small
   ENDELSE

   ;S-prior: ensure sigma_z(z) rises: 
   IF (sprior EQ 'yes') THEN BEGIN 
      FOR jj=1L,n_elements(sig_z)-1 DO $
         IF (sig_z(jj) LT sig_z(jj-1)) THEN BEGIN 
         GOTO,AGAIN
      ENDIF
   ENDIF

   IF (tparsRin(0) GT 0) THEN $
      sig_Rz = sigma_rz(abs(z_dat),zp_kz,tparst)

   IF (vcorrect EQ 'yes') THEN $
      vz_mean = vzmean(abs(z_dat),zp_kz,vmparst) $
   ELSE vz_mean = dblarr(n_elements(z_dat))

   ;Calculate likelihood:
   IF (uselike EQ 'yes') THEN BEGIN
      ;Errors:
      IF (adderrors EQ 'yes') THEN BEGIN
         ;Solve error convolution:
GOTO,SKIPCONVOL 
         prob_z = dblarr(n_elements(z_dat))
         FOR jj=0L,n_elements(z_dat)-1 DO BEGIN 
            zintmin = -abs(z_dat_err(jj))*3.0
            zintmax = abs(z_dat_err(jj))*3.0
            zintpnts = 25
            zint = dindgen(zintpnts) * (zintmax-zintmin)/double(zintpnts-1) + $
                   zintmin + z_dat(jj)
            perr_z = errorz(z_dat(jj) - zint, z_dat_err(jj))
            nu_int = nu(abs(zint),zp_kz,nupars,quadratic,monotonic)
            p_z = nu_int
            prob_z(jj) = int_tabulated(zint, perr_z * p_z)
            IF (prob_z(jj) LT 0) THEN BEGIN 
               print,'Ooops a negative probability! Something is wrong ... stopping.'
               stop
            ENDIF
         ENDFOR
SKIPCONVOL:
         nu_pz = nu(abs(z_dat),zp_kz,nupars,quadratic,monotonic)
         prob_z = nu_pz

         ;FOR TESTING! 
         ;test = nu_z
         ;plot,z_dat,test,psym=3
         ;oplot,z_dat,prob_z,color=2,psym=3
         ;stop

         sig_sum = sqrt(sig_z^2. + vz_dat_err^2.)
         aprob_sigz = alog(1.0/(sqrt(2.0*!PI) * sig_sum)) - (vz_dat-vz_mean)^2./2./sig_sum^2.

         ;*** WARNING *** TILT with errors not yet supported ... ! 
         prob_tilt = 1.0
      ENDIF ELSE BEGIN
         ;Calcualte likelihood [N.B. Log[Li] can be +ve!]:
         prob_z = nu_z
         aprob_sigz = alog(1.0/(sqrt(2.0*!PI) * sig_z)) - (vz_dat-vz_mean)^2./2./sig_z^2.

         IF (tparsRin(0) GT 0) THEN BEGIN
            wid_Rz = sigma_rz(abs(z_dat),zp_kz,tparswt)
            prob_tilt = 1.0/!PI/wid_Rz * BESELK(abs(vz_dat*vR_dat-sig_Rz)/wid_Rz,0)
         ENDIF ELSE prob_tilt = 1.0
      ENDELSE 

      prob_t = total(alog(prob_z) + aprob_sigz + alog(prob_tilt))
      IF (prob_t NE prob_t) THEN BEGIN
         print,'Ooops prob_t is NaN ... ', prob_t
         stop
      ENDIF 

      ;Calculate the likelihood ratio:
      fnewoverf = EXP(prob_t - prob)
   ENDIF ELSE BEGIN 
      ;Normalise nu at min_z [integrate model over bins?]: 
      nu_z = nu_z / max(nu_z)
      prob_t = total((nu_z - nu_dat)^2./nu_dat_err^2.) + $
               total((sig_z - sig_dat)^2./sig_dat_err^2.)

      IF (tparsRin(0) GT 0) THEN BEGIN
         sig_Rz = sigma_rz(z_dat,zp_kz,tparst)
         prob_t = prob_t + $
                  total((sig_Rz - sigRz_dat)^2./sigRz_dat_err^2.)
      ENDIF
      fnewoverf = EXP(prob/2.0-prob_t/2.0)
   ENDELSE 
    
   ;Accept the new f-function?
   ran = randomu(seed,/DOUBLE)

   IF (ran LT fnewoverf) THEN BEGIN
      acccount = acccount + 1.
      pars = parst
      prob = prob_t
      IF (logprior EQ 'yes') THEN lpars = lparst
      
      IF (tparsRin(0) GT 0) THEN BEGIN 
         tpars = tparst
         tparsR = tparsRt
         tparsw = tparswt
         IF (logprior EQ 'yes') THEN BEGIN 
            ltpars = ltparst
            ltparsw = ltparswt
         ENDIF
      ENDIF
      
      IF (vcorrect EQ 'yes') THEN BEGIN 
         vmpars = vmparst
      ENDIF
      IF (zcorrect EQ 'yes') THEN BEGIN
         zshift = zshiftt
      ENDIF

      IF (testplot EQ 'yes') THEN BEGIN
         ;Calculate profiles: 
         nu_zpl = nu(zpl,zp_kz,nupars,quadratic,monotonic)
         sig_zpl = sigma_z(zpl,zp_kz,$
                           kzpars,blow,nupars,norm1,tparst,tparsRt,quadratic,monotonic)
         kz_zpl = kz(zpl,zp_kz,$
                     kzpars,blow,quadratic)
         
         ;Convert kz_z to Sigma in Msun / pc^2:
         Msigma_zpl = abs(kz_zpl) / (2.*!PI*G1)
         Msigma_zpl = Msigma_zpl / 1000.^2.

         ;Do the plots: 
         plot,zpl,nu_zpl/max(nu_zpl),/ylog,yrange=[numin,numax],xrange=[0.,zplmax],$
              title='!6',xtitle='z(kpc)',ytitle='nu [units]'

         zdp = z_dat_bin(where(z_dat_bin GT 0))
         ndp = nu_dat_bin(where(z_dat_bin GT 0))
         ndpe = nu_dat_err_bin(where(z_dat_bin GT 0))
         mnorm = max(ndp)
         ndp = ndp / mnorm
         ndpe = ndpe / mnorm

         oploterror,zdp,ndp,ndpe,color=4,errcol=4
         IF (dowhich EQ 'simple') THEN oplot,zth,nu_zth,color=2

         plot,zpl,sig_zpl,xrange=[0,zplmax],yrange=[0,55],$
              title='!6',xtitle='z(kpc)',ytitle='sigma_z [km/s]'

         sdp = sig_dat_bin(where(z_dat_bin GT 0))
         sdpe = sig_dat_err_bin(where(z_dat_bin GT 0))
  
         oploterror,zdp,sdp,sdpe,color=4,errcol=4
         IF (dowhich EQ 'simple') THEN oplot,zstar,sigzstar,color=2,psym=3

         plot,zpl,Msigma_zpl,title='!6',xtitle='z(kpc)',$
              ytitle='Sigma_z [Msun/pc^2]',yrange=[0,80],xrange=[0,zplmax]
         IF (dowhich NE 'simple') THEN BEGIN 
            oploterror,zvis,sigusevis,siguseviserr,color=2,errcol=2
            oploterror,zsurf,sigdm_surf,sigdm_surferr,color=3,errcol=3
            oploterror,zsurf,sigdm_surf/2.,sigdm_surferr,color=3,errcol=3,linestyle=1
            oplot,zsurf,sigs_surf+sigdm_surf,color=4
            oplot,zsurf,sigs_surf+sigdm_surf/2.,color=4,linestyle=1
         ENDIF ELSE BEGIN
            ;Overplot theory curve: 
            oplot,zth,abs(Kz_zth) / (2.*!PI*G1) / 1000^2.,color=4
            IF (bprior EQ 'yes') THEN oplot,zvis,sigusevis,color=2
         ENDELSE 

         ;Tilt:
         IF (tparsRin(0) GT 0) THEN BEGIN 
            sig_Rz = sigma_rz(zpl,zp_kz,tpars)
            plot,zpl,sig_Rz,title='!6',xtitle='z(kpc)',ytitle='Sig_Rz',$
                 yrange=[-200,200]
            oploterror,z_dat_bin,sigRz_dat_bin,sigRz_dat_err_bin,$
                       color=4,errcol=4
         ENDIF ELSE BEGIN
            IF (vcorrect EQ 'yes') THEN BEGIN 
               vz_mean = vzmean(zpl,zp_kz,vmpars)
               plot,zpl,vz_mean,title='!6',$
                    xtitle='z(kpc)',ytitle='<v_z>(km/s)',$
                    yrange=[-10,10]
            ENDIF ELSE BEGIN 
               ;Dark matter density here: 
               kzparsu = abs(kzpars) 
               denarr = dblarr(n_elements(kzparsu))
               denarr(0) = kzparsu(0)
               FOR i=1L,n_elements(kzparsu)-1 DO $
                  denarr(i) = denarr(i-1) + kzparsu(i)
               denarr = reverse(denarr)

               plot,zp_kz,denarr / (4.0*!PI*G1) / 1000^3.,$
                    yrange = [0,0.03], xtitle='z(kpc)', ytitle='!7q!6!ddm!n [Msun pc!u-3!n]', $
                    title='!6'

               IF (dowhich EQ 'simple') THEN BEGIN 
                  ;Overplot theory curve: 
                  Kz_zthd = -2.0 * F * zth
                  IF (adddarkdisc EQ 'yes') THEN $
                     Kz_zthd = Kz_zthd - KD*zth/sqrt(zth^2.+DD^2.)
                  Sigz_zth = abs(Kz_zthd) / (2.0*!PI*G1) / 1000^2. 
                  denth = deriv(zth,Sigz_zth) / 1000.
                  oplot,zth,denth,color=4
               ENDIF 
            ENDELSE 
         ENDELSE 
      ENDIF
         
      ;Screen output: 
      IF (logprior EQ 'no') THEN stepout = parstep(nt_kz-1) $
      ELSE stepout = lparstep(nt_kz-1)
      print,n,prob,stepout,acccount/rejcount,ini,zshift
      
      ;Decide whether to end initphase:
      ini = ini + 1
      IF (endgame EQ 'yes') THEN BEGIN
         IF (initphase NE 'over') THEN BEGIN 
            print,''
            print,'********** Initialisation phase over **********'
            print,'Step size chosen:'
            IF (logprior EQ 'no' ) THEN BEGIN
               print,parstep
               print,pars
            ENDIF ELSE BEGIN
               print,lparstep
               print,lpars
               print,pars
            ENDELSE
            print,''
         ENDIF
         initphase = 'over'
      ENDIF
   ENDIF ELSE BEGIN 
      ;Rejected
      rejcount = rejcount + 1.
   ENDELSE 

   ;Adapt stepsize during initialisation phase: 
   IF (initphase EQ 'start') THEN BEGIN
      IF (acccount GT 0) AND (rejcount GT 0) THEN BEGIN 
         IF (acccount/rejcount LT accrejtollow) THEN BEGIN 
            parstep = parstep / 1.01
            IF (logprior EQ 'yes') THEN lparstep = lparstep / 1.01
            IF (tparsRin(0) GT 0) THEN BEGIN
               tparstep = tparstep / 1.01
               tparswstep = tparswstep / 1.01
               IF (logprior EQ 'yes') THEN BEGIN 
                  ltparstep = ltparstep / 1.01
                  ltparswstep = ltparswstep / 1.01
               ENDIF
            ENDIF

            IF (vcorrect EQ 'yes') THEN $
               vmparstep = vmparstep / 1.01
            IF (zcorrect EQ 'yes') THEN $
               zshiftstep = zshiftstep / 1.01
         ENDIF 
         IF (acccount/rejcount GT accrejtolhigh) THEN BEGIN
            parstep = parstep * 1.01
            IF (logprior EQ 'yes') THEN lparstep = lparstep * 1.01

            IF (tparsRin(0) GT 0) THEN BEGIN
               tparstep = tparstep * 1.01
               tparswstep = tparswstep * 1.01
               IF (logprior EQ 'yes') THEN BEGIN 
                  ltparstep = ltparstep * 1.01
                  ltparswstep = ltparswstep * 1.01
               ENDIF
            ENDIF

            IF (vcorrect EQ 'yes') THEN $ 
               vmparstep = vmparstep * 1.01
            IF (zcorrect EQ 'yes') THEN $
               zshiftstep = zshiftstep * 1.01
         ENDIF
      ENDIF

      ;Work out when to end initphase:
      IF (ini GT inimax) THEN endgame = 'yes'
   ENDIF

   ;Update the counter:
   IF (initphase EQ 'over') THEN n = n + 1
ENDWHILE

;Write the data to a file:
openw,1,outfilemet
writeu,1,LONG(npars),LONG(niter)
writeu,1,metarray
close,1

IF (tparsRin(0) GT 0) THEN BEGIN
   openw,1,outfilemet+'_tpars'
   writeu,1,LONG(n_elements(tpars)),LONG(niter)
   writeu,1,mettpars
   close,1
ENDIF

print,'Finished!'

;Close the output file, set the plotting back to the screen and exit.
IF (devtype EQ 'PS') THEN device,/close	
set_plot, 'X'
!P.FONT=-1
!P.multi=0

END
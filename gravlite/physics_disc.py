#!/usr/bin/env python3

##
# @file
# calculations for velocity dispersion

# (c) 2013 Pascal Steger, psteger@phys.ethz.ch

import pdb
import numpy as np
import scipy
import scipy.integrate
from scipy.integrate import simps,trapz
#import gl_plot as gpl
import gl_params as gp
import gl_helper as gh




## Set up regularly spaced r0 array for integration:
# @param z_in array of unsorted z values
def get_zarrays(z_in):
    pnts = gp.nipol; zmin = min(z_in); zmax = max(z_in);
    dz = (zmax-zmin)/(pnts-1.); z0 = np.arange(pnts)*dz+zmin
    z_outer     = zmax+z0-zmin
    z_tot       = np.hstack((z0[:-1], z_outer))  # [1:] all but first, [:-1] all but last
    return z0,z_tot,zmin,zmax,dz,z_outer



## General function to describe the density profile
# @param z array of z values above the plane
# @param M corresponding enclosed mass
def calculate_dens(z,M):                  # [TODO], [TODO]
    z0 = np.hstack([0,z])
    deltaM = [];
    deltaM.append(M[0])
    for i in range(1,len(z)):
        deltaM.append(M[i]-M[i-1])
    
    dens=[];  deltavol=[]
    for i in range(len(z)):
        deltavol.append( z0[i+1]-z0[i] )   # TODO: 1D is right
        dens.append( deltaM[i]/deltavol[i] )
    return np.array(dens)


## return delta as delta_i = delta(r_i)
def delta(dpars):
    # other possibility: calculate cumulative sum for representation of delta
    return dpars


## calculate density from parameters
# @param denspars internal representation of the density profile
def densdefault(denspars):
    return dens(gp.xipol, denspars)



## calculate vertical force from Kz
# @param xipol height above midplane
# @param Kz TODO
def kappa(xipol, Kz):
    r0 = xipol
    kzpars = -np.hstack([Kz[0]/r0[0], (Kz[1:]-Kz[:-1])/(r0[1:]-r0[:-1])])
    return kzpars



## take denspars (as polynomial?) coefficients, calculate polynomial, give back Kz
# @param xipol array height above midplane
# @param denspars internal representation of density
def dens(xipol, denspars):              # [pc], [TODO]
    r0 = np.hstack([0,xipol])
    if gp.checkint:
        return gp.ipol.densdat          # [TODO] in disc case
    if not gp.poly:
        if gp.denslog:
            return -np.cumsum((r0[1:]-r0[:-1])*10.**denspars) # TODO: sign
        else:
            return -np.cumsum((r0[1:]-r0[:-1])*denspars) # [TODO]

    else:
        scale = gp.scaledens*max(xipol)     # [pc]
        tmp = np.zeros(len(xipol))
        for i in range(0,len(denspars)):
            tmp += denspars[i]*((scale-xipol)/scale)**i # [log10(msun/pc^3)]
            # gpl.plot(gp.ipol.densr,gp.ipol.densdat); gpl.plot(gp.xipol,10.**tmp); gpl.yscale('log')
    
        dout = 10.**tmp if gp.denslog else tmp            # [Msun/pc^3]

    gh.checknan(dout)
    return dout                 # [msun/pc^3]





## General function to describe the density profile.
# @param nupars array of internal tracer density representation
def nu(nupars):                 # [(log10) Msun/pc^3]
    if gp.nulog:
        nuout = np.power(10.0, nupars) # [Msun/pc^3]
    else:
        nuout = nupars[:]       # [Musn/pc^3]

    gh.checknan(nuout)
    #nuout = nuout/max(nuout)                # [Msun/pc^3], normalized to 1 here
    return nuout/max(nuout)






## Fully non-parametric monotonic *decreasing* function [c.f. Kz function].
# Note, here we explicitly avoid rnuz_z(0) = 0 since this would correspond
# to a constraint rnu_z(zmax) = 0 which is only true if zmax = infty.
# @param z array of z values above plane
# @param zpars
# @param pars
def nu_decrease(z, zpars, pars):
    parsu = abs(pars)                   #     # Mirror prior
    
    if gp.monotonic:
        rnuz_z = np.zeros(len(zpars))
        rnuz_z[0] = parsu[0]
        for i in range(1,len(rnuz_z)):
            rnuz_z[i] = rnuz_z[i-1] + parsu[i]
        fun = rnuz_z[::-1]
    else:
        # Alternative here --> don't assume monotonic!
        fun = parsu
    
    # Normalise: 
    if not gp.quadratic:
        # Exact linear interpolation integral: 
        norm_nu = 0.
        for i in range(len(zpars)-1):
            zl = zpars[i]; zr = zpars[i+1]; zz = zr-zl
            b = fun[i]; a = fun[i+1]; norm_nu = norm_nu + (a-b)/2./zz*(zr**2.-zl**2.) + b*zr - a*zl
    else:
        if gp.qtest:
            gpl.plot(zpars, pars)    
            test = gh.ipol(zpars,pars,z)
            gpl.plot(z,test,psym=3,color=2)
        
        # Exact quadratic interpolation:
        norm_nu = 0.
        for i in range(1,len(zpars)-1):
            z0 = zpars[i-1]; z1 = zpars[i]; z2 = zpars[i+1]
            f0 = fun[i-1];   f1 = fun[i];   f2 = fun[i+1]
            h = z2-z1
            a = f0; b = (f1-a)/h; c = (f2-2.*b*h-a)/2./h**2. 
            z1d = z1-z0; z2d = z1**2.-z0**2.; z3d = z1**3.-z0**3.
            
            if i == len(zpars)-2:
                # Last bin integrate from z0 --> z2: 
                z1d = z2-z0; z2d = z2**2.-z0**2.; z3d = z2**3.-z0**3.
            
            intquad = (a - b*z0 + c*z0*z1)*z1d + (b/2. - c/2.*(z0+z1))*z2d + c/3.*z3d
            norm_nu = norm_nu + intquad
            
            if gp.qtest:
                print i, h, intquad
                testy = a + b*(z-z0) + c*(z-z0)*(z-z1)
                if i != len(zpars)-3:
                    sel = (z > z0 and z < z1)
                    zcut = z[sel]
                    tcut = testy[sel]
            else:
                sel  = (z > z0 and z < z2)
                zcut = z[sel]; tcut = testy[sel]

        if gp.qtest:
            gpl.plot(zcut,tcut,psym=3,color=4)
            print 'qtest: will stop'
            print simps(test,z), norm_nu 
            exit(1)
            
    fun /= norm_nu

    # Interpolate to input z:
    if not gp.quadratic:
        f = gh.ipol(zpars,fun,z)
    else:
        f = gh.ipol(zpars,fun,z)        # TODO: assure quadratic interpolation
    
    # Check for negative density:
    sel = (f>0)
    small = min(f[sel])
    for jj in range(len(f)):
        if (f[jj] < 0):
            f[jj] = small
    return f







## General function to calculate the Kz force law:
# Non-parametric Kz function here. Use cumulative integral to
# ensure monotinicity in an efficient manner. Note here we
# use kz_z(0) = kzpars(0) * dz so that it can be zero, or
# otherwise just small in the case of large bins. This latter
# avoids the interpolated kz_out[0] going negative for coarse 
# binning.
# @param z_in TODO
# @param zpars TODO
# @param kzpars TODO
# @param blow TODO
def kz(z_in, zpars, kzpars, blow):
    # Mirror prior # TODO: baryon minimum prior [blow]:
    #kzparsu = abs(kzpars)
    
    # Assume here interpolation between dens "grid points", 
    # [linear or quadratic]. The grid points are stored 
    # in kzpars and give the *differential* increase in 
    # dens(z) towards small z [monotonic dens-prior]: 
    #denarr = np.zeros(gp.nipol)
    #denarr[0] = kzparsu[0]
    #for i in range(1,len(kzparsu)):
    #    denarr[i] = denarr[i-1] + kzparsu[i]
    #denarr = denarr[::-1]

    # override previous statements: use dens parameter directly, so denarr is really given by
    denarr = kzpars
    
    # Solve interpolated integral for Kz: 
    if not gp.quadratic:
        # Linear interpolation here: 
        kz_z = np.zeros(gp.nipol)
        for i in range(1,gp.nipol):
            zl = zpars[i-1]; zr = zpars[i]; zz = zr-zl
            b = denarr[i-1]; a = denarr[i]; kz_z[i] = kz_z[i-1]+(a-b)/2./zz*(zr**2.-zl**2.)+b*zr-a*zl
    else:
        # Quadratic interpolation here: 
        kz_z = np.zeros(gp.nipol)
        for i in range(1,gp.nipol-1):
            z0 = zpars[i-1];  z1 = zpars[i];  z2 = zpars[i+1]
            f0 = denarr[i-1]; f1 = denarr[i]; f2 = denarr[i+1]
            h = z2-z1; a = f0; b = (f1-a)/h; c = (f2-2.*b*h-a)/2./h**2.
            z1d = z1-z0; z2d = z1**2.-z0**2.; z3d = z1**3.-z0**3.
            intbit = (a-b*z0+c*z0*z1)*z1d+(b/2.-c/2.*(z0+z1))*z2d+c/3.*z3d
            kz_z[i] = kz_z[i-1] + intbit
            if i == n_elements(zpars)-2:
                # Deal with very last bin:
                z1d = z2-z1; z2d = z2**2.-z1**2.; z3d = z2**3.-z1**3.
                
                intbit = (a - b*z0 + c*z0*z1)*z1d + (b/2. - c/2.*(z0+z1))*z2d + c/3.*z3d
                kz_z[i+1] = kz_z[i] + intbit
    
    if gp.qtest:
        pnts = 5000;  zmin = min(zpars); zmax = max(zpars)
        z = np.arange(pnts)*(zmax-zmin)/(pnts-1.) + zmin
        if not gp.quadratic:
            denarr_z = gh.ipol(zpars,denarr,z) #             # TODO: assure linear interpolation? see IDL help
        else:
            denarr_z = gh.ipol(zpars,denarr,z) #             # TODO: assure only quadratic interpolation
            
        kz_th = np.zeros(pnts)
        for i in range(1,pnts):
            kz_th[i] = simps(denarr_z[:i],z[:i])
        
        if gp.quadratic:
            test = gh.ipol(zpars,kz_z,z) #             # TODO: assure quadratic interpolation
        else:
            test = gh.ipol(zpars,kz_z,z)

        testsimp = np.zeros(len(zpars))
        delta_z = zpars[2] - zpars[1]
        for i in range(1,len(zpars)):
            testsimp[i] = testsimp[i-1] + denarr[i] * delta_z
    
        gpl.plot(z,kz_th);        gpl.plot(zpars,kz_z)
        gpl.plot(z,test);         gpl.plot(zpars,testsimp)
        gpl.show()

    kz_out = kz_z # + blow # let blow alone, take overall Kz
    
    # Then interpolate back to the input array:
    #if not gp.quadratic:
    #    kz_out = gh.ipol(zpars,kz_z,z_in) #         # TODO: assure linear interpolation
    #else:
    #    kz_out = gh.ipol(zpars,kz_z,z_in) #         # TODO: quadratic!
        
    # Error checking. Sometimes when kz_z(0) << kz_z(1), 
    # the interpolant can go negative. This just means that 
    # we have resolved what should be kz_z(0) = 0. A simple
    # fix should suffice: 
    for jj in range(0,len(kz_out)):
        if (kz_out[jj] < 0):
            kz_out[jj] = 0.
        
    return kz_out





## calculate z velocity dispersion
# @param zp TODO
# @param kzpars TODO
# @param nupars TODO
# @param norm TODO
# @param tpars TODO
# @param tparsR TODO
def sigmaz(zp, kzpars, nupars, norm, tpars, tparsR):
    # calculate density and Kz force:
    nu_z = nupars/np.max(nupars)          # normalized to 1
    # kz_z = kz(zp,zp,kzpars,blow,quadratic) # TODO: reenable
    kz_z = kzpars
    
    # add tilt correction [if required]:
    if gp.deltaprior:
        Rsun = tparsR[0];  hr   = tparsR[1];  hsig = tparsR[2]
        tc = sigma_rz(zp,zp,tpars)
        tc = tc * (1.0/Rsun - 1.0/hr - 1.0/hsig)
        # flag when the tilt becomes significant:
        if abs(np.sum(tc))/abs(np.sum(kz_z)) > 0.1:
            print 'Tilt > 10%!',abs(np.sum(tc)),abs(np.sum(kz_z))
        kz_z = kz_z-tc
    
    # do exact integral
    if not gp.quadratic:
        # linear interpolation here: 
        sigint = np.zeros(len(zp))
        for i in range(1,len(zp)):
            zl = zp[i-1];  zr = zp[i];  zz = zr-zl
            b = nu_z[i-1]; a = nu_z[i]; q = kz_z[i-1]; p = kz_z[i]
        
            intbit = (a-b)*(p-q)/(3.0*zz**2.) * (zr**3.-zl**3.) + \
                ((a-b)/(2.0*zz) * (q-(p-q)*zl/zz) + (p-q)/(2.0*zz)  * (b-(a-b)*zl/zz)) * (zr**2.-zl**2.)+\
                (b-(a-b)*zl/zz) * (q-(p-q)*zl/zz) * zz
      
            if i==0:
                sigint[0] = intbit
            else:
                sigint[i] = sigint[i-1] + intbit
    else:
        # quadratic interpolation
        sigint = np.zeros(len(zp))
        for i in range(1,len(zp)-1):
            z0 = zp[i-1];   z1 = zp[i];   z2 = zp[i+1]
            f0 = nu_z[i-1]; f1 = nu_z[i]; f2 = nu_z[i+1]
            fd0 = kz_z[i-1];fd1 = kz_z[i];fd2 = kz_z[i+1]
            h = z2-z1; a = f0; b = (f1-a)/h; c = (f2-2.*b*h-a)/2./h**2.
            ad = fd0; bd = (fd1-ad)/h; cd = (fd2-2.*bd*h-ad)/2./h**2.
            AA = a*bd+ad*b; BB = c*ad+cd*a; CC = b*cd+bd*c
            z1d = z1-z0; z2d = z1**2.-z0**2.; z3d = z1**3.-z0**3.; z4d = z1**4.-z0**4.; z5d = z1**5.-z0**5.
            intbit = z1d * (a*ad - z0*(AA-BB*z1) + z0**2.*(b*bd-CC*z1) + \
                        c*cd*z0**2.*z1**2.) + \
                        z2d * (0.5*(AA-BB*z1)-z0*(b*bd-CC*z1)-z0/2.*BB+z0**2./2.*CC - \
                        (z0*z1**2.+z0**2.*z1)*c*cd)+z3d*(1.0/3.0*(b*bd-CC*z1)+1.0/3.0*BB-2.0/3.0*z0*CC + \
                        1.0/3.0*c*cd*(z1**2.+z0**2.+4.0*z0*z1))+z4d*(1.0/4.0*CC-c*cd/2.0*(z1 + z0)) + \
                        z5d*c*cd/5.

            sigint[i] = sigint[i-1] + intbit
            if i == len(zp)-2:
                # Deal with very last bin: 
                z1d = z2-z1; z2d = z2**2.-z1**2.; z3d = z2**3.-z1**3.; z4d = z2**4.-z1**4.; z5d = z2**5.-z1**5.
                intbit = z1d * (a*ad - z0*(AA-BB*z1) + z0**2.*(b*bd-CC*z1) + \
                         c*cd*z0**2.*z1**2.) + \
                  z2d * (0.5*(AA-BB*z1)-z0*(b*bd-CC*z1) - z0/2.*BB + z0**2./2.*CC - \
                         (z0*z1**2. + z0**2.*z1)*c*cd) + \
                  z3d * (1.0/3.0*(b*bd-CC*z1)+1.0/3.0*BB - 2.0/3.0*z0*CC + \
                         1.0/3.0*c*cd*(z1**2. + z0**2. + 4.0*z0*z1)) + \
                  z4d * (1.0/4.0*CC - c*cd/2.0 * (z1 + z0)) + \
                  z5d * c*cd / 5.

                sigint[i+1] = sigint[i] + intbit

    if gp.qtest:
        nu_z = nupars
        pnts = 5000; zmin = min(zp); zmax = max(zp)
        z = dindgen(pnts)*(zmax-zmin)/double(pnts-1) + zmin 
        #kz_z = kz(z,zp,kzpars,blow)
        
        sigint_th = np.zeros(pnts)
        for i in range(1,pnts):
            sigint_th[i] = simps(Kz_z[:i]*nu_z[:i],z[:i])
        if gp.quadratic:
            # TODO: quadratic
            test = gh.ipol(zp, sigint, z)
        else:
            test = gh.ipol(zp, sigint, z)

        gpl.plot(z,sigint_th)
        gpl.plot(zp,sigint,color=2)
        gpl.plot(z,test,color=4)
        gpl.show()
        
    sig_z_t2 = 1.0/nu_z * (sigint + norm) # TODO: try to fit without..
    
    return  np.sqrt(sig_z_t2)





## General function to describe the tilt profile
# @param z
# @param zpars
# @param tpars
def sigma_rz(z, zpars, tpars):
    #Mirror prior
    tparsu = abs(tpars)
    
    # dz = zpars[2]-zpars[1]
    # sig_Rz = np.zeros(gp.nipol)
    # sig_Rz[0] = tparsu[0] * dz / 2.
    # for i in range(1,gp.nipol):
    #   sig_Rz[i] = sig_Rz[i-1] + tparsu[i] * dz
    # f = gp.ipol(zpars,sig_Rz,z)
    
    # Alternative here --> don't assume monotonic!
    f = gh.ipol(zpars,tparsu,z)
    return f




## function to calculate surface density from Kz parameter
# @param Kz force
def Sigmaz(Kz):
    return abs(Kz)/(2.*np.pi*gp.G1)



## calculate enclosed mass from density parameters
# @param denspars internal representation of the density
def Mzdefault(denspars):
    return Sigmaz(denspars)

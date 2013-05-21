#!/usr/bin/python
# (c) 2013 Pascal S.P. Steger
'''parameters for the MCMC'''

import numpy as np
import numpy.random as npr
import random
import gl_params as gp
import gl_helper as gh
import pdb
if gp.geom == 'sphere':
    import physics_sphere as phys
elif gp.geom == 'disc':
    import physics_disc as phys





class Params:
    'Common base class for all parameter sets'
    # pars = np.array([nupars1,nupars2,denspars,deltapars1,deltapars2,Mslopepars,sigmaslopepars1,sigmaslopepars2])
    # TODO: generalize to include array for nu_i, delta_i, sigsl_i arrays, i=1..Npops
    def __init__ (self, locpop, nu1=None, dens=None, delta1=None, Msl=None, sig1sl=None, norm=None, nu2=None, delta2=None, sig2sl=None):

        if locpop == -2: # set according to values
            self.nu1    = np.zeros(gp.nipol)+nu1
            self.nu2    = np.zeros(gp.nipol)+nu2
            self.dens    = np.zeros(gp.nipol)+dens
            self.delta1  = np.zeros(gp.nipol)+delta1
            self.delta2  = np.zeros(gp.nipol)+delta2
            self.Msl    = np.zeros(1)+Msl
            self.sig1sl = np.zeros(1)+sig1sl
            self.sig2sl = np.zeros(1)+sig2sl
            self.norm   = np.zeros(1)
        if locpop == -1: # set according to values
            self.nu1    = np.zeros(gp.nipol)+nu1
            self.dens    = np.zeros(gp.nipol)+dens
            self.delta1  = np.zeros(gp.nipol)+delta1
            self.Msl    = np.zeros(1)+Msl
            self.sig1sl = np.zeros(1)+sig1sl
            self.norm   = np.zeros(1)
        elif locpop==0: # set all to -1 or 0
            self.nu1    = np.zeros(gp.nipol)
            self.nu2    = np.zeros(gp.nipol)
            self.dens    = np.zeros(gp.nipol)
            self.delta1  = np.zeros(gp.nipol)
            self.delta2  = np.zeros(gp.nipol)
            self.Msl    = np.zeros(1)
            self.sig1sl = np.zeros(1)
            self.sig2sl = np.zeros(1)
            self.norm   = np.zeros(1)
        elif locpop == 1: # fill with values for one population only
            self.nu1    = nu1
            self.dens    = dens
            self.delta1  = delta1
            self.Msl    = np.zeros(1)+Msl
            self.sig1sl = np.zeros(1)+sig1sl
            self.norm   = np.zeros(1)+norm
        elif locpop==2:   # fill with values for two populations
            self.nu1    = nu1
            self.nu2    = nu2
            self.dens    = dens
            self.delta1  = delta1
            self.delta2  = delta2
            self.Msl    = np.zeros(1)+Msl
            self.sig1sl = np.zeros(1)+sig1sl
            self.sig2sl = np.zeros(1)+sig2sl
            self.norm   = np.zeros(1)
            
    def setuniformrandom(self):
        self.nu1    = npr.uniform(-1,1,gp.nipol)
        self.dens    = npr.uniform(-1,1,gp.nipol)
        self.delta1  = npr.uniform(-1,1,gp.nipol)
        self.Msl    = npr.uniform(-1,1,1)
        self.sig1sl = npr.uniform(-1,1,1)
        self.norm   = npr.uniform(-1,1,1)
        if gp.pops==2:
            self.nu2    = npr.uniform(-1,1,gp.nipol)
            self.delta2  = npr.uniform(-1,1,gp.nipol)
            self.sig2sl = npr.uniform(-1,1,1)

        return self

    def wiggle_nu1(self):
        self.nu1 = npr.uniform(-1, 1, gp.nipol)
        return self

    def wiggle_nu2(self):
        self.nu2 = npr.uniform(-1, 1, gp.nipol)
        return self
    
    def wiggle_nu(self):
        self.wiggle_nu1()
        if gp.pops==2:
            self.wiggle_nu2()
        return self
 
    def wiggle_dens(self):
        if gp.constdens:
            self.dens = np.zeros(gp.nipol) + npr.uniform(-1,1)
        else:
            self.dens = npr.uniform(-1, 1, gp.nipol)
        self.Msl = npr.uniform(-1, 1)
        return self
    
    def wiggle_delta(self):
        self.delta1 = npr.uniform(-1,1,gp.nipol)
        if gp.pops ==2:
            self.delta2 = npr.uniform(-1,1,gp.nipol)
        return self

    def wiggle_tilt(self):
        # Wiggle tilt parameters [if needed]:
        # rant = 2.0 * (0.5 - randomu(seed,/DOUBLE,ntparsR))
        # tparsRt = tparsR + rant * tparsRerr
        self.tilt = npr.uniform(-1,1,gp.nipol)
        return self


    def wigglebin(self,p=0):
        self.nu1[p]   = npr.uniform(-1,1)
        self.dens[p]   = npr.uniform(-1,1)
        self.delta1[p] = npr.uniform(-1,1)
        if gp.pops==2:
            self.nu2[p]   = npr.uniform(-1,1)
            self.delta2[p] = npr.uniform(-1,1)
        return self

    def wiggleslopes(self):
        self.sig1sl = npr.uniform(-1,1)
        self.norm   = npr.uniform(-1,1)
        if gp.pops==2:
            self.sig2sl[p] = npr.uniform(-1,1)
        return self

    def dot(self,nr):
        self.nu1    *= nr;        self.dens    *= nr;        self.delta1  *= nr
        self.Msl    *= nr;        self.sig1sl *= nr;         self.norm    *= nr
        if gp.pops == 2:
            self.nu2    *= nr;    self.delta2  *= nr;        self.sig2sl *= nr
        return self

    def divdot(self,nr):
        self.nu1   /= nr;         self.dens   /= nr;         self.delta1 /= nr
        self.Msl   /= nr;         self.sig1sl/= nr;          self.norm   /= nr
        if gp.pops == 2:
            self.nu2   /= nr;     self.delta2 /= nr;         self.sig2sl/= nr
        return self

    def mul(self, pars):
        self.nu1   *= pars.nu1;   self.dens   *= pars.dens;   self.delta1 *= pars.delta1
        self.Msl   *= pars.Msl;   self.sig1sl*= pars.sig1sl;  self.norm   *= pars.norm
        if gp.pops == 2:
            self.nu2 *= pars.nu2; self.delta2 *= pars.delta2; self.sig2sl *= pars.sig2sl
        return self

    def add(self, pars):
        self.nu1    += pars.nu1;  self.dens    += pars.dens;  self.delta1  += pars.delta1
        self.Msl    += pars.Msl;  self.sig1sl += pars.sig1sl; self.norm    += pars.norm
        if gp.pops==2:
            self.nu2 += pars.nu2; self.delta2 += pars.delta2; self.sig2sl += pars.sig2sl
        return self

    def getlog(self):
        if gp.pops==1:
            return Params(gp.pops,\
                          np.log10(self.nu1),\
                          np.log10(self.dens),\
                          self.delta1,\
                          self.Msl, self.sig1sl)

        elif gp.pops==2:
            return Params(gp.pops,\
                          np.log10(self.nu1),\
                          np.log10(self.dens),\
                          self.delta1,\
                          self.Msl, self.sig1sl,\
                          np.log10(self.nu2),\
                          self.delta2,\
                          self.sig2sl)
    def set(self,other):
        self.nu1    = other.nu1
        self.dens    = other.dens
        self.delta1  = other.delta1
        self.Msl    = other.Msl
        self.sig1sl = other.sig1sl
        self.norm   = other.norm
        if gp.pops==2:
            self.nu2    = other.nu2
            self.delta2  = other.delta2
            self.sig2sl = other.sig2sl
        return self

            
    def output(self):
        print >> '  # nu1     = ',gh.pretty(self.nu1)
        print >> '  # dens     = ',gh.pretty(self.dens)
        print >> '  # delta1   = ',gh.pretty(self.delta1)
        print >> '  # Msl     = ',gh.pretty(self.Msl)
        print >> '  # sig1sl  = ',gh.pretty(self.sig1sl)
        print >> '  # norm    = ',gp.pretty(self.norm)
        if gp.pops==2:
            print >> '  # nu2     = ',gh.pretty(self.nu2)
            print >> '  # delta2   = ',gh.pretty(self.delta2)
            print >> '  # sig2sl  = ',gh.pretty(self.sig2sl)
        return
    


    def adaptworst(self,mult):
        if gp.pops == 1:
            if gp.chi2t_nu1 > gp.chi2t_sig1:
                self.nu1 *= mult
            else:
                self.dens *= mult
                self.Msl *= mult
                self.norm *= mult
        if gp.pops==2:
            if gp.chi2t1 > gp.chi2t2:
                if gp.chi2t_nu1 > gp.chi2t_sig1:
                    self.nu1 *= mult
                else:
                    self.dens *= mult
                    self.Msl *= mult
                    self.norm *= mult
            else:
                if gp.chi2t_nu2 > gp.chi2t_sig2:
                    self.nu2 *= mult
                else:
                    self.dens *= mult
                    self.Msl *= mult
                    self.norm *= mult

    def adaptall(self,mult):
        if gp.pops==1:
            self.nu1 *= mult
            self.dens *= mult
            self.Msl *= mult
            self.norm *= mult
        return
                



    def scale_prop_chi2(self):
        if gp.pops == 1:
            # depending on nu parametrization: only
            self.nu1    *= gp.chi2t_nu1/gp.chi2t


            # depending on siglos, to be changed if mainly siglos contributing
            self.Msl    *= gp.chi2t_sig1/gp.chi2t
            self.delta1 *= gp.chi2t_sig1/gp.chi2t
            self.dens   *= gp.chi2t_sig1/gp.chi2t
            
            # for disc only
            self.norm *= 1.
        elif gp.pops == 2:
            # depending on nu parametrization:
            self.nu1    *= np.sqrt(gp.chi2t_nu1/gp.chi2t)
            self.nu2    *= np.sqrt(gp.chi2t_nu2/gp.chi2t)


            # depending on siglos
            self.delta1 *= np.sqrt(gp.chi2t_sig1/gp.chi2t)
            self.delta2 *= np.sqrt(gp.chi2t_sig2/gp.chi2t)
                
            self.Msl    *= np.sqrt(gp.chi2t_sig/gp.chi2t)
            self.dens   *= np.sqrt(gp.chi2t_sig/gp.chi2t)
        return self



    def has_negative(self):
        if min(self.nu1) < 0. and not gp.nulog:
            return True
        if gp.geom=='sphere' and min(phys.dens(gp.xipol,self.dens)<0.):
            return True
        if min(self.Msl<0):
            self.Msl = -self.Msl
            print 'flipped Msl'
        if gp.pops==2:
            if min(self.nu2) < 0. and not gp.nulog:
                return True
        return False
    
    def get_nu(self):
        if gp.pops==1:
            return [self.nu1]
        elif gp.pops==2:
            return [self.nu1, self.nu2]

    def set_nu(self,nus):
        if gp.pops==1:
            self.nu1 = nus[0]
        elif gp.pops==2:
            self.nu1 = nus[0]
            self.nu2 = nus[1]
        return self

    def get_delta(self):
        if gp.pops==1:
            return [self.delta1]
        elif gp.pops==2:
            return [self.delta1, self.delta2]

    def set_delta(self,deltas):
        if gp.pops==1:
            self.delta1 = deltas[0]
        elif gp.pops ==2:
            self.delta1 = deltas[0]
            self.delta2 = deltas[1]
        return self

    def get_sigsl(self):
        if gp.pops==1:
            return [self.sig1sl]
        elif gp.pops ==2:
            return [self.sig1sl, self.sig2sl]

    def set_sigsl(self,sigs):
        if gp.pops == 1:
            self.sig1sl = sigs[0]
        elif gp.pops ==2:
            self.sig1sl = sigs[0]
            self.sig2sl = sigs[1]
        return self

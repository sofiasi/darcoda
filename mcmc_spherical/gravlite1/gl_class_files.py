#!/usr/bin/python2.7
# class to generate all filenames, independent of which investigation is being performed

import gl_params as gp
import gl_helper as gh

if gp.geom == 'sphere':
    import physics_sphere as phys
elif gp.geom == 'disc':
    import physics_disc as phys



    
def get_case(cas):
    # Set number of tracers to look at
    # want to set ntracers1 = 1e3              # case 1
    #             ntracers1 = 1e4              # case 2
    #             ntracers1 = ntracers2 = 5e3  # case 3
    
    ntracers1 = 0; ntracers2 = 0
    if cas == 1:
        ntracers1 = 2000
    elif cas == 2:
        ntracers1 = 10000
    elif cas == 3:
        ntracers1 = 5000
        ntracers2 = 5000
    return ntracers1, ntracers2




    
class Files:
    'Common base class for all filename sets'
    # massfile, nufile[], sigfile[], outname = Files(investigate)


    
    def __init__ (self):
        self.dir = ''
        self.massfile = ''; self.analytic = ''
        self.nufiles  = []
        self.sigfiles = []
        self.posvelfiles = []
        self.set_dir(gp.machine) # 'darkside' or 'local'
        self.ntracer1, self.ntracer2,self.nstr1, self.nstr2 = self.set_ntracers(gp.cas)
        
        if gp.investigate == 'hernquist':
            self.set_hernquist()
        elif gp.investigate == 'walker':
            self.set_walker()
        elif gp.investigate == 'sim':
            self.set_disc_sim()
        elif gp.investigate == 'simple':
            self.set_disc_simple()

        self.outname = self.get_outname()

        if False:
            print >> 'input:'
            if len(self.massfile) > 0:
                print >> self.massfile
                print >> self.nufiles
                print >> self.sigfiles
            else:
                print >> self.posvelfiles

        return




    
    def set_dir(self, machine):
        if machine == 'darkside':
            self.dir = '/home/ast/read/dark/dwarf_data/'
        elif machine == 'local':
            self.dir = '/home/psteger/sci/dwarf_data/'
        return




        
    def set_ntracers(self,cas):
        ntracers1,ntracers2 = get_case(cas)
        self.ntracer1 = ntracers1;   self.ntracer2 = ntracers2
        self.nstr1 = str(ntracers1); self.nstr2 = str(ntracers2)
        return self.ntracer1, self.ntracer2, self.nstr1, self.nstr2



    
    def get_outname(self):
        import datetime
        bname = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if gp.investigate == 'walker':
            bname = bname + '_case_' + str(gp.walkercase)
            ntr1, ntr2  = get_case(gp.cas)
            bname = bname + '_' + str(ntr1) + '_' + str(ntr2)
        if (gp.gprior>0) : bname = bname + '_gprior'
        if (gp.cprior>=0) : bname = bname + '_cprior'
        
        if gp.mirror  : bname = bname + '_mirr'
        if gp.nulog: bname = bname + '_nulog'
        if gp.denslog: bname = bname + '_denslog'
        if gp.lbprior : bname = bname + '_lb'
        
        if gp.deltaprior: bname = bname + '_delta' 
        bname = bname + '_mslope' if (gp.mprior<0) else bname + '_mconst'
        
        if gp.bprior: bname = bname + '_bprior'
        if gp.investigate == 'hernquist':
            bname = bname+'_'+self.nstr1+'_'+self.nstr2+'_'+str(gp.nipol)
        
        if gp.sprior:    bname = bname + '_sprior'
        if gp.uselike:   bname = bname + '_uselike'
        if gp.constdens: bname = bname + '_constdens'
        if gp.adderrors: bname = bname + '_errors'
        if gp.rprior:    bname = bname + '_rprior'
        if gp.quadratic: bname = bname + '_quad'
        if gp.monotonic: bname = bname + '_mono'

        import os; import os.path
        if not os.path.exists(self.dir+bname+"/"):
            os.makedirs(self.dir+bname+"/")
        return bname + "/" + bname



        
    def get_sim_name(self):
        if gp.pops == 1:
            sim = 'unit_hern_1_'
        elif gp.pops == 2:
            sim = 'dual_unit_hern_1_'
        return sim




        
    def set_hernquist(self):
        '''set all filenames for Hernquist case'''
        self.dir = self.dir + 'data_hernquist/'
        sim = self.get_sim_name()
        self.massfile = self.dir+'enclosedmass/'+sim+'enclosedmass.txt'
        if gp.pops == 1:
            if gp.checksigma and gp.cas == 0:
                self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm.txt') # all comp.
                self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm.txt') # first comp.
                self.sigfiles.append(self.dir+'velocitydispersionlos/'+sim+'veldisplos.txt') # all comp.
                self.sigfiles.append(self.dir+'velocitydispersionlos/'+sim+'veldisplos.txt') # first comp.
            else:
                self.nufiles.append(self.dir+'densityfalloff/' +sim+'falloffnotnorm_'+\
                                    self.nstr1+'_'+self.nstr2+'.txt') # all comp.
                self.nufiles.append(self.dir+'densityfalloff/' +sim+'falloffnotnorm_'+\
                                    self.nstr1+'_'+self.nstr2+'.txt') # first comp.
                self.sigfiles.append(self.dir+'/velocitydispersionlos/' +sim+'veldisplos_'\
                                     +self.nstr1+'_'+self.nstr2+'.txt') # all comp.
                self.sigfiles.append(self.dir+'/velocitydispersionlos/' +sim+'veldisplos_'\
                                     +self.nstr1+'_'+self.nstr2+'.txt') # first comp.
                
        elif gp.pops == 2: # before: _*_[1,2].txt
            self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm.txt') # all comp.
            self.nufiles.append(self.dir+'densityfalloff/'\
                                +sim+'falloffnotnorm_'+self.nstr1+'_0.txt')
            self.sigfiles.append(self.dir+'/velocitydispersionlos/' +sim+'veldisplos_'+self.nstr1+'_'+nstr2+'.txt') # all comp.
            self.sigfiles.append(self.dir+'velocitydispersionlos/'\
                                 +sim+'veldisplos_'+self.nstr1+'_0.txt')
            self.nufiles.append(self.dir+'densityfalloff/'\
                                +sim+'falloffnotnorm_0_'+self.nstr2+'.txt')
            self.sigfiles.append(self.dir+'velocitydispersionlos/'\
                                 +sim+'veldisplos_0_'+self.nstr2+'.txt')
        return





        

    def set_walker(self):
        '''derive filenames from Walker&Penarrubia parameters'''
        self.dir = self.dir + 'data_walker/'
        if gp.walkercase == 0:
            gamma_star1 =   0.1;    gamma_star2 =   1.0 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     = 1000.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 0 # 0 or 1

        elif gp.walkercase == 1:
            gamma_star1 =   1.0;    gamma_star2 =   1.0 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     =  500.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 0 # core

        elif gp.walkercase == 2:
            gamma_star1 =   1.0;    gamma_star2 =   1.0 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     =  500.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 1 # cusp

            
        alpha_DM    = 1;    beta_DM     = 3;
        rho0        = 1 # to be read from the corresp. gs*mpc3.dat file
        r_DM        = 1000                    # fixed to 1000pc
        
        AAA = gh.myfill(100*gamma_star1)     #100
        BBB = gh.myfill(10*beta_star1)       #050
        CCC = gh.myfill(r_star1/10)          #100
        DDD = gh.myfill(100*r_a1)            #100
        EEE = {0: "core",
             1: "cusp"
             }[gamma_DM]                 #core
        FFF = gh.myfill(100*gamma_star2)     #010
        GGG = gh.myfill(10*beta_star2)       #050
        HHH = gh.myfill(r_star2/10)          #100
        III = gh.myfill(100*r_a2)            #100
        JJJ = EEE                         #core
        NNN = gh.myfill(3)                   #003    # realization (1..10)
        
        self.dir = self.dir+ "c1_"+AAA+"_"+BBB+"_"+CCC+"_"+DDD+"_"+EEE+"_c2_"+FFF+"_"+GGG+\
                  "_"+HHH+"_"+III+"_"+JJJ+"_"+NNN+"_6d/"

        self.massfile = self.dir+'enclosedmass/enclosedmass_0.txt'
        self.analytic = self.dir+'samplepars'
        print 'analytic set to ',self.analytic
        
        self.nufiles.append(self.dir+'nu/nunotnorm_0.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
        if gp.pops == 1:
            self.nufiles.append(self.dir+'nu/nunotnorm_0.txt') # first and only comp.
            self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
        if gp.pops == 2:
            self.nufiles.append(self.dir+'nu/nunotnorm_1.txt') # first comp.
            self.sigfiles.append(self.dir+'siglos/siglos_1.txt')
            self.nufiles.append(self.dir+'nu/nunotnorm_2.txt') # second comp.
            self.sigfiles.append(self.dir+'siglos/siglos_2.txt')
        self.outname = self.get_outname()
        return
    




    def get_scale_file(self,i):
        # get rcore, dens0, dens0pc, totmass, maxvlos from file par_0.txt
        return self.dir+'scale_'+str(i)+'.txt'


    def get_ntracer_file(self,i):
        return self.dir+'ntracer_'+str(i)+'.txt'



    def set_fornax(self):
        self.dir = self.dir + 'data_dwarf/data_obs/for/'
        return




        
    def set_disc_sim(self):
        self.dir = self.dir + 'data_disc_sim/mwhr/'
        self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_stars.txt') # all components
        self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_stars.txt') # first comp.
        if gp.pops == 2:
            self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_dm.txt') # second comp.

        self.nufiles.append(self.dir + 'nu/mwhr_r8500_ang'+gp.patch+'_falloff.txt') # all comp.
        self.nufiles.append(self.dir + 'nu/mwhr_r8500_ang'+gp.patch+'_falloff.txt') # first comp.
        self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvelbl.txt') # all comp.
        self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvelbl.txt') # first comp.
        
        self.massfile = self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfaceden.txt'
        # self.massfile.append(self.dir + 'siglos/mwhr_r8500_ang'+gp.patch+'_surfacedenDM.txt')
        
        return
    
    def set_disc_simple(self):
        self.dir = self.dir + 'data_disc_simple/'
        return


    def get_outfiles(self):
        outplot = self.dir + self.outname + '.png'
        outdat  = self.dir + self.outname + '.dat'
        outtxt  = self.dir + self.outname + '.txt'
        return outplot, outdat, outtxt

    def get_outpng(self):
        return self.dir + self.outname + '.png'

    def get_outdat(self):
        return self.dir + self.outname + '.dat'

    def get_outtxt(self):
        return self.dir + self.outname + '.txt'



    def get_outprofs(self):
        profnus = []; profdeltas = []; profsigs = []
        profM = self.dir + self.outname+'.profM'
        profnus.append(self.dir + self.outname+'.profnu1')
        profdeltas.append(self.dir + self.outname+'.profdelta1')
        profsigs.append(self.dir + self.outname+'.profsig1')
        if gp.pops == 2:
            profnus.append(self.dir + self.outname+'.profnu2')
            profdeltas.append(self.dir + self.outname+'.profdelta2')
            profsigs.append(self.dir + self.outname+'.profsig2')
        return profM, profnus, profdeltas, profsigs
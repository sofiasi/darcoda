#!/usr/bin/env python3

##
# @file
# plot walker models

# (c) 2013 Pascal Steger, psteger@phys.ethz.ch

import numpy as np
from pylab import *
import pdb
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from matplotlib.backends.backend_pdf import PdfPages
from plots_common import *

## run all plotting commands
def run():
    # Walker data sets
    base = gp.files.machine
    dir = base + '/DTobs/for/'

    # TODO: replace nampart selection with select_run.run()
    # nampart = '20130425120348_cprior_mslope_rprior' # ca2 working fine for 1000 iterations
    # nampart = '20130426090433_cprior_mslope_rprior' # ca2 too high mass at high radii, 50k
    # nampart = '20130426120258_cprior_mslope_rprior' # ca2 better mass? no, too low overall
    # nampart = '20130426161637_cprior_nulog_denslog_mslope_rprior' # ca2 new denslog:  too high mass, especially around middle radii
    # nampart = '20130426165536_cprior_nulog_denslog_mslope_rprior' # ca2 and up to 100000 its: works
    # nampart = '20130429110855_cprior_nulog_denslog_mslope_rprior' # 50k steps: works
    # nampart = '20130502080536_cprior_nulog_denslog_mslope_rprior' # ca0 10: London failed 2.5k, too high mass
    # nampart = '20130510090417_case_1_0_0_cprior_nulog_denslog_mslope_rprior' # ca2, core, running
    # nampart = '20130620084320_cprior_nulog_denslog_mslope_rprior' # Fornax 11k it, stopped due to rising dens prior
    # nampart = '20130620130634_cprior_nulog_denslog_mslope_rprior' # Fornax 6k it, stopped due to rising dens prior
    # nampart = '20130620155947_cprior_nulog_denslog_mslope_rprior' # Fornax >15k it, running
    nampart = '20130625094648_cprior_nulog_denslog_mslope_rprior' # 100k its
    basename = dir + nampart + '/' + nampart

    print('input: ', basename)
    M = np.loadtxt(basename+'.profdens',skiprows=0,unpack=False)
    # M = np.loadtxt(basename+'.profdelta1',skiprows=0,unpack=False)
    
    radii = M[0]
    radii = radii
    profs = M[1000::10]
    print('# models: ',len(profs))
    
    Mprofbins = np.transpose(profs)
    
    for i in range(len(Mprofbins)):
        # sort all mass models bin by bin
        Mprofbins[i] = np.sort(Mprofbins[i])
        
    bins=len(radii)
    Mmedi = np.zeros(bins); Mmax  = np.zeros(bins); Mmin  = np.zeros(bins)
    M95hi = np.zeros(bins); M95lo = np.zeros(bins)
    M68hi = np.zeros(bins); M68lo = np.zeros(bins)
    mlen = len(Mprofbins[0])
    for i in range(len(radii)):
        Mmax[i]  = Mprofbins[i,mlen-1]
        M95hi[i] = Mprofbins[i,0.95 * mlen]
        M68hi[i] = Mprofbins[i,0.68 * mlen]
        Mmedi[i] = Mprofbins[i,0.50 * mlen]
        M68lo[i] = Mprofbins[i,0.32 * mlen]
        M95lo[i] = Mprofbins[i,0.05 * mlen]
        Mmin[i]  = Mprofbins[i,0]
        
    rsc = 1.#0.5
    Msc = 1.#10.
    sel = (radii<15000.)             # TODO: selection right?
    radsc = radii[sel]*rsc

    ion()
    plot1 = plotGraph()
    pp = PdfPages(basename + '.profdens.pdf')
    # pp = PdfPages(basename + '.profdelta1.pdf')
    pp.savefig(plot1)

    # We can also set the file's metadata via the PdfPages object:
    d = pp.infodict()
    d['Title'] = 'Multipage PDF'
    d['Author'] = u'Pascal Steger'
    d['Subject'] = 'dwarf spheroidal dark matter density profile'
    d['Keywords'] = 'PdfPages multipage keywords author title subject'
#   d['CreationDate'] = datetime.datetime(2013,05,06)
    d['ModDate'] = datetime.datetime.today()
    pp.close()
    ioff()

    save_profile(basename,'dens',M95lo,M68lo,Mmedi,M68hi,M95hi)

    analyt = M_anf(radii)

    print('# radii  lower 95%    lower 68%   median      upper 68%   upper 95%   analytic')
    for i in range(len(radii)):
        print(radii[i],M95lo[i],M68lo[i],Mmedi[i],M68hi[i],M95hi[i],analyt[i])

    show_plots()
    return

## plot all things in one plot
def plotGraph():
    fig = plt.figure()
    ### Plotting arrangements ###
    xlabel(r'$r\quad[\mathrm{pc}]$')
    #ylabel(r'$M\quad[\mathrm{M}_{\odot}]$') #[10^5 M_{\odot}]')
    #ylabel(r'$\beta$') #[10^5 M_{\odot}]')
    ylabel(r'$\rho\quad[\mathrm{M}_{\odot}/\mathrm{pc}^3]$') #[10^5 M_{\odot}]')
    fill_between(radsc, M95lo[sel]*Msc, M95hi[sel]*Msc,\
                 color='black',alpha=0.2,lw=1)
    fill_between(radsc, M68lo[sel]*Msc, M68hi[sel]*Msc,\
                 color='black',alpha=0.4,lw=1)
    plot(radsc,Mmedi[sel]*Msc,'r',lw=2)

    # theoretical model
    # plot(rsc*radii[sel],Msc*Mwalkertot(radii)[sel],'--',color='black',lw=2)
    # only for dens:
    errorbar(x=668.,y=4.2E-2, xerr=34., yerr=0.7E-2,lw=2) 
    # data point from Walker+2009
    xscale('log');    yscale('log')
    ylim([0.005,1.5]); xlim([100.,1200.])
    return fig

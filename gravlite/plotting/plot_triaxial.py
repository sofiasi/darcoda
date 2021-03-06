#!/usr/bin/env python3

##
# @file
# plot range of profiles for triaxial dataset

# (c) 2013 Pascal Steger, psteger@phys.ethz.ch


import numpy as np
from pylab import *
import pdb
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from gl_analytic import Mwalkertot, rhowalktot_3D, rhotriax, betatriax
from matplotlib.backends.backend_pdf import PdfPages
from plots_common import *

# TODO: use select_run
# Walker data sets
base = gp.files.machine

# case
dir = base + 'DT_triax/StarsInCuspI/'
# first
nampart = '20130705155757_cprior_nulog_denslog_mslope_rprior' 
# first Mio, with node
nampart = '20130717093510_cprior_nulog_denslog_mslope_rprior' 
# 2nd Mio
nampart = '20130718123300_cprior_nulog_denslog_mslope_rprior' 

basename = dir + nampart + '/' + nampart

print('input: ', basename)
# M = np.loadtxt(basename+'.profrho',skiprows=0,unpack=False)
M = np.loadtxt(basename+'.profdelta1',skiprows=0,unpack=False)

radii = M[0]
radii = radii
profs = M[1::10]
#profs = M[-20000:]

Mprofbins = np.transpose(profs)
radii = radii[:-1]
Mprofbins = Mprofbins[:-1]

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
Msc = 1.
sel = (radii<15000.)             # TODO: selection right?
radsc = radii[sel]*rsc


def plotGraph():
    fig = plt.figure()
    ### Plotting arrangements ###
    xlabel(r'$r\quad[\mathrm{pc}]$')
    #ylabel(r'$M\quad[\mathrm{M}_{\odot}]$') #[10^5 M_{\odot}]')
    #ylabel(r'$\rho\quad[\mathrm{M}_{\odot}/\mathrm{pc}^3]$') #[10^5 M_{\odot}]')
    ylabel(r'$\beta$')
    fill_between(radsc, M95lo[sel]*Msc, M95hi[sel]*Msc,\
                 color='black',alpha=0.2,lw=1)
    fill_between(radsc, M68lo[sel]*Msc, M68hi[sel]*Msc,\
                 color='black',alpha=0.4,lw=1)
    plot(radsc,Mmedi[sel]*Msc,'r',lw=2)
    # theoretical model
    #plot(rsc*radii[sel],Msc*Mwalkertot(radii)[sel],'--',color='black',lw=2)
    #plot(rsc*radii[sel],Msc*rhowalktot_3D(radii)[sel],'--',color='black',lw=2)
    #plot(rsc*radii[sel],Msc*rhotriax(radii)[sel],'--',color='black',lw=2)
    plot(rsc*radii[sel],Msc*betatriax(radii)[sel],'--',color='black',lw=2)

    axvline(x=1500., color='green', visible=True)
    axvline(x=1500.*0.8, color='green', visible=True)
    axvline(x=1500.*0.6, color='green', visible=True)
    axvline(x=810., color='blue', visible=True)

    # xscale('log'); yscale('log'); ylim([0.005,1.5])
    xlim([100.,1200.])
    ylim([-0.15,0.9])
    return fig

ion()
plot1 = plotGraph()
# pp = PdfPages(basename + '.profdens.pdf')
pp = PdfPages(basename + '.profdelta1.pdf')
pp.savefig(plot1)

# We can also set the file's metadata via the PdfPages object:
d = pp.infodict()
d['Title'] = 'Multipage PDF'
d['Author'] = u'Pascal Steger'
d['Subject'] = 'dwarf spheroidal dark matter density profile'
d['Keywords'] = 'PdfPages multipage keywords author title subject'
d['CreationDate'] = datetime.datetime(2013,05,06)
d['ModDate'] = datetime.datetime.today()
pp.close()
ioff()

save_profile(basename,'delta1',M95lo,M68lo,Mmedi,M68hi,M95hi)

#analyt = M_anf(radii)
analyt = betatriax(radii)

print('# radii  lower 95%    lower 68%   median      upper 68%   upper 95%   analytic')
for i in range(len(radii)):
    print(radii[i],M95lo[i],M68lo[i],Mmedi[i],M68hi[i],M95hi[i],analyt[i])


show_plots()


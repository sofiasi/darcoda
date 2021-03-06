#!/usr/bin/env python3

##
# @file
# all helper functions

# (c) 2013 Pascal S.P. Steger, psteger@phys.ethz.ch

import numpy as np
import numpy.random as npr
import sys
import traceback
import pdb
from scipy.interpolate import splrep, splev
from scipy.integrate import quad
import gl_params as gp
import gl_plot as gpl

def myfill(x,N=3):
    if x==np.inf or x==-np.inf:
        return "inf"
    return str(int(x)).zfill(N)
## \fn myfill(x,N=3)
#  print integer with leading zeros
# @param x integer
# @param N number of paddings
# @return 00x


def quadinflog(x, y, A, B):
    # work in log(y) space to enable smoother interpolating functions
    # scale to avoid any values <= 1
    minlog = min(np.log(y))
    shiftlog = np.exp(1.5-minlog) # 1.-minlog not possible
    # otherwise we get divergent integrals for high radii (low length of x and y)
    tcknulog = splrep(x, np.log(y*shiftlog), k=1, s=0.1)
    maxy = max(y)
    invexp = lambda x: min(maxy, np.exp(splev(x,tcknulog,der=0))/shiftlog)
    dropoffint = quad(invexp, A, B)
    return dropoffint[0]
## \fn quadinflog(x, y, A, B)
# integrate y over x, using splines
# @param x free variable
# @param integrand
# @param A left boundary
# @param B right boundary

def quadinfloglog(x, y, A, B):
    # work in log(x), log(y) space to enable smoother interpolating functions
    # scale to avoid any values <= 1
    #minlog = min(np.log(y))
    #shiftlog = np.exp(1.5-minlog) # 1.-minlog not possible,
    # otherwise we get divergent integrals for high radii (low length of x and y)
    tcknulog = splrep(np.log(x), np.log(y), k=1, s=0.1) # tunable k=2; s=0, ..
    invexp = lambda x: min(y[0], np.exp(splev(np.log(x), tcknulog, der=0)))#/shiftlog)
    dropoffint = quad(invexp, A, B)
    return dropoffint[0]
## \fn quadinflog(x, y, A, B)
# integrate y over x, using splines
# @param x free variable
# @param integrand
# @param A left boundary
# @param B right boundary


def quadinflog2(x, y, A, B):
    # work in logarithmic space to enable smoother interpolating functions
    # scale to avoid any values <= 1 (such that a second log step can be taken)
    minlog = min(np.log(y))
    shiftlog = np.exp(1.5-minlog) # 1.-minlog not possible,
    # otherwise we get divergent integrals for high radii (low length of x and y)
    
    tcknulog = splrep(x,np.log(np.log(y*shiftlog)), k=1, s=0.1)
    invexp = lambda x: min(y[0],np.exp(np.exp(splev(x,tcknulog,der=0)))/shiftlog)
    dropoffint = quad(invexp, A, B)
    return dropoffint[0]
## \fn quadinflog2(x, y, A, B)
# integrate y over x, using splines in log(log(y)) space
# @param x free variable
# @param integrand
# @param A left boundary
# @param B right boundary


def checknan(arr, place=''):
    if np.isnan(np.sum(arr)):
        print('NaN found! '+place)
        raise Exception('NaN', 'found')
        traceback.print_tb(sys.exc_info()[2])
        return True
    else:
        return False
## \fn checknan(arr, place=''):
# NaN encountered at any position in arr?
# @param arr array of float values
# @return True if NaN found

    
def checkpositive(arr, place=''):
    if checknan(arr, place):
        return True
    if min(arr) < 0.:
        print(place+" < 0 !")
        # traceback.print_tb(sys.exc_info()[2])
        raise Exception('negative','found')
        return True
    else:
        return False
## \fn checkpositive(arr, place='')
# abort if negative value found
# @param arr array of float values
# @return Exception if (non-physical) negative value found


def derivative(f):
    def df(x, h=0.1e-5):
        return ( f(x+h/2) - f(x-h/2) )/h
    return df
## \fn derivative(f)
# Computes the numerical derivative of a function.
# @param f function (ex. sin  or  cos)

def deriv(y,x):
    step = x[1]-x[0]
    xnew = []
    flick = 5.
    for i in range(len(x)):
        xnew.append(x[i]-step/flick)
        xnew.append(x[i]+step/flick)

    ynew = ipol(x,y,xnew,smooth=1.5e-9)
    
    dydx = []
    for i in range(len(x)):
        dydx.append((ynew[2*i+1]-ynew[2*i])/(step/flick))

    return np.array(dydx)
## \fn deriv(y,x)
# gives numeric differentiation, assumes constant x spacings
# @param y dependent variable, array of size N
# @param x free variable, array of same size N
# @return dy/dx

def derivcoarse(y,x):
    y0 = ipol(x[:3],y[:3],x[0]-(x[1]-x[0])) #[y]
    y = np.hstack([y0, y]) #[y]
    x = np.hstack([x[0]-(x[1]-x[0]), x]) #[x]
    return (y[1:]-y[:-1])/(x[1:]-x[:-1])
## \fn derivcoarse(y,x)
# numerical derivative, with h=const=stepsize of radial bins
# @param y dependent variable, array of size N
# @param x free variable, array of same size N
# @return quotient of differences


def derivipol(y,x):
    step = x[1]-x[0]
    rbf = Rbf(x, y, smooth=1.5e-9)

    dydx = np.zeros(len(x))
    import scipy.misc as sm
    for i in range(len(x)):
        dydx[i] = sm.derivative(rbf, x[i], dx=step, n=1, args=(), order=3)
    return dydx
## \fn derivipol(y,x)
# numerical derivated with function from interpolation
# @param y dependent variable, array of size N
# @param x free variable, array of same size N


def err(a):
    return gp.err/a*(1.+npr.rand()/1000.)
## \fn err(a)
# penalize prior violations with almost constant low likelihood
# a small change makes sure that if all nlive points in MultiNest
# get the same error, it does not abort there

def expDtofloat(strun):
    return float(strun.decode('utf-8').replace('D','E'))
## \fn expDtofloat(s)
# replace D floats with E floats
# @param s string
# @return s in 'xxxExx' format


def readcol3(filena):
    a,b,c = np.loadtxt(filena,skiprows=1,unpack=True)
    return a,b,c
## \fn readcol3(filena)
# read in 3 columns of data
# @param filena filename
# @return a,b,c: columns of a 3-column file


def readcol5(filena):
    a,b,c,d,e = np.loadtxt(filena,skiprows=1,unpack=True)
    return a,b,c,d,e
## \fn readcol5(filena)
# read in 5 columns of data
# @param filena filename
# @return 5 columns


def readcoln(filena):
    return np.loadtxt(filena,skiprows=1,unpack=True)
## \fn readcoln(filena)
# read in n columns of data
# @param filena filename
# @return array

    
def pretty(arr,dig=3):
    return ("%."+str(dig)+"f")%arr
## \fn pretty(arr,dig=3)
# clip floats after dig=3 digits
# @param arr array of floats
# @param dig number of digits, default is 3


from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
def smooth(xin, yin, smooth=1.e-9):
    return ipol(xin,yin,xin,smooth)
## \fn smooth(xin, yin, smooth=1.e-9)
# interpolate function in lin space, smooth it
# @param xin free variable array
# @param yin dependent array
# @smooth smoothing number. very small as a default. can be enhanced for smaller derivatives


def smoothlog(xin,yin,smooth=1.e-9):
    return ipollog(xin,yin,xin,smooth)
## \fn smoothlog(xin, yin, smooth=1.e-9
# interpolate function in log space, smooth it. use only if yin[i]>0
# @param xin free variable array
# @param yin dependent array
# @smooth smoothing number. very small as a default. can be enhanced for smaller derivatives


def ipol(xin,yin,xout,smooth=1.e-9):
    if np.isnan(np.sum(yin)):
        print('NaN found! Go check where it occured!')
        pdb.set_trace()
    rbf = Rbf(xin, yin, smooth=smooth)
    return rbf(xout)
## \fn ipol(xin, yin, xout, smooth=1.e-9)
# interpolate function in lin space, based on radial basis functions
# @param xin free variable array
# @param yin dependent array
# @param xout interpolation points
# @smooth smoothing number. very small as a default. can be enhanced for smaller derivatives


def ipollog(xin, yin, xout, smooth=1.e-9):
    if min(yin)<0.:
        print(file='negative value encountered in ipollog, working with ipol now')
        return ipol(xin,yin,xout,smooth)
    
    rbf = Rbf(xin, np.log10(yin), smooth=smooth)
    return 10**(rbf(xout))
## \fn ipollog(xin, yin, xout, smooth=1.e-9)
# interpolate function in log space, based on radial basis functions
# @param xin free variable array
# @param yin dependent array
# @param xout interpolation points
# @smooth smoothing number. very small as a default. can be enhanced for smaller derivatives


def expol(xin, yin, xout):
    rbf = Rbf(xin, yin)
    return rbf(xout)
## \fn expol(xin, yin, xout)
# extrapolate data to xout, based on radial basis functions
# @param xin free variable array
# @param yin dependent array
# @param xout interpolation points


def wait():
    input("Press Enter to continue...")
    return
## \fn wait()
# wait for key press

def bin_r_linear(rmin, rmax, nbin):
    binlength = (rmax - rmin)/(1.*nbin) #[rscale]
    binmin = np.zeros(nbin);  binmax = np.zeros(nbin)
    rbin = np.zeros(nbin)
    for k in range(nbin):
        binmin[k] = rmin+k*binlength #[rscale]
        binmax[k] = rmin+(k+1)*binlength #[rscale]
        rbin[k]   = binmin[k]+0.5*binlength #[rscale]
    return binmin, binmax, rbin
## \fn bin_r_linear(rmin, rmax, nbin)
# split interval linearly into bins
# @param rmin starting point of interval
# @param rmax endpoint of interval
# @param nbin number of bins
# @return arrays of (beginning of bins, end of bins, position of bins)


def bin_r_log(rmin, rmax, nbin):
    bins   = np.logspace(np.log10(rmin), np.log10(rmax), nbin+1, endpoint=True)
    binmin = bins[:-1]; binmax = bins[1:]
    rbin = np.zeros(nbin)
    for k in range(nbin):
        rbin[k]   = np.logspace(np.log10(binmin[k]),np.log10(binmax[k]),3, endpoint=True)[1]
    return binmin, binmax, rbin
## \fn bin_r_log(rmin, rmax, nbin)
# split interval into bins, in a logarithmic fashion
# @param rmin starting point of interval
# @param rmax endpoint of interval
# @param nbin number of bins
# @return arrays of (beginning of bins, end of bins, position of bins)


def bin_r_const_tracers(r0,no):
    # procedure: get all particles in bin i
    #            get minimum, maximum radius. get radius of min/max before/after bin i
    #            get mean of (half of max bin/min next bin) for bin radius
    order = np.argsort(r0)
    r0 = np.array(r0)[order]

    no = int(no)
    
    mini = list(range(1,len(r0),no))
    maxi = list(range(no,len(r0),no))
    maxi.append(len(r0))
    mini = np.array(mini)-1; maxi = np.array(maxi)-1
    minri = [];   maxri = []
    nbin = int(1.*len(r0)/no)
    for i in range(nbin):
        minri.append(r0[mini[i]])
        maxri.append(r0[maxi[i]])

    midri = []
    # TODO: check fine to take *not* half the first particle radius for midri
    for i in range(nbin):
        midri.append((minri[i]+maxri[i])/2.)
    return minri, maxri, midri
## \fn bin_r_const_tracers(r0, no)
# split interval into bins of constant particle number
# @param r0 radii from all particles in an array
# @param no integer, number of bins
# @return arrays of (beginning of bins, end of bins, position of bins)


def sort_profiles_binwise(profs):
    for i in range(len(profs)):
        # sort all mass models bin by bin
        profs[i] = np.sort(profs[i])
    return profs
## \fn sort_profiles_binwise(profs)
# take array of profiles, sort along each bin
# @param profs array [prof1, prof2, ..., profN]
# @return [bin1 bin2 .. binN]_min .. [bin1 bin2 .. binN]_max


def get_median_1_2_sig(profs):
    bins = len(profs)
    Mmedi = np.zeros(bins); Mmax  = np.zeros(bins); Mmin  = np.zeros(bins)
    M95hi = np.zeros(bins); M95lo = np.zeros(bins)
    M68hi = np.zeros(bins); M68lo = np.zeros(bins)
    mlen = len(profs[0])
    for i in range(bins):
        Mmax[i]  = profs[i, mlen-1]
        M95hi[i] = profs[i, 0.95 * mlen]
        M68hi[i] = profs[i, 0.68 * mlen]
        Mmedi[i] = profs[i, 0.50 * mlen]
        M68lo[i] = profs[i, 0.32 * mlen]
        M95lo[i] = profs[i, 0.05 * mlen]
        Mmin[i]  = profs[i, 0]
    return Mmin, M95lo, M68lo, Mmedi, M68hi, M95hi, Mmax
## \fn get_median_1_2_sig(profs)
# return envelopes of profiles at median, min, max, and 1, 2 sigma interval for a range of profiles
# @param profs bin-wise sorted profiles
# @return  Mmin, M95lo, M68lo, Mmedi, M68hi, M95hi, Mmax


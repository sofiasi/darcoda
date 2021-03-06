#!/usr/bin/python
# calculate density falloff
import gl_params as gp
import gr_params as gpr
import numpy as np
import multiprocessing as mp

# set binning
print 'TODO: check whether 2*rmax is needed!'
if gp.lograd:
  binmin,binmax,rbin = gh.bin_r_log(gpr.rmax/gpr.nbins,gpr.rmax,gp.nbins)
else:
  binmin,binmax,rbin = gh.bin_r_linear(gpr.rmin,gpr.rmax,gp.nbins)



print 'input:'
print gpr.fileposspherical
r,phi = np.loadtxt(gpr.fileposspherical,unpack=True,skiprows=1)
ndm = len(r)
rs  = r       #gpr.rerror*np.random.randn(ndm)+r

def foo_pool(k):
  rsi = gpr.rerror*np.random.randn(len(rs))+rs
  locmass = []; loca = []
  for i in range(bins):
    ind1=np.argwhere(np.logical_and( rsi > rbin[i], rsi < rbin[i+1])).flatten()
    locmass.append(1.*len(ind1)/ndm)
    loca.append(1.*len(ind1))
  return locmass,loca

mass=[]
alog=[]
def log_result(result):
  m,a=result
  mass.append(m)
  alog.append(a)

pool=mp.Pool(processes=24)
for k in range(gpr.nit):
  pool.apply_async(foo_pool, args=(k, ), callback=log_result)
pool.close()
pool.join()

massarr = np.array(mass)
aarr = np.array(alog)

print 'output:'
print gpr.filemass
filemass = open(gpr.filemass,'w')
print >> filemass,'r','M(r)','error'
totmass=0
ac=0
for i in range(bins):
  totmass  += np.sum(massarr[:,i])/gpr.nit
  ac       += np.sum(aarr[:,i])/gpr.nit
  masserror = totmass/np.sqrt(ac)
  print >> filemass, rbin[i+1], totmass, masserror
  print rbin[i+1], totmass, masserror

filemass.close()

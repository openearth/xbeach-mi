#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 15:24:17 CEST 2016

@author: dro, wv

using kdtree
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from interpol import interpoldln,interpolkd

def tic():
    # Homemade version of matlab tic and toc functions
    import time
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()


def toc():
    import time
    if 'startTime_for_tictoc' in globals():
        print "Elapsed time is " + str(time.time() - startTime_for_tictoc) + " seconds."
    else:
        print "Toc: start time not set"

Plot = False
Plot = True

def plotit(name,x1,y1,z1,x2,y2,z2,amp):
    plt.figure()
    plt.scatter(x1, y1, 10, z1, linewidths=0.01, vmin=0., vmax=amp)
    plt.scatter(x2.flatten(), y2.flatten(),
                5, z2, linewidths=0.01, vmin=0., vmax=amp)
    plt.axis('equal')
    plt.savefig(name)
    plt.close()

# Test kdtree
tic()
print 'preparation'
m1 = 200
n1 = 600

dx = 10.
dy = 10.
xori = 0.
yori = 0.
alfa = 20. * np.pi / 180.
amp = 1.
L = 1000
x0 = 500.
y0 = 2500.
cosa = np.cos(alfa)
sina = np.sin(alfa)
x1 = np.zeros((m1, n1))
y1 = np.zeros((m1, n1))
mask = np.ones((m1, n1))
for j in range(n1):
    for i in range(m1):
        x1[i, j] = xori + i * dx * cosa - j * dy * sina
        y1[i, j] = yori + i * dx * sina + j * dy * cosa
#        z1[i,j]=i+m1*j
z1 = amp * np.exp(-((x1 - x0) ** 2 + (y1 - y0) ** 2) / L ** 2)
m2 = 50
n2 = 500
dx2 = 20.
dy2 = 5.
xori = 500.
yori = 2000.
alfa = 30. * np.pi / 180.
cosa = np.cos(alfa)
sina = np.sin(alfa)
x2 = np.zeros((m2, n2))
y2 = np.zeros((m2, n2))
z2 = np.zeros((m2* n2)) 

z2_ini = np.zeros((m2* n2)) + amp

for j in range(n2):
    for i in range(m2):
        x2[i, j] = xori + i * dx2 * cosa - j * dy2 * sina
        y2[i, j] = yori + i * dx2 * sina + j * dy2 * cosa
print 'grid 1 ', m1 * n1, ' points, grid 2 ', m2 * n2, ' points'
toc()
gr = np.asarray((x1.flatten(), y1.flatten())).T
tic()
print 'testing Delaunay'
tri = interpoldln(gr,z1.flatten(),fill_value=amp)
toc()
tic()
print 'testing kdtree'
distx = abs(gr[0,0]-gr[1,0])
disty = abs(gr[0,0]-gr[1,1])
max_dist = 2*max(distx,disty)
max_dist = 1.1*np.sqrt(distx**2 + disty**2)
tree = interpolkd(gr,z1.flatten(),fill_value=amp,max_dist=max_dist)
toc()
tic()
print 'testing Delaunay interpolation'
z2 = tri(np.asarray((x2.flatten(), y2.flatten())).T)
toc()
if Plot:
    tic()
    print 'plotting results for Delaunay interpolation:'
    plotit('000dln.png',x1,y1,z1,x2,y2,z2,amp)
    toc()
tic()
print 'testing kdtree interpolation'
z2 = tree(np.asarray((x2.flatten(), y2.flatten())).T)
toc()
if Plot:
    tic()
    print 'plotting results for kdtree interpolation:'
    plotit('000kd.png',x1,y1,z1,x2,y2,z2,amp)
    toc()
for y0 in range(500,5000,500):
    print 'shift hump in grid 1 and interpolate again'
    z1 = amp * np.exp(-((x1 - x0) ** 2 + (y1 - y0) ** 2) / L ** 2)
    tri.setz(z1.flatten())
    tree.setz(z1.flatten())
    print 'Delaunay:'
    tic()
    z2 = tri(np.asarray((x2.flatten(), y2.flatten())).T)
    toc()
    if Plot:
        tic()
        print 'plotting Delaunay'
        plotit('%ddln.png'%y0,x1,y1,z1,x2,y2,z2,amp)
        toc()
    print 'kdtree:'
    tic()
    z2 = tree(np.asarray((x2.flatten(), y2.flatten())).T)
    toc()
    if Plot:
        tic()
        print 'plotting kdtree'
        plotit('%dkd.png'%y0,x1,y1,z1,x2,y2,z2,amp)
        toc()
    toc()

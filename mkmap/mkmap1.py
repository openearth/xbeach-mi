# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 18:13:20 2016

@author: dro

wvermin: trying to optimize this. In statu nascendi
"""
import sys
#from numpy import *
import numpy as np
#from timeit import *
import timeit as tm
import bisect
import matplotlib.pyplot as plt
from inspect import currentframe

def getln():  # get line number
    cf = currentframe()
    return 'line '+str(cf.f_back.f_lineno)+':'


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


def bilin5(xa, ya, x, y):
    w = np.zeros(4)
    ier = 0
    x1 = xa[0]
    y1 = ya[0]
    x2 = xa[1]
    y2 = ya[1]
    x3 = xa[2]
    y3 = ya[2]
    x4 = xa[3]
    y4 = ya[3]
    #
    # The bilinear interpolation problem is first transformed
    # to the quadrangle with nodes (0,0),(1,0),(x3t,y3t),(0,1)
    # and required location (xt,yt)
    #
    a21 = x2 - x1
    a22 = y2 - y1
    a31 = x3 - x1
    a32 = y3 - y1
    a41 = x4 - x1
    a42 = y4 - y1
    det = a21 * a42 - a22 * a41
    if abs(det) < 1.0e-20:
        ier = 1
        w[0:3] = 0.
        return w, ier
    x3t = (a42 * a31 - a41 * a32) / det
    y3t = (-a22 * a31 + a21 * a32) / det
    xt = (a42 * (x - x1) - a41 * (y - y1)) / det
    yt = (-a22 * (x - x1) + a21 * (y - y1)) / det
    if (x3t < 0.0) or (y3t < 0.0):
        # distorted quadrangle
        ier = 2
        return w, ier
    if abs(x3t - 1.0) < 1.0e-7:
        xi = xt
        if abs(y3t - 1.0) < 1.0e-7:
            eta = yt
        elif abs(1.0 + (y3t - 1.0) * xt) < 1.0e-6:
            # extrapolation over too large a distance
            ier = 3
            return w, ier
        else:
            eta = yt / (1.0 + (y3t - 1.0) * xt)
    elif abs(y3t - 1.0) < 1.0e-6:
        eta = yt
        if abs(1.00 + (x3t - 1.0) * yt) < 1.0e-6:
            # extrapolation over too large a distance
            ier = 3
            return w, ier
        else:
            xi = xt / (1.0 + (x3t - 1.0) * yt)
    else:
        a = y3t - 1.0
        b = 1.0 + (x3t - 1.0) * yt - (y3t - 1.0) * xt
        c = -xt
        discr = b * b - 4.0 * a * c
        if discr < 1.0e-6:
            # extrapolation over too large a distance
            ier = 3
            return w, ier
        xi = (-b + np.sqrt(discr)) / (2.0 * a)
        eta = ((y3t - 1.0) * (xi - xt) + (x3t - 1.0) * yt) / (x3t - 1.0)
    w[0] = (1.0 - xi) * (1.0 - eta)
    w[1] = xi * (1.0 - eta)
    w[2] = xi * eta
    w[3] = eta * (1.0 - xi)
    return w, ier


def mkmap(x1, y1, mask, x2, y2):
    # --description-----------------------------------------------------------------
    #
    #
    #     FUNCTION MKMAP
    #     Interpolation of curvilinear, numerically ordered grid (grid1)
    #     to random points, with weighting points (grid2).
    #
    #     J.A. Roelvink
    #     UNESCO-IHE/Deltares
    #     24-2-1992 (MKMAP Fortran version)
    #     26-4-2016 (MKMAP Python version)
    #
    #     Given: numerically ordered grid M1*N1
    #     with coordinates X1 (1:M1,1:N1)
    #                  and Y1 (1:M1,1:N1)
    #
    #     Also given: random points X2(1:N2)
    #                           and Y2(1:N2)
    #
    #     To be determined:  weighting factors and pointers for bilinear interpolation
    #     Weighting factors and locations of the requested (random) points in the
    #     ordered grid are saved in resp.
    #     W(0:3,0:N2-1) and Iref(0:3,0:N2-1)
    #
    eps = 0.00001
    #
    x2 = x2.flatten()
    y2 = y2.flatten()
    nrx = np.argsort(x2)
    nry = np.argsort(y2)
    xs = x2[nrx]
    ys = y2[nry]

    #
    # Loop over all cels of grid1
    #
    #
    m1 = np.size(x1, 0)
    n1 = np.size(x1, 1)
    n2 = np.size(x2)
    print getln(),m1,n1,n2
    #filled = np.zeros((m1, n1))
    #iflag  = np.zeros(np.size(x2), dtype=int)
    nrin   = np.zeros(np.size(x2), dtype=int)
    xp     = np.zeros((m1,n1,5))
    yp     = np.zeros((m1,n1,5))
    iref   = np.zeros((4, n2), dtype=int)
    w      = np.zeros((4, n2))
    #ipl    = -1

    
    for j1 in range(n1 - 1):
        print getln(),'een',j1
        for i1 in range(m1 - 1):
#         for i1 in range(4):
            #
            # Cell definition
            #
#            tic()
            if mask[i1, j1] == 0 or mask[i1 + 1, j1] == 0 or mask[i1 + 1, j1 + 1] == 0 or mask[i1, j1 + 1] == 0:
                break
            xp[i1,j1,0] = x1[i1, j1]
            xp[i1,j1,1] = x1[i1 + 1, j1]
            xp[i1,j1,2] = x1[i1 + 1, j1 + 1]
            xp[i1,j1,3] = x1[i1, j1 + 1]
            xp[i1,j1,4] = x1[i1, j1]
            yp[i1,j1,0] = y1[i1, j1]
            yp[i1,j1,1] = y1[i1 + 1, j1]
            yp[i1,j1,2] = y1[i1 + 1, j1 + 1]
            yp[i1,j1,3] = y1[i1, j1 + 1]
            yp[i1,j1,4] = y1[i1, j1]
            # Determine minimum and maximum X and Y of the cell
            #
            xpmin = np.min(xp,2)
            xpmax = np.max(xp,2)
            ypmin = np.min(yp,2)
            ypmax = np.max(yp,2)

            #print getln(),xpmin.shape,':',xp.shape

    xpt     = np.zeros((m1-1,n1-1,5))
    ypt     = np.zeros((m1-1,n1-1,5))
    xpt[:,:,0]       = x1[:m1-1,:n1-1]
    print getln(),xp.shape
    print getln(),xpt[:,:,0]-xp[:m1-1,:n1-1,0]

    xpt[:,:,1]    = x1[1:m1,:n1-1]

    print getln(),xpt[:,:,1]-xp[:m1-1,:n1-1,1]

    xpt[:,:,2] = x1[1:m1,1:n1]
    print getln(),xpt[:,:,2]-xp[:m1-1,:n1-1,2]
    xpt[:,:,3]    = x1[:m1-1,1:n1]
    print getln(),xpt[:,:,3]-xp[:m1-1,:n1-1,3]
    xpt[:,:,4]       = x1[:m1-1,:n1-1]
    print getln(),xpt[:,:,4]-xp[:m1-1,:n1-1,4]
    print getln(),np.sum(np.abs(xpt-xp[:m1-1,:n1-1,:]))
    sys.exit(0)

    for j1 in range(n1 - 1):
        print getln(),'twee',j1
        for i1 in range(m1 - 1):
            if mask[i1, j1] == 0 or mask[i1 + 1, j1] == 0 or mask[i1 + 1, j1 + 1] == 0 or mask[i1, j1 + 1] == 0:
                break
            ilo = bisect.bisect_left(xs, xpmin[i1,j1])
            ihi = bisect.bisect_right(xs, xpmax[i1,j1], lo=ilo)
            jlo = bisect.bisect_left(ys, ypmin[i1,j1])
            jhi = bisect.bisect_right(ys, ypmax[i1,j1], lo=jlo)
            selx = nrx[ilo:ihi]
            sely = nry[jlo:jhi]
            nrin = list(set(selx) & set(sely))
            nin = np.size(nrin)
            #
            # Check whether selected points of grid2 lie within the cell
            # using function IPON; if so, determine weights W of the surrounding
            # values in grid1 using function bilin. Save the weights in Wtab
            # The reference to grid1 is saved in arrays Iref and Jref.
            #
            for iin in range(0, nin):
                i2 = nrin[iin]
                # print i1,j1,iin,i2
                inout = ipon(xp[i1,j1], yp[i1,j1], x2[i2], y2[i2])
                if inout >= 0:
                    w[:, i2], ier = bilin5(xp[i1,j1], yp[i1,j1], x2[i2], y2[i2])
                       #
                    iref[0, i2] = i1 + j1 * m1
                    iref[1, i2] = i1 + 1 + j1 * m1
                    iref[2, i2] = i1 + 1 + (j1 + 1) * m1
                    iref[3, i2] = i1 + (j1 + 1) * m1
                    # print i1,j1,i2
    return w, iref


def grmap(f1, f2, iref, w):
    # --description-----------------------------------------------------------------
    #
    # compute interpolated values for all points on grid 2
    #
    # special treatment of points on grid 2 that are outside
    # grid 1; in that case iref(1,i2)=0 AND w(ip,i2)=0 for all ip
    #
    # Iref(1,i2)   i1    ifac   F2(i2)*ifac     Result
    #
    #      0        1      1      F2(i2)        Old value is kept
    #    j,j>0      j      0       0.           F2 is initialized
    #
    # --pseudo code and references--------------------------------------------------
    # NONE
    # --declarations----------------------------------------------------------------
    #
    # executable statements -------------------------------------------------------
    #
    f1 = f1.transpose()
    f1 = f1.flatten()
    # print f1
    f2 = f2.flatten()
    # print f2
    n1 = np.size(f1)
    Np = np.size(iref, 0)
    n2 = np.size(iref, 1)

    for i2 in range(n2):
        i = iref[0, i2]
        if i > 0:
            f2[i2] = 0.
            # Function values at grid 2 are expressed as weighted average
            # of function values in Np surrounding points of grid 1
            #
            for ip in range(Np):
                i1 = iref[ip, i2]
                f2[i2] = f2[i2] + w[ip, i2] * f1[i1]
                # print i2,ip,i1,w[ip,i2],f1[i1],f2[i2]
    # print f2
    return f2


def ipon(x, y, xp, yp):
#--description----------------------------------------------------------------
#
# Deltares                                                               *
# AUTHOR : J.A.ROELVINK                                                  *
# DATE   : 22-12-1988                                                    *
# DETERMINE WHETHER POINT (xp,yp) LIES IN POLYGON (x,y)
# POINT n+1 IS SET EQUAL TO POINT 1                                      *
# inpout = -1 :  OUTSIDE POLYGON                                         *
# inpout =  0 :  ON EDGE OF POLYGON                                      *
# inpout =  1 :  INSIDE POLYGON                                          *
# USED METHOD :         - DRAW A VERTICAL LINE THROUGH (xp,yp)           *
#                       - DETERMINE NUMBER OF INTERSECTIONS WITH POLYGON *
#                         UNDER yp : nunder                              *
#                       - IF nunder IS EVEN, THEN THE POINT LIES OUTSIDE *
#                         THE POLYGON, OTHERWISE IT LIES INSIDE          *
#                       - THE EDGE IS TREATED SEPARATELY                 *
#
#     Close polygon and subtract coordinates of xp,yp
    n = np.size(x) - 1
#      x=concatenate((x,[x[0]]),0)
#      y=concatenate((y,[y[0]]),0)
    x = x - xp
    y = y - yp
    nunder = 0
    for i in range(n):
#         if max(x)<0 or min(x)>0 or max(y)<0 or min(y)>0:
#             inout=-1
#             return inout
        if abs(x[i]) < 1.0E-8 and abs(y[i]) < 1.0E-8:
            inout = 0
            return inout
        elif (x[i] < 0. and x[i + 1] >= 0.) or (x[i + 1] < 0. and x[i] >= 0.):
            if y[i] < 0. and y[i + 1] < 0.:
                nunder = nunder + 1
            elif (y[i] <= 0. and y[i + 1] >= 0.) or (y[i + 1] <= 0. and y[i] >= 0.):
                ysn = (y[i] * x[i + 1] - x[i] * y[i + 1]) / (x[i + 1] - x[i])
                if ysn < 0.:
                    nunder = nunder + 1
                elif ysn <= 0.:
            #
            # Edge
            #
                    inout = 0
                    return inout
#         elif abs(x[i])<1.0E-8 and abs(x[i + 1])<1.0E-8:
    if np.mod(nunder, 2) == 0:
 #
 # Outside
 #
        inout = -1
    else:
 #
 # Inside
 #
        inout = 1
    return inout

# Test bilin5 and ipon functions
tic()
print 'testing ipon and bilin5'
x = [-1, .5, 1.5, 0, -1.]
y = [.1, -1., -.2, 3, .1]
z = [1., 3., -5., 3., 1.]
Plot = True
xp = -1. + 3. * np.random.random(10000)
yp = -1. + 4. * np.random.random(10000)
zp = np.zeros(np.size(xp))
w = np.zeros((4, np.size(xp)))
for i in range(np.size(xp)):
    if ipon(x, y, xp[i], yp[i]) >= 0:
        ww, ier = bilin5(x, y, xp[i], yp[i])
        w[:, i] = ww
        for j in range(4):
            zp[i] = zp[i] + w[j, i] * z[j]
toc()
tic()
if Plot:
    print 'plotting result of ipon and bilin5'
    plt.figure(1)
    plt.scatter(xp, yp, 20, zp, 'o', linewidths=.01)
    plt.scatter(x, y, 100, z, 'o', linewidths=.01)
    plt.set_cmap('jet')
    plt.plot(x, y, 'k')
    plt.savefig('plot11.png')
toc()
# Test mkmap and grmap functions
tic()
print 'testing mkmap and grmap; preparation'
m1 = 200
n1 = 600
m1=10
n1=30
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
mask = np.ones((m1, n1))

m1t = np.array(range(m1)).reshape(m1,1)
n1t = np.array(range(n1)).reshape(1,n1)
dxt = np.ones((1,n1))*dx
dyt = np.ones((m1,1))*dy

x1 = xori + np.dot(m1t,dxt*cosa)-np.dot(dyt*sina,n1t)
y1 = yori + np.dot(m1t,dxt*sina)+np.dot(dyt*cosa,n1t)

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
z2 = np.zeros((m2, n2))

m2t = np.array(range(m2)).reshape(m2,1)
n2t = np.array(range(n2)).reshape(1,n2)
dx2t = np.ones((1,n2))*dx2
dy2t = np.ones((m2,1))*dy2

x2 = xori + np.dot(m2t,dx2t*cosa)-np.dot(dy2t*sina,n2t)
y2 = yori + np.dot(m2t,dx2t*sina)+np.dot(dy2t*cosa,n2t)


print 'grid 1 ', m1 * n1, ' points, grid 2 ', m2 * n2, ' points'
toc()
tic()
print 'testing mkmap'
w, iref = mkmap(x1, y1, mask, x2, y2)
toc()
tic()
print 'testing grmap'
z2 = grmap(z1, z2, iref, w)
toc()
tic()
if Plot:
    print 'plotting results'
    plt.figure(2)
    plt.scatter(x1, y1, 10, z1, linewidths=0.01, vmin=0., vmax=amp)
    plt.scatter(x2.flatten(), y2.flatten(),
                5, z2, linewidths=0.01, vmin=0., vmax=amp)
    plt.axis('equal')
    plt.savefig('plot12.png')
# plt.pcolor(x2,y2,z2)
toc()
tic()
print 'shift hump in grid 1 and interpolate again'
y0 = 3500.
z1 = amp * np.exp(-((x1 - x0) ** 2 + (y1 - y0) ** 2) / L ** 2)
z2 = grmap(z1, z2, iref, w)
toc()
tic()
if Plot:
    print 'plot results'
    plt.figure(3)
    plt.scatter(x1, y1, 10, z1, linewidths=0.01, vmin=0., vmax=amp)
    plt.scatter(x2.flatten(), y2.flatten(),
                5, z2, linewidths=0.01, vmin=0., vmax=amp)
    plt.axis('equal')
    plt.savefig('plot13.png')
toc()

import sys
import numpy as np
try:
    from pykdtree.kdtree import KDTree
    print 'Using pykdtree'
except:
    from scipy.spatial import cKDTree as KDTree
    print 'Using scipy.spatial'
# pykdtree from https://github.com/storpipfugl/pykdtree is much faster:
#    from pykdtree.kdtree import KDTree
class interpolkd:
#
# works with scipy and pykdtree:
#

    def __init__(self, X, z=None, max_dist=-1, fill_value=np.NaN, leafsize=10):
        self.tree = KDTree(X, leafsize=leafsize)
        self.length = len(X)
        self.setfill_value(fill_value)
        if z is not None:
            self.setz(z)
        self.setmax_dist(max_dist)

    def setz(self,z):
        assert self.length == len(z), "len(X) %d != len(z) %d" % (self.length, len(z))
        self.z = z.copy()

    def setfill_value(self,fill_value):
        self.fill_value = fill_value

    def setmax_dist(self,max_dist):
        self.max_dist = max_dist

    def __call__(self,q,nnear=2,p=1):
        q = np.asarray(q)
        qdim = q.ndim
        if qdim == 1:
            q = np.array([q])
            
        d, ix = self.tree.query(q, k=nnear, eps=0)

        if nnear == 1:
            wz=self.z[ix]
        else:
            w = 1./np.maximum(d,1e-10)**p
            w = np.divide(w,np.sum(w,axis=1)[:,np.newaxis])
            wz = np.einsum('ij,ij->i',w,self.z[ix])

        if self.max_dist >= 0:
            if len(d.shape) == 2:
                wz[np.min(d,1) > self.max_dist] = self.fill_value
            else:
                wz[d > self.max_dist] = self.fill_value

        return wz if qdim > 1 else wz[0]
        
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator
class interpoldln:
    def __init__(self,X,z=None,fill_value=np.NaN):
        self.tri = Delaunay(X)
        self.length = X.shape[0]
        self.dim = X.shape[1]
        self.setfill_value(fill_value)
        if z is not None:
            self.setz(z)

    def setz(self,z):
        assert self.length == len(z), "len(X) %d != len(z) %d" % (self.length, len(z))
        self.z = z.copy()
        self.F = LinearNDInterpolator(self.tri, self.z, fill_value=self.fill_value)
        # warming up this function:
        self.F(np.zeros(self.dim))

    def setfill_value(self,fill_value):
        self.fill_value = fill_value

    def __call__(self,q):
        result = self.F(q)
        return result

if __name__ == "__main__":
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

    r=np.random.random
    n=300
    x = np.linspace(-1,1,n+1)
    y = np.linspace(-2,2,n+1)
    xv,yv = np.meshgrid(x,y)
    X = np.array((xv.flatten(),yv.flatten())).T
    z = np.array(r(X.shape[0]))
    z = np.sum(np.sin(X),1)
    q = np.array((r(5),r(5))).T-0.5
    print 'number of grid points:',X.shape[0]
    print 'computing kd tree:'
    tic()
    tree = interpolkd(X,z=z,fill_value=-123.)
    toc()
    print 'computing dln tree:'
    tic()
    tri = interpoldln(X,z,fill_value=-123.)
    toc()
    rtree = tree(q)
    rtri = tri(q)

    print 'kd ',rtree
    print 'dln',rtri

    print 
    m = 100000
    print 'interpolating',m,'random points'
    qq = np.array((r(m),r(m))).T-0.5
    print 'kd tree:'
    tic()
    rtree = tree(qq)
    toc()
    qq = np.array((r(m),r(m))).T-0.5
    print 'dln tree:',qq.shape
    tic()
    rtri = tri(qq)
    toc()

    nx = int(np.sqrt(m))
    ny = nx
    xx = np.linspace(-0.9,0.9,nx+1)
    yy = np.linspace(-1.9,1.9,ny+1)
    xxv,yyv = np.meshgrid(xx,yy)
    qqq = np.array((xxv.flatten(),yyv.flatten())).T
    print 'interpolating',qqq.shape[0],'regular grid points'

    print 'kd tree:'
    tic()
    rtree = tree(qqq)
    toc()
    print 'dln tree:'
    tic()
    rtri = tri(qqq)
    toc()

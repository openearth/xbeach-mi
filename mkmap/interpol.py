import sys
import numpy as np
class interpolkd:
#
# works with scipy and pykdtree:
#
    try:
        from pykdtree.kdtree import KDTree
        print 'Using pykdtree'
    except:
        from scipy.spatial import cKDTree as KDTree
        print 'Using scipy.spatial'
# pykdtree from https://github.com/storpipfugl/pykdtree is much faster:
#    from pykdtree.kdtree import KDTree

    def __init__(self, X, z=None, max_dist=-1, fill_value=np.NaN, leafsize=10):
        self.tree = self.KDTree(X, leafsize=leafsize)
        self.length = len(X)
        self.setfill_value(fill_value)
        if z is not None:
            self.setz(z)
        self.setmax_dist(max_dist)

    def setz(self,z):
        assert self.length == len(z), "len(X) %d != len(z) %d" % (self.length, len(z))
        self.z = z

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
        
class interpoldln:
    from scipy.spatial import Delaunay
    from scipy.interpolate import LinearNDInterpolator
    def __init__(self,X,z=None,fill_value=np.NaN):
        self.tri = self.Delaunay(X)
        self.length = len(X)
        self.setfill_value(fill_value)
        if z is not None:
            self.setz(z)

    def setz(self,z):
        assert self.length == len(z), "len(X) %d != len(z) %d" % (self.length, len(z))
        self.z = z
        self.F = self.LinearNDInterpolator(self.tri, self.z, fill_value=self.fill_value)

    def setfill_value(self,fill_value):
        self.fill_value = fill_value

    def __call__(self,q):
        result = self.F(q)
        return result

if __name__ == "__main__":
    pass

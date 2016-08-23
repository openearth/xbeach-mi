import sub1
P=sub1.sub1module
import numpy as np
print P.aap(3)
(x,y) = P.noot(4)
print x
print y
x=np.array([1,2,3,4,5],dtype=np.int32)
P.mies(6,x)
print x
print type(x)
print x.dtype
P.xyz = 123


rx = P.rxyz()
print 'rx',rx
print 'rx',type(rx)

P.allocit(14)
xa = P.xarray
print 'xa',xa
P.xarray = np.zeros(len(xa))
P.xarray[5:7] = 21
P.getit(xa)
print 'xa',xa

sp = 'abcd'
s = np.array(sp)
t = np.array('a'*20)
P.modstring(s,t)
# f2py changes last character of string in chr(0):
ttt = t.tostring().replace(chr(0),' ').rstrip()
print 'ttt:['+ttt+']'

if 0:
    s = np.array(['abcde','abcde','abcde'],dtype='c').T
    print s
    print s.shape
    P.arraystring(s,5,3)

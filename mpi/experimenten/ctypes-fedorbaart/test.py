import numpy as np
from ctypes import (CDLL, POINTER, ARRAY, c_void_p,
                    c_int, byref,c_double, c_char,
                    c_char_p, create_string_buffer)
from numpy.ctypeslib import ndpointer
import os
 
dllpath = os.path.abspath("test.dylib") # or .dll or .so
libtest = CDLL(dllpath)
 
# Define some extra types
# pointer to a double
c_double_p = POINTER(c_double)
# pointer to a integer
c_int_p = POINTER(c_int)
 
shape2x2=(2,2)
# Pointer to a 2x2 double in fortran layout
c_double2x2_c = ndpointer(shape=shape2x2, dtype="double", flags="C")
c_double2x2_f = ndpointer(shape=shape2x2, dtype="double", flags="FORTRAN")
# Pointer to a pointer to a 10x10 double in fortran layout
c_double2x2_f_p = POINTER(c_double2x2_f)
c_double2x2_c_p = POINTER(c_double2x2_c)
shape3x2=(3,2)
shape2x3=(2,3)
# Pointer to a 2x3,3x2 double in fortran layout
c_double2x3_c = ndpointer(shape=shape2x3, dtype="double", flags="C")
c_double2x3_f = ndpointer(shape=shape2x3, dtype="double", flags="FORTRAN")
c_double3x2_c = ndpointer(shape=shape3x2, dtype="double", flags="C")
c_double3x2_f = ndpointer(shape=shape3x2, dtype="double", flags="FORTRAN")
# Pointer to a pointer to a 2x3,3x2 double in fortran layout
c_double2x3_f_p = POINTER(c_double2x3_f)
c_double2x3_c_p = POINTER(c_double2x3_c)
c_double3x2_f_p = POINTER(c_double3x2_f)
c_double3x2_c_p = POINTER(c_double3x2_c)
 
# Pointer to a character pointer
c_char_p_p = POINTER(c_char_p)
MAXSTRLEN=512
# Character array (Fortran can only return c_char arrays in c compatible mode)
c_char_array = ARRAY(c_char,MAXSTRLEN)
# Pointer to a character array
c_char_array_p = POINTER(c_char_array)
 
# oneint
f = libtest.oneint
f.argtypes=[c_int_p]
arg1 = c_int(1)
rc=f(byref(arg1))
print arg1.value
 
# onedouble
f = libtest.onedouble
f.argtypes=[c_double_p]
arg1 = c_double(1)
rc=f(byref(arg1))
print arg1.value
 
# 2x2
f = libtest.twobytwodouble
f.argtypes=[c_double2x2_f]
arg1 = np.zeros(shape2x2, order="F")
rc=f(arg1)
arr = np.array(arg1)
print arr
print arr.flags
 
 
# 2x2 p
f = libtest.twobytwodoublepointer
f.argtypes=[c_double2x2_c_p]
arg1 = c_double2x2_c()
rc=f(byref(arg1))
arr = np.array(arg1)
print arr
print arr.flags
 
# 2x3
f = libtest.twobythreedouble
f.argtypes=[c_double2x3_f]
arg1 = np.zeros(shape2x3,order="F")
rc=f(arg1)
arr = np.array(arg1)
print arr
print arr.flags
 
 
# 2x3 corresponds to 3x2 p in C order, reversed from F.
f = libtest.twobythreedoublepointer
f.argtypes=[c_double3x2_c_p]
arg1 = c_double3x2_c()
rc=f(byref(arg1))
arr = np.array(arg1, order="C")
print arr
print arr.flags
 
 
# Exchange one letter
f = libtest.letter
f.argtypes=[c_char_p]
arg1 = c_char('H')
rc=f(byref(arg1))
print arg1.value
 
# Exchange a string (in)
f = libtest.stringin
f.argtypes=[c_char_array_p]
arg1 = create_string_buffer('Hello from python',MAXSTRLEN)
rc=f(byref(arg1))
 
# Exchange a string (out)
f = libtest.stringout
f.argtypes=[c_char_array_p]
arg1 = create_string_buffer('',MAXSTRLEN)
rc=f(byref(arg1))
print arg1.value
 
 
del libtest

from mpi4py import MPI
import sys
import numpy as np
comm = MPI.COMM_WORLD
comm.Barrier()

if comm.rank == 0:
    print 'test with all processes:',comm.size

comm.Barrier()

x = np.array([[1.0,2.0,3.0],[5.0,6.0,7.0]],'d')


# print comm.rank,'x:',type(x),x
comm.Barrier()

if comm.rank == 0:
    y = np.zeros_like(x)
else:
    y = None


# do not: y=x, because we need a different memory location
# for y

# print comm.rank,'y:',type(y),y

try:
    #comm.Reduce([x, MPI.DOUBLE],[y,MPI.DOUBLE],op=MPI.SUM)
    comm.Reduce(x,y,op=MPI.SUM,root=0)
except Exception,e:
    print 'error in process',comm.rank,str(e)

comm.Barrier()

#if comm.rank == 0:
#    print y

comm.Barrier()
if comm.rank == 0:
    expect = comm.size*x
    result = expect-y
    print 'result (should be 0):' , result.sum()

comm.Barrier()

if comm.rank == 0:
    print 'test with 2 processes' 

member = (comm.rank < 2)
print comm.rank,'member',member

if not member:
    x = np.array([0])

if comm.rank == 0:
    y = np.zeros_like(x)
else:
    y = None

print comm.rank,'x',type(x),x

try:
    comm.Reduce(x,y,op=MPI.SUM,root=0)
except Exception,e:
    print 'error in process',comm.rank,str(e)


if comm.rank == 0:
    print comm.rank,'y',type(y),y
    expect = 2*x
    result = expect - y
    print 'result (should be 0):' , result.sum()


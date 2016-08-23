from mpi4py import MPI
import numpy as np

comm  = MPI.COMM_WORLD
fcomm = comm.py2f()
rank  = comm.rank

if rank < 2:
    color = 1
    x=1
    parmfile = "parmfile1"
else:
    color = 2
    x=2
    parmfile = "parmfile2"

comm1  = comm.Split(color,rank)
fcomm1 = comm1.py2f()

import sub
P = sub.submodule

P.subsub(fcomm1,x)

comm.Barrier()

rank1 = comm1.rank

if color == 1:
    s = P.summit(fcomm1,x)
elif color == 2:
    s = P.prod(fcomm1,x)

print 'sum',s,rank,rank1,color

comm.Barrier()

P.initialize_mpi(fcomm1,color)
comm.Barrier()
P.initialize(parmfile)
comm.Barrier()


for i in range(4):
    P.update(0.1)

comm.Barrier()
P.finalize()


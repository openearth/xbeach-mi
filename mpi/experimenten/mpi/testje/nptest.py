from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD

if comm.rank == 0:
    x = np.ones((2,3))
    print x
    print
else:
    x=None

x = comm.bcast(x)
comm.Barrier()
print comm.rank,x

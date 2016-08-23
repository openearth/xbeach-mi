#!/usr/bin/env python
# using bmiwrapper to communicate with 2 xbeach instances
# using mpi4py to create two processes, each running a 
# bmi-aware xbeach

from mpi4py import MPI
import sys
from bmi.wrapper import BMIWrapper
import numpy as np

def parentcode():
    comm = MPI.COMM_SELF.Spawn(sys.argv[0],
            args = 'xbeach-bmi-mpi-serial.py',
            maxprocs = 2)

def childcode():
    print 'size,rank:',comm.size,comm.rank

comm = MPI.COMM_WORLD
fcomm = np.array([comm.py2f()])
size = comm.size
if comm.rank == 0:
    print 'MPI initialized: size = ',size

if (MPI.Comm.Get_parent() == MPI.COMM_NULL):
    parentcode()
else:
    childcode()


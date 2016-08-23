#!/usr/bin/env python
#http://stackoverflow.com/questions/15271599/reduce-a-list-with-operator-as-summing-each-element-in-mpi4py
import numpy as np
from mpi4py import MPI
comm = MPI.COMM_WORLD

comm.Barrier()
t_start = MPI.Wtime()

# this array lives on each processor
data = np.zeros(5)
for i in xrange(comm.rank, len(data), comm.size):
    # set data in each array that is different for each processor
    data[i] = i

# print out the data arrays for each processor
print '[%i]'%comm.rank, data
comm.Barrier()

# the 'totals' array will hold the sum of each 'data' array
if comm.rank==0:
    # only processor 0 will actually get the data
    totals = np.zeros_like(data)
else:
    totals = None

# use MPI to get the totals 
comm.Reduce(
    [data, MPI.DOUBLE],
    [totals, MPI.DOUBLE],
    op = MPI.SUM,
    root = 0
)

# print out the 'totals'
# only processor 0 actually has the data
print '[%i]'%comm.rank, totals

comm.Barrier()
t_diff = MPI.Wtime() - t_start
if comm.rank==0: print t_diff

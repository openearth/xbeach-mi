# communication patterns
# start this program using:
#   mpiexec -n 5 python bmitest.py
#
# The import of mpi4py automatically initializes MPI, so from the
# beginning, n (5) processes are running in parallel.
# We start with: comm = MPI.COMM_WORLD, so communicator comm contains
# all processes (the number is specified after -n in the mpiexec call)
#
# comm is split into two communicators:
# 
#  - for processes with comm.rank < 2
#  - for processes with comm.rank >=2
# 
# In both groups, the new communicator is called comm1
#
# The simplified 'xbeach' is called 'sub' in this example.
# Two instances of sub are created: one for comm1 with processes
# with comm.rank < 2, and one for comm1 for the other processes
# In the example program we call these 'sub_instance'
# The sub instances will use comm1 as communicator.
# Before the 'initialize', the value of the mpi communicator
# to be used is defined, using 'set_var'.
# This not very neat, is there a possibility to do something properly
# before 'initialize'?
# 
# A communicator comm2 is created, which contains the processes
# for which comm1.rank == 0. For the other processes, comm2 is invalid.
# This communicator is used to communicate between the two instances of sub.
# For processes that are in comm2, talktosub is set to 1.
#
# Example, with in total 5 processes:
#
#  name  comm.rank comm1.rank comm2.rank sub_instance talktosub
#   A       0         0           0          1           1
#   B       1         1           n/a        1           0
#   C       2         0           1          2           1
#   D       3         1           n/a        2           0
#   E       4         2           n/a        2           0
#
# sub_instance 1 will read parmfile1 at initialization
# sub_instance 2 will read parmfile2 at initialization
#
# In the production version, a number of xbeach'es could be
# tied together.
# Probably, some convenience functions or variables would be desirable,
# for example to find out the correspondence between process numbers
# in different communicators and roles.
#
# In principle, this setup also will work with non-mpi-aware apps.
#

from mpi4py import MPI
import sys
from bmi.wrapper import BMIWrapper
import numpy as np
comm = MPI.COMM_WORLD
fcomm = np.array([comm.py2f()])
size = comm.size
if comm.rank == 0:
    print 'MPI initialized: size = ',size

# create communicator comm1:

if comm.rank < 2:
    sub_instance = 1
    parmfile = 'parmfile1'
else:
    sub_instance = 2
    parmfile = 'parmfile2'

comm1  = comm.Split(sub_instance,comm.rank)
fcomm1 = np.array([comm1.py2f()])
size1 = comm1.size
print 'sub_instance size1 rank1',sub_instance,size1,comm1.rank

# We use comm.Barrier toseparate the outputs of the different steps
# Ina real program they should be ommitted.

comm.Barrier()

w = BMIWrapper(engine='sub')

# set the communicators and instance numbers to be used 
# set_var has as side effect some extra initializations for MPI in sub

w.set_var('mpicomm',fcomm1)
w.set_var('instance',np.array([sub_instance]))

comm.Barrier()

w.initialize(parmfile)

comm.Barrier()

if comm1.rank == 0:
    talktosub = 1
else:
    talktosub = 0

for name in 'z','iz','nx','ny','time':
    # calling get_var in all processes, but expect the result
    # only in the talktosub processes
    arr = w.get_var(name)

    if talktosub == 1:
        print '------------',sub_instance,name,arr.shape
        if len(arr.shape) > 1:
            print arr[0,0],arr[5-1,4-1]
        else:
            print name,arr

comm.Barrier()

#create a communicator, containing the processes for which the rank
# in comm1 equals 0:


comm2  = comm.Split(talktosub,comm.rank)

comm.Barrier()

print 'rank,rank1,rank2:',comm.rank,comm1.rank,comm2.rank

meanz=np.array([-123.0])
for i  in range(5):
    comm.Barrier()
    w.update(0.1)

    # the z-values of processes in sub_instance=1 are incremented by the mean
    # of the z-values in sub_instance=2

    zarr = w.get_var('z')
    if talktosub == 1:
        print comm.rank,comm2.rank,'rank,rank2,meanz before:',meanz
        if comm2.rank == 1:
            meanz = np.array([zarr.mean()])
            comm2.Send(meanz,0,123)
        elif comm2.rank == 0:
            comm2.Recv(meanz,1,123)
            zarr = zarr + meanz
        # at this point, rank = 0 has the value of the modified z
        print comm.rank,comm2.rank,'rank,rank2,meanz after:',meanz
    if sub_instance == 1:
        w.set_var('z',zarr)
    
comm.Barrier()
print 'rank,meanz:',comm.rank,meanz[0]

comm.Barrier()

for name in 'z','iz','nx','ny','time':
    # calling get_var in all processes, but expect the result
    # only in the talktosub processes
    arr = w.get_var(name)

    if talktosub == 1:
        print '------------',sub_instance,name,arr.shape
        if len(arr.shape) > 1:
            print arr[0,0],arr[5-1,4-1]
        else:
            print name,arr

comm.Barrier()

w.finalize()

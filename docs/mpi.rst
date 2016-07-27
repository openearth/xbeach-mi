MPI
===

An MPI version of XBeach MI is being developed. This version can be
ran within an MPICH2 or OpenMPI wrapper. Individual XBeach models can
then be distributed over multiple cores for optimal performance.

The beta version of the MPI version can be found in a branch of the
GitHub repository:

https://github.com/openearth/xbeach-mi/tree/mpi

Examples
--------

.. code::

   mpirun -n 8 xbeach-mi xbeachmi.json

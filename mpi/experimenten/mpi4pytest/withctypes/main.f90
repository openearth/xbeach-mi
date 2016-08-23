program main
   use mpi
   implicit none
   integer ier
   call MPI_Init(ier)
   call subsub(MPI_COMM_WORLD)
   print *,'all done'
   call MPI_Finalize(ier)
end program main

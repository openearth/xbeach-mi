program main
   use mpi
   use submodule
   implicit none
   integer ier,irank
   call MPI_Init(ier)
   call subsub(MPI_COMM_WORLD,123)
   call MPI_Comm_rank(MPI_COMM_WORLD,irank,ier)
   call MPI_Barrier(MPI_COMM_WORLD,ier)
   if (irank .eq. 0) then
      print *,'all done'
   endif
   call MPI_Finalize(ier)
end program main

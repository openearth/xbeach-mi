module timestepmodule
   use mpi
   use datamodule
   implicit none
   save
contains
   subroutine timestep(dt)
      real*8, intent(in) :: dt

      integer ier
      ! for some reason: updating is done by process 1,
      ! the result is broadcasted
      if (globalrank .eq. 1) then
         globalz = globalzz + globalz+dt*size(globalz)
      endif
      call MPI_Bcast(globalz,size(globalz),MPI_DOUBLE_PRECISION,1,globalcomm,ier)
      if (globalrank .eq. 0) then
         print *,globalcolor,': dt: ',dt,'lastz: ',globalz(globalx,globaly)
      endif
   end subroutine timestep
end module timestepmodule

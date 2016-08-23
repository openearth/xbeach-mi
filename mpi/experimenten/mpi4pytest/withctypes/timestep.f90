module timestepmodule
   use mpi
   use datamodule
   implicit none
contains
   subroutine timestep(dt)
      real*8, intent(in) :: dt
      integer ier,i,j
      ! as an example, updating is done by process 1,
      ! the result is broadcasted
      if (globalrank .eq. 1) then
         do i=2,globalx
            do j=2,globaly
               globalz(i,j) = globalz(i,j) + &
                  &(globalz(i-1,j)+globalz(i,j-1)+globalz(i-1,j-1))*0.1d0
            enddo
         enddo
      endif
      call MPI_Bcast(globalz,size(globalz),MPI_DOUBLE_PRECISION,1,globalcomm,ier)
      if (globalrank .eq. 0) then
         print *,globalinstance,': dt: ',dt,'lastz: ',globalz(globalx,globaly)
      endif
      globaltime = globaltime + dt
   end subroutine timestep
end module timestepmodule

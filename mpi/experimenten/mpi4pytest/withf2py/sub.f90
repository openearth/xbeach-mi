module submodule
   use mpi
   use datamodule
   implicit none
   save
contains
   subroutine subsub(comm,x)
      use mpi
      implicit none
      integer, intent(in) :: comm
      integer, intent(in) :: x
      integer ier, irank, isize
      call MPI_Comm_rank(comm,irank,ier)
      call MPI_Comm_size(comm,isize,ier)
      print *,isize,x
      return
   end subroutine subsub
   integer function summit(comm,x)
      use mpi
      implicit none
      integer, intent(in) :: comm
      integer, intent(in) :: x
      integer ier
      integer y
      y = -1
      call MPI_Reduce(x,y,1,MPI_INTEGER,MPI_SUM,0,comm,ier)
      summit = y
      return
   end function summit

   integer function prod(comm,x)
      use mpi
      implicit none
      integer, intent(in) :: comm
      integer, intent(in) :: x
      integer ier
      integer y
      y = -1
      call MPI_Reduce(x,y,1,MPI_INTEGER,MPI_PROD,0,comm,ier)
      prod = y
      return
   end function prod

   subroutine initialize_mpi(comm,color)
      implicit none
      integer, intent(in) :: comm,color

      integer ier

      globalcomm = comm
      globalcolor = color
      call MPI_Comm_rank(globalcomm, globalrank,ier)

      print *,globalcolor,globalrank,'initialized'

   end subroutine initialize_mpi

   subroutine initialize(s)
      implicit none
      character(*), intent(in) :: s

      integer ier

      if(globalrank .eq.0) then
         open(14,file=s)
         read(14,*),globalx, globaly
         close(14)
      endif
      call MPI_Bcast(globalx,1,MPI_INTEGER,0,globalcomm,ier)
      call MPI_Bcast(globaly,1,MPI_INTEGER,0,globalcomm,ier)
      allocate(globalz(globalx,globaly))
      allocate(globalzz(globalx,globaly))
      globalz = 1
      globalzz = 0
      print *,'initialize',globalcolor,globalrank,globalx,globaly
   end subroutine initialize

   subroutine update(dt)
      use timestepmodule
      implicit none
      real*8, intent(in) :: dt

      real*8 mydt
      if (dt < 0) then
         mydt = 0.1
      else
         mydt = dt
      endif

      call timestep(mydt)

   end subroutine update

   subroutine get_var(s,x)
      implicit none
      character(*) :: s
      real*8, intent(out) :: x(:)

      x = 10
      
   end subroutine get_var

   subroutine finalize()
      if (globalrank .eq. 0)then
         print *,globalcolor,': finalized'
      endif
   end subroutine finalize

end module submodule

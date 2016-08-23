module submodule
   use iso_c_binding
   use mpi
   use datamodule
   use timestepmodule
   use constantsmodule
   use iso_c_utils
   implicit none
   save
contains

   subroutine initialize(s) bind(C, name='initialize')
      implicit none
      character(c_char), intent(in) :: s(*)

      character(1024) :: parmfile
      integer ier

      parmfile = char_array_to_string(s)

      if(globalrank .eq.0) then
         open(14,file=parmfile)
         read(14,*),globalx, globaly
         close(14)
      endif
      call MPI_Bcast(globalx,1,MPI_INTEGER,0,globalcomm,ier)
      call MPI_Bcast(globaly,1,MPI_INTEGER,0,globalcomm,ier)
      allocate(globalz(globalx,globaly))
      allocate(globaliz(globalx,globaly))
      globalz = -123
      globaliz = 123
      globalz(4,5) = 12345
      globaliz(4,5) = 12345
      print *,'initialize',globalinstance,globalrank,globalx,globaly
   end subroutine initialize

   integer(c_int) function update(dt) bind(C, name='update')
      implicit none
      real(c_double), value, intent(in) :: dt

      real*8 mydt
      if (dt < 0) then
         mydt = 0.1
      else
         mydt = dt
      endif

      call timestep(mydt)
      update = 0
   end function update

   integer(c_int) function finalize() bind(C, name='finalize')
      if (globalrank .eq. 0)then
         print *,globalinstance,': finalized'
      endif
      finalize = 0
   end function finalize


   subroutine get_var_type(var_name,type_name) bind(C, name='get_var_type')
      implicit none
      character(c_char), intent(in)  :: var_name(*)
      character(c_char), intent(out) :: type_name(MAXSTRINGLEN)

      character(strlen(var_name)) :: sname
      character(MAXSTRINGLEN)     :: stype

      sname = char_array_to_string(var_name)

      select case(sname)
       case('z')
         stype = 'double'
       case('time')
         stype = 'double'
       case('iz')
         stype = 'int'
       case('nx')
         stype = 'int'
       case('ny')
         stype = 'int'
      end select

      type_name = string_to_char_array(trim(stype))

   end subroutine get_var_type


   subroutine get_var_rank(c_var_name, rank) bind(C, name='get_var_rank')
      implicit none
      character(c_char), intent(in) :: c_var_name(*)
      integer(c_int), intent(out) :: rank
      character(len=strlen(c_var_name)) :: var_name

      var_name = char_array_to_string(c_var_name)

      select case(var_name)
       case('z','iz')
          rank = 2
       case('time','nx','ny')
          rank = 0
      end select
   end subroutine get_var_rank

   subroutine get_var_shape(c_var_name, shape) bind(C, name="get_var_shape")

      character(kind=c_char), intent(in) :: c_var_name(*)
      integer(c_int), intent(inout) :: shape(MAXDIMS)

      character(len=strlen(c_var_name)) :: var_name

      var_name = char_array_to_string(c_var_name)
      shape = (/0, 0, 0, 0, 0, 0/)

      select case(var_name)

       case('z','iz')
         ! return in c memory order
         shape(2) = globalx
         ! return in c memory order
         shape(1) = globaly
      case('time','nx','ny')
         shape(1) = 0
      end select

   end subroutine get_var_shape


   subroutine get_var(var_name,x) bind(C, name='get_var')
      ! In reality, this subroutine would collect the distributed
      ! arrays. As a substitute, we call MPI_Barrier to make sure that
      ! all needed processes are involved. 
      ! If not: this subroutine will hang
      implicit none
      character(c_char), intent(in) :: var_name(*)
      type(c_ptr), intent(inout) :: x

      character(strlen(var_name)) :: sname
      integer ier

      call MPI_Barrier(globalcomm,ier)

      sname = char_array_to_string(var_name)
      select case(sname)
       case('z')
         x = c_loc(globalz(1,1))
       case('time')
         x = c_loc(globaltime)
       case('iz')
         x = c_loc(globaliz(1,1))
       case('nx')
         x = c_loc(globalx)
       case('ny')
         x = c_loc(globaly)
      end select

   end subroutine get_var

   subroutine set_var(c_var_name,xptr) bind(C,name='set_var')
      ! In reality, this subroutine would distribute the global
      ! arrays. As a substitute, we call MPI_Barrier to make sure that
      ! all needed processes are involved. 
      ! If not: this subroutine will hang
      use iso_c_binding, only: c_double, c_char, c_loc, c_f_pointer
      implicit none
      character(kind=c_char), intent(in) :: c_var_name(*)
      type(c_ptr), value, intent(in) :: xptr

      character(len=strlen(c_var_name)) :: var_name
      real(c_double), pointer :: x_0d_double_ptr
!      real(c_double), pointer :: x_1d_double_ptr(:)
      real(c_double), pointer :: x_2d_double_ptr(:,:)
!      real(c_double), pointer :: x_3d_double_ptr(:,:,:)
!      real(c_double), pointer :: x_4d_double_ptr(:,:,:,:)
      integer(c_int), pointer :: x_0d_int_ptr
!      integer(c_int), pointer :: x_1d_int_ptr(:)
      integer(c_int), pointer :: x_2d_int_ptr(:,:)

      integer ier

      var_name = char_array_to_string(c_var_name)


      select case(var_name)
       case('mpicomm')
         call c_f_pointer(xptr,x_0d_int_ptr,shape(globalcomm))
         globalcomm = x_0d_int_ptr
         call MPI_Comm_rank(globalcomm,globalrank,ier)
         call MPI_Comm_size(globalcomm,globalsize,ier)
       case('instance')
         call c_f_pointer(xptr,x_0d_int_ptr,shape(globalinstance))
         globalinstance = x_0d_int_ptr
         print *,'sub: instance size rank:',globalinstance,globalsize,globalrank

       case('z')
         if (globalrank == 0) then
            print *,'sub: z(1,1:3) before:',globalz(1,1:3)
            call c_f_pointer(xptr,x_2d_double_ptr,shape(globalz))
            globalz = x_2d_double_ptr
            print *,'sub: z(1,1:3) after:',globalz(1,1:3)
         endif
         call MPI_Bcast(globalz,size(globalz),MPI_DOUBLE_PRECISION,0,globalcomm,ier)
       case('iz')
         if (globalrank == 0) then
            call c_f_pointer(xptr,x_2d_int_ptr,shape(globaliz))
            globaliz = x_2d_int_ptr
         endif
         call MPI_Bcast(globaliz,size(globaliz),MPI_INTEGER,0,globalcomm,ier)
       case('time')
         if (globalrank == 0) then
            call c_f_pointer(xptr,x_0d_double_ptr,shape(globaltime))
            globaltime = x_0d_double_ptr
         endif
         call MPI_Bcast(globaltime,1,MPI_DOUBLE_PRECISION,0,globalcomm,ier)
       case('nx')
         if (globalrank == 0) then
            call c_f_pointer(xptr,x_0d_int_ptr,shape(globalx))
            globalx = x_0d_int_ptr
         endif
         call MPI_Bcast(globalx,1,MPI_INTEGER,0,globalcomm,ier)
       case('ny')
         if (globalrank == 0) then
            call c_f_pointer(xptr,x_0d_int_ptr,shape(globaly))
            globaly = x_0d_int_ptr
         endif
         call MPI_Bcast(globaly,1,MPI_INTEGER,0,globalcomm,ier)
      end select

      call MPI_Barrier(globalcomm,ier)

   end subroutine set_var

end module submodule

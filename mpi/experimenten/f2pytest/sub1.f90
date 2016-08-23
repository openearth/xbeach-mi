module sub1module
   implicit none
   save

   integer xyz
   integer, allocatable :: xarray(:)

contains

   integer function aap(x)
      integer, intent(in) :: x
      aap = 10*x
      return
   end function aap

   subroutine noot(a,x,y)
      integer, intent(in)  :: a
      integer, intent(out) :: x,y
      x = a*10
      y = a+10
   end subroutine noot

   subroutine mies(a,x)
      integer, intent(inout) :: x(:)
      integer, intent(in) :: a
      x = a*x
   end subroutine mies

   integer function rxyz()
      rxyz = xyz
   end function rxyz

   subroutine allocit(n)
      integer, intent(in) :: n
      integer i
      allocate(xarray(n))
      do i=1,n
         xarray(i) = i
      enddo

   end subroutine allocit

   subroutine getit(x)
      integer, intent(inout) :: x(:)
      x = xarray
   end subroutine getit

   subroutine modstring(s,t)
      implicit none
      character(*), intent(in)    :: s
      character(*), intent(inout) :: t

      print *,'modstring s:',s,len(s)
      print *,'modstring t:',t,len(t)
      t = s // s
      print *,'modstring t:',t,len(t)
   end subroutine modstring

   subroutine string2array(s,a)
      implicit none
      character(*), intent(in) :: s
      character, intent(inout) :: a(:)

      integer i
      do i=1,min(len(s),size(a))
         a(i) = s(i:i)
      enddo
   end subroutine string2array

   subroutine arraystring(s,ls,ns)
      implicit none
      character, intent(inout) :: s(ls,ns)
      integer, intent(in) :: ls,ns
      print *,s(1,:)
   end subroutine arraystring

end module sub1module

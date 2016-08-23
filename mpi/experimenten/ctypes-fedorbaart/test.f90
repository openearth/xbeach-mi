module test
use iso_c_binding
implicit none
integer, parameter :: MAXSTRLEN = 512
contains
 
! Utility functions
! fortran character(len=*) are not compatible with c
! To be compatible with c, strings sould be copied to a c_char array
function char_array_to_string(char_array, length)
  integer(c_int) :: length
  character(c_char) :: char_array(length)
  character(len=length) :: char_array_to_string
  integer :: i
  do i = 1, length
     char_array_to_string(i:i) = char_array(i)
  enddo
end function char_array_to_string
 
! C ends strings with a \0 character. Add this so it is received correctly in c compatible languages
function string_to_char_array(s, length)
  integer(c_int) :: length
  character :: s(*)
  character(c_char) :: string_to_char_array(length)
  integer :: i
  do i = 1, length
     string_to_char_array(i:i) = s(i)
  enddo
  string_to_char_array(i+1:i+1) = C_NULL_CHAR
end function string_to_char_array
 
 
 
! 1 int
integer(c_int) function oneint(arg1) bind(C, name="oneint")
  integer(c_int), intent(inout) :: arg1
  arg1 = 111
  oneint = 123
end function oneint
 
! 1 double
integer(c_int) function onedouble(arg1) bind(C, name="onedouble")
  real(c_double), intent(inout) :: arg1
  arg1 = 1.11d0
  onedouble = 123
end function onedouble
 
 
! 10by10 double
integer(c_int) function twobytwodouble(x) bind(C, name="twobytwodouble")
  real(c_double),intent(inout)  :: x(2,2)
  x = 4
  x(2,1) = 21
  x(1,2) = 12
  twobytwodouble = 123
end function twobytwodouble
 
 
! 10by10 double
integer(c_int) function twobythreedouble(x) bind(C, name="twobythreedouble")
  real(c_double),intent(inout)  :: x(2,3)
  x = 6
  x(2,1) = 21
  x(1,3) = 13
  twobythreedouble = 123
end function twobythreedouble
 
integer(c_int) function twobytwodoublepointer(ptr) bind(C, name="twobytwodoublepointer")
  type(c_ptr), intent(inout) :: ptr
  real(c_double), target, save  :: x(2,2)
 
  x = 4
  x(2,1) = 21
  x(1,2) = 12
  ptr=c_loc(x)
  twobytwodoublepointer = 123
end function twobytwodoublepointer
 
 
! 10by10 double pointer
integer(c_int) function twobythreedoublepointer(ptr) bind(C, name="twobythreedoublepointer")
  type(c_ptr), intent(inout) :: ptr
  ! Save is required here for the memory to remain available after the function call
  real(c_double), target, save  :: x(2,3)
  x = 6
  x(2,1) = 21
  x(1,3) = 13
  ptr = c_loc(x)
  twobythreedoublepointer = 123
end function twobythreedoublepointer
 
! character
integer(c_int) function letter(arg1) bind(C, name="letter")
  character(kind=c_char), intent(inout) :: arg1
  arg1 = 'W'
  letter = 123
end function letter
 
! string in (string in length is not fixed but internally you need to set a fixed string length)
integer(c_int) function stringin(arg1) bind(C, name="stringin")
  character(kind=c_char), intent(in) :: arg1(*)
  character(len=MAXSTRLEN) :: string
  string = char_array_to_string(arg1, MAXSTRLEN)
  write(*,*)string
  stringin = 123
end function stringin
 
! string out (requires fixed number of letters)
integer(c_int) function stringout(arg1) bind(C, name="stringout")
  ! Output string has to be fixed
  character(kind=c_char), intent(out) :: arg1(MAXSTRLEN)
  character(len=MAXSTRLEN) :: string
  string = "Hello from fortran"
  arg1 = string_to_char_array(string, len(trim(string)))
  stringout = 123
end function stringout
 
 
end module test

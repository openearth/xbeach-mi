integer(c_int) function t() bind(C, name='t')
   use iso_c_binding
   print *,'hallo'
   t=0
end function t

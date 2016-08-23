module datamodule
   use iso_c_binding
   save
   integer(c_int),target :: globalx,globaly
   integer globalcomm,globalrank,globalinstance,globalsize
   real(c_double),  allocatable, target :: globalz (:,:)
   integer(c_int),  allocatable, target :: globaliz(:,:)
   character(20), allocatable :: input_var_names(:)
   real*8, target :: globaltime
end module datamodule

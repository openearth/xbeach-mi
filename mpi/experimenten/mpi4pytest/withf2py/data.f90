module datamodule
   use mytypemodule
   implicit none
   save
   integer globalx,globaly
   integer globalcomm,globalrank,globalcolor
   real*8, allocatable:: globalz(:,:)
   real*8, allocatable:: globalzz(:,:)
end module datamodule

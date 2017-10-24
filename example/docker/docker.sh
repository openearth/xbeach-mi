#!/bin/bash

workingdir=`pwd`
instances=( "$@" )

docker network create XBEACHMI
docker run \
       --volume ${workingdir}:/data \
       --network XBEACHMI \
       deltares/xbeach-mi xbeach-mi-prepare config.json

for i in "${!instances[@]}"
do
    
    port=$(expr 53606 + 3 \* $i)
    
    docker create \
           --volume ${workingdir}"/."${instances[$i]}":/data" \
           --network XBEACHMI \
           --env PORT=${port} \
           deltares/xbeach
    
    docker start $(docker ps -lq)
    
done

docker create \
       --volume ${workingdir}":/data" \
       deltares/xbeach-mi xbeach-mi config.json

docker start $(docker ps -lq)

docker network rm XBEACHMI

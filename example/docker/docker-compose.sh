#!/bin/bash

workingdir=`pwd`
instances=( "$@" )

NAME="docker-compose-xbeachmi.yml"

echo "version: \"3\"" > $NAME
echo "services:" >> $NAME
echo "  xbeach-preparation:" >> $NAME
echo "    image: deltares/xbeach-mi" >> $NAME
echo "    volumes:" >> $NAME
echo "      - ./:/data" >> $NAME
echo "    command: xbeach-mi-prepare config.json" >> $NAME
echo "  xbeach-orchestrator:" >> $NAME
echo "    image: deltares/xbeach-mi" >> $NAME
echo "    depends_on:" >> $NAME

for i in "${!instances[@]}"
do
    
    port=$(expr 53606 + 3 \* $i)
    
    echo "      - ${instances[$i]}" >> $NAME

done

echo "    volumes:" >> $NAME
echo "      - ./:/data" >> $NAME

for i in "${!instances[@]}"
do
    
    port=$(expr 53606 + 3 \* $i)

    echo "  ${instances[$i]}:" >> $NAME
    echo "    image: deltares/xbeach" >> $NAME
    echo "    depends_on:" >> $NAME
    echo "      - xbeach-preparation" >> $NAME
    echo "    environment:" >> $NAME
    echo "      - PORT=$port" >> $NAME
    echo "    volumes:" >> $NAME
    echo "      - .${instances[$i]}/:/data" >> $NAME

done

docker-compose -f $NAME up

#!/bin/bash

container_id=$(docker ps -aqf "name=i2b2-etl")

if [ ! -z ${container_id} ]
then
    echo "Deleting already running etl container : $(docker rm -f $container_id)"
fi

docker-compose -f docker-compose-i2b2-etl.yml up -d

# Add etl function to ~/.bashrc and source ~/.bashrc
grep -q 'i2b2-etl' ~/.bashrc || echo -e 'etl() { \n ARGS="$@" \n docker exec -it i2b2-etl bash -c "python -m i2b2_cdi.loader.i2b2_cdi_loader ${ARGS}" \n}\n' >> ~/.bashrc
source ~/.bashrc
exec bash

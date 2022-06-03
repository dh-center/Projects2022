#!/bin/bash

set -e

# if you run postgres first time (to create volume)
# ./database/run_postgres_secured.sh
# apply dump from backup_postgres.sh

docker-compose down
git fetch
git reset --hard origin/master
docker-compose up --build -d

# start extractor (should be started inside of container)
docker exec -it one_media_tlg_extractor /bin/bash
# inside container
# ./run_in_container.sh
# exit

# check logs
docker-compose logs -f


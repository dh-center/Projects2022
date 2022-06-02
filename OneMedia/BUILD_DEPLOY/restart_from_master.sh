#!/bin/bash

set -e
set -x

echo "====================Restart is started!=============================="
echo "====================Stopping old components!========================="

docker-compose down

echo "====================All components are down!========================="
echo "====================Fetch master!===================================="

git fetch
git reset --hard origin/master

echo "====================Rebuild search!==================================="

(cd search && ./build_jar.sh)

echo "====================Rebuild UI!==================================="

(cd ui && ./build_jar.sh)

echo "====================Start all containers!============================="

docker-compose up -d --build

echo "==========================COMPLETED!=================================="

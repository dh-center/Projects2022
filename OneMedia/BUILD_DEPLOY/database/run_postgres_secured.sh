#!/bin/bash

# DO NOT FORGET CHMOD 777 on volume files, otherwise it will not work!!!
sudo mkdir ./sql_scripts/volume
sudo chmod 777 ./sql_scripts/volume/*
sudo chmod 777 ./sql_scripts/volume
docker-compose up --remove-orphans -d one_media_db

# to remove database
# docker-compose down
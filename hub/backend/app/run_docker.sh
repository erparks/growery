#!/bin/bash

docker build -t hub_image -f ../docker/app/Dockerfile .
docker run -it hub_image
#!/bin/bash
source .env
docker -H ${DOCKER_HOST} compose -f docker/compose.yaml up --build -d
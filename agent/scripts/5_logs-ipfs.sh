#!/bin/bash
source .env

docker_cmd() {
    if [ -n "${DOCKER_HOST}" ]; then
        docker -H ${DOCKER_HOST} "$@"
    else
        docker "$@"
    fi
}

docker_cmd logs ipfs-node --follow
#!/bin/bash
source .env

docker_cmd() {
    if [ -n "${DOCKER_HOST}" ]; then
        docker -H ${DOCKER_HOST} "$@"
    else
        docker "$@"
    fi
}

docker_cmd compose -f docker/compose.yaml down -v
./scripts/3_deploy-agent.sh
./scripts/4_logs-agent.sh
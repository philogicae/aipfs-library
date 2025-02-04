#!/bin/bash
source .env
docker -H ${DOCKER_HOST} logs aipfs-agent-backend --follow
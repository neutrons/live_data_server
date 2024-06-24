#!/bin/bash

MINIMUM_VERSION_NUMBER=1.27  # minimum valid version of docker-compose file

DOCKER_COMPOSE=$1  # path to docker-compose command
version=$(${DOCKER_COMPOSE} --version | sed -ne 's/[^0-9]*\(\([0-9]\.\)\{0,4\}[0-9][^.]\).*/\1/p')

function version_validate {
    # return 0 if first greater or equal than second, otherwise return 1
    local a=$1 b=$2 x y
    while [[ $a || $b ]]; do
        x=${a%%.*} y=${b%%.*}
        [[ "10#${x:-0}" -gt "10#${y:-0}" ]] && return 0
        [[ "10#${x:-0}" -lt "10#${y:-0}" ]] && return 1
        a=${a:${#x} + 1} b=${b:${#y} + 1}
    done
    return 0
}

version_validate $version ${MINIMUM_VERSION_NUMBER}
valid=$?

test $valid -eq 1 && echo "Error: Invalid docker-compose. Minimum valid version is ${MINIMUM_VERSION_NUMBER}"
exit $valid

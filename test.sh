if [[ $(docker compose version 2>/dev/null) != "" ]]; then
    DOCKER_COMPOSE="docker compose"
elif [[ $(docker-compose version 2>/dev/null) != "" ]]; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "docker compose or docker-compose is not installed"
    exit 1
fi

$DOCKER_COMPOSE version

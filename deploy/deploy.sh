#!/bin/bash

source $HOME/.config/turplanlegger/env
NEW_SHA=$(curl -sH "Authorization: Bearer $GITHUB_ACCESS_TOKEN" https://api.github.com/user/packages/container/turplanlegger-api/versions | jq -r '.[] | select(.metadata.container.tags[] | contains("main")).name'
)
OLD_SHA=$(docker image inspect ghcr.io/sixcare/turplanlegger-api:main --format '{{json .RepoDigests}}' | jq .[0] | cut -d'@' -f2 | cut -d'"' -f1)

if [ $NEW_SHA != $OLD_SHA ]; then
    cd $HOME/turplanlegger-api
    curl -fsLO https://raw.githubusercontent.com/sixcare/turplanlegger-api/main/docker-compose.yml
    docker compose pull
    docker compose --env-file $HOME/.config/turplanlegger/env up -d
fi

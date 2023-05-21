#!/bin/bash

set -e

# Source environment variables
source "${HOME}/.config/turplanlegger/env"

# Get the SHA of the new image
NEW_SHA=$(curl -sH "Authorization: Bearer ${GITHUB_ACCESS_TOKEN}" "https://api.github.com/user/packages/container/turplanlegger-api/versions" | jq -r '.[] | select(.metadata.container.tags[] | contains("main")).name')
if [[ -z "${NEW_SHA}" ]]; then
    echo "Unable to retrieve the new image SHA"
    exit 1
fi

# Get the SHA of the old image
OLD_SHA=$(docker image inspect ghcr.io/sixcare/turplanlegger-api:main --format '{{.Id}}')
if [[ -z "${OLD_SHA}" ]]; then
    echo "Unable to retrieve the old image SHA"
    exit 1
fi

# Compare SHAs and update the image if necessary
if [[ "${NEW_SHA}" != "${OLD_SHA}" ]]; then
    cd "${HOME}/turplanlegger-api"
    
    # Backup current docker-compose file
    cp docker-compose.yml docker-compose.yml.bak
    
    # Download new docker-compose file
    if ! curl -fsLO "https://raw.githubusercontent.com/sixcare/turplanlegger-api/main/docker-compose.yml"; then
        echo "Failed to download docker-compose file, reverting to backup"
        mv docker-compose.yml.bak docker-compose.yml
        exit 1
    fi
    
    # Pull new images
    if ! docker compose pull; then
        echo "Failed to pull new Docker images"
        exit 1
    fi

    # Restart services
    docker compose --env-file "${HOME}/.config/turplanlegger/env" up -d
else
    echo "No new updates available"
fi

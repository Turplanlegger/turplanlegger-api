#!/bin/bash

set -e

# Define variables
ENV_FILE="${HOME}/.config/turplanlegger/env-develop"
REPO_DIR="${HOME}/turplanlegger-api-develop/"
COMPOSE_FILE="${REPO_DIR}/docker-compose.dev.yml"

if ! git -C "$REPO_DIR" rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    printf "Not a git directory. Please ensure it is.\n"
    exit 1
fi

if [[ -f "$ENV_FILE" ]]; then
    source "$ENV_FILE"
else
    printf "Environment file not found: %s\n" "$ENV_FILE"
    exit 1
fi

if [[ -z $GITHUB_ACCESS_TOKEN ]]: then
    printf "GITHUB_ACCESS_TOKEN not defined \n"
    exit 1
fi

# Retrieve the latest commit SHA from the GitHub API
NEW_SHA=$(curl -sH "Authorization: Bearer ${GITHUB_ACCESS_TOKEN}" "https://api.github.com/repos/Turplanlegger/turplanlegger-api/commits?per_page=1&sha=develop" | jq -r '.[0].sha')

OLD_SHA=$(git -C "$REPO_DIR" log -n 1 --format=format:%H)

if [[ -z "$NEW_SHA" ]]; then
    printf "Unable to retrieve the new commit SHA\n"
    exit 1
fi

if [[ -z "$OLD_SHA" ]]; then
    printf "Unable to retrieve the old commit SHA\n"
    exit 1
fi

if [[ "$NEW_SHA" != "$OLD_SHA" ]]; then
    # Fetch the latest changes from the remote develop branch
    git -C "$REPO_DIR" fetch --force --prune --prune-tags --quiet
    git -C "$REPO_DIR" reset --quiet --hard origin/develop

    # Build and start Docker containers
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build --quiet
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --quiet-pull --remove-orphans
fi

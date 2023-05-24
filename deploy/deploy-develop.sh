#!/bin/bash

set -e

source "${HOME}/.config/turplanlegger/env-develop"

cd "${HOME}/turplanlegger-api-develop/"

if ! git rev-parse --quiet --is-inside-work-treee > /dev/null 2>&1; then
    printf "Not a git directory. Ensure it is\n"
    exit 1
fi

NEW_SHA=$(curl -sH "Authorization: Bearer ${GITHUB_ACCESS_TOKEN}" 'https://api.github.com/repos/sixcare/turplanlegger-api/commits?per_page=1&sha=develop' | jq -r .[0].sha)
OLD_SHA=$(git log -n 1 --format=format:%H)

if [[ -z "${NEW_SHA}" ]]; then
    printf "Unable to retrieve the new commit SHA\n"
    exit 1
fi

if [[ -z "${OLD_SHA}" ]]; then
    printf "Unable to retrieve the old commit SHA\n"
    exit 1
fi

if [[ "${NEW_SHA}" != "${OLD_SHA}" ]]; then
    git fetch --force --prune --prune-tags --quiet
    git reset --quiet --hard origin/develop
    docker compose --env-file "${HOME}/.config/turplanlegger/env-develop" -f docker-compose.dev.yml build --quiet
    docker compose --env-file "${HOME}/.config/turplanlegger/env-develop" -f docker-compose.dev.yml up -d --quiet-pull --remove-orphans
fi

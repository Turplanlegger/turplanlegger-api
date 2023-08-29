#!/bin/bash

set -e

if [[ -z "$API_URL" ]]; then
    printf "API_URL is not defined\n"
    exit 1
fi

VERSION=$(grep __version__  ./turplanlegger/__about__.py | cut -d "'" -f 2)
printf "Repo version: $VERSION\n"

API_VERSION=$(curl -sf $API_URL/version | jq -r .version)
printf "Deployed version: $API_VERSION\n"

COUNT=0
while [[ "$COUNT" -lt "16" ]]; do
    API_VERSION=$(curl -sf $API_URL/version | jq -r .version)
    if [ "$API_VERSION" == "$VERSION" ]; then
        printf "Hurra 🎉 New version is deployed: $API_VERSION \n"
        exit 0
    fi
    COUNT=$(( $COUNT + 1 ))
    printf "Retry attempt $COUNT/16\n"
    sleep 15
done

printf "Huffda! Deploy failed 🤕\n"
exit 1

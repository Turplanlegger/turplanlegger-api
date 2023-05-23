#!/bin/bash

set -e

VERSION=$(grep __version__  ./turplanlegger/__about__.py | cut -d "'" -f 2)
printf "Repo version: $VERSION\n"
COUNT=0
while [[ "$COUNT" -lt "16" ]]; do
    API_VERSION=$(curl -sf https://turplanlegger.sixca.re/version | jq -r .version)
    printf "Deployed version: $API_VERSION\n"

    if [ "$API_VERSION" == "$VERSION" ]; then
        printf "Hurra! New version is deployed 🎉\n"
        exit 0
    fi
    COUNT=$(( $COUNT + 1 ))
    printf "Retry attempt $COUNT/16\n"
    sleep 15
done

printf "Huffda! Deploy failed 🤕\n"
exit 1
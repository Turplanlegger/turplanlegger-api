import os
import time

import jwt
import requests

private_key = os.environ.get('PRIVATE_KEY')
if private_key is None:
    print('PRIVATE_KEY is not set')
    exit(1)

app_id = os.environ.get('APP_ID')
if app_id is None:
    print('APP_ID is not set')
    exit(1)

installation_id = os.environ.get('INSTALLATION_ID')
if installation_id is None:
    print('INSTALLATION_ID is not set')
    exit(1)

payload = {
    'iat': int(time.time()),
    'exp': int(time.time()) + 60,
    'iss': app_id
}

try:
    encoded_jwt = jwt.encode(payload, private_key.encode(), algorithm='RS256')
except jwt.exceptions as e:
    print('Failed to generate JWT')
    print(e)
    exit(1)

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {encoded_jwt}',
    'X-GitHub-Api-Version': '2022-11-28',
}

try:
    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers=headers,
    )
    response.raise_for_status()
except requests.HTTPError as e:
    print('Failed to generate access token')
    print(e)
    exit(1)

try:
    token = response.json().get('token')
except requests.JSONDecodeError as e:
    print('Failed to extract token')
    print(e)
    exit(1)

print(f'TOKEN={token}')


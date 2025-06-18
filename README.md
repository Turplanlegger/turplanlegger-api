# Turplanlegger
Python API for planning trips

## Install
```bash
pip install .
```

### Production
```bash
pip install '.[prod]'
```

### Development
```bash
pip install '.[dev]'
```

## Testing
Run test:
```
pip install pytest
pytest tests/test_*.py`
```

## Building and publishing.
Editing the [\_\_about__.py](turplanlegger/__about__.py) file will trigger a GitHub Action that creates a new version tag.  
After a new version tag is avaiable on GitHub, the new version will be built by GitHub Actions and a new release is published.

## Docker

### Deploy script
Prerequisite: A GitHub API token with the scope `read:packages` is required for the script to work

Add a cronjob that runs the deploy script:
```console
mkdir ~/turplanlegger-api
mkdir -p ~/.config/turplanlegger
curl -o ~/turplanlegger-api/deploy.sh https://raw.githubusercontent.com/Turplanlegger/turplanlegger-api/latest/deploy/deploy.sh
chmod +x ~/turplanlegger-api/deploy.sh
curl -o ~/.config/turplanlegger/env https://raw.githubusercontent.com/Turplanlegger/turplanlegger-api/latest/deploy/env
chmod 600 ~/.config/turplanlegger/env
# Add Github access token, secret key and secret key id to env file
crontab -l | { cat; echo "*/2 * * * * $HOME/turplanlegger-api/deploy.sh > /dev/null 2>&1"; } | crontab -
```

### Deploy script Develop
Prerequisite: A GitHub api token with read access to code, commit statuses, and metadata permissions is required for the script to work  

```console
git clone https://github.com/Turplanlegger/turplanlegger-api ~/turplanlegger-api-develop
chmod +x ~/turplanlegger-api-develop/deploy/deploy-develop.sh
mkdir -p ~/.config/turplanlegger
cp ~/home/turplanlegger-api-dev/deploy/env ~/.config/turplanlegger/env-develop
chmod 600 ~/.config/turplanlegger/env-develop
# Add Github access token, secret key and secret key id to env file
crontab -l | { cat; echo "*/2 * * * * $HOME/turplanlegger-api-develop/deploy/deploy-develop.sh > /dev/null 2>&1"; } | crontab -

```

### Dev
```bash
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml --env-file env-dev up -d
```

### Prod
```bash
docker compose --env-file env up -d
```

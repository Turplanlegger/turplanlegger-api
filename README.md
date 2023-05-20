# Turplanlegger
Python API for planning trips

## Install
```bash
pip install .
```

### Production
```bash
pip install .[prod]
```

### Development
```bash
pip install .[dev]
```

## Testing
Run test:
```
pip install pytest
pytest tests/test_*.py`
```

Run test and save result:
```
pip install pytest pytest-csv
pytest tests/test_*.py --csv tests/test_result.csv --csv-columns utc_timestamp,id,module,name,file,status,message,duration
git commit tests/test_result.csv -m "Unitetest result"
```


## Docker

### Deploy script
Prerequisite: A GitHub api token with the scope `read:packages` is required for the script to work  

Add a cronjob that runs the deploy script:
```bash
mkdir ~/turplanlegger-api
mkdir -p ~/.config/turplanlegger
curl -o ~/turplanlegger-api/deploy.sh https://raw.githubusercontent.com/sixcare/turplanlegger-api/main/deploy/deploy.sh
chmod +x ~/turplanlegger-api/deploy.sh
curl -o ~/.config/turplanlegger/env https://raw.githubusercontent.com/sixcare/turplanlegger-api/main/deploy/env
chmod 600 ~/.config/turplanlegger/env
crontab -l | { cat; echo "*/2 * * * * $HOME/turplanlegger-api/deploy.sh > /dev/null 2>&1"; } | crontab -
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

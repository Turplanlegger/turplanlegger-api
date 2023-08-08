# Install doc

## Ubuntu 22.04

### Postgres
`sudo apt-get install postgresql-15`

### Packages
Install build tools:  
`sudo apt-get install build-essential`

Install python3.11-dev:  
`sudo apt-get install python3.11-dev`

Install libq-dev:  
`sudo apt-get install libpq-dev`

### Python venv
```bash
sudo apt-get install python3.11-venv
mkdir venv
python3 -m venv venv
source venv/bin/activate
pip install .['dev']
```

### Config
Create a config directory and file:  
`mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf`

### Start development instance
```bash
export FLASK_APP=turplanlegger
flask run --debugger --port 8080 --with-threads --reload
```

## Docker

### Install docker
https://docs.docker.com/get-docker/

### Start development instance
```bash
docker-compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml --env-file env-dev up -d
```
### Start PostgreSQL database container
```console
docker run -e POSTGRES_USER=turadm -e POSTGRES_PASSWORD=passord -e POSTGRES_DB=turplanlegger -p 5432:5432 -d postgres:15-alpine
```
Connect using string: `postgresql://turadm:passord@localhost:5432/turplanlegger?connect_timeout=10&application_name=turplanlegger-api`


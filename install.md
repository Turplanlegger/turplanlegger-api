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
source venv/bin/active
pip install . ['dev']
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
docker-compose up
```

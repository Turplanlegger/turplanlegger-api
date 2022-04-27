# Install doc

## Ubuntu 22.04

### Postgres
`sudo apt-get install postgresql-14`

### Packages
Install build tools:  
``sudo apt-get install build-essential`

Install python3.10-dev:  
`sudo apt-get install python3.10-dev`

Install libq-dev:  
`sudo apt-get install libpq-dev`

### Python venv
```bash
sudo apt-get install python3.10-venv
mkdir venv
python3 -m venv venv
source venv/bin/active
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

### Config
Create a config directory and file:  
`mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf`

### Start development instance
```bash
export FLASK_APP=turplanlegger FLASK_ENV=development
flask run --debugger --port 8080 --with-threads --reload
```

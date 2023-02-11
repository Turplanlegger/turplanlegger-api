FROM python:3.11

RUN pip install --upgrade pip

WORKDIR /turplanlegger

COPY . .

RUN pip install --no-cache-dir .['dev'] hatch

RUN mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf

RUN echo 'DATABASE_URI="host=turplanlegger-db dbname=postgres user=user password=pass"' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'DATABASE_NAME="postgres"' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'DATABASE_MAX_RETRIES=5' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'LOG_TO_FILE=True' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'SECRET_KEY="DEFAULT"' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'SECRET_KEY_ID="1"' >> /etc/turplanlegger/turplanlegger.conf

 CMD [ "hatch", "run", "cov" ]

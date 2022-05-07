FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y \
    build-essential \
    python3.10-dev \
    python3-pip \
    postgresql-14 \
    libpq-dev

WORKDIR /turplanlegger

ADD requirements.txt /app/requirements.txt
ADD requirements-dev.txt /app/requirements-dev.txt

RUN pip3 install -r /app/requirements.txt
RUN pip3 install -r /app/requirements-dev.txt

RUN mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf

RUN echo 'DATABASE_URI="host=turplanleggerdb dbname=postgres user=user password=pass"' >> /etc/turplanlegger/turplanlegger.conf
RUN echo 'DATABASE_NAME="postgres"' >> /etc/turplanlegger/turplanlegger.conf
RUN echo 'DATABASE_MAX_RETRIES=5' >> /etc/turplanlegger/turplanlegger.conf

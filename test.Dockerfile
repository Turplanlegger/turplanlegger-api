FROM python:3.11

ARG DATABASE_URI
ARG BASE_URL
ARG SECRET_KEY=hemmelig
ARG SECRET_KEY_ID=1

RUN pip install --upgrade pip

WORKDIR /turplanlegger

COPY . .

RUN pip install --no-cache-dir .['dev'] hatch

RUN mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf

RUN echo "DATABASE_URI='${DATABASE_URI}'" >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'LOG_TO_FILE=True' >> /etc/turplanlegger/turplanlegger.conf && \
 echo "SECRET_KEY='${SECRET_KEY}'" >> /etc/turplanlegger/turplanlegger.conf && \
 echo "SECRET_KEY_ID='${SECRET_KEY_ID}'" >> /etc/turplanlegger/turplanlegger.conf

 CMD [ "hatch", "run", "cov" ]

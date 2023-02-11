FROM python:3.11

ARG DATABASE_URI=postgresql://turadm:you-need-a-new-password@turplanlegger-db:5432/turplanlegger?connect_timeout=10&application_name=turplanleggerapi
ARG BASE_URL=turplanlegger-api
ARG SECRET_KEY
ARG SECRET_KEY_ID

RUN pip install --upgrade pip

WORKDIR /turplanlegger

COPY . .

RUN pip install --no-cache-dir .['prod']

RUN mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf

RUN echo "DATABASE_URI='${DATABASE_URI}'" >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'LOG_TO_FILE=True' >> /etc/turplanlegger/turplanlegger.conf && \
 echo "SECRET_KEY='${SECRET_KEY}'" >> /etc/turplanlegger/turplanlegger.conf && \
 echo "SECRET_KEY_ID='${SECRET_KEY_ID}'" >> /etc/turplanlegger/turplanlegger.conf

CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "wsgi:app", "--processes", "4", "--threads", "2", "--stats", "0.0.0.0:9191"]

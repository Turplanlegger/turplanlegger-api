FROM python:3.11

RUN pip install --upgrade pip

WORKDIR /turplanlegger

COPY . .

# ADD dist/turplanlegger*.whl /app/turplanlegger-0.01b1-py3-none-any.whl

RUN pwd; pip install --no-cache-dir .['dev'] hatch

RUN mkdir /etc/turplanlegger && touch /etc/turplanlegger/turplanlegger.conf

RUN echo 'DATABASE_URI="host=turplanleggerdb dbname=postgres user=user password=pass"' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'DATABASE_NAME="postgres"' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'DATABASE_MAX_RETRIES=5' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'LOG_TO_FILE=True' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'SECRET_KEY="DEFAULT"' >> /etc/turplanlegger/turplanlegger.conf && \
 echo 'SECRET_KEY_ID="1"' >> /etc/turplanlegger/turplanlegger.conf

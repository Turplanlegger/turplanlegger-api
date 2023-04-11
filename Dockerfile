FROM python:3.11-bullseye

RUN pip install --upgrade pip

WORKDIR /turplanlegger

COPY . .

RUN pip install --no-cache-dir .['prod']

CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "wsgi:app", "--processes", "4", "--threads", "2"]

EXPOSE 5000

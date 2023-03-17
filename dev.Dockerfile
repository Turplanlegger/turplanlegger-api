FROM python:3.11-bullseye

RUN pip install --upgrade pip

WORKDIR /turplanlegger

COPY . .

RUN pip install --no-cache-dir .['dev'] hatch

CMD [ "flask", "run", "--debugger", "--port", "8080", "--host", "0.0.0.0", "--with-threads"]

EXPOSE 8080

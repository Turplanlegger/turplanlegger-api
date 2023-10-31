FROM python:3.12-slim-bullseye

# Set work directory
WORKDIR /turplanlegger

COPY . .

# Install build dependencies, then run `pip install`, then remove unneeded build dependencies all in a single step.
# Combined RUN statements into one to reduce number of image layers.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gcc postgresql-client libpq-dev libc6-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir .['prod'] && \
    apt-get purge -y --auto-remove gcc libpq-dev libc6-dev && \
    rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 CMD [ "curl", "-fs", "http://localhost:5000/test"]

# Default command
CMD ["gunicorn", "--bind=0.0.0.0:5000", "--workers=2", "--threads=4", "--worker-class=gthread", "--log-file=-", "wsgi:app"]

# Expose port
EXPOSE 5000

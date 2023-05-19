FROM python:3.11-slim-bullseye

# Set work directory
WORKDIR /turplanlegger

# Copy rest of the application code
COPY . .

# Install build dependencies, then run `pip install`, then remove unneeded build dependencies all in a single step.
# Combined RUN statements into one to reduce number of image layers.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc postgresql-client libpq-dev libc6-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir .['prod'] && \
    apt-get purge -y --auto-remove gcc libpq-dev libc6-dev && \
    rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 CMD [ "curl", "-fs", "http://localhost:5000/test"]

# Default command
CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "wsgi:app", "--processes", "4", "--threads", "2"]

# Expose port
EXPOSE 5000

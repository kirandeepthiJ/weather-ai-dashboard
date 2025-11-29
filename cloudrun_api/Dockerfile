# Use slim python
FROM python:3.11-slim

# Install system deps (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app
COPY main.py .

# Use PORT env var supplied by Cloud Run
ENV PORT 8080
EXPOSE 8080

# Start with Gunicorn (4 workers)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--worker-class", "gthread", "--threads", "8", "--timeout", "180", "main:app"]




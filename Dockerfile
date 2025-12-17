FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY startup.sh .

# Make startup script executable
RUN chmod +x startup.sh

# Create directory for SQLite database if needed
RUN mkdir -p /app/data

# Set Python path
ENV PYTHONPATH=/app

# Run startup script
CMD ["./startup.sh"]

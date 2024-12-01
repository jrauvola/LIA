# Use Python 3.12.2 slim image for smaller size
FROM python:3.12.2-slim-bullseye

# Allow statements and log messages to immediately appear
ENV PYTHONUNBUFFERED=1

# Set the PORT environment variable
ENV PORT=80

# Set working directory
WORKDIR /app

# Install system dependencies and FFmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port
EXPOSE 80

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "4", "--timeout", "120", "lia_backend:app"]
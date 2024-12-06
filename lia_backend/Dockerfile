# Use an AI/ML focused base image instead
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
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    wget \
    # Added dependencies for unstructured
    poppler-utils \
    libmagic1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install newer version of SQLite3
RUN wget https://www.sqlite.org/2024/sqlite-autoconf-3450000.tar.gz && \
    tar xvfz sqlite-autoconf-3450000.tar.gz && \
    cd sqlite-autoconf-3450000 && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf sqlite-autoconf-3450000* && \
    ldconfig

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies in smaller groups
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir flask gunicorn && \
    pip install --no-cache-dir tensorflow && \
    pip install --no-cache-dir praat-parselmouth==0.4.5 && \
    pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Create NLTK data directory for non-root user
RUN mkdir -p /home/appuser/nltk_data && \
    chown -R appuser:appuser /home/appuser/nltk_data

# Create directory for ChromaDB
RUN mkdir -p /app/chroma && \
    chown -R appuser:appuser /app/chroma

USER appuser

# Expose port
EXPOSE 80

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "1", "--threads", "4", "--timeout", "120", "main:app"]
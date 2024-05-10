# Use a base image with Python 3.12.2 on Debian Bullseye
FROM python:3.12.2-bullseye

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the PORT environment variable
ENV PORT 80

# Expose port 80 (if your Flask app is running on port 80)
EXPOSE 80

# Set working directory for the app
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy your Flask app file
ADD lia_backend.py ./

# Install dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --no-cache-dir \
    google-generativeai==0.5.0 \
    google-cloud-storage \
    Flask \
    Flask-Cors \
    google-cloud-speech \
    pandas \
    spacy \
    pypdf \
    PyPDF2 \
    langchain \
    langchain-google-vertexai \
    langchain-google-community \
    chromadb \
    moviepy

# Download the spaCy English model
RUN python -m spacy download en_core_web_sm

# Start Flask app (modify the entry point command if needed)
ENTRYPOINT ["python", "lia_backend.py"]
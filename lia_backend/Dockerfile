FROM python:3.12.2-bullseye

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Expose port
EXPOSE 80

# Set working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy Streamlit app (replace with your copy command if needed)
ADD lia_backend.py ./

# Install dependencies
RUN python -m pip install --no-cache-dir \
  google-generativeai==0.5.0 \
  google-cloud-storage \
  Flask Flask-Cors \
  datetime

# Start Flask app
ENTRYPOINT ["python", "lia_backend.py"]

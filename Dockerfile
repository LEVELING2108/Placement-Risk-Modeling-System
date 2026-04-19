# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Set work directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for persistence
RUN mkdir -p data models

# Expose the port the app runs on
EXPOSE 8000

# Script to initialize database and run server
RUN echo '#!/bin/bash\n\
python init_db.py\n\
# If models are not found, we can optionally train here, \n\
# but usually models are trained outside and mounted or built-in.\n\
# For this demo, let's ensure models exist.\n\
if [ ! -f "models/placement_model.pkl" ]; then\n\
    echo "No models found, training..." \n\
    python train.py\n\
fi\n\
uvicorn main:app --host 0.0.0.0 --port 8000' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"]

FROM python:3.9-slim

# Install system dependencies (including ffmpeg for video processing)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install TensorFlow and MLflow
RUN pip install tensorflow mlflow

# Set working directory in the container
WORKDIR /app

# Copy your local code to the container
COPY . /app

# Install other dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the port for Flask (5000)
EXPOSE 5000

# Start the Flask application (replace model.py with your actual Flask entry point, e.g., app.py)
CMD ["python3", "app.py"]

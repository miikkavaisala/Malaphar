# Use a slim Python base image
FROM python:3.12-slim

# Install system dependencies (required for matplotlib)
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir numpy matplotlib

# Copy your script into the container
COPY demo.py .

# Set the default command
CMD ["python", "demo.py"]

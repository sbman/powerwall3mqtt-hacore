# Use the official Debian-based Python image
FROM python:3.13-slim

# Install system dependencies including tini
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip install --no-cache-dir \
    pyyaml \
    cachetools \
    requests \
    protobuf 

RUN pip install --break-system-packages paho-mqtt

# Set the working directory
WORKDIR /app

# Copy the application code
COPY /app /app

# Use tini as the entrypoint to handle zombie processes properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the application
CMD ["python", "powerwall3mqtt.py"]

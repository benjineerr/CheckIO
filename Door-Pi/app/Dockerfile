# Super lightweight Door Node
FROM python:3.11-alpine

# Install system dependencies for serial communication
RUN apk add --no-cache gcc musl-dev

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create config directory and set permissions
RUN mkdir -p /app/config

# Run as non-root user for security
RUN adduser -D -s /bin/sh appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import json; print(json.dumps({'status': 'healthy'}))" || exit 1

# Start the application
CMD ["python", "main.py"]
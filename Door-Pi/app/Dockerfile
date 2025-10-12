# Door-Pi/app/Dockerfile - Einfache Version
FROM python:3.11-alpine

# Install system dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create directories
RUN mkdir -p /app/config /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["python", "-u", "main.py"]
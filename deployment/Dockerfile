# EasyGrant Smart Proposal Assistant - Simple Single-Stage Dockerfile
# Constitution Principle IX: Hostability - Single container, <512MB RAM

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source code
COPY backend/ /app/backend/

# Configuration file is in backend/config.yaml
# .env file is mounted via environment variables in render.yaml

# Copy sample files for demo functionality
COPY samples/ /app/samples/

# Create data directories
RUN mkdir -p /app/data/uploads /app/vector

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run FastAPI server
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]

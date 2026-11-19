FROM python:3.12-slim

WORKDIR /app

# Install system libraries needed by OpenCV and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose port (default 8080 for Railway)
EXPOSE 8080

# Start command
CMD ["sh", "-c", "python -m app.download_models || true; exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

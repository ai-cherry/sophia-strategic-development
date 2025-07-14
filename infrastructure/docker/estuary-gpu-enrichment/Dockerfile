# Estuary GPU Enrichment Processor
# Handles embeddings via Lambda GPU and storage to Weaviate
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY processor.py .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Environment variables (will be overridden by Estuary)
ENV LAMBDA_INFERENCE_URL=http://lambda-inference:8080
ENV WEAVIATE_URL=http://weaviate:8080
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ENV BATCH_SIZE=100

# Estuary Flow expects this
ENTRYPOINT ["/app/entrypoint.sh"] 
# Lambda Inference Service Dockerfile
# Optimized for NVIDIA B200 GPUs with CUDA 12.2

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_VISIBLE_DEVICES=0 \
    TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0" \
    MAX_JOBS=4

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-inference.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements-inference.txt && \
    # Pre-download the model to avoid startup delays
    python3 -c "from transformers import AutoTokenizer, AutoModel; \
                AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
                AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application code
COPY lambda_inference_service.py .
COPY ../../backend/core/auto_esc_config.py /app/backend/core/

# Create non-root user
RUN useradd -m -u 1000 inference && \
    chown -R inference:inference /app

USER inference

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the service
CMD ["python3", "-m", "uvicorn", "lambda_inference_service:app", \
     "--host", "0.0.0.0", "--port", "8080", "--workers", "1"] 
"""
Lambda Inference Service - GPU-accelerated embeddings with Portkey fallback
Handles batch embedding requests with <50ms latency on Lambda B200 GPUs
"""
import asyncio
import time
from typing import List, Dict, Optional
import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import torch
from transformers import AutoTokenizer, AutoModel
from portkey_ai import Portkey

from backend.core.auto_esc_config import get_config_value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Lambda Inference Service",
    description="GPU-accelerated embedding service for Sophia AI",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and tokenizer
device = None
tokenizer = None
model = None
portkey_client = None

# Request/Response models
class EmbedRequest(BaseModel):
    input: List[str] = Field(..., description="List of texts to embed")
    model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Model to use for embeddings",
    )

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]
    latency_ms: float

class HealthResponse(BaseModel):
    status: str
    gpu_available: bool
    cuda_device: Optional[str]
    model_loaded: bool
    portkey_configured: bool

# Retry configuration for Lambda flakes
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 2.0
    exponential_base: float = 2

async def exponential_backoff_retry(func, *args, **kwargs):
    """Execute function with exponential backoff retry logic"""
    config = RetryConfig()

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == config.max_attempts - 1:
                raise

            delay = min(
                config.base_delay * (config.exponential_base**attempt),
                config.max_delay,
            )
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)

@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup"""
    global device, tokenizer, model, portkey_client

    try:
        # Check for GPU availability
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            logger.info(
                f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
            )
            logger.info(
                f"CUDA cores: {torch.cuda.get_device_properties(0).multi_processor_count * 128}"
            )  # Approximate
        else:
            device = torch.device("cpu")
            logger.warning("No GPU available, falling back to CPU")

        # Load tokenizer and model
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        logger.info(f"Loading model: {model_name}")

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name).to(device)
        model.eval()  # Set to evaluation mode

        logger.info("Model loaded successfully")

        # Initialize Portkey client for fallback
        portkey_api_key = get_config_value("PORTKEY_API_KEY")
        if portkey_api_key:
            portkey_client = Portkey(api_key=portkey_api_key)
            logger.info("Portkey client initialized for fallback")
        else:
            logger.warning("Portkey API key not found, fallback disabled")

    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise

async def generate_embeddings_gpu(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using GPU-accelerated model"""
    start_time = time.time()

    try:
        with torch.no_grad():
            # Tokenize inputs
            inputs = tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            ).to(device)

            # Generate embeddings
            outputs = model(**inputs)

            # Mean pooling
            embeddings = outputs.last_hidden_state.mean(dim=1)

            # Convert to CPU and numpy
            embeddings = embeddings.cpu().numpy().tolist()

        latency = (time.time() - start_time) * 1000
        logger.info(f"Generated {len(texts)} embeddings in {latency:.2f}ms")

        return embeddings

    except Exception as e:
        logger.error(f"GPU embedding generation failed: {e}")
        raise

async def generate_embeddings_portkey(
    texts: List[str], model: str
) -> List[List[float]]:
    """Fallback to Portkey for embedding generation"""
    if not portkey_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Portkey fallback not available",
        )

    embeddings = []
    for text in texts:
        response = await portkey_client.embeddings.create(model=model, input=text)
        embeddings.append(response.data[0].embedding)

    return embeddings

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    """
    Generate embeddings for input texts

    Supports batch processing with GPU acceleration
    Falls back to Portkey/OpenRouter on overload
    """
    start_time = time.time()

    # Validate input
    if not request.input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Input list cannot be empty"
        )

    if len(request.input) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size cannot exceed 100 texts",
        )

    try:
        # Try GPU embedding with retry logic
        embeddings = await exponential_backoff_retry(
            generate_embeddings_gpu, request.input
        )

    except Exception as gpu_error:
        logger.warning(f"GPU embedding failed, falling back to Portkey: {gpu_error}")

        try:
            # Fallback to Portkey
            embeddings = await generate_embeddings_portkey(request.input, request.model)
        except Exception as portkey_error:
            logger.error(f"Portkey fallback also failed: {portkey_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Both GPU and Portkey embedding generation failed",
            )

    # Calculate usage
    total_tokens = sum(len(tokenizer.encode(text)) for text in request.input)

    latency_ms = (time.time() - start_time) * 1000

    return EmbedResponse(
        embeddings=embeddings,
        model=request.model,
        usage={"prompt_tokens": total_tokens, "total_tokens": total_tokens},
        latency_ms=latency_ms,
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        gpu_available=torch.cuda.is_available(),
        cuda_device=str(device) if device else None,
        model_loaded=model is not None,
        portkey_configured=portkey_client is not None,
    )

@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    metrics_lines = []

    # GPU metrics
    if torch.cuda.is_available():
        memory_allocated = torch.cuda.memory_allocated() / 1e9
        memory_reserved = torch.cuda.memory_reserved() / 1e9

        metrics_lines.extend(
            [
                "# HELP gpu_memory_allocated_gb GPU memory allocated in GB",
                "# TYPE gpu_memory_allocated_gb gauge",
                f"gpu_memory_allocated_gb {memory_allocated:.3f}",
                "# HELP gpu_memory_reserved_gb GPU memory reserved in GB",
                "# TYPE gpu_memory_reserved_gb gauge",
                f"gpu_memory_reserved_gb {memory_reserved:.3f}",
            ]
        )

    return "\n".join(metrics_lines)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Lambda Inference Service",
        "version": "1.0.0",
        "gpu": torch.cuda.is_available(),
        "endpoints": {
            "embed": "/embed",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
        },
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

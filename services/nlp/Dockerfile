# =============================================================================
# SentinelBERT NLP Service Dockerfile (Python)
# =============================================================================
# 
# This Dockerfile builds the Python-based NLP service with BERT models.
# It supports both CPU and GPU execution with CUDA optimization.
# 
# Build stages:
# 1. Base stage: Python environment with system dependencies
# 2. Dependencies stage: Install Python packages and ML models
# 3. Runtime stage: Optimized runtime environment
# 
# Usage:
#   CPU: docker build -t sentinelbert-nlp .
#   GPU: docker build -t sentinelbert-nlp --build-arg CUDA_VERSION=11.8 .
# 
# Build arguments:
#   PYTHON_VERSION: Python version (default: 3.11)
#   CUDA_VERSION: CUDA version for GPU support (default: none)
#   PYTORCH_VERSION: PyTorch version (default: 2.1.0)
# 
# =============================================================================

# -----------------------------------------------------------------------------
# Base Stage - Python environment setup
# -----------------------------------------------------------------------------
ARG PYTHON_VERSION=3.11
ARG CUDA_VERSION=""

# Use CUDA base image if CUDA_VERSION is specified, otherwise use standard Python
FROM python:${PYTHON_VERSION}-slim as base

# Build arguments
ARG CUDA_VERSION
ARG PYTORCH_VERSION=2.1.0
ARG TRANSFORMERS_VERSION=4.35.0

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    # System libraries
    libpq-dev \
    libssl-dev \
    libffi-dev \
    # Image processing libraries
    libjpeg-dev \
    libpng-dev \
    # Audio processing libraries
    libsndfile1-dev \
    # Network tools
    curl \
    wget \
    # Git for model downloads
    git \
    # Cleanup tools
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install CUDA dependencies if CUDA_VERSION is specified
RUN if [ -n "$CUDA_VERSION" ]; then \
        apt-get update && apt-get install -y \
        nvidia-cuda-toolkit \
        && rm -rf /var/lib/apt/lists/*; \
    fi

# -----------------------------------------------------------------------------
# Dependencies Stage - Install Python packages
# -----------------------------------------------------------------------------
FROM base as dependencies

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file first for better caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
# Install PyTorch first (CPU or GPU version based on CUDA_VERSION)
RUN if [ -n "$CUDA_VERSION" ]; then \
        # Install GPU version of PyTorch
        pip install torch==${PYTORCH_VERSION} torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118; \
    else \
        # Install CPU version of PyTorch
        pip install torch==${PYTORCH_VERSION} torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; \
    fi

# Install other ML and web framework dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional development tools (can be removed in production)
RUN pip install --no-cache-dir \
    # Debugging and profiling
    ipython \
    memory-profiler \
    # Code quality
    black \
    flake8 \
    # Testing
    pytest \
    pytest-asyncio \
    pytest-cov

# -----------------------------------------------------------------------------
# Model Download Stage - Download and cache ML models
# -----------------------------------------------------------------------------
FROM dependencies as models

# Create model directories
RUN mkdir -p /app/models/bert /app/models/cache /app/models/custom

# Set Transformers cache directory
ENV TRANSFORMERS_CACHE=/app/models/cache
ENV HF_HOME=/app/models/cache

# Download pre-trained BERT models
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
import torch; \
print('Downloading BERT base model...'); \
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased'); \
model = AutoModel.from_pretrained('bert-base-uncased'); \
tokenizer.save_pretrained('/app/models/bert/bert-base-uncased'); \
model.save_pretrained('/app/models/bert/bert-base-uncased'); \
print('BERT base model downloaded successfully!')"

# Download sentiment analysis model
RUN python -c "\
from transformers import pipeline; \
print('Downloading sentiment analysis model...'); \
sentiment_pipeline = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest'); \
print('Sentiment analysis model downloaded successfully!')"

# Download additional models for behavioral analysis
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
models = ['bert-base-multilingual-cased', 'distilbert-base-uncased']; \
[print(f'Downloading {model_name}...') or \
 AutoTokenizer.from_pretrained(model_name).save_pretrained(f'/app/models/bert/{model_name}') or \
 AutoModel.from_pretrained(model_name).save_pretrained(f'/app/models/bert/{model_name}') \
 for model_name in models]; \
print('Additional models downloaded successfully!')"

# -----------------------------------------------------------------------------
# Runtime Stage - Optimized production environment
# -----------------------------------------------------------------------------
FROM dependencies as runtime

# Copy models from model stage
COPY --from=models /app/models /app/models

# Create non-root user for security
RUN groupadd -r sentinelbert && \
    useradd -r -g sentinelbert -d /app -s /sbin/nologin \
    -c "SentinelBERT NLP Service" sentinelbert

# Copy application source code
COPY . /app/

# Create necessary directories
RUN mkdir -p /var/log/sentinelbert /app/data /app/temp && \
    chown -R sentinelbert:sentinelbert /app /var/log/sentinelbert

# Set environment variables for the application
ENV MODEL_PATH=/app/models \
    TRANSFORMERS_CACHE=/app/models/cache \
    HF_HOME=/app/models/cache \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    NUMEXPR_NUM_THREADS=4

# GPU-specific environment variables (if CUDA is available)
RUN if [ -n "$CUDA_VERSION" ]; then \
        echo "export CUDA_VISIBLE_DEVICES=\${CUDA_VISIBLE_DEVICES:-0}" >> /etc/environment; \
        echo "export NVIDIA_VISIBLE_DEVICES=all" >> /etc/environment; \
        echo "export NVIDIA_DRIVER_CAPABILITIES=compute,utility" >> /etc/environment; \
    fi

# Switch to non-root user
USER sentinelbert

# Expose service port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set resource limits and optimization flags
ENV MEMORY_LIMIT=4G \
    CPU_LIMIT=2.0 \
    MAX_WORKERS=2 \
    WORKER_CONNECTIONS=1000

# Pre-compile Python bytecode for faster startup
RUN python -m compileall /app

# Warm up the models (load them once to cache)
RUN python -c "\
import sys; \
sys.path.append('/app'); \
try: \
    from models.sentiment_model import SentinelBERTModel; \
    print('Warming up BERT model...'); \
    model = SentinelBERTModel(); \
    print('Model warmed up successfully!'); \
except Exception as e: \
    print(f'Model warmup failed: {e}'); \
"

# Default command to run the service
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Alternative command for development with auto-reload
# CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -----------------------------------------------------------------------------
# Development Stage - Additional development tools
# -----------------------------------------------------------------------------
FROM runtime as development

# Switch back to root to install development tools
USER root

# Install additional development dependencies
RUN pip install --no-cache-dir \
    # Jupyter for interactive development
    jupyter \
    jupyterlab \
    # Debugging tools
    pdb++ \
    ipdb \
    # Performance profiling
    py-spy \
    # Code formatting and linting
    black \
    isort \
    flake8 \
    mypy \
    # Testing frameworks
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-mock

# Install system development tools
RUN apt-get update && apt-get install -y \
    # Editors
    vim \
    nano \
    # System monitoring
    htop \
    # Network debugging
    netcat-openbsd \
    # Process management
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create development configuration
RUN mkdir -p /app/dev-config

# Switch back to non-root user
USER sentinelbert

# Expose additional ports for development
# Jupyter port
EXPOSE 8888
# Debugger port
EXPOSE 5678

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

# -----------------------------------------------------------------------------
# Metadata and Labels
# -----------------------------------------------------------------------------
LABEL maintainer="SentinelBERT Team <team@sentinelbert.com>"
LABEL version="1.0.0"
LABEL description="SentinelBERT NLP Service with BERT-based Sentiment Analysis"
LABEL org.opencontainers.image.title="SentinelBERT NLP Service"
LABEL org.opencontainers.image.description="Python-based NLP service with BERT models"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="SentinelBERT"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/your-org/SentinelBERT"

# ML-specific labels
LABEL ml.framework="PyTorch"
LABEL ml.model="BERT"
LABEL ml.task="sentiment-analysis"
LABEL ml.gpu-support="optional"

# Security labels
LABEL security.non-root="true"
LABEL security.user="sentinelbert"

# Build information
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.version=$VERSION
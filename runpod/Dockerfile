# RunPod Serverless Dockerfile for II-Search-4B
# Optimized for Personal Use - Single GPU Configuration
# Qwen3-4B with DeepSeek-R1 Reasoning Parser

FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install vLLM with CUDA 12.4 support and reasoning capabilities
# Using latest version that supports DeepSeek-R1 reasoning parser
RUN pip install --no-cache-dir vllm>=0.8.0

# Install RunPod SDK
RUN pip install --no-cache-dir runpod>=1.7.0

# Copy application files
COPY src/ /app/src/

# Set environment variables for optimal performance
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/runpod-volume/.cache/huggingface
ENV TRANSFORMERS_CACHE=/runpod-volume/.cache/huggingface
ENV HF_DATASETS_CACHE=/runpod-volume/.cache/huggingface/datasets

# Model-specific environment variables (optimized for single GPU)
ENV MODEL_NAME="Intelligent-Internet/II-Search-4B"
ENV SERVED_MODEL_NAME="II-Search-4B"
ENV TENSOR_PARALLEL_SIZE=1
ENV MAX_MODEL_LEN=32768
ENV GPU_MEMORY_UTILIZATION=0.90

# vLLM specific settings for DeepSeek-R1 reasoning
ENV ENABLE_REASONING="true"
ENV REASONING_PARSER="deepseek_r1"

# RoPE scaling configuration (optional for 32K context)
ENV ROPE_SCALING='{"rope_type":"linear","factor":2.0}'

# Optional: Pre-download model during build (uncomment if baking model into image)
# Requires HF_TOKEN to be passed as build secret
# RUN --mount=type=secret,id=HF_TOKEN \
#     python3 -c "from huggingface_hub import snapshot_download; \
#     snapshot_download('Intelligent-Internet/II-Search-4B', token=open('/run/secrets/HF_TOKEN', 'r').read().strip())"

# Expose port for local testing (not required for RunPod)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set the entrypoint to the handler
CMD ["python", "-u", "/app/src/handler.py"]

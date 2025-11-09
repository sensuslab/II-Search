# RunPod Deployment Guide for II-Search-4B

Complete guide for deploying the II-Search-4B model on RunPod Serverless with vLLM inference and auto-scaling.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Cost Optimization](#cost-optimization)

---

## Prerequisites

### Required Accounts & Tools
- **RunPod Account**: Sign up at [runpod.io](https://runpod.io)
- **Docker**: Installed locally for building images
- **Docker Registry**: Docker Hub, GitHub Container Registry, or similar
- **HuggingFace Token** (if model is gated): Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### GPU Requirements
- **Minimum**: 8x A100 (80GB) or 8x H100 GPUs
- **Reason**: The deployment uses `--tensor-parallel-size 8`
- **Estimated VRAM**: ~32-40GB total (4-5GB per GPU for 4B model)

---

## Quick Start

### Option 1: Use Pre-built Image (Recommended)

If you have a pre-built Docker image:

1. **Go to RunPod Dashboard** → "Serverless"
2. **Click "New Endpoint"**
3. **Configure**:
   - **Name**: `II-Search-4B-vLLM`
   - **Container Image**: `your-registry/ii-search-4b-runpod:latest`
   - **GPU Type**: Select A100 80GB or H100
   - **GPUs Per Worker**: `8`
   - **Idle Timeout**: `900` seconds (15 minutes)
   - **Min Workers**: `0` (scales to zero)
   - **Max Workers**: `3` (adjust based on budget)
4. **Environment Variables**: (Set in RunPod UI)
   ```
   MODEL_NAME=Intelligent-Internet/II-Search-4B
   SERVED_MODEL_NAME=II-Search-4B
   TENSOR_PARALLEL_SIZE=8
   MAX_MODEL_LEN=131072
   ENABLE_REASONING=true
   REASONING_PARSER=deepseek_r1
   GPU_MEMORY_UTILIZATION=0.95
   ```
5. **Deploy** and wait for initialization

### Option 2: Build from Source

1. **Clone this repository**:
   ```bash
   git clone <your-repo-url>
   cd runpod
   ```

2. **Set environment variables**:
   ```bash
   export HF_TOKEN=your_huggingface_token  # If model is gated
   export REGISTRY=docker.io/yourusername
   ```

3. **Build and push**:
   ```bash
   cd builder
   ./build.sh v1.0
   ```

4. **Follow Option 1** steps above with your image

---

## Detailed Setup

### Step 1: Build Docker Image

```bash
# Set your registry
export REGISTRY=docker.io/yourusername
export IMAGE_TAG=v1.0

# Optional: Set HuggingFace token for gated models
export HF_TOKEN=hf_xxxxxxxxxxxxx

# Build
cd runpod/builder
./build.sh ${IMAGE_TAG}
```

The build script will:
- Build the Docker image with vLLM and dependencies
- Tag it for your registry
- Optionally push to registry

### Step 2: Push to Docker Registry

If you didn't push during build:

```bash
docker push ${REGISTRY}/ii-search-4b-runpod:${IMAGE_TAG}
```

### Step 3: Create RunPod Endpoint

#### Via RunPod Dashboard:

1. Navigate to: **RunPod Dashboard** → **Serverless** → **+ New Endpoint**

2. **Basic Configuration**:
   - **Endpoint Name**: `II-Search-4B-vLLM`
   - **Container Image**: `your-registry/ii-search-4b-runpod:v1.0`
   - **Container Disk**: `20 GB` (minimum)

3. **GPU Configuration**:
   - **GPU Type**: A100 80GB or H100
   - **GPUs Per Worker**: `8` ⚠️ **CRITICAL**
   - **Min Active Workers**: `0`
   - **Max Workers**: `3` (adjust based on expected load)

4. **Scaling Configuration**:
   - **Scaling Type**: `Queue Delay`
   - **Idle Timeout**: `900` seconds (15 minutes) ⚠️ **REQUIRED**
   - **Execution Timeout**: `600` seconds (10 minutes, adjust as needed)

5. **Environment Variables**:
   Click "Add Environment Variable" and add:

   | Variable | Value |
   |----------|-------|
   | `MODEL_NAME` | `Intelligent-Internet/II-Search-4B` |
   | `SERVED_MODEL_NAME` | `II-Search-4B` |
   | `TENSOR_PARALLEL_SIZE` | `8` |
   | `MAX_MODEL_LEN` | `131072` |
   | `ENABLE_REASONING` | `true` |
   | `REASONING_PARSER` | `deepseek_r1` |
   | `GPU_MEMORY_UTILIZATION` | `0.95` |
   | `HF_TOKEN` | `your_token` (if model is gated) |

6. **Advanced Settings** (Optional):
   - **Network Volume**: Enable for faster model loading (recommended)
   - **Volume Size**: 50GB minimum
   - **Volume Mount Path**: `/runpod-volume`

7. **Click "Deploy"**

#### Via RunPod API/CLI:

```bash
# Install RunPod CLI
pip install runpod

# Create endpoint (example)
runpod create endpoint \
  --name "II-Search-4B-vLLM" \
  --image "your-registry/ii-search-4b-runpod:v1.0" \
  --gpu-type "A100-80GB" \
  --gpus-per-worker 8 \
  --min-workers 0 \
  --max-workers 3 \
  --idle-timeout 900 \
  --env MODEL_NAME=Intelligent-Internet/II-Search-4B \
  --env TENSOR_PARALLEL_SIZE=8
```

---

## Configuration

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `Intelligent-Internet/II-Search-4B` | HuggingFace model ID |
| `SERVED_MODEL_NAME` | `II-Search-4B` | Name exposed in API |
| `TENSOR_PARALLEL_SIZE` | `8` | Number of GPUs for tensor parallelism |
| `MAX_MODEL_LEN` | `131072` | Maximum context length |
| `GPU_MEMORY_UTILIZATION` | `0.95` | GPU memory utilization (0.0-1.0) |
| `ENABLE_REASONING` | `true` | Enable reasoning output |
| `REASONING_PARSER` | `deepseek_r1` | Reasoning parser type |
| `ROPE_SCALING` | See Dockerfile | RoPE scaling configuration |
| `HF_TOKEN` | - | HuggingFace token (for gated models) |

### RoPE Scaling Configuration

The model uses YARN RoPE scaling for extended context:

```json
{
  "rope_type": "yarn",
  "factor": 1.5,
  "original_max_position_embeddings": 98304
}
```

This allows the 4B model to handle up to 131,072 tokens.

---

## Testing

### Test via RunPod Dashboard

1. Go to your endpoint page
2. Click "Run" or "Test"
3. Input:
   ```json
   {
     "input": {
       "prompt": "What is the capital of France?",
       "sampling_params": {
         "temperature": 0.7,
         "top_p": 0.9,
         "max_tokens": 512
       }
     }
   }
   ```
4. Check the output for both `text` and `reasoning` fields

### Test via API

```bash
# Set your endpoint ID and API key
ENDPOINT_ID="your-endpoint-id"
API_KEY="your-runpod-api-key"

# Make a request
curl -X POST "https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "Explain quantum computing in simple terms.",
      "sampling_params": {
        "temperature": 0.7,
        "max_tokens": 1024
      }
    }
  }'
```

### Test with Python

```python
import runpod

runpod.api_key = "your-runpod-api-key"
endpoint = runpod.Endpoint("your-endpoint-id")

# Run inference
result = endpoint.run_sync({
    "input": {
        "prompt": "What are the benefits of renewable energy?",
        "sampling_params": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2048
        }
    }
})

print("Response:", result["output"]["text"])
print("Reasoning:", result["output"]["reasoning"])
```

---

## Monitoring & Troubleshooting

### Monitoring

1. **RunPod Dashboard**: Check endpoint metrics
   - Active workers
   - Request count
   - Error rate
   - Execution time

2. **Logs**: View worker logs in RunPod dashboard
   - Look for initialization errors
   - Check model loading time
   - Monitor GPU utilization

### Common Issues

#### 1. Cold Start is Too Slow (>5 minutes)

**Cause**: Model downloads on every cold start

**Solutions**:
- Enable Network Volume in endpoint settings
- Pre-bake model into Docker image (uncomment lines in Dockerfile)
- Increase idle timeout to reduce cold starts

#### 2. Out of Memory (OOM) Errors

**Cause**: Insufficient GPU memory

**Solutions**:
- Reduce `MAX_MODEL_LEN` (e.g., to 65536)
- Lower `GPU_MEMORY_UTILIZATION` (e.g., to 0.90)
- Verify you're using 8 GPUs (`TENSOR_PARALLEL_SIZE=8`)
- Use GPUs with more VRAM (H100 instead of A100)

#### 3. Workers Not Scaling Down

**Cause**: Idle timeout not configured or traffic is continuous

**Solutions**:
- Verify idle timeout is set to 900 seconds
- Check that scaling type is "Queue Delay"
- Ensure there are actual idle periods between requests

#### 4. Reasoning Output Not Appearing

**Cause**: Reasoning parser not enabled or incorrect configuration

**Solutions**:
- Verify `ENABLE_REASONING=true`
- Check `REASONING_PARSER=deepseek_r1`
- Update vLLM version if needed (`vllm>=0.8.0`)

#### 5. Model Not Loading (404/401 Errors)

**Cause**: Model is gated or HF_TOKEN not set

**Solutions**:
- Request access to model on HuggingFace
- Set `HF_TOKEN` environment variable
- Verify token has correct permissions

---

## Cost Optimization

### Understanding Costs

RunPod Serverless charges per second of GPU usage:
- **8x A100 80GB**: ~$0.0128/second ($46.08/hour when active)
- **8x H100**: ~$0.0192/second ($69.12/hour when active)

With 15-minute idle timeout and auto-scaling to zero:
- You only pay when processing requests + 15 minutes after last request
- No charges when completely idle

### Optimization Strategies

1. **Tune Idle Timeout**:
   - **15 minutes (900s)**: Good for intermittent traffic (recommended)
   - **5 minutes (300s)**: Lower costs, more cold starts
   - **30 minutes (1800s)**: Fewer cold starts, higher idle costs

2. **Use Network Volumes**:
   - Cache model on volume for faster cold starts
   - Reduces initialization time from 5+ minutes to <30 seconds
   - Volume storage cost: ~$0.10/GB/month

3. **Batch Requests**:
   - Send multiple requests during active period
   - Maximize utilization during billable time

4. **Monitor Usage**:
   - Track cold start frequency
   - Adjust min/max workers based on patterns
   - Consider keeping 1 worker active during peak hours

5. **Right-Size GPU Count**:
   - 4B model doesn't need 8 GPUs for capacity
   - Could reduce to 4 GPUs if supported by model
   - However, tensor-parallel-size must match GPU count

### Example Cost Calculation

**Scenario**: 100 requests/day, 30 seconds per request, 15-min idle timeout

- **Active time**: 100 requests × 30s = 3,000 seconds
- **Idle time**: 100 periods × 900s = 90,000 seconds (max)
- **Realistic idle**: ~10 periods × 900s = 9,000 seconds (batched requests)
- **Total billable**: 3,000 + 9,000 = 12,000 seconds = 3.33 hours
- **Daily cost (8x A100)**: 3.33 hours × $46.08 = **~$153/day**
- **Monthly cost**: **~$4,590/month**

Compare to always-on Pod:
- **8x A100 always-on**: 24 hours × 30 days × $46.08 = **$33,177/month**
- **Savings with serverless**: **86% reduction**

---

## Next Steps

1. ✅ Deploy endpoint following this guide
2. ✅ Test with sample requests
3. ✅ Monitor cold start times and adjust idle timeout
4. ✅ Enable network volume for production
5. ✅ Set up monitoring and alerts
6. ✅ Integrate with your application

For issues or questions, refer to:
- [RunPod Documentation](https://docs.runpod.io)
- [vLLM Documentation](https://docs.vllm.ai)
- [Model on HuggingFace](https://huggingface.co/Intelligent-Internet/II-Search-4B)

---

## Support

- **RunPod Support**: support@runpod.io
- **RunPod Discord**: [discord.gg/runpod](https://discord.gg/runpod)
- **vLLM GitHub**: [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)

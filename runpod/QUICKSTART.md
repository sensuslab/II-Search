# Quick Start Guide - II-Search-4B Personal Deployment

Deploy II-Search-4B on a single GPU in 15 minutes for personal testing.

## ⚡ Quick Deploy (For Impatient Users)

```bash
# 1. Build (5 min)
cd runpod/builder && export REGISTRY=docker.io/yourusername && ./build.sh

# 2. Deploy on RunPod Dashboard:
#    - Image: docker.io/yourusername/ii-search-4b-runpod:latest
#    - GPU: 1x RTX 4090 (budget) or 1x A100 (performance)
#    - GPUs per worker: 1
#    - Idle timeout: 300 seconds
#    - Max workers: 1
#    - Environment variables: Set TENSOR_PARALLEL_SIZE=1, MAX_MODEL_LEN=32768

# 3. Test (2 min)
cd ../tests && python test_endpoint.py --endpoint-id YOUR_ID --api-key YOUR_KEY --run-tests
```

---

## 📋 Prerequisites (2 minutes)

### Required
- [ ] RunPod account at [runpod.io](https://runpod.io)
- [ ] Docker installed locally
- [ ] Docker Hub account (free)

### Optional
- [ ] HuggingFace token (if model is gated)
- [ ] Python 3.11+ for local testing

---

## Step 1: Build Docker Image (5 minutes)

```bash
# Navigate to builder directory
cd runpod/builder

# Set your Docker registry
export REGISTRY=docker.io/yourusername  # Replace with your Docker Hub username

# Optional: Set HuggingFace token if model is gated
export HF_TOKEN=hf_xxxxxxxxxxxxx

# Build and push
./build.sh v1.0
```

**Expected output:**
```
✅ Build complete!
✅ Push complete!
Use this image in RunPod: docker.io/yourusername/ii-search-4b-runpod:v1.0
```

---

## Step 2: Create RunPod Endpoint (5 minutes)

### A. Go to RunPod Dashboard

1. Navigate to: https://runpod.io/console/serverless
2. Click **"+ New Endpoint"**

### B. Basic Settings

| Field | Value |
|-------|-------|
| **Endpoint Name** | `II-Search-4B-Personal` |
| **Container Image** | `docker.io/yourusername/ii-search-4b-runpod:v1.0` |
| **Container Disk** | `15 GB` |

### C. GPU Settings

| Field | Value | Notes |
|-------|-------|-------|
| **GPU Type** | `RTX4090` or `A100 80GB` | RTX 4090 is 57% cheaper |
| **GPUs Per Worker** | `1` | ⚠️ Single GPU only |
| **Min Workers** | `0` | Scale to zero |
| **Max Workers** | `1` | Personal use - one instance max |

### D. Scaling Settings

| Field | Value |
|-------|-------|
| **Scaling Type** | `Queue Delay` |
| **Idle Timeout** | `300` seconds (5 minutes) |
| **Execution Timeout** | `300` seconds |

### E. Environment Variables

Click "+ Add Environment Variable" for each:

| Variable | Value |
|----------|-------|
| `TENSOR_PARALLEL_SIZE` | `1` |
| `MAX_MODEL_LEN` | `32768` |
| `GPU_MEMORY_UTILIZATION` | `0.90` |
| `ENABLE_REASONING` | `true` |
| `REASONING_PARSER` | `deepseek_r1` |

*Optional: Add `HF_TOKEN` if model requires authentication*

### F. Network Volume (Highly Recommended)

| Field | Value |
|-------|-------|
| **Enable Network Volume** | `Yes` |
| **Size** | `30 GB` |
| **Mount Path** | `/runpod-volume` |

**Cost**: ~$3/month, saves 2-5 minutes on every cold start

### G. Deploy

Click **"Deploy"** and wait 30-60 seconds for initialization.

---

## Step 3: Get Endpoint Details (1 minute)

Once deployed:

1. **Endpoint ID**: Found in the URL or endpoint details page
2. **API Key**: Go to Settings → API Keys → Copy

---

## Step 4: Test Your Endpoint (2 minutes)

### Option 1: Quick cURL Test

```bash
# Replace with your actual values
ENDPOINT_ID="your_endpoint_id_here"
API_KEY="your_api_key_here"

curl -X POST "https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "What is 2+2? Explain your reasoning.",
      "sampling_params": {
        "temperature": 0.7,
        "max_tokens": 256
      }
    }
  }'
```

### Option 2: Python Test Script

```bash
# Set environment variables
export RUNPOD_API_KEY="your_api_key_here"
export RUNPOD_ENDPOINT_ID="your_endpoint_id_here"

# Run test suite
cd runpod/tests
python test_endpoint.py \
  --endpoint-id $RUNPOD_ENDPOINT_ID \
  --api-key $RUNPOD_API_KEY \
  --run-tests
```

### Option 3: Single Prompt Test

```bash
python test_endpoint.py \
  --endpoint-id $RUNPOD_ENDPOINT_ID \
  --api-key $RUNPOD_API_KEY \
  --prompt "Explain quantum entanglement in simple terms."
```

---

## ✅ Expected Results

### First Request (Cold Start)
- ⏱️ **Without network volume**: 2-5 minutes
- ⏱️ **With network volume**: 20-30 seconds
- 📦 Model downloads and initializes

### Subsequent Requests (Warm)
- ⏱️ **Response time**: 2-5 seconds
- ⚡ **Tokens/second**: 30-60 (depends on GPU)
- 💬 **Includes reasoning**: Yes (if enabled)

### After 5 Minutes Idle
- 💤 Worker shuts down automatically
- 💰 No charges while idle
- 🔄 Next request triggers cold start

---

## 💰 Cost Breakdown

### GPU Options

**RTX 4090 24GB** (Budget Choice):
- Cost: $2.48/hour
- Per request (5min idle): $0.21
- 1 hour daily: $74/month
- **Best for**: Light testing, budget-conscious

**A100 80GB** (Best Performance):
- Cost: $5.76/hour
- Per request (5min idle): $0.48
- 1 hour daily: $173/month
- **Best for**: Faster responses, extended context

### Usage Examples

**10 requests/week**:
- RTX 4090: ~$8/month
- A100: ~$20/month

**5 requests/day**:
- RTX 4090: ~$32/month
- A100: ~$72/month

**1 hour active daily**:
- RTX 4090: ~$74/month
- A100: ~$173/month

---

## 🛠️ Quick Troubleshooting

### Cold Start Taking Forever (>5 minutes)?
**Solution**: Enable network volume (Step 2F above)

### "Out of Memory" Error?
**Solution**: Reduce context length:
```bash
# In environment variables:
MAX_MODEL_LEN=16384  # From 32768
GPU_MEMORY_UTILIZATION=0.85  # From 0.90
```

### No Reasoning in Response?
**Solution**: Check environment variables:
```bash
ENABLE_REASONING=true
REASONING_PARSER=deepseek_r1
```

### Costs Too High?
**Solution**:
1. Use RTX 4090 instead of A100
2. Reduce idle timeout to 180 seconds (3 minutes)
3. Check you set max_workers=1

---

## 🎯 What Can You Do Now?

### 1. Tool Use & Function Calling
```python
prompt = """
Available tools:
- calculate(expression: str) -> float
- search(query: str) -> str

Question: What is 127 * 89?
"""
```

### 2. RAG & Vector Store Integration
```python
# Retrieve relevant context
context = your_vector_db.search(query, top_k=5)

# Query with context
prompt = f"Context: {context}\n\nQuestion: {query}"
response = query_model(prompt)
```

### 3. Reasoning Tasks
```python
prompt = """
Solve this step by step:
A train travels 120 km in 2 hours. What is its speed in m/s?
"""
text, reasoning = query_model(prompt)
print(f"Reasoning:\n{reasoning}")
print(f"Answer:\n{text}")
```

---

## 📊 Performance Expectations

### RTX 4090 24GB
- **Context**: 16K tokens
- **Speed**: ~30-40 tokens/second
- **Latency**: ~3-5 seconds for 512 tokens
- **Cost**: $0.21 per request

### A100 80GB
- **Context**: 32K tokens
- **Speed**: ~50-60 tokens/second
- **Latency**: ~2-3 seconds for 512 tokens
- **Cost**: $0.48 per request

---

## 🚀 Next Steps

1. ✅ **Integrate into your app**: Use the API endpoint in your code
2. ✅ **Experiment with prompts**: Test different reasoning tasks
3. ✅ **Try tool use**: Implement function calling
4. ✅ **Connect vector store**: Build RAG applications
5. ✅ **Monitor costs**: Check RunPod dashboard regularly

---

## 📚 Additional Resources

- **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed configuration
- **Configuration**: See [configs/runpod-config.json](configs/runpod-config.json) for templates
- **RunPod Docs**: https://docs.runpod.io
- **Model Card**: https://huggingface.co/Intelligent-Internet/II-Search-4B

---

## ❓ Common Questions

**Q: Why single GPU if the start command specifies tensor-parallel-size 8?**
A: The original command was for production scale. A 4B model only needs ~8GB VRAM and fits easily on one GPU. Single GPU is perfect for personal use.

**Q: Can I use an even cheaper GPU?**
A: Yes! Try L40S (48GB, $3.44/hr) or even RTX 3090 (24GB, ~$2/hr) for budget testing.

**Q: What if I need longer context?**
A: On A100 80GB, you can increase `MAX_MODEL_LEN` to 65536 (65K tokens). Just adjust the environment variable.

**Q: Will it work for production?**
A: This config is optimized for personal testing. For production, see DEPLOYMENT.md for scaling strategies.

**Q: How do I reduce costs further?**
A:
1. Use RTX 4090 instead of A100 (57% cheaper)
2. Reduce idle timeout to 180s
3. Use the endpoint less frequently
4. Consider spot instances if available

---

**Total Setup Time**: ~15 minutes
**Difficulty**: Beginner-friendly
**Monthly Cost**: $74-173 (1hr daily) or $8-20 (10 requests/week)
**Perfect For**: Personal testing, development, tool use, RAG applications

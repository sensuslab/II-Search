# Quick Start Guide - II-Search-4B on RunPod

Get your II-Search-4B model running on RunPod in under 30 minutes.

## Prerequisites Check

- [ ] RunPod account created at [runpod.io](https://runpod.io)
- [ ] Docker installed locally
- [ ] Docker Hub or GHCR account
- [ ] Credit card added to RunPod for GPU access
- [ ] (Optional) HuggingFace token if model is gated

## Step 1: Build Docker Image (10 minutes)

```bash
# Clone repository
git clone <your-repo>
cd runpod

# Configure
export REGISTRY=docker.io/yourusername  # Your Docker registry
export HF_TOKEN=hf_xxxxx                # If model is gated

# Build and push
cd builder
./build.sh v1.0
```

**Expected output**:
```
✅ Build complete!
✅ Push complete!
Use this image in RunPod: docker.io/yourusername/ii-search-4b-runpod:v1.0
```

## Step 2: Create RunPod Endpoint (5 minutes)

### Via Dashboard (Easiest):

1. Go to: https://runpod.io/console/serverless

2. Click **"+ New Endpoint"**

3. Fill in **Basic Settings**:
   - **Name**: `II-Search-4B`
   - **Container Image**: `docker.io/yourusername/ii-search-4b-runpod:v1.0`
   - **Container Disk**: `20 GB`

4. Configure **GPU Settings**:
   - **GPU Type**: `A100 80GB` (or `H100` if available)
   - **GPUs Per Worker**: `8` ⚠️
   - **Min Active Workers**: `0`
   - **Max Workers**: `1` (for testing)

5. Set **Scaling**:
   - **Scaling Type**: `Queue Delay`
   - **Idle Timeout**: `900` seconds
   - **Execution Timeout**: `600` seconds

6. Add **Environment Variables** (click "+ Add Environment Variable" for each):

   | Key | Value |
   |-----|-------|
   | `MODEL_NAME` | `Intelligent-Internet/II-Search-4B` |
   | `TENSOR_PARALLEL_SIZE` | `8` |
   | `MAX_MODEL_LEN` | `131072` |
   | `ENABLE_REASONING` | `true` |
   | `REASONING_PARSER` | `deepseek_r1` |

7. **(Recommended)** Enable **Network Volume**:
   - Toggle "Network Volume" to ON
   - **Size**: `50 GB`
   - **Mount Path**: `/runpod-volume`

8. Click **"Deploy"**

9. Wait for endpoint to initialize (5-15 minutes for first run)

## Step 3: Get Your Endpoint Details (1 minute)

Once deployed, note:
- **Endpoint ID**: Shows in URL: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID`
- **API Key**: Found in RunPod Settings → API Keys

## Step 4: Test Your Endpoint (2 minutes)

### Quick Test (cURL):

```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "What is 2+2? Think step by step.",
      "sampling_params": {
        "temperature": 0.7,
        "max_tokens": 256
      }
    }
  }'
```

### Python Test:

```python
import requests

ENDPOINT_ID = "your_endpoint_id"
API_KEY = "your_api_key"

response = requests.post(
    f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "input": {
            "prompt": "Explain quantum computing simply.",
            "sampling_params": {
                "temperature": 0.7,
                "max_tokens": 512
            }
        }
    }
)

result = response.json()
print("Text:", result["output"]["text"])
print("Reasoning:", result["output"]["reasoning"])
```

### Automated Test:

```bash
cd runpod/tests
pip install requests

python test_endpoint.py \
  --endpoint-id YOUR_ENDPOINT_ID \
  --api-key YOUR_API_KEY \
  --run-tests
```

## Expected Results

### First Request (Cold Start):
- ⏱️ **Time**: 5-15 minutes (without network volume)
- ⏱️ **Time**: 30-90 seconds (with network volume)
- 📥 **Model loading**: Downloads from HuggingFace
- 🔧 **Initialization**: vLLM engine starts across 8 GPUs

### Subsequent Requests (Warm):
- ⏱️ **Time**: 2-10 seconds (depending on prompt length)
- ⚡ **Fast**: Model already loaded in memory

### After 15 Minutes Idle:
- 💤 **Auto-scaling**: Worker shuts down
- 💰 **No charges**: You stop paying for GPUs
- ⏱️ **Next request**: Cold start again

## Troubleshooting Quick Fixes

### "Out of Memory" Error
```bash
# Reduce context length in RunPod environment variables:
MAX_MODEL_LEN=32768  # Instead of 131072
```

### Cold Starts Too Slow
```bash
# Enable Network Volume in endpoint settings (if not already)
# Or increase idle timeout to reduce frequency:
Idle Timeout: 1800  # 30 minutes
```

### No Reasoning in Output
```bash
# Verify environment variables are set:
ENABLE_REASONING=true
REASONING_PARSER=deepseek_r1
```

## Cost Awareness

⚠️ **IMPORTANT**: This configuration costs approximately:
- **$46/hour** when workers are active
- **$0/hour** when scaled to zero

With 15-minute idle timeout:
- After each request, worker stays active for 15 more minutes
- Multiple requests within 15 minutes = charged once
- Isolated requests = charged for 15 min each

**Example Daily Cost**:
- 10 requests, well-spaced = 10 × 15 min = 2.5 hours = **$115/day**
- 10 requests, within 15 min window = 15 min = **$11.50/day**

## Next Steps

✅ **Basic Setup Complete!** Now you can:

1. **Optimize Costs**: Read [DEPLOYMENT.md](DEPLOYMENT.md) for cost optimization
2. **Identify Issues**: Check [POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md)
3. **Integrate**: Use the endpoint in your application
4. **Scale**: Increase `max_workers` based on traffic
5. **Monitor**: Set up alerts in RunPod dashboard

## Common Configuration Changes

### Reduce GPU Count (Lower Cost):
```bash
# In RunPod environment variables:
TENSOR_PARALLEL_SIZE=2  # Instead of 8
# Also change "GPUs Per Worker" to 2 in GPU settings
```

### Shorter Context (Less Memory):
```bash
MAX_MODEL_LEN=32768  # Instead of 131072
```

### Faster Scaling Down:
```bash
Idle Timeout: 300  # 5 minutes instead of 15
```

### Keep Always Active (No Cold Starts):
```bash
Min Active Workers: 1  # Instead of 0
# ⚠️ Costs $46/hour continuously!
```

## Support Resources

- 📖 **Full Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- ⚠️ **Issues**: [POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md)
- 🌐 **RunPod Docs**: https://docs.runpod.io
- 💬 **RunPod Discord**: https://discord.gg/runpod

---

**Estimated Total Time**: 20-30 minutes
**Difficulty**: Intermediate
**Cost**: ~$46/hour when active (scales to $0 when idle)

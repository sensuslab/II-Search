# II-Search-4B RunPod Serverless - Personal Use Deployment

Deploy II-Search-4B (Qwen3-4B with DeepSeek-R1 reasoning) on a single GPU for personal testing and development.

## 🚀 Quick Start (15 Minutes)

```bash
# 1. Build Docker image
cd runpod/builder
export REGISTRY=docker.io/yourusername
./build.sh v1.0

# 2. Deploy on RunPod:
#    - GPU: 1x A100 80GB (or RTX 4090 for budget)
#    - Idle timeout: 300s (5 minutes)
#    - Max workers: 1

# 3. Test
cd ../tests
python test_endpoint.py --endpoint-id YOUR_ID --api-key YOUR_KEY --run-tests
```

## 💡 Why This Configuration?

This deployment is optimized for **personal use** with:

- ✅ **Single GPU**: 4B model fits comfortably on one GPU
- ✅ **32K Context**: Sufficient for tools, prompting, and vector store operations
- ✅ **Auto-scaling**: Scales to zero after 5 minutes of inactivity
- ✅ **Fast Responses**: ~30-60 tokens/second throughput
- ✅ **Reasoning Support**: DeepSeek-R1 parser for thinking extraction
- ✅ **Cost-Effective**: ~$0.48 per request with 5-min idle timeout

## 💰 Cost Estimates (Personal Use)

### GPU Options

| GPU | Cost/Hour | Cost per Request* | Monthly (1hr/day) |
|-----|-----------|-------------------|-------------------|
| **RTX 4090 24GB** | $2.48 | $0.21 | **$74** |
| **A5000 24GB** | $2.84 | $0.24 | $85 |
| **A100 80GB** | $5.76 | $0.48 | $173 |

_*Assuming 5-minute idle timeout per request_

### Usage Examples

**Light Testing** (10 requests/week):
- RTX 4090: ~$8/month
- A100: ~$20/month

**Regular Testing** (5 requests/day):
- RTX 4090: ~$32/month
- A100: ~$72/month

**Daily Development** (1 hour active/day):
- RTX 4090: ~$74/month
- A100: ~$173/month

## 📋 Requirements

### Cloud Infrastructure
- RunPod account ([sign up free](https://runpod.io))
- Docker registry (Docker Hub, GHCR)
- Network volume recommended (30GB = $3/month)

### Local Development
- Docker 20.10+
- Python 3.11+ (for testing)

### Model Access
- HuggingFace token if model is gated

## 🎯 Features

- **vLLM Inference**: Optimized for speed and efficiency
- **DeepSeek-R1 Reasoning**: Extract model thinking process
- **Tool Use Support**: Compatible with function calling and tools
- **Vector Store Ready**: Works with RAG and embedding workflows
- **Streaming**: Real-time token streaming support
- **Auto-scaling**: Zero cost when idle

## 📁 Project Structure

```
runpod/
├── Dockerfile                 # Single GPU optimized
├── requirements.txt           # Python dependencies
├── src/
│   └── handler.py            # RunPod serverless handler
├── builder/
│   └── build.sh              # Build and push script
├── tests/
│   └── test_endpoint.py      # Testing utilities
├── configs/
│   └── runpod-config.json    # Configuration templates
├── README.md                 # This file
├── QUICKSTART.md             # Step-by-step guide
└── DEPLOYMENT.md             # Detailed documentation
```

## 🔧 Configuration

### Default Settings (Optimized for Personal Use)

```json
{
  "model": "Intelligent-Internet/II-Search-4B",
  "tensor_parallel_size": 1,
  "max_context_length": 32768,
  "gpu_count": 1,
  "idle_timeout": 300,
  "max_workers": 1,
  "gpu_memory_utilization": 0.90
}
```

### GPU Recommendations

| Use Case | GPU | Context | Monthly Cost |
|----------|-----|---------|--------------|
| **Budget Testing** | RTX 4090 | 16K | $74 (1hr/day) |
| **Balanced** | A5000 | 24K | $85 (1hr/day) |
| **Best Performance** | A100 80GB | 32K | $173 (1hr/day) |
| **Extended Context** | A100 80GB | 65K | $173 (1hr/day) |

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: 15-minute deployment guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Comprehensive setup and configuration
- **[configs/runpod-config.json](configs/runpod-config.json)**: Configuration templates

## 🧪 Testing

### Quick Test
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "Explain quantum computing in simple terms.",
      "sampling_params": {
        "temperature": 0.7,
        "max_tokens": 512
      }
    }
  }'
```

### Python Integration
```python
import requests

def query_model(prompt: str, max_tokens: int = 512):
    response = requests.post(
        f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "input": {
                "prompt": prompt,
                "sampling_params": {
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            }
        }
    )
    result = response.json()
    return result["output"]["text"], result["output"]["reasoning"]

# Example
text, reasoning = query_model("What is 2+2? Think step by step.")
print(f"Answer: {text}")
print(f"Reasoning: {reasoning}")
```

## ⚠️ Important Notes

### Model Size
- **4B parameters** = ~8GB GPU memory
- Fits comfortably on 24GB+ GPUs
- No need for multi-GPU setup

### Context Length
- **32K tokens**: Good for most personal use
- **16K tokens**: Budget GPUs (RTX 4090)
- **65K tokens**: Extended context (A100 only)

### Cold Starts
- **Without network volume**: 2-5 minutes
- **With network volume**: 20-30 seconds
- **Cost**: ~$3/month for 30GB volume

### Reasoning Parser
- DeepSeek-R1 parser extracts thinking process
- Compatible with Qwen3-based models
- Test locally first if unsure

## 🛠️ Troubleshooting

### "Out of Memory" Error
```bash
# Reduce context length in environment variables:
MAX_MODEL_LEN=16384  # From 32768
GPU_MEMORY_UTILIZATION=0.85  # From 0.90
```

### Slow Cold Starts
```bash
# Enable network volume in RunPod endpoint settings
# Size: 30GB, Mount: /runpod-volume
```

### No Reasoning Output
```bash
# Verify environment variables:
ENABLE_REASONING=true
REASONING_PARSER=deepseek_r1
```

### High Costs
```bash
# Reduce idle timeout:
Idle Timeout: 180  # 3 minutes instead of 5
# Or use cheaper GPU:
GPU Type: RTX4090  # Instead of A100
```

## 📚 Use Cases

### Tool Use & Function Calling
```python
# Model supports tool definitions in prompts
prompt = """
Available tools:
- search(query: str) -> List[str]
- calculate(expression: str) -> float

Question: What is the population of Tokyo divided by 2?
"""
```

### RAG & Vector Store
```python
# Works with vector databases and embeddings
context = retrieve_from_vector_store(query)
prompt = f"Context: {context}\n\nQuestion: {query}"
response = query_model(prompt)
```

### Reasoning Tasks
```python
# DeepSeek-R1 parser extracts step-by-step thinking
prompt = "Solve: If x + 5 = 12, what is x? Think step by step."
text, reasoning = query_model(prompt)
print(f"Reasoning:\n{reasoning}")
print(f"Answer:\n{text}")
```

## 🔗 Resources

- **Model**: [Intelligent-Internet/II-Search-4B](https://huggingface.co/Intelligent-Internet/II-Search-4B)
- **RunPod Docs**: [docs.runpod.io](https://docs.runpod.io)
- **vLLM Docs**: [docs.vllm.ai](https://docs.vllm.ai)

## 💬 Support

- **RunPod Discord**: [discord.gg/runpod](https://discord.gg/runpod)
- **Issues**: Open an issue in this repository

## 🎓 Recommendations

1. ✅ **Start with RTX 4090** for budget testing
2. ✅ **Enable network volume** for fast cold starts
3. ✅ **Use 5-minute idle timeout** for personal use
4. ✅ **Monitor costs** in RunPod dashboard
5. ✅ **Test reasoning parser** before heavy use

---

**Version**: 2.0.0 (Personal Use Optimized)
**Last Updated**: 2025-11-09
**Configuration**: Single GPU, 32K context, auto-scaling
**Target Use Case**: Personal testing, development, tool use, vector stores

# II-Search-4B RunPod Serverless Deployment

Deploy the II-Search-4B model (Qwen3-4B fine-tune with DeepSeek-R1 reasoning) on RunPod Serverless with vLLM inference engine and automatic scaling.

## 🚀 Quick Start

```bash
# 1. Clone and navigate
cd runpod

# 2. Build Docker image
export REGISTRY=docker.io/yourusername
cd builder && ./build.sh v1.0

# 3. Deploy on RunPod
# - Go to https://runpod.io/console/serverless
# - Create new endpoint with your image
# - Configure 8 GPUs, 900s idle timeout
# - Set environment variables (see DEPLOYMENT.md)

# 4. Test
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Hello, world!"}}'
```

## 📁 Project Structure

```
runpod/
├── Dockerfile                 # Docker image for vLLM + RunPod
├── requirements.txt           # Python dependencies
├── src/
│   └── handler.py            # RunPod serverless handler
├── builder/
│   └── build.sh              # Build and push script
├── tests/
│   └── test_endpoint.py      # Testing utilities
├── configs/
│   └── runpod-config.json    # RunPod configuration template
├── DEPLOYMENT.md             # Comprehensive deployment guide
├── POTENTIAL_ISSUES.md       # Issues and troubleshooting
└── README.md                 # This file
```

## 🎯 Features

- ✅ **vLLM Inference Engine**: High-throughput, low-latency inference
- ✅ **DeepSeek-R1 Reasoning Parser**: Extract model reasoning/thinking
- ✅ **Auto-scaling**: Scale to zero with 15-minute idle timeout
- ✅ **Extended Context**: Support for up to 131K tokens
- ✅ **Tensor Parallelism**: Distributed across 8 GPUs
- ✅ **OpenAI-Compatible API**: Easy integration
- ✅ **Network Volume Support**: Fast cold starts

## 📋 Requirements

### Infrastructure
- **RunPod Account** with serverless access
- **Docker Registry** (Docker Hub, GHCR, etc.)
- **8x A100 80GB** or **8x H100** GPUs per worker

### Software
- Docker 20.10+
- Python 3.11+
- vLLM 0.8.0+
- CUDA 12.4+

### Optional
- HuggingFace Token (if model is gated)
- RunPod Network Volume (recommended for production)

## 🔧 Configuration

### Model Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Model | `Intelligent-Internet/II-Search-4B` | Base model on HuggingFace |
| Architecture | Qwen3-4B (fine-tuned) | 4B parameters |
| Context Length | 131,072 tokens | With YARN RoPE scaling |
| Tensor Parallel | 8 GPUs | Distributed inference |
| Reasoning | DeepSeek-R1 Parser | Thinking extraction |

### Scaling Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Min Workers | 0 | Scale to zero when idle |
| Max Workers | 3 | Limit concurrent instances |
| Idle Timeout | 900s (15 min) | Balance cost vs cold starts |
| Execution Timeout | 600s (10 min) | For long-context requests |
| Scaling Type | Queue Delay | Responsive to request patterns |

## 💰 Cost Estimates

### Per-Second Pricing (Active Time Only)
- **8x A100 80GB**: $0.0128/second = $46.08/hour
- **8x H100**: $0.0192/second = $69.12/hour

### Monthly Estimates

| Usage Pattern | Active Time | Monthly Cost (8x A100) |
|---------------|-------------|------------------------|
| **Light** (1h/day) | 30 hours | $1,382 |
| **Moderate** (6h/day) | 180 hours | $8,294 |
| **Heavy** (12h/day) | 360 hours | $16,589 |
| **Always-On** (24h/day) | 720 hours | $33,178 |

> **Note**: With autoscaling, you pay only for active + idle time (up to 15 min after last request)

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete deployment guide with step-by-step instructions
- **[POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md)**: Comprehensive list of potential issues and solutions

## 🧪 Testing

### Local Testing (Single GPU)

```bash
# Test vLLM configuration locally first
docker run --gpus all -p 8000:8000 \
  -e MODEL_NAME=Intelligent-Internet/II-Search-4B \
  -e TENSOR_PARALLEL_SIZE=1 \
  ii-search-4b-runpod:latest
```

### RunPod Endpoint Testing

See `tests/test_endpoint.py` for automated testing:

```bash
python tests/test_endpoint.py \
  --endpoint-id YOUR_ENDPOINT_ID \
  --api-key YOUR_API_KEY
```

## ⚠️ Important Warnings

### 1. **High GPU Cost**
Using 8 GPUs costs **$46/hour when active**. Consider starting with 2-4 GPUs for testing.

### 2. **Cold Start Time**
First request after idle period takes **5-15 minutes** without network volume. Enable network volume for production.

### 3. **Memory Requirements**
131K context length requires significant VRAM. Monitor for OOM errors and reduce `MAX_MODEL_LEN` if needed.

### 4. **Reasoning Parser Compatibility**
DeepSeek-R1 parser support is new. Test thoroughly before production deployment.

See [POTENTIAL_ISSUES.md](POTENTIAL_ISSUES.md) for complete list.

## 🛠️ Troubleshooting

### Cold Starts Too Slow
- Enable Network Volume in RunPod endpoint settings
- Pre-bake model into Docker image
- Increase idle timeout to reduce frequency

### Out of Memory Errors
- Reduce `MAX_MODEL_LEN` from 131072 to 65536 or 32768
- Lower `GPU_MEMORY_UTILIZATION` from 0.95 to 0.90
- Verify 8 GPUs are allocated

### Workers Not Scaling Down
- Check idle timeout is set to 900 seconds
- Verify scaling type is "Queue Delay"
- Ensure traffic has actual idle periods

### Reasoning Not Working
- Verify `ENABLE_REASONING=true` and `REASONING_PARSER=deepseek_r1`
- Update to vLLM 0.8.0 or later
- Check model compatibility with reasoning parser

## 🤝 Contributing

Improvements welcome! Areas for contribution:
- Performance benchmarks
- Cost optimization strategies
- Alternative model configurations
- Integration examples

## 📄 License

This deployment configuration is provided as-is. Check model license at:
https://huggingface.co/Intelligent-Internet/II-Search-4B

## 🔗 Resources

- **Model**: [Intelligent-Internet/II-Search-4B](https://huggingface.co/Intelligent-Internet/II-Search-4B)
- **RunPod Docs**: [docs.runpod.io](https://docs.runpod.io)
- **vLLM Docs**: [docs.vllm.ai](https://docs.vllm.ai)
- **DeepSeek-R1**: [github.com/deepseek-ai/DeepSeek-R1](https://github.com/deepseek-ai/DeepSeek-R1)

## 📞 Support

- **RunPod Discord**: [discord.gg/runpod](https://discord.gg/runpod)
- **vLLM GitHub**: [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- **Issues**: Open an issue in this repository

---

**Version**: 1.0.0
**Last Updated**: 2025-11-09
**Status**: Production Ready (with considerations - see POTENTIAL_ISSUES.md)

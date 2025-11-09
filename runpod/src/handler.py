#!/usr/bin/env python3
"""
RunPod Serverless Handler for II-Search-4B with vLLM
Supports DeepSeek-R1 Reasoning Parser and auto-scaling
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
import runpod
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from vllm.entrypoints.openai.api_server import (
    OpenAIServingChat,
    OpenAIServingCompletion,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configuration from environment variables
MODEL_NAME = os.getenv("MODEL_NAME", "Intelligent-Internet/II-Search-4B")
SERVED_MODEL_NAME = os.getenv("SERVED_MODEL_NAME", "II-Search-4B")
TENSOR_PARALLEL_SIZE = int(os.getenv("TENSOR_PARALLEL_SIZE", "8"))
MAX_MODEL_LEN = int(os.getenv("MAX_MODEL_LEN", "131072"))
GPU_MEMORY_UTILIZATION = float(os.getenv("GPU_MEMORY_UTILIZATION", "0.95"))
ENABLE_REASONING = os.getenv("ENABLE_REASONING", "true").lower() == "true"
REASONING_PARSER = os.getenv("REASONING_PARSER", "deepseek_r1")

# RoPE scaling configuration
import json
ROPE_SCALING = json.loads(os.getenv("ROPE_SCALING",
    '{"rope_type":"yarn","factor":1.5,"original_max_position_embeddings":98304}'))

# Initialize vLLM engine
logger.info(f"Initializing vLLM engine for model: {MODEL_NAME}")
logger.info(f"Configuration: TP={TENSOR_PARALLEL_SIZE}, MaxLen={MAX_MODEL_LEN}, Reasoning={ENABLE_REASONING}")

# Create engine arguments
engine_args = AsyncEngineArgs(
    model=MODEL_NAME,
    served_model_name=SERVED_MODEL_NAME,
    tensor_parallel_size=TENSOR_PARALLEL_SIZE,
    max_model_len=MAX_MODEL_LEN,
    gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
    trust_remote_code=True,
    enable_reasoning=ENABLE_REASONING,
    reasoning_parser=REASONING_PARSER if ENABLE_REASONING else None,
    rope_scaling=ROPE_SCALING,
    disable_log_requests=False,
    disable_log_stats=False,
)

# Initialize the async engine
vllm_engine = None

async def initialize_engine():
    """Initialize the vLLM engine asynchronously"""
    global vllm_engine
    if vllm_engine is None:
        logger.info("Creating AsyncLLMEngine...")
        vllm_engine = AsyncLLMEngine.from_engine_args(engine_args)
        logger.info("vLLM engine initialized successfully!")
    return vllm_engine


async def generate_text(prompt: str, sampling_params: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """
    Generate text using vLLM engine with streaming support

    Args:
        prompt: Input text prompt
        sampling_params: Dictionary of sampling parameters

    Yields:
        Generated text chunks
    """
    engine = await initialize_engine()

    # Create sampling parameters
    params = SamplingParams(
        temperature=sampling_params.get("temperature", 0.7),
        top_p=sampling_params.get("top_p", 0.9),
        max_tokens=sampling_params.get("max_tokens", 2048),
        stop=sampling_params.get("stop", None),
        frequency_penalty=sampling_params.get("frequency_penalty", 0.0),
        presence_penalty=sampling_params.get("presence_penalty", 0.0),
    )

    # Generate with streaming
    request_id = f"runpod-{os.urandom(8).hex()}"

    async for output in engine.generate(prompt, params, request_id):
        if output.outputs:
            text = output.outputs[0].text
            # Extract reasoning if available
            if ENABLE_REASONING and hasattr(output.outputs[0], 'reasoning_content'):
                reasoning = output.outputs[0].reasoning_content
                yield json.dumps({
                    "text": text,
                    "reasoning": reasoning,
                    "finished": output.finished
                })
            else:
                yield json.dumps({
                    "text": text,
                    "finished": output.finished
                })


async def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    RunPod handler function for processing inference requests

    Job input format:
    {
        "input": {
            "prompt": "Your question here",
            "sampling_params": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048,
                ...
            },
            "stream": false
        }
    }

    Returns:
        Dictionary containing generated text and reasoning (if enabled)
    """
    try:
        job_input = job.get("input", {})

        # Validate input
        if "prompt" not in job_input:
            return {
                "error": "Missing 'prompt' in job input",
                "status": "error"
            }

        prompt = job_input["prompt"]
        sampling_params = job_input.get("sampling_params", {})
        stream = job_input.get("stream", False)

        logger.info(f"Processing request with prompt length: {len(prompt)} chars")

        if stream:
            # Streaming response
            async def stream_generator():
                async for chunk in generate_text(prompt, sampling_params):
                    yield chunk

            return stream_generator()
        else:
            # Non-streaming response - collect all chunks
            full_response = {
                "text": "",
                "reasoning": "",
                "finished": False
            }

            async for chunk in generate_text(prompt, sampling_params):
                chunk_data = json.loads(chunk)
                full_response["text"] = chunk_data.get("text", "")
                full_response["reasoning"] = chunk_data.get("reasoning", "")
                full_response["finished"] = chunk_data.get("finished", False)

            return {
                "output": full_response,
                "status": "success"
            }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "status": "error"
        }


if __name__ == "__main__":
    logger.info("Starting RunPod serverless worker for II-Search-4B")
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"Tensor Parallel Size: {TENSOR_PARALLEL_SIZE}")
    logger.info(f"Max Model Length: {MAX_MODEL_LEN}")
    logger.info(f"Reasoning Enabled: {ENABLE_REASONING}")

    # Start RunPod serverless worker
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True,  # Enable streaming aggregation
    })

#!/usr/bin/env python3
"""
Test script for II-Search-4B RunPod Serverless Endpoint
"""

import os
import sys
import time
import json
import argparse
import requests
from typing import Dict, Any, Optional


class RunPodEndpointTester:
    """Test RunPod serverless endpoint"""

    def __init__(self, endpoint_id: str, api_key: str):
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def run_sync(self, prompt: str, sampling_params: Optional[Dict[str, Any]] = None) -> Dict:
        """Run synchronous inference request"""
        if sampling_params is None:
            sampling_params = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 512
            }

        payload = {
            "input": {
                "prompt": prompt,
                "sampling_params": sampling_params
            }
        }

        print(f"\n{'='*60}")
        print(f"Running sync request...")
        print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"{'='*60}\n")

        start_time = time.time()

        try:
            response = requests.post(
                f"{self.base_url}/runsync",
                headers=self.headers,
                json=payload,
                timeout=600  # 10 minute timeout
            )
            response.raise_for_status()

            elapsed = time.time() - start_time
            result = response.json()

            print(f"✅ Request completed in {elapsed:.2f}s")
            return result

        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            print(f"❌ Request failed after {elapsed:.2f}s: {e}")
            raise

    def run_async(self, prompt: str, sampling_params: Optional[Dict[str, Any]] = None) -> str:
        """Run asynchronous inference request and return job ID"""
        if sampling_params is None:
            sampling_params = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 512
            }

        payload = {
            "input": {
                "prompt": prompt,
                "sampling_params": sampling_params
            }
        }

        print(f"\n{'='*60}")
        print(f"Running async request...")
        print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"{'='*60}\n")

        try:
            response = requests.post(
                f"{self.base_url}/run",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            job_id = result.get("id")

            print(f"✅ Job submitted: {job_id}")
            return job_id

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            raise

    def check_status(self, job_id: str) -> Dict:
        """Check status of async job"""
        try:
            response = requests.get(
                f"{self.base_url}/status/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Status check failed: {e}")
            raise

    def wait_for_completion(self, job_id: str, timeout: int = 600) -> Dict:
        """Wait for async job to complete"""
        print(f"Waiting for job {job_id} to complete...")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            status = self.check_status(job_id)
            current_status = status.get("status")

            if current_status != last_status:
                print(f"Status: {current_status}")
                last_status = current_status

            if current_status == "COMPLETED":
                elapsed = time.time() - start_time
                print(f"✅ Job completed in {elapsed:.2f}s")
                return status

            elif current_status in ["FAILED", "CANCELLED"]:
                print(f"❌ Job {current_status.lower()}")
                return status

            time.sleep(2)

        print(f"❌ Timeout after {timeout}s")
        return {"status": "TIMEOUT"}


def print_result(result: Dict):
    """Pretty print inference result"""
    print(f"\n{'='*60}")
    print("RESULT")
    print(f"{'='*60}\n")

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    if "output" in result:
        output = result["output"]

        if isinstance(output, dict):
            if "text" in output:
                print(f"Text:\n{output['text']}\n")

            if "reasoning" in output and output["reasoning"]:
                print(f"{'-'*60}")
                print(f"Reasoning:\n{output['reasoning']}\n")

            if "finished" in output:
                print(f"Finished: {output['finished']}")
        else:
            print(f"Output: {output}")

    print(f"{'='*60}\n")


def run_tests(endpoint_id: str, api_key: str):
    """Run comprehensive endpoint tests"""
    tester = RunPodEndpointTester(endpoint_id, api_key)

    # Test 1: Simple question
    print("\n" + "="*60)
    print("TEST 1: Simple Question")
    print("="*60)

    try:
        result = tester.run_sync(
            prompt="What is the capital of France?",
            sampling_params={
                "temperature": 0.7,
                "max_tokens": 128
            }
        )
        print_result(result)
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")

    # Test 2: Reasoning task
    print("\n" + "="*60)
    print("TEST 2: Reasoning Task")
    print("="*60)

    try:
        result = tester.run_sync(
            prompt="Solve this step by step: If a train travels 120 km in 2 hours, what is its average speed in meters per second?",
            sampling_params={
                "temperature": 0.3,
                "max_tokens": 1024
            }
        )
        print_result(result)
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")

    # Test 3: Long context (if supported)
    print("\n" + "="*60)
    print("TEST 3: Longer Response")
    print("="*60)

    try:
        result = tester.run_sync(
            prompt="Explain the concept of quantum entanglement in simple terms, then describe three potential applications.",
            sampling_params={
                "temperature": 0.8,
                "max_tokens": 2048
            }
        )
        print_result(result)
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Test II-Search-4B RunPod Endpoint")
    parser.add_argument("--endpoint-id", required=True, help="RunPod endpoint ID")
    parser.add_argument("--api-key", help="RunPod API key (or set RUNPOD_API_KEY env var)")
    parser.add_argument("--prompt", help="Custom prompt to test")
    parser.add_argument("--run-tests", action="store_true", help="Run comprehensive tests")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("RUNPOD_API_KEY")
    if not api_key:
        print("Error: API key required. Set --api-key or RUNPOD_API_KEY environment variable")
        sys.exit(1)

    if args.run_tests:
        # Run comprehensive test suite
        run_tests(args.endpoint_id, api_key)
    elif args.prompt:
        # Test single custom prompt
        tester = RunPodEndpointTester(args.endpoint_id, api_key)
        result = tester.run_sync(args.prompt)
        print_result(result)
    else:
        print("Specify --run-tests or --prompt to test the endpoint")
        sys.exit(1)


if __name__ == "__main__":
    main()

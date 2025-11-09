#!/bin/bash
# Build script for II-Search-4B RunPod Docker image

set -e

# Configuration
IMAGE_NAME="ii-search-4b-runpod"
IMAGE_TAG="${1:-latest}"
REGISTRY="${REGISTRY:-}"  # Set to your Docker registry (e.g., docker.io/username)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building II-Search-4B RunPod Docker Image${NC}"
echo "========================================"

# Check if HF_TOKEN is set for private models
if [ -z "$HF_TOKEN" ]; then
    echo -e "${YELLOW}Warning: HF_TOKEN not set. If the model is gated, the build will fail.${NC}"
    echo "Set it with: export HF_TOKEN=your_token_here"
fi

# Build the image
echo -e "${GREEN}Building Docker image...${NC}"
cd "$(dirname "$0")/.."

if [ -n "$HF_TOKEN" ]; then
    # Build with HuggingFace token secret
    docker build \
        --secret id=HF_TOKEN \
        -t ${IMAGE_NAME}:${IMAGE_TAG} \
        -f Dockerfile \
        .
else
    # Build without token (for public models)
    docker build \
        -t ${IMAGE_NAME}:${IMAGE_TAG} \
        -f Dockerfile \
        .
fi

echo -e "${GREEN}Build complete!${NC}"

# Tag for registry if REGISTRY is set
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    echo -e "${GREEN}Tagging image for registry: ${FULL_IMAGE_NAME}${NC}"
    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}

    # Ask if user wants to push
    read -p "Push to registry? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Pushing to registry...${NC}"
        docker push ${FULL_IMAGE_NAME}
        echo -e "${GREEN}Push complete!${NC}"
        echo -e "${YELLOW}Use this image in RunPod: ${FULL_IMAGE_NAME}${NC}"
    fi
else
    echo -e "${YELLOW}To push to a registry, set REGISTRY environment variable:${NC}"
    echo "  export REGISTRY=docker.io/yourusername"
    echo "  ./build.sh"
fi

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Push the image to a Docker registry (Docker Hub, GHCR, etc.)"
echo "2. Create a new RunPod Serverless Endpoint"
echo "3. Use the image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "4. Configure with 8 GPUs per worker (tensor-parallel-size=8)"
echo "5. Set idle timeout to 900 seconds (15 minutes)"
echo ""
echo "See DEPLOYMENT.md for detailed instructions"

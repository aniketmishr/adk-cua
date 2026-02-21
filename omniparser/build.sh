#!/bin/bash

# Build script for Omniparser Docker image

IMAGE_NAME="omniparser"
IMAGE_TAG="latest"

echo "🔨 Building Omniparser Docker image..."
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Build the image
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "Image size:"
    docker images ${IMAGE_NAME}:${IMAGE_TAG}
    echo ""
    echo "To run:"
    echo "  docker run -p 5000:5000 ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    echo "To push to registry:"
    echo "  docker tag ${IMAGE_NAME}:${IMAGE_TAG} your-username/${IMAGE_NAME}:${IMAGE_TAG}"
    echo "  docker push your-username/${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi
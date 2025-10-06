#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Building Internal Genius Docker Images ===${NC}\n"

# Enable BuildKit for faster builds and caching
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Function to print section headers
print_section() {
    echo -e "\n${YELLOW}>>> $1${NC}\n"
}

# Parse arguments
BUILD_API=true
BUILD_WORKER=true
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --api-only)
            BUILD_WORKER=false
            shift
            ;;
        --worker-only)
            BUILD_API=false
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --help)
            echo "Usage: ./build.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --api-only      Build only the API service"
            echo "  --worker-only   Build only the Worker service"
            echo "  --no-cache      Build without using cache"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build API service
if [ "$BUILD_API" = true ]; then
    print_section "Building FastAPI Service (Lightweight)"

    if [ "$NO_CACHE" = true ]; then
        docker build \
            --no-cache \
            --file ./backend/Dockerfile.api \
            --tag internal-genius-api:latest \
            --progress=plain \
            ./backend
    else
        docker build \
            --file ./backend/Dockerfile.api \
            --tag internal-genius-api:latest \
            --progress=plain \
            ./backend
    fi

    echo -e "${GREEN}✓ API service built successfully${NC}"

    # Show image size
    API_SIZE=$(docker images internal-genius-api:latest --format "{{.Size}}")
    echo -e "${GREEN}  Image size: ${API_SIZE}${NC}"
fi

# Build Worker service
if [ "$BUILD_WORKER" = true ]; then
    print_section "Building Celery Worker Service (Heavy ML)"

    if [ "$NO_CACHE" = true ]; then
        docker build \
            --no-cache \
            --file ./backend/Dockerfile.worker \
            --tag internal-genius-worker:latest \
            --progress=plain \
            ./backend
    else
        docker build \
            --file ./backend/Dockerfile.worker \
            --tag internal-genius-worker:latest \
            --progress=plain \
            ./backend
    fi

    echo -e "${GREEN}✓ Worker service built successfully${NC}"

    # Show image size
    WORKER_SIZE=$(docker images internal-genius-worker:latest --format "{{.Size}}")
    echo -e "${GREEN}  Image size: ${WORKER_SIZE}${NC}"
fi

print_section "Build Summary"

if [ "$BUILD_API" = true ] && [ "$BUILD_WORKER" = true ]; then
    echo -e "${GREEN}Both services built successfully!${NC}"
    echo -e "\nImage Sizes:"
    echo -e "  API:    ${API_SIZE}"
    echo -e "  Worker: ${WORKER_SIZE}"
elif [ "$BUILD_API" = true ]; then
    echo -e "${GREEN}API service built successfully! Size: ${API_SIZE}${NC}"
else
    echo -e "${GREEN}Worker service built successfully! Size: ${WORKER_SIZE}${NC}"
fi

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Run: ${GREEN}docker compose up -d${NC}"
echo -e "  2. Check logs: ${GREEN}docker compose logs -f${NC}"
echo -e "  3. Test API: ${GREEN}curl http://localhost:8000/${NC}"

.PHONY: help build build-api build-worker up down logs clean restart test stats

# Default target
help:
	@echo "Internal Genius - Docker Commands"
	@echo ""
	@echo "Setup & Build:"
	@echo "  make build          - Build all images"
	@echo "  make build-api      - Build API image only"
	@echo "  make build-worker   - Build Worker image only"
	@echo "  make build-nc       - Build without cache"
	@echo ""
	@echo "Running:"
	@echo "  make up             - Start all services"
	@echo "  make up-api         - Start API and dependencies only"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make restart-api    - Restart API only"
	@echo "  make restart-worker - Restart Worker only"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs           - View all logs"
	@echo "  make logs-api       - View API logs"
	@echo "  make logs-worker    - View Worker logs"
	@echo "  make stats          - Show container resource usage"
	@echo "  make ps             - Show running containers"
	@echo ""
	@echo "Debugging:"
	@echo "  make shell-api      - Enter API container"
	@echo "  make shell-worker   - Enter Worker container"
	@echo "  make test-api       - Test API health"
	@echo "  make celery-status  - Check Celery worker status"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make clean-images   - Remove images"
	@echo "  make clean-cache    - Remove build cache"
	@echo "  make clean-all      - Full cleanup"

# Build targets
build:
	@echo "Building all images..."
	export DOCKER_BUILDKIT=1 && docker compose build

build-api:
	@echo "Building API image..."
	export DOCKER_BUILDKIT=1 && docker compose build backend

build-worker:
	@echo "Building Worker image..."
	export DOCKER_BUILDKIT=1 && docker compose build celery-worker

build-nc:
	@echo "Building without cache..."
	export DOCKER_BUILDKIT=1 && docker compose build --no-cache

# Running targets
up:
	@echo "Starting all services..."
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@make ps

up-api:
	@echo "Starting API and dependencies..."
	docker compose up -d backend redis chroma
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@make ps

down:
	@echo "Stopping all services..."
	docker compose down

restart:
	@echo "Restarting all services..."
	docker compose restart

restart-api:
	@echo "Restarting API..."
	docker compose restart backend

restart-worker:
	@echo "Restarting Worker..."
	docker compose restart celery-worker

# Monitoring targets
logs:
	docker compose logs -f

logs-api:
	docker compose logs -f backend

logs-worker:
	docker compose logs -f celery-worker

stats:
	docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

ps:
	docker compose ps

# Debugging targets
shell-api:
	docker compose exec backend bash

shell-worker:
	docker compose exec celery-worker bash

test-api:
	@echo "Testing API health..."
	@curl -f http://localhost:8000/ || echo "API not responding"

celery-status:
	@echo "Checking Celery worker status..."
	docker compose exec celery-worker celery -A celery_worker:celery inspect active

celery-stats:
	@echo "Celery worker statistics..."
	docker compose exec celery-worker celery -A celery_worker:celery inspect stats

# Cleanup targets
clean:
	@echo "Removing containers and volumes..."
	docker compose down -v

clean-images:
	@echo "Removing internal-genius images..."
	docker images | grep internal-genius | awk '{print $$3}' | xargs -r docker rmi -f

clean-cache:
	@echo "Removing Docker build cache..."
	docker builder prune -f

clean-all: clean clean-images clean-cache
	@echo "Full cleanup complete!"

# Development targets
dev:
	@echo "Starting in development mode with hot reload..."
	docker compose watch

dev-api:
	@echo "Starting API in development mode..."
	docker compose up backend redis chroma

# Database targets
db-reset:
	@echo "Resetting ChromaDB..."
	docker compose down chroma
	docker volume rm $$(docker volume ls -q | grep chroma) 2>/dev/null || true
	docker compose up -d chroma

# Image size check
size:
	@echo "Image sizes:"
	@docker images internal-genius-api:latest --format "API:    {{.Size}}"
	@docker images internal-genius-worker:latest --format "Worker: {{.Size}}"

# Quick rebuild and restart
rebuild: build down up
	@echo "Rebuild complete!"

rebuild-api: build-api restart-api
	@echo "API rebuilt!"

rebuild-worker: build-worker restart-worker
	@echo "Worker rebuilt!"

# Production deployment
deploy:
	@echo "Deploying to production..."
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Backup
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	docker compose exec chroma tar czf - /chroma/chroma > backups/chroma-$$(date +%Y%m%d-%H%M%S).tar.gz
	@echo "Backup created in backups/"

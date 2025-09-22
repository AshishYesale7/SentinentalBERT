# SentinentalBERT Development Makefile
# Provides convenient commands for Docker development workflow

.PHONY: help dev-up dev-down dev-restart dev-logs dev-build dev-clean dev-status test lint format

# Default target
help: ## Show this help message
	@echo "SentinentalBERT Development Commands"
	@echo "===================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Environment Commands
dev-up: ## Start the development environment
	@echo "🚀 Starting SentinentalBERT development environment..."
	./start-dev.sh

dev-down: ## Stop the development environment
	@echo "🛑 Stopping development environment..."
	./start-dev.sh stop

dev-restart: ## Restart the development environment
	@echo "🔄 Restarting development environment..."
	./start-dev.sh restart

dev-status: ## Show status of all services
	@echo "📊 Service Status:"
	./start-dev.sh status

dev-logs: ## Show logs for all services
	@echo "📋 Service Logs:"
	./start-dev.sh logs

dev-logs-dashboard: ## Show logs for dashboard only
	@echo "📋 Dashboard Logs:"
	docker-compose -f docker-compose.dev.yml logs -f streamlit-dashboard

dev-logs-nlp: ## Show logs for NLP service only
	@echo "📋 NLP Service Logs:"
	docker-compose -f docker-compose.dev.yml logs -f nlp-service

dev-logs-backend: ## Show logs for backend service only
	@echo "📋 Backend Service Logs:"
	docker-compose -f docker-compose.dev.yml logs -f backend-service

# Build Commands
dev-build: ## Build all development images
	@echo "🔨 Building development images..."
	docker-compose -f docker-compose.dev.yml build

dev-build-dashboard: ## Build dashboard image only
	@echo "🔨 Building dashboard image..."
	docker-compose -f docker-compose.dev.yml build streamlit-dashboard

dev-build-no-cache: ## Build all images without cache
	@echo "🔨 Building all images without cache..."
	docker-compose -f docker-compose.dev.yml build --no-cache

# Database Commands
db-reset: ## Reset the development database
	@echo "🗄️ Resetting database..."
	docker-compose -f docker-compose.dev.yml stop postgres
	docker-compose -f docker-compose.dev.yml rm -f postgres
	docker volume rm sentinelbert_postgres_dev_data || true
	docker-compose -f docker-compose.dev.yml up -d postgres
	@echo "⏳ Waiting for database to initialize..."
	sleep 30

db-shell: ## Open PostgreSQL shell
	@echo "🗄️ Opening database shell..."
	docker-compose -f docker-compose.dev.yml exec postgres psql -U sentinel -d sentinelbert

db-backup: ## Backup development database
	@echo "💾 Creating database backup..."
	mkdir -p backups
	docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U sentinel sentinelbert > backups/sentinelbert_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

# Redis Commands
redis-shell: ## Open Redis CLI
	@echo "🔴 Opening Redis shell..."
	docker-compose -f docker-compose.dev.yml exec redis redis-cli -a $${REDIS_PASSWORD:-redispass123}

redis-flush: ## Flush Redis cache
	@echo "🔴 Flushing Redis cache..."
	docker-compose -f docker-compose.dev.yml exec redis redis-cli -a $${REDIS_PASSWORD:-redispass123} FLUSHALL

# Testing Commands
test: ## Run all tests
	@echo "🧪 Running tests..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard python -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard python -m pytest tests/ --cov=. --cov-report=html

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard python -m pytest tests/test_integration.py -v

# Code Quality Commands
lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code with black
	@echo "🎨 Formatting code..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard black . --line-length=127

type-check: ## Run type checking with mypy
	@echo "🔍 Running type checks..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard mypy . --ignore-missing-imports

# Monitoring Commands
monitor: ## Open monitoring dashboard
	@echo "📊 Opening monitoring dashboards..."
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000 (admin/admin123)"
	@echo "Adminer: http://localhost:8084"

# Cleanup Commands
dev-clean: ## Clean up development environment
	@echo "🧹 Cleaning up development environment..."
	./start-dev.sh clean

dev-clean-volumes: ## Remove all volumes (destructive)
	@echo "⚠️  This will remove all data volumes. Are you sure? [y/N]"
	@read -r REPLY; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		docker-compose -f docker-compose.dev.yml down -v; \
		echo "✅ Volumes removed"; \
	else \
		echo "❌ Cancelled"; \
	fi

dev-clean-all: ## Remove everything (containers, volumes, images)
	@echo "⚠️  This will remove EVERYTHING. Are you sure? [y/N]"
	@read -r REPLY; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		docker-compose -f docker-compose.dev.yml down -v --rmi all; \
		docker system prune -a --volumes -f; \
		echo "✅ Everything cleaned"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Service-specific Commands
dashboard-shell: ## Open shell in dashboard container
	@echo "🖥️ Opening dashboard shell..."
	docker-compose -f docker-compose.dev.yml exec streamlit-dashboard /bin/bash

nlp-shell: ## Open shell in NLP service container
	@echo "🖥️ Opening NLP service shell..."
	docker-compose -f docker-compose.dev.yml exec nlp-service /bin/bash

backend-shell: ## Open shell in backend service container
	@echo "🖥️ Opening backend service shell..."
	docker-compose -f docker-compose.dev.yml exec backend-service /bin/bash

# Environment Commands
env-setup: ## Set up environment file
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.dev .env; \
		echo "✅ .env file created. Please review and modify as needed."; \
	else \
		echo "ℹ️  .env file already exists"; \
	fi

env-validate: ## Validate environment configuration
	@echo "🔍 Validating environment configuration..."
	@if [ -f .env ]; then \
		echo "✅ .env file exists"; \
		grep -q "POSTGRES_PASSWORD" .env && echo "✅ PostgreSQL password set" || echo "❌ PostgreSQL password missing"; \
		grep -q "REDIS_PASSWORD" .env && echo "✅ Redis password set" || echo "❌ Redis password missing"; \
		grep -q "JWT_SECRET" .env && echo "✅ JWT secret set" || echo "❌ JWT secret missing"; \
	else \
		echo "❌ .env file missing. Run 'make env-setup' first"; \
	fi

# Quick Development Workflow
quick-start: env-setup dev-build dev-up ## Quick start: setup env, build, and start
	@echo "🎉 Development environment is ready!"
	@echo "Dashboard: http://localhost:8501"

quick-restart: dev-down dev-up ## Quick restart: stop and start
	@echo "🔄 Environment restarted"

# Health Checks
health-check: ## Check health of all services
	@echo "🏥 Checking service health..."
	@echo "Dashboard: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8501/_stcore/health || echo 'DOWN')"
	@echo "Backend: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/actuator/health || echo 'DOWN')"
	@echo "NLP Service: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo 'DOWN')"
	@echo "PostgreSQL: $$(docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U sentinel -d sentinelbert > /dev/null 2>&1 && echo 'UP' || echo 'DOWN')"
	@echo "Redis: $$(docker-compose -f docker-compose.dev.yml exec redis redis-cli -a $${REDIS_PASSWORD:-redispass123} ping 2>/dev/null || echo 'DOWN')"

# Documentation
docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@echo "Opening README_DOCKER_DEV.md..."
	@if command -v mdcat > /dev/null 2>&1; then \
		mdcat README_DOCKER_DEV.md; \
	elif command -v bat > /dev/null 2>&1; then \
		bat README_DOCKER_DEV.md; \
	else \
		cat README_DOCKER_DEV.md; \
	fi
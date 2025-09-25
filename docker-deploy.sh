#!/bin/bash

# SentinelBERT Docker Deployment Script
# Simplified Docker-only deployment with health checks and retry logic
# Version: 2.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
SIMPLE_COMPOSE_FILE="${PROJECT_DIR}/docker-compose.simple.yml"
MACOS_COMPOSE_FILE="${PROJECT_DIR}/docker-compose.macos.yml"
MAX_RETRIES=3
RETRY_DELAY=10

# Detect OS and set appropriate compose file
if [[ "$OSTYPE" == "darwin"* ]]; then
    ACTIVE_COMPOSE_FILE="$MACOS_COMPOSE_FILE"
    OS_TYPE="macos"
else
    ACTIVE_COMPOSE_FILE="$SIMPLE_COMPOSE_FILE"
    OS_TYPE="linux"
fi

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Docker prerequisites and fix compatibility issues
check_docker() {
    print_header "Checking Docker Prerequisites"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        print_info "Install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Detect OS for platform-specific fixes
    OS_TYPE="unknown"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
        print_info "Detected macOS - applying compatibility fixes"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="linux"
        print_info "Detected Linux"
    fi
    
    # Check if Docker daemon is running
    if ! docker info > /dev/null 2>&1; then
        print_warning "Docker daemon connectivity issue detected"
        
        if [[ "$OS_TYPE" == "macos" ]]; then
            print_info "Attempting macOS Docker Desktop fix..."
            fix_macos_docker
        else
            print_error "Docker daemon is not running"
            print_info "Please start Docker and try again"
            exit 1
        fi
    fi
    
    # Apply Docker API version compatibility fix
    fix_docker_api_compatibility
    
    # Final connectivity test
    if ! docker version > /dev/null 2>&1; then
        print_error "Docker connectivity still failing after fixes"
        print_info "Manual intervention required - see MACOS_DOCKER_FIX.md"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are available and compatible"
}

# Fix macOS Docker Desktop connectivity issues
fix_macos_docker() {
    print_info "Checking Docker Desktop status on macOS..."
    
    # Check if Docker Desktop is running
    if ! pgrep -f "Docker Desktop" >/dev/null; then
        print_warning "Docker Desktop not running, attempting to start..."
        open -a Docker
        print_info "Waiting for Docker Desktop to start (60 seconds)..."
        sleep 60
        
        # Wait for Docker to be ready
        local count=0
        while ! docker version >/dev/null 2>&1 && [ $count -lt 12 ]; do
            print_info "Still waiting for Docker... ($count/12)"
            sleep 10
            count=$((count + 1))
        done
    fi
    
    # If still not working, try restart
    if ! docker version >/dev/null 2>&1; then
        print_warning "Docker still not responding, attempting restart..."
        pkill -f "Docker Desktop" 2>/dev/null || true
        pkill -f "com.docker.docker" 2>/dev/null || true
        sleep 5
        open -a Docker
        print_info "Waiting for Docker Desktop restart (90 seconds)..."
        sleep 90
    fi
}

# Fix Docker API version compatibility for all platforms
fix_docker_api_compatibility() {
    print_info "Applying Docker API version compatibility fixes..."
    
    # Set compatible API version for older daemons
    export DOCKER_API_VERSION=1.40
    
    # Add to current shell session
    if [[ -f ~/.bashrc ]]; then
        echo "export DOCKER_API_VERSION=1.40" >> ~/.bashrc
    fi
    if [[ -f ~/.zshrc ]]; then
        echo "export DOCKER_API_VERSION=1.40" >> ~/.zshrc
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Create .zshrc if it doesn't exist on macOS
        echo "export DOCKER_API_VERSION=1.40" >> ~/.zshrc
    fi
    
    # Test API compatibility
    if docker version >/dev/null 2>&1; then
        print_success "Docker API compatibility confirmed"
        
        # Get Docker version info
        local docker_version=$(docker version --format '{{.Client.Version}}' 2>/dev/null || echo "unknown")
        local api_version=$(docker version --format '{{.Client.APIVersion}}' 2>/dev/null || echo "unknown")
        print_info "Docker Client: $docker_version (API: $api_version)"
    else
        print_warning "Docker API compatibility issues persist"
        # Try with even older API version
        export DOCKER_API_VERSION=1.35
        if docker version >/dev/null 2>&1; then
            print_success "Docker working with API version 1.35"
        else
            print_error "Docker API compatibility cannot be resolved automatically"
        fi
    fi
}

# Create simplified environment file for Docker
create_docker_env() {
    print_header "Creating Docker Environment"
    
    if [[ -f "$ENV_FILE" ]]; then
        print_info "Environment file exists, backing up..."
        cp "$ENV_FILE" "${ENV_FILE}.backup"
    fi
    
    cat > "$ENV_FILE" << 'EOF'
# SentinelBERT Docker Environment
# Auto-generated for Docker deployment

# Database Configuration
POSTGRES_PASSWORD=sentinel_docker_2024
POSTGRES_DB=sentinelbert
POSTGRES_USER=sentinel

# Redis Configuration
REDIS_PASSWORD=redis_docker_2024

# Elasticsearch Configuration
ELASTIC_PASSWORD=elastic_docker_2024

# JWT Configuration
JWT_SECRET=docker_jwt_secret_key_2024_very_secure

# API Keys (Update these with your actual keys)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=SentinelBERT/1.0

YOUTUBE_API_KEY=your_youtube_api_key_here

INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=grafana_docker_2024
EOF
    
    print_success "Docker environment file created"
}

# Create simplified Docker Compose for core services
create_simplified_compose() {
    print_header "Creating Simplified Docker Compose"
    
    cat > "${PROJECT_DIR}/docker-compose.simple.yml" << 'EOF'
version: '3.8'

services:
  # Core Database
  postgres:
    image: postgres:15-alpine
    container_name: sentinelbert-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-sentinelbert}
      POSTGRES_USER: ${POSTGRES_USER:-sentinel}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - sentinelbert-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-sentinel}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: sentinelbert-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - sentinelbert-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  # NLP Service
  nlp-service:
    build:
      context: ./services/nlp
      dockerfile: Dockerfile
    container_name: sentinelbert-nlp
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - DATABASE_URL=postgresql://${POSTGRES_USER:-sentinel}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-sentinelbert}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - sentinelbert-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Streamlit Dashboard
  streamlit-dashboard:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    container_name: sentinelbert-streamlit
    environment:
      - NLP_SERVICE_URL=http://nlp-service:8000
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - DATABASE_URL=postgresql://${POSTGRES_USER:-sentinel}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-sentinelbert}
    depends_on:
      nlp-service:
        condition: service_healthy
    ports:
      - "12000:8501"
    networks:
      - sentinelbert-net
    restart: unless-stopped

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sentinelbert-frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - nlp-service
    ports:
      - "12001:80"
    networks:
      - sentinelbert-net
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  sentinelbert-net:
    driver: bridge
EOF
    
    print_success "Simplified Docker Compose created"
}

# Create macOS-compatible Docker Compose
create_macos_compose() {
    print_header "Creating macOS-Compatible Docker Compose"
    
    # Use the existing macOS compose file if it exists, otherwise create it
    if [[ ! -f "$MACOS_COMPOSE_FILE" ]]; then
        print_info "Creating macOS-compatible compose file..."
        
        cat > "$MACOS_COMPOSE_FILE" << 'EOF'
services:
  postgres:
    image: postgres:13-alpine
    container_name: sentinelbert-postgres-macos
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-sentinelbert}
      POSTGRES_USER: ${POSTGRES_USER:-sentinel}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-sentinel} -d ${POSTGRES_DB:-sentinelbert}"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:6-alpine
    container_name: sentinelbert-redis-macos
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  streamlit-app:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    container_name: sentinelbert-app-macos
    ports:
      - "12000:12000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-sentinel}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-sentinelbert}
      - REDIS_URL=redis://redis:6379
      - STREAMLIT_SERVER_PORT=12000
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    driver: bridge
EOF
        print_success "macOS-compatible Docker Compose created"
    else
        print_success "Using existing macOS-compatible Docker Compose"
    fi
}

# Create Dockerfiles if they don't exist
create_dockerfiles() {
    print_header "Creating Dockerfiles"
    
    # NLP Service Dockerfile
    if [[ ! -f "services/nlp/Dockerfile" ]]; then
        cat > "services/nlp/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
        print_success "Created NLP service Dockerfile"
    fi
    
    # Streamlit Dockerfile
    cat > "Dockerfile.streamlit" << 'EOF'
FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    software-properties-common \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose Streamlit port
EXPOSE 12000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12000/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "enhanced_viral_dashboard.py", "--server.port=12000", "--server.address=0.0.0.0", "--server.headless=true", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
EOF
    print_success "Created Streamlit Dockerfile"
    
    # Frontend Dockerfile
    if [[ ! -f "frontend/Dockerfile" ]]; then
        cat > "frontend/Dockerfile" << 'EOF'
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
        print_success "Created Frontend Dockerfile"
    fi
    
    # Create nginx config for frontend
    if [[ ! -f "frontend/nginx.conf" ]]; then
        cat > "frontend/nginx.conf" << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://nlp-service:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
        print_success "Created nginx configuration"
    fi
}

# Deploy with retry logic
deploy_with_retry() {
    local attempt=1
    
    print_info "Using compose file: $(basename "$ACTIVE_COMPOSE_FILE") for $OS_TYPE"
    
    while [[ $attempt -le $MAX_RETRIES ]]; do
        print_info "Deployment attempt $attempt of $MAX_RETRIES"
        
        if docker-compose -f "$ACTIVE_COMPOSE_FILE" up -d --build; then
            print_success "Docker services started successfully"
            return 0
        else
            print_error "Deployment attempt $attempt failed"
            
            if [[ $attempt -lt $MAX_RETRIES ]]; then
                print_info "Retrying in $RETRY_DELAY seconds..."
                sleep $RETRY_DELAY
                
                # Clean up failed containers
                docker-compose -f "$ACTIVE_COMPOSE_FILE" down --remove-orphans
            fi
        fi
        
        ((attempt++))
    done
    
    print_error "All deployment attempts failed"
    return 1
}

# Wait for services to be healthy
wait_for_services() {
    print_header "Waiting for Services to Start"
    
    local services=("postgres" "redis" "nlp-service")
    local max_wait=300  # 5 minutes
    local wait_time=0
    
    for service in "${services[@]}"; do
        print_info "Waiting for $service to be healthy..."
        
        while [[ $wait_time -lt $max_wait ]]; do
            if docker-compose -f "$ACTIVE_COMPOSE_FILE" ps | grep "$service" | grep -q "healthy\|Up"; then
                print_success "$service is ready"
                break
            fi
            
            sleep 10
            wait_time=$((wait_time + 10))
            
            if [[ $wait_time -ge $max_wait ]]; then
                print_error "$service failed to start within $max_wait seconds"
                return 1
            fi
        done
    done
    
    print_success "All core services are ready"
}

# Test service endpoints
test_services() {
    print_header "Testing Service Endpoints"
    
    local services_ok=true
    
    # Test NLP service
    if curl -f -s "http://localhost:8000/health" > /dev/null; then
        print_success "NLP service is responding"
    else
        print_error "NLP service is not responding"
        services_ok=false
    fi
    
    # Test Streamlit dashboard
    if curl -f -s "http://localhost:12000" > /dev/null; then
        print_success "Streamlit dashboard is responding"
    else
        print_warning "Streamlit dashboard may still be starting"
    fi
    
    # Test React frontend
    if curl -f -s "http://localhost:12001" > /dev/null; then
        print_success "React frontend is responding"
    else
        print_warning "React frontend may still be starting"
    fi
    
    if [[ "$services_ok" == true ]]; then
        print_success "Core services are healthy"
    else
        print_error "Some core services are not responding"
        return 1
    fi
}

# Show deployment info
show_deployment_info() {
    print_header "Deployment Complete"
    
    echo -e "${GREEN}🎉 SentinelBERT Docker deployment successful!${NC}"
    echo ""
    print_info "Access URLs:"
    echo "  🎯 Streamlit Dashboard: http://localhost:12000"
    echo "  ⚛️  React Frontend:     http://localhost:12001"
    echo "  🤖 NLP API:            http://localhost:8000"
    echo "  📊 API Documentation:  http://localhost:8000/docs"
    echo "  🗄️  PostgreSQL:        localhost:5432"
    echo "  🔴 Redis:              localhost:6379"
    echo ""
    print_info "Management commands:"
    echo "  View logs:    docker-compose -f $(basename "$ACTIVE_COMPOSE_FILE") logs -f"
    echo "  Stop all:     docker-compose -f $(basename "$ACTIVE_COMPOSE_FILE") down"
    echo "  Restart:      docker-compose -f $(basename "$ACTIVE_COMPOSE_FILE") restart"
    echo "  Clean all:    docker-compose -f $(basename "$ACTIVE_COMPOSE_FILE") down -v"
    echo ""
    print_warning "Update API keys in .env file for full social media functionality"
}

# Clean up function
cleanup() {
    print_header "Cleaning Up"
    
    docker-compose -f "$ACTIVE_COMPOSE_FILE" down --remove-orphans
    docker system prune -f
    
    print_success "Cleanup completed"
}

# Main deployment function
main() {
    case "${1:-deploy}" in
        deploy)
            check_docker
            create_docker_env
            if [[ "$OS_TYPE" == "macos" ]]; then
                create_macos_compose
            else
                create_simplified_compose
            fi
            create_dockerfiles
            deploy_with_retry
            wait_for_services
            sleep 10  # Additional wait for services to fully initialize
            test_services
            show_deployment_info
            ;;
        clean)
            cleanup
            ;;
        status)
            docker-compose -f "$ACTIVE_COMPOSE_FILE" ps
            test_services
            ;;
        logs)
            docker-compose -f "$ACTIVE_COMPOSE_FILE" logs -f
            ;;
        stop)
            docker-compose -f "$ACTIVE_COMPOSE_FILE" down
            ;;
        restart)
            docker-compose -f "$ACTIVE_COMPOSE_FILE" restart
            ;;
        *)
            echo "Usage: $0 {deploy|clean|status|logs|stop|restart}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy all services"
            echo "  clean    - Clean up all containers and volumes"
            echo "  status   - Show service status"
            echo "  logs     - Show service logs"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
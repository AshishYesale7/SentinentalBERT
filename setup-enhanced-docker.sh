#!/bin/bash

# Enhanced SentinelBERT Docker Setup Script
# Supports Linux and macOS development environments
# Indian Police Hackathon - Viral Tracking System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_info "Detected Linux environment"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS environment"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if Docker is installed and running
check_docker() {
    log_header "Checking Docker Installation"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        if [[ "$OS" == "macos" ]]; then
            log_info "Install Docker Desktop for Mac: https://docs.docker.com/desktop/mac/install/"
        else
            log_info "Install Docker for Linux: https://docs.docker.com/engine/install/"
        fi
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        if [[ "$OS" == "macos" ]]; then
            log_info "Start Docker Desktop application"
        else
            log_info "Start Docker service: sudo systemctl start docker"
        fi
        exit 1
    fi
    
    log_success "Docker is installed and running"
    docker --version
}

# Check if Docker Compose is installed
check_docker_compose() {
    log_header "Checking Docker Compose Installation"
    
    # Check for docker-compose command or docker compose plugin
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        log_success "Docker Compose (standalone) is installed"
        docker-compose --version
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
        log_success "Docker Compose (plugin) is installed"
        docker compose version
    else
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        log_info "Install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    log_header "Creating Directory Structure"
    
    directories=(
        "data/postgres"
        "data/redis"
        "data/elasticsearch"
        "data/prometheus"
        "data/grafana"
        "models/nlp"
        "models/viral"
        "cache/nlp"
        "cache/huggingface"
        "cache/viral"
        "evidence/signatures"
        "logs/backend"
        "logs/nlp"
        "logs/viral"
        "logs/evidence"
        "temp_files"
        "evidence_storage"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        else
            log_info "Directory already exists: $dir"
        fi
    done
    
    # Set proper permissions
    if [[ "$OS" == "linux" ]]; then
        # Set permissions for PostgreSQL data directory
        chmod 700 data/postgres 2>/dev/null || true
        # Set permissions for Elasticsearch data directory
        chmod 777 data/elasticsearch 2>/dev/null || true
    fi
    
    log_success "Directory structure created successfully"
}

# Setup environment file
setup_environment() {
    log_header "Setting Up Environment Configuration"
    
    if [[ ! -f ".env.enhanced" ]]; then
        log_error ".env.enhanced file not found. Please ensure it exists."
        exit 1
    fi
    
    # Copy environment file for Docker Compose
    cp .env.enhanced .env
    log_success "Environment configuration ready"
    
    # Display important environment variables
    log_info "Key configuration:"
    echo "  - Database: PostgreSQL on port 5432"
    echo "  - Redis: Redis on port 6379"
    echo "  - Elasticsearch: Elasticsearch on port 9200"
    echo "  - Dashboard: Streamlit on port 12000"
    echo "  - Monitoring: Grafana on port 3000"
    echo "  - API: Backend service on port 8080"
}

# Check system resources
check_system_resources() {
    log_header "Checking System Resources"
    
    # Check available memory
    if [[ "$OS" == "linux" ]]; then
        total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    else
        total_mem=$(sysctl -n hw.memsize | awk '{printf "%.0f", $1/1024/1024/1024}')
    fi
    
    log_info "Total system memory: ${total_mem}GB"
    
    if [[ $total_mem -lt 8 ]]; then
        log_warning "System has less than 8GB RAM. Performance may be affected."
        log_warning "Consider reducing Docker memory limits in docker-compose.enhanced.yml"
    else
        log_success "System has sufficient memory for enhanced deployment"
    fi
    
    # Check available disk space
    available_space=$(df -h . | awk 'NR==2 {print $4}')
    log_info "Available disk space: $available_space"
}

# Pull required Docker images
pull_images() {
    log_header "Pulling Required Docker Images"
    
    images=(
        "postgres:15-alpine"
        "redis:7.2-alpine"
        "docker.elastic.co/elasticsearch/elasticsearch:8.10.0"
        "prom/prometheus:latest"
        "grafana/grafana:latest"
        "jaegertracing/all-in-one:latest"
        "nginx:alpine"
        "adminer:latest"
        "rediscommander/redis-commander:latest"
        "mobz/elasticsearch-head:5"
    )
    
    for image in "${images[@]}"; do
        log_info "Pulling $image..."
        docker pull "$image" || log_warning "Failed to pull $image"
    done
    
    log_success "Docker images pulled successfully"
}

# Build custom images
build_images() {
    log_header "Building Custom Docker Images"
    
    log_info "Building enhanced dashboard image..."
    docker build -f Dockerfile.enhanced -t sentinelbert-enhanced:latest . || {
        log_error "Failed to build enhanced dashboard image"
        exit 1
    }
    
    log_success "Custom images built successfully"
}

# Start services
start_services() {
    log_header "Starting Enhanced SentinelBERT Services"
    
    log_info "Starting services with docker compose..."
    $COMPOSE_CMD -f docker-compose.enhanced.yml up -d
    
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    log_header "Checking Service Health"
    
    services=(
        "postgres:5432"
        "redis:6379"
        "elasticsearch:9200"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        log_info "Checking $name on port $port..."
        
        if nc -z localhost "$port" 2>/dev/null; then
            log_success "$name is running on port $port"
        else
            log_warning "$name is not responding on port $port"
        fi
    done
    
    # Check dashboard health
    log_info "Checking dashboard health..."
    sleep 10
    if curl -f http://localhost:12000/_stcore/health &>/dev/null; then
        log_success "Enhanced dashboard is running on port 12000"
    else
        log_warning "Dashboard health check failed, but it may still be starting"
    fi
}

# Test Twitter API connection
test_twitter_api() {
    log_header "Testing Twitter API Connection"
    
    log_info "Running Twitter API test..."
    if python3 test_twitter_api.py 2>/dev/null; then
        log_success "Twitter API connection test passed"
    else
        log_warning "Twitter API test failed or not available"
        log_info "You can run 'python3 test_twitter_api.py' manually later"
    fi
}

# Display access information
display_access_info() {
    log_header "🎉 Enhanced SentinelBERT is Ready!"
    
    echo -e "${GREEN}Access your services:${NC}"
    echo ""
    echo -e "${CYAN}📊 Enhanced Dashboard:${NC}"
    echo "   http://localhost:12000"
    echo "   http://localhost:12001 (alternative)"
    echo ""
    echo -e "${CYAN}🗄️ Database Management:${NC}"
    echo "   Adminer: http://localhost:8084"
    echo "   PostgreSQL: localhost:5432"
    echo ""
    echo -e "${CYAN}🔧 Development Tools:${NC}"
    echo "   Redis Commander: http://localhost:8085"
    echo "   Elasticsearch Head: http://localhost:9100"
    echo ""
    echo -e "${CYAN}📈 Monitoring:${NC}"
    echo "   Grafana: http://localhost:3000 (admin/admin123)"
    echo "   Prometheus: http://localhost:9090"
    echo "   Jaeger: http://localhost:16686"
    echo ""
    echo -e "${CYAN}🔌 API Services:${NC}"
    echo "   Backend API: http://localhost:8080"
    echo "   NLP Service: http://localhost:8000"
    echo "   Viral Detection: http://localhost:8083"
    echo "   Evidence Service: http://localhost:8082"
    echo ""
    echo -e "${YELLOW}🎯 For Indian Police Hackathon Demo:${NC}"
    echo "   1. Open http://localhost:12000"
    echo "   2. Navigate to 'Influence Network' tab"
    echo "   3. Select 'VIRAL ORIGIN TRACKING'"
    echo "   4. Test with @YesaleAshish or any tweet URL"
    echo ""
    echo -e "${BLUE}📋 Useful Commands:${NC}"
    echo "   View logs: docker-compose -f docker-compose.enhanced.yml logs -f"
    echo "   Stop services: docker-compose -f docker-compose.enhanced.yml down"
    echo "   Restart services: docker-compose -f docker-compose.enhanced.yml restart"
    echo "   Test API: python3 simple_demo_test.py"
    echo ""
}

# Cleanup function
cleanup_on_error() {
    log_error "Setup failed. Cleaning up..."
    $COMPOSE_CMD -f docker-compose.enhanced.yml down 2>/dev/null || true
    exit 1
}

# Main setup function
main() {
    log_header "🇮🇳 Enhanced SentinelBERT Setup"
    log_info "Indian Police Hackathon - Viral Tracking System"
    log_info "Starting enhanced Docker setup..."
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    # Run setup steps
    detect_os
    check_docker
    check_docker_compose
    check_system_resources
    create_directories
    setup_environment
    pull_images
    build_images
    start_services
    test_twitter_api
    display_access_info
    
    log_success "Enhanced SentinelBERT setup completed successfully!"
    log_info "The system is now ready for development and hackathon demo."
}

# Handle command line arguments
case "${1:-}" in
    "clean")
        log_info "Cleaning up Docker resources..."
        $COMPOSE_CMD -f docker-compose.enhanced.yml down -v
        docker system prune -f
        log_success "Cleanup completed"
        ;;
    "restart")
        log_info "Restarting services..."
        $COMPOSE_CMD -f docker-compose.enhanced.yml restart
        log_success "Services restarted"
        ;;
    "logs")
        $COMPOSE_CMD -f docker-compose.enhanced.yml logs -f
        ;;
    "status")
        $COMPOSE_CMD -f docker-compose.enhanced.yml ps
        ;;
    "test")
        test_twitter_api
        python3 simple_demo_test.py
        ;;
    *)
        main
        ;;
esac
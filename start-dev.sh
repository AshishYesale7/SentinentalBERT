#!/bin/bash

# SentinentalBERT Development Environment Startup Script
# This script sets up and starts the complete development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to create .env file if it doesn't exist
setup_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from .env.dev template..."
        cp .env.dev .env
        print_success ".env file created. Please review and modify as needed."
    else
        print_status ".env file already exists"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs evidence_storage temp_files models monitoring/grafana/dev
    print_success "Directories created"
}

# Function to pull/build images
build_images() {
    print_status "Building Docker images..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f docker-compose.dev.yml build --no-cache streamlit-dashboard
    print_success "Images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting SentinentalBERT development environment..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    # Start core services first
    print_status "Starting database services..."
    $COMPOSE_CMD -f docker-compose.dev.yml up -d postgres redis elasticsearch
    
    # Wait for databases to be ready
    print_status "Waiting for databases to be ready..."
    sleep 30
    
    # Start application services
    print_status "Starting application services..."
    $COMPOSE_CMD -f docker-compose.dev.yml up -d nlp-service backend-service evidence-service ingestion-service viral-detection
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 20
    
    # Start the main dashboard
    print_status "Starting Streamlit dashboard..."
    $COMPOSE_CMD -f docker-compose.dev.yml up -d streamlit-dashboard
    
    # Start monitoring and admin tools
    print_status "Starting monitoring and admin tools..."
    $COMPOSE_CMD -f docker-compose.dev.yml up -d adminer redis-commander prometheus grafana
    
    print_success "All services started successfully!"
}

# Function to show service status
show_status() {
    print_status "Checking service status..."
    
    # Use docker-compose or docker compose based on availability
    if command -v docker-compose > /dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD -f docker-compose.dev.yml ps
}

# Function to show access URLs
show_urls() {
    echo ""
    print_success "=== SentinentalBERT Development Environment Ready ==="
    echo ""
    echo -e "${GREEN}🚀 Main Application:${NC}"
    echo -e "   Streamlit Dashboard: ${BLUE}http://localhost:8501${NC}"
    echo ""
    echo -e "${GREEN}🔧 API Services:${NC}"
    echo -e "   Backend API:         ${BLUE}http://localhost:8080${NC}"
    echo -e "   NLP Service:         ${BLUE}http://localhost:8000${NC}"
    echo -e "   Evidence Service:    ${BLUE}http://localhost:8082${NC}"
    echo -e "   Ingestion Service:   ${BLUE}http://localhost:8081${NC}"
    echo -e "   Viral Detection:     ${BLUE}http://localhost:8083${NC}"
    echo ""
    echo -e "${GREEN}🗄️ Database Admin:${NC}"
    echo -e "   Adminer (PostgreSQL): ${BLUE}http://localhost:8084${NC}"
    echo -e "   Redis Commander:      ${BLUE}http://localhost:8085${NC}"
    echo ""
    echo -e "${GREEN}📊 Monitoring:${NC}"
    echo -e "   Prometheus:          ${BLUE}http://localhost:9090${NC}"
    echo -e "   Grafana:             ${BLUE}http://localhost:3000${NC} (admin/admin123)"
    echo ""
    echo -e "${GREEN}🔍 Search & Analytics:${NC}"
    echo -e "   Elasticsearch:       ${BLUE}http://localhost:9200${NC}"
    echo ""
    echo -e "${YELLOW}📝 Default Credentials:${NC}"
    echo -e "   PostgreSQL: sentinel/sentinelpass123"
    echo -e "   Redis: redispass123"
    echo -e "   Grafana: admin/admin123"
    echo ""
    echo -e "${BLUE}💡 Tip: Use 'docker-compose -f docker-compose.dev.yml logs -f [service-name]' to view logs${NC}"
    echo ""
}

# Function to wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for Streamlit dashboard
    for i in {1..30}; do
        if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Streamlit dashboard health check timeout"
        fi
        sleep 2
    done
    
    print_success "Services are ready!"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              SentinentalBERT Development Setup              ║"
    echo "║                                                              ║"
    echo "║  This script will set up the complete development           ║"
    echo "║  environment with all services and dependencies.            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    check_docker
    check_docker_compose
    
    # Setup environment
    setup_env_file
    create_directories
    
    # Build and start services
    build_images
    start_services
    
    # Wait for services to be ready
    wait_for_services
    
    # Show status and URLs
    show_status
    show_urls
    
    print_success "Development environment is ready! 🎉"
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "Stopping all services..."
        if command -v docker-compose > /dev/null 2>&1; then
            docker-compose -f docker-compose.dev.yml down
        else
            docker compose -f docker-compose.dev.yml down
        fi
        print_success "All services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        if command -v docker-compose > /dev/null 2>&1; then
            docker-compose -f docker-compose.dev.yml restart
        else
            docker compose -f docker-compose.dev.yml restart
        fi
        print_success "All services restarted"
        ;;
    "logs")
        if command -v docker-compose > /dev/null 2>&1; then
            docker-compose -f docker-compose.dev.yml logs -f "${2:-}"
        else
            docker compose -f docker-compose.dev.yml logs -f "${2:-}"
        fi
        ;;
    "status")
        show_status
        show_urls
        ;;
    "clean")
        print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            if command -v docker-compose > /dev/null 2>&1; then
                docker-compose -f docker-compose.dev.yml down -v --rmi all
            else
                docker compose -f docker-compose.dev.yml down -v --rmi all
            fi
            print_success "Environment cleaned"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Start the development environment"
        echo "  stop       Stop all services"
        echo "  restart    Restart all services"
        echo "  logs       Show logs (optionally for specific service)"
        echo "  status     Show service status and URLs"
        echo "  clean      Remove all containers, volumes, and images"
        echo "  help       Show this help message"
        ;;
    *)
        main
        ;;
esac
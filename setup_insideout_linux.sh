#!/bin/bash

# InsideOut Platform Setup Script for Linux
# Automated deployment script for Indian Police departments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/setup.log"
ENV_FILE="$SCRIPT_DIR/.env"

# Default values
ENVIRONMENT="production"
ENABLE_GPU=false
CLEAN_INSTALL=false
SKIP_DEPS=false
ENABLE_SSL=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to show usage
show_usage() {
    cat << EOF
InsideOut Platform Setup Script

Usage: $0 [OPTIONS]

OPTIONS:
    --prod              Production deployment with optimizations
    --dev               Development deployment with hot reload
    --gpu               Enable GPU support for ML processing
    --clean             Clean installation (removes existing data)
    --skip-deps         Skip dependency installation
    --ssl               Enable SSL/HTTPS configuration
    --help              Show this help message

EXAMPLES:
    $0                  # Basic installation
    $0 --prod --gpu     # Production with GPU support
    $0 --dev            # Development environment
    $0 --clean --prod   # Clean production installation

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod)
            ENVIRONMENT="production"
            shift
            ;;
        --dev)
            ENVIRONMENT="development"
            shift
            ;;
        --gpu)
            ENABLE_GPU=true
            shift
            ;;
        --clean)
            CLEAN_INSTALL=true
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --ssl)
            ENABLE_SSL=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This script is designed for Linux systems only"
        exit 1
    fi
    
    # Check memory
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $TOTAL_MEM -lt 8 ]]; then
        print_warning "System has ${TOTAL_MEM}GB RAM. Recommended: 16GB+ for optimal performance"
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df -BG "$SCRIPT_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $AVAILABLE_SPACE -lt 50 ]]; then
        print_error "Insufficient disk space. Available: ${AVAILABLE_SPACE}GB, Required: 50GB+"
        exit 1
    fi
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. Consider using a non-root user with sudo privileges"
    fi
    
    print_success "System requirements check completed"
}

# Function to install dependencies
install_dependencies() {
    if [[ "$SKIP_DEPS" == true ]]; then
        print_status "Skipping dependency installation"
        return
    fi
    
    print_status "Installing system dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt"
        UPDATE_CMD="apt-get update"
        INSTALL_CMD="apt-get install -y"
    elif command -v yum &> /dev/null; then
        PKG_MANAGER="yum"
        UPDATE_CMD="yum update -y"
        INSTALL_CMD="yum install -y"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
        UPDATE_CMD="dnf update -y"
        INSTALL_CMD="dnf install -y"
    else
        print_error "Unsupported package manager. Please install Docker and Docker Compose manually"
        exit 1
    fi
    
    # Update package lists
    print_status "Updating package lists..."
    sudo $UPDATE_CMD >> "$LOG_FILE" 2>&1
    
    # Install basic dependencies
    print_status "Installing basic dependencies..."
    sudo $INSTALL_CMD curl wget git unzip htop >> "$LOG_FILE" 2>&1
    
    # Install Docker
    if ! command -v docker &> /dev/null; then
        print_status "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh >> "$LOG_FILE" 2>&1
        sudo usermod -aG docker $USER
        rm get-docker.sh
        print_success "Docker installed successfully"
    else
        print_status "Docker already installed"
    fi
    
    # Install Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_status "Installing Docker Compose..."
        DOCKER_COMPOSE_VERSION="2.21.0"
        sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed successfully"
    else
        print_status "Docker Compose already installed"
    fi
    
    # Install NVIDIA Docker runtime if GPU enabled
    if [[ "$ENABLE_GPU" == true ]]; then
        print_status "Installing NVIDIA Docker runtime..."
        if command -v nvidia-smi &> /dev/null; then
            distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
            curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
            curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
            sudo apt-get update
            sudo apt-get install -y nvidia-docker2
            sudo systemctl restart docker
            print_success "NVIDIA Docker runtime installed"
        else
            print_warning "NVIDIA drivers not found. GPU support will be disabled"
            ENABLE_GPU=false
        fi
    fi
    
    print_success "Dependencies installation completed"
}

# Function to generate secure passwords
generate_passwords() {
    print_status "Generating secure passwords..."
    
    # Generate random passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    NEO4J_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    GRAFANA_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    ENCRYPTION_KEY_ID="key-$(date +%Y%m%d)-$(openssl rand -hex 4)"
    
    print_success "Secure passwords generated"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > "$ENV_FILE" << EOF
# InsideOut Platform Configuration
# Generated on $(date)

# Environment
ENVIRONMENT=$ENVIRONMENT
ENABLE_GPU=$ENABLE_GPU

# Database Passwords
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
NEO4J_PASSWORD=$NEO4J_PASSWORD

# Security
JWT_SECRET=$JWT_SECRET
ENCRYPTION_KEY_ID=$ENCRYPTION_KEY_ID

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=$GRAFANA_PASSWORD

# API Keys (Please update with your actual keys)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
YOUTUBE_API_KEY=your_youtube_api_key_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# External Services
BLOCKCHAIN_ENDPOINT=http://blockchain:8545
LEGAL_AUTHORITY_API=http://court-system:8080

# GPU Support
CUDA_VISIBLE_DEVICES=${ENABLE_GPU:+0}

EOF
    
    chmod 600 "$ENV_FILE"
    print_success "Environment file created: $ENV_FILE"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$SCRIPT_DIR/data"/{postgres,redis,elasticsearch,neo4j,models,evidence,logs}
    mkdir -p "$SCRIPT_DIR/logs"/{ingestion,nlp,backend,frontend,viral-detection,evidence}
    mkdir -p "$SCRIPT_DIR/monitoring"/{prometheus,grafana}
    mkdir -p "$SCRIPT_DIR/nginx"/{ssl,conf.d}
    
    # Set appropriate permissions
    chmod 755 "$SCRIPT_DIR/data"
    chmod 700 "$SCRIPT_DIR/data/evidence"
    
    print_success "Directories created successfully"
}

# Function to clean existing installation
clean_installation() {
    if [[ "$CLEAN_INSTALL" == true ]]; then
        print_warning "Performing clean installation..."
        
        # Stop and remove containers
        docker-compose -f docker-compose.insideout.yml down -v --remove-orphans 2>/dev/null || true
        
        # Remove data directories
        sudo rm -rf "$SCRIPT_DIR/data"
        
        # Remove Docker images
        docker system prune -af --volumes 2>/dev/null || true
        
        print_success "Clean installation completed"
    fi
}

# Function to configure SSL
configure_ssl() {
    if [[ "$ENABLE_SSL" == true ]]; then
        print_status "Configuring SSL certificates..."
        
        SSL_DIR="$SCRIPT_DIR/nginx/ssl"
        mkdir -p "$SSL_DIR"
        
        # Generate self-signed certificate for development
        if [[ "$ENVIRONMENT" == "development" ]]; then
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout "$SSL_DIR/insideout.key" \
                -out "$SSL_DIR/insideout.crt" \
                -subj "/C=IN/ST=Delhi/L=New Delhi/O=Indian Police/OU=Cyber Crime/CN=insideout.local"
            print_success "Self-signed SSL certificate generated"
        else
            print_warning "For production, please place your SSL certificates in $SSL_DIR/"
            print_warning "Required files: insideout.crt, insideout.key"
        fi
    fi
}

# Function to create monitoring configuration
create_monitoring_config() {
    print_status "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > "$SCRIPT_DIR/monitoring/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'insideout-backend'
    static_configs:
      - targets: ['backend-service:8080']
    metrics_path: '/actuator/prometheus'

  - job_name: 'insideout-nlp'
    static_configs:
      - targets: ['nlp-service:8000']
    metrics_path: '/metrics'

  - job_name: 'insideout-viral-detection'
    static_configs:
      - targets: ['viral-detection-service:8001']
    metrics_path: '/metrics'

  - job_name: 'insideout-evidence'
    static_configs:
      - targets: ['evidence-service:8002']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    
    print_success "Monitoring configuration created"
}

# Function to build and deploy services
deploy_services() {
    print_status "Building and deploying InsideOut services..."
    
    cd "$SCRIPT_DIR"
    
    # Set Docker Compose file
    COMPOSE_FILE="docker-compose.insideout.yml"
    
    # Add GPU support if enabled
    if [[ "$ENABLE_GPU" == true ]]; then
        export COMPOSE_FILE="$COMPOSE_FILE:docker-compose.gpu.yml"
    fi
    
    # Build services
    print_status "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --parallel >> "$LOG_FILE" 2>&1
    
    # Start services
    print_status "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d >> "$LOG_FILE" 2>&1
    
    print_success "Services deployment completed"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for PostgreSQL..."
    timeout 300 bash -c 'until docker-compose -f docker-compose.insideout.yml exec -T postgres pg_isready -U insideout -d insideout; do sleep 5; done'
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout 300 bash -c 'until docker-compose -f docker-compose.insideout.yml exec -T redis redis-cli ping; do sleep 5; done'
    
    # Wait for ElasticSearch
    print_status "Waiting for ElasticSearch..."
    timeout 300 bash -c 'until curl -f http://localhost:9200/_cluster/health; do sleep 10; done' >> "$LOG_FILE" 2>&1
    
    # Wait for services
    print_status "Waiting for application services..."
    sleep 60
    
    print_success "All services are ready"
}

# Function to initialize database
initialize_database() {
    print_status "Initializing database..."
    
    # Run database migrations
    docker-compose -f docker-compose.insideout.yml exec -T postgres psql -U insideout -d insideout -f /docker-entrypoint-initdb.d/01-schema.sql >> "$LOG_FILE" 2>&1
    
    # Create ElasticSearch indices
    curl -X PUT "localhost:9200/social_posts" \
        -H "Content-Type: application/json" \
        -d '{"settings": {"number_of_shards": 3, "number_of_replicas": 1}}' >> "$LOG_FILE" 2>&1
    
    curl -X PUT "localhost:9200/viral_clusters" \
        -H "Content-Type: application/json" \
        -d '{"settings": {"number_of_shards": 2, "number_of_replicas": 1}}' >> "$LOG_FILE" 2>&1
    
    print_success "Database initialization completed"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Check service health
    SERVICES=("postgres:5432" "redis:6379" "elasticsearch:9200" "backend-service:8080" "nlp-service:8000" "viral-detection-service:8001" "evidence-service:8002" "dashboard:80")
    
    for service in "${SERVICES[@]}"; do
        SERVICE_NAME=$(echo $service | cut -d':' -f1)
        SERVICE_PORT=$(echo $service | cut -d':' -f2)
        
        if docker-compose -f docker-compose.insideout.yml ps | grep -q "$SERVICE_NAME.*Up"; then
            print_success "$SERVICE_NAME is running"
        else
            print_error "$SERVICE_NAME is not running"
        fi
    done
    
    # Test API endpoints
    print_status "Testing API endpoints..."
    
    # Test backend health
    if curl -f http://localhost:8080/actuator/health >> "$LOG_FILE" 2>&1; then
        print_success "Backend API is healthy"
    else
        print_warning "Backend API health check failed"
    fi
    
    # Test NLP service
    if curl -f http://localhost:8000/health >> "$LOG_FILE" 2>&1; then
        print_success "NLP service is healthy"
    else
        print_warning "NLP service health check failed"
    fi
    
    # Test viral detection service
    if curl -f http://localhost:8001/health >> "$LOG_FILE" 2>&1; then
        print_success "Viral detection service is healthy"
    else
        print_warning "Viral detection service health check failed"
    fi
    
    # Test evidence service
    if curl -f http://localhost:8002/health >> "$LOG_FILE" 2>&1; then
        print_success "Evidence service is healthy"
    else
        print_warning "Evidence service health check failed"
    fi
    
    print_success "Deployment verification completed"
}

# Function to show access information
show_access_info() {
    print_success "InsideOut Platform deployment completed successfully!"
    echo
    echo "=== ACCESS INFORMATION ==="
    echo
    echo "🌐 InsideOut Dashboard:"
    echo "   URL: http://localhost:3000"
    echo "   Default Login: admin / admin123"
    echo
    echo "🔧 Backend API:"
    echo "   URL: http://localhost:8080/api"
    echo "   Documentation: http://localhost:8080/swagger-ui.html"
    echo
    echo "📊 Monitoring:"
    echo "   Grafana: http://localhost:3001 (admin / $GRAFANA_PASSWORD)"
    echo "   Prometheus: http://localhost:9090"
    echo "   Jaeger: http://localhost:16686"
    echo
    echo "🗄️ Databases:"
    echo "   PostgreSQL: localhost:5432 (insideout / $POSTGRES_PASSWORD)"
    echo "   Redis: localhost:6379"
    echo "   ElasticSearch: http://localhost:9200"
    echo "   Neo4j: http://localhost:7474 (neo4j / $NEO4J_PASSWORD)"
    echo
    echo "📝 Configuration:"
    echo "   Environment file: $ENV_FILE"
    echo "   Log file: $LOG_FILE"
    echo
    echo "⚠️  IMPORTANT SECURITY NOTES:"
    echo "   1. Change default passwords in production"
    echo "   2. Update API keys in $ENV_FILE"
    echo "   3. Configure SSL certificates for production"
    echo "   4. Restrict network access as needed"
    echo
    echo "📚 Next Steps:"
    echo "   1. Update API keys in the environment file"
    echo "   2. Configure user accounts and permissions"
    echo "   3. Set up backup procedures"
    echo "   4. Review security settings"
    echo
}

# Function to show quick commands
show_quick_commands() {
    echo "=== QUICK COMMANDS ==="
    echo
    echo "Start services:"
    echo "  docker-compose -f docker-compose.insideout.yml up -d"
    echo
    echo "Stop services:"
    echo "  docker-compose -f docker-compose.insideout.yml down"
    echo
    echo "View logs:"
    echo "  docker-compose -f docker-compose.insideout.yml logs -f [service-name]"
    echo
    echo "Check status:"
    echo "  docker-compose -f docker-compose.insideout.yml ps"
    echo
    echo "Scale services:"
    echo "  docker-compose -f docker-compose.insideout.yml up -d --scale nlp-service=3"
    echo
    echo "Update services:"
    echo "  git pull && docker-compose -f docker-compose.insideout.yml build && docker-compose -f docker-compose.insideout.yml up -d"
    echo
}

# Main execution
main() {
    echo "=== InsideOut Platform Setup ==="
    echo "Starting deployment for Indian Police departments..."
    echo
    
    # Initialize log file
    echo "Setup started at $(date)" > "$LOG_FILE"
    
    # Run setup steps
    check_system_requirements
    install_dependencies
    generate_passwords
    create_env_file
    create_directories
    clean_installation
    configure_ssl
    create_monitoring_config
    deploy_services
    wait_for_services
    initialize_database
    verify_deployment
    
    # Show results
    show_access_info
    show_quick_commands
    
    print_success "Setup completed successfully!"
}

# Run main function
main "$@"
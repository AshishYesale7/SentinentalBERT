#!/bin/bash

# =============================================================================
# SentinelBERT Automated Setup Script
# =============================================================================
# 
# This script automates the complete setup and deployment of SentinelBERT
# for local development and testing environments.
# 
# Features:
# - System dependency checking and installation
# - Environment configuration
# - Database initialization
# - Service deployment
# - Health checks and verification
# - Monitoring setup
# 
# Usage:
#   chmod +x setup.sh
#   ./setup.sh [options]
# 
# Options:
#   --dev          Setup for development (with hot reload)
#   --prod         Setup for production
#   --gpu          Enable GPU support for ML processing
#   --no-build     Skip Docker image building
#   --clean        Clean existing data and start fresh
#   --help         Show this help message
# 
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="sentinelbert"
LOG_FILE="${SCRIPT_DIR}/setup.log"
COMPOSE_FILE="docker-compose.yml"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default options
ENVIRONMENT="development"
GPU_SUPPORT=false
SKIP_BUILD=false
CLEAN_INSTALL=false
VERBOSE=false

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print info message
info() {
    print_color $BLUE "[INFO] $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

# Print success message
success() {
    print_color $GREEN "[SUCCESS] $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" >> "$LOG_FILE"
}

# Print warning message
warn() {
    print_color $YELLOW "[WARNING] $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1" >> "$LOG_FILE"
}

# Print error message
error() {
    print_color $RED "[ERROR] $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
}

# Print step header
step() {
    print_color $PURPLE "\n=== $1 ==="
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [STEP] $1" >> "$LOG_FILE"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if port is available
port_available() {
    local port=$1
    ! nc -z localhost "$port" >/dev/null 2>&1
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local health_url=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" >/dev/null 2>&1; then
            success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# =============================================================================
# SYSTEM REQUIREMENTS CHECK
# =============================================================================

check_system_requirements() {
    step "Checking System Requirements"
    
    # Check operating system
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        info "Operating System: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        info "Operating System: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        info "Operating System: Windows (WSL/Cygwin)"
    else
        warn "Unsupported operating system: $OSTYPE"
    fi
    
    # Check available memory
    if command_exists free; then
        local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$memory_gb" -lt 8 ]; then
            warn "Low memory detected: ${memory_gb}GB. Recommended: 16GB+"
        else
            info "Available memory: ${memory_gb}GB"
        fi
    fi
    
    # Check available disk space
    local disk_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$disk_space" -lt 20 ]; then
        warn "Low disk space: ${disk_space}GB. Recommended: 50GB+"
    else
        info "Available disk space: ${disk_space}GB"
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "curl" "git")
    local missing_commands=()
    
    for cmd in "${required_commands[@]}"; do
        if command_exists "$cmd"; then
            info "✓ $cmd is installed"
        else
            missing_commands+=("$cmd")
        fi
    done
    
    if [ ${#missing_commands[@]} -ne 0 ]; then
        error "Missing required commands: ${missing_commands[*]}"
        info "Please install missing dependencies and run the script again"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon is not running"
        info "Please start Docker and run the script again"
        exit 1
    fi
    
    success "System requirements check completed"
}

# =============================================================================
# DEPENDENCY INSTALLATION
# =============================================================================

install_dependencies() {
    step "Installing Dependencies"
    
    # Detect package manager and install dependencies
    if command_exists apt-get; then
        info "Using apt package manager"
        sudo apt-get update
        sudo apt-get install -y curl wget git unzip jq
    elif command_exists yum; then
        info "Using yum package manager"
        sudo yum update -y
        sudo yum install -y curl wget git unzip jq
    elif command_exists brew; then
        info "Using Homebrew package manager"
        brew update
        brew install curl wget git jq
    else
        warn "No supported package manager found. Please install dependencies manually."
    fi
    
    # Install Docker if not present
    if ! command_exists docker; then
        info "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        warn "Please log out and log back in for Docker group changes to take effect"
    fi
    
    # Install Docker Compose if not present
    if ! command_exists docker-compose; then
        info "Installing Docker Compose..."
        local compose_version="2.23.0"
        sudo curl -L "https://github.com/docker/compose/releases/download/v${compose_version}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    success "Dependencies installation completed"
}

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

setup_environment() {
    step "Setting Up Environment Configuration"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        info "Creating .env file from template..."
        cp .env.example .env
        
        # Generate secure passwords and keys
        info "Generating secure passwords and keys..."
        
        # Generate random passwords
        local postgres_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        local redis_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        local jwt_secret=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
        local encryption_key=$(openssl rand -base64 32)
        local hash_salt=$(openssl rand -base64 16)
        
        # Update .env file with generated values
        sed -i "s/CHANGE_ME_SECURE_PASSWORD_HERE/$postgres_password/g" .env
        sed -i "s/CHANGE_ME_REDIS_PASSWORD_HERE/$redis_password/g" .env
        sed -i "s/CHANGE_ME_JWT_SECRET_MINIMUM_32_CHARACTERS_LONG/$jwt_secret/g" .env
        sed -i "s/CHANGE_ME_ENCRYPTION_KEY_HERE/$encryption_key/g" .env
        sed -i "s/CHANGE_ME_HASH_SALT_HERE/$hash_salt/g" .env
        
        success "Environment file created with secure passwords"
        warn "Please edit .env file to add your social media API keys"
    else
        info ".env file already exists"
    fi
    
    # Create necessary directories
    info "Creating necessary directories..."
    mkdir -p data/{postgres,redis,elasticsearch,prometheus,grafana,models}
    mkdir -p logs/{ingestion,nlp,backend,frontend,nginx}
    mkdir -p database/{init,elasticsearch}
    mkdir -p monitoring/{prometheus,grafana}
    mkdir -p nginx/{ssl,conf.d}
    
    # Set proper permissions
    chmod 755 data logs database monitoring nginx
    chmod -R 755 data/* logs/* 2>/dev/null || true
    
    success "Environment configuration completed"
}

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

initialize_databases() {
    step "Initializing Databases"
    
    # Create PostgreSQL initialization script if it doesn't exist
    if [ ! -f "database/init/01-init.sql" ]; then
        info "Creating PostgreSQL initialization script..."
        cat > database/init/01-init.sql << 'EOF'
-- SentinelBERT Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create main tables
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    author_id_hash VARCHAR(64) NOT NULL,
    author_username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sentiment_score DECIMAL(5,4),
    indexed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_social_posts_platform_created 
    ON social_posts(platform, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_content_gin 
    ON social_posts USING gin(to_tsvector('english', content));

-- Create users table
CREATE TABLE IF NOT EXISTS app_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'VIEWER',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin123)
INSERT INTO app_users (username, email, password_hash, role) 
VALUES (
    'admin', 
    'admin@sentinelbert.local', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PZvO.S', 
    'ADMIN'
) ON CONFLICT (username) DO NOTHING;
EOF
        success "PostgreSQL initialization script created"
    fi
    
    # Create ElasticSearch index template
    if [ ! -f "database/elasticsearch/social_posts_template.json" ]; then
        info "Creating ElasticSearch index template..."
        cat > database/elasticsearch/social_posts_template.json << 'EOF'
{
  "index_patterns": ["social_posts*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1
    },
    "mappings": {
      "properties": {
        "id": {"type": "keyword"},
        "platform": {"type": "keyword"},
        "content": {"type": "text"},
        "author_username": {"type": "keyword"},
        "created_at": {"type": "date"},
        "sentiment_score": {"type": "float"}
      }
    }
  }
}
EOF
        success "ElasticSearch index template created"
    fi
    
    success "Database initialization completed"
}

# =============================================================================
# MONITORING SETUP
# =============================================================================

setup_monitoring() {
    step "Setting Up Monitoring Configuration"
    
    # Create Prometheus configuration
    if [ ! -f "monitoring/prometheus/prometheus.yml" ]; then
        info "Creating Prometheus configuration..."
        mkdir -p monitoring/prometheus
        cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'sentinelbert-backend'
    static_configs:
      - targets: ['backend-service:8080']
    metrics_path: '/api/actuator/prometheus'

  - job_name: 'sentinelbert-nlp'
    static_configs:
      - targets: ['nlp-service:8000']
    metrics_path: '/metrics'

  - job_name: 'sentinelbert-ingestion'
    static_configs:
      - targets: ['ingestion-service:8081']
    metrics_path: '/metrics'
EOF
        success "Prometheus configuration created"
    fi
    
    # Create Grafana provisioning
    if [ ! -d "monitoring/grafana/provisioning" ]; then
        info "Creating Grafana provisioning configuration..."
        mkdir -p monitoring/grafana/provisioning/{datasources,dashboards}
        
        cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
        
        cat > monitoring/grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
EOF
        success "Grafana provisioning configuration created"
    fi
    
    success "Monitoring setup completed"
}

# =============================================================================
# SERVICE DEPLOYMENT
# =============================================================================

deploy_services() {
    step "Deploying Services"
    
    # Set compose file based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        COMPOSE_FILE="docker-compose.yml -f docker-compose.dev.yml"
    fi
    
    # Clean existing containers if requested
    if [ "$CLEAN_INSTALL" = true ]; then
        info "Cleaning existing containers and volumes..."
        docker-compose down -v --remove-orphans 2>/dev/null || true
        docker system prune -f
    fi
    
    # Build images if not skipping
    if [ "$SKIP_BUILD" = false ]; then
        info "Building Docker images..."
        if [ "$GPU_SUPPORT" = true ]; then
            docker-compose -f $COMPOSE_FILE build --build-arg CUDA_VERSION=11.8
        else
            docker-compose -f $COMPOSE_FILE build
        fi
        success "Docker images built successfully"
    fi
    
    # Start services
    info "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    success "Services deployment initiated"
}

# =============================================================================
# HEALTH CHECKS
# =============================================================================

verify_deployment() {
    step "Verifying Deployment"
    
    # Wait for database services
    info "Waiting for database services..."
    sleep 30
    
    # Check PostgreSQL
    if wait_for_service "PostgreSQL" "http://localhost:5432" 15; then
        success "PostgreSQL is ready"
    else
        error "PostgreSQL failed to start"
        return 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        success "Redis is ready"
    else
        error "Redis failed to start"
        return 1
    fi
    
    # Check ElasticSearch
    if wait_for_service "ElasticSearch" "http://localhost:9200/_cluster/health" 20; then
        success "ElasticSearch is ready"
    else
        error "ElasticSearch failed to start"
        return 1
    fi
    
    # Wait for application services
    info "Waiting for application services..."
    sleep 60
    
    # Check NLP service
    if wait_for_service "NLP Service" "http://localhost:8000/health" 30; then
        success "NLP Service is ready"
    else
        error "NLP Service failed to start"
        return 1
    fi
    
    # Check Backend service
    if wait_for_service "Backend Service" "http://localhost:8080/api/actuator/health" 30; then
        success "Backend Service is ready"
    else
        error "Backend Service failed to start"
        return 1
    fi
    
    # Check Frontend
    if wait_for_service "Frontend" "http://localhost:3000/health" 15; then
        success "Frontend is ready"
    else
        error "Frontend failed to start"
        return 1
    fi
    
    # Initialize ElasticSearch indices
    info "Initializing ElasticSearch indices..."
    sleep 10
    curl -X PUT "localhost:9200/_index_template/social_posts_template" \
         -H "Content-Type: application/json" \
         -d @database/elasticsearch/social_posts_template.json >/dev/null 2>&1 || true
    
    success "Deployment verification completed"
}

# =============================================================================
# POST-DEPLOYMENT TASKS
# =============================================================================

post_deployment() {
    step "Post-Deployment Tasks"
    
    # Display service URLs
    info "Service URLs:"
    echo "  Frontend Dashboard: http://localhost:3000"
    echo "  Backend API: http://localhost:8080/api"
    echo "  Grafana: http://localhost:3001 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
    echo "  Jaeger: http://localhost:16686"
    
    # Display default credentials
    info "Default Credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    
    # Display next steps
    info "Next Steps:"
    echo "  1. Edit .env file to add your social media API keys"
    echo "  2. Access the dashboard at http://localhost:3000"
    echo "  3. Check logs with: docker-compose logs -f"
    echo "  4. Stop services with: docker-compose down"
    
    # Create quick commands script
    cat > quick-commands.sh << 'EOF'
#!/bin/bash
# SentinelBERT Quick Commands

case "$1" in
    "start")
        docker-compose up -d
        ;;
    "stop")
        docker-compose down
        ;;
    "restart")
        docker-compose restart
        ;;
    "logs")
        docker-compose logs -f ${2:-}
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        docker-compose down -v
        docker system prune -f
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|clean}"
        echo "  logs [service] - View logs for specific service"
        ;;
esac
EOF
    chmod +x quick-commands.sh
    
    success "Post-deployment tasks completed"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

show_help() {
    cat << EOF
SentinelBERT Setup Script

Usage: $0 [OPTIONS]

OPTIONS:
    --dev           Setup for development environment
    --prod          Setup for production environment
    --gpu           Enable GPU support for ML processing
    --no-build      Skip Docker image building
    --clean         Clean existing data and start fresh
    --verbose       Enable verbose output
    --help          Show this help message

EXAMPLES:
    $0                    # Default development setup
    $0 --prod --gpu       # Production setup with GPU support
    $0 --clean --dev      # Clean development setup
    $0 --no-build         # Quick start without rebuilding images

EOF
}

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                ENVIRONMENT="development"
                shift
                ;;
            --prod)
                ENVIRONMENT="production"
                shift
                ;;
            --gpu)
                GPU_SUPPORT=true
                shift
                ;;
            --no-build)
                SKIP_BUILD=true
                shift
                ;;
            --clean)
                CLEAN_INSTALL=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                set -x
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Initialize log file
    echo "SentinelBERT Setup Log - $(date)" > "$LOG_FILE"
    
    # Print banner
    print_color $CYAN "
╔═══════════════════════════════════════════════════════════════╗
║                     SentinelBERT Setup                       ║
║          Multi-Platform Sentiment Analysis System            ║
╚═══════════════════════════════════════════════════════════════╝
"
    
    info "Starting SentinelBERT setup in $ENVIRONMENT mode..."
    info "GPU Support: $GPU_SUPPORT"
    info "Skip Build: $SKIP_BUILD"
    info "Clean Install: $CLEAN_INSTALL"
    
    # Execute setup steps
    check_system_requirements
    setup_environment
    initialize_databases
    setup_monitoring
    deploy_services
    verify_deployment
    post_deployment
    
    # Final success message
    print_color $GREEN "
╔═══════════════════════════════════════════════════════════════╗
║                 🎉 SETUP COMPLETED SUCCESSFULLY! 🎉          ║
║                                                               ║
║  SentinelBERT is now running and ready for use!             ║
║  Access the dashboard at: http://localhost:3000              ║
║                                                               ║
║  Check the logs: tail -f $LOG_FILE                           ║
╚═══════════════════════════════════════════════════════════════╝
"
}

# Run main function with all arguments
main "$@"
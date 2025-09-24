#!/bin/bash

# SentinelBERT Complete Deployment Script
# Supports macOS, Linux, and Docker deployments
# Version: 2.0
# Author: Team Code X

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="SentinelBERT"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${PROJECT_DIR}/deployment.log"
ENV_FILE="${PROJECT_DIR}/.env"

# Deployment modes
DOCKER_MODE=false
NATIVE_MODE=false
DEV_MODE=false
FORCE_REINSTALL=false

# Service ports
NLP_PORT=8000
FRONTEND_PORT=12001
STREAMLIT_PORT=12000
BACKEND_PORT=8080

# Print functions
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

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    echo "$1"
}

# Help function
show_help() {
    cat << EOF
SentinelBERT Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -d, --docker        Deploy using Docker Compose
    -n, --native        Deploy natively (macOS/Linux)
    -v, --dev           Development mode (with hot reload)
    -f, --force         Force reinstall all dependencies
    -h, --help          Show this help message
    --clean             Clean all containers and volumes
    --status            Check deployment status
    --logs              Show service logs
    --stop              Stop all services

EXAMPLES:
    $0 --docker         # Deploy with Docker
    $0 --native         # Deploy natively
    $0 --dev --native   # Development mode
    $0 --clean          # Clean deployment
    $0 --status         # Check status

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--docker)
                DOCKER_MODE=true
                shift
                ;;
            -n|--native)
                NATIVE_MODE=true
                shift
                ;;
            -v|--dev)
                DEV_MODE=true
                shift
                ;;
            -f|--force)
                FORCE_REINSTALL=true
                shift
                ;;
            --clean)
                clean_deployment
                exit 0
                ;;
            --status)
                check_deployment_status
                exit 0
                ;;
            --logs)
                show_logs
                exit 0
                ;;
            --stop)
                stop_services
                exit 0
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Default to native mode if no mode specified
    if [[ "$DOCKER_MODE" == false && "$NATIVE_MODE" == false ]]; then
        NATIVE_MODE=true
    fi
}

# System detection
detect_system() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        SYSTEM="macos"
        print_info "Detected macOS system"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        SYSTEM="linux"
        print_info "Detected Linux system"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python $python_version found"
    fi
    
    # Check Node.js for frontend
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    else
        node_version=$(node --version)
        print_success "Node.js $node_version found"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    else
        npm_version=$(npm --version)
        print_success "npm $npm_version found"
    fi
    
    # Docker mode specific checks
    if [[ "$DOCKER_MODE" == true ]]; then
        if ! command -v docker &> /dev/null; then
            missing_deps+=("docker")
        else
            print_success "Docker found"
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            missing_deps+=("docker-compose")
        else
            print_success "Docker Compose found"
        fi
    fi
    
    # Report missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Please install missing dependencies and run again"
        
        if [[ "$SYSTEM" == "macos" ]]; then
            print_info "Install with Homebrew:"
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    python3) echo "  brew install python" ;;
                    node) echo "  brew install node" ;;
                    npm) echo "  brew install npm" ;;
                    docker) echo "  brew install --cask docker" ;;
                    docker-compose) echo "  brew install docker-compose" ;;
                esac
            done
        elif [[ "$SYSTEM" == "linux" ]]; then
            print_info "Install with package manager (Ubuntu/Debian):"
            for dep in "${missing_deps[@]}"; do
                case $dep in
                    python3) echo "  sudo apt-get install python3 python3-pip" ;;
                    node) echo "  sudo apt-get install nodejs" ;;
                    npm) echo "  sudo apt-get install npm" ;;
                    docker) echo "  sudo apt-get install docker.io" ;;
                    docker-compose) echo "  sudo apt-get install docker-compose" ;;
                esac
            done
        fi
        exit 1
    fi
}

# Create environment file
create_env_file() {
    print_header "Creating Environment Configuration"
    
    if [[ -f "$ENV_FILE" && "$FORCE_REINSTALL" == false ]]; then
        print_info "Environment file exists, skipping creation"
        return
    fi
    
    cat > "$ENV_FILE" << EOF
# SentinelBERT Environment Configuration
# Generated on $(date)

# Database Configuration
POSTGRES_PASSWORD=sentinel_secure_2024
DB_HOST=localhost
DB_NAME=sentinelbert
DB_USER=sentinel
DB_PASSWORD=sentinel_secure_2024

# Redis Configuration
REDIS_PASSWORD=redis_secure_2024
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_SSL=false

# Elasticsearch Configuration
ELASTIC_PASSWORD=elastic_secure_2024

# JWT Configuration
JWT_SECRET=your_super_secure_jwt_secret_key_here_2024

# API Keys (Replace with your actual keys)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=SentinelBERT/1.0

YOUTUBE_API_KEY=your_youtube_api_key

INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin_secure_2024

# Service URLs
NLP_SERVICE_URL=http://localhost:${NLP_PORT}
BACKEND_SERVICE_URL=http://localhost:${BACKEND_PORT}
FRONTEND_URL=http://localhost:${FRONTEND_PORT}
STREAMLIT_URL=http://localhost:${STREAMLIT_PORT}

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
    
    print_success "Environment file created at $ENV_FILE"
    print_warning "Please update API keys in $ENV_FILE before running services"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" || "$FORCE_REINSTALL" == true ]]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install main requirements
    if [[ -f "requirements.txt" ]]; then
        print_info "Installing main requirements..."
        pip install -r requirements.txt
    fi
    
    # Install NLP service requirements
    if [[ -f "services/nlp/requirements.txt" ]]; then
        print_info "Installing NLP service requirements..."
        pip install -r services/nlp/requirements.txt
    fi
    
    # Install additional real-time dependencies
    print_info "Installing real-time data dependencies..."
    pip install tweepy praw google-api-python-client psycopg2-binary
    
    print_success "Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    print_header "Installing Node.js Dependencies"
    
    if [[ -d "frontend" ]]; then
        cd frontend
        
        if [[ ! -d "node_modules" || "$FORCE_REINSTALL" == true ]]; then
            print_info "Installing frontend dependencies..."
            npm install
        else
            print_info "Frontend dependencies already installed"
        fi
        
        cd ..
        print_success "Node.js dependencies installed"
    else
        print_warning "Frontend directory not found, skipping Node.js dependencies"
    fi
}

# Setup database
setup_database() {
    print_header "Setting up Database"
    
    if [[ "$DOCKER_MODE" == true ]]; then
        print_info "Database will be set up via Docker Compose"
        return
    fi
    
    # Check if PostgreSQL is running
    if ! pgrep -x "postgres" > /dev/null; then
        print_info "Starting PostgreSQL..."
        if [[ "$SYSTEM" == "macos" ]]; then
            brew services start postgresql
        elif [[ "$SYSTEM" == "linux" ]]; then
            sudo systemctl start postgresql
        fi
    fi
    
    # Create database and user
    print_info "Creating database and user..."
    createdb sentinelbert 2>/dev/null || print_info "Database already exists"
    
    # Run SQL schema if exists
    if [[ -f "sql/enhanced_tracking_schema.sql" ]]; then
        print_info "Running database schema..."
        psql -d sentinelbert -f sql/enhanced_tracking_schema.sql
    fi
    
    print_success "Database setup completed"
}

# Start services in native mode
start_native_services() {
    print_header "Starting Native Services"
    
    # Load environment variables
    source "$ENV_FILE"
    source venv/bin/activate
    
    # Create logs directory
    mkdir -p logs
    
    # Start NLP service
    print_info "Starting NLP service on port $NLP_PORT..."
    cd services/nlp
    uvicorn main:app --host 0.0.0.0 --port $NLP_PORT --reload > ../../logs/nlp_service.log 2>&1 &
    NLP_PID=$!
    echo $NLP_PID > ../../logs/nlp_service.pid
    cd ../..
    
    # Wait for NLP service to start
    sleep 5
    
    # Start Streamlit dashboard
    print_info "Starting Streamlit dashboard on port $STREAMLIT_PORT..."
    streamlit run enhanced_viral_dashboard.py --server.port $STREAMLIT_PORT --server.address 0.0.0.0 --server.headless true > logs/streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > logs/streamlit.pid
    
    # Start React frontend
    if [[ -d "frontend" ]]; then
        print_info "Starting React frontend on port $FRONTEND_PORT..."
        cd frontend
        npm start > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../logs/frontend.pid
        cd ..
    fi
    
    # Save all PIDs
    cat > logs/all_services.pid << EOF
NLP_PID=$NLP_PID
STREAMLIT_PID=$STREAMLIT_PID
FRONTEND_PID=$FRONTEND_PID
EOF
    
    print_success "All services started successfully"
}

# Start services in Docker mode
start_docker_services() {
    print_header "Starting Docker Services"
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Build and start services
    print_info "Building and starting Docker services..."
    docker-compose up -d --build
    
    print_success "Docker services started successfully"
}

# Check service health
check_service_health() {
    print_header "Checking Service Health"
    
    local services_healthy=true
    
    # Check NLP service
    if curl -f -s "http://localhost:$NLP_PORT/health" > /dev/null; then
        print_success "NLP service is healthy"
    else
        print_error "NLP service is not responding"
        services_healthy=false
    fi
    
    # Check Streamlit dashboard
    if curl -f -s "http://localhost:$STREAMLIT_PORT" > /dev/null; then
        print_success "Streamlit dashboard is healthy"
    else
        print_error "Streamlit dashboard is not responding"
        services_healthy=false
    fi
    
    # Check React frontend
    if curl -f -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
        print_success "React frontend is healthy"
    else
        print_warning "React frontend is not responding (may still be starting)"
    fi
    
    if [[ "$services_healthy" == true ]]; then
        print_success "All critical services are healthy"
    else
        print_error "Some services are not healthy. Check logs for details."
    fi
}

# Show deployment status
check_deployment_status() {
    print_header "Deployment Status"
    
    if [[ "$DOCKER_MODE" == true ]]; then
        docker-compose ps
    else
        print_info "Checking native services..."
        
        # Check if PID files exist and processes are running
        if [[ -f "logs/nlp_service.pid" ]]; then
            nlp_pid=$(cat logs/nlp_service.pid)
            if ps -p $nlp_pid > /dev/null; then
                print_success "NLP service running (PID: $nlp_pid)"
            else
                print_error "NLP service not running"
            fi
        fi
        
        if [[ -f "logs/streamlit.pid" ]]; then
            streamlit_pid=$(cat logs/streamlit.pid)
            if ps -p $streamlit_pid > /dev/null; then
                print_success "Streamlit dashboard running (PID: $streamlit_pid)"
            else
                print_error "Streamlit dashboard not running"
            fi
        fi
        
        if [[ -f "logs/frontend.pid" ]]; then
            frontend_pid=$(cat logs/frontend.pid)
            if ps -p $frontend_pid > /dev/null; then
                print_success "React frontend running (PID: $frontend_pid)"
            else
                print_error "React frontend not running"
            fi
        fi
    fi
    
    check_service_health
}

# Show service logs
show_logs() {
    print_header "Service Logs"
    
    if [[ "$DOCKER_MODE" == true ]]; then
        docker-compose logs --tail=50 -f
    else
        print_info "Showing native service logs..."
        
        if [[ -f "logs/nlp_service.log" ]]; then
            echo -e "${BLUE}=== NLP Service Logs ===${NC}"
            tail -20 logs/nlp_service.log
        fi
        
        if [[ -f "logs/streamlit.log" ]]; then
            echo -e "${BLUE}=== Streamlit Dashboard Logs ===${NC}"
            tail -20 logs/streamlit.log
        fi
        
        if [[ -f "logs/frontend.log" ]]; then
            echo -e "${BLUE}=== Frontend Logs ===${NC}"
            tail -20 logs/frontend.log
        fi
    fi
}

# Stop services
stop_services() {
    print_header "Stopping Services"
    
    if [[ "$DOCKER_MODE" == true ]]; then
        docker-compose down
    else
        # Stop native services
        if [[ -f "logs/all_services.pid" ]]; then
            source logs/all_services.pid
            
            [[ -n "$NLP_PID" ]] && kill $NLP_PID 2>/dev/null && print_info "Stopped NLP service"
            [[ -n "$STREAMLIT_PID" ]] && kill $STREAMLIT_PID 2>/dev/null && print_info "Stopped Streamlit dashboard"
            [[ -n "$FRONTEND_PID" ]] && kill $FRONTEND_PID 2>/dev/null && print_info "Stopped React frontend"
            
            # Clean up PID files
            rm -f logs/*.pid
        fi
        
        # Kill any remaining processes
        pkill -f "uvicorn main:app" 2>/dev/null || true
        pkill -f "streamlit run" 2>/dev/null || true
        pkill -f "react-scripts start" 2>/dev/null || true
    fi
    
    print_success "All services stopped"
}

# Clean deployment
clean_deployment() {
    print_header "Cleaning Deployment"
    
    # Stop services first
    stop_services
    
    if [[ "$DOCKER_MODE" == true ]]; then
        # Clean Docker resources
        docker-compose down -v --remove-orphans
        docker system prune -f
    fi
    
    # Clean logs
    rm -rf logs/
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Deployment cleaned"
}

# Main deployment function
main_deploy() {
    print_header "SentinelBERT Deployment Starting"
    
    # Initialize log file
    echo "Deployment started at $(date)" > "$LOG_FILE"
    
    # Detect system
    detect_system
    
    # Check prerequisites
    check_prerequisites
    
    # Create environment file
    create_env_file
    
    if [[ "$NATIVE_MODE" == true ]]; then
        # Native deployment
        install_python_deps
        install_node_deps
        setup_database
        start_native_services
    elif [[ "$DOCKER_MODE" == true ]]; then
        # Docker deployment
        start_docker_services
    fi
    
    # Wait for services to start
    print_info "Waiting for services to initialize..."
    sleep 15
    
    # Check service health
    check_service_health
    
    # Show access URLs
    print_header "Deployment Complete"
    print_success "SentinelBERT is now running!"
    echo ""
    print_info "Access URLs:"
    echo "  🎯 Streamlit Dashboard: http://localhost:$STREAMLIT_PORT"
    echo "  ⚛️  React Frontend:     http://localhost:$FRONTEND_PORT"
    echo "  🤖 NLP API:            http://localhost:$NLP_PORT"
    echo "  📊 API Documentation:  http://localhost:$NLP_PORT/docs"
    echo ""
    print_info "Useful commands:"
    echo "  Check status: $0 --status"
    echo "  View logs:    $0 --logs"
    echo "  Stop all:     $0 --stop"
    echo "  Clean all:    $0 --clean"
    echo ""
    print_warning "Remember to update API keys in $ENV_FILE for full functionality"
}

# Main execution
main() {
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Parse arguments
    parse_args "$@"
    
    # Run main deployment
    main_deploy
}

# Run main function with all arguments
main "$@"
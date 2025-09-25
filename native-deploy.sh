#!/bin/bash

# SentinelBERT Native Deployment Script
# For macOS and Linux systems
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
VENV_DIR="${PROJECT_DIR}/venv"
ENV_FILE="${PROJECT_DIR}/.env"
LOGS_DIR="${PROJECT_DIR}/logs"
PIDS_DIR="${PROJECT_DIR}/pids"

# Service ports
NLP_PORT=8000
FRONTEND_PORT=12001
STREAMLIT_PORT=12000

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

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Detected macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "Detected Linux"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check system prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing=()
    
    # Check Python 3.8+
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        python_major=$(echo $python_version | cut -d'.' -f1)
        python_minor=$(echo $python_version | cut -d'.' -f2)
        
        if [[ $python_major -eq 3 && $python_minor -ge 8 ]]; then
            print_success "Python $python_version found"
        else
            print_error "Python 3.8+ required, found $python_version"
            missing+=("python3.8+")
        fi
    else
        missing+=("python3")
    fi
    
    # Check Node.js 16+
    if command -v node &> /dev/null; then
        node_version=$(node --version | sed 's/v//')
        node_major=$(echo $node_version | cut -d'.' -f1)
        
        if [[ $node_major -ge 16 ]]; then
            print_success "Node.js $node_version found"
        else
            print_error "Node.js 16+ required, found $node_version"
            missing+=("node16+")
        fi
    else
        missing+=("node")
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        npm_version=$(npm --version)
        print_success "npm $npm_version found"
    else
        missing+=("npm")
    fi
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi
    
    # Report missing dependencies
    if [[ ${#missing[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing[*]}"
        print_info "Installation instructions:"
        
        if [[ "$OS" == "macos" ]]; then
            echo "  Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  Then run: brew install python node npm curl"
        elif [[ "$OS" == "linux" ]]; then
            echo "  Ubuntu/Debian: sudo apt-get update && sudo apt-get install python3 python3-pip nodejs npm curl"
            echo "  CentOS/RHEL: sudo yum install python3 python3-pip nodejs npm curl"
        fi
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Create project directories
create_directories() {
    print_info "Creating project directories..."
    
    mkdir -p "$LOGS_DIR"
    mkdir -p "$PIDS_DIR"
    mkdir -p "${PROJECT_DIR}/data"
    
    print_success "Directories created"
}

# Create environment file
create_env_file() {
    print_header "Creating Environment Configuration"
    
    if [[ -f "$ENV_FILE" ]]; then
        print_info "Environment file exists, backing up..."
        cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    cat > "$ENV_FILE" << EOF
# SentinelBERT Native Environment Configuration
# Generated on $(date)

# Service Configuration
NLP_PORT=$NLP_PORT
FRONTEND_PORT=$FRONTEND_PORT
STREAMLIT_PORT=$STREAMLIT_PORT

# Database Configuration (Optional - for advanced features)
DB_HOST=localhost
DB_NAME=sentinelbert
DB_USER=sentinel
DB_PASSWORD=sentinel_native_2024
DB_PORT=5432

# Redis Configuration (Optional - for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_native_2024
REDIS_SSL=false

# JWT Configuration
JWT_SECRET=native_jwt_secret_key_2024_very_secure

# API Keys (Replace with your actual keys)
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

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# Service URLs
NLP_SERVICE_URL=http://localhost:$NLP_PORT
FRONTEND_URL=http://localhost:$FRONTEND_PORT
STREAMLIT_URL=http://localhost:$STREAMLIT_PORT
EOF
    
    print_success "Environment file created at $ENV_FILE"
    print_warning "Please update API keys in $ENV_FILE for full functionality"
}

# Setup Python environment
setup_python_env() {
    print_header "Setting up Python Environment"
    
    # Create virtual environment
    if [[ ! -d "$VENV_DIR" ]]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv "$VENV_DIR"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    print_info "Upgrading pip..."
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
    
    # Install additional dependencies for real-time features
    print_info "Installing real-time data dependencies..."
    pip install tweepy praw google-api-python-client psycopg2-binary
    
    print_success "Python environment setup complete"
}

# Test database connection
test_database_connection() {
    print_header "Testing Database Connection"
    
    if [[ -f "test_local_db_connection.py" ]]; then
        print_info "Testing PostgreSQL connection..."
        if python test_local_db_connection.py; then
            print_success "Database connection successful"
        else
            print_warning "Database connection failed - continuing with SQLite cache only"
            print_info "See LOCAL_POSTGRESQL_SETUP.md for database setup instructions"
        fi
    else
        print_warning "Database test script not found"
    fi
}

# Setup Node.js environment
setup_node_env() {
    print_header "Setting up Node.js Environment"
    
    if [[ -d "frontend" ]]; then
        cd frontend
        
        if [[ ! -d "node_modules" ]]; then
            print_info "Installing frontend dependencies..."
            npm install
        else
            print_info "Frontend dependencies already installed"
        fi
        
        cd ..
        print_success "Node.js environment setup complete"
    else
        print_warning "Frontend directory not found, skipping Node.js setup"
    fi
}

# Start NLP service
start_nlp_service() {
    print_info "Starting NLP service on port $NLP_PORT..."
    
    source "$VENV_DIR/bin/activate"
    source "$ENV_FILE"
    
    cd services/nlp
    nohup uvicorn main:app --host 0.0.0.0 --port $NLP_PORT --reload > "$LOGS_DIR/nlp_service.log" 2>&1 &
    NLP_PID=$!
    echo $NLP_PID > "$PIDS_DIR/nlp_service.pid"
    cd ../..
    
    # Wait and check if service started
    sleep 3
    if ps -p $NLP_PID > /dev/null; then
        print_success "NLP service started (PID: $NLP_PID)"
    else
        print_error "Failed to start NLP service"
        return 1
    fi
}

# Start Streamlit dashboard
start_streamlit_dashboard() {
    print_info "Starting Streamlit dashboard on port $STREAMLIT_PORT..."
    
    source "$VENV_DIR/bin/activate"
    source "$ENV_FILE"
    
    nohup streamlit run enhanced_viral_dashboard.py \
        --server.port $STREAMLIT_PORT \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.enableCORS false \
        --server.enableXsrfProtection false \
        > "$LOGS_DIR/streamlit.log" 2>&1 &
    
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > "$PIDS_DIR/streamlit.pid"
    
    # Wait and check if service started
    sleep 3
    if ps -p $STREAMLIT_PID > /dev/null; then
        print_success "Streamlit dashboard started (PID: $STREAMLIT_PID)"
    else
        print_error "Failed to start Streamlit dashboard"
        return 1
    fi
}

# Start React frontend
start_react_frontend() {
    if [[ ! -d "frontend" ]]; then
        print_warning "Frontend directory not found, skipping React frontend"
        return 0
    fi
    
    print_info "Starting React frontend on port $FRONTEND_PORT..."
    
    cd frontend
    source "$ENV_FILE"
    
    # Set environment variables for React
    export BROWSER=none
    export HOST=0.0.0.0
    export PORT=$FRONTEND_PORT
    
    nohup npm start > "$LOGS_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PIDS_DIR/frontend.pid"
    cd ..
    
    # Wait and check if service started
    sleep 5
    if ps -p $FRONTEND_PID > /dev/null; then
        print_success "React frontend started (PID: $FRONTEND_PID)"
    else
        print_warning "React frontend may still be starting"
    fi
}

# Check service health
check_service_health() {
    print_header "Checking Service Health"
    
    local all_healthy=true
    
    # Check NLP service
    print_info "Checking NLP service..."
    if curl -f -s "http://localhost:$NLP_PORT/health" > /dev/null; then
        print_success "NLP service is healthy"
    else
        print_error "NLP service is not responding"
        all_healthy=false
    fi
    
    # Check Streamlit dashboard
    print_info "Checking Streamlit dashboard..."
    if curl -f -s "http://localhost:$STREAMLIT_PORT" > /dev/null; then
        print_success "Streamlit dashboard is healthy"
    else
        print_error "Streamlit dashboard is not responding"
        all_healthy=false
    fi
    
    # Check React frontend (optional)
    if [[ -f "$PIDS_DIR/frontend.pid" ]]; then
        print_info "Checking React frontend..."
        if curl -f -s "http://localhost:$FRONTEND_PORT" > /dev/null; then
            print_success "React frontend is healthy"
        else
            print_warning "React frontend may still be starting"
        fi
    fi
    
    if [[ "$all_healthy" == true ]]; then
        print_success "All critical services are healthy"
    else
        print_error "Some services are not healthy. Check logs for details."
        return 1
    fi
}

# Show service status
show_status() {
    print_header "Service Status"
    
    # Check NLP service
    if [[ -f "$PIDS_DIR/nlp_service.pid" ]]; then
        nlp_pid=$(cat "$PIDS_DIR/nlp_service.pid")
        if ps -p $nlp_pid > /dev/null; then
            print_success "NLP service running (PID: $nlp_pid)"
        else
            print_error "NLP service not running"
        fi
    else
        print_error "NLP service not started"
    fi
    
    # Check Streamlit dashboard
    if [[ -f "$PIDS_DIR/streamlit.pid" ]]; then
        streamlit_pid=$(cat "$PIDS_DIR/streamlit.pid")
        if ps -p $streamlit_pid > /dev/null; then
            print_success "Streamlit dashboard running (PID: $streamlit_pid)"
        else
            print_error "Streamlit dashboard not running"
        fi
    else
        print_error "Streamlit dashboard not started"
    fi
    
    # Check React frontend
    if [[ -f "$PIDS_DIR/frontend.pid" ]]; then
        frontend_pid=$(cat "$PIDS_DIR/frontend.pid")
        if ps -p $frontend_pid > /dev/null; then
            print_success "React frontend running (PID: $frontend_pid)"
        else
            print_error "React frontend not running"
        fi
    else
        print_info "React frontend not started"
    fi
    
    # Check service health
    check_service_health
}

# Show logs
show_logs() {
    print_header "Service Logs"
    
    if [[ -f "$LOGS_DIR/nlp_service.log" ]]; then
        echo -e "${BLUE}=== NLP Service Logs (last 20 lines) ===${NC}"
        tail -20 "$LOGS_DIR/nlp_service.log"
        echo ""
    fi
    
    if [[ -f "$LOGS_DIR/streamlit.log" ]]; then
        echo -e "${BLUE}=== Streamlit Dashboard Logs (last 20 lines) ===${NC}"
        tail -20 "$LOGS_DIR/streamlit.log"
        echo ""
    fi
    
    if [[ -f "$LOGS_DIR/frontend.log" ]]; then
        echo -e "${BLUE}=== Frontend Logs (last 20 lines) ===${NC}"
        tail -20 "$LOGS_DIR/frontend.log"
        echo ""
    fi
}

# Stop services
stop_services() {
    print_header "Stopping Services"
    
    # Stop NLP service
    if [[ -f "$PIDS_DIR/nlp_service.pid" ]]; then
        nlp_pid=$(cat "$PIDS_DIR/nlp_service.pid")
        if ps -p $nlp_pid > /dev/null; then
            kill $nlp_pid
            print_info "Stopped NLP service (PID: $nlp_pid)"
        fi
        rm -f "$PIDS_DIR/nlp_service.pid"
    fi
    
    # Stop Streamlit dashboard
    if [[ -f "$PIDS_DIR/streamlit.pid" ]]; then
        streamlit_pid=$(cat "$PIDS_DIR/streamlit.pid")
        if ps -p $streamlit_pid > /dev/null; then
            kill $streamlit_pid
            print_info "Stopped Streamlit dashboard (PID: $streamlit_pid)"
        fi
        rm -f "$PIDS_DIR/streamlit.pid"
    fi
    
    # Stop React frontend
    if [[ -f "$PIDS_DIR/frontend.pid" ]]; then
        frontend_pid=$(cat "$PIDS_DIR/frontend.pid")
        if ps -p $frontend_pid > /dev/null; then
            kill $frontend_pid
            print_info "Stopped React frontend (PID: $frontend_pid)"
        fi
        rm -f "$PIDS_DIR/frontend.pid"
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "streamlit run" 2>/dev/null || true
    pkill -f "react-scripts start" 2>/dev/null || true
    
    print_success "All services stopped"
}

# Clean deployment
clean_deployment() {
    print_header "Cleaning Deployment"
    
    # Stop services
    stop_services
    
    # Clean logs
    rm -rf "$LOGS_DIR"
    rm -rf "$PIDS_DIR"
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean Node modules (optional)
    read -p "Remove node_modules? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf frontend/node_modules
        print_info "Removed node_modules"
    fi
    
    print_success "Deployment cleaned"
}

# Main deployment function
deploy() {
    print_header "SentinelBERT Native Deployment"
    
    detect_os
    check_prerequisites
    create_directories
    create_env_file
    setup_python_env
    test_database_connection
    setup_node_env
    
    # Start services
    start_nlp_service
    start_streamlit_dashboard
    start_react_frontend
    
    # Wait for services to initialize
    print_info "Waiting for services to initialize..."
    sleep 15
    
    # Check health
    check_service_health
    
    # Show deployment info
    print_header "Deployment Complete"
    print_success "SentinelBERT is now running natively!"
    echo ""
    print_info "Access URLs:"
    echo "  🎯 Streamlit Dashboard: http://localhost:$STREAMLIT_PORT"
    echo "  ⚛️  React Frontend:     http://localhost:$FRONTEND_PORT"
    echo "  🤖 NLP API:            http://localhost:$NLP_PORT"
    echo "  📊 API Documentation:  http://localhost:$NLP_PORT/docs"
    echo ""
    print_info "Management commands:"
    echo "  Check status: $0 status"
    echo "  View logs:    $0 logs"
    echo "  Stop all:     $0 stop"
    echo "  Clean all:    $0 clean"
    echo ""
    print_warning "Update API keys in $ENV_FILE for full social media functionality"
}

# Main function
main() {
    cd "$PROJECT_DIR"
    
    case "${1:-deploy}" in
        deploy)
            deploy
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        stop)
            stop_services
            ;;
        clean)
            clean_deployment
            ;;
        restart)
            stop_services
            sleep 2
            deploy
            ;;
        *)
            echo "Usage: $0 {deploy|status|logs|stop|clean|restart}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy all services natively"
            echo "  status   - Show service status"
            echo "  logs     - Show service logs"
            echo "  stop     - Stop all services"
            echo "  clean    - Clean deployment"
            echo "  restart  - Restart all services"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
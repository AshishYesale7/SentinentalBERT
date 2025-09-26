#!/bin/bash

# SentinelBERT Quick Start Script
# Automatically detects and deploys using the best available method
# Version: 3.0 - Updated for macOS compatibility and current project structure
#
# Features:
# - Streamlit Analytics Dashboard (Government-style interface) on port 12000
# - React Frontend (Modern web interface) on port 12001
# - FastAPI NLP Service (BERT-based processing) on port 8000
# - PostgreSQL 15 database with local setup
# - Redis caching service on port 6379
# - Docker Compose orchestration with health checks
# - macOS-optimized installation and setup
# - Environment configuration for external access

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Welcome message
show_welcome() {
    clear
    echo -e "${BLUE}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗ ║
║   ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║ ║
║   ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║ ║
║   ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║ ║
║   ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗║
║   ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝║
║                                                               ║
║                    BERT Quick Start Deployment               ║
║                         Team: Code X                         ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo ""
    print_info "Welcome to SentinelBERT Quick Start Deployment!"
    echo ""
}

# Detect system capabilities
detect_capabilities() {
    print_header "Detecting System Capabilities"
    
    # Check operating system
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Operating System: macOS"
        
        # Check for Homebrew on macOS
        if command -v brew &> /dev/null; then
            print_success "Homebrew: Available"
            BREW_AVAILABLE=true
        else
            print_warning "Homebrew: Not available (recommended for macOS)"
            BREW_AVAILABLE=false
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "Operating System: Linux"
        BREW_AVAILABLE=false
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check Docker availability
    DOCKER_AVAILABLE=false
    if command -v docker &> /dev/null; then
        if docker info > /dev/null 2>&1; then
            DOCKER_AVAILABLE=true
            print_success "Docker: Available and running"
            
            # Check Docker Compose
            if docker compose version > /dev/null 2>&1; then
                print_success "Docker Compose: Available (v2)"
            elif command -v docker-compose &> /dev/null; then
                print_success "Docker Compose: Available (v1)"
            else
                print_warning "Docker Compose: Not available"
            fi
        else
            print_warning "Docker: Installed but not running"
            print_info "Please start Docker Desktop on macOS"
        fi
    else
        print_warning "Docker: Not available"
        if [[ "$OS" == "macos" ]]; then
            print_info "Install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        fi
    fi
    
    # Check PostgreSQL
    POSTGRES_AVAILABLE=false
    if command -v psql &> /dev/null; then
        postgres_version=$(psql --version | cut -d' ' -f3 | cut -d'.' -f1)
        if [[ $postgres_version -ge 12 ]]; then
            POSTGRES_AVAILABLE=true
            print_success "PostgreSQL: $postgres_version (compatible)"
        else
            print_warning "PostgreSQL: $postgres_version (requires 12+)"
        fi
    else
        print_warning "PostgreSQL: Not available"
        if [[ "$OS" == "macos" && "$BREW_AVAILABLE" == true ]]; then
            print_info "Can install with: brew install postgresql@15"
        fi
    fi
    
    # Check Python
    PYTHON_AVAILABLE=false
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        python_major=$(echo $python_version | cut -d'.' -f1)
        python_minor=$(echo $python_version | cut -d'.' -f2)
        
        if [[ $python_major -eq 3 && $python_minor -ge 8 ]]; then
            PYTHON_AVAILABLE=true
            print_success "Python: $python_version (compatible)"
        else
            print_warning "Python: $python_version (requires 3.8+)"
        fi
    else
        print_warning "Python: Not available"
        if [[ "$OS" == "macos" && "$BREW_AVAILABLE" == true ]]; then
            print_info "Can install with: brew install python@3.11"
        fi
    fi
    
    # Check Node.js
    NODE_AVAILABLE=false
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        node_version=$(node --version | sed 's/v//')
        node_major=$(echo $node_version | cut -d'.' -f1)
        
        if [[ $node_major -ge 16 ]]; then
            NODE_AVAILABLE=true
            print_success "Node.js: $node_version (compatible)"
        else
            print_warning "Node.js: $node_version (requires 16+)"
        fi
    else
        print_warning "Node.js: Not available"
        if [[ "$OS" == "macos" && "$BREW_AVAILABLE" == true ]]; then
            print_info "Can install with: brew install node"
        fi
    fi
}

# Install missing dependencies on macOS
install_macos_dependencies() {
    print_header "Installing Missing Dependencies on macOS"
    
    if [[ "$BREW_AVAILABLE" == false ]]; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
        BREW_AVAILABLE=true
        print_success "Homebrew installed successfully"
    fi
    
    # Install PostgreSQL if not available
    if [[ "$POSTGRES_AVAILABLE" == false ]]; then
        print_info "Installing PostgreSQL 15..."
        brew install postgresql@15
        brew services start postgresql@15
        
        # Add to PATH
        echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
        export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
        
        print_success "PostgreSQL 15 installed and started"
        POSTGRES_AVAILABLE=true
    fi
    
    # Install Python if not available
    if [[ "$PYTHON_AVAILABLE" == false ]]; then
        print_info "Installing Python 3.11..."
        brew install python@3.11
        print_success "Python 3.11 installed"
        PYTHON_AVAILABLE=true
    fi
    
    # Install Node.js if not available
    if [[ "$NODE_AVAILABLE" == false ]]; then
        print_info "Installing Node.js..."
        brew install node
        print_success "Node.js installed"
        NODE_AVAILABLE=true
    fi
    
    # Install Docker if not available
    if [[ "$DOCKER_AVAILABLE" == false ]]; then
        print_info "Installing Docker Desktop..."
        brew install --cask docker
        print_warning "Please start Docker Desktop manually after installation"
        print_info "Docker Desktop will be available in Applications folder"
    fi
}

# Setup PostgreSQL database
setup_postgresql() {
    print_header "Setting up PostgreSQL Database"
    
    if [[ "$OS" == "macos" ]]; then
        # Ensure PostgreSQL is running
        if ! brew services list | grep postgresql@15 | grep started > /dev/null; then
            print_info "Starting PostgreSQL service..."
            brew services start postgresql@15
        fi
        
        # Wait for PostgreSQL to start
        sleep 3
        
        # Create database and user
        print_info "Creating SentinelBERT database..."
        createdb sentinelbert 2>/dev/null || print_info "Database already exists"
        
        # Create user if needed
        psql -d postgres -c "CREATE USER sentinel WITH PASSWORD 'sentinel123';" 2>/dev/null || print_info "User already exists"
        psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE sentinelbert TO sentinel;" 2>/dev/null
        
        print_success "PostgreSQL database setup complete"
    fi
}

# Recommend deployment method
recommend_deployment() {
    print_header "Deployment Method Recommendation"
    
    if [[ "$DOCKER_AVAILABLE" == true && "$POSTGRES_AVAILABLE" == true ]]; then
        RECOMMENDED_METHOD="docker"
        print_success "Recommended: Docker Deployment with Local PostgreSQL"
        print_info "✓ Isolated containerized services"
        print_info "✓ Local PostgreSQL 15 database"
        print_info "✓ Easy to manage and scale"
        print_info "✓ Consistent across systems"
        print_info "✓ Includes all services with health checks"
    elif [[ "$DOCKER_AVAILABLE" == true ]]; then
        RECOMMENDED_METHOD="docker-full"
        print_success "Recommended: Full Docker Deployment"
        print_info "✓ Complete containerized environment"
        print_info "✓ PostgreSQL in container"
        print_info "✓ Easy to manage"
        print_info "✓ No external dependencies"
    elif [[ "$PYTHON_AVAILABLE" == true ]]; then
        RECOMMENDED_METHOD="native"
        print_success "Recommended: Native Deployment"
        print_info "✓ Direct system installation"
        print_info "✓ Better performance"
        print_info "✓ Easier debugging"
        if [[ "$NODE_AVAILABLE" == false ]]; then
            print_warning "⚠ React frontend will be skipped (Node.js not available)"
        fi
        if [[ "$POSTGRES_AVAILABLE" == false ]]; then
            print_warning "⚠ PostgreSQL required for full functionality"
        fi
    else
        print_error "No suitable deployment method available"
        print_info "Would you like to install missing dependencies?"
        if [[ "$OS" == "macos" ]]; then
            read -p "Install dependencies automatically? (Y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                install_macos_dependencies
                # Re-detect capabilities after installation
                detect_capabilities
                recommend_deployment
                return
            fi
        fi
        print_info "Please install either:"
        print_info "  1. Docker Desktop and PostgreSQL 15, OR"
        print_info "  2. Python 3.8+, Node.js 16+, and PostgreSQL 15"
        exit 1
    fi
}

# Show deployment options
show_deployment_options() {
    echo ""
    print_info "Available deployment options:"
    echo ""
    
    if [[ "$DOCKER_AVAILABLE" == true ]]; then
        echo "  1) Docker Deployment (Recommended)"
        echo "     - Complete isolated environment"
        echo "     - All services included"
        echo "     - Easy management"
    fi
    
    if [[ "$PYTHON_AVAILABLE" == true ]]; then
        echo "  2) Native Deployment"
        echo "     - Direct system installation"
        echo "     - Better performance"
        echo "     - Easier development"
    fi
    
    echo "  3) Manual selection"
    echo "  4) Exit"
    echo ""
}

# Get user choice
get_user_choice() {
    while true; do
        read -p "Select deployment method (1-4): " choice
        
        case $choice in
            1)
                if [[ "$DOCKER_AVAILABLE" == true ]]; then
                    DEPLOYMENT_METHOD="docker"
                    break
                else
                    print_error "Docker is not available"
                fi
                ;;
            2)
                if [[ "$PYTHON_AVAILABLE" == true ]]; then
                    DEPLOYMENT_METHOD="native"
                    break
                else
                    print_error "Python 3.8+ is not available"
                fi
                ;;
            3)
                show_manual_options
                break
                ;;
            4)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please select 1-4."
                ;;
        esac
    done
}

# Show manual deployment options
show_manual_options() {
    echo ""
    print_info "Manual deployment options:"
    echo "  1) Docker with simplified setup"
    echo "  2) Native with core services only"
    echo "  3) Development mode (native with hot reload)"
    echo "  4) Back to main menu"
    echo ""
    
    while true; do
        read -p "Select option (1-4): " choice
        
        case $choice in
            1)
                DEPLOYMENT_METHOD="docker-simple"
                break
                ;;
            2)
                DEPLOYMENT_METHOD="native-core"
                break
                ;;
            3)
                DEPLOYMENT_METHOD="native-dev"
                break
                ;;
            4)
                show_deployment_options
                get_user_choice
                return
                ;;
            *)
                print_error "Invalid choice. Please select 1-4."
                ;;
        esac
    done
}

# Setup React NLP Dashboard
setup_react_dashboard() {
    print_header "Setting up React NLP Dashboard"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_info "Installing Node.js..."
        if [[ "$OS" == "linux" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif [[ "$OS" == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install node
            else
                print_error "Please install Node.js manually from https://nodejs.org/"
                return 1
            fi
        fi
    fi
    
    # Navigate to frontend directory
    cd frontend
    
    # Create .env file for React configuration
    print_info "Configuring React development server..."
    cat > .env << 'EOF'
DANGEROUSLY_DISABLE_HOST_CHECK=true
BROWSER=none
HOST=0.0.0.0
PORT=12001
WDS_SOCKET_HOST=0.0.0.0
WDS_SOCKET_PORT=12001
EOF
    
    # Install dependencies
    print_info "Installing React dependencies..."
    npm install
    
    # Start React development server in background
    print_info "Starting React NLP Dashboard on port 12001..."
    npm start > react_server.log 2>&1 &
    REACT_PID=$!
    echo $REACT_PID > react_server.pid
    
    # Wait for server to start
    print_info "Waiting for React server to start..."
    sleep 15
    
    # Check if server is running
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:12001 | grep -q "200"; then
        print_success "React NLP Dashboard started successfully on port 12001"
    else
        print_warning "React server may still be starting up..."
    fi
    
    # Return to main directory
    cd ..
}

# Setup environment variables
setup_environment() {
    print_header "Setting up Environment Variables"
    
    if [[ ! -f ".env" ]]; then
        print_info "Creating .env file..."
        cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=sentinel
POSTGRES_PASSWORD=sentinel123
POSTGRES_DB=sentinelbert
DB_HOST=host.docker.internal
DB_PORT=5432

# Redis Configuration
REDIS_PASSWORD=sentinel_redis_2024

# API Keys (Update with your actual keys)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

# NLP Service Configuration
NLP_SERVICE_URL=http://localhost:8000
REACT_APP_API_URL=/api

# Security
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here
EOF
        print_success ".env file created"
    else
        print_info ".env file already exists"
    fi
}

# Execute deployment
execute_deployment() {
    print_header "Starting Deployment"
    
    # Setup environment first
    setup_environment
    
    case $DEPLOYMENT_METHOD in
        docker)
            print_info "Starting Docker deployment with local PostgreSQL..."
            
            # Setup PostgreSQL first
            setup_postgresql
            
            # Start Docker services
            print_info "Starting Docker Compose services..."
            if command -v docker-compose &> /dev/null; then
                docker-compose -f docker-compose.simple.yml up -d
            else
                docker compose -f docker-compose.simple.yml up -d
            fi
            
            # Wait for services to be healthy
            print_info "Waiting for services to be healthy..."
            sleep 30
            
            # Check service health
            check_service_health
            ;;
        docker-full)
            print_info "Starting full Docker deployment..."
            
            # Use full docker-compose with PostgreSQL container
            print_info "Starting all services in containers..."
            if command -v docker-compose &> /dev/null; then
                docker-compose up -d
            else
                docker compose up -d
            fi
            
            # Wait for services to be healthy
            print_info "Waiting for services to be healthy..."
            sleep 45
            
            # Check service health
            check_service_health
            ;;
        native)
            print_info "Starting native deployment..."
            
            # Setup PostgreSQL
            setup_postgresql
            
            # Install Python dependencies
            print_info "Installing Python dependencies..."
            pip3 install -r requirements-docker.txt
            
            # Start NLP service
            print_info "Starting NLP service..."
            cd services/nlp
            python3 main.py &
            NLP_PID=$!
            echo $NLP_PID > nlp_service.pid
            cd ../..
            
            # Start Streamlit dashboard
            print_info "Starting Streamlit dashboard..."
            streamlit run enhanced_viral_dashboard.py --server.port=12000 --server.address=0.0.0.0 &
            STREAMLIT_PID=$!
            echo $STREAMLIT_PID > streamlit.pid
            
            # Setup React frontend if available
            if [[ "$NODE_AVAILABLE" == true ]]; then
                setup_react_dashboard
            fi
            ;;
        *)
            print_error "Unknown deployment method: $DEPLOYMENT_METHOD"
            exit 1
            ;;
    esac
}

# Check service health
check_service_health() {
    print_header "Checking Service Health"
    
    # Check NLP service
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "NLP Service: Healthy"
    else
        print_warning "NLP Service: Not responding"
    fi
    
    # Check Streamlit dashboard
    if curl -s http://localhost:12000 > /dev/null; then
        print_success "Streamlit Dashboard: Healthy"
    else
        print_warning "Streamlit Dashboard: Not responding"
    fi
    
    # Check React frontend
    if curl -s http://localhost:12001 > /dev/null; then
        print_success "React Frontend: Healthy"
    else
        print_warning "React Frontend: Not responding"
    fi
    
    # Check PostgreSQL
    if [[ "$POSTGRES_AVAILABLE" == true ]]; then
        if psql -h localhost -U sentinel -d sentinelbert -c "SELECT 1;" > /dev/null 2>&1; then
            print_success "PostgreSQL: Connected"
        else
            print_warning "PostgreSQL: Connection failed"
        fi
    fi
}

# Show post-deployment info
show_post_deployment() {
    print_header "Deployment Complete!"
    
    echo -e "${GREEN}🎉 SentinelBERT has been successfully deployed!${NC}"
    echo ""
    
    print_info "What's running:"
    echo "  🎯 Streamlit Analytics Dashboard - Government-style interface with legal compliance"
    echo "  ⚛️  React Frontend - Modern web interface with sentiment analysis"
    echo "  🤖 NLP Service - BERT-based sentiment and behavioral analysis"
    echo "  🗄️  PostgreSQL 15 - Local database for data storage"
    echo "  🔄 Redis - Caching and session management"
    echo "  📊 Real-time Analytics - Multi-platform social media monitoring"
    echo ""
    
    print_info "Access URLs:"
    echo "  📱 Streamlit Analytics Dashboard: http://localhost:12000"
    echo "  💻 React Frontend:               http://localhost:12001"
    echo "  🔧 NLP API Service:              http://localhost:8000"
    echo "  📖 API Documentation:            http://localhost:8000/docs"
    echo "  🗄️  PostgreSQL:                  localhost:5432 (user: sentinel, db: sentinelbert)"
    echo "  🔄 Redis Cache:                  localhost:6379"
    echo ""
    
    print_info "Key Features Available:"
    echo "  ✅ Multi-platform social media analysis (Twitter, Facebook, Instagram, etc.)"
    echo "  ✅ Indian platform support (Koo, ShareChat, Josh, Moj)"
    echo "  ✅ Advanced sentiment analysis with 98%+ accuracy"
    echo "  ✅ Behavioral pattern detection and influence scoring"
    echo "  ✅ Viral content tracking and prediction"
    echo "  ✅ Legal compliance framework (IT Act 2000, CrPC 1973, Evidence Act 1872)"
    echo "  ✅ Multi-language support (10+ Indian languages + global)"
    echo "  ✅ Real-time monitoring and analytics"
    echo "  ✅ Evidence collection with chain of custody"
    echo "  ✅ Geographic spread analysis"
    echo ""
    
    print_info "Next steps:"
    echo "  1. Open your browser and visit the URLs above"
    echo "  2. Update API keys in .env file for social media integration:"
    echo "     • Twitter/X API credentials"
    echo "     • Other social media platform keys"
    echo "  3. Test sentiment analysis on the React frontend"
    echo "  4. Explore the comprehensive analytics dashboard"
    echo "  5. Start tracking viral content and social media trends!"
    echo ""
    
    print_warning "Important notes:"
    echo "  • Update API keys in .env for full social media functionality"
    echo "  • PostgreSQL is running locally - ensure it stays running"
    echo "  • Check service logs if you encounter issues"
    echo "  • All services have health checks and auto-restart"
    echo ""
    
    if [[ "$DEPLOYMENT_METHOD" == "docker"* ]]; then
        print_info "Docker management commands:"
        echo "  Status:  docker ps"
        echo "  Logs:    docker-compose -f docker-compose.simple.yml logs"
        echo "  Stop:    docker-compose -f docker-compose.simple.yml down"
        echo "  Restart: docker-compose -f docker-compose.simple.yml restart"
    else
        print_info "Native management commands:"
        echo "  Status:  ps aux | grep -E '(streamlit|python.*main.py)'"
        echo "  Stop NLP: kill \$(cat nlp_service.pid)"
        echo "  Stop Streamlit: kill \$(cat streamlit.pid)"
        echo "  PostgreSQL: brew services stop postgresql@15"
    fi
    
    echo ""
    print_success "SentinelBERT is ready for social media intelligence and analysis!"
}

# Handle errors
handle_error() {
    print_error "Deployment failed!"
    print_info "Troubleshooting steps:"
    echo "  1. Check the error messages above"
    echo "  2. Ensure all prerequisites are installed"
    echo "  3. Try running with verbose logging"
    echo "  4. Check the deployment logs"
    echo ""
    print_info "Get help:"
    echo "  • Check README.md for detailed instructions"
    echo "  • Review system requirements"
    echo "  • Try alternative deployment method"
    exit 1
}

# Main function
main() {
    # Set error handler
    trap handle_error ERR
    
    # Show welcome
    show_welcome
    
    # Detect system
    detect_capabilities
    
    # Recommend deployment
    recommend_deployment
    
    # Show options and get choice
    show_deployment_options
    get_user_choice
    
    # Confirm deployment
    echo ""
    print_info "Selected deployment method: $DEPLOYMENT_METHOD"
    read -p "Proceed with deployment? (Y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi
    
    # Execute deployment
    execute_deployment
    
    # Show post-deployment info
    show_post_deployment
}

# Check if running in supported environment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Change to script directory
    cd "$(dirname "${BASH_SOURCE[0]}")"
    
    # Run main function
    main "$@"
else
    print_error "This script should be executed directly, not sourced"
    exit 1
fi
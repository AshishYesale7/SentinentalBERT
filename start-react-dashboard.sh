#!/bin/bash

# SentinelBERT React NLP Dashboard Startup Script
# This script specifically starts the React NLP Dashboard

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Main function to start React dashboard
start_react_dashboard() {
    print_header "Starting React NLP Dashboard"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed!"
        print_info "Please install Node.js 16+ from https://nodejs.org/"
        print_info "Or run the main quick-start.sh script which will install it automatically"
        exit 1
    fi
    
    # Check Node.js version
    node_version=$(node --version | sed 's/v//')
    node_major=$(echo $node_version | cut -d'.' -f1)
    
    if [[ $node_major -lt 16 ]]; then
        print_error "Node.js version $node_version is too old. Requires 16+"
        exit 1
    fi
    
    print_success "Node.js version: $node_version"
    
    # Navigate to frontend directory
    if [[ ! -d "frontend" ]]; then
        print_error "Frontend directory not found!"
        print_info "Make sure you're running this script from the SentinentalBERT root directory"
        exit 1
    fi
    
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
    
    # Check if node_modules exists
    if [[ ! -d "node_modules" ]]; then
        print_info "Installing React dependencies..."
        npm install
    else
        print_info "Dependencies already installed"
    fi
    
    # Check if NLP service is running
    print_info "Checking NLP service connectivity..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health | grep -q "200"; then
        print_success "NLP service is running on port 8001"
    else
        print_warning "NLP service not detected on port 8001"
        print_info "Make sure to start the NLP service first:"
        print_info "  cd services/nlp && python main.py"
    fi
    
    # Start React development server
    print_info "Starting React NLP Dashboard on port 12001..."
    print_info "Press Ctrl+C to stop the server"
    echo ""
    
    # Start in foreground so user can see logs and stop with Ctrl+C
    npm start
}

# Check if running in supported environment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Change to script directory
    cd "$(dirname "${BASH_SOURCE[0]}")"
    
    # Show header
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║              SentinelBERT React NLP Dashboard               ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    # Run main function
    start_react_dashboard
else
    print_error "This script should be executed directly, not sourced"
    exit 1
fi
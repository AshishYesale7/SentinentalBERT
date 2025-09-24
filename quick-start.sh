#!/bin/bash

# SentinelBERT Quick Start Script
# Automatically detects and deploys using the best available method
# Version: 2.0

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
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "Operating System: Linux"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    # Check Docker availability
    DOCKER_AVAILABLE=false
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        if docker info > /dev/null 2>&1; then
            DOCKER_AVAILABLE=true
            print_success "Docker: Available and running"
        else
            print_warning "Docker: Installed but not running"
        fi
    else
        print_warning "Docker: Not available"
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
    fi
}

# Recommend deployment method
recommend_deployment() {
    print_header "Deployment Method Recommendation"
    
    if [[ "$DOCKER_AVAILABLE" == true ]]; then
        RECOMMENDED_METHOD="docker"
        print_success "Recommended: Docker Deployment"
        print_info "✓ Isolated environment"
        print_info "✓ Easy to manage"
        print_info "✓ Consistent across systems"
        print_info "✓ Includes all services"
    elif [[ "$PYTHON_AVAILABLE" == true ]]; then
        RECOMMENDED_METHOD="native"
        print_success "Recommended: Native Deployment"
        print_info "✓ Direct system installation"
        print_info "✓ Better performance"
        print_info "✓ Easier debugging"
        if [[ "$NODE_AVAILABLE" == false ]]; then
            print_warning "⚠ React frontend will be skipped (Node.js not available)"
        fi
    else
        print_error "No suitable deployment method available"
        print_info "Please install either:"
        print_info "  1. Docker and Docker Compose, OR"
        print_info "  2. Python 3.8+ and Node.js 16+"
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

# Execute deployment
execute_deployment() {
    print_header "Starting Deployment"
    
    case $DEPLOYMENT_METHOD in
        docker)
            print_info "Starting Docker deployment..."
            chmod +x docker-deploy.sh
            ./docker-deploy.sh deploy
            ;;
        docker-simple)
            print_info "Starting simplified Docker deployment..."
            chmod +x docker-deploy.sh
            ./docker-deploy.sh deploy
            ;;
        native)
            print_info "Starting native deployment..."
            chmod +x native-deploy.sh
            ./native-deploy.sh deploy
            ;;
        native-core)
            print_info "Starting core native deployment..."
            chmod +x native-deploy.sh
            ./native-deploy.sh deploy
            ;;
        native-dev)
            print_info "Starting development deployment..."
            chmod +x native-deploy.sh
            ./native-deploy.sh deploy
            ;;
        *)
            print_error "Unknown deployment method: $DEPLOYMENT_METHOD"
            exit 1
            ;;
    esac
}

# Show post-deployment info
show_post_deployment() {
    print_header "Deployment Complete!"
    
    echo -e "${GREEN}🎉 SentinelBERT has been successfully deployed!${NC}"
    echo ""
    
    print_info "What's running:"
    echo "  🎯 Streamlit Dashboard - Government-style interface"
    echo "  ⚛️  React Frontend - Modern web interface"
    echo "  🤖 NLP API - BERT-based sentiment analysis"
    echo "  📊 Real-time Analytics - Social media monitoring"
    echo ""
    
    print_info "Access URLs:"
    echo "  📱 Streamlit Dashboard: http://localhost:12000"
    echo "  💻 React Frontend:     http://localhost:12001"
    echo "  🔧 NLP API:            http://localhost:8000"
    echo "  📖 API Documentation:  http://localhost:8000/docs"
    echo ""
    
    print_info "Next steps:"
    echo "  1. Open your browser and visit the URLs above"
    echo "  2. Update API keys in .env file for social media integration"
    echo "  3. Start analyzing social media content!"
    echo ""
    
    print_warning "Important notes:"
    echo "  • Update API keys in .env for full functionality"
    echo "  • Check service logs if you encounter issues"
    echo "  • Use management scripts for service control"
    echo ""
    
    if [[ "$DEPLOYMENT_METHOD" == "docker"* ]]; then
        print_info "Docker management commands:"
        echo "  Status: ./docker-deploy.sh status"
        echo "  Logs:   ./docker-deploy.sh logs"
        echo "  Stop:   ./docker-deploy.sh stop"
    else
        print_info "Native management commands:"
        echo "  Status: ./native-deploy.sh status"
        echo "  Logs:   ./native-deploy.sh logs"
        echo "  Stop:   ./native-deploy.sh stop"
    fi
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
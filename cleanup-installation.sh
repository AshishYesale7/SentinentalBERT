#!/bin/bash

# SentinelBERT Installation Cleanup Script
# Completely removes all installation artifacts and processes
# Version: 1.0

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
    echo -e "${RED}"
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
║                    INSTALLATION CLEANUP                      ║
║                         Team: Code X                         ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo ""
    print_warning "This will completely clean up your SentinelBERT installation!"
    echo ""
}

# Stop all running processes
stop_processes() {
    print_header "Stopping Running Processes"
    
    # Stop Docker containers
    if command -v docker &> /dev/null; then
        print_info "Stopping Docker containers..."
        
        # Stop containers by name patterns
        for container in $(docker ps -q --filter "name=sentinelbert" --filter "name=streamlit" --filter "name=nlp" --filter "name=frontend" --filter "name=redis" --filter "name=postgres" 2>/dev/null || true); do
            if [ ! -z "$container" ]; then
                docker stop "$container" 2>/dev/null || true
                print_success "Stopped container: $container"
            fi
        done
        
        # Stop containers using docker-compose
        if [ -f "docker-compose.yml" ]; then
            docker-compose down --remove-orphans 2>/dev/null || true
            print_success "Stopped docker-compose services"
        fi
        
        if [ -f "docker-compose.macos.yml" ]; then
            docker-compose -f docker-compose.macos.yml down --remove-orphans 2>/dev/null || true
            print_success "Stopped macOS docker-compose services"
        fi
        
        if [ -f "docker-compose.enhanced.yml" ]; then
            docker-compose -f docker-compose.enhanced.yml down --remove-orphans 2>/dev/null || true
            print_success "Stopped enhanced docker-compose services"
        fi
    fi
    
    # Stop Python processes (Streamlit, FastAPI, etc.)
    print_info "Stopping Python processes..."
    
    # Find and kill Streamlit processes
    for pid in $(ps aux | grep -E "streamlit.*run" | grep -v grep | awk '{print $2}' 2>/dev/null || true); do
        if [ ! -z "$pid" ]; then
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            kill -KILL "$pid" 2>/dev/null || true
            print_success "Stopped Streamlit process: $pid"
        fi
    done
    
    # Find and kill FastAPI/Uvicorn processes
    for pid in $(ps aux | grep -E "(uvicorn|fastapi)" | grep -v grep | awk '{print $2}' 2>/dev/null || true); do
        if [ ! -z "$pid" ]; then
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            kill -KILL "$pid" 2>/dev/null || true
            print_success "Stopped FastAPI process: $pid"
        fi
    done
    
    # Find and kill any Python processes running our scripts
    for pid in $(ps aux | grep -E "python.*enhanced_viral_dashboard" | grep -v grep | awk '{print $2}' 2>/dev/null || true); do
        if [ ! -z "$pid" ]; then
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            kill -KILL "$pid" 2>/dev/null || true
            print_success "Stopped dashboard process: $pid"
        fi
    done
    
    # Stop Node.js processes
    print_info "Stopping Node.js processes..."
    for pid in $(ps aux | grep -E "node.*frontend" | grep -v grep | awk '{print $2}' 2>/dev/null || true); do
        if [ ! -z "$pid" ]; then
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            kill -KILL "$pid" 2>/dev/null || true
            print_success "Stopped Node.js process: $pid"
        fi
    done
    
    print_success "All processes stopped"
}

# Clean up Docker resources
cleanup_docker() {
    print_header "Cleaning Docker Resources"
    
    if command -v docker &> /dev/null; then
        # Remove containers
        print_info "Removing containers..."
        for container in $(docker ps -aq --filter "name=sentinelbert" --filter "name=streamlit" --filter "name=nlp" --filter "name=frontend" --filter "name=redis" --filter "name=postgres" 2>/dev/null || true); do
            if [ ! -z "$container" ]; then
                docker rm -f "$container" 2>/dev/null || true
                print_success "Removed container: $container"
            fi
        done
        
        # Remove images
        print_info "Removing images..."
        for image in $(docker images -q --filter "reference=*sentinelbert*" --filter "reference=*streamlit*" --filter "reference=*nlp*" 2>/dev/null || true); do
            if [ ! -z "$image" ]; then
                docker rmi -f "$image" 2>/dev/null || true
                print_success "Removed image: $image"
            fi
        done
        
        # Remove volumes
        print_info "Removing volumes..."
        for volume in $(docker volume ls -q --filter "name=sentinelbert" 2>/dev/null || true); do
            if [ ! -z "$volume" ]; then
                docker volume rm "$volume" 2>/dev/null || true
                print_success "Removed volume: $volume"
            fi
        done
        
        # Remove networks
        print_info "Removing networks..."
        for network in $(docker network ls -q --filter "name=sentinelbert" 2>/dev/null || true); do
            if [ ! -z "$network" ]; then
                docker network rm "$network" 2>/dev/null || true
                print_success "Removed network: $network"
            fi
        done
        
        # Clean up dangling resources
        docker system prune -f 2>/dev/null || true
        print_success "Docker cleanup completed"
    else
        print_info "Docker not available, skipping Docker cleanup"
    fi
}

# Clean up files and directories
cleanup_files() {
    print_header "Cleaning Files and Directories"
    
    # Remove log files
    print_info "Removing log files..."
    find . -name "*.log" -type f -delete 2>/dev/null || true
    rm -f *.log 2>/dev/null || true
    print_success "Log files removed"
    
    # Remove PID files
    print_info "Removing PID files..."
    find . -name "*.pid" -type f -delete 2>/dev/null || true
    rm -f *.pid 2>/dev/null || true
    print_success "PID files removed"
    
    # Remove Python cache
    print_info "Removing Python cache..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -type f -delete 2>/dev/null || true
    find . -name "*.pyo" -type f -delete 2>/dev/null || true
    print_success "Python cache removed"
    
    # Remove Node.js modules (but keep package.json)
    print_info "Removing Node.js modules..."
    if [ -d "frontend/node_modules" ]; then
        rm -rf frontend/node_modules
        print_success "Frontend node_modules removed"
    fi
    find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
    print_success "Node.js modules removed"
    
    # Remove temporary files
    print_info "Removing temporary files..."
    rm -f .env.local .env.development .env.production 2>/dev/null || true
    rm -f *.tmp *.temp 2>/dev/null || true
    rm -f nohup.out 2>/dev/null || true
    
    # Remove database files (but keep schema)
    print_info "Removing database files..."
    rm -f data/*.db data/*.sqlite data/*.sqlite3 2>/dev/null || true
    print_success "Database files removed"
    
    # Remove build artifacts
    print_info "Removing build artifacts..."
    rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
    rm -rf frontend/build/ frontend/dist/ 2>/dev/null || true
    print_success "Build artifacts removed"
    
    # Remove test artifacts
    print_info "Removing test artifacts..."
    rm -rf .pytest_cache/ .coverage htmlcov/ 2>/dev/null || true
    rm -f *.coverage 2>/dev/null || true
    print_success "Test artifacts removed"
    
    # Remove deployment artifacts
    print_info "Removing deployment artifacts..."
    rm -f deployment_report.json enhanced_integration_test_report.json 2>/dev/null || true
    rm -f macos_compatibility_results.json 2>/dev/null || true
    rm -f macos_compatibility_test.log 2>/dev/null || true
    print_success "Deployment artifacts removed"
    
    # Remove weird files (like the "=2.1.0" file I noticed)
    print_info "Removing anomalous files..."
    rm -f "=2.1.0" 2>/dev/null || true
    find . -name "=*" -type f -delete 2>/dev/null || true
    print_success "Anomalous files removed"
}

# Clean up virtual environments
cleanup_venv() {
    print_header "Cleaning Virtual Environments"
    
    # Remove common virtual environment directories
    for venv_dir in venv env .venv .env virtualenv; do
        if [ -d "$venv_dir" ]; then
            rm -rf "$venv_dir"
            print_success "Removed virtual environment: $venv_dir"
        fi
    done
    
    # Deactivate any active virtual environment
    if [ ! -z "${VIRTUAL_ENV:-}" ]; then
        deactivate 2>/dev/null || true
        print_success "Deactivated virtual environment"
    fi
}

# Reset configuration files
reset_config() {
    print_header "Resetting Configuration Files"
    
    # Backup and reset .env files
    if [ -f ".env" ]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
        print_info "Backed up .env file"
    fi
    
    # Remove local configuration
    rm -f .env.local .env.development .env.production 2>/dev/null || true
    print_success "Local configuration files removed"
}

# Show cleanup summary
show_cleanup_summary() {
    print_header "Cleanup Summary"
    
    echo -e "${GREEN}🧹 Installation cleanup completed successfully!${NC}"
    echo ""
    
    print_info "What was cleaned:"
    echo "  🔄 All running processes stopped"
    echo "  🐳 Docker containers, images, and volumes removed"
    echo "  📁 Log files and temporary files removed"
    echo "  🐍 Python cache and bytecode files removed"
    echo "  📦 Node.js modules removed"
    echo "  🗄️  Database files cleared"
    echo "  🏗️  Build artifacts removed"
    echo "  🧪 Test artifacts removed"
    echo "  🌐 Virtual environments removed"
    echo ""
    
    print_info "What was preserved:"
    echo "  📄 Source code files"
    echo "  ⚙️  Configuration templates"
    echo "  📋 Requirements files"
    echo "  🗂️  Database schemas"
    echo "  📖 Documentation"
    echo ""
    
    print_success "Your installation is now clean and ready for fresh deployment!"
    echo ""
    
    print_info "To reinstall:"
    echo "  ./quick-start.sh    # Interactive deployment"
    echo "  ./docker-deploy.sh  # Docker deployment"
    echo "  ./native-deploy.sh  # Native deployment"
    echo ""
}

# Confirm cleanup
confirm_cleanup() {
    echo ""
    print_warning "This will completely clean up your SentinelBERT installation!"
    print_warning "All running processes will be stopped and temporary files removed."
    echo ""
    print_info "What will be cleaned:"
    echo "  • All running processes (Streamlit, FastAPI, Node.js)"
    echo "  • Docker containers, images, and volumes"
    echo "  • Log files and temporary files"
    echo "  • Python cache and Node.js modules"
    echo "  • Database files (schemas preserved)"
    echo "  • Build and test artifacts"
    echo "  • Virtual environments"
    echo ""
    print_info "What will be preserved:"
    echo "  • Source code and configuration templates"
    echo "  • Requirements files and documentation"
    echo "  • Database schemas"
    echo ""
    
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleanup cancelled"
        exit 0
    fi
}

# Main cleanup function
main() {
    # Show welcome
    show_welcome
    
    # Confirm cleanup
    confirm_cleanup
    
    # Execute cleanup steps
    stop_processes
    cleanup_docker
    cleanup_files
    cleanup_venv
    reset_config
    
    # Show summary
    show_cleanup_summary
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
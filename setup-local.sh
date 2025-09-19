#!/bin/bash

# =============================================================================
# SentinentalBERT Local Development Setup Script
# =============================================================================
# 
# DESCRIPTION:
# This script sets up a complete local development environment for SentinentalBERT
# with all necessary dependencies, services, and configurations. It's designed
# to work with free API keys and minimal system requirements.
#
# FEATURES:
# - Automated dependency installation and verification
# - Free API key configuration with detailed instructions
# - Local Docker-based service deployment
# - Privacy and security compliance setup
# - Development tools and debugging utilities
# - Comprehensive health checks and validation
#
# REQUIREMENTS:
# - Operating System: Linux (Ubuntu 18.04+), macOS (10.15+), or Windows with WSL2
# - Memory: 8GB+ RAM (16GB recommended)
# - Storage: 20GB+ free disk space
# - Docker: Docker Engine 20.10+ and Docker Compose 2.0+
# - Internet: Stable connection for downloads and API access
#
# USAGE:
# ./setup-local.sh [OPTIONS]
#
# OPTIONS:
# --clean          Clean installation (removes existing data)
# --dev            Development mode with hot reload
# --gpu            Enable GPU support (requires NVIDIA GPU)
# --minimal        Minimal installation (core services only)
# --help           Show this help message
#
# LEGAL & PRIVACY:
# This script includes privacy-compliant configurations and GDPR-ready settings
# for legal and compliance-sensitive environments. All data processing follows
# privacy-by-design principles with built-in anonymization and audit logging.
#
# Author: SentinentalBERT Team
# License: MIT License with Privacy Compliance Addendum
# Version: 1.0.0
# Last Updated: 2024-01-15
# =============================================================================

# =============================================================================
# SCRIPT CONFIGURATION AND GLOBAL VARIABLES
# =============================================================================

# Script metadata and version information
readonly SCRIPT_NAME="SentinentalBERT Local Setup"
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_AUTHOR="SentinentalBERT Team"

# Color codes for enhanced terminal output
readonly RED='\033[0;31m'      # Error messages
readonly GREEN='\033[0;32m'    # Success messages
readonly YELLOW='\033[1;33m'   # Warning messages
readonly BLUE='\033[0;34m'     # Information messages
readonly PURPLE='\033[0;35m'   # Debug messages
readonly CYAN='\033[0;36m'     # Highlight messages
readonly NC='\033[0m'          # No Color (reset)

# System requirements and configuration
readonly MIN_RAM_GB=8          # Minimum RAM requirement in GB
readonly MIN_DISK_GB=20        # Minimum disk space requirement in GB
readonly DOCKER_MIN_VERSION="20.10"  # Minimum Docker version
readonly COMPOSE_MIN_VERSION="2.0"   # Minimum Docker Compose version

# Project directories and file paths
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DATA_DIR="${PROJECT_ROOT}/data"
readonly LOGS_DIR="${PROJECT_ROOT}/logs"
readonly CONFIG_DIR="${PROJECT_ROOT}/config"
readonly SCRIPTS_DIR="${PROJECT_ROOT}/scripts"

# Service configuration
readonly SERVICES=("postgres" "redis" "elasticsearch" "nlp-service" "backend-service" "ingestion-service" "frontend")
readonly REQUIRED_PORTS=(5432 6379 9200 8000 8080 8081 3000 9090 3001)

# Default configuration values
CLEAN_INSTALL=false           # Whether to perform clean installation
DEV_MODE=false               # Whether to enable development mode
GPU_SUPPORT=false            # Whether to enable GPU support
MINIMAL_INSTALL=false        # Whether to perform minimal installation
VERBOSE=false                # Whether to enable verbose output

# =============================================================================
# UTILITY FUNCTIONS FOR OUTPUT AND LOGGING
# =============================================================================

# Function to print colored status messages with timestamps
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

# Function to print debug messages (only when verbose mode is enabled)
print_debug() {
    if [[ "$VERBOSE" == true ]]; then
        echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] [DEBUG]${NC} $1"
    fi
}

# Function to print highlighted messages
print_highlight() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] [HIGHLIGHT]${NC} $1"
}

# Function to log messages to file (for audit trail and debugging)
log_message() {
    local level="$1"
    local message="$2"
    local log_file="${LOGS_DIR}/setup.log"
    
    # Create logs directory if it doesn't exist
    mkdir -p "${LOGS_DIR}"
    
    # Write log entry with timestamp and level
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$log_file"
}

# =============================================================================
# SYSTEM VALIDATION AND PREREQUISITE CHECKING
# =============================================================================

# Function to display script header and information
show_header() {
    clear
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "  $SCRIPT_NAME v$SCRIPT_VERSION"
    echo "  $SCRIPT_AUTHOR"
    echo "============================================================================="
    echo -e "${NC}"
    echo ""
    echo "🚀 Setting up SentinentalBERT local development environment..."
    echo "📋 This script will install and configure all necessary components"
    echo "🔒 Privacy-compliant setup with GDPR-ready configurations"
    echo "⚖️  Legal authentication and audit logging enabled"
    echo ""
}

# Function to show help message with detailed usage instructions
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --clean          Clean installation (removes existing data and containers)"
    echo "  --dev            Development mode with hot reload and debug features"
    echo "  --gpu            Enable GPU support (requires NVIDIA GPU with drivers)"
    echo "  --minimal        Minimal installation (core services only, faster setup)"
    echo "  --verbose        Enable verbose output for debugging"
    echo "  --help           Show this help message and exit"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                    # Standard installation"
    echo "  $0 --dev             # Development mode with hot reload"
    echo "  $0 --clean --gpu     # Clean installation with GPU support"
    echo "  $0 --minimal         # Minimal installation for testing"
    echo ""
    echo "REQUIREMENTS:"
    echo "  - Docker Engine 20.10+"
    echo "  - Docker Compose 2.0+"
    echo "  - 8GB+ RAM (16GB recommended)"
    echo "  - 20GB+ free disk space"
    echo "  - Internet connection"
    echo ""
    echo "For more information, visit: https://github.com/bot-starter/SentinentalBERT"
}

# Function to check if the script is running with sufficient privileges
check_privileges() {
    print_status "Checking user privileges..."
    
    # Check if running as root (not recommended for development)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root is not recommended for development"
        print_warning "Consider running as a regular user with Docker permissions"
        
        # Ask for confirmation to continue
        read -p "Do you want to continue as root? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Setup cancelled by user"
            exit 1
        fi
    fi
    
    # Check if user can run Docker commands
    if ! docker info >/dev/null 2>&1; then
        print_error "Cannot run Docker commands. Please ensure:"
        print_error "1. Docker is installed and running"
        print_error "2. Your user is in the 'docker' group"
        print_error "3. You have sufficient permissions"
        echo ""
        print_status "To add your user to the docker group, run:"
        print_status "sudo usermod -aG docker \$USER"
        print_status "Then log out and log back in"
        exit 1
    fi
    
    print_success "User privileges check passed"
    log_message "INFO" "User privileges validated successfully"
}

# Function to check system requirements (RAM, disk space, etc.)
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check available RAM
    local ram_gb
    if command -v free >/dev/null 2>&1; then
        # Linux system
        ram_gb=$(free -g | awk '/^Mem:/{print $2}')
    elif command -v vm_stat >/dev/null 2>&1; then
        # macOS system
        ram_gb=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    else
        print_warning "Cannot determine available RAM, skipping check"
        ram_gb=$MIN_RAM_GB
    fi
    
    if [[ $ram_gb -lt $MIN_RAM_GB ]]; then
        print_warning "Available RAM ($ram_gb GB) is less than recommended ($MIN_RAM_GB GB)"
        print_warning "Performance may be degraded"
    else
        print_success "RAM check passed: $ram_gb GB available"
    fi
    
    # Check available disk space
    local disk_gb
    disk_gb=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [[ $disk_gb -lt $MIN_DISK_GB ]]; then
        print_error "Insufficient disk space: $disk_gb GB available, $MIN_DISK_GB GB required"
        exit 1
    else
        print_success "Disk space check passed: $disk_gb GB available"
    fi
    
    # Check operating system compatibility
    local os_name
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        os_name="Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        os_name="macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        os_name="Windows"
    else
        print_warning "Unknown operating system: $OSTYPE"
        os_name="Unknown"
    fi
    
    print_success "Operating system: $os_name"
    log_message "INFO" "System requirements check completed: RAM=${ram_gb}GB, Disk=${disk_gb}GB, OS=${os_name}"
}

# Function to check Docker and Docker Compose installation and versions
check_docker() {
    print_status "Checking Docker installation..."
    
    # Check if Docker is installed
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed"
        print_error "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker version
    local docker_version
    docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    print_status "Docker version: $docker_version"
    
    # Compare version (simplified comparison)
    if ! version_compare "$docker_version" "$DOCKER_MIN_VERSION"; then
        print_error "Docker version $docker_version is too old (minimum: $DOCKER_MIN_VERSION)"
        print_error "Please update Docker to the latest version"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_error "Please start Docker and try again"
        exit 1
    fi
    
    print_success "Docker check passed: version $docker_version"
    
    # Check Docker Compose
    print_status "Checking Docker Compose installation..."
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose is not installed"
        print_error "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check Docker Compose version
    local compose_version
    compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    print_status "Docker Compose version: $compose_version"
    
    if ! version_compare "$compose_version" "$COMPOSE_MIN_VERSION"; then
        print_error "Docker Compose version $compose_version is too old (minimum: $COMPOSE_MIN_VERSION)"
        print_error "Please update Docker Compose to the latest version"
        exit 1
    fi
    
    print_success "Docker Compose check passed: version $compose_version"
    log_message "INFO" "Docker validation completed: Docker=${docker_version}, Compose=${compose_version}"
}

# Function to compare version numbers (simplified semantic versioning)
version_compare() {
    local version1="$1"
    local version2="$2"
    
    # Convert versions to comparable format
    local v1_major v1_minor v2_major v2_minor
    v1_major=$(echo "$version1" | cut -d. -f1)
    v1_minor=$(echo "$version1" | cut -d. -f2)
    v2_major=$(echo "$version2" | cut -d. -f1)
    v2_minor=$(echo "$version2" | cut -d. -f2)
    
    # Compare major version
    if [[ $v1_major -gt $v2_major ]]; then
        return 0  # version1 > version2
    elif [[ $v1_major -lt $v2_major ]]; then
        return 1  # version1 < version2
    fi
    
    # Major versions are equal, compare minor version
    if [[ $v1_minor -ge $v2_minor ]]; then
        return 0  # version1 >= version2
    else
        return 1  # version1 < version2
    fi
}

# Function to check network connectivity and port availability
check_network() {
    print_status "Checking network connectivity and port availability..."
    
    # Check internet connectivity
    if ! ping -c 1 google.com >/dev/null 2>&1; then
        print_warning "No internet connectivity detected"
        print_warning "Some features may not work properly"
    else
        print_success "Internet connectivity check passed"
    fi
    
    # Check if required ports are available
    local unavailable_ports=()
    for port in "${REQUIRED_PORTS[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            unavailable_ports+=("$port")
        fi
    done
    
    if [[ ${#unavailable_ports[@]} -gt 0 ]]; then
        print_warning "The following ports are already in use: ${unavailable_ports[*]}"
        print_warning "This may cause conflicts with SentinentalBERT services"
        
        # Ask user if they want to continue
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Setup cancelled due to port conflicts"
            exit 1
        fi
    else
        print_success "All required ports are available"
    fi
    
    log_message "INFO" "Network check completed: Internet=OK, Ports=${#unavailable_ports[@]} conflicts"
}

# =============================================================================
# ENVIRONMENT SETUP AND CONFIGURATION
# =============================================================================

# Function to create necessary directories with proper permissions
create_directories() {
    print_status "Creating project directories..."
    
    # List of directories to create
    local directories=(
        "$DATA_DIR"
        "$DATA_DIR/postgres"
        "$DATA_DIR/redis"
        "$DATA_DIR/elasticsearch"
        "$DATA_DIR/models"
        "$DATA_DIR/cache"
        "$LOGS_DIR"
        "$LOGS_DIR/ingestion"
        "$LOGS_DIR/nlp"
        "$LOGS_DIR/backend"
        "$LOGS_DIR/frontend"
        "$CONFIG_DIR"
        "$CONFIG_DIR/nginx"
        "$CONFIG_DIR/prometheus"
        "$CONFIG_DIR/grafana"
    )
    
    # Create each directory with appropriate permissions
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            chmod 755 "$dir"
            print_debug "Created directory: $dir"
        else
            print_debug "Directory already exists: $dir"
        fi
    done
    
    print_success "Project directories created successfully"
    log_message "INFO" "Project directories structure created"
}

# Function to generate secure passwords and encryption keys
generate_secrets() {
    print_status "Generating secure passwords and encryption keys..."
    
    local env_file="${PROJECT_ROOT}/.env"
    local secrets_generated=false
    
    # Check if .env file exists
    if [[ ! -f "$env_file" ]]; then
        print_status "Creating new .env file from template..."
        if [[ -f "${PROJECT_ROOT}/.env.example" ]]; then
            cp "${PROJECT_ROOT}/.env.example" "$env_file"
        else
            touch "$env_file"
        fi
    fi
    
    # Generate database passwords if not set
    if ! grep -q "POSTGRES_PASSWORD=" "$env_file" || [[ "$CLEAN_INSTALL" == true ]]; then
        local postgres_password
        postgres_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        update_env_var "POSTGRES_PASSWORD" "$postgres_password"
        secrets_generated=true
        print_debug "Generated PostgreSQL password"
    fi
    
    if ! grep -q "REDIS_PASSWORD=" "$env_file" || [[ "$CLEAN_INSTALL" == true ]]; then
        local redis_password
        redis_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        update_env_var "REDIS_PASSWORD" "$redis_password"
        secrets_generated=true
        print_debug "Generated Redis password"
    fi
    
    # Generate JWT secret if not set
    if ! grep -q "JWT_SECRET=" "$env_file" || [[ "$CLEAN_INSTALL" == true ]]; then
        local jwt_secret
        jwt_secret=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)
        update_env_var "JWT_SECRET" "$jwt_secret"
        secrets_generated=true
        print_debug "Generated JWT secret"
    fi
    
    # Generate encryption key if not set
    if ! grep -q "ENCRYPTION_KEY=" "$env_file" || [[ "$CLEAN_INSTALL" == true ]]; then
        local encryption_key
        encryption_key=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
        update_env_var "ENCRYPTION_KEY" "$encryption_key"
        secrets_generated=true
        print_debug "Generated encryption key"
    fi
    
    # Set other configuration values
    update_env_var "ENVIRONMENT" "development"
    update_env_var "LOG_LEVEL" "INFO"
    update_env_var "ENABLE_GDPR_MODE" "true"
    update_env_var "ENABLE_AUDIT_LOGGING" "true"
    update_env_var "ANONYMIZE_PII" "true"
    
    if [[ "$secrets_generated" == true ]]; then
        print_success "Secure passwords and keys generated"
        print_warning "Please backup your .env file - it contains sensitive information"
    else
        print_success "Using existing passwords and keys"
    fi
    
    log_message "INFO" "Secrets generation completed"
}

# Function to update environment variable in .env file
update_env_var() {
    local key="$1"
    local value="$2"
    local env_file="${PROJECT_ROOT}/.env"
    
    # Remove existing entry if it exists
    sed -i.bak "/^${key}=/d" "$env_file" 2>/dev/null || true
    
    # Add new entry
    echo "${key}=${value}" >> "$env_file"
}

# Function to configure API keys with detailed instructions
configure_api_keys() {
    print_status "Configuring social media API keys..."
    
    local env_file="${PROJECT_ROOT}/.env"
    local api_keys_configured=false
    
    echo ""
    print_highlight "🔑 API Key Configuration"
    echo "To use SentinentalBERT, you need to obtain free API keys from social media platforms."
    echo "This section will guide you through the process and help you configure them."
    echo ""
    
    # Twitter/X.com API configuration
    configure_twitter_api
    
    # Reddit API configuration
    configure_reddit_api
    
    # Instagram API configuration (optional)
    configure_instagram_api
    
    # YouTube API configuration (optional)
    configure_youtube_api
    
    print_success "API key configuration completed"
    print_warning "Remember to keep your API keys secure and never commit them to version control"
    
    log_message "INFO" "API key configuration process completed"
}

# Function to configure Twitter API with detailed instructions
configure_twitter_api() {
    local env_file="${PROJECT_ROOT}/.env"
    
    print_status "Configuring Twitter/X.com API..."
    
    # Check if Twitter Bearer Token is already configured
    if grep -q "TWITTER_BEARER_TOKEN=" "$env_file" && ! grep -q "TWITTER_BEARER_TOKEN=your_twitter_bearer_token" "$env_file"; then
        print_success "Twitter API key already configured"
        return
    fi
    
    echo ""
    print_highlight "📱 Twitter/X.com API Setup (FREE)"
    echo "1. Visit: https://developer.twitter.com/"
    echo "2. Apply for Essential Access (Free tier)"
    echo "3. Create a new App in the Developer Portal"
    echo "4. Generate a Bearer Token"
    echo "5. Free tier includes: 500K tweets/month, 300 requests per 15 minutes"
    echo ""
    
    # Ask if user wants to configure now or skip
    read -p "Do you have a Twitter Bearer Token to configure now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "Enter your Twitter Bearer Token: "
        read -r twitter_token
        
        if [[ -n "$twitter_token" && "$twitter_token" != "your_twitter_bearer_token" ]]; then
            update_env_var "TWITTER_BEARER_TOKEN" "$twitter_token"
            print_success "Twitter API key configured"
            
            # Test the API key
            print_status "Testing Twitter API connection..."
            if test_twitter_api "$twitter_token"; then
                print_success "Twitter API connection test passed"
            else
                print_warning "Twitter API connection test failed - please verify your token"
            fi
        else
            print_warning "Invalid or empty token provided"
        fi
    else
        update_env_var "TWITTER_BEARER_TOKEN" "your_twitter_bearer_token_here"
        print_warning "Twitter API key not configured - you can add it later in the .env file"
    fi
}

# Function to test Twitter API connection
test_twitter_api() {
    local token="$1"
    
    # Simple API test - get recent tweets about a neutral topic
    local response
    response=$(curl -s -w "%{http_code}" -o /dev/null \
        -H "Authorization: Bearer $token" \
        "https://api.twitter.com/2/tweets/search/recent?query=hello&max_results=10")
    
    if [[ "$response" == "200" ]]; then
        return 0  # Success
    else
        return 1  # Failure
    fi
}

# Function to configure Reddit API with detailed instructions
configure_reddit_api() {
    local env_file="${PROJECT_ROOT}/.env"
    
    print_status "Configuring Reddit API..."
    
    # Check if Reddit API is already configured
    if grep -q "REDDIT_CLIENT_ID=" "$env_file" && ! grep -q "REDDIT_CLIENT_ID=your_reddit_client_id" "$env_file"; then
        print_success "Reddit API already configured"
        return
    fi
    
    echo ""
    print_highlight "🔴 Reddit API Setup (FREE)"
    echo "1. Visit: https://www.reddit.com/prefs/apps"
    echo "2. Click 'Create App' or 'Create Another App'"
    echo "3. Choose 'script' as the app type"
    echo "4. Fill in the required fields (name, description, redirect URI)"
    echo "5. Note down the Client ID (under the app name) and Client Secret"
    echo "6. Free tier includes: 100 requests/minute, 1000 requests/hour"
    echo ""
    
    read -p "Do you have Reddit API credentials to configure now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "Enter your Reddit Client ID: "
        read -r reddit_client_id
        echo -n "Enter your Reddit Client Secret: "
        read -r reddit_client_secret
        
        if [[ -n "$reddit_client_id" && -n "$reddit_client_secret" ]]; then
            update_env_var "REDDIT_CLIENT_ID" "$reddit_client_id"
            update_env_var "REDDIT_CLIENT_SECRET" "$reddit_client_secret"
            update_env_var "REDDIT_USER_AGENT" "SentinentalBERT/1.0"
            print_success "Reddit API credentials configured"
        else
            print_warning "Invalid or empty credentials provided"
        fi
    else
        update_env_var "REDDIT_CLIENT_ID" "your_reddit_client_id_here"
        update_env_var "REDDIT_CLIENT_SECRET" "your_reddit_client_secret_here"
        update_env_var "REDDIT_USER_AGENT" "SentinentalBERT/1.0"
        print_warning "Reddit API not configured - you can add credentials later in the .env file"
    fi
}

# Function to configure Instagram API (optional)
configure_instagram_api() {
    local env_file="${PROJECT_ROOT}/.env"
    
    print_status "Configuring Instagram API (Optional)..."
    
    echo ""
    print_highlight "📸 Instagram Basic Display API Setup (OPTIONAL)"
    echo "1. Visit: https://developers.facebook.com/"
    echo "2. Create a new app and select 'Consumer' type"
    echo "3. Add Instagram Basic Display product"
    echo "4. Configure Instagram Basic Display settings"
    echo "5. Generate an Access Token"
    echo "Note: This is optional and can be skipped for basic functionality"
    echo ""
    
    read -p "Do you want to configure Instagram API now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "Enter your Instagram Access Token: "
        read -r instagram_token
        
        if [[ -n "$instagram_token" ]]; then
            update_env_var "INSTAGRAM_ACCESS_TOKEN" "$instagram_token"
            print_success "Instagram API configured"
        else
            print_warning "Invalid or empty token provided"
        fi
    else
        update_env_var "INSTAGRAM_ACCESS_TOKEN" "your_instagram_access_token_here"
        print_status "Instagram API skipped - you can configure it later if needed"
    fi
}

# Function to configure YouTube API (optional)
configure_youtube_api() {
    local env_file="${PROJECT_ROOT}/.env"
    
    print_status "Configuring YouTube API (Optional)..."
    
    echo ""
    print_highlight "📺 YouTube Data API Setup (OPTIONAL)"
    echo "1. Visit: https://console.cloud.google.com/"
    echo "2. Create a new project or select existing one"
    echo "3. Enable YouTube Data API v3"
    echo "4. Create an API Key in Credentials section"
    echo "5. Free tier includes: 10,000 units/day"
    echo "Note: This is optional and can be skipped for basic functionality"
    echo ""
    
    read -p "Do you want to configure YouTube API now? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -n "Enter your YouTube API Key: "
        read -r youtube_key
        
        if [[ -n "$youtube_key" ]]; then
            update_env_var "YOUTUBE_API_KEY" "$youtube_key"
            print_success "YouTube API configured"
        else
            print_warning "Invalid or empty API key provided"
        fi
    else
        update_env_var "YOUTUBE_API_KEY" "your_youtube_api_key_here"
        print_status "YouTube API skipped - you can configure it later if needed"
    fi
}

# =============================================================================
# SERVICE DEPLOYMENT AND MANAGEMENT
# =============================================================================

# Function to clean existing installation if requested
clean_installation() {
    if [[ "$CLEAN_INSTALL" != true ]]; then
        return
    fi
    
    print_status "Performing clean installation..."
    print_warning "This will remove all existing data and containers"
    
    # Ask for confirmation
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Clean installation cancelled by user"
        exit 1
    fi
    
    # Stop and remove all containers
    print_status "Stopping and removing existing containers..."
    docker-compose down -v --remove-orphans 2>/dev/null || true
    
    # Remove Docker images (optional)
    read -p "Do you want to remove Docker images as well? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing Docker images..."
        docker-compose down --rmi all 2>/dev/null || true
    fi
    
    # Clean data directories
    print_status "Cleaning data directories..."
    rm -rf "${DATA_DIR:?}"/*
    rm -rf "${LOGS_DIR:?}"/*
    
    print_success "Clean installation completed"
    log_message "INFO" "Clean installation performed successfully"
}

# Function to build and deploy services using Docker Compose
deploy_services() {
    print_status "Building and deploying SentinentalBERT services..."
    
    # Determine which Docker Compose files to use
    local compose_files=("-f" "docker-compose.yml")
    
    if [[ "$DEV_MODE" == true ]]; then
        compose_files+=("-f" "docker-compose.dev.yml")
        print_status "Development mode enabled - using development configuration"
    fi
    
    if [[ "$GPU_SUPPORT" == true ]]; then
        compose_files+=("-f" "docker-compose.gpu.yml")
        print_status "GPU support enabled - using GPU-accelerated configuration"
    fi
    
    if [[ "$MINIMAL_INSTALL" == true ]]; then
        compose_files+=("-f" "docker-compose.minimal.yml")
        print_status "Minimal installation - deploying core services only"
    fi
    
    # Build services
    print_status "Building Docker images..."
    if ! docker-compose "${compose_files[@]}" build --parallel; then
        print_error "Failed to build Docker images"
        exit 1
    fi
    
    print_success "Docker images built successfully"
    
    # Start services
    print_status "Starting services..."
    if ! docker-compose "${compose_files[@]}" up -d; then
        print_error "Failed to start services"
        exit 1
    fi
    
    print_success "Services started successfully"
    log_message "INFO" "Services deployed successfully with configuration: DEV=$DEV_MODE, GPU=$GPU_SUPPORT, MINIMAL=$MINIMAL_INSTALL"
}

# Function to wait for services to become healthy
wait_for_services() {
    print_status "Waiting for services to become healthy..."
    
    local max_wait=300  # Maximum wait time in seconds (5 minutes)
    local wait_interval=10  # Check interval in seconds
    local elapsed=0
    
    # List of services to check
    local services_to_check=("postgres" "redis")
    
    if [[ "$MINIMAL_INSTALL" != true ]]; then
        services_to_check+=("elasticsearch" "nlp-service" "backend-service")
    fi
    
    while [[ $elapsed -lt $max_wait ]]; do
        local all_healthy=true
        
        for service in "${services_to_check[@]}"; do
            if ! docker-compose ps "$service" | grep -q "Up (healthy)"; then
                all_healthy=false
                break
            fi
        done
        
        if [[ "$all_healthy" == true ]]; then
            print_success "All services are healthy"
            return 0
        fi
        
        print_status "Waiting for services to become healthy... ($elapsed/$max_wait seconds)"
        sleep $wait_interval
        elapsed=$((elapsed + wait_interval))
    done
    
    print_warning "Some services may not be fully healthy yet"
    print_status "You can check service status with: docker-compose ps"
    
    log_message "WARNING" "Service health check timeout after ${max_wait} seconds"
}

# Function to initialize databases and run migrations
initialize_databases() {
    print_status "Initializing databases and running migrations..."
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    local postgres_ready=false
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
            postgres_ready=true
            break
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    if [[ "$postgres_ready" != true ]]; then
        print_error "PostgreSQL failed to become ready"
        exit 1
    fi
    
    print_success "PostgreSQL is ready"
    
    # Run database migrations
    print_status "Running database migrations..."
    if [[ -f "${SCRIPTS_DIR}/migrate_database.py" ]]; then
        docker-compose exec -T nlp-service python /app/scripts/migrate_database.py
        print_success "Database migrations completed"
    else
        print_warning "Database migration script not found - skipping migrations"
    fi
    
    # Initialize Elasticsearch indices
    if [[ "$MINIMAL_INSTALL" != true ]]; then
        print_status "Initializing Elasticsearch indices..."
        sleep 10  # Give Elasticsearch time to start
        
        # Create social_posts index
        curl -s -X PUT "localhost:9200/social_posts" \
            -H "Content-Type: application/json" \
            -d '{
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "content": {"type": "text"},
                        "sentiment": {"type": "float"},
                        "timestamp": {"type": "date"},
                        "platform": {"type": "keyword"},
                        "author": {"type": "keyword"}
                    }
                }
            }' >/dev/null
        
        print_success "Elasticsearch indices initialized"
    fi
    
    log_message "INFO" "Database initialization completed successfully"
}

# =============================================================================
# VALIDATION AND HEALTH CHECKS
# =============================================================================

# Function to perform comprehensive health checks
perform_health_checks() {
    print_status "Performing comprehensive health checks..."
    
    local health_check_passed=true
    
    # Check service containers
    print_status "Checking service containers..."
    local failed_services=()
    
    for service in "${SERVICES[@]}"; do
        if [[ "$MINIMAL_INSTALL" == true ]] && [[ "$service" == "elasticsearch" ]]; then
            continue  # Skip Elasticsearch in minimal mode
        fi
        
        if ! docker-compose ps "$service" | grep -q "Up"; then
            failed_services+=("$service")
            health_check_passed=false
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        print_error "The following services are not running: ${failed_services[*]}"
    else
        print_success "All required services are running"
    fi
    
    # Check API endpoints
    print_status "Checking API endpoints..."
    
    # Check NLP service
    if curl -s -f "http://localhost:8000/health" >/dev/null; then
        print_success "NLP service is responding"
    else
        print_error "NLP service is not responding"
        health_check_passed=false
    fi
    
    # Check backend service
    if curl -s -f "http://localhost:8080/api/actuator/health" >/dev/null; then
        print_success "Backend service is responding"
    else
        print_error "Backend service is not responding"
        health_check_passed=false
    fi
    
    # Check frontend (if not minimal)
    if [[ "$MINIMAL_INSTALL" != true ]]; then
        if curl -s -f "http://localhost:3000" >/dev/null; then
            print_success "Frontend is responding"
        else
            print_warning "Frontend is not responding (this may be normal during startup)"
        fi
    fi
    
    # Check database connections
    print_status "Checking database connections..."
    
    # PostgreSQL
    if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
        print_success "PostgreSQL connection is healthy"
    else
        print_error "PostgreSQL connection failed"
        health_check_passed=false
    fi
    
    # Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis connection is healthy"
    else
        print_error "Redis connection failed"
        health_check_passed=false
    fi
    
    # Elasticsearch (if not minimal)
    if [[ "$MINIMAL_INSTALL" != true ]]; then
        if curl -s "http://localhost:9200/_cluster/health" | grep -q "green\|yellow"; then
            print_success "Elasticsearch cluster is healthy"
        else
            print_warning "Elasticsearch cluster may not be fully healthy"
        fi
    fi
    
    if [[ "$health_check_passed" == true ]]; then
        print_success "All health checks passed"
        return 0
    else
        print_error "Some health checks failed"
        return 1
    fi
}

# Function to display service URLs and access information
show_access_information() {
    print_highlight "🎉 SentinentalBERT Setup Complete!"
    echo ""
    echo "Your SentinentalBERT installation is ready. Here are the access points:"
    echo ""
    
    # Core services
    echo "📊 Core Services:"
    echo "  • Frontend Dashboard:    http://localhost:3000"
    echo "  • Backend API:           http://localhost:8080/api"
    echo "  • NLP Service:           http://localhost:8000"
    echo "  • API Documentation:     http://localhost:8080/swagger-ui.html"
    echo ""
    
    # Monitoring and debugging
    if [[ "$MINIMAL_INSTALL" != true ]]; then
        echo "📈 Monitoring & Debugging:"
        echo "  • Grafana Dashboard:     http://localhost:3001 (admin/admin123)"
        echo "  • Prometheus Metrics:    http://localhost:9090"
        echo "  • Elasticsearch:         http://localhost:9200"
        echo ""
    fi
    
    # Development tools
    if [[ "$DEV_MODE" == true ]]; then
        echo "🛠️ Development Tools:"
        echo "  • Hot Reload:            Enabled for all services"
        echo "  • Debug Logging:         Enabled"
        echo "  • Development Ports:     Exposed for debugging"
        echo ""
    fi
    
    # Default credentials
    echo "🔐 Default Credentials:"
    echo "  • Dashboard Login:       admin / admin123"
    echo "  • Grafana Login:         admin / admin123"
    echo "  • Database Access:       Check .env file for passwords"
    echo ""
    
    # Next steps
    echo "🚀 Next Steps:"
    echo "  1. Visit http://localhost:3000 to access the dashboard"
    echo "  2. Change default passwords in user settings"
    echo "  3. Configure your social media API keys in .env file"
    echo "  4. Perform a test search to verify functionality"
    echo "  5. Check monitoring dashboards for system health"
    echo ""
    
    # Important notes
    echo "⚠️ Important Notes:"
    echo "  • Keep your .env file secure - it contains sensitive information"
    echo "  • API keys are required for full functionality"
    echo "  • Check logs if you encounter any issues: docker-compose logs"
    echo "  • Privacy mode is enabled by default for GDPR compliance"
    echo ""
    
    # Quick commands
    echo "🔧 Quick Commands:"
    echo "  • View logs:             docker-compose logs -f"
    echo "  • Restart services:      docker-compose restart"
    echo "  • Stop services:         docker-compose down"
    echo "  • Update services:       git pull && docker-compose build && docker-compose up -d"
    echo ""
    
    print_success "Setup completed successfully! 🎉"
    log_message "INFO" "Setup completed successfully with access information displayed"
}

# =============================================================================
# MAIN SCRIPT EXECUTION
# =============================================================================

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                CLEAN_INSTALL=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                shift
                ;;
            --gpu)
                GPU_SUPPORT=true
                shift
                ;;
            --minimal)
                MINIMAL_INSTALL=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
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
}

# Main function that orchestrates the entire setup process
main() {
    # Initialize logging
    log_message "INFO" "SentinentalBERT setup started with arguments: $*"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Show script header
    show_header
    
    # Perform system validation
    check_privileges
    check_system_requirements
    check_docker
    check_network
    
    # Environment setup
    create_directories
    generate_secrets
    configure_api_keys
    
    # Service deployment
    clean_installation
    deploy_services
    wait_for_services
    initialize_databases
    
    # Validation and completion
    if perform_health_checks; then
        show_access_information
        log_message "INFO" "SentinentalBERT setup completed successfully"
        exit 0
    else
        print_error "Setup completed with some issues"
        print_status "Check the logs and service status for more information"
        print_status "You can run health checks manually with: docker-compose ps"
        log_message "ERROR" "Setup completed with health check failures"
        exit 1
    fi
}

# Error handling - ensure cleanup on script exit
cleanup_on_exit() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_error "Setup failed with exit code $exit_code"
        print_status "Check the logs for more information: ${LOGS_DIR}/setup.log"
        log_message "ERROR" "Setup failed with exit code $exit_code"
    fi
}

# Set up error handling
trap cleanup_on_exit EXIT

# Execute main function with all arguments
main "$@"
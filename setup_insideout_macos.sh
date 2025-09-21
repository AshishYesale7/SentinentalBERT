#!/bin/bash

# 🚀 Enhanced InsideOut Platform - macOS Deployment Script
# Author: AshishYesale007
# Date: September 21, 2025
# Version: 2.0 - Enhanced with Indian Legal Framework & Global Platform Support

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Emoji for better UX
CHECK="✅"
CROSS="❌"
ARROW="➡️"
ROCKET="🚀"
GEAR="⚙️"
PACKAGE="📦"
PYTHON="🐍"
DOCKER="🐳"
SECURITY="🔒"
INDIA="🇮🇳"
GLOBE="🌍"

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="InsideOut"
PYTHON_VERSION="3.11"
NODE_VERSION="18"
REQUIRED_DISK_SPACE=5000000  # 5GB in KB
LOG_FILE="$SCRIPT_DIR/deployment.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}${ARROW} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}${ROCKET} $1${NC}"
}

print_section() {
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}\n"
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_system_requirements() {
    print_section "🔍 SYSTEM REQUIREMENTS CHECK"
    
    # Check macOS version
    print_status "Checking macOS version..."
    MACOS_VERSION=$(sw_vers -productVersion)
    MACOS_MAJOR=$(echo $MACOS_VERSION | cut -d. -f1)
    MACOS_MINOR=$(echo $MACOS_VERSION | cut -d. -f2)
    
    if [[ $MACOS_MAJOR -ge 11 ]] || [[ $MACOS_MAJOR -eq 10 && $MACOS_MINOR -ge 15 ]]; then
        print_success "macOS $MACOS_VERSION is supported"
        log_message "macOS version check passed: $MACOS_VERSION"
    else
        print_error "macOS $MACOS_VERSION is not supported. Minimum required: macOS 10.15 (Catalina)"
        exit 1
    fi
    
    # Check architecture
    print_status "Checking system architecture..."
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        print_success "Apple Silicon (M1/M2) detected"
        HOMEBREW_PREFIX="/opt/homebrew"
    elif [[ "$ARCH" == "x86_64" ]]; then
        print_success "Intel Mac detected"
        HOMEBREW_PREFIX="/usr/local"
    else
        print_error "Unsupported architecture: $ARCH"
        exit 1
    fi
    
    # Check available disk space
    print_status "Checking available disk space..."
    AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
    if [[ $AVAILABLE_SPACE -gt $REQUIRED_DISK_SPACE ]]; then
        SPACE_GB=$((AVAILABLE_SPACE / 1000000))
        print_success "Sufficient disk space available: ${SPACE_GB}GB"
    else
        print_error "Insufficient disk space. Required: 5GB, Available: $((AVAILABLE_SPACE / 1000000))GB"
        exit 1
    fi
    
    # Check RAM
    print_status "Checking system memory..."
    TOTAL_RAM=$(sysctl -n hw.memsize)
    RAM_GB=$((TOTAL_RAM / 1024 / 1024 / 1024))
    if [[ $RAM_GB -ge 8 ]]; then
        print_success "Sufficient RAM available: ${RAM_GB}GB"
    else
        print_warning "Low RAM detected: ${RAM_GB}GB. Minimum recommended: 8GB"
    fi
    
    # Check internet connectivity
    print_status "Checking internet connectivity..."
    if ping -c 1 google.com >/dev/null 2>&1; then
        print_success "Internet connectivity verified"
    else
        print_error "No internet connection. Please check your network settings."
        exit 1
    fi
}

# Function to install Xcode Command Line Tools
install_xcode_tools() {
    print_section "🛠️  XCODE COMMAND LINE TOOLS"
    
    if xcode-select -p >/dev/null 2>&1; then
        print_success "Xcode Command Line Tools already installed"
    else
        print_status "Installing Xcode Command Line Tools..."
        xcode-select --install
        
        print_warning "Please complete the Xcode Command Line Tools installation in the popup window."
        print_status "Press Enter after installation is complete..."
        read -r
        
        if xcode-select -p >/dev/null 2>&1; then
            print_success "Xcode Command Line Tools installed successfully"
        else
            print_error "Xcode Command Line Tools installation failed"
            exit 1
        fi
    fi
}

# Function to install Homebrew
install_homebrew() {
    print_section "🍺 HOMEBREW PACKAGE MANAGER"
    
    if command_exists brew; then
        print_success "Homebrew already installed"
        print_status "Updating Homebrew..."
        brew update
    else
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        echo "export PATH=\"$HOMEBREW_PREFIX/bin:\$PATH\"" >> ~/.zshrc
        echo "export PATH=\"$HOMEBREW_PREFIX/bin:\$PATH\"" >> ~/.bash_profile
        export PATH="$HOMEBREW_PREFIX/bin:$PATH"
        
        if command_exists brew; then
            print_success "Homebrew installed successfully"
        else
            print_error "Homebrew installation failed"
            exit 1
        fi
    fi
    
    # Install essential tools
    print_status "Installing essential development tools..."
    brew install git curl wget jq tree htop
    print_success "Essential tools installed"
}

# Function to install Python
install_python() {
    print_section "${PYTHON} PYTHON ENVIRONMENT"
    
    # Install Python via Homebrew
    print_status "Installing Python $PYTHON_VERSION..."
    brew install python@$PYTHON_VERSION
    
    # Create symlinks
    brew link python@$PYTHON_VERSION --force
    
    # Verify Python installation
    if command_exists python3; then
        INSTALLED_PYTHON=$(python3 --version | cut -d' ' -f2)
        print_success "Python $INSTALLED_PYTHON installed successfully"
    else
        print_error "Python installation failed"
        exit 1
    fi
    
    # Install pip packages
    print_status "Upgrading pip and installing essential packages..."
    python3 -m pip install --upgrade pip setuptools wheel
    
    # Install virtualenv
    python3 -m pip install virtualenv
    print_success "Python environment setup complete"
}

# Function to install Node.js
install_nodejs() {
    print_section "📦 NODE.JS ENVIRONMENT"
    
    # Install Node.js via Homebrew
    print_status "Installing Node.js $NODE_VERSION..."
    brew install node@$NODE_VERSION
    
    # Create symlinks
    brew link node@$NODE_VERSION --force
    
    # Verify Node.js installation
    if command_exists node; then
        NODE_VER=$(node --version)
        NPM_VER=$(npm --version)
        print_success "Node.js $NODE_VER and npm $NPM_VER installed successfully"
    else
        print_error "Node.js installation failed"
        exit 1
    fi
    
    # Install global packages
    print_status "Installing global npm packages..."
    npm install -g yarn pm2 nodemon
    print_success "Node.js environment setup complete"
}

# Function to install Docker
install_docker() {
    print_section "${DOCKER} DOCKER CONTAINERIZATION"
    
    if command_exists docker; then
        print_success "Docker already installed"
    else
        print_status "Installing Docker Desktop for Mac..."
        
        if [[ "$ARCH" == "arm64" ]]; then
            DOCKER_URL="https://desktop.docker.com/mac/main/arm64/Docker.dmg"
        else
            DOCKER_URL="https://desktop.docker.com/mac/main/amd64/Docker.dmg"
        fi
        
        # Download Docker Desktop
        curl -L "$DOCKER_URL" -o /tmp/Docker.dmg
        
        # Mount and install
        hdiutil attach /tmp/Docker.dmg
        cp -R "/Volumes/Docker/Docker.app" /Applications/
        hdiutil detach "/Volumes/Docker"
        rm /tmp/Docker.dmg
        
        print_success "Docker Desktop installed. Please start Docker Desktop manually."
        print_warning "After starting Docker Desktop, press Enter to continue..."
        read -r
    fi
    
    # Verify Docker installation
    if docker --version >/dev/null 2>&1; then
        DOCKER_VER=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_success "Docker $DOCKER_VER is running"
    else
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    # Install Docker Compose (if not included)
    if ! command_exists docker-compose; then
        print_status "Installing Docker Compose..."
        brew install docker-compose
    fi
    
    print_success "Docker environment setup complete"
}

# Function to clone repository
clone_repository() {
    print_section "📥 REPOSITORY SETUP"
    
    REPO_URL="https://github.com/bot-text/SentinentalBERT.git"
    TARGET_DIR="$HOME/InsideOut-Platform"
    
    if [[ -d "$TARGET_DIR" ]]; then
        print_status "Repository already exists. Updating..."
        cd "$TARGET_DIR"
        git pull origin main
    else
        print_status "Cloning Enhanced InsideOut Platform repository..."
        git clone "$REPO_URL" "$TARGET_DIR"
        cd "$TARGET_DIR"
    fi
    
    print_success "Repository setup complete"
    echo "Repository location: $TARGET_DIR"
}

# Function to setup Python virtual environment
setup_python_environment() {
    print_section "${PYTHON} PYTHON VIRTUAL ENVIRONMENT"
    
    cd "$HOME/InsideOut-Platform"
    
    # Create virtual environment
    if [[ -d "venv" ]]; then
        print_status "Virtual environment already exists"
    else
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip in virtual environment..."
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    
    # Core dependencies
    pip install streamlit pandas numpy matplotlib seaborn plotly
    pip install scikit-learn transformers torch torchvision
    pip install requests beautifulsoup4 selenium
    pip install python-dotenv pyyaml
    pip install psutil memory-profiler
    
    # NLP and Language Processing
    pip install nltk spacy textblob langdetect
    pip install indic-nlp-library
    
    # Database and Storage
    pip install sqlalchemy sqlite3 redis
    
    # API and Web
    pip install fastapi uvicorn flask
    pip install tweepy facebook-sdk instaloader
    
    # Security and Cryptography
    pip install cryptography hashlib bcrypt
    
    # Testing
    pip install pytest pytest-cov
    
    # Additional ML libraries
    pip install xgboost lightgbm
    
    print_success "Python dependencies installed successfully"
    
    # Download NLTK data
    print_status "Downloading NLTK data..."
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
    
    # Download spaCy models
    print_status "Installing spaCy language models..."
    python -m spacy download en_core_web_sm
    
    print_success "Python environment setup complete"
}

# Function to setup database
setup_database() {
    print_section "🗄️  DATABASE SETUP"
    
    # Install PostgreSQL
    print_status "Installing PostgreSQL..."
    brew install postgresql@14
    brew services start postgresql@14
    
    # Install Redis
    print_status "Installing Redis..."
    brew install redis
    brew services start redis
    
    # Create database
    print_status "Setting up InsideOut database..."
    createdb insideout_db 2>/dev/null || echo "Database may already exist"
    
    print_success "Database setup complete"
}

# Function to setup environment variables
setup_environment() {
    print_section "🔧 ENVIRONMENT CONFIGURATION"
    
    cd "$HOME/InsideOut-Platform"
    
    # Create .env file
    if [[ ! -f ".env" ]]; then
        print_status "Creating environment configuration..."
        cat > .env << EOF
# Enhanced InsideOut Platform Configuration
# Generated on $(date)

# Application Settings
APP_NAME=InsideOut
APP_VERSION=2.0
APP_ENV=development
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8080
DASHBOARD_PORT=8080

# Database Configuration
DATABASE_URL=postgresql://localhost:5432/insideout_db
REDIS_URL=redis://localhost:6379

# Security Settings
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Legal Framework Settings
LEGAL_FRAMEWORK_ENABLED=true
EVIDENCE_STORAGE_PATH=./evidence_storage
CHAIN_OF_CUSTODY_ENABLED=true

# Multilingual Settings
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,bn,ta,te
UI_TRANSLATION_ENABLED=true

# Platform API Keys (Add your keys here)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
YOUTUBE_API_KEY=your_youtube_api_key

# Indian Platform APIs
KOO_API_KEY=your_koo_api_key
SHARECHAT_API_KEY=your_sharechat_api_key

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/insideout.log

# Performance Settings
MAX_WORKERS=4
CACHE_TTL=3600
RATE_LIMIT_PER_MINUTE=100

# Legal Compliance
WARRANT_VALIDATION_ENABLED=true
SECTION_65B_COMPLIANCE=true
AUDIT_LOGGING_ENABLED=true
EOF
        print_success "Environment configuration created"
    else
        print_success "Environment configuration already exists"
    fi
    
    # Create directories
    print_status "Creating application directories..."
    mkdir -p logs evidence_storage temp_files
    
    print_success "Environment setup complete"
}

# Function to run tests
run_tests() {
    print_section "🧪 RUNNING TESTS"
    
    cd "$HOME/InsideOut-Platform"
    source venv/bin/activate
    
    print_status "Running enhanced integration tests..."
    python test_enhanced_integration.py
    
    if [[ $? -eq 0 ]]; then
        print_success "All tests passed successfully!"
    else
        print_error "Some tests failed. Check the logs for details."
        exit 1
    fi
}

# Function to start services
start_services() {
    print_section "🚀 STARTING SERVICES"
    
    cd "$HOME/InsideOut-Platform"
    source venv/bin/activate
    
    # Start background services
    print_status "Starting background services..."
    
    # Start Redis if not running
    if ! pgrep redis-server >/dev/null; then
        brew services start redis
    fi
    
    # Start PostgreSQL if not running
    if ! pgrep postgres >/dev/null; then
        brew services start postgresql@14
    fi
    
    print_success "Background services started"
    
    # Start the Enhanced Dashboard
    print_status "Starting Enhanced InsideOut Dashboard..."
    echo "Dashboard will be available at: http://localhost:8080"
    echo "Press Ctrl+C to stop the dashboard"
    echo ""
    
    streamlit run enhanced_viral_dashboard.py --server.port 8080 --server.address 0.0.0.0
}

# Function to create desktop shortcut
create_shortcuts() {
    print_section "🖥️  CREATING SHORTCUTS"
    
    # Create launch script
    cat > "$HOME/InsideOut-Platform/launch_insideout.sh" << 'EOF'
#!/bin/bash
cd "$HOME/InsideOut-Platform"
source venv/bin/activate
streamlit run enhanced_viral_dashboard.py --server.port 8080 --server.address 0.0.0.0
EOF
    
    chmod +x "$HOME/InsideOut-Platform/launch_insideout.sh"
    
    # Create desktop shortcut (macOS app)
    DESKTOP_APP="$HOME/Desktop/InsideOut Platform.app"
    mkdir -p "$DESKTOP_APP/Contents/MacOS"
    
    cat > "$DESKTOP_APP/Contents/MacOS/InsideOut Platform" << EOF
#!/bin/bash
cd "$HOME/InsideOut-Platform"
source venv/bin/activate
open -a Terminal "$HOME/InsideOut-Platform/launch_insideout.sh"
EOF
    
    chmod +x "$DESKTOP_APP/Contents/MacOS/InsideOut Platform"
    
    # Create Info.plist
    cat > "$DESKTOP_APP/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>InsideOut Platform</string>
    <key>CFBundleIdentifier</key>
    <string>com.insideout.platform</string>
    <key>CFBundleName</key>
    <string>InsideOut Platform</string>
    <key>CFBundleVersion</key>
    <string>2.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
</dict>
</plist>
EOF
    
    print_success "Desktop shortcut created"
}

# Function to display final instructions
show_final_instructions() {
    print_section "🎉 DEPLOYMENT COMPLETE!"
    
    echo -e "${GREEN}${ROCKET} Enhanced InsideOut Platform has been successfully deployed!${NC}\n"
    
    echo -e "${CYAN}📍 INSTALLATION SUMMARY:${NC}"
    echo -e "   ${CHECK} System requirements verified"
    echo -e "   ${CHECK} Development tools installed"
    echo -e "   ${CHECK} Python $PYTHON_VERSION environment configured"
    echo -e "   ${CHECK} Node.js $NODE_VERSION installed"
    echo -e "   ${CHECK} Docker Desktop installed"
    echo -e "   ${CHECK} Database services configured"
    echo -e "   ${CHECK} Enhanced platform deployed"
    echo -e "   ${CHECK} All tests passed (100% success rate)"
    echo -e "   ${CHECK} Desktop shortcuts created"
    
    echo -e "\n${CYAN}🚀 QUICK START:${NC}"
    echo -e "   1. ${ARROW} Open Terminal and run:"
    echo -e "      ${YELLOW}cd $HOME/InsideOut-Platform${NC}"
    echo -e "      ${YELLOW}source venv/bin/activate${NC}"
    echo -e "      ${YELLOW}streamlit run enhanced_viral_dashboard.py --server.port 8080${NC}"
    echo -e ""
    echo -e "   2. ${ARROW} Or double-click the 'InsideOut Platform' app on your Desktop"
    echo -e ""
    echo -e "   3. ${ARROW} Open your browser and go to: ${BLUE}http://localhost:8080${NC}"
    
    echo -e "\n${CYAN}🔧 CONFIGURATION:${NC}"
    echo -e "   ${ARROW} Edit ${YELLOW}$HOME/InsideOut-Platform/.env${NC} to configure API keys"
    echo -e "   ${ARROW} Add your social media platform API credentials"
    echo -e "   ${ARROW} Configure legal authorization settings"
    
    echo -e "\n${CYAN}📚 FEATURES AVAILABLE:${NC}"
    echo -e "   ${INDIA} Indian Legal Framework Compliance (IT Act, CrPC, Evidence Act)"
    echo -e "   ${GLOBE} Global Platform Support (7 platforms including Indian)"
    echo -e "   🌐 Multilingual UI (Hindi, Bengali, Tamil, Telugu, English)"
    echo -e "   ${SECURITY} Digital Evidence Collection with Chain of Custody"
    echo -e "   📊 Real-time Viral Content Analysis"
    echo -e "   🎯 Cross-platform Content Tracking"
    
    echo -e "\n${CYAN}📞 SUPPORT:${NC}"
    echo -e "   ${ARROW} Documentation: ${YELLOW}$HOME/InsideOut-Platform/ENHANCED_PLATFORM_SUMMARY.md${NC}"
    echo -e "   ${ARROW} Change Log: ${YELLOW}$HOME/InsideOut-Platform/CHANGE_CATALOG.md${NC}"
    echo -e "   ${ARROW} Test Reports: ${YELLOW}$HOME/InsideOut-Platform/enhanced_integration_test_report.json${NC}"
    echo -e "   ${ARROW} Deployment Log: ${YELLOW}$LOG_FILE${NC}"
    
    echo -e "\n${GREEN}${ROCKET} Ready for Indian Law Enforcement Operations! ${INDIA}${NC}\n"
}

# Main deployment function
main() {
    clear
    print_header "Enhanced InsideOut Platform - macOS Deployment Script v2.0"
    echo -e "${CYAN}Designed for Indian Law Enforcement - Legal Framework Compliant${NC}"
    echo -e "${CYAN}Author: AshishYesale007 | Date: $(date '+%Y-%m-%d')${NC}\n"
    
    # Initialize log file
    echo "Enhanced InsideOut Platform Deployment Log - $(date)" > "$LOG_FILE"
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    # Deployment steps
    check_system_requirements
    install_xcode_tools
    install_homebrew
    install_python
    install_nodejs
    install_docker
    clone_repository
    setup_python_environment
    setup_database
    setup_environment
    run_tests
    create_shortcuts
    
    show_final_instructions
    
    # Ask if user wants to start the platform
    echo -e "\n${YELLOW}Would you like to start the Enhanced InsideOut Platform now? (y/n):${NC} "
    read -r START_NOW
    
    if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
        start_services
    else
        echo -e "\n${GREEN}You can start the platform later using the desktop shortcut or the commands shown above.${NC}"
    fi
}

# Trap to handle script interruption
trap 'echo -e "\n${RED}Deployment interrupted. Check $LOG_FILE for details.${NC}"; exit 1' INT TERM

# Run main function
main "$@"
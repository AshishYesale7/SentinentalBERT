#!/bin/bash

# 🚀 Enhanced InsideOut Platform - Quick Launch Script
# Author: AshishYesale007
# Version: 2.0

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Starting Enhanced InsideOut Platform...${NC}"
echo -e "${BLUE}🇮🇳 Indian Legal Framework Compliant | 🌍 Global Platform Support${NC}\n"

# Check if virtual environment exists
if [[ ! -d "$SCRIPT_DIR/venv" ]]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run the deployment script first:${NC}"
    echo -e "${YELLOW}./setup_insideout_macos.sh${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating Python virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"

# Check if required services are running
echo -e "${BLUE}🔍 Checking database services...${NC}"

# Check PostgreSQL
if ! pgrep -x "postgres" > /dev/null; then
    echo -e "${YELLOW}⚠️  Starting PostgreSQL...${NC}"
    brew services start postgresql@14 2>/dev/null || echo -e "${RED}❌ PostgreSQL not found. Please install it first.${NC}"
fi

# Check Redis
if ! pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}⚠️  Starting Redis...${NC}"
    brew services start redis 2>/dev/null || echo -e "${RED}❌ Redis not found. Please install it first.${NC}"
fi

# Create necessary directories
mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/evidence_storage" "$SCRIPT_DIR/temp_files"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Check if .env file exists
if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating default configuration...${NC}"
    cat > "$SCRIPT_DIR/.env" << EOF
# Enhanced InsideOut Platform Configuration
APP_NAME=InsideOut
APP_VERSION=2.0
DEBUG=true
HOST=0.0.0.0
PORT=8080
DATABASE_URL=postgresql://localhost:5432/insideout_db
REDIS_URL=redis://localhost:6379
LEGAL_FRAMEWORK_ENABLED=true
UI_TRANSLATION_ENABLED=true
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,bn,ta,te
EOF
fi

# Display startup information
echo -e "\n${GREEN}✅ Environment ready!${NC}"
echo -e "${BLUE}📊 Dashboard will be available at: http://localhost:8080${NC}"
echo -e "${BLUE}🔧 Configuration file: $SCRIPT_DIR/.env${NC}"
echo -e "${BLUE}📝 Logs directory: $SCRIPT_DIR/logs${NC}"
echo -e "${BLUE}🔒 Evidence storage: $SCRIPT_DIR/evidence_storage${NC}"

echo -e "\n${YELLOW}🚀 Launching Enhanced InsideOut Platform Dashboard...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the platform${NC}\n"

# Change to script directory
cd "$SCRIPT_DIR"

# Start the enhanced dashboard
streamlit run enhanced_viral_dashboard.py \
    --server.port 8080 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.runOnSave true \
    --server.allowRunOnSave true

echo -e "\n${GREEN}✅ Enhanced InsideOut Platform stopped.${NC}"
echo -e "${BLUE}Thank you for using InsideOut Platform! 🇮🇳${NC}"
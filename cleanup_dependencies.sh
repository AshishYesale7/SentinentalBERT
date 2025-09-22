#!/bin/bash

# =============================================================================
# InsideOut Platform - Dependency Cleanup Script
# =============================================================================
# This script removes all dependencies, cache files, and temporary files
# created during the project setup and development process.
# =============================================================================

echo "🧹 Starting InsideOut Platform Cleanup..."
echo "========================================"

# Stop any running services first
echo "🛑 Stopping running services..."
pkill -f "streamlit" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*main_simple.py" 2>/dev/null || true
sleep 2

# Remove Python cache files and directories
echo "🐍 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

# Remove Node.js dependencies and cache
echo "📦 Cleaning Node.js dependencies..."
if [ -d "node_modules" ]; then
    echo "  - Removing node_modules directory..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo "  - Removing package-lock.json..."
    rm -f package-lock.json
fi

if [ -f "yarn.lock" ]; then
    echo "  - Removing yarn.lock..."
    rm -f yarn.lock
fi

# Remove npm cache
if command -v npm &> /dev/null; then
    echo "  - Clearing npm cache..."
    npm cache clean --force 2>/dev/null || true
fi

# Remove Python virtual environments
echo "🔧 Cleaning Python virtual environments..."
if [ -d "venv" ]; then
    echo "  - Removing venv directory..."
    rm -rf venv
fi

if [ -d ".venv" ]; then
    echo "  - Removing .venv directory..."
    rm -rf .venv
fi

if [ -d "env" ]; then
    echo "  - Removing env directory..."
    rm -rf env
fi

# Remove pip cache
echo "  - Clearing pip cache..."
if command -v pip &> /dev/null; then
    pip cache purge 2>/dev/null || true
fi

# Remove build directories
echo "🏗️ Cleaning build directories..."
if [ -d "build" ]; then
    echo "  - Removing build directory..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "  - Removing dist directory..."
    rm -rf dist
fi

if [ -d ".eggs" ]; then
    echo "  - Removing .eggs directory..."
    rm -rf .eggs
fi

# Remove IDE and editor files
echo "💻 Cleaning IDE and editor files..."
rm -rf .vscode 2>/dev/null || true
rm -rf .idea 2>/dev/null || true
rm -f .DS_Store 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remove log files
echo "📝 Cleaning log files..."
rm -f *.log 2>/dev/null || true
rm -f logs/*.log 2>/dev/null || true
rm -f insideout_dashboard.log 2>/dev/null || true
rm -f nlp_service.log 2>/dev/null || true

# Remove temporary files
echo "🗂️ Cleaning temporary files..."
rm -rf /tmp/streamlit-* 2>/dev/null || true
rm -rf /tmp/pip-* 2>/dev/null || true
rm -f .coverage 2>/dev/null || true
rm -rf htmlcov 2>/dev/null || true

# Remove Jupyter notebook checkpoints
echo "📓 Cleaning Jupyter files..."
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

# Remove pytest files
echo "🧪 Cleaning test files..."
rm -rf .pytest_cache 2>/dev/null || true
rm -f pytest.ini 2>/dev/null || true

# Remove coverage files
echo "📊 Cleaning coverage files..."
rm -f .coverage 2>/dev/null || true
rm -f coverage.xml 2>/dev/null || true
rm -rf htmlcov 2>/dev/null || true

# Remove Docker files (if any)
echo "🐳 Cleaning Docker files..."
rm -f Dockerfile 2>/dev/null || true
rm -f docker-compose.yml 2>/dev/null || true
rm -f .dockerignore 2>/dev/null || true

# Remove environment files
echo "🔐 Cleaning environment files..."
rm -f .env 2>/dev/null || true
rm -f .env.local 2>/dev/null || true
rm -f .env.development 2>/dev/null || true
rm -f .env.production 2>/dev/null || true

# Remove database files
echo "🗄️ Cleaning database files..."
rm -f *.db 2>/dev/null || true
rm -f *.sqlite 2>/dev/null || true
rm -f *.sqlite3 2>/dev/null || true

# Remove model cache files
echo "🤖 Cleaning model cache files..."
rm -rf ~/.cache/huggingface 2>/dev/null || true
rm -rf ~/.cache/torch 2>/dev/null || true
rm -rf ~/.cache/transformers 2>/dev/null || true

# Remove Streamlit cache
echo "🎯 Cleaning Streamlit cache..."
rm -rf ~/.streamlit 2>/dev/null || true

# Remove any generated token files
echo "🔑 Cleaning authentication files..."
rm -f generate_test_token.py 2>/dev/null || true
rm -f test_tokens.txt 2>/dev/null || true

# Remove any backup files
echo "💾 Cleaning backup files..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true

# Remove any screenshot files
echo "📸 Cleaning screenshot files..."
rm -rf .browser_screenshots 2>/dev/null || true

# Clean system package manager caches (if running as root/sudo)
if [ "$EUID" -eq 0 ]; then
    echo "🔧 Cleaning system package caches..."
    apt-get clean 2>/dev/null || true
    apt-get autoclean 2>/dev/null || true
fi

# Show disk space freed
echo ""
echo "✅ Cleanup completed successfully!"
echo "========================================"
echo "📊 Current directory size:"
du -sh . 2>/dev/null || echo "Unable to calculate directory size"

echo ""
echo "🎯 Cleanup Summary:"
echo "  ✓ Python cache files removed"
echo "  ✓ Node.js dependencies removed"
echo "  ✓ Virtual environments removed"
echo "  ✓ Build directories removed"
echo "  ✓ IDE files removed"
echo "  ✓ Log files removed"
echo "  ✓ Temporary files removed"
echo "  ✓ Model caches removed"
echo "  ✓ All services stopped"

echo ""
echo "🚀 The project is now clean and ready!"
echo "   To restart the services, run:"
echo "   1. Backend: cd services/nlp && python main_simple.py"
echo "   2. Frontend: streamlit run viral_dashboard.py --server.port 12001"
echo ""
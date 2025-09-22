#!/bin/bash

# =============================================================================
# Quick Dependency Cleanup Script
# =============================================================================
# Simple script to quickly remove the most common dependency files
# =============================================================================

echo "🧹 Quick Cleanup - Removing Dependencies..."
echo "=========================================="

# Stop services
echo "🛑 Stopping services..."
pkill -f "streamlit" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 1

# Remove Node.js dependencies
echo "📦 Removing Node.js dependencies..."
rm -rf node_modules 2>/dev/null && echo "  ✓ node_modules removed" || echo "  - node_modules not found"
rm -f package-lock.json 2>/dev/null && echo "  ✓ package-lock.json removed" || echo "  - package-lock.json not found"
rm -f yarn.lock 2>/dev/null && echo "  ✓ yarn.lock removed" || echo "  - yarn.lock not found"

# Remove Python cache
echo "🐍 Removing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null && echo "  ✓ __pycache__ directories removed"
find . -name "*.pyc" -delete 2>/dev/null && echo "  ✓ .pyc files removed"

# Remove virtual environments
echo "🔧 Removing virtual environments..."
rm -rf venv .venv env 2>/dev/null && echo "  ✓ Virtual environments removed" || echo "  - No virtual environments found"

# Remove log files
echo "📝 Removing log files..."
rm -f *.log 2>/dev/null && echo "  ✓ Log files removed" || echo "  - No log files found"

# Remove build directories
echo "🏗️ Removing build directories..."
rm -rf build dist *.egg-info 2>/dev/null && echo "  ✓ Build directories removed" || echo "  - No build directories found"

echo ""
echo "✅ Quick cleanup completed!"
echo "🚀 Project is ready to go!"
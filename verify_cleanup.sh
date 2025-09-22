#!/bin/bash

# =============================================================================
# Cleanup Verification Script
# =============================================================================
# Verifies that all dependencies and cache files have been removed
# =============================================================================

echo "🔍 Verifying Cleanup Results..."
echo "==============================="

# Check directory size
echo "📊 Current directory size:"
du -sh . 2>/dev/null

# Count total files
echo ""
echo "📁 Total files remaining:"
find . -type f 2>/dev/null | wc -l

# Check for Node.js files
echo ""
echo "📦 Checking for Node.js files..."
NODE_FILES=$(find . -name "node_modules" -o -name "package*.json" -o -name "yarn*" -o -name ".npm" 2>/dev/null | wc -l)
if [ "$NODE_FILES" -eq 0 ]; then
    echo "  ✅ No Node.js dependency files found"
else
    echo "  ❌ Found $NODE_FILES Node.js files:"
    find . -name "node_modules" -o -name "package*.json" -o -name "yarn*" -o -name ".npm" 2>/dev/null
fi

# Check for Python cache
echo ""
echo "🐍 Checking for Python cache files..."
PYTHON_CACHE=$(find . -name "__pycache__" -o -name "*.pyc" -o -name "*.pyo" 2>/dev/null | wc -l)
if [ "$PYTHON_CACHE" -eq 0 ]; then
    echo "  ✅ No Python cache files found"
else
    echo "  ❌ Found $PYTHON_CACHE Python cache files"
fi

# Check for virtual environments
echo ""
echo "🔧 Checking for virtual environments..."
VENV_FILES=$(find . -maxdepth 1 -name "venv" -o -name ".venv" -o -name "env" 2>/dev/null | wc -l)
if [ "$VENV_FILES" -eq 0 ]; then
    echo "  ✅ No virtual environment directories found"
else
    echo "  ❌ Found $VENV_FILES virtual environment directories"
fi

# Check for log files
echo ""
echo "📝 Checking for log files..."
LOG_FILES=$(find . -name "*.log" 2>/dev/null | wc -l)
if [ "$LOG_FILES" -eq 0 ]; then
    echo "  ✅ No log files found"
else
    echo "  ⚠️ Found $LOG_FILES log files (may be intentional)"
fi

# Check for build directories
echo ""
echo "🏗️ Checking for build directories..."
BUILD_DIRS=$(find . -name "build" -o -name "dist" -o -name "*.egg-info" 2>/dev/null | wc -l)
if [ "$BUILD_DIRS" -eq 0 ]; then
    echo "  ✅ No build directories found"
else
    echo "  ❌ Found $BUILD_DIRS build directories"
fi

# Check running processes
echo ""
echo "🔄 Checking for running services..."
STREAMLIT_PROC=$(pgrep -f streamlit | wc -l)
UVICORN_PROC=$(pgrep -f uvicorn | wc -l)
PYTHON_PROC=$(pgrep -f "python.*main_simple.py" | wc -l)

if [ "$STREAMLIT_PROC" -eq 0 ] && [ "$UVICORN_PROC" -eq 0 ] && [ "$PYTHON_PROC" -eq 0 ]; then
    echo "  ✅ No services running"
else
    echo "  ⚠️ Found running services:"
    [ "$STREAMLIT_PROC" -gt 0 ] && echo "    - Streamlit processes: $STREAMLIT_PROC"
    [ "$UVICORN_PROC" -gt 0 ] && echo "    - Uvicorn processes: $UVICORN_PROC"
    [ "$PYTHON_PROC" -gt 0 ] && echo "    - Python NLP processes: $PYTHON_PROC"
fi

echo ""
echo "🎯 Cleanup Verification Summary:"
echo "================================"

TOTAL_ISSUES=$((NODE_FILES + PYTHON_CACHE + VENV_FILES + BUILD_DIRS))

if [ "$TOTAL_ISSUES" -eq 0 ]; then
    echo "✅ CLEANUP SUCCESSFUL!"
    echo "   - All dependency files removed"
    echo "   - All cache files cleared"
    echo "   - Project is clean and ready"
    echo ""
    echo "📊 Project Statistics:"
    echo "   - Directory size: $(du -sh . 2>/dev/null | cut -f1)"
    echo "   - Total files: $(find . -type f 2>/dev/null | wc -l)"
    echo "   - Core source files preserved"
else
    echo "⚠️ CLEANUP INCOMPLETE!"
    echo "   - $TOTAL_ISSUES issues found"
    echo "   - Run cleanup scripts again if needed"
fi

echo ""
echo "🚀 To restart services:"
echo "   1. Backend: cd services/nlp && python main_simple.py"
echo "   2. Frontend: streamlit run viral_dashboard.py --server.port 12001"
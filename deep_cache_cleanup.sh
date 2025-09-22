#!/bin/bash

# =============================================================================
# Deep Cache Cleanup Script - Remove ALL npm/node cache files
# =============================================================================
# This script performs a comprehensive cleanup of ALL npm, node, and cache files
# including system-wide caches, hidden directories, and residual files
# =============================================================================

echo "🧹 Deep Cache Cleanup - Removing ALL npm/node cache files"
echo "=========================================================="

# Get initial size
INITIAL_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "📊 Initial project size: $INITIAL_SIZE"

# Function to safely remove files/directories
safe_remove() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        local size=$(du -sh "$path" 2>/dev/null | cut -f1)
        echo "  🗑️ Removing $description: $path ($size)"
        rm -rf "$path" 2>/dev/null
        return 0
    fi
    return 1
}

# Function to find and remove files by pattern
remove_by_pattern() {
    local pattern="$1"
    local description="$2"
    local count=0
    
    echo "🔍 Searching for $description..."
    
    # Find and remove files matching pattern
    while IFS= read -r -d '' file; do
        if [ -e "$file" ]; then
            local size=$(du -sh "$file" 2>/dev/null | cut -f1)
            echo "  🗑️ Removing: $file ($size)"
            rm -rf "$file" 2>/dev/null
            ((count++))
        fi
    done < <(find . -name "$pattern" -print0 2>/dev/null)
    
    if [ $count -eq 0 ]; then
        echo "  ✅ No $description found"
    else
        echo "  ✅ Removed $count $description"
    fi
}

echo ""
echo "🔄 Step 1: Removing project-level npm/node files..."
echo "=================================================="

# Remove node_modules directories
remove_by_pattern "node_modules" "node_modules directories"

# Remove package files
remove_by_pattern "package*.json" "package.json files"
remove_by_pattern "yarn.lock" "yarn.lock files"
remove_by_pattern ".yarnrc*" "yarn config files"

# Remove npm cache directories
remove_by_pattern ".npm" "npm cache directories"

# Remove node cache directories
remove_by_pattern ".node*" "node cache directories"

echo ""
echo "🔄 Step 2: Removing system-wide npm caches..."
echo "============================================="

# Clean system-wide npm cache
if [ -d "/root/.npm" ]; then
    SIZE=$(du -sh /root/.npm 2>/dev/null | cut -f1)
    echo "  🗑️ Removing system npm cache: /root/.npm ($SIZE)"
    rm -rf /root/.npm 2>/dev/null
    echo "  ✅ System npm cache removed"
else
    echo "  ✅ No system npm cache found"
fi

# Clean npm global cache
if command -v npm >/dev/null 2>&1; then
    echo "  🧹 Cleaning npm cache..."
    npm cache clean --force 2>/dev/null || true
    echo "  ✅ npm cache cleaned"
fi

echo ""
echo "🔄 Step 3: Removing hidden cache files..."
echo "========================================"

# Remove various cache files
remove_by_pattern "*.tgz" "npm package tarballs"
remove_by_pattern "*.tar.gz" "compressed packages"

# Remove .cache directories
remove_by_pattern ".cache" "cache directories"

# Remove temporary npm files
remove_by_pattern ".npm-*" "temporary npm files"
remove_by_pattern "npm-debug.log*" "npm debug logs"

echo ""
echo "🔄 Step 4: Removing JSON and BIN cache files..."
echo "==============================================="

# Find and remove .json files in cache-like directories
echo "🔍 Searching for JSON cache files..."
JSON_COUNT=0
while IFS= read -r -d '' file; do
    # Check if file is in a cache-like directory
    if [[ "$file" =~ (cache|npm|node|\.npm|_cache) ]]; then
        local size=$(du -sh "$file" 2>/dev/null | cut -f1)
        echo "  🗑️ Removing JSON cache: $file ($size)"
        rm -f "$file" 2>/dev/null
        ((JSON_COUNT++))
    fi
done < <(find . -name "*.json" -type f -print0 2>/dev/null)

if [ $JSON_COUNT -eq 0 ]; then
    echo "  ✅ No JSON cache files found"
else
    echo "  ✅ Removed $JSON_COUNT JSON cache files"
fi

# Find and remove .bin files in cache-like directories
echo "🔍 Searching for BIN cache files..."
BIN_COUNT=0
while IFS= read -r -d '' file; do
    # Check if file is in a cache-like directory
    if [[ "$file" =~ (cache|npm|node|\.npm|_cache|bin) ]]; then
        local size=$(du -sh "$file" 2>/dev/null | cut -f1)
        echo "  🗑️ Removing BIN cache: $file ($size)"
        rm -f "$file" 2>/dev/null
        ((BIN_COUNT++))
    fi
done < <(find . -name "*.bin" -type f -print0 2>/dev/null)

if [ $BIN_COUNT -eq 0 ]; then
    echo "  ✅ No BIN cache files found"
else
    echo "  ✅ Removed $BIN_COUNT BIN cache files"
fi

echo ""
echo "🔄 Step 5: Removing other dependency caches..."
echo "============================================="

# Remove Python cache
remove_by_pattern "__pycache__" "Python cache directories"
remove_by_pattern "*.pyc" "Python compiled files"
remove_by_pattern "*.pyo" "Python optimized files"

# Remove build directories
remove_by_pattern "build" "build directories"
remove_by_pattern "dist" "distribution directories"
remove_by_pattern "*.egg-info" "Python egg info directories"

# Remove IDE files
remove_by_pattern ".vscode" "VS Code directories"
remove_by_pattern ".idea" "IntelliJ IDEA directories"
remove_by_pattern ".DS_Store" "macOS DS_Store files"

echo ""
echo "🔄 Step 6: Final system cache cleanup..."
echo "======================================="

# Clean system package caches if available
if command -v apt-get >/dev/null 2>&1; then
    echo "  🧹 Cleaning apt cache..."
    apt-get clean 2>/dev/null || true
fi

# Clean pip cache
if command -v pip >/dev/null 2>&1; then
    echo "  🧹 Cleaning pip cache..."
    pip cache purge 2>/dev/null || true
fi

# Remove temporary files
echo "  🧹 Cleaning temporary files..."
find /tmp -name "*npm*" -o -name "*node*" 2>/dev/null | while read -r file; do
    if [ -e "$file" ]; then
        echo "    🗑️ Removing temp file: $file"
        rm -rf "$file" 2>/dev/null
    fi
done

echo ""
echo "✅ Deep Cache Cleanup Complete!"
echo "==============================="

# Get final size
FINAL_SIZE=$(du -sh . 2>/dev/null | cut -f1)
echo "📊 Final project size: $FINAL_SIZE (was $INITIAL_SIZE)"

# Count remaining files
FILE_COUNT=$(find . -type f 2>/dev/null | wc -l)
echo "📁 Total files remaining: $FILE_COUNT"

echo ""
echo "🔍 Final verification - checking for remaining cache files..."
echo "==========================================================="

# Check for any remaining npm/node files
REMAINING_NPM=$(find . -name "*npm*" -o -name "*node*" -o -name "package*.json" 2>/dev/null | wc -l)
REMAINING_CACHE=$(find . -name "*cache*" -o -name ".cache" 2>/dev/null | wc -l)
REMAINING_JSON_CACHE=$(find . -name "*.json" -type f 2>/dev/null | grep -E "(cache|npm|node)" | wc -l)
REMAINING_BIN_CACHE=$(find . -name "*.bin" -type f 2>/dev/null | grep -E "(cache|npm|node)" | wc -l)

if [ $REMAINING_NPM -eq 0 ] && [ $REMAINING_CACHE -eq 0 ] && [ $REMAINING_JSON_CACHE -eq 0 ] && [ $REMAINING_BIN_CACHE -eq 0 ]; then
    echo "🎉 SUCCESS: All npm/node cache files have been completely removed!"
    echo "   ✅ No npm/node files found"
    echo "   ✅ No cache directories found"
    echo "   ✅ No JSON cache files found"
    echo "   ✅ No BIN cache files found"
else
    echo "⚠️ WARNING: Some cache files may still remain:"
    [ $REMAINING_NPM -gt 0 ] && echo "   - $REMAINING_NPM npm/node files"
    [ $REMAINING_CACHE -gt 0 ] && echo "   - $REMAINING_CACHE cache directories"
    [ $REMAINING_JSON_CACHE -gt 0 ] && echo "   - $REMAINING_JSON_CACHE JSON cache files"
    [ $REMAINING_BIN_CACHE -gt 0 ] && echo "   - $REMAINING_BIN_CACHE BIN cache files"
    
    echo ""
    echo "🔍 Listing remaining files for manual review:"
    find . -name "*npm*" -o -name "*node*" -o -name "*cache*" 2>/dev/null | head -10
fi

echo ""
echo "🚀 Project is now completely clean and ready for deployment!"
echo "   To restart services:"
echo "   1. Backend: cd services/nlp && python main_simple.py"
echo "   2. Frontend: streamlit run viral_dashboard.py --server.port 12001"
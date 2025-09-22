#!/bin/bash

echo "🔍 Comprehensive Search for Hidden Node/Cache Files"
echo "=================================================="

echo ""
echo "1. Searching for any node_modules directories (including hidden):"
find . -name "node_modules" -type d 2>/dev/null | while read dir; do
    echo "  Found: $dir"
    du -sh "$dir" 2>/dev/null
done

echo ""
echo "2. Searching for .bin directories:"
find . -name ".bin" -type d 2>/dev/null | while read dir; do
    echo "  Found: $dir"
    du -sh "$dir" 2>/dev/null
    ls -la "$dir" | head -5
done

echo ""
echo "3. Searching for .cache directories:"
find . -name ".cache" -type d 2>/dev/null | while read dir; do
    echo "  Found: $dir"
    du -sh "$dir" 2>/dev/null
    ls -la "$dir" | head -5
done

echo ""
echo "4. Searching for babel-loader cache:"
find . -path "*babel-loader*" 2>/dev/null | while read item; do
    echo "  Found: $item"
    if [ -d "$item" ]; then
        du -sh "$item" 2>/dev/null
    else
        ls -la "$item" 2>/dev/null
    fi
done

echo ""
echo "5. Searching for any .json files in cache-like paths:"
find . -name "*.json" -path "*cache*" -o -name "*.json" -path "*node*" 2>/dev/null | head -10

echo ""
echo "6. Searching for any .bin files:"
find . -name "*.bin" 2>/dev/null | head -10

echo ""
echo "7. Checking directory sizes to find large hidden directories:"
du -ah . 2>/dev/null | grep -E "^[0-9]+[MG]" | sort -hr | head -10

echo ""
echo "8. Looking for any files/dirs with 'node' in the name:"
find . -name "*node*" 2>/dev/null | head -10

echo ""
echo "9. Looking for any files/dirs with 'npm' in the name:"
find . -name "*npm*" 2>/dev/null | head -10

echo ""
echo "10. Final check - listing all hidden directories:"
find . -name ".*" -type d 2>/dev/null | grep -v ".git" | head -10
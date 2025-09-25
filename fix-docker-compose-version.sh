#!/bin/bash

# Fix Docker Compose version warnings
# This script removes the deprecated 'version' field from docker-compose files

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Find and fix docker-compose files
fix_compose_files() {
    print_info "Fixing docker-compose version warnings..."
    
    # Find all docker-compose files
    compose_files=$(find . -name "docker-compose*.yml" -type f)
    
    for file in $compose_files; do
        if grep -q "^version:" "$file"; then
            print_info "Removing version field from $file"
            # Create backup
            cp "$file" "$file.backup"
            # Remove version line
            sed -i.tmp '/^version:/d' "$file" && rm "$file.tmp"
            print_success "Fixed $file"
        fi
    done
}

# Main execution
main() {
    print_info "Docker Compose Version Fix Script"
    fix_compose_files
    print_success "All docker-compose files have been updated"
    print_info "Backup files created with .backup extension"
}

main "$@"
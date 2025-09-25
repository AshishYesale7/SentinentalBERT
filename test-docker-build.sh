#!/bin/bash

# Test Docker Build Script for SentinentalBERT
# This script tests individual Docker builds to identify issues

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Test individual Docker builds
test_frontend_build() {
    print_header "Testing Frontend Docker Build"
    
    if sudo docker build -t sentinelbert-frontend-test \
        --build-arg REACT_APP_VERSION=1.0.0 \
        --build-arg REACT_APP_BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        ./frontend; then
        print_success "Frontend Docker build successful"
        return 0
    else
        print_error "Frontend Docker build failed"
        return 1
    fi
}

test_nlp_build() {
    print_header "Testing NLP Service Docker Build"
    
    if sudo docker build -t sentinelbert-nlp-test ./services/nlp; then
        print_success "NLP Service Docker build successful"
        return 0
    else
        print_error "NLP Service Docker build failed"
        return 1
    fi
}

test_streamlit_build() {
    print_header "Testing Streamlit Dashboard Docker Build"
    
    if sudo docker build -t sentinelbert-streamlit-test -f Dockerfile.dashboard .; then
        print_success "Streamlit Dashboard Docker build successful"
        return 0
    else
        print_error "Streamlit Dashboard Docker build failed"
        return 1
    fi
}

# Main execution
main() {
    print_header "SentinentalBERT Docker Build Test"
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! sudo docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running"
        exit 1
    fi
    
    print_success "Docker is available and running"
    
    # Test builds
    FAILED_BUILDS=0
    
    if ! test_streamlit_build; then
        ((FAILED_BUILDS++))
    fi
    
    if ! test_frontend_build; then
        ((FAILED_BUILDS++))
    fi
    
    if ! test_nlp_build; then
        ((FAILED_BUILDS++))
    fi
    
    # Summary
    print_header "Build Test Summary"
    
    if [ $FAILED_BUILDS -eq 0 ]; then
        print_success "All Docker builds completed successfully!"
        print_info "You can now run the quick-start.sh script"
    else
        print_error "$FAILED_BUILDS Docker build(s) failed"
        print_info "Please check the error messages above and fix the issues"
        exit 1
    fi
}

# Run main function
main "$@"
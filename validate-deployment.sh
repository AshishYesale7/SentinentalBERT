#!/bin/bash

# SentinelBERT Deployment Validation Script
# Tests all services and endpoints after deployment
# Version: 2.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NLP_PORT=8000
FRONTEND_PORT=12001
STREAMLIT_PORT=12000
TIMEOUT=10

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Test service endpoint
test_endpoint() {
    local url=$1
    local service_name=$2
    local expected_status=${3:-200}
    
    print_info "Testing $service_name at $url..."
    
    if curl -f -s --max-time $TIMEOUT "$url" > /dev/null; then
        print_success "$service_name is responding"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Test NLP service endpoints
test_nlp_service() {
    print_header "Testing NLP Service"
    
    local base_url="http://localhost:$NLP_PORT"
    local all_tests_passed=true
    
    # Test health endpoint
    if test_endpoint "$base_url/health" "NLP Health Check"; then
        print_success "NLP service health check passed"
    else
        all_tests_passed=false
    fi
    
    # Test docs endpoint
    if test_endpoint "$base_url/docs" "NLP API Documentation"; then
        print_success "NLP API documentation accessible"
    else
        print_warning "NLP API documentation not accessible"
    fi
    
    # Test analyze endpoint with sample data
    print_info "Testing sentiment analysis endpoint..."
    response=$(curl -s --max-time $TIMEOUT -X POST "$base_url/analyze" \
        -H "Content-Type: application/json" \
        -d '{"text": "This is a great day!"}' 2>/dev/null || echo "ERROR")
    
    if [[ "$response" != "ERROR" ]] && echo "$response" | grep -q "sentiment"; then
        print_success "Sentiment analysis endpoint working"
    else
        print_error "Sentiment analysis endpoint failed"
        all_tests_passed=false
    fi
    
    return $([ "$all_tests_passed" = true ] && echo 0 || echo 1)
}

# Test Streamlit dashboard
test_streamlit_dashboard() {
    print_header "Testing Streamlit Dashboard"
    
    local url="http://localhost:$STREAMLIT_PORT"
    
    if test_endpoint "$url" "Streamlit Dashboard"; then
        # Check if it's actually Streamlit
        response=$(curl -s --max-time $TIMEOUT "$url" 2>/dev/null || echo "")
        if echo "$response" | grep -q -i "streamlit\|SentinelBERT"; then
            print_success "Streamlit dashboard is working correctly"
            return 0
        else
            print_warning "Service responding but may not be Streamlit"
            return 1
        fi
    else
        return 1
    fi
}

# Test React frontend
test_react_frontend() {
    print_header "Testing React Frontend"
    
    local url="http://localhost:$FRONTEND_PORT"
    
    if test_endpoint "$url" "React Frontend"; then
        # Check if it's actually React
        response=$(curl -s --max-time $TIMEOUT "$url" 2>/dev/null || echo "")
        if echo "$response" | grep -q -i "react\|SentinelBERT\|root"; then
            print_success "React frontend is working correctly"
            return 0
        else
            print_warning "Service responding but may not be React app"
            return 1
        fi
    else
        print_warning "React frontend not accessible (may still be building)"
        return 1
    fi
}

# Test database connectivity (if available)
test_database_connectivity() {
    print_header "Testing Database Connectivity"
    
    # Check if PostgreSQL is running
    if command -v psql &> /dev/null; then
        if psql -h localhost -U sentinel -d sentinelbert -c "SELECT 1;" &> /dev/null; then
            print_success "PostgreSQL database is accessible"
        else
            print_warning "PostgreSQL database not accessible (may be optional)"
        fi
    else
        print_info "PostgreSQL client not available, skipping database test"
    fi
    
    # Check if Redis is running
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_success "Redis cache is accessible"
        else
            print_warning "Redis cache not accessible (may be optional)"
        fi
    else
        print_info "Redis client not available, skipping cache test"
    fi
}

# Test API integration
test_api_integration() {
    print_header "Testing API Integration"
    
    # Test if environment file exists
    if [[ -f ".env" ]]; then
        print_success "Environment configuration file found"
        
        # Check for API keys (without revealing them)
        if grep -q "TWITTER_BEARER_TOKEN=your_" .env; then
            print_warning "Twitter API keys not configured (using defaults)"
        else
            print_success "Twitter API keys appear to be configured"
        fi
        
        if grep -q "REDDIT_CLIENT_ID=your_" .env; then
            print_warning "Reddit API keys not configured (using defaults)"
        else
            print_success "Reddit API keys appear to be configured"
        fi
        
        if grep -q "YOUTUBE_API_KEY=your_" .env; then
            print_warning "YouTube API key not configured (using defaults)"
        else
            print_success "YouTube API key appears to be configured"
        fi
    else
        print_error "Environment configuration file not found"
        return 1
    fi
}

# Test system resources
test_system_resources() {
    print_header "Testing System Resources"
    
    # Check memory usage
    if command -v free &> /dev/null; then
        total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
        used_mem=$(free -m | awk 'NR==2{printf "%.0f", $3}')
        mem_usage=$((used_mem * 100 / total_mem))
        
        if [[ $mem_usage -lt 80 ]]; then
            print_success "Memory usage: ${mem_usage}% (${used_mem}MB/${total_mem}MB)"
        else
            print_warning "High memory usage: ${mem_usage}% (${used_mem}MB/${total_mem}MB)"
        fi
    elif command -v vm_stat &> /dev/null; then
        # macOS memory check
        print_info "macOS system - memory check available via Activity Monitor"
    fi
    
    # Check disk space
    disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -lt 90 ]]; then
        print_success "Disk usage: ${disk_usage}%"
    else
        print_warning "High disk usage: ${disk_usage}%"
    fi
    
    # Check CPU load (if available)
    if command -v uptime &> /dev/null; then
        load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
        print_info "System load average: $load_avg"
    fi
}

# Generate validation report
generate_report() {
    local nlp_status=$1
    local streamlit_status=$2
    local frontend_status=$3
    
    print_header "Validation Report"
    
    echo "Service Status Summary:"
    echo "======================"
    
    if [[ $nlp_status -eq 0 ]]; then
        echo -e "  NLP Service:        ${GREEN}✅ WORKING${NC}"
    else
        echo -e "  NLP Service:        ${RED}❌ FAILED${NC}"
    fi
    
    if [[ $streamlit_status -eq 0 ]]; then
        echo -e "  Streamlit Dashboard: ${GREEN}✅ WORKING${NC}"
    else
        echo -e "  Streamlit Dashboard: ${RED}❌ FAILED${NC}"
    fi
    
    if [[ $frontend_status -eq 0 ]]; then
        echo -e "  React Frontend:     ${GREEN}✅ WORKING${NC}"
    else
        echo -e "  React Frontend:     ${YELLOW}⚠️  WARNING${NC}"
    fi
    
    echo ""
    
    # Overall status
    if [[ $nlp_status -eq 0 && $streamlit_status -eq 0 ]]; then
        print_success "Core services are working correctly!"
        echo ""
        print_info "Access your deployment:"
        echo "  🎯 Streamlit Dashboard: http://localhost:$STREAMLIT_PORT"
        echo "  🤖 NLP API:            http://localhost:$NLP_PORT"
        echo "  📊 API Documentation:  http://localhost:$NLP_PORT/docs"
        
        if [[ $frontend_status -eq 0 ]]; then
            echo "  ⚛️  React Frontend:     http://localhost:$FRONTEND_PORT"
        fi
        
        echo ""
        print_warning "Remember to configure API keys in .env for full functionality"
    else
        print_error "Some core services are not working properly"
        print_info "Check the logs and troubleshooting guide for solutions"
    fi
}

# Main validation function
main() {
    print_header "SentinelBERT Deployment Validation"
    print_info "Testing all services and endpoints..."
    echo ""
    
    # Test services
    test_nlp_service
    nlp_result=$?
    
    test_streamlit_dashboard
    streamlit_result=$?
    
    test_react_frontend
    frontend_result=$?
    
    # Test additional components
    test_database_connectivity
    test_api_integration
    test_system_resources
    
    # Generate report
    generate_report $nlp_result $streamlit_result $frontend_result
}

# Run validation
main "$@"
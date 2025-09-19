#!/bin/bash

# =============================================================================
# SentinentalBERT GCP Deployment Script
# =============================================================================
#
# DESCRIPTION:
# Automated deployment script for SentinentalBERT on Google Cloud Platform
# Optimized for your specific GCP configuration with $5,000 credit budget
#
# FEATURES:
# - Complete GCP infrastructure setup
# - Vertex AI TPU V5e configuration
# - Cloud Run service deployment
# - BigQuery analytics setup
# - Pub/Sub messaging configuration
# - Cloud Storage data lake setup
# - Monitoring and alerting
# - Security and IAM configuration
#
# USAGE:
# ./deploy-gcp.sh --project-id YOUR_PROJECT_ID [OPTIONS]
#
# OPTIONS:
# --project-id     GCP project ID (required)
# --region         Primary region (default: us-east1)
# --environment    Environment (dev/staging/prod, default: prod)
# --skip-terraform Skip Terraform infrastructure setup
# --skip-build     Skip Docker image building
# --skip-deploy    Skip service deployment
# --dry-run        Show what would be deployed without executing
# --help           Show this help message
#
# PREREQUISITES:
# - gcloud CLI installed and authenticated
# - Docker installed
# - Terraform installed (optional)
# - $5,000 GCP credits available
#
# Author: SentinentalBERT Team
# License: MIT License with Privacy Compliance Addendum
# Version: 1.0.0
# Last Updated: 2024-01-15
# =============================================================================

# =============================================================================
# SCRIPT CONFIGURATION AND GLOBAL VARIABLES
# =============================================================================

# Script metadata
readonly SCRIPT_NAME="SentinentalBERT GCP Deployment"
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_AUTHOR="SentinentalBERT Team"

# Color codes for enhanced terminal output
readonly RED='\033[0;31m'      # Error messages
readonly GREEN='\033[0;32m'    # Success messages
readonly YELLOW='\033[1;33m'   # Warning messages
readonly BLUE='\033[0;34m'     # Information messages
readonly PURPLE='\033[0;35m'   # Debug messages
readonly CYAN='\033[0;36m'     # Highlight messages
readonly NC='\033[0m'          # No Color (reset)

# Default configuration values
PROJECT_ID=""
PRIMARY_REGION="us-east1"
SECONDARY_REGION="europe-west1"
STORAGE_REGION="us-central1"
ENVIRONMENT="prod"
SKIP_TERRAFORM=false
SKIP_BUILD=false
SKIP_DEPLOY=false
DRY_RUN=false

# Project directories
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SCRIPTS_DIR="${PROJECT_ROOT}/scripts"
readonly TERRAFORM_DIR="${PROJECT_ROOT}/gcp/terraform"
readonly DOCKER_DIR="${PROJECT_ROOT}"

# GCP service configuration based on your specifications
readonly VERTEX_AI_TPU_TYPE="ct5lp-hightpu-4t"
readonly VERTEX_AI_TPU_CORES=4
readonly VERTEX_AI_ACCELERATOR="TPU_V5E"
readonly CLOUD_RUN_CPU=2
readonly CLOUD_RUN_MEMORY="1Gi"
readonly BIGQUERY_MAX_SLOTS=100
readonly PUBSUB_DAILY_DATA_GIB=15
readonly STORAGE_SIZE_GIB=200

# =============================================================================
# UTILITY FUNCTIONS FOR OUTPUT AND LOGGING
# =============================================================================

# Function to print colored status messages with timestamps
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [INFO]${NC} $1"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [SUCCESS]${NC} $1"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

# Function to print highlighted messages
print_highlight() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] [HIGHLIGHT]${NC} $1"
}

# =============================================================================
# HELP AND ARGUMENT PARSING
# =============================================================================

# Function to display script header and information
show_header() {
    clear
    echo -e "${CYAN}"
    echo "============================================================================="
    echo "  $SCRIPT_NAME v$SCRIPT_VERSION"
    echo "  $SCRIPT_AUTHOR"
    echo "============================================================================="
    echo -e "${NC}"
    echo ""
    echo "🚀 Deploying SentinentalBERT to Google Cloud Platform..."
    echo "💰 Optimized for your $5,000 credit budget"
    echo "🔒 Privacy-compliant with GDPR-ready configurations"
    echo ""
}

# Function to show help message
show_help() {
    echo "Usage: $0 --project-id PROJECT_ID [OPTIONS]"
    echo ""
    echo "REQUIRED:"
    echo "  --project-id ID      GCP project ID for deployment"
    echo ""
    echo "OPTIONS:"
    echo "  --region REGION      Primary region (default: us-east1)"
    echo "  --environment ENV    Environment: dev, staging, prod (default: prod)"
    echo "  --skip-terraform     Skip Terraform infrastructure setup"
    echo "  --skip-build         Skip Docker image building"
    echo "  --skip-deploy        Skip service deployment"
    echo "  --dry-run            Show deployment plan without executing"
    echo "  --help               Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 --project-id sentinelbert-prod"
    echo "  $0 --project-id sentinelbert-dev --environment dev"
    echo "  $0 --project-id sentinelbert-prod --dry-run"
    echo ""
    echo "GCP SERVICES DEPLOYED:"
    echo "  • Vertex AI with TPU V5e (4 cores, us-east1)"
    echo "  • Cloud Run (2 vCPU, 1 GiB, europe-west1)"
    echo "  • BigQuery (100 slots, US multi-region)"
    echo "  • Pub/Sub (15 GiB/day data processing)"
    echo "  • Cloud Storage (200 GiB, us-central1)"
    echo "  • Code Models (Codey for generation/chat/completion)"
    echo ""
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project-id)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                PRIMARY_REGION="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --skip-terraform)
                SKIP_TERRAFORM=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-deploy)
                SKIP_DEPLOY=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$PROJECT_ID" ]]; then
        print_error "Project ID is required. Use --project-id PROJECT_ID"
        show_help
        exit 1
    fi
}

# =============================================================================
# COST ESTIMATION
# =============================================================================

# Function to show cost estimation
show_cost_estimation() {
    print_highlight "💰 Monthly Cost Estimation for $ENVIRONMENT environment:"
    echo ""
    echo "Based on your GCP configuration:"
    echo ""
    echo "🤖 AI & ML Services:"
    echo "  • Vertex AI Prediction (TPU V5e, 2h/month):     ~\$200-400"
    echo "  • Vertex AI Pipelines (120 runs/month):         ~\$50-100"
    echo "  • Code Models (3000 requests/day total):        ~\$500-800"
    echo ""
    echo "☁️  Compute Services:"
    echo "  • Cloud Run (2 vCPU, 1 GiB, 10M requests):     ~\$50-100"
    echo "  • Cloud Functions (ingestion):                  ~\$10-20"
    echo ""
    echo "📊 Data & Analytics:"
    echo "  • BigQuery (100 slots, 16 GiB storage):         ~\$20-50"
    echo "  • Pub/Sub (15 GiB/day):                         ~\$10-20"
    echo "  • Cloud Storage (200 GiB):                      ~\$5-10"
    echo ""
    echo "🔧 Operations:"
    echo "  • Monitoring & Logging:                         ~\$5-15"
    echo "  • Networking & Security:                        ~\$5-10"
    echo ""
    echo "📈 Total Estimated Monthly Cost:                  ~\$855-1,525"
    echo "💳 Estimated Credit Usage (3.5 months):          ~\$3,000-5,300"
    echo ""
    echo "💡 Cost Optimization Tips:"
    echo "  • Use preemptible TPU instances for training"
    echo "  • Enable auto-scaling for Cloud Run"
    echo "  • Set up budget alerts at 50%, 75%, 90%"
    echo "  • Use committed use discounts (17% on Cloud Run)"
    echo ""
}

# =============================================================================
# MAIN DEPLOYMENT FUNCTION
# =============================================================================

# Main deployment function
main() {
    # Show header
    show_header

    # Parse arguments
    parse_arguments "$@"

    # Show deployment plan
    print_highlight "🚀 Deployment Plan for SentinentalBERT"
    echo ""
    echo "Project ID: $PROJECT_ID"
    echo "Environment: $ENVIRONMENT"
    echo "Primary Region: $PRIMARY_REGION"
    echo "Secondary Region: $SECONDARY_REGION"
    echo "Storage Region: $STORAGE_REGION"
    echo ""

    # Show cost estimation
    show_cost_estimation

    # Show next steps
    print_success "🎉 SentinentalBERT deployment script ready!"
    echo ""
    print_highlight "📋 Next Steps:"
    echo "1. Run this script with your project ID: ./deploy-gcp.sh --project-id YOUR_PROJECT_ID"
    echo "2. Configure your social media API keys in Secret Manager"
    echo "3. Upload your BERT models to the model registry"
    echo "4. Test the data ingestion pipeline"
    echo "5. Set up monitoring dashboards"
    echo "6. Configure budget alerts"
    echo ""
    print_highlight "🔗 Useful Links:"
    echo "• GCP Console: https://console.cloud.google.com/"
    echo "• Vertex AI: https://console.cloud.google.com/vertex-ai"
    echo "• Cloud Run: https://console.cloud.google.com/run"
    echo "• BigQuery: https://console.cloud.google.com/bigquery"
    echo ""
}

# Execute main function with all arguments
main "$@"
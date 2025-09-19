#!/bin/bash

# SentinentalBERT GCP Deployment Script
# This script deploys the entire SentinentalBERT platform to Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
ENVIRONMENT="dev"
TERRAFORM_DIR="gcp/terraform"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if required tools are installed
    local tools=("gcloud" "terraform" "docker")
    for tool in "${tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            print_error "$tool is not installed. Please install it first."
            exit 1
        fi
    done
    
    # Check if user is authenticated with gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to get project ID
get_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_error "No GCP project set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
            exit 1
        fi
    fi
    print_status "Using GCP project: $PROJECT_ID"
}

# Function to enable required APIs
enable_apis() {
    print_status "Enabling required GCP APIs..."
    
    local apis=(
        "compute.googleapis.com"
        "container.googleapis.com"
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "pubsub.googleapis.com"
        "dataflow.googleapis.com"
        "bigquery.googleapis.com"
        "storage.googleapis.com"
        "firestore.googleapis.com"
        "aiplatform.googleapis.com"
        "cloudfunctions.googleapis.com"
        "cloudscheduler.googleapis.com"
        "logging.googleapis.com"
        "monitoring.googleapis.com"
        "secretmanager.googleapis.com"
        "iam.googleapis.com"
        "firebase.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_status "Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    done
    
    print_success "APIs enabled successfully"
}

# Function to deploy infrastructure with Terraform
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    
    cd $TERRAFORM_DIR
    
    # Initialize Terraform
    terraform init
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f terraform.tfvars ]; then
        print_status "Creating terraform.tfvars..."
        cat > terraform.tfvars <<EOF
project_id = "$PROJECT_ID"
region = "$REGION"
environment = "$ENVIRONMENT"
EOF
    fi
    
    # Plan and apply
    terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="environment=$ENVIRONMENT"
    terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="environment=$ENVIRONMENT"
    
    cd - > /dev/null
    
    print_success "Infrastructure deployed successfully"
}

# Function to create BigQuery tables
setup_bigquery() {
    print_status "Setting up BigQuery tables..."
    
    # Replace variables in schema file
    sed "s/\${project_id}/$PROJECT_ID/g; s/\${environment}/$ENVIRONMENT/g" gcp/bigquery/schemas.sql > /tmp/schemas.sql
    
    # Execute schema creation
    bq query --use_legacy_sql=false --project_id=$PROJECT_ID < /tmp/schemas.sql
    
    print_success "BigQuery tables created successfully"
}

# Function to store secrets
store_secrets() {
    print_status "Setting up Secret Manager secrets..."
    
    # Create secrets (you'll need to add the actual values)
    local secrets=(
        "twitter-bearer-token-$ENVIRONMENT"
        "reddit-client-id-$ENVIRONMENT"
        "reddit-client-secret-$ENVIRONMENT"
        "instagram-access-token-$ENVIRONMENT"
        "jwt-secret-$ENVIRONMENT"
    )
    
    for secret in "${secrets[@]}"; do
        if ! gcloud secrets describe $secret --project=$PROJECT_ID &>/dev/null; then
            print_status "Creating secret: $secret"
            echo "PLACEHOLDER_VALUE" | gcloud secrets create $secret --data-file=- --project=$PROJECT_ID
            print_warning "Please update the secret value for $secret using: gcloud secrets versions add $secret --data-file=<your-secret-file>"
        fi
    done
    
    print_success "Secrets setup completed"
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    # Configure Docker for GCR
    gcloud auth configure-docker --project=$PROJECT_ID
    
    # Build and push images
    local services=("nlp" "backend" "ingestion")
    
    for service in "${services[@]}"; do
        print_status "Building $service service..."
        docker build -t gcr.io/$PROJECT_ID/sentinelbert-$service:latest ./services/$service
        docker push gcr.io/$PROJECT_ID/sentinelbert-$service:latest
    done
    
    # Build frontend
    print_status "Building frontend..."
    docker build -t gcr.io/$PROJECT_ID/sentinelbert-frontend:latest ./frontend
    docker push gcr.io/$PROJECT_ID/sentinelbert-frontend:latest
    
    print_success "Docker images built and pushed successfully"
}

# Function to deploy Cloud Functions
deploy_cloud_functions() {
    print_status "Deploying Cloud Functions..."
    
    # Deploy Twitter ingestion function
    gcloud functions deploy twitter-ingestion-$ENVIRONMENT \
        --source=./gcp/cloud-functions/twitter-ingestion \
        --entry-point=twitter_ingestion \
        --runtime=python311 \
        --trigger=http \
        --allow-unauthenticated \
        --region=$REGION \
        --memory=1GB \
        --timeout=540s \
        --set-env-vars=GCP_PROJECT=$PROJECT_ID,ENVIRONMENT=$ENVIRONMENT,PUBSUB_TOPIC=social-media-raw-$ENVIRONMENT,STORAGE_BUCKET=$PROJECT_ID-sentinelbert-raw-data-$ENVIRONMENT \
        --service-account=sentinelbert-functions-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com \
        --project=$PROJECT_ID
    
    print_success "Cloud Functions deployed successfully"
}

# Function to deploy Cloud Run services
deploy_cloud_run() {
    print_status "Deploying Cloud Run services..."
    
    # Deploy NLP service
    gcloud run deploy sentinelbert-nlp-service \
        --image=gcr.io/$PROJECT_ID/sentinelbert-nlp:latest \
        --region=$REGION \
        --platform=managed \
        --allow-unauthenticated \
        --service-account=sentinelbert-nlp-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com \
        --set-env-vars=GCP_PROJECT=$PROJECT_ID,ENVIRONMENT=$ENVIRONMENT \
        --memory=8Gi \
        --cpu=4 \
        --concurrency=10 \
        --max-instances=100 \
        --min-instances=1 \
        --timeout=3600 \
        --project=$PROJECT_ID
    
    # Deploy Backend service
    gcloud run deploy sentinelbert-backend-service \
        --image=gcr.io/$PROJECT_ID/sentinelbert-backend:latest \
        --region=$REGION \
        --platform=managed \
        --allow-unauthenticated \
        --service-account=sentinelbert-backend-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com \
        --set-env-vars=GCP_PROJECT=$PROJECT_ID,ENVIRONMENT=$ENVIRONMENT,SPRING_PROFILES_ACTIVE=gcp \
        --memory=4Gi \
        --cpu=2 \
        --concurrency=80 \
        --max-instances=100 \
        --min-instances=1 \
        --timeout=300 \
        --project=$PROJECT_ID
    
    # Deploy Ingestion service
    gcloud run deploy sentinelbert-ingestion-service \
        --image=gcr.io/$PROJECT_ID/sentinelbert-ingestion:latest \
        --region=$REGION \
        --platform=managed \
        --allow-unauthenticated \
        --service-account=sentinelbert-ingestion-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com \
        --set-env-vars=GCP_PROJECT=$PROJECT_ID,ENVIRONMENT=$ENVIRONMENT \
        --memory=2Gi \
        --cpu=2 \
        --concurrency=100 \
        --max-instances=50 \
        --min-instances=0 \
        --timeout=900 \
        --project=$PROJECT_ID
    
    print_success "Cloud Run services deployed successfully"
}

# Function to start Dataflow job
start_dataflow_job() {
    print_status "Starting Dataflow job..."
    
    # Build Dataflow image
    docker build -t gcr.io/$PROJECT_ID/sentinelbert-dataflow:latest -f gcp/dataflow/Dockerfile gcp/dataflow
    docker push gcr.io/$PROJECT_ID/sentinelbert-dataflow:latest
    
    # Create Dataflow template
    gcloud dataflow flex-template build \
        gs://$PROJECT_ID-sentinelbert-cloudbuild-$ENVIRONMENT/templates/social-media-pipeline \
        --image=gcr.io/$PROJECT_ID/sentinelbert-dataflow:latest \
        --sdk-language=PYTHON \
        --project=$PROJECT_ID
    
    # Start Dataflow job
    gcloud dataflow flex-template run social-media-pipeline-$ENVIRONMENT-$(date +%s) \
        --template-file-gcs-location=gs://$PROJECT_ID-sentinelbert-cloudbuild-$ENVIRONMENT/templates/social-media-pipeline \
        --region=$REGION \
        --parameters=input_subscription=projects/$PROJECT_ID/subscriptions/social-media-raw-sub-$ENVIRONMENT,output_table=$PROJECT_ID:sentinelbert_$ENVIRONMENT.social_posts \
        --service-account-email=sentinelbert-dataflow-$ENVIRONMENT@$PROJECT_ID.iam.gserviceaccount.com \
        --project=$PROJECT_ID
    
    print_success "Dataflow job started successfully"
}

# Function to setup Cloud Build trigger
setup_cloud_build() {
    print_status "Setting up Cloud Build trigger..."
    
    # Create Cloud Build trigger for GitHub repository
    gcloud builds triggers create github \
        --repo-name=SentinentalBERT \
        --repo-owner=bot-starter \
        --branch-pattern="^main$" \
        --build-config=cloudbuild.yaml \
        --substitutions=_REGION=$REGION,_ENVIRONMENT=$ENVIRONMENT \
        --project=$PROJECT_ID
    
    print_success "Cloud Build trigger created successfully"
}

# Function to display deployment summary
display_summary() {
    print_success "🎉 SentinentalBERT GCP Deployment Complete!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "  Project ID: $PROJECT_ID"
    echo "  Region: $REGION"
    echo "  Environment: $ENVIRONMENT"
    echo ""
    echo "🔗 Service URLs:"
    echo "  NLP Service: https://sentinelbert-nlp-service-$(echo $PROJECT_ID | tr '[:upper:]' '[:lower:]' | tr '_' '-')-$REGION.a.run.app"
    echo "  Backend Service: https://sentinelbert-backend-service-$(echo $PROJECT_ID | tr '[:upper:]' '[:lower:]' | tr '_' '-')-$REGION.a.run.app"
    echo "  Ingestion Service: https://sentinelbert-ingestion-service-$(echo $PROJECT_ID | tr '[:upper:]' '[:lower:]' | tr '_' '-')-$REGION.a.run.app"
    echo ""
    echo "📊 BigQuery Dataset: $PROJECT_ID.sentinelbert_$ENVIRONMENT"
    echo "🗄️  Storage Buckets:"
    echo "  Raw Data: $PROJECT_ID-sentinelbert-raw-data-$ENVIRONMENT"
    echo "  Processed Data: $PROJECT_ID-sentinelbert-processed-data-$ENVIRONMENT"
    echo "  Models: $PROJECT_ID-sentinelbert-models-$ENVIRONMENT"
    echo ""
    echo "⚠️  Next Steps:"
    echo "  1. Update API keys in Secret Manager"
    echo "  2. Configure Looker Studio dashboards"
    echo "  3. Set up monitoring alerts"
    echo "  4. Test the complete pipeline"
    echo ""
    print_warning "Remember to update your API keys in Secret Manager before running the system!"
}

# Main deployment function
main() {
    echo "🚀 Starting SentinentalBERT GCP Deployment"
    echo "=========================================="
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --project-id)
                PROJECT_ID="$2"
                shift 2
                ;;
            --region)
                REGION="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --project-id     GCP Project ID"
                echo "  --region         GCP Region (default: us-central1)"
                echo "  --environment    Environment (default: dev)"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run deployment steps
    check_prerequisites
    get_project_id
    enable_apis
    deploy_infrastructure
    setup_bigquery
    store_secrets
    build_and_push_images
    deploy_cloud_functions
    deploy_cloud_run
    start_dataflow_job
    setup_cloud_build
    display_summary
}

# Run main function
main "$@"
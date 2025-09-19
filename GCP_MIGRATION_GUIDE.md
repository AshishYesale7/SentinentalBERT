# SentinentalBERT GCP Migration Guide

This guide provides comprehensive instructions for migrating the SentinentalBERT platform from a local Docker-based deployment to Google Cloud Platform (GCP) for production-ready, scalable operation.

## 🎯 Migration Overview

### Current Architecture → GCP Architecture

| Component | Current | GCP Migration |
|-----------|---------|---------------|
| **Message Queue** | Kafka + Zookeeper | Cloud Pub/Sub |
| **Data Storage** | PostgreSQL + ElasticSearch + Redis | BigQuery + Cloud Storage + Firestore |
| **Data Processing** | Local Python scripts | Dataflow (Apache Beam) |
| **ML Models** | Local BERT models | Vertex AI + Cloud Storage |
| **API Ingestion** | Rust service | Cloud Functions |
| **Application Services** | Docker containers | Cloud Run |
| **Frontend** | Nginx + React | Firebase Hosting |
| **Monitoring** | Prometheus + Grafana | Cloud Monitoring + Logging |
| **CI/CD** | Docker Compose | Cloud Build |
| **Scheduling** | Cron jobs | Cloud Scheduler |

## 🏗️ Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Social Media  │───▶│  Cloud Functions│───▶│   Cloud Pub/Sub │
│      APIs       │    │   (Ingestion)   │    │  (Raw Messages) │
│                 │    │                 │    │                 │
│ • Twitter API   │    │ • Rate Limiting │    │ • Topic: raw    │
│ • Reddit API    │    │ • Data Cleaning │    │ • Subscription  │
│ • Instagram API │    │ • Error Handling│    │ • Dead Letter   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Cloud Storage  │◀───│    Dataflow     │◀───│   Pub/Sub Sub   │
│   (Raw Data)    │    │   (Processing)  │    │  (Processing)   │
│                 │    │                 │    │                 │
│ • JSON Files    │    │ • Data Cleaning │    │ • Batch Process │
│ • Media Files   │    │ • Deduplication │    │ • Auto Scaling  │
│ • Partitioned   │    │ • Enrichment    │    │ • Error Handling│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    BigQuery     │◀───│   Vertex AI     │◀───│   Cloud Run     │
│   (Analytics)   │    │  (ML Models)    │    │   (NLP Service) │
│                 │    │                 │    │                 │
│ • Social Posts  │    │ • BERT Models   │    │ • Sentiment     │
│ • Sentiment     │    │ • Custom Models │    │ • Behavior      │
│ • Behavior      │    │ • Auto Scaling  │    │ • Influence     │
│ • Influence     │    │ • Model Versions│    │ • API Endpoints │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Looker Studio   │◀───│   Cloud Run     │───▶│    Firestore    │
│  (Dashboards)   │    │ (Backend API)   │    │ (Real-time DB)  │
│                 │    │                 │    │                 │
│ • Charts        │    │ • REST APIs     │    │ • User Sessions │
│ • Reports       │    │ • WebSocket     │    │ • Cache Data    │
│ • Analytics     │    │ • Authentication│    │ • Real-time     │
│ • Alerts        │    │ • Authorization │    │ • Lookups       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │Firebase Hosting │
                       │   (Frontend)    │
                       │                 │
                       │ • React App     │
                       │ • CDN           │
                       │ • SSL/TLS       │
                       │ • Global Scale  │
                       └─────────────────┘
```

## 📋 Prerequisites

### Required Tools
- **Google Cloud SDK** (gcloud CLI)
- **Terraform** (>= 1.0)
- **Docker** (>= 20.10)
- **Node.js** (>= 16) for frontend
- **Python** (>= 3.9) for scripts

### GCP Account Setup
1. Create or select a GCP project
2. Enable billing for the project
3. Install and authenticate gcloud CLI:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### API Keys Required
- **Twitter/X.com API** - Bearer Token (Essential Access - Free)
- **Reddit API** - Client ID and Secret (Free)
- **Instagram Basic Display API** - Access Token (Free)
- **YouTube Data API** - API Key (Free, optional)

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/bot-starter/SentinentalBERT.git
cd SentinentalBERT

# Run the automated deployment script
./deploy-gcp.sh --project-id YOUR_PROJECT_ID --region us-central1 --environment dev

# Follow the prompts and wait for completion
```

### Option 2: Manual Step-by-Step Deployment

Follow the detailed steps in the [Manual Deployment](#manual-deployment) section below.

## 🔧 Manual Deployment

### Step 1: Infrastructure Setup

1. **Deploy Infrastructure with Terraform**
   ```bash
   cd gcp/terraform
   
   # Initialize Terraform
   terraform init
   
   # Create terraform.tfvars
   cat > terraform.tfvars <<EOF
   project_id = "your-gcp-project-id"
   region = "us-central1"
   environment = "dev"
   EOF
   
   # Plan and apply
   terraform plan
   terraform apply
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable \
     compute.googleapis.com \
     container.googleapis.com \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     pubsub.googleapis.com \
     dataflow.googleapis.com \
     bigquery.googleapis.com \
     storage.googleapis.com \
     firestore.googleapis.com \
     aiplatform.googleapis.com \
     cloudfunctions.googleapis.com \
     cloudscheduler.googleapis.com \
     logging.googleapis.com \
     monitoring.googleapis.com \
     secretmanager.googleapis.com \
     iam.googleapis.com \
     firebase.googleapis.com
   ```

### Step 2: Data Storage Setup

1. **Create BigQuery Tables**
   ```bash
   # Replace variables in schema file
   sed "s/\${project_id}/YOUR_PROJECT_ID/g; s/\${environment}/dev/g" gcp/bigquery/schemas.sql > /tmp/schemas.sql
   
   # Execute schema creation
   bq query --use_legacy_sql=false --project_id=YOUR_PROJECT_ID < /tmp/schemas.sql
   ```

2. **Configure Secret Manager**
   ```bash
   # Store API keys (replace with actual values)
   echo "YOUR_TWITTER_BEARER_TOKEN" | gcloud secrets create twitter-bearer-token-dev --data-file=-
   echo "YOUR_REDDIT_CLIENT_ID" | gcloud secrets create reddit-client-id-dev --data-file=-
   echo "YOUR_REDDIT_CLIENT_SECRET" | gcloud secrets create reddit-client-secret-dev --data-file=-
   echo "YOUR_INSTAGRAM_ACCESS_TOKEN" | gcloud secrets create instagram-access-token-dev --data-file=-
   echo "$(openssl rand -base64 32)" | gcloud secrets create jwt-secret-dev --data-file=-
   ```

### Step 3: Build and Deploy Services

1. **Build Docker Images**
   ```bash
   # Configure Docker for GCR
   gcloud auth configure-docker
   
   # Build and push images
   docker build -t gcr.io/YOUR_PROJECT_ID/sentinelbert-nlp:latest ./services/nlp
   docker push gcr.io/YOUR_PROJECT_ID/sentinelbert-nlp:latest
   
   docker build -t gcr.io/YOUR_PROJECT_ID/sentinelbert-backend:latest ./services/backend
   docker push gcr.io/YOUR_PROJECT_ID/sentinelbert-backend:latest
   
   docker build -t gcr.io/YOUR_PROJECT_ID/sentinelbert-ingestion:latest ./services/ingestion
   docker push gcr.io/YOUR_PROJECT_ID/sentinelbert-ingestion:latest
   
   docker build -t gcr.io/YOUR_PROJECT_ID/sentinelbert-frontend:latest ./frontend
   docker push gcr.io/YOUR_PROJECT_ID/sentinelbert-frontend:latest
   ```

2. **Deploy Cloud Functions**
   ```bash
   gcloud functions deploy twitter-ingestion-dev \
     --source=./gcp/cloud-functions/twitter-ingestion \
     --entry-point=twitter_ingestion \
     --runtime=python311 \
     --trigger=http \
     --allow-unauthenticated \
     --region=us-central1 \
     --memory=1GB \
     --timeout=540s \
     --set-env-vars=GCP_PROJECT=YOUR_PROJECT_ID,ENVIRONMENT=dev
   ```

3. **Deploy Cloud Run Services**
   ```bash
   # Deploy NLP Service
   gcloud run deploy sentinelbert-nlp-service \
     --image=gcr.io/YOUR_PROJECT_ID/sentinelbert-nlp:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --memory=8Gi \
     --cpu=4 \
     --max-instances=100 \
     --min-instances=1
   
   # Deploy Backend Service
   gcloud run deploy sentinelbert-backend-service \
     --image=gcr.io/YOUR_PROJECT_ID/sentinelbert-backend:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --memory=4Gi \
     --cpu=2
   
   # Deploy Ingestion Service
   gcloud run deploy sentinelbert-ingestion-service \
     --image=gcr.io/YOUR_PROJECT_ID/sentinelbert-ingestion:latest \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --memory=2Gi \
     --cpu=2
   ```

### Step 4: Start Data Processing Pipeline

1. **Deploy Dataflow Pipeline**
   ```bash
   # Build Dataflow image
   docker build -t gcr.io/YOUR_PROJECT_ID/sentinelbert-dataflow:latest -f gcp/dataflow/Dockerfile gcp/dataflow
   docker push gcr.io/YOUR_PROJECT_ID/sentinelbert-dataflow:latest
   
   # Create Dataflow template
   gcloud dataflow flex-template build \
     gs://YOUR_PROJECT_ID-sentinelbert-cloudbuild-dev/templates/social-media-pipeline \
     --image=gcr.io/YOUR_PROJECT_ID/sentinelbert-dataflow:latest \
     --sdk-language=PYTHON
   
   # Start Dataflow job
   gcloud dataflow flex-template run social-media-pipeline-dev-$(date +%s) \
     --template-file-gcs-location=gs://YOUR_PROJECT_ID-sentinelbert-cloudbuild-dev/templates/social-media-pipeline \
     --region=us-central1 \
     --parameters=input_subscription=projects/YOUR_PROJECT_ID/subscriptions/social-media-raw-sub-dev,output_table=YOUR_PROJECT_ID:sentinelbert_dev.social_posts
   ```

### Step 5: Deploy Frontend

1. **Setup Firebase Hosting**
   ```bash
   cd frontend
   
   # Install Firebase CLI
   npm install -g firebase-tools
   
   # Login to Firebase
   firebase login
   
   # Initialize Firebase project
   firebase init hosting
   
   # Build and deploy
   npm run build
   firebase deploy
   ```

### Step 6: Setup Monitoring and CI/CD

1. **Create Cloud Build Trigger**
   ```bash
   gcloud builds triggers create github \
     --repo-name=SentinentalBERT \
     --repo-owner=bot-starter \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Setup Cloud Scheduler**
   ```bash
   gcloud scheduler jobs create http daily-ingestion-dev \
     --schedule="0 2 * * *" \
     --uri="https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/twitter-ingestion-dev" \
     --http-method=POST \
     --headers="Content-Type=application/json" \
     --message-body='{"query": "climate change -is:retweet lang:en", "max_results": 100}'
   ```

## 📊 Data Flow Architecture

### 1. Data Ingestion Flow
```
Social Media APIs → Cloud Functions → Pub/Sub → Cloud Storage (Raw)
                                   ↓
                              Dataflow Pipeline
                                   ↓
                              BigQuery (Processed)
```

### 2. ML Processing Flow
```
Pub/Sub Messages → Cloud Run (NLP) → Vertex AI Models → BigQuery (Results)
                                   ↓
                              Behavioral Analysis
                                   ↓
                              Influence Scoring
```

### 3. Analytics Flow
```
BigQuery → Looker Studio → Dashboards & Reports
         ↓
    Cloud Run (Backend) → React Frontend → Users
```

## 🔐 Security Configuration

### IAM Roles and Service Accounts

The Terraform configuration creates the following service accounts with appropriate permissions:

- **Ingestion Service**: `sentinelbert-ingestion-dev@PROJECT_ID.iam.gserviceaccount.com`
  - Pub/Sub Publisher
  - Storage Object Admin
  
- **NLP Service**: `sentinelbert-nlp-dev@PROJECT_ID.iam.gserviceaccount.com`
  - Pub/Sub Subscriber
  - Vertex AI User
  - BigQuery Data Editor
  
- **Backend Service**: `sentinelbert-backend-dev@PROJECT_ID.iam.gserviceaccount.com`
  - BigQuery Admin
  - Firestore User
  
- **Dataflow Service**: `sentinelbert-dataflow-dev@PROJECT_ID.iam.gserviceaccount.com`
  - Dataflow Worker
  - BigQuery Admin
  - Storage Object Admin

### API Security

- All Cloud Run services use IAM authentication
- Cloud Functions can be configured for authenticated access
- API keys stored securely in Secret Manager
- Network security through VPC (optional)

## 📈 Scaling and Performance

### Auto Scaling Configuration

- **Cloud Run**: Auto-scales from 0-100 instances based on traffic
- **Dataflow**: Auto-scales workers based on message backlog
- **Vertex AI**: Scales model endpoints automatically
- **Cloud Functions**: Scales to handle concurrent requests

### Performance Optimizations

- **Caching**: Redis-compatible Firestore for real-time data
- **CDN**: Firebase Hosting provides global CDN
- **Compression**: GZip compression enabled on all services
- **Connection Pooling**: Database connections optimized
- **Batch Processing**: Efficient batch processing in Dataflow

## 💰 Cost Optimization

### Cost Management Features

- **Budget Alerts**: Configured in Terraform
- **Resource Limits**: CPU and memory limits set
- **Auto Scaling**: Scale to zero when not in use
- **Data Lifecycle**: Automatic data deletion policies
- **Preemptible Instances**: Used where appropriate

### Estimated Monthly Costs (Development Environment)

| Service | Estimated Cost |
|---------|----------------|
| Cloud Run (3 services) | $50-100 |
| Cloud Functions | $10-20 |
| BigQuery | $20-50 |
| Cloud Storage | $10-30 |
| Pub/Sub | $5-15 |
| Dataflow | $100-200 |
| Vertex AI | $50-150 |
| **Total** | **$245-565** |

*Costs vary based on usage patterns and data volume*

## 🔍 Monitoring and Observability

### Built-in Monitoring

- **Cloud Logging**: Centralized log aggregation
- **Cloud Monitoring**: Metrics and alerting
- **Error Reporting**: Automatic error detection
- **Cloud Trace**: Distributed tracing
- **Cloud Profiler**: Performance profiling

### Custom Metrics

- Request counts and latencies
- Model inference times
- Data processing throughput
- Error rates and types
- Business metrics (sentiment trends, etc.)

### Alerting Policies

- High error rates
- Service downtime
- Budget thresholds
- Data quality issues
- Performance degradation

## 🧪 Testing and Validation

### Testing Strategy

1. **Unit Tests**: Individual service testing
2. **Integration Tests**: Service-to-service communication
3. **End-to-End Tests**: Complete pipeline testing
4. **Load Tests**: Performance under load
5. **Chaos Engineering**: Failure scenario testing

### Validation Checklist

- [ ] All services deployed successfully
- [ ] Pub/Sub messages flowing correctly
- [ ] BigQuery tables populated
- [ ] ML models responding
- [ ] Frontend accessible
- [ ] Monitoring dashboards working
- [ ] Alerts configured
- [ ] API keys working
- [ ] Data quality checks passing

## 🚨 Troubleshooting

### Common Issues

1. **Service Account Permissions**
   ```bash
   # Check service account permissions
   gcloud projects get-iam-policy YOUR_PROJECT_ID
   
   # Add missing permissions
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/REQUIRED_ROLE"
   ```

2. **API Quota Exceeded**
   ```bash
   # Check quota usage
   gcloud compute project-info describe --project=YOUR_PROJECT_ID
   
   # Request quota increase through GCP Console
   ```

3. **Dataflow Job Failures**
   ```bash
   # Check Dataflow job logs
   gcloud dataflow jobs list --region=us-central1
   gcloud dataflow jobs show JOB_ID --region=us-central1
   ```

4. **Cloud Run Cold Starts**
   - Set minimum instances to 1 for critical services
   - Optimize container startup time
   - Use health checks appropriately

### Debug Commands

```bash
# Check service status
gcloud run services list --region=us-central1

# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Test Cloud Function
curl -X POST "https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/twitter-ingestion-dev" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_results": 10}'

# Check Pub/Sub messages
gcloud pubsub topics list
gcloud pubsub subscriptions list

# Query BigQuery
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`YOUR_PROJECT_ID.sentinelbert_dev.social_posts\`"
```

## 📚 Additional Resources

### Documentation Links

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Apache Beam Documentation](https://beam.apache.org/documentation/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

### Support Channels

- **GitHub Issues**: For code-related issues
- **GCP Support**: For infrastructure issues
- **Community Forums**: For general questions
- **Documentation**: For detailed guides

## 🔄 Migration Rollback Plan

If you need to rollback to the original Docker-based deployment:

1. **Stop GCP Services**
   ```bash
   # Stop Cloud Run services
   gcloud run services delete sentinelbert-nlp-service --region=us-central1
   gcloud run services delete sentinelbert-backend-service --region=us-central1
   gcloud run services delete sentinelbert-ingestion-service --region=us-central1
   
   # Cancel Dataflow jobs
   gcloud dataflow jobs cancel JOB_ID --region=us-central1
   ```

2. **Export Data from BigQuery**
   ```bash
   # Export data to Cloud Storage
   bq extract --destination_format=NEWLINE_DELIMITED_JSON \
     YOUR_PROJECT_ID:sentinelbert_dev.social_posts \
     gs://YOUR_BUCKET/export/social_posts_*.json
   ```

3. **Restart Local Environment**
   ```bash
   # Return to original directory
   cd /path/to/original/SentinentalBERT
   
   # Start local services
   docker-compose up -d
   ```

## 🎯 Next Steps

After successful deployment:

1. **Configure Looker Studio Dashboards**
2. **Set up additional monitoring alerts**
3. **Implement data quality checks**
4. **Configure backup and disaster recovery**
5. **Set up staging and production environments**
6. **Implement advanced security features**
7. **Optimize costs based on usage patterns**

---

**🎉 Congratulations!** You have successfully migrated SentinentalBERT to Google Cloud Platform. Your system is now production-ready, scalable, and leverages the full power of GCP's managed services.

For questions or support, please refer to the troubleshooting section or create an issue in the GitHub repository.
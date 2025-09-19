# Cloud Run Setup Guide for SentinentalBERT

<div align="center">

![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Serverless-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**Serverless Container Deployment with Auto-scaling and Cost Optimization**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [🐳 Container Configuration](#-container-configuration)
- [⚡ Service Deployment](#-service-deployment)
- [📊 Auto-scaling Configuration](#-auto-scaling-configuration)
- [🔒 Security & IAM](#-security--iam)
- [🌐 Custom Domains & SSL](#-custom-domains--ssl)
- [📈 Monitoring & Logging](#-monitoring--logging)
- [💰 Cost Optimization](#-cost-optimization)
- [🧪 Testing & Validation](#-testing--validation)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide configures Google Cloud Run for SentinentalBERT's serverless container deployment. Your configuration supports high-throughput processing with cost-effective auto-scaling.

### 🌟 Your Cloud Run Configuration

Based on your specifications:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| **Region** | europe-west1 (Belgium) | GPU-supported tier 1 region |
| **CPU** | 2 vCPU per instance | High-performance processing |
| **Memory** | 1 GiB per instance | Optimized for ML workloads |
| **Requests/Month** | 10 million | High-volume API serving |
| **Execution Time** | 400ms per request | Fast response times |
| **Concurrency** | 20 requests per instance | Efficient resource utilization |
| **Min Instances** | 0 | Cost optimization (scale to zero) |
| **Max Instances** | 100 | Handle traffic spikes |
| **Traffic Pattern** | Daily peak/trough (12h active) | Optimized billing |
| **CUD** | 1-year commitment (17% discount) | Cost savings |

### 💰 Cost Benefits

- **Pay-per-use**: Only charged when processing requests
- **Auto-scaling**: Scales to zero during idle periods
- **Committed Use Discount**: 17% savings with 1-year commitment
- **Regional optimization**: europe-west1 for optimal performance/cost

### ⏱️ Estimated Setup Time: 25-30 minutes

---

## 🔧 Prerequisites

### ✅ Required Setup

1. **GCP Project**: With Cloud Run API enabled
2. **Docker**: Installed locally for building images
3. **gcloud CLI**: Authenticated and configured
4. **Container Registry**: Access to push images
5. **Service Account**: With appropriate permissions

### 📦 Install Required Tools

```bash
# Install Docker (if not already installed)
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# macOS
brew install docker

# Windows
# Download from https://docs.docker.com/desktop/windows/install/

# Install Cloud Run components
gcloud components install cloud-run-proxy
gcloud components update
```

### 🔑 Enable APIs and Authentication

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Configure Docker for GCP
gcloud auth configure-docker

# Set default region
gcloud config set run/region europe-west1
```

---

## 🚀 Step-by-Step Setup

### Step 1: Project Structure Setup

```bash
# Navigate to project root
cd /path/to/SentinentalBERT

# Create Cloud Run specific directories
mkdir -p gcp/cloud-run/{nlp-service,backend-service,frontend-service}
mkdir -p gcp/cloud-run/configs
mkdir -p gcp/cloud-run/scripts
```

### Step 2: Environment Configuration

```bash
# Create Cloud Run environment file
cat > gcp/cloud-run/.env.cloudrun << 'EOF'
# Cloud Run Configuration for SentinentalBERT
PROJECT_ID=your-sentinelbert-project
REGION=europe-west1
SERVICE_ACCOUNT=cloud-run-service@your-project.iam.gserviceaccount.com

# Resource Configuration
CPU_LIMIT=2
MEMORY_LIMIT=1Gi
MAX_INSTANCES=100
MIN_INSTANCES=0
CONCURRENCY=20
TIMEOUT=300

# Traffic Configuration
ALLOW_UNAUTHENTICATED=false
INGRESS=all
EXECUTION_ENVIRONMENT=gen2

# Environment Variables
ENVIRONMENT=production
LOG_LEVEL=INFO
ENABLE_METRICS=true
EOF
```

---

## 🐳 Container Configuration

### Step 3: Create Optimized Dockerfiles

#### 3.1 NLP Service Dockerfile

```dockerfile
# gcp/cloud-run/nlp-service/Dockerfile
# Multi-stage build for optimized NLP service container

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY services/nlp/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY services/nlp/ .
COPY shared/ ./shared/

# Set ownership and permissions
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Set environment variables for Cloud Run
ENV PORT=8080
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Start command optimized for Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
```

#### 3.2 Backend Service Dockerfile

```dockerfile
# gcp/cloud-run/backend-service/Dockerfile
# Optimized backend service container

FROM openjdk:17-jdk-slim as builder

# Install Maven
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Maven files
COPY services/backend/pom.xml .
COPY services/backend/src ./src

# Build application
RUN mvn clean package -DskipTests

# Production stage
FROM openjdk:17-jre-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy JAR from builder
COPY --from=builder /app/target/*.jar app.jar

# Set ownership
RUN chown appuser:appuser app.jar
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# Expose port
EXPOSE 8080

# JVM optimization for Cloud Run
ENV JAVA_OPTS="-Xmx768m -Xms256m -XX:+UseG1GC -XX:+UseContainerSupport"

# Start command
CMD exec java $JAVA_OPTS -jar app.jar
```

#### 3.3 Frontend Service Dockerfile

```dockerfile
# gcp/cloud-run/frontend-service/Dockerfile
# Optimized React frontend with Nginx

# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY frontend/ .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx configuration
COPY gcp/cloud-run/frontend-service/nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001

# Set permissions
RUN chown -R appuser:appuser /usr/share/nginx/html && \
    chown -R appuser:appuser /var/cache/nginx && \
    chown -R appuser:appuser /var/log/nginx && \
    chown -R appuser:appuser /etc/nginx/conf.d

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Step 4: Create Nginx Configuration

```nginx
# gcp/cloud-run/frontend-service/nginx.conf
# Optimized Nginx configuration for Cloud Run

user appuser;
worker_processes auto;
pid /tmp/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    server {
        listen 8080;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Static assets with caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            try_files $uri =404;
        }

        # API proxy to backend
        location /api/ {
            proxy_pass http://sentinelbert-backend-service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # React app routing
        location / {
            try_files $uri $uri/ /index.html;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }

        # Error pages
        error_page 404 /index.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

---

## ⚡ Service Deployment

### Step 5: Build and Push Container Images

```bash
# Create build script
cat > gcp/cloud-run/scripts/build-and-push.sh << 'EOF'
#!/bin/bash

# Build and push script for Cloud Run services
set -e

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="europe-west1"

echo "🚀 Building and pushing Cloud Run services for project: $PROJECT_ID"

# Configure Docker for GCP
gcloud auth configure-docker

# Build NLP Service
echo "📦 Building NLP Service..."
docker build -t gcr.io/$PROJECT_ID/sentinelbert-nlp:latest \
    -f gcp/cloud-run/nlp-service/Dockerfile .

echo "📤 Pushing NLP Service..."
docker push gcr.io/$PROJECT_ID/sentinelbert-nlp:latest

# Build Backend Service
echo "📦 Building Backend Service..."
docker build -t gcr.io/$PROJECT_ID/sentinelbert-backend:latest \
    -f gcp/cloud-run/backend-service/Dockerfile .

echo "📤 Pushing Backend Service..."
docker push gcr.io/$PROJECT_ID/sentinelbert-backend:latest

# Build Frontend Service
echo "📦 Building Frontend Service..."
docker build -t gcr.io/$PROJECT_ID/sentinelbert-frontend:latest \
    -f gcp/cloud-run/frontend-service/Dockerfile .

echo "📤 Pushing Frontend Service..."
docker push gcr.io/$PROJECT_ID/sentinelbert-frontend:latest

echo "✅ All services built and pushed successfully!"
EOF

chmod +x gcp/cloud-run/scripts/build-and-push.sh

# Run the build script
./gcp/cloud-run/scripts/build-and-push.sh your-sentinelbert-project
```

### Step 6: Deploy Services to Cloud Run

#### 6.1 Deploy NLP Service

```bash
# Deploy NLP service with your specifications
gcloud run deploy sentinelbert-nlp \
    --image=gcr.io/$PROJECT_ID/sentinelbert-nlp:latest \
    --region=europe-west1 \
    --platform=managed \
    --cpu=2 \
    --memory=1Gi \
    --min-instances=0 \
    --max-instances=100 \
    --concurrency=20 \
    --timeout=300 \
    --no-allow-unauthenticated \
    --service-account=cloud-run-service@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars="ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID" \
    --execution-environment=gen2 \
    --ingress=all \
    --port=8080
```

#### 6.2 Deploy Backend Service

```bash
# Deploy backend service
gcloud run deploy sentinelbert-backend \
    --image=gcr.io/$PROJECT_ID/sentinelbert-backend:latest \
    --region=europe-west1 \
    --platform=managed \
    --cpu=2 \
    --memory=1Gi \
    --min-instances=0 \
    --max-instances=100 \
    --concurrency=20 \
    --timeout=300 \
    --no-allow-unauthenticated \
    --service-account=cloud-run-service@$PROJECT_ID.iam.gserviceaccount.com \
    --set-env-vars="ENVIRONMENT=production,PROJECT_ID=$PROJECT_ID" \
    --execution-environment=gen2 \
    --ingress=all \
    --port=8080
```

#### 6.3 Deploy Frontend Service

```bash
# Deploy frontend service
gcloud run deploy sentinelbert-frontend \
    --image=gcr.io/$PROJECT_ID/sentinelbert-frontend:latest \
    --region=europe-west1 \
    --platform=managed \
    --cpu=1 \
    --memory=512Mi \
    --min-instances=0 \
    --max-instances=50 \
    --concurrency=80 \
    --timeout=300 \
    --allow-unauthenticated \
    --set-env-vars="ENVIRONMENT=production" \
    --execution-environment=gen2 \
    --ingress=all \
    --port=8080
```

### Step 7: Configure Service Communication

```bash
# Create service-to-service communication script
cat > gcp/cloud-run/scripts/configure-services.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="europe-west1"

echo "🔗 Configuring service-to-service communication..."

# Get service URLs
NLP_URL=$(gcloud run services describe sentinelbert-nlp \
    --region=$REGION --format="value(status.url)")

BACKEND_URL=$(gcloud run services describe sentinelbert-backend \
    --region=$REGION --format="value(status.url)")

FRONTEND_URL=$(gcloud run services describe sentinelbert-frontend \
    --region=$REGION --format="value(status.url)")

echo "Service URLs:"
echo "  NLP Service: $NLP_URL"
echo "  Backend Service: $BACKEND_URL"
echo "  Frontend Service: $FRONTEND_URL"

# Update backend service with NLP service URL
gcloud run services update sentinelbert-backend \
    --region=$REGION \
    --set-env-vars="NLP_SERVICE_URL=$NLP_URL"

# Update frontend service with backend URL
gcloud run services update sentinelbert-frontend \
    --region=$REGION \
    --set-env-vars="BACKEND_SERVICE_URL=$BACKEND_URL"

echo "✅ Service communication configured!"
EOF

chmod +x gcp/cloud-run/scripts/configure-services.sh
./gcp/cloud-run/scripts/configure-services.sh your-sentinelbert-project
```

---

## 📊 Auto-scaling Configuration

### Step 8: Configure Advanced Auto-scaling

```yaml
# gcp/cloud-run/configs/autoscaling.yaml
# Advanced auto-scaling configuration

apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: sentinelbert-nlp
  annotations:
    # Auto-scaling annotations
    autoscaling.knative.dev/minScale: "0"
    autoscaling.knative.dev/maxScale: "100"
    autoscaling.knative.dev/target: "70"  # Target 70% CPU utilization
    
    # Traffic-based scaling
    run.googleapis.com/cpu-throttling: "false"
    run.googleapis.com/execution-environment: "gen2"
    
    # Custom metrics scaling
    autoscaling.knative.dev/metric: "concurrency"
    autoscaling.knative.dev/target-utilization-percentage: "70"
    
    # Scaling behavior
    autoscaling.knative.dev/window: "60s"
    autoscaling.knative.dev/scale-down-delay: "30s"
    autoscaling.knative.dev/stable-window: "60s"

spec:
  template:
    metadata:
      annotations:
        # Resource allocation
        run.googleapis.com/cpu: "2000m"
        run.googleapis.com/memory: "1Gi"
        
        # Concurrency settings
        run.googleapis.com/max-instances: "100"
        run.googleapis.com/min-instances: "0"
        
        # Startup optimization
        run.googleapis.com/startup-cpu-boost: "true"
        
    spec:
      containerConcurrency: 20
      timeoutSeconds: 300
      
      containers:
      - image: gcr.io/PROJECT_ID/sentinelbert-nlp:latest
        ports:
        - containerPort: 8080
        
        resources:
          limits:
            cpu: "2000m"
            memory: "1Gi"
          requests:
            cpu: "1000m"
            memory: "512Mi"
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

### Step 9: Apply Auto-scaling Configuration

```bash
# Apply auto-scaling configuration
cat > gcp/cloud-run/scripts/apply-autoscaling.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="europe-west1"

echo "⚡ Applying auto-scaling configuration..."

# Update NLP service with advanced scaling
gcloud run services update sentinelbert-nlp \
    --region=$REGION \
    --min-instances=0 \
    --max-instances=100 \
    --concurrency=20 \
    --cpu=2 \
    --memory=1Gi \
    --timeout=300 \
    --no-cpu-throttling \
    --execution-environment=gen2

# Update backend service
gcloud run services update sentinelbert-backend \
    --region=$REGION \
    --min-instances=0 \
    --max-instances=100 \
    --concurrency=20 \
    --cpu=2 \
    --memory=1Gi \
    --timeout=300 \
    --no-cpu-throttling \
    --execution-environment=gen2

# Update frontend service (lighter configuration)
gcloud run services update sentinelbert-frontend \
    --region=$REGION \
    --min-instances=0 \
    --max-instances=50 \
    --concurrency=80 \
    --cpu=1 \
    --memory=512Mi \
    --timeout=300

echo "✅ Auto-scaling configuration applied!"
EOF

chmod +x gcp/cloud-run/scripts/apply-autoscaling.sh
./gcp/cloud-run/scripts/apply-autoscaling.sh your-sentinelbert-project
```

---

## 🔒 Security & IAM

### Step 10: Configure Security and IAM

```bash
# Create security configuration script
cat > gcp/cloud-run/scripts/configure-security.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="europe-west1"

echo "🔒 Configuring Cloud Run security..."

# Create Cloud Run service account if not exists
gcloud iam service-accounts create cloud-run-service \
    --display-name="Cloud Run Service Account" \
    --description="Service account for Cloud Run services" || true

SA_EMAIL="cloud-run-service@$PROJECT_ID.iam.gserviceaccount.com"

# Assign necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.invoker"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

# Configure service-to-service authentication
echo "🔐 Configuring service-to-service authentication..."

# Allow backend to invoke NLP service
gcloud run services add-iam-policy-binding sentinelbert-nlp \
    --region=$REGION \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.invoker"

# Allow frontend to invoke backend service
gcloud run services add-iam-policy-binding sentinelbert-backend \
    --region=$REGION \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.invoker"

echo "✅ Security configuration completed!"
EOF

chmod +x gcp/cloud-run/scripts/configure-security.sh
./gcp/cloud-run/scripts/configure-security.sh your-sentinelbert-project
```

---

## 🌐 Custom Domains & SSL

### Step 11: Configure Custom Domain (Optional)

```bash
# Configure custom domain script
cat > gcp/cloud-run/scripts/configure-domain.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
DOMAIN=${2:-"api.sentinelbert.com"}
REGION="europe-west1"

echo "🌐 Configuring custom domain: $DOMAIN"

# Map domain to Cloud Run service
gcloud run domain-mappings create \
    --service=sentinelbert-backend \
    --domain=$DOMAIN \
    --region=$REGION

# Get DNS records to configure
echo "📋 Configure these DNS records in your domain provider:"
gcloud run domain-mappings describe $DOMAIN \
    --region=$REGION \
    --format="value(status.resourceRecords[].name,status.resourceRecords[].rrdata)"

echo "✅ Domain mapping created. Configure DNS records as shown above."
EOF

chmod +x gcp/cloud-run/scripts/configure-domain.sh
# ./gcp/cloud-run/scripts/configure-domain.sh your-sentinelbert-project api.sentinelbert.com
```

---

## 📈 Monitoring & Logging

### Step 12: Set Up Monitoring

```python
# gcp/cloud-run/monitoring/cloud_run_monitor.py
"""
Cloud Run monitoring and metrics collection
Tracks performance, costs, and scaling behavior
"""

from google.cloud import monitoring_v3
from google.cloud import logging
import time
from typing import Dict, Any

class CloudRunMonitor:
    """Monitor Cloud Run services"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.logging_client = logging.Client()
        self.project_name = f"projects/{project_id}"
    
    def get_service_metrics(self, service_name: str, region: str = "europe-west1") -> Dict[str, Any]:
        """Get metrics for a Cloud Run service"""
        
        # Define time range (last hour)
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": seconds - 3600, "nanos": nanos}
        })
        
        # Request metrics
        request = monitoring_v3.ListTimeSeriesRequest(
            name=self.project_name,
            filter=f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"',
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        results = self.monitoring_client.list_time_series(request=request)
        
        metrics = {
            "request_count": 0,
            "request_latency": 0,
            "instance_count": 0,
            "cpu_utilization": 0,
            "memory_utilization": 0,
            "error_rate": 0
        }
        
        for result in results:
            metric_type = result.metric.type
            if "request_count" in metric_type:
                metrics["request_count"] = sum(point.value.int64_value for point in result.points)
            elif "request_latencies" in metric_type:
                metrics["request_latency"] = sum(point.value.double_value for point in result.points) / len(result.points)
            # Add more metric processing as needed
        
        return metrics
    
    def create_alert_policy(self, service_name: str):
        """Create alert policy for Cloud Run service"""
        
        alert_policy = monitoring_v3.AlertPolicy(
            display_name=f"Cloud Run {service_name} High Error Rate",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content=f"Alert when {service_name} error rate exceeds 5%"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="High error rate",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter=f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=0.05,
                        duration={"seconds": 300}
                    )
                )
            ]
        )
        
        created_policy = self.monitoring_client.create_alert_policy(
            name=self.project_name,
            alert_policy=alert_policy
        )
        
        return created_policy

# Usage example
if __name__ == "__main__":
    monitor = CloudRunMonitor("your-sentinelbert-project")
    
    # Get metrics for NLP service
    nlp_metrics = monitor.get_service_metrics("sentinelbert-nlp")
    print(f"NLP Service Metrics: {nlp_metrics}")
    
    # Create alert policy
    alert_policy = monitor.create_alert_policy("sentinelbert-nlp")
    print(f"Alert policy created: {alert_policy.name}")
```

### Step 13: Configure Logging

```bash
# Create logging configuration
cat > gcp/cloud-run/configs/logging.yaml << 'EOF'
# Cloud Run logging configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: logging-config
data:
  log_level: "INFO"
  structured_logging: "true"
  log_format: "json"
  
  # Log routing
  application_logs: "projects/PROJECT_ID/logs/sentinelbert-application"
  access_logs: "projects/PROJECT_ID/logs/sentinelbert-access"
  error_logs: "projects/PROJECT_ID/logs/sentinelbert-errors"
  
  # Log retention
  retention_days: "30"
  
  # Export configuration
  export_to_bigquery: "true"
  bigquery_dataset: "sentinelbert_logs"
EOF
```

---

## 💰 Cost Optimization

### Step 14: Implement Cost Optimization

```python
# gcp/cloud-run/optimization/cost_optimizer.py
"""
Cost optimization for Cloud Run services
Implements intelligent scaling and resource management
"""

import time
from typing import Dict, List
from google.cloud import run_v2
from google.cloud import monitoring_v3

class CloudRunCostOptimizer:
    """Optimize Cloud Run costs based on usage patterns"""
    
    def __init__(self, project_id: str, region: str = "europe-west1"):
        self.project_id = project_id
        self.region = region
        self.run_client = run_v2.ServicesClient()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
    
    def analyze_usage_patterns(self, service_name: str, days: int = 7) -> Dict:
        """Analyze service usage patterns over time"""
        
        # Get historical metrics
        metrics = self._get_historical_metrics(service_name, days)
        
        # Analyze patterns
        patterns = {
            "peak_hours": self._identify_peak_hours(metrics),
            "low_usage_periods": self._identify_low_usage_periods(metrics),
            "average_concurrency": self._calculate_average_concurrency(metrics),
            "scaling_efficiency": self._calculate_scaling_efficiency(metrics)
        }
        
        return patterns
    
    def optimize_service_configuration(self, service_name: str) -> Dict:
        """Optimize service configuration based on usage patterns"""
        
        patterns = self.analyze_usage_patterns(service_name)
        
        # Calculate optimal configuration
        optimal_config = {
            "min_instances": 0,  # Always scale to zero for cost savings
            "max_instances": min(100, patterns["average_concurrency"] * 2),
            "cpu": self._optimize_cpu_allocation(patterns),
            "memory": self._optimize_memory_allocation(patterns),
            "concurrency": self._optimize_concurrency(patterns)
        }
        
        return optimal_config
    
    def implement_scheduled_scaling(self, service_name: str):
        """Implement scheduled scaling based on traffic patterns"""
        
        patterns = self.analyze_usage_patterns(service_name)
        
        # Create scaling schedule
        scaling_schedule = []
        
        for hour in range(24):
            if hour in patterns["peak_hours"]:
                # Pre-warm instances during peak hours
                scaling_schedule.append({
                    "hour": hour,
                    "min_instances": 2,
                    "max_instances": 100
                })
            elif hour in patterns["low_usage_periods"]:
                # Aggressive scaling down during low usage
                scaling_schedule.append({
                    "hour": hour,
                    "min_instances": 0,
                    "max_instances": 10
                })
            else:
                # Normal scaling
                scaling_schedule.append({
                    "hour": hour,
                    "min_instances": 0,
                    "max_instances": 50
                })
        
        return scaling_schedule
    
    def _get_historical_metrics(self, service_name: str, days: int) -> List:
        """Get historical metrics for analysis"""
        # Implementation would fetch actual metrics
        return []
    
    def _identify_peak_hours(self, metrics: List) -> List[int]:
        """Identify peak usage hours"""
        # Analysis implementation
        return [9, 10, 11, 14, 15, 16]  # Example peak hours
    
    def _identify_low_usage_periods(self, metrics: List) -> List[int]:
        """Identify low usage periods"""
        # Analysis implementation
        return [0, 1, 2, 3, 4, 5, 22, 23]  # Example low usage hours
    
    def _calculate_average_concurrency(self, metrics: List) -> float:
        """Calculate average concurrency"""
        # Analysis implementation
        return 15.0  # Example average
    
    def _calculate_scaling_efficiency(self, metrics: List) -> float:
        """Calculate scaling efficiency"""
        # Analysis implementation
        return 0.85  # Example efficiency
    
    def _optimize_cpu_allocation(self, patterns: Dict) -> str:
        """Optimize CPU allocation"""
        if patterns["average_concurrency"] > 15:
            return "2000m"  # 2 vCPU
        else:
            return "1000m"  # 1 vCPU
    
    def _optimize_memory_allocation(self, patterns: Dict) -> str:
        """Optimize memory allocation"""
        if patterns["average_concurrency"] > 15:
            return "1Gi"
        else:
            return "512Mi"
    
    def _optimize_concurrency(self, patterns: Dict) -> int:
        """Optimize concurrency setting"""
        return min(20, int(patterns["average_concurrency"] * 1.5))

# Usage example
if __name__ == "__main__":
    optimizer = CloudRunCostOptimizer("your-sentinelbert-project")
    
    # Analyze and optimize NLP service
    optimal_config = optimizer.optimize_service_configuration("sentinelbert-nlp")
    print(f"Optimal configuration: {optimal_config}")
    
    # Get scaling schedule
    schedule = optimizer.implement_scheduled_scaling("sentinelbert-nlp")
    print(f"Scaling schedule: {schedule}")
```

---

## 🧪 Testing & Validation

### Step 15: Create Test Suite

```bash
# Create comprehensive test script
cat > gcp/cloud-run/scripts/test-services.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="europe-west1"

echo "🧪 Testing Cloud Run services..."

# Get service URLs
NLP_URL=$(gcloud run services describe sentinelbert-nlp \
    --region=$REGION --format="value(status.url)")

BACKEND_URL=$(gcloud run services describe sentinelbert-backend \
    --region=$REGION --format="value(status.url)")

FRONTEND_URL=$(gcloud run services describe sentinelbert-frontend \
    --region=$REGION --format="value(status.url)")

# Test health endpoints
echo "🔍 Testing health endpoints..."

# Test NLP service health
echo "Testing NLP service health..."
curl -f "$NLP_URL/health" || echo "❌ NLP health check failed"

# Test backend service health
echo "Testing backend service health..."
curl -f "$BACKEND_URL/actuator/health" || echo "❌ Backend health check failed"

# Test frontend service health
echo "Testing frontend service health..."
curl -f "$FRONTEND_URL/health" || echo "❌ Frontend health check failed"

# Test API endpoints
echo "🔍 Testing API endpoints..."

# Test sentiment analysis endpoint
echo "Testing sentiment analysis..."
curl -X POST "$BACKEND_URL/api/v1/analyze/sentiment" \
    -H "Content-Type: application/json" \
    -d '{"texts": ["I love this product!"]}' || echo "❌ Sentiment analysis failed"

# Load testing
echo "🚀 Running load test..."
for i in {1..10}; do
    curl -s "$BACKEND_URL/api/v1/health" > /dev/null &
done
wait

echo "✅ All tests completed!"
EOF

chmod +x gcp/cloud-run/scripts/test-services.sh
./gcp/cloud-run/scripts/test-services.sh your-sentinelbert-project
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Service Not Starting

**Error**: `Service failed to start`

**Solution**:
```bash
# Check service logs
gcloud run services logs read sentinelbert-nlp --region=europe-west1

# Check container health
gcloud run services describe sentinelbert-nlp --region=europe-west1

# Verify container image
docker run --rm gcr.io/$PROJECT_ID/sentinelbert-nlp:latest
```

#### Issue 2: High Cold Start Times

**Problem**: Slow initial response times

**Solution**:
```bash
# Enable CPU boost
gcloud run services update sentinelbert-nlp \
    --region=europe-west1 \
    --cpu-boost

# Optimize container image
# - Use multi-stage builds
# - Minimize dependencies
# - Use smaller base images
```

#### Issue 3: Memory Issues

**Error**: `Container killed due to memory limit`

**Solution**:
```bash
# Increase memory allocation
gcloud run services update sentinelbert-nlp \
    --region=europe-west1 \
    --memory=2Gi

# Optimize application memory usage
# - Implement connection pooling
# - Use streaming for large responses
# - Add memory monitoring
```

#### Issue 4: Authentication Errors

**Error**: `Permission denied` or `Unauthenticated`

**Solution**:
```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID

# Update service account
gcloud run services update sentinelbert-nlp \
    --region=europe-west1 \
    --service-account=cloud-run-service@$PROJECT_ID.iam.gserviceaccount.com

# Test authentication
gcloud auth print-access-token
```

---

## 📞 Important Links & References

### 🔗 Essential Links

- **Cloud Run Console**: https://console.cloud.google.com/run
- **Container Registry**: https://console.cloud.google.com/gcr
- **Cloud Build**: https://console.cloud.google.com/cloud-build
- **Monitoring**: https://console.cloud.google.com/monitoring

### 📚 Documentation References

- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Container Best Practices**: https://cloud.google.com/architecture/best-practices-for-building-containers
- **Auto-scaling**: https://cloud.google.com/run/docs/configuring/concurrency
- **Security**: https://cloud.google.com/run/docs/securing/service-identity
- **Monitoring**: https://cloud.google.com/run/docs/monitoring
- **Pricing**: https://cloud.google.com/run/pricing

### 🛠️ Tools & Resources

- **Docker**: https://docs.docker.com/
- **gcloud CLI**: https://cloud.google.com/sdk/gcloud/reference/run
- **Cloud Run Button**: https://github.com/GoogleCloudPlatform/cloud-run-button
- **Samples**: https://github.com/GoogleCloudPlatform/cloud-run-samples

---

<div align="center">

**Next Steps**: Continue with [BigQuery Setup](./05-bigquery-setup.md) to configure your analytics infrastructure.

*Your Cloud Run services are now deployed with optimal auto-scaling and cost management for 10M requests/month.*

</div>
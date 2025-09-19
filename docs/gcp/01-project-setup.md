# GCP Project Setup Guide for SentinentalBERT

<div align="center">

![GCP Project](https://img.shields.io/badge/GCP%20Project-Setup-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Billing](https://img.shields.io/badge/Billing-Enabled-green?style=for-the-badge&logo=google-pay&logoColor=white)

**Complete GCP Project Configuration for Production Deployment**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [💰 Billing Configuration](#-billing-configuration)
- [🔑 API Enablement](#-api-enablement)
- [🛡️ IAM Setup](#️-iam-setup)
- [📊 Quotas & Limits](#-quotas--limits)
- [🔍 Verification](#-verification)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide walks you through setting up a Google Cloud Platform project specifically configured for SentinentalBERT deployment. The setup is optimized for your $5,000 credit budget and includes all necessary services and configurations.

### 🌟 What You'll Set Up

- **GCP Project**: With proper naming and organization
- **Billing Account**: Linked with $5,000 credits and budget alerts
- **APIs**: All required services enabled
- **IAM**: Service accounts and permissions
- **Quotas**: Optimized for your workload
- **Security**: Basic security configurations

### ⏱️ Estimated Time: 15-20 minutes

---

## 🔧 Prerequisites

### ✅ Required Items

1. **Google Account**: Personal or business Google account
2. **GCP Credits**: $5,000 in GCP credits available
3. **gcloud CLI**: Installed on your local machine
4. **Admin Access**: Ability to create projects and manage billing

### 📥 Install gcloud CLI

If you haven't installed the gcloud CLI yet:

**Windows:**
```powershell
# Download and run the installer
# https://cloud.google.com/sdk/docs/install-windows
```

**macOS:**
```bash
# Using Homebrew
brew install --cask google-cloud-sdk

# Or download installer
# https://cloud.google.com/sdk/docs/install-mac
```

**Linux:**
```bash
# Ubuntu/Debian
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Or use package manager
sudo apt-get install google-cloud-cli
```

### 🔐 Authentication

```bash
# Authenticate with your Google account
gcloud auth login

# Set up application default credentials
gcloud auth application-default login
```

---

## 🚀 Step-by-Step Setup

### Step 1: Create GCP Project

#### 1.1 Choose Project ID

Your project ID should be unique and descriptive:

```bash
# Recommended naming convention
PROJECT_ID="sentinelbert-prod-$(date +%Y%m%d)"
# Example: sentinelbert-prod-20240115

# Alternative naming options
PROJECT_ID="sentinelbert-production"
PROJECT_ID="your-company-sentinelbert"
```

#### 1.2 Create Project via gcloud CLI

```bash
# Create the project
gcloud projects create $PROJECT_ID \
    --name="SentinentalBERT Production" \
    --labels="environment=production,team=ml-engineering,project=sentinelbert"

# Verify project creation
gcloud projects describe $PROJECT_ID
```

#### 1.3 Create Project via Console (Alternative)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Fill in project details:
   - **Project name**: `SentinentalBERT Production`
   - **Project ID**: `sentinelbert-prod-20240115`
   - **Organization**: Select your organization (if applicable)
4. Click **Create**

### Step 2: Set Default Project

```bash
# Set as default project
gcloud config set project $PROJECT_ID

# Verify current project
gcloud config get-value project
```

### Step 3: Enable Billing

#### 3.1 Link Billing Account via CLI

```bash
# List available billing accounts
gcloud billing accounts list

# Link billing account to project
BILLING_ACCOUNT_ID="ABCDEF-123456-GHIJKL"  # Replace with your billing account ID
gcloud billing projects link $PROJECT_ID \
    --billing-account=$BILLING_ACCOUNT_ID

# Verify billing is enabled
gcloud billing projects describe $PROJECT_ID
```

#### 3.2 Link Billing Account via Console

1. Go to [Billing Console](https://console.cloud.google.com/billing)
2. Select your billing account
3. Click **Manage** → **Projects**
4. Click **Link a project**
5. Select your project and click **Set account**

---

## 💰 Billing Configuration

### Step 4: Set Up Budget Alerts

#### 4.1 Create Budget via CLI

```bash
# Create budget configuration file
cat > budget-config.json << EOF
{
  "displayName": "SentinentalBERT Budget",
  "budgetFilter": {
    "projects": ["projects/$PROJECT_ID"]
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "5000"
    }
  },
  "thresholdRules": [
    {
      "thresholdPercent": 0.5,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.75,
      "spendBasis": "CURRENT_SPEND"
    },
    {
      "thresholdPercent": 0.9,
      "spendBasis": "CURRENT_SPEND"
    }
  ]
}
EOF

# Create budget (requires billing API)
gcloud services enable cloudbilling.googleapis.com
# Note: Budget creation via CLI requires additional setup
# Recommend using Console for budget creation
```

#### 4.2 Create Budget via Console

1. Go to [Billing Console](https://console.cloud.google.com/billing)
2. Select your billing account
3. Click **Budgets & alerts** → **Create budget**
4. Configure budget:
   - **Name**: `SentinentalBERT Budget`
   - **Projects**: Select your project
   - **Amount**: `$5,000`
   - **Alert thresholds**: `50%`, `75%`, `90%`
5. Set up notifications:
   - **Email**: Your admin email
   - **Pub/Sub**: Optional for automated responses
6. Click **Finish**

### Step 5: Cost Allocation Labels

```bash
# Set project labels for cost tracking
gcloud projects update $PROJECT_ID \
    --update-labels="environment=production,team=ml-engineering,project=sentinelbert,cost-center=ai-ml"
```

---

## 🔑 API Enablement

### Step 6: Enable Required APIs

#### 6.1 Core APIs for SentinentalBERT

```bash
# Enable all required APIs at once
gcloud services enable \
    aiplatform.googleapis.com \
    ml.googleapis.com \
    run.googleapis.com \
    bigquery.googleapis.com \
    pubsub.googleapis.com \
    storage.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    secretmanager.googleapis.com \
    cloudkms.googleapis.com \
    compute.googleapis.com \
    container.googleapis.com \
    cloudscheduler.googleapis.com \
    dataflow.googleapis.com \
    cloudsql.googleapis.com \
    redis.googleapis.com \
    --project=$PROJECT_ID
```

#### 6.2 Verify API Enablement

```bash
# List enabled APIs
gcloud services list --enabled --project=$PROJECT_ID

# Check specific API
gcloud services list --enabled --filter="name:aiplatform.googleapis.com" --project=$PROJECT_ID
```

#### 6.3 API Descriptions

| API | Service | Purpose |
|-----|---------|---------|
| `aiplatform.googleapis.com` | Vertex AI | ML model training and serving |
| `ml.googleapis.com` | AI Platform | Legacy ML services |
| `run.googleapis.com` | Cloud Run | Serverless containers |
| `bigquery.googleapis.com` | BigQuery | Data warehouse and analytics |
| `pubsub.googleapis.com` | Pub/Sub | Message streaming |
| `storage.googleapis.com` | Cloud Storage | Object storage |
| `cloudfunctions.googleapis.com` | Cloud Functions | Serverless functions |
| `cloudbuild.googleapis.com` | Cloud Build | CI/CD pipelines |
| `monitoring.googleapis.com` | Cloud Monitoring | Observability |
| `logging.googleapis.com` | Cloud Logging | Log management |
| `secretmanager.googleapis.com` | Secret Manager | Secrets storage |
| `cloudkms.googleapis.com` | Cloud KMS | Encryption keys |
| `compute.googleapis.com` | Compute Engine | Virtual machines |
| `container.googleapis.com` | GKE | Kubernetes clusters |
| `cloudscheduler.googleapis.com` | Cloud Scheduler | Cron jobs |
| `dataflow.googleapis.com` | Dataflow | Stream/batch processing |

---

## 🛡️ IAM Setup

### Step 7: Create Service Accounts

#### 7.1 Main Application Service Account

```bash
# Create main service account
gcloud iam service-accounts create sentinelbert-app \
    --display-name="SentinentalBERT Application" \
    --description="Main service account for SentinentalBERT application" \
    --project=$PROJECT_ID

# Get service account email
SA_EMAIL="sentinelbert-app@$PROJECT_ID.iam.gserviceaccount.com"
```

#### 7.2 Vertex AI Service Account

```bash
# Create Vertex AI service account
gcloud iam service-accounts create vertex-ai-service \
    --display-name="Vertex AI Service Account" \
    --description="Service account for Vertex AI operations" \
    --project=$PROJECT_ID

VERTEX_SA_EMAIL="vertex-ai-service@$PROJECT_ID.iam.gserviceaccount.com"
```

#### 7.3 Cloud Run Service Account

```bash
# Create Cloud Run service account
gcloud iam service-accounts create cloud-run-service \
    --display-name="Cloud Run Service Account" \
    --description="Service account for Cloud Run services" \
    --project=$PROJECT_ID

CLOUDRUN_SA_EMAIL="cloud-run-service@$PROJECT_ID.iam.gserviceaccount.com"
```

### Step 8: Assign IAM Roles

#### 8.1 Main Application Roles

```bash
# Assign roles to main service account
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
```

#### 8.2 Vertex AI Roles

```bash
# Assign Vertex AI specific roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$VERTEX_SA_EMAIL" \
    --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$VERTEX_SA_EMAIL" \
    --role="roles/ml.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$VERTEX_SA_EMAIL" \
    --role="roles/storage.admin"
```

#### 8.3 Cloud Run Roles

```bash
# Assign Cloud Run specific roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDRUN_SA_EMAIL" \
    --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUDRUN_SA_EMAIL" \
    --role="roles/cloudsql.client"
```

### Step 9: Create Service Account Keys

```bash
# Create key for main service account
gcloud iam service-accounts keys create ~/sentinelbert-app-key.json \
    --iam-account=$SA_EMAIL

# Create key for Vertex AI service account
gcloud iam service-accounts keys create ~/vertex-ai-key.json \
    --iam-account=$VERTEX_SA_EMAIL

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/sentinelbert-app-key.json
```

---

## 📊 Quotas & Limits

### Step 10: Check and Request Quotas

#### 10.1 Check Current Quotas

```bash
# Check Vertex AI quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Check specific quotas
gcloud compute regions describe us-east1 --project=$PROJECT_ID
```

#### 10.2 Required Quotas for Your Configuration

| Service | Resource | Required | Default | Action Needed |
|---------|----------|----------|---------|---------------|
| **Vertex AI** | TPU v5e cores | 4 | 0 | Request increase |
| **Cloud Run** | Services per region | 10 | 1000 | ✅ Sufficient |
| **BigQuery** | Slots | 100 | 2000 | ✅ Sufficient |
| **Pub/Sub** | Topics | 50 | 10000 | ✅ Sufficient |
| **Cloud Storage** | Buckets | 20 | 1000 | ✅ Sufficient |

#### 10.3 Request TPU Quota Increase

1. Go to [Quotas Console](https://console.cloud.google.com/iam-admin/quotas)
2. Filter by:
   - **Service**: `Vertex AI API`
   - **Location**: `us-east1`
3. Find `TPU v5e cores` quota
4. Click **Edit quotas**
5. Request increase to **4 cores**
6. Provide justification:
   ```
   Requesting TPU v5e quota for SentinentalBERT ML project.
   Need 4 cores for BERT model training and inference.
   Expected usage: 2 hours per month for cost optimization.
   ```

---

## 🔍 Verification

### Step 11: Verify Setup

#### 11.1 Project Verification

```bash
# Verify project details
gcloud projects describe $PROJECT_ID --format="table(
    projectId,
    name,
    labels.list():label=LABELS,
    lifecycleState
)"

# Check billing status
gcloud billing projects describe $PROJECT_ID --format="table(
    projectId,
    billingAccountName,
    billingEnabled
)"
```

#### 11.2 API Verification

```bash
# Count enabled APIs
gcloud services list --enabled --project=$PROJECT_ID | wc -l

# Verify critical APIs
for api in aiplatform.googleapis.com run.googleapis.com bigquery.googleapis.com; do
    echo "Checking $api..."
    gcloud services list --enabled --filter="name:$api" --project=$PROJECT_ID
done
```

#### 11.3 IAM Verification

```bash
# List service accounts
gcloud iam service-accounts list --project=$PROJECT_ID

# Check roles for main service account
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:$SA_EMAIL"
```

#### 11.4 Create Verification Script

```bash
# Create verification script
cat > verify-setup.sh << 'EOF'
#!/bin/bash

PROJECT_ID=$(gcloud config get-value project)
echo "🔍 Verifying GCP setup for project: $PROJECT_ID"
echo ""

# Check project
echo "📋 Project Status:"
gcloud projects describe $PROJECT_ID --format="value(lifecycleState)"

# Check billing
echo "💰 Billing Status:"
gcloud billing projects describe $PROJECT_ID --format="value(billingEnabled)"

# Check APIs
echo "🔑 Enabled APIs:"
gcloud services list --enabled --project=$PROJECT_ID | grep -E "(aiplatform|run|bigquery|pubsub|storage)" | wc -l
echo "   (Should be at least 5 core APIs)"

# Check service accounts
echo "🛡️  Service Accounts:"
gcloud iam service-accounts list --project=$PROJECT_ID | grep -c "sentinelbert"
echo "   (Should be at least 3 service accounts)"

echo ""
echo "✅ Setup verification completed!"
EOF

chmod +x verify-setup.sh
./verify-setup.sh
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Billing Not Enabled

**Error**: `Project billing is not enabled`

**Solution**:
```bash
# Check billing status
gcloud billing projects describe $PROJECT_ID

# If not enabled, link billing account
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
```

#### Issue 2: API Not Enabled

**Error**: `API [service] is not enabled`

**Solution**:
```bash
# Enable specific API
gcloud services enable [API_NAME] --project=$PROJECT_ID

# Example
gcloud services enable aiplatform.googleapis.com --project=$PROJECT_ID
```

#### Issue 3: Insufficient Permissions

**Error**: `Permission denied` or `Access denied`

**Solution**:
```bash
# Check current user permissions
gcloud projects get-iam-policy $PROJECT_ID

# Add necessary role to user
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:your-email@domain.com" \
    --role="roles/owner"
```

#### Issue 4: Quota Exceeded

**Error**: `Quota exceeded for resource`

**Solution**:
1. Go to [Quotas Console](https://console.cloud.google.com/iam-admin/quotas)
2. Find the specific quota
3. Request increase with business justification

#### Issue 5: Service Account Key Issues

**Error**: `Could not create service account key`

**Solution**:
```bash
# Check if service account exists
gcloud iam service-accounts list --project=$PROJECT_ID

# Recreate service account if needed
gcloud iam service-accounts create sentinelbert-app \
    --display-name="SentinentalBERT Application" \
    --project=$PROJECT_ID
```

### Getting Help

- **GCP Documentation**: https://cloud.google.com/docs
- **Support Console**: https://console.cloud.google.com/support
- **Community**: https://stackoverflow.com/questions/tagged/google-cloud-platform
- **Status Page**: https://status.cloud.google.com/

---

## 📞 Important Links & References

### 🔗 Essential GCP Console Links

- **Project Dashboard**: https://console.cloud.google.com/home/dashboard?project=$PROJECT_ID
- **Billing Console**: https://console.cloud.google.com/billing
- **IAM Console**: https://console.cloud.google.com/iam-admin/iam
- **API Library**: https://console.cloud.google.com/apis/library
- **Quotas Console**: https://console.cloud.google.com/iam-admin/quotas
- **Service Accounts**: https://console.cloud.google.com/iam-admin/serviceaccounts

### 📚 Documentation References

- **GCP Project Setup**: https://cloud.google.com/resource-manager/docs/creating-managing-projects
- **Billing Setup**: https://cloud.google.com/billing/docs/how-to/manage-billing-account
- **IAM Best Practices**: https://cloud.google.com/iam/docs/using-iam-securely
- **Service Accounts**: https://cloud.google.com/iam/docs/service-accounts
- **API Management**: https://cloud.google.com/apis/docs/getting-started
- **Quota Management**: https://cloud.google.com/docs/quota

### 🛠️ CLI References

- **gcloud CLI**: https://cloud.google.com/sdk/gcloud/reference
- **Project Commands**: https://cloud.google.com/sdk/gcloud/reference/projects
- **IAM Commands**: https://cloud.google.com/sdk/gcloud/reference/iam
- **Services Commands**: https://cloud.google.com/sdk/gcloud/reference/services

---

<div align="center">

**Next Steps**: Continue with [Vertex AI Setup](./02-vertex-ai-setup.md) to configure your ML infrastructure.

*Your GCP project is now ready for SentinentalBERT deployment with optimized cost management and security.*

</div>
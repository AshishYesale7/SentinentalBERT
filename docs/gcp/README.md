# SentinentalBERT Google Cloud Platform Setup Guide

<div align="center">

![GCP](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Vertex AI](https://img.shields.io/badge/Vertex%20AI-FF6F00?style=for-the-badge&logo=google&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-669DF6?style=for-the-badge&logo=google-cloud&logoColor=white)

**Production-Ready GCP Deployment for Advanced Sentiment Analysis**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [💰 Cost Optimization](#-cost-optimization)
- [🏗️ Architecture](#️-architecture)
- [📚 Setup Guides](#-setup-guides)
- [🔧 Configuration](#-configuration)
- [🚀 Deployment](#-deployment)
- [📊 Monitoring](#-monitoring)
- [🔒 Security](#-security)

---

## 🎯 Overview

This guide provides comprehensive instructions for deploying SentinentalBERT on Google Cloud Platform using your optimized configuration. The setup is designed for production workloads with cost optimization and scalability in mind.

### 🌟 Key Features

- **Vertex AI Integration**: TPU V5e acceleration for ML workloads
- **Serverless Architecture**: Cloud Run with auto-scaling
- **Data Pipeline**: Pub/Sub → BigQuery → Cloud Storage
- **Code Generation**: Codey models for automated development
- **Cost Optimized**: Designed to maximize your $5,000 credits

### 📊 Your GCP Configuration Summary

| Service | Configuration | Monthly Cost Est. |
|---------|---------------|-------------------|
| **Vertex AI Prediction** | TPU V5e, 4 cores, 2 hours/month | ~$200-400 |
| **Vertex AI Pipelines** | 120 pipeline runs/month | ~$50-100 |
| **Code Models (Codey)** | 1000 requests/day each | ~$500-800 |
| **Cloud Run** | 2 vCPU, 1 GiB, 10M requests | ~$50-100 |
| **BigQuery** | 100 slots, 6 GiB active, 10 GiB long-term | ~$20-50 |
| **Pub/Sub** | 15 GiB daily data | ~$10-20 |
| **Cloud Storage** | 200 GiB Standard Storage | ~$5-10 |
| **Total Estimated** | | **~$835-1,480/month** |

---

## 💰 Cost Optimization Strategy

### 🎯 Credit Allocation (Recommended)

- **70% ($3,500)**: Vertex AI, TPU, and Codey models
- **15% ($750)**: Cloud Run, compute resources
- **10% ($500)**: BigQuery, Cloud Storage, Pub/Sub
- **5% ($250)**: Monitoring, logging, security

### 💡 Cost Optimization Tips

1. **Use Committed Use Discounts**: 17% discount on Cloud Run
2. **Optimize TPU Usage**: Schedule ML training during off-peak hours
3. **Batch Processing**: Group API calls to reduce per-request costs
4. **Data Lifecycle**: Automatically move old data to cheaper storage classes
5. **Resource Monitoring**: Set up budget alerts at 50%, 75%, 90%

---

## 📚 Setup Guides

### 🚀 Quick Start Checklist

- [ ] [1. Project Setup & Billing](./01-project-setup.md)
- [ ] [2. Vertex AI Configuration](./02-vertex-ai-setup.md)
- [ ] [3. Code Models Setup](./03-code-models-setup.md)
- [ ] [4. Cloud Run Deployment](./04-cloud-run-setup.md)
- [ ] [5. BigQuery & Analytics](./05-bigquery-setup.md)
- [ ] [6. Pub/Sub Configuration](./06-pubsub-setup.md)
- [ ] [7. Cloud Storage Setup](./07-storage-setup.md)
- [ ] [8. Monitoring & Alerting](./08-monitoring-setup.md)
- [ ] [9. Security Configuration](./09-security-setup.md)
- [ ] [10. Deployment Automation](./10-deployment-automation.md)

---

## 🔧 Configuration

### 🌐 Environment Variables

Your `.env` file should include these GCP-specific configurations:

```bash
# =============================================================================
# GOOGLE CLOUD PLATFORM CONFIGURATION
# =============================================================================

# Project Configuration
GCP_PROJECT_ID=your-sentinelbert-project
GCP_REGION=us-east1
GCP_ZONE=us-east1-a

# Vertex AI Configuration
VERTEX_AI_REGION=us-east1
VERTEX_AI_TPU_TYPE=ct5lp-hightpu-4t
VERTEX_AI_TPU_CORES=4
VERTEX_AI_ACCELERATOR=TPU_V5E

# Code Models Configuration
CODEY_PROJECT_ID=your-sentinelbert-project
CODEY_LOCATION=us-central1
CODEY_GENERATION_REQUESTS_PER_DAY=1000
CODEY_CHAT_REQUESTS_PER_DAY=1000
CODEY_COMPLETION_REQUESTS_PER_DAY=1000

# Cloud Run Configuration
CLOUD_RUN_REGION=europe-west1
CLOUD_RUN_CPU=2
CLOUD_RUN_MEMORY=1Gi
CLOUD_RUN_MAX_INSTANCES=100
CLOUD_RUN_MIN_INSTANCES=0

# BigQuery Configuration
BIGQUERY_DATASET=sentinelbert_analytics
BIGQUERY_LOCATION=US
BIGQUERY_MAX_SLOTS=100
BIGQUERY_EDITION=STANDARD

# Pub/Sub Configuration
PUBSUB_TOPIC=social-media-ingestion
PUBSUB_SUBSCRIPTION=sentiment-analysis
PUBSUB_RETENTION_DAYS=1

# Cloud Storage Configuration
STORAGE_BUCKET=sentinelbert-data-lake
STORAGE_REGION=us-central1
STORAGE_CLASS=STANDARD
```

---

## 📞 Support & Resources

### 🔗 Important Links

- **GCP Console**: https://console.cloud.google.com/
- **Vertex AI**: https://console.cloud.google.com/vertex-ai
- **Cloud Run**: https://console.cloud.google.com/run
- **BigQuery**: https://console.cloud.google.com/bigquery
- **Cloud Storage**: https://console.cloud.google.com/storage
- **Monitoring**: https://console.cloud.google.com/monitoring

### 📚 Documentation References

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)

---

<div align="center">

**Next Steps**: Start with [Project Setup](./01-project-setup.md) to begin your GCP deployment.

*This guide is optimized for your specific GCP configuration and $5,000 credit budget.*

</div>
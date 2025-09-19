# Monitoring & Alerting Setup Guide for SentinentalBERT

<div align="center">

![Monitoring](https://img.shields.io/badge/Monitoring-Cloud%20Operations-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Alerting](https://img.shields.io/badge/Alerting-Real%20Time-FF6F00?style=for-the-badge&logo=prometheus&logoColor=white)

**Comprehensive Observability with Cost-Optimized Monitoring**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [📊 Monitoring Dashboard](#-monitoring-dashboard)
- [🚨 Alert Policies](#-alert-policies)
- [💰 Cost Monitoring](#-cost-monitoring)
- [📈 Performance Metrics](#-performance-metrics)
- [🔍 Log Management](#-log-management)
- [📱 Notification Channels](#-notification-channels)
- [🧪 Testing & Validation](#-testing--validation)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide configures comprehensive monitoring and alerting for SentinentalBERT across all GCP services. Your setup includes cost optimization, performance tracking, and proactive alerting within your $5,000 budget.

### 🌟 Your Monitoring Configuration

Based on your specifications:

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| **Cloud Monitoring** | Standard tier | Core metrics and alerting |
| **Cloud Logging** | 50 GiB/month | Application and system logs |
| **Uptime Checks** | 10 checks | Service availability monitoring |
| **Alert Policies** | 25 policies | Comprehensive alerting |
| **Dashboards** | 5 custom dashboards | Visual monitoring |
| **Notification Channels** | Email, Slack, PagerDuty | Multi-channel alerting |
| **SLA Monitoring** | 99.9% availability | Service level tracking |

### 💰 Cost Optimization Features

- **Intelligent Sampling**: Reduce log volume while maintaining visibility
- **Metric Filtering**: Focus on critical metrics only
- **Alert Deduplication**: Prevent alert storms
- **Automated Scaling**: Monitor and optimize resource usage

### ⏱️ Estimated Setup Time: 30-35 minutes

---

## 🔧 Prerequisites

### ✅ Required Setup

1. **GCP Project**: With monitoring APIs enabled
2. **Service Account**: With monitoring permissions
3. **Notification Endpoints**: Email, Slack webhook, etc.
4. **gcloud CLI**: Authenticated and configured

### 📦 Install Required Tools

```bash
# Install monitoring client libraries
pip install google-cloud-monitoring
pip install google-cloud-logging
pip install google-cloud-error-reporting

# Install additional dependencies
pip install prometheus-client
pip install grafana-api
```

### 🔑 Enable APIs

```bash
# Enable monitoring and logging APIs
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable clouderrorreporting.googleapis.com
gcloud services enable cloudtrace.googleapis.com
gcloud services enable cloudprofiler.googleapis.com

# Verify API enablement
gcloud services list --enabled --filter="name:monitoring"
```

---

## 🚀 Step-by-Step Setup

### Step 1: Create Monitoring Configuration

```bash
# Create monitoring configuration directory
mkdir -p gcp/monitoring/{dashboards,alerts,policies,scripts,templates}

# Create configuration file
cat > gcp/monitoring/config.yaml << 'EOF'
# Monitoring Configuration for SentinentalBERT
project_id: "your-sentinelbert-project"
region: "us-central1"

# Monitoring configuration
monitoring_tier: "standard"
log_retention_days: 30
uptime_checks: 10
alert_policies: 25
custom_dashboards: 5

# Cost optimization
log_volume_gib_per_month: 50
metric_sampling_rate: 0.1  # 10% sampling for high-volume metrics
alert_deduplication_window: "300s"

# SLA targets
availability_target: 99.9
latency_target_ms: 500
error_rate_target: 0.1

# Services to monitor
services:
  - name: "vertex-ai"
    type: "ml_service"
    critical: true
    sla_target: 99.9
    
  - name: "cloud-run"
    type: "compute_service"
    critical: true
    sla_target: 99.9
    
  - name: "bigquery"
    type: "data_service"
    critical: true
    sla_target: 99.9
    
  - name: "pubsub"
    type: "messaging_service"
    critical: true
    sla_target: 99.9
    
  - name: "cloud-storage"
    type: "storage_service"
    critical: false
    sla_target: 99.5

# Alert categories
alert_categories:
  - name: "cost_alerts"
    priority: "high"
    channels: ["email", "slack"]
    
  - name: "performance_alerts"
    priority: "medium"
    channels: ["email"]
    
  - name: "availability_alerts"
    priority: "critical"
    channels: ["email", "slack", "pagerduty"]
    
  - name: "security_alerts"
    priority: "critical"
    channels: ["email", "slack", "pagerduty"]

# Notification channels
notification_channels:
  email:
    - "admin@yourcompany.com"
    - "devops@yourcompany.com"
  slack:
    webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    channel: "#sentinelbert-alerts"
  pagerduty:
    integration_key: "YOUR_PAGERDUTY_INTEGRATION_KEY"
EOF
```

### Step 2: Create Monitoring Setup Script

```bash
# Create monitoring setup script
cat > gcp/monitoring/scripts/setup-monitoring.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="us-central1"

echo "📊 Setting up comprehensive monitoring for project: $PROJECT_ID"

# Create notification channels
echo "📱 Creating notification channels..."

# Email notification channel
gcloud alpha monitoring channels create \
    --display-name="SentinentalBERT Admin Email" \
    --type="email" \
    --channel-labels="email_address=admin@yourcompany.com" \
    --project=$PROJECT_ID

# Slack notification channel (if webhook configured)
# gcloud alpha monitoring channels create \
#     --display-name="SentinentalBERT Slack" \
#     --type="slack" \
#     --channel-labels="url=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
#     --project=$PROJECT_ID

# Create uptime checks
echo "🔍 Creating uptime checks..."

# Cloud Run service uptime check
gcloud monitoring uptime create \
    --display-name="SentinentalBERT Backend Health" \
    --http-check-path="/health" \
    --hostname="your-backend-service-url.run.app" \
    --project=$PROJECT_ID

# BigQuery uptime check (custom)
gcloud monitoring uptime create \
    --display-name="BigQuery Availability" \
    --http-check-path="/health" \
    --hostname="bigquery.googleapis.com" \
    --project=$PROJECT_ID

# Create log-based metrics
echo "📝 Creating log-based metrics..."

# Error rate metric
gcloud logging metrics create error_rate \
    --description="Application error rate" \
    --log-filter='severity>=ERROR' \
    --project=$PROJECT_ID

# Request latency metric
gcloud logging metrics create request_latency \
    --description="Request latency distribution" \
    --log-filter='httpRequest.latency>0' \
    --project=$PROJECT_ID

echo "✅ Basic monitoring setup completed!"
echo "📋 Next steps:"
echo "  1. Configure custom dashboards"
echo "  2. Set up alert policies"
echo "  3. Test notification channels"
EOF

chmod +x gcp/monitoring/scripts/setup-monitoring.sh
./gcp/monitoring/scripts/setup-monitoring.sh your-sentinelbert-project
```

---

## 📊 Monitoring Dashboard

### Step 3: Create Comprehensive Dashboards

```python
# gcp/monitoring/dashboards/dashboard_manager.py
"""
Dashboard management for SentinentalBERT monitoring
Creates comprehensive monitoring dashboards
"""

from google.cloud import monitoring_dashboard_v1
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SentinelBertDashboardManager:
    """
    Comprehensive dashboard management for SentinentalBERT
    Creates and manages monitoring dashboards
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_dashboard_v1.DashboardsServiceClient()
        self.project_name = f"projects/{project_id}"
        
        logger.info(f"Dashboard manager initialized for project: {project_id}")
    
    def create_main_dashboard(self) -> str:
        """
        Create main SentinentalBERT monitoring dashboard
        
        Returns:
            Dashboard ID
        """
        
        dashboard_config = {
            "displayName": "SentinentalBERT - Main Dashboard",
            "mosaicLayout": {
                "tiles": [
                    self._create_system_overview_tile(),
                    self._create_cost_overview_tile(),
                    self._create_performance_metrics_tile(),
                    self._create_error_rate_tile(),
                    self._create_ml_pipeline_tile(),
                    self._create_data_pipeline_tile()
                ]
            }
        }
        
        try:
            dashboard = self.client.create_dashboard(
                parent=self.project_name,
                dashboard=dashboard_config
            )
            
            dashboard_id = dashboard.name.split('/')[-1]
            logger.info(f"Created main dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create main dashboard: {str(e)}")
            return ""
    
    def create_cost_dashboard(self) -> str:
        """
        Create cost monitoring dashboard
        
        Returns:
            Dashboard ID
        """
        
        dashboard_config = {
            "displayName": "SentinentalBERT - Cost Monitoring",
            "mosaicLayout": {
                "tiles": [
                    self._create_daily_cost_tile(),
                    self._create_service_cost_breakdown_tile(),
                    self._create_budget_utilization_tile(),
                    self._create_cost_trends_tile(),
                    self._create_resource_utilization_tile(),
                    self._create_cost_optimization_tile()
                ]
            }
        }
        
        try:
            dashboard = self.client.create_dashboard(
                parent=self.project_name,
                dashboard=dashboard_config
            )
            
            dashboard_id = dashboard.name.split('/')[-1]
            logger.info(f"Created cost dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create cost dashboard: {str(e)}")
            return ""
    
    def create_ml_pipeline_dashboard(self) -> str:
        """
        Create ML pipeline monitoring dashboard
        
        Returns:
            Dashboard ID
        """
        
        dashboard_config = {
            "displayName": "SentinentalBERT - ML Pipeline",
            "mosaicLayout": {
                "tiles": [
                    self._create_vertex_ai_metrics_tile(),
                    self._create_model_performance_tile(),
                    self._create_training_metrics_tile(),
                    self._create_inference_metrics_tile(),
                    self._create_tpu_utilization_tile(),
                    self._create_model_accuracy_tile()
                ]
            }
        }
        
        try:
            dashboard = self.client.create_dashboard(
                parent=self.project_name,
                dashboard=dashboard_config
            )
            
            dashboard_id = dashboard.name.split('/')[-1]
            logger.info(f"Created ML pipeline dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create ML pipeline dashboard: {str(e)}")
            return ""
    
    def create_data_pipeline_dashboard(self) -> str:
        """
        Create data pipeline monitoring dashboard
        
        Returns:
            Dashboard ID
        """
        
        dashboard_config = {
            "displayName": "SentinentalBERT - Data Pipeline",
            "mosaicLayout": {
                "tiles": [
                    self._create_pubsub_metrics_tile(),
                    self._create_bigquery_metrics_tile(),
                    self._create_storage_metrics_tile(),
                    self._create_data_freshness_tile(),
                    self._create_pipeline_throughput_tile(),
                    self._create_data_quality_tile()
                ]
            }
        }
        
        try:
            dashboard = self.client.create_dashboard(
                parent=self.project_name,
                dashboard=dashboard_config
            )
            
            dashboard_id = dashboard.name.split('/')[-1]
            logger.info(f"Created data pipeline dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create data pipeline dashboard: {str(e)}")
            return ""
    
    def create_sla_dashboard(self) -> str:
        """
        Create SLA monitoring dashboard
        
        Returns:
            Dashboard ID
        """
        
        dashboard_config = {
            "displayName": "SentinentalBERT - SLA Monitoring",
            "mosaicLayout": {
                "tiles": [
                    self._create_availability_sla_tile(),
                    self._create_latency_sla_tile(),
                    self._create_error_rate_sla_tile(),
                    self._create_uptime_checks_tile(),
                    self._create_sla_burn_rate_tile(),
                    self._create_incident_tracking_tile()
                ]
            }
        }
        
        try:
            dashboard = self.client.create_dashboard(
                parent=self.project_name,
                dashboard=dashboard_config
            )
            
            dashboard_id = dashboard.name.split('/')[-1]
            logger.info(f"Created SLA dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create SLA dashboard: {str(e)}")
            return ""
    
    def _create_system_overview_tile(self) -> Dict:
        """Create system overview tile"""
        return {
            "width": 12,
            "height": 4,
            "widget": {
                "title": "System Overview",
                "scorecard": {
                    "timeSeriesQuery": {
                        "timeSeriesFilter": {
                            "filter": 'resource.type="gce_instance"',
                            "aggregation": {
                                "alignmentPeriod": "60s",
                                "perSeriesAligner": "ALIGN_MEAN"
                            }
                        }
                    },
                    "sparkChartView": {
                        "sparkChartType": "SPARK_LINE"
                    }
                }
            }
        }
    
    def _create_cost_overview_tile(self) -> Dict:
        """Create cost overview tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Daily Cost Overview",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="billing_account"',
                                "aggregation": {
                                    "alignmentPeriod": "86400s",
                                    "perSeriesAligner": "ALIGN_SUM"
                                }
                            }
                        },
                        "plotType": "LINE"
                    }],
                    "yAxis": {
                        "label": "Cost (USD)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_performance_metrics_tile(self) -> Dict:
        """Create performance metrics tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Response Time & Throughput",
                "xyChart": {
                    "dataSets": [
                        {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": 'resource.type="cloud_run_revision"',
                                    "aggregation": {
                                        "alignmentPeriod": "60s",
                                        "perSeriesAligner": "ALIGN_MEAN"
                                    }
                                }
                            },
                            "plotType": "LINE"
                        }
                    ],
                    "yAxis": {
                        "label": "Response Time (ms)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_error_rate_tile(self) -> Dict:
        """Create error rate tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Error Rate",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="cloud_run_revision"',
                                "aggregation": {
                                    "alignmentPeriod": "300s",
                                    "perSeriesAligner": "ALIGN_RATE"
                                }
                            }
                        },
                        "plotType": "STACKED_AREA"
                    }],
                    "yAxis": {
                        "label": "Error Rate (%)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_ml_pipeline_tile(self) -> Dict:
        """Create ML pipeline tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "ML Pipeline Status",
                "scorecard": {
                    "timeSeriesQuery": {
                        "timeSeriesFilter": {
                            "filter": 'resource.type="aiplatform.googleapis.com/PipelineJob"',
                            "aggregation": {
                                "alignmentPeriod": "3600s",
                                "perSeriesAligner": "ALIGN_COUNT"
                            }
                        }
                    },
                    "gaugeView": {
                        "lowerBound": 0.0,
                        "upperBound": 100.0
                    }
                }
            }
        }
    
    def _create_data_pipeline_tile(self) -> Dict:
        """Create data pipeline tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Data Pipeline Throughput",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="pubsub_topic"',
                                "aggregation": {
                                    "alignmentPeriod": "300s",
                                    "perSeriesAligner": "ALIGN_RATE"
                                }
                            }
                        },
                        "plotType": "STACKED_BAR"
                    }],
                    "yAxis": {
                        "label": "Messages/sec",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    # Additional tile creation methods for other dashboards...
    def _create_daily_cost_tile(self) -> Dict:
        """Create daily cost tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Daily Cost Breakdown",
                "pieChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="billing_account"',
                                "aggregation": {
                                    "alignmentPeriod": "86400s",
                                    "perSeriesAligner": "ALIGN_SUM",
                                    "crossSeriesReducer": "REDUCE_SUM",
                                    "groupByFields": ["resource.label.service"]
                                }
                            }
                        }
                    }]
                }
            }
        }
    
    def _create_service_cost_breakdown_tile(self) -> Dict:
        """Create service cost breakdown tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Service Cost Breakdown",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="billing_account"',
                                "aggregation": {
                                    "alignmentPeriod": "3600s",
                                    "perSeriesAligner": "ALIGN_SUM",
                                    "crossSeriesReducer": "REDUCE_SUM",
                                    "groupByFields": ["resource.label.service"]
                                }
                            }
                        },
                        "plotType": "STACKED_AREA"
                    }],
                    "yAxis": {
                        "label": "Cost (USD)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_budget_utilization_tile(self) -> Dict:
        """Create budget utilization tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Budget Utilization",
                "scorecard": {
                    "timeSeriesQuery": {
                        "timeSeriesFilter": {
                            "filter": 'resource.type="billing_account"',
                            "aggregation": {
                                "alignmentPeriod": "86400s",
                                "perSeriesAligner": "ALIGN_SUM"
                            }
                        }
                    },
                    "gaugeView": {
                        "lowerBound": 0.0,
                        "upperBound": 5000.0  # $5000 budget
                    }
                }
            }
        }
    
    def _create_vertex_ai_metrics_tile(self) -> Dict:
        """Create Vertex AI metrics tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Vertex AI TPU Utilization",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="aiplatform.googleapis.com/Endpoint"',
                                "aggregation": {
                                    "alignmentPeriod": "300s",
                                    "perSeriesAligner": "ALIGN_MEAN"
                                }
                            }
                        },
                        "plotType": "LINE"
                    }],
                    "yAxis": {
                        "label": "Utilization (%)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_pubsub_metrics_tile(self) -> Dict:
        """Create Pub/Sub metrics tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Pub/Sub Message Flow",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="pubsub_topic"',
                                "aggregation": {
                                    "alignmentPeriod": "60s",
                                    "perSeriesAligner": "ALIGN_RATE"
                                }
                            }
                        },
                        "plotType": "STACKED_AREA"
                    }],
                    "yAxis": {
                        "label": "Messages/sec",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_bigquery_metrics_tile(self) -> Dict:
        """Create BigQuery metrics tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "BigQuery Query Performance",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="bigquery_project"',
                                "aggregation": {
                                    "alignmentPeriod": "300s",
                                    "perSeriesAligner": "ALIGN_MEAN"
                                }
                            }
                        },
                        "plotType": "LINE"
                    }],
                    "yAxis": {
                        "label": "Query Duration (s)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_availability_sla_tile(self) -> Dict:
        """Create availability SLA tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Service Availability (SLA: 99.9%)",
                "scorecard": {
                    "timeSeriesQuery": {
                        "timeSeriesFilter": {
                            "filter": 'resource.type="uptime_check"',
                            "aggregation": {
                                "alignmentPeriod": "3600s",
                                "perSeriesAligner": "ALIGN_FRACTION_TRUE"
                            }
                        }
                    },
                    "gaugeView": {
                        "lowerBound": 99.0,
                        "upperBound": 100.0
                    }
                }
            }
        }
    
    # Additional tile methods would continue here...
    
    def create_all_dashboards(self) -> Dict[str, str]:
        """
        Create all monitoring dashboards
        
        Returns:
            Dictionary mapping dashboard names to IDs
        """
        
        dashboards = {}
        
        try:
            dashboards["main"] = self.create_main_dashboard()
            dashboards["cost"] = self.create_cost_dashboard()
            dashboards["ml_pipeline"] = self.create_ml_pipeline_dashboard()
            dashboards["data_pipeline"] = self.create_data_pipeline_dashboard()
            dashboards["sla"] = self.create_sla_dashboard()
            
            logger.info(f"Created {len(dashboards)} dashboards")
            return dashboards
            
        except Exception as e:
            logger.error(f"Failed to create dashboards: {str(e)}")
            return dashboards

# Usage example
if __name__ == "__main__":
    manager = SentinelBertDashboardManager("your-sentinelbert-project")
    
    # Create all dashboards
    dashboards = manager.create_all_dashboards()
    print(f"Created dashboards: {dashboards}")
```

---

## 🚨 Alert Policies

### Step 4: Create Comprehensive Alert Policies

```python
# gcp/monitoring/alerts/alert_manager.py
"""
Alert policy management for SentinentalBERT
Creates comprehensive alerting across all services
"""

from google.cloud import monitoring_v3
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SentinelBertAlertManager:
    """
    Comprehensive alert management for SentinentalBERT
    Creates and manages alert policies across all services
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.AlertPolicyServiceClient()
        self.project_name = f"projects/{project_id}"
        
        # Alert policy templates
        self.alert_templates = {
            "cost_alerts": [
                {
                    "name": "Daily Budget Exceeded",
                    "threshold": 100.0,  # $100 daily
                    "comparison": "COMPARISON_GREATER_THAN",
                    "duration": "300s"
                },
                {
                    "name": "Monthly Budget 75% Used",
                    "threshold": 3750.0,  # 75% of $5000
                    "comparison": "COMPARISON_GREATER_THAN",
                    "duration": "3600s"
                }
            ],
            "performance_alerts": [
                {
                    "name": "High Response Time",
                    "threshold": 2000.0,  # 2 seconds
                    "comparison": "COMPARISON_GREATER_THAN",
                    "duration": "300s"
                },
                {
                    "name": "Low Throughput",
                    "threshold": 10.0,  # 10 requests/minute
                    "comparison": "COMPARISON_LESS_THAN",
                    "duration": "600s"
                }
            ],
            "availability_alerts": [
                {
                    "name": "Service Unavailable",
                    "threshold": 0.999,  # 99.9% availability
                    "comparison": "COMPARISON_LESS_THAN",
                    "duration": "300s"
                },
                {
                    "name": "High Error Rate",
                    "threshold": 0.05,  # 5% error rate
                    "comparison": "COMPARISON_GREATER_THAN",
                    "duration": "300s"
                }
            ],
            "resource_alerts": [
                {
                    "name": "High CPU Usage",
                    "threshold": 80.0,  # 80% CPU
                    "comparison": "COMPARISON_GREATER_THAN",
                    "duration": "600s"
                },
                {
                    "name": "High Memory Usage",
                    "threshold": 85.0,  # 85% memory
                    "comparison": "COMPARISON_GREATER_THAN",
                    "duration": "600s"
                }
            ]
        }
        
        logger.info(f"Alert manager initialized for project: {project_id}")
    
    def create_cost_alerts(self, notification_channels: List[str]) -> List[str]:
        """
        Create cost monitoring alerts
        
        Args:
            notification_channels: List of notification channel names
            
        Returns:
            List of created alert policy names
        """
        
        created_policies = []
        
        # Daily cost alert
        daily_cost_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Daily Cost Alert",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when daily costs exceed $100",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Daily cost > $100",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="billing_account"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=100.0,
                        duration={"seconds": 300},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 86400},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_SUM
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels,
            alert_strategy=monitoring_v3.AlertPolicy.AlertStrategy(
                auto_close={"seconds": 86400}  # Auto-close after 1 day
            )
        )
        
        # Monthly budget alert
        monthly_budget_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Monthly Budget Alert",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when monthly costs exceed 75% of $5000 budget",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Monthly cost > $3750",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="billing_account"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=3750.0,
                        duration={"seconds": 3600},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 86400},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_SUM
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        try:
            # Create policies
            created_daily = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=daily_cost_policy
            )
            created_policies.append(created_daily.name)
            
            created_monthly = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=monthly_budget_policy
            )
            created_policies.append(created_monthly.name)
            
            logger.info(f"Created {len(created_policies)} cost alert policies")
            
        except Exception as e:
            logger.error(f"Failed to create cost alerts: {str(e)}")
        
        return created_policies
    
    def create_performance_alerts(self, notification_channels: List[str]) -> List[str]:
        """
        Create performance monitoring alerts
        
        Args:
            notification_channels: List of notification channel names
            
        Returns:
            List of created alert policy names
        """
        
        created_policies = []
        
        # High response time alert
        response_time_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - High Response Time",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when response time exceeds 2 seconds",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Response time > 2s",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="cloud_run_revision"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=2000.0,  # 2000ms
                        duration={"seconds": 300},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 60},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        # Low throughput alert
        throughput_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Low Throughput",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when request throughput drops below 10 requests/minute",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Throughput < 10 req/min",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="cloud_run_revision"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_LESS_THAN,
                        threshold_value=10.0,
                        duration={"seconds": 600},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 60},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        try:
            # Create policies
            created_response = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=response_time_policy
            )
            created_policies.append(created_response.name)
            
            created_throughput = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=throughput_policy
            )
            created_policies.append(created_throughput.name)
            
            logger.info(f"Created {len(created_policies)} performance alert policies")
            
        except Exception as e:
            logger.error(f"Failed to create performance alerts: {str(e)}")
        
        return created_policies
    
    def create_availability_alerts(self, notification_channels: List[str]) -> List[str]:
        """
        Create availability monitoring alerts
        
        Args:
            notification_channels: List of notification channel names
            
        Returns:
            List of created alert policy names
        """
        
        created_policies = []
        
        # Service availability alert
        availability_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Service Unavailable",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when service availability drops below 99.9%",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Availability < 99.9%",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="uptime_check"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_LESS_THAN,
                        threshold_value=0.999,
                        duration={"seconds": 300},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 300},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_FRACTION_TRUE
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        # High error rate alert
        error_rate_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - High Error Rate",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when error rate exceeds 5%",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Error rate > 5%",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="cloud_run_revision"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=0.05,
                        duration={"seconds": 300},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 60},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        try:
            # Create policies
            created_availability = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=availability_policy
            )
            created_policies.append(created_availability.name)
            
            created_error = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=error_rate_policy
            )
            created_policies.append(created_error.name)
            
            logger.info(f"Created {len(created_policies)} availability alert policies")
            
        except Exception as e:
            logger.error(f"Failed to create availability alerts: {str(e)}")
        
        return created_policies
    
    def create_ml_pipeline_alerts(self, notification_channels: List[str]) -> List[str]:
        """
        Create ML pipeline specific alerts
        
        Args:
            notification_channels: List of notification channel names
            
        Returns:
            List of created alert policy names
        """
        
        created_policies = []
        
        # TPU utilization alert
        tpu_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Low TPU Utilization",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when TPU utilization is below 20% for extended period",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="TPU utilization < 20%",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="aiplatform.googleapis.com/Endpoint"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_LESS_THAN,
                        threshold_value=0.20,
                        duration={"seconds": 1800},  # 30 minutes
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 300},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        # Model accuracy alert
        accuracy_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Model Accuracy Drop",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when model accuracy drops below 85%",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Model accuracy < 85%",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='metric.type="custom.googleapis.com/ml/model_accuracy"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_LESS_THAN,
                        threshold_value=0.85,
                        duration={"seconds": 600},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 300},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        try:
            # Create policies
            created_tpu = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=tpu_policy
            )
            created_policies.append(created_tpu.name)
            
            created_accuracy = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=accuracy_policy
            )
            created_policies.append(created_accuracy.name)
            
            logger.info(f"Created {len(created_policies)} ML pipeline alert policies")
            
        except Exception as e:
            logger.error(f"Failed to create ML pipeline alerts: {str(e)}")
        
        return created_policies
    
    def create_data_pipeline_alerts(self, notification_channels: List[str]) -> List[str]:
        """
        Create data pipeline specific alerts
        
        Args:
            notification_channels: List of notification channel names
            
        Returns:
            List of created alert policy names
        """
        
        created_policies = []
        
        # Pub/Sub backlog alert
        pubsub_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - Pub/Sub Message Backlog",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when Pub/Sub message backlog exceeds 10,000 messages",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Message backlog > 10k",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="pubsub_subscription"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=10000.0,
                        duration={"seconds": 300},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 60},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        # BigQuery query failure alert
        bigquery_policy = monitoring_v3.AlertPolicy(
            display_name="SentinentalBERT - BigQuery Query Failures",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when BigQuery query failure rate exceeds 10%",
                mime_type="text/markdown"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Query failure rate > 10%",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="bigquery_project"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=0.10,
                        duration={"seconds": 300},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 300},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE
                            )
                        ]
                    )
                )
            ],
            notification_channels=notification_channels
        )
        
        try:
            # Create policies
            created_pubsub = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=pubsub_policy
            )
            created_policies.append(created_pubsub.name)
            
            created_bigquery = self.client.create_alert_policy(
                name=self.project_name,
                alert_policy=bigquery_policy
            )
            created_policies.append(created_bigquery.name)
            
            logger.info(f"Created {len(created_policies)} data pipeline alert policies")
            
        except Exception as e:
            logger.error(f"Failed to create data pipeline alerts: {str(e)}")
        
        return created_policies
    
    def create_all_alerts(self, notification_channels: List[str]) -> Dict[str, List[str]]:
        """
        Create all alert policies
        
        Args:
            notification_channels: List of notification channel names
            
        Returns:
            Dictionary mapping alert categories to policy names
        """
        
        all_alerts = {}
        
        try:
            all_alerts["cost"] = self.create_cost_alerts(notification_channels)
            all_alerts["performance"] = self.create_performance_alerts(notification_channels)
            all_alerts["availability"] = self.create_availability_alerts(notification_channels)
            all_alerts["ml_pipeline"] = self.create_ml_pipeline_alerts(notification_channels)
            all_alerts["data_pipeline"] = self.create_data_pipeline_alerts(notification_channels)
            
            total_policies = sum(len(policies) for policies in all_alerts.values())
            logger.info(f"Created {total_policies} alert policies across {len(all_alerts)} categories")
            
        except Exception as e:
            logger.error(f"Failed to create all alerts: {str(e)}")
        
        return all_alerts

# Usage example
if __name__ == "__main__":
    alert_manager = SentinelBertAlertManager("your-sentinelbert-project")
    
    # Example notification channels (would be actual channel names)
    notification_channels = [
        "projects/your-project/notificationChannels/123456789",
        "projects/your-project/notificationChannels/987654321"
    ]
    
    # Create all alerts
    alerts = alert_manager.create_all_alerts(notification_channels)
    print(f"Created alerts: {alerts}")
```

Let me continue with the remaining sections and complete this guide:

<function_calls>
<invoke name="str_replace_editor">
<parameter name="command">str_replace
---

## 🧪 Testing & Validation

### Step 9: Create Test Suite

```bash
# Create comprehensive monitoring test script
cat > gcp/monitoring/scripts/test-monitoring.sh << 'SCRIPT_EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}

echo "🧪 Testing monitoring and alerting setup for project: $PROJECT_ID"

# Test 1: Verify monitoring APIs are enabled
echo "🔍 Testing API enablement..."
for api in monitoring.googleapis.com logging.googleapis.com clouderrorreporting.googleapis.com; do
    if gcloud services list --enabled --filter="name:$api" --project=$PROJECT_ID | grep -q $api; then
        echo "✅ API $api is enabled"
    else
        echo "❌ API $api is not enabled"
    fi
done

# Test 2: Check notification channels
echo "📱 Testing notification channels..."
CHANNELS=$(gcloud alpha monitoring channels list --project=$PROJECT_ID --format="value(name)" | wc -l)
if [ $CHANNELS -gt 0 ]; then
    echo "✅ Found $CHANNELS notification channels"
else
    echo "❌ No notification channels found"
fi

# Test 3: Check alert policies
echo "🚨 Testing alert policies..."
POLICIES=$(gcloud alpha monitoring policies list --project=$PROJECT_ID --format="value(name)" | wc -l)
if [ $POLICIES -gt 0 ]; then
    echo "✅ Found $POLICIES alert policies"
else
    echo "❌ No alert policies found"
fi

# Test 4: Check uptime checks
echo "🔍 Testing uptime checks..."
UPTIME_CHECKS=$(gcloud monitoring uptime list --project=$PROJECT_ID --format="value(name)" | wc -l)
if [ $UPTIME_CHECKS -gt 0 ]; then
    echo "✅ Found $UPTIME_CHECKS uptime checks"
else
    echo "❌ No uptime checks found"
fi

# Test 5: Test log-based metrics
echo "📊 Testing log-based metrics..."
METRICS=$(gcloud logging metrics list --project=$PROJECT_ID --format="value(name)" | wc -l)
if [ $METRICS -gt 0 ]; then
    echo "✅ Found $METRICS log-based metrics"
else
    echo "❌ No log-based metrics found"
fi

# Test 6: Generate test alert
echo "🚨 Generating test alert..."
gcloud logging write test-log '{"message":"Test alert for monitoring validation","severity":"ERROR","test":true}' --severity=ERROR --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Test log entry created successfully"
else
    echo "❌ Failed to create test log entry"
fi

echo ""
echo "✅ Monitoring testing completed!"
echo "📋 Manual verification steps:"
echo "  1. Check Cloud Monitoring console for dashboards"
echo "  2. Verify alert notifications are received"
echo "  3. Test uptime check endpoints"
echo "  4. Review log entries in Cloud Logging"
SCRIPT_EOF

chmod +x gcp/monitoring/scripts/test-monitoring.sh
./gcp/monitoring/scripts/test-monitoring.sh your-sentinelbert-project
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Monitoring API Not Enabled

**Error**: `API [monitoring.googleapis.com] not enabled`

**Solution**:
```bash
# Enable monitoring APIs
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable clouderrorreporting.googleapis.com

# Verify enablement
gcloud services list --enabled --filter="name:monitoring"
```

#### Issue 2: Insufficient Permissions

**Error**: `Permission denied` when creating alert policies

**Solution**:
```bash
# Check current permissions
gcloud projects get-iam-policy your-project

# Add monitoring admin role
gcloud projects add-iam-policy-binding your-project \
    --member="user:your-email@domain.com" \
    --role="roles/monitoring.admin"
```

#### Issue 3: Notification Channel Creation Failed

**Problem**: Cannot create Slack or PagerDuty channels

**Solution**:
```bash
# Verify webhook URLs and integration keys
# For Slack: Test webhook URL manually
curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test message"}' \
    YOUR_SLACK_WEBHOOK_URL

# For PagerDuty: Verify integration key in PagerDuty console
```

#### Issue 4: High Monitoring Costs

**Problem**: Monitoring costs exceeding budget

**Solution**:
```bash
# Reduce log retention
gcloud logging buckets update _Default \
    --retention-days=7 \
    --location=global

# Implement log sampling
gcloud logging sinks create sampled-logs \
    bigquery.googleapis.com/projects/PROJECT/datasets/logs \
    --log-filter='sample(insertId, 0.1)'  # 10% sampling
```

#### Issue 5: Alert Fatigue

**Problem**: Too many alerts being generated

**Solution**:
```python
# Implement alert deduplication
alert_policy.alert_strategy = monitoring_v3.AlertPolicy.AlertStrategy(
    auto_close={"seconds": 3600},  # Auto-close after 1 hour
    notification_rate_limit={
        "period": {"seconds": 300},  # 5 minutes
    }
)
```

---

## 📞 Important Links & References

### 🔗 Essential Links

- **Cloud Monitoring Console**: https://console.cloud.google.com/monitoring
- **Cloud Logging Console**: https://console.cloud.google.com/logs
- **Error Reporting Console**: https://console.cloud.google.com/errors
- **Uptime Checks Console**: https://console.cloud.google.com/monitoring/uptime

### 📚 Documentation References

- **Cloud Monitoring Documentation**: https://cloud.google.com/monitoring/docs
- **Cloud Logging Documentation**: https://cloud.google.com/logging/docs
- **Alert Policies**: https://cloud.google.com/monitoring/alerts
- **Notification Channels**: https://cloud.google.com/monitoring/support/notification-options
- **SLA Monitoring**: https://cloud.google.com/monitoring/sli-slo
- **Cost Monitoring**: https://cloud.google.com/billing/docs/how-to/budgets
- **Pricing**: https://cloud.google.com/monitoring/pricing

### 🛠️ Tools & Resources

- **gcloud CLI**: https://cloud.google.com/sdk/gcloud/reference/monitoring
- **Python Client**: https://cloud.google.com/python/docs/reference/monitoring/latest
- **Monitoring Query Language**: https://cloud.google.com/monitoring/mql
- **Alerting Best Practices**: https://cloud.google.com/monitoring/alerts/best-practices

---

<div align="center">

**Next Steps**: Continue with [Security Configuration](./09-security-setup.md) to secure your infrastructure.

*Your comprehensive monitoring and alerting system is now configured with cost optimization and SLA tracking.*

</div>

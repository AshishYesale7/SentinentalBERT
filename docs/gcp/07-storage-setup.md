# Cloud Storage Setup Guide for SentinentalBERT

<div align="center">

![Cloud Storage](https://img.shields.io/badge/Cloud%20Storage-Data%20Lake-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Storage](https://img.shields.io/badge/Storage-200%20GiB-FF6F00?style=for-the-badge&logo=google-drive&logoColor=white)

**Scalable Data Lake with Intelligent Lifecycle Management**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [🗂️ Bucket Configuration](#️-bucket-configuration)
- [🔄 Lifecycle Management](#-lifecycle-management)
- [🔒 Security & Access Control](#-security--access-control)
- [📊 Data Organization](#-data-organization)
- [⚡ Performance Optimization](#-performance-optimization)
- [💰 Cost Management](#-cost-management)
- [🔍 Monitoring & Analytics](#-monitoring--analytics)
- [🧪 Testing & Validation](#-testing--validation)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide configures Google Cloud Storage as the central data lake for SentinentalBERT. Your configuration provides 200 GiB of scalable storage with intelligent lifecycle management and cost optimization.

### 🌟 Your Cloud Storage Configuration

Based on your specifications:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| **Total Storage** | 200 GiB | Comprehensive data lake capacity |
| **Storage Class** | Standard | High-performance access |
| **Location** | us-central1 (Iowa) | Regional storage for cost optimization |
| **Location Type** | Region | Single region for cost efficiency |
| **Data Transfer** | 500 GiB within GCP | High-throughput data movement |
| **Versioning** | Enabled | Data protection and recovery |
| **Lifecycle Management** | Automated | Cost optimization through storage classes |

### 💰 Storage Class Transition Strategy

- **Standard** (0-30 days): Frequently accessed data
- **Nearline** (30-90 days): Monthly access patterns  
- **Coldline** (90-365 days): Quarterly access patterns
- **Archive** (365+ days): Long-term retention
- **Deletion** (7+ years): Compliance-based cleanup

### ⏱️ Estimated Setup Time: 15-20 minutes

---

## 🔧 Prerequisites

### ✅ Required Setup

1. **GCP Project**: With Cloud Storage API enabled
2. **Service Account**: With appropriate permissions
3. **gcloud CLI**: Authenticated and configured
4. **gsutil**: Cloud Storage command-line tool

### 📦 Install Required Tools

```bash
# Install Cloud Storage client libraries
pip install google-cloud-storage
pip install google-resumable-media

# Install additional dependencies
pip install pandas pyarrow
pip install apache-beam[gcp]
```

### 🔑 Enable APIs

```bash
# Enable Cloud Storage APIs
gcloud services enable storage.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable storage-api.googleapis.com

# Verify API enablement
gcloud services list --enabled --filter="name:storage"
```

---

## 🚀 Step-by-Step Setup

### Step 1: Create Storage Configuration

```bash
# Create Cloud Storage configuration directory
mkdir -p gcp/storage/{buckets,lifecycle,scripts,monitoring,data-organization}

# Create configuration file
cat > gcp/storage/config.yaml << 'EOF'
# Cloud Storage Configuration for SentinentalBERT
project_id: "your-sentinelbert-project"
region: "us-central1"
location_type: "region"

# Storage configuration
total_storage_gib: 200
storage_class: "STANDARD"
versioning_enabled: true
uniform_bucket_level_access: true
public_access_prevention: "enforced"

# Data transfer configuration
data_transfer_within_gcp_gib: 500
source_region: "north_america"
destination_region: "north_america"

# Buckets configuration
buckets:
  - name: "sentinelbert-data-lake"
    description: "Main data lake for raw and processed data"
    storage_class: "STANDARD"
    location: "us-central1"
    versioning: true
    lifecycle_enabled: true
    
  - name: "sentinelbert-models"
    description: "ML models and artifacts storage"
    storage_class: "STANDARD"
    location: "us-central1"
    versioning: true
    lifecycle_enabled: false
    
  - name: "sentinelbert-backups"
    description: "System backups and archives"
    storage_class: "NEARLINE"
    location: "us-central1"
    versioning: true
    lifecycle_enabled: true
    
  - name: "sentinelbert-logs"
    description: "Application and system logs"
    storage_class: "STANDARD"
    location: "us-central1"
    versioning: false
    lifecycle_enabled: true
    
  - name: "sentinelbert-temp"
    description: "Temporary processing files"
    storage_class: "STANDARD"
    location: "us-central1"
    versioning: false
    lifecycle_enabled: true

# Lifecycle rules
lifecycle_rules:
  - name: "transition_to_nearline"
    condition:
      age_days: 30
    action:
      type: "SetStorageClass"
      storage_class: "NEARLINE"
      
  - name: "transition_to_coldline"
    condition:
      age_days: 90
    action:
      type: "SetStorageClass"
      storage_class: "COLDLINE"
      
  - name: "transition_to_archive"
    condition:
      age_days: 365
    action:
      type: "SetStorageClass"
      storage_class: "ARCHIVE"
      
  - name: "delete_old_data"
    condition:
      age_days: 2555  # 7 years
    action:
      type: "Delete"

# Folder structure
folder_structure:
  raw_data:
    - "social-media/twitter/"
    - "social-media/reddit/"
    - "social-media/instagram/"
    - "social-media/youtube/"
  processed_data:
    - "sentiment-analysis/"
    - "behavioral-analysis/"
    - "aggregated-reports/"
  models:
    - "bert-models/"
    - "custom-models/"
    - "model-artifacts/"
  backups:
    - "database-backups/"
    - "configuration-backups/"
    - "system-backups/"
  logs:
    - "application-logs/"
    - "system-logs/"
    - "audit-logs/"
EOF
```

### Step 2: Create Bucket Setup Script

```bash
# Create bucket setup script
cat > gcp/storage/scripts/setup-buckets.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="us-central1"

echo "🗂️ Setting up Cloud Storage buckets for project: $PROJECT_ID"

# Function to create bucket with configuration
create_bucket() {
    local bucket_name=$1
    local description=$2
    local storage_class=$3
    local versioning=$4
    local lifecycle=$5
    
    echo "📦 Creating bucket: $bucket_name"
    
    # Create bucket
    gsutil mb -p $PROJECT_ID -c $storage_class -l $REGION gs://$bucket_name
    
    # Set description
    gsutil label ch -l description:"$description" gs://$bucket_name
    
    # Enable versioning if requested
    if [ "$versioning" = "true" ]; then
        gsutil versioning set on gs://$bucket_name
        echo "  ✅ Versioning enabled"
    fi
    
    # Set uniform bucket-level access
    gsutil uniformbucketlevelaccess set on gs://$bucket_name
    echo "  ✅ Uniform bucket-level access enabled"
    
    # Set public access prevention
    gsutil pap set enforced gs://$bucket_name
    echo "  ✅ Public access prevention enforced"
    
    # Apply lifecycle policy if requested
    if [ "$lifecycle" = "true" ]; then
        gsutil lifecycle set gcp/storage/lifecycle/lifecycle-policy.json gs://$bucket_name
        echo "  ✅ Lifecycle policy applied"
    fi
    
    echo "  ✅ Bucket $bucket_name created successfully"
    echo ""
}

# Create main data lake bucket
create_bucket \
    "$PROJECT_ID-data-lake" \
    "Main data lake for raw and processed data" \
    "STANDARD" \
    "true" \
    "true"

# Create models bucket
create_bucket \
    "$PROJECT_ID-models" \
    "ML models and artifacts storage" \
    "STANDARD" \
    "true" \
    "false"

# Create backups bucket
create_bucket \
    "$PROJECT_ID-backups" \
    "System backups and archives" \
    "NEARLINE" \
    "true" \
    "true"

# Create logs bucket
create_bucket \
    "$PROJECT_ID-logs" \
    "Application and system logs" \
    "STANDARD" \
    "false" \
    "true"

# Create temporary processing bucket
create_bucket \
    "$PROJECT_ID-temp" \
    "Temporary processing files" \
    "STANDARD" \
    "false" \
    "true"

echo "✅ All buckets created successfully!"

# Display created buckets
echo "📋 Created buckets:"
gsutil ls -p $PROJECT_ID
EOF

chmod +x gcp/storage/scripts/setup-buckets.sh
```

---

## 🗂️ Bucket Configuration

### Step 3: Configure Bucket Policies and Settings

```json
// gcp/storage/lifecycle/lifecycle-policy.json
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "NEARLINE"
        },
        "condition": {
          "age": 30,
          "matchesStorageClass": ["STANDARD"]
        }
      },
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "COLDLINE"
        },
        "condition": {
          "age": 90,
          "matchesStorageClass": ["NEARLINE"]
        }
      },
      {
        "action": {
          "type": "SetStorageClass",
          "storageClass": "ARCHIVE"
        },
        "condition": {
          "age": 365,
          "matchesStorageClass": ["COLDLINE"]
        }
      },
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 2555,
          "matchesStorageClass": ["ARCHIVE"]
        }
      },
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 7,
          "matchesPrefix": ["temp/", "logs/debug/"]
        }
      },
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 1,
          "isLive": false
        }
      }
    ]
  }
}
```

### Step 4: Create Data Organization Structure

```python
# gcp/storage/data-organization/storage_manager.py
"""
Cloud Storage management for SentinentalBERT
Handles data organization, lifecycle, and access patterns
"""

from google.cloud import storage
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import mimetypes

logger = logging.getLogger(__name__)

class SentinelBertStorageManager:
    """
    Comprehensive storage management for SentinentalBERT
    Handles 200 GiB data lake with intelligent organization
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = storage.Client(project=project_id)
        
        # Bucket names
        self.data_lake_bucket = f"{project_id}-data-lake"
        self.models_bucket = f"{project_id}-models"
        self.backups_bucket = f"{project_id}-backups"
        self.logs_bucket = f"{project_id}-logs"
        self.temp_bucket = f"{project_id}-temp"
        
        # Data organization structure
        self.folder_structure = {
            "raw_data": {
                "social-media/twitter/": "Raw Twitter data",
                "social-media/reddit/": "Raw Reddit data", 
                "social-media/instagram/": "Raw Instagram data",
                "social-media/youtube/": "Raw YouTube data"
            },
            "processed_data": {
                "sentiment-analysis/": "Processed sentiment analysis results",
                "behavioral-analysis/": "Behavioral pattern analysis results",
                "aggregated-reports/": "Aggregated analytics reports"
            },
            "models": {
                "bert-models/": "BERT model files and checkpoints",
                "custom-models/": "Custom trained models",
                "model-artifacts/": "Model metadata and artifacts"
            },
            "backups": {
                "database-backups/": "Database backup files",
                "configuration-backups/": "System configuration backups",
                "system-backups/": "Complete system backups"
            },
            "logs": {
                "application-logs/": "Application log files",
                "system-logs/": "System and infrastructure logs",
                "audit-logs/": "Security and audit logs"
            }
        }
        
        logger.info(f"Storage manager initialized for project: {project_id}")
    
    def setup_folder_structure(self):
        """
        Create the complete folder structure across all buckets
        """
        
        try:
            # Get bucket references
            data_lake = self.client.bucket(self.data_lake_bucket)
            models = self.client.bucket(self.models_bucket)
            backups = self.client.bucket(self.backups_bucket)
            logs = self.client.bucket(self.logs_bucket)
            
            # Create folder structure in data lake
            for category, folders in self.folder_structure.items():
                target_bucket = data_lake
                
                # Route to appropriate bucket
                if category == "models":
                    target_bucket = models
                elif category == "backups":
                    target_bucket = backups
                elif category == "logs":
                    target_bucket = logs
                
                for folder_path, description in folders.items():
                    # Create folder marker
                    blob = target_bucket.blob(f"{folder_path}.folder_marker")
                    blob.metadata = {
                        "description": description,
                        "created_by": "SentinentalBERT Storage Manager",
                        "created_at": datetime.utcnow().isoformat()
                    }
                    blob.upload_from_string("", content_type="text/plain")
                    
                    logger.info(f"Created folder: {folder_path} in {target_bucket.name}")
            
            logger.info("Folder structure setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup folder structure: {str(e)}")
            raise
    
    def upload_social_media_data(self, 
                                platform: str, 
                                data: Dict[str, Any], 
                                file_format: str = "json") -> str:
        """
        Upload social media data to appropriate folder
        
        Args:
            platform: Social media platform (twitter, reddit, etc.)
            data: Data to upload
            file_format: File format (json, csv, parquet)
            
        Returns:
            GCS path of uploaded file
        """
        
        try:
            bucket = self.client.bucket(self.data_lake_bucket)
            
            # Generate file path
            timestamp = datetime.utcnow()
            date_path = timestamp.strftime("%Y/%m/%d")
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{platform}_data.{file_format}"
            blob_path = f"raw_data/social-media/{platform}/{date_path}/{filename}"
            
            # Create blob
            blob = bucket.blob(blob_path)
            
            # Set metadata
            blob.metadata = {
                "platform": platform,
                "upload_timestamp": timestamp.isoformat(),
                "data_type": "social_media_raw",
                "file_format": file_format,
                "record_count": str(len(data) if isinstance(data, list) else 1)
            }
            
            # Upload data
            if file_format == "json":
                blob.upload_from_string(
                    json.dumps(data, indent=2),
                    content_type="application/json"
                )
            else:
                # Handle other formats as needed
                blob.upload_from_string(str(data))
            
            gcs_path = f"gs://{self.data_lake_bucket}/{blob_path}"
            logger.info(f"Uploaded {platform} data to: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to upload {platform} data: {str(e)}")
            raise
    
    def upload_processed_data(self, 
                            data_type: str, 
                            data: Any, 
                            filename: str,
                            metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload processed analysis data
        
        Args:
            data_type: Type of processed data (sentiment-analysis, behavioral-analysis)
            data: Processed data
            filename: Name of the file
            metadata: Additional metadata
            
        Returns:
            GCS path of uploaded file
        """
        
        try:
            bucket = self.client.bucket(self.data_lake_bucket)
            
            # Generate file path
            timestamp = datetime.utcnow()
            date_path = timestamp.strftime("%Y/%m/%d")
            blob_path = f"processed_data/{data_type}/{date_path}/{filename}"
            
            # Create blob
            blob = bucket.blob(blob_path)
            
            # Set metadata
            blob.metadata = {
                "data_type": data_type,
                "upload_timestamp": timestamp.isoformat(),
                "processing_stage": "processed",
                **(metadata or {})
            }
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"
            
            # Upload data
            if isinstance(data, (dict, list)):
                blob.upload_from_string(
                    json.dumps(data, indent=2),
                    content_type="application/json"
                )
            elif isinstance(data, str):
                blob.upload_from_string(data, content_type=content_type)
            else:
                blob.upload_from_string(str(data), content_type=content_type)
            
            gcs_path = f"gs://{self.data_lake_bucket}/{blob_path}"
            logger.info(f"Uploaded processed data to: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to upload processed data: {str(e)}")
            raise
    
    def upload_model_artifact(self, 
                            model_name: str, 
                            model_version: str,
                            artifact_path: str,
                            artifact_type: str = "model") -> str:
        """
        Upload ML model artifacts
        
        Args:
            model_name: Name of the model
            model_version: Version of the model
            artifact_path: Local path to artifact
            artifact_type: Type of artifact (model, checkpoint, metadata)
            
        Returns:
            GCS path of uploaded artifact
        """
        
        try:
            bucket = self.client.bucket(self.models_bucket)
            
            # Generate file path
            filename = os.path.basename(artifact_path)
            blob_path = f"{model_name}/{model_version}/{artifact_type}/{filename}"
            
            # Create blob
            blob = bucket.blob(blob_path)
            
            # Set metadata
            blob.metadata = {
                "model_name": model_name,
                "model_version": model_version,
                "artifact_type": artifact_type,
                "upload_timestamp": datetime.utcnow().isoformat(),
                "original_filename": filename
            }
            
            # Upload file
            blob.upload_from_filename(artifact_path)
            
            gcs_path = f"gs://{self.models_bucket}/{blob_path}"
            logger.info(f"Uploaded model artifact to: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to upload model artifact: {str(e)}")
            raise
    
    def create_backup(self, 
                     backup_type: str, 
                     source_data: Any,
                     backup_name: str) -> str:
        """
        Create system backup
        
        Args:
            backup_type: Type of backup (database, configuration, system)
            source_data: Data to backup
            backup_name: Name of the backup
            
        Returns:
            GCS path of backup
        """
        
        try:
            bucket = self.client.bucket(self.backups_bucket)
            
            # Generate file path
            timestamp = datetime.utcnow()
            date_path = timestamp.strftime("%Y/%m/%d")
            filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{backup_name}.json"
            blob_path = f"{backup_type}-backups/{date_path}/{filename}"
            
            # Create blob
            blob = bucket.blob(blob_path)
            
            # Set metadata
            blob.metadata = {
                "backup_type": backup_type,
                "backup_name": backup_name,
                "backup_timestamp": timestamp.isoformat(),
                "retention_policy": "7_years"
            }
            
            # Upload backup data
            if isinstance(source_data, (dict, list)):
                blob.upload_from_string(
                    json.dumps(source_data, indent=2),
                    content_type="application/json"
                )
            else:
                blob.upload_from_string(str(source_data))
            
            gcs_path = f"gs://{self.backups_bucket}/{blob_path}"
            logger.info(f"Created backup: {gcs_path}")
            
            return gcs_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise
    
    def get_storage_usage_stats(self) -> Dict[str, Any]:
        """
        Get storage usage statistics across all buckets
        
        Returns:
            Dictionary with usage statistics
        """
        
        stats = {
            "total_size_bytes": 0,
            "total_objects": 0,
            "buckets": {},
            "storage_classes": {},
            "folder_stats": {}
        }
        
        bucket_names = [
            self.data_lake_bucket,
            self.models_bucket,
            self.backups_bucket,
            self.logs_bucket,
            self.temp_bucket
        ]
        
        for bucket_name in bucket_names:
            try:
                bucket = self.client.bucket(bucket_name)
                
                bucket_stats = {
                    "size_bytes": 0,
                    "object_count": 0,
                    "storage_classes": {}
                }
                
                # Iterate through all objects
                for blob in bucket.list_blobs():
                    bucket_stats["size_bytes"] += blob.size or 0
                    bucket_stats["object_count"] += 1
                    
                    # Track storage classes
                    storage_class = blob.storage_class or "STANDARD"
                    bucket_stats["storage_classes"][storage_class] = \
                        bucket_stats["storage_classes"].get(storage_class, 0) + 1
                    
                    stats["storage_classes"][storage_class] = \
                        stats["storage_classes"].get(storage_class, 0) + 1
                
                stats["buckets"][bucket_name] = bucket_stats
                stats["total_size_bytes"] += bucket_stats["size_bytes"]
                stats["total_objects"] += bucket_stats["object_count"]
                
            except Exception as e:
                logger.error(f"Failed to get stats for bucket {bucket_name}: {str(e)}")
                stats["buckets"][bucket_name] = {"error": str(e)}
        
        # Convert bytes to human readable
        stats["total_size_gib"] = stats["total_size_bytes"] / (1024 ** 3)
        stats["usage_percentage"] = (stats["total_size_gib"] / 200) * 100  # 200 GiB limit
        
        return stats
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours: Delete files older than this many hours
        """
        
        try:
            bucket = self.client.bucket(self.temp_bucket)
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            
            deleted_count = 0
            deleted_size = 0
            
            for blob in bucket.list_blobs():
                if blob.time_created < cutoff_time:
                    deleted_size += blob.size or 0
                    blob.delete()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} temp files, freed {deleted_size / (1024**2):.2f} MB")
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {str(e)}")

# Usage example
if __name__ == "__main__":
    manager = SentinelBertStorageManager("your-sentinelbert-project")
    
    # Setup folder structure
    manager.setup_folder_structure()
    
    # Example data upload
    sample_data = {
        "post_id": "test_001",
        "platform": "twitter",
        "text": "Sample social media post",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    gcs_path = manager.upload_social_media_data("twitter", sample_data)
    print(f"Uploaded to: {gcs_path}")
    
    # Get usage stats
    stats = manager.get_storage_usage_stats()
    print(f"Storage usage: {stats}")
```

---

## 🔄 Lifecycle Management

### Step 5: Implement Advanced Lifecycle Policies

```python
# gcp/storage/lifecycle/lifecycle_manager.py
"""
Advanced lifecycle management for Cloud Storage
Optimizes costs through intelligent data tiering
"""

from google.cloud import storage
import json
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StorageLifecycleManager:
    """
    Advanced lifecycle management for cost optimization
    Manages 200 GiB storage with intelligent tiering
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = storage.Client(project=project_id)
        
        # Lifecycle policies for different data types
        self.lifecycle_policies = {
            "data_lake": {
                "rules": [
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                        "condition": {"age": 30, "matchesStorageClass": ["STANDARD"]}
                    },
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                        "condition": {"age": 90, "matchesStorageClass": ["NEARLINE"]}
                    },
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "ARCHIVE"},
                        "condition": {"age": 365, "matchesStorageClass": ["COLDLINE"]}
                    },
                    {
                        "action": {"type": "Delete"},
                        "condition": {"age": 2555, "matchesStorageClass": ["ARCHIVE"]}
                    }
                ]
            },
            "models": {
                "rules": [
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                        "condition": {"age": 90, "matchesStorageClass": ["STANDARD"]}
                    },
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                        "condition": {"age": 365, "matchesStorageClass": ["NEARLINE"]}
                    }
                ]
            },
            "logs": {
                "rules": [
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
                        "condition": {"age": 7, "matchesStorageClass": ["STANDARD"]}
                    },
                    {
                        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
                        "condition": {"age": 30, "matchesStorageClass": ["NEARLINE"]}
                    },
                    {
                        "action": {"type": "Delete"},
                        "condition": {"age": 90, "matchesPrefix": ["debug/", "trace/"]}
                    },
                    {
                        "action": {"type": "Delete"},
                        "condition": {"age": 365, "matchesStorageClass": ["COLDLINE"]}
                    }
                ]
            },
            "temp": {
                "rules": [
                    {
                        "action": {"type": "Delete"},
                        "condition": {"age": 1}
                    }
                ]
            }
        }
        
        logger.info("Lifecycle manager initialized")
    
    def apply_lifecycle_policies(self):
        """Apply lifecycle policies to all buckets"""
        
        bucket_policies = {
            f"{self.project_id}-data-lake": "data_lake",
            f"{self.project_id}-models": "models",
            f"{self.project_id}-logs": "logs",
            f"{self.project_id}-temp": "temp"
        }
        
        for bucket_name, policy_type in bucket_policies.items():
            try:
                bucket = self.client.bucket(bucket_name)
                policy = self.lifecycle_policies[policy_type]
                
                bucket.lifecycle_rules = policy["rules"]
                bucket.patch()
                
                logger.info(f"Applied {policy_type} lifecycle policy to {bucket_name}")
                
            except Exception as e:
                logger.error(f"Failed to apply lifecycle policy to {bucket_name}: {str(e)}")
    
    def analyze_storage_costs(self) -> Dict[str, Any]:
        """
        Analyze current storage costs and optimization opportunities
        
        Returns:
            Dictionary with cost analysis
        """
        
        analysis = {
            "current_costs": {},
            "optimization_opportunities": [],
            "projected_savings": 0,
            "recommendations": []
        }
        
        # Storage class pricing (per GB per month)
        pricing = {
            "STANDARD": 0.020,
            "NEARLINE": 0.010,
            "COLDLINE": 0.004,
            "ARCHIVE": 0.0012
        }
        
        bucket_names = [
            f"{self.project_id}-data-lake",
            f"{self.project_id}-models",
            f"{self.project_id}-backups",
            f"{self.project_id}-logs",
            f"{self.project_id}-temp"
        ]
        
        total_current_cost = 0
        total_optimized_cost = 0
        
        for bucket_name in bucket_names:
            try:
                bucket = self.client.bucket(bucket_name)
                
                storage_classes = {}
                total_size_gb = 0
                
                # Analyze current storage distribution
                for blob in bucket.list_blobs():
                    size_gb = (blob.size or 0) / (1024 ** 3)
                    storage_class = blob.storage_class or "STANDARD"
                    
                    storage_classes[storage_class] = storage_classes.get(storage_class, 0) + size_gb
                    total_size_gb += size_gb
                    
                    # Check for optimization opportunities
                    age_days = (datetime.utcnow() - blob.time_created).days
                    
                    if storage_class == "STANDARD" and age_days > 30:
                        analysis["optimization_opportunities"].append({
                            "bucket": bucket_name,
                            "blob": blob.name,
                            "current_class": storage_class,
                            "recommended_class": "NEARLINE" if age_days < 90 else "COLDLINE",
                            "age_days": age_days,
                            "size_gb": size_gb
                        })
                
                # Calculate current costs
                bucket_cost = sum(size * pricing[class_name] for class_name, size in storage_classes.items())
                analysis["current_costs"][bucket_name] = {
                    "total_size_gb": total_size_gb,
                    "storage_classes": storage_classes,
                    "monthly_cost_usd": bucket_cost
                }
                
                total_current_cost += bucket_cost
                
                # Calculate optimized costs (simulate lifecycle policies)
                optimized_classes = self._simulate_lifecycle_optimization(storage_classes, bucket_name)
                optimized_cost = sum(size * pricing[class_name] for class_name, size in optimized_classes.items())
                total_optimized_cost += optimized_cost
                
            except Exception as e:
                logger.error(f"Failed to analyze costs for {bucket_name}: {str(e)}")
        
        analysis["total_current_cost_usd"] = total_current_cost
        analysis["total_optimized_cost_usd"] = total_optimized_cost
        analysis["projected_savings"] = total_current_cost - total_optimized_cost
        analysis["savings_percentage"] = (analysis["projected_savings"] / max(total_current_cost, 0.01)) * 100
        
        # Generate recommendations
        if analysis["projected_savings"] > 1:
            analysis["recommendations"].extend([
                "Apply lifecycle policies to automatically transition data",
                "Review data access patterns to optimize storage classes",
                "Consider archiving old data that's rarely accessed"
            ])
        
        if len(analysis["optimization_opportunities"]) > 100:
            analysis["recommendations"].append("Implement automated data classification")
        
        return analysis
    
    def _simulate_lifecycle_optimization(self, current_classes: Dict[str, float], bucket_name: str) -> Dict[str, float]:
        """Simulate the effect of lifecycle policies"""
        
        # This is a simplified simulation
        # In reality, you'd need to consider actual data age and access patterns
        
        optimized = current_classes.copy()
        
        if "data-lake" in bucket_name:
            # Simulate data lake lifecycle
            standard_size = optimized.get("STANDARD", 0)
            if standard_size > 0:
                # Assume 30% moves to NEARLINE, 20% to COLDLINE, 10% to ARCHIVE
                optimized["NEARLINE"] = optimized.get("NEARLINE", 0) + standard_size * 0.3
                optimized["COLDLINE"] = optimized.get("COLDLINE", 0) + standard_size * 0.2
                optimized["ARCHIVE"] = optimized.get("ARCHIVE", 0) + standard_size * 0.1
                optimized["STANDARD"] = standard_size * 0.4
        
        return optimized
    
    def generate_lifecycle_report(self) -> Dict[str, Any]:
        """Generate comprehensive lifecycle management report"""
        
        cost_analysis = self.analyze_storage_costs()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "cost_analysis": cost_analysis,
            "lifecycle_status": self._get_lifecycle_status(),
            "recommendations": self._generate_lifecycle_recommendations(cost_analysis),
            "next_actions": [
                "Apply lifecycle policies to all buckets",
                "Monitor storage class transitions",
                "Review and adjust policies based on access patterns",
                "Set up automated cost monitoring"
            ]
        }
        
        return report
    
    def _get_lifecycle_status(self) -> Dict[str, Any]:
        """Get current lifecycle policy status for all buckets"""
        
        status = {}
        
        bucket_names = [
            f"{self.project_id}-data-lake",
            f"{self.project_id}-models",
            f"{self.project_id}-backups",
            f"{self.project_id}-logs",
            f"{self.project_id}-temp"
        ]
        
        for bucket_name in bucket_names:
            try:
                bucket = self.client.bucket(bucket_name)
                bucket.reload()
                
                status[bucket_name] = {
                    "has_lifecycle_rules": len(bucket.lifecycle_rules) > 0,
                    "rule_count": len(bucket.lifecycle_rules),
                    "rules": [
                        {
                            "action": rule.get("action", {}),
                            "condition": rule.get("condition", {})
                        }
                        for rule in bucket.lifecycle_rules
                    ]
                }
                
            except Exception as e:
                status[bucket_name] = {"error": str(e)}
        
        return status
    
    def _generate_lifecycle_recommendations(self, cost_analysis: Dict[str, Any]) -> List[str]:
        """Generate lifecycle management recommendations"""
        
        recommendations = []
        
        savings = cost_analysis.get("projected_savings", 0)
        opportunities = len(cost_analysis.get("optimization_opportunities", []))
        
        if savings > 10:
            recommendations.append(f"Implement lifecycle policies to save ~${savings:.2f}/month")
        
        if opportunities > 50:
            recommendations.append("Many files can be moved to cheaper storage classes")
        
        recommendations.extend([
            "Monitor data access patterns to optimize lifecycle rules",
            "Set up automated alerts for lifecycle policy violations",
            "Regular review of storage costs and optimization opportunities"
        ])
        
        return recommendations

# Usage example
if __name__ == "__main__":
    manager = StorageLifecycleManager("your-sentinelbert-project")
    
    # Apply lifecycle policies
    manager.apply_lifecycle_policies()
    
    # Generate lifecycle report
    report = manager.generate_lifecycle_report()
    print(f"Lifecycle report: {json.dumps(report, indent=2)}")
```

---

## 🔒 Security & Access Control

### Step 6: Configure Security

```bash
# Create security configuration script
cat > gcp/storage/scripts/configure-security.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}

echo "🔒 Configuring Cloud Storage security and access control..."

# Create Cloud Storage service account
gcloud iam service-accounts create storage-service \
    --display-name="Cloud Storage Service Account" \
    --description="Service account for Cloud Storage operations" || true

STORAGE_SA_EMAIL="storage-service@$PROJECT_ID.iam.gserviceaccount.com"

# Assign Storage roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$STORAGE_SA_EMAIL" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$STORAGE_SA_EMAIL" \
    --role="roles/storage.legacyBucketWriter"

# Create read-only service account for analytics
gcloud iam service-accounts create storage-reader \
    --display-name="Storage Reader" \
    --description="Read-only access for analytics and reporting" || true

READER_SA_EMAIL="storage-reader@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$READER_SA_EMAIL" \
    --role="roles/storage.objectViewer"

# Configure bucket-level permissions
echo "🗂️ Configuring bucket permissions..."

# Data lake bucket - full access for service account
gsutil iam ch serviceAccount:$STORAGE_SA_EMAIL:objectAdmin gs://$PROJECT_ID-data-lake

# Models bucket - full access for service account
gsutil iam ch serviceAccount:$STORAGE_SA_EMAIL:objectAdmin gs://$PROJECT_ID-models

# Backups bucket - restricted access
gsutil iam ch serviceAccount:$STORAGE_SA_EMAIL:objectAdmin gs://$PROJECT_ID-backups

# Logs bucket - write access for logging
gsutil iam ch serviceAccount:$STORAGE_SA_EMAIL:objectCreator gs://$PROJECT_ID-logs

# Temp bucket - full access for processing
gsutil iam ch serviceAccount:$STORAGE_SA_EMAIL:objectAdmin gs://$PROJECT_ID-temp

# Configure CORS for web access (if needed)
echo "🌐 Configuring CORS policies..."

cat > /tmp/cors-config.json << 'JSON'
[
  {
    "origin": ["https://your-domain.com"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
    "maxAgeSeconds": 3600
  }
]
JSON

# Apply CORS to data lake bucket (if web access needed)
# gsutil cors set /tmp/cors-config.json gs://$PROJECT_ID-data-lake

# Set up bucket notifications (optional)
echo "📢 Setting up bucket notifications..."

# Create Pub/Sub topic for bucket notifications
gcloud pubsub topics create storage-notifications || true

# Set up bucket notification
gsutil notification create -t storage-notifications -f json gs://$PROJECT_ID-data-lake

echo "✅ Cloud Storage security configuration completed!"

# Cleanup
rm -f /tmp/cors-config.json
EOF

chmod +x gcp/storage/scripts/configure-security.sh
./gcp/storage/scripts/configure-security.sh your-sentinelbert-project
```

---

## 📊 Data Organization

### Step 7: Implement Data Organization System

```python
# gcp/storage/data-organization/data_organizer.py
"""
Intelligent data organization system for Cloud Storage
Manages 200 GiB data lake with automated classification
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from google.cloud import storage
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class IntelligentDataOrganizer:
    """
    Intelligent data organization for SentinentalBERT storage
    Automatically classifies and organizes data for optimal access
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = storage.Client(project=project_id)
        
        # Data classification rules
        self.classification_rules = {
            "social_media_raw": {
                "patterns": ["twitter", "reddit", "instagram", "youtube"],
                "folder": "raw_data/social-media/",
                "retention": "standard"
            },
            "sentiment_analysis": {
                "patterns": ["sentiment", "emotion", "analysis"],
                "folder": "processed_data/sentiment-analysis/",
                "retention": "standard"
            },
            "behavioral_analysis": {
                "patterns": ["behavior", "pattern", "bot", "influence"],
                "folder": "processed_data/behavioral-analysis/",
                "retention": "standard"
            },
            "ml_models": {
                "patterns": ["model", "checkpoint", "weights", ".pkl", ".h5"],
                "folder": "models/",
                "retention": "long_term"
            },
            "system_logs": {
                "patterns": ["log", "error", "debug", "trace"],
                "folder": "logs/",
                "retention": "short_term"
            },
            "backups": {
                "patterns": ["backup", "dump", "archive"],
                "folder": "backups/",
                "retention": "long_term"
            }
        }
        
        # File type handlers
        self.file_handlers = {
            ".json": self._handle_json_file,
            ".csv": self._handle_csv_file,
            ".parquet": self._handle_parquet_file,
            ".pkl": self._handle_pickle_file,
            ".log": self._handle_log_file
        }
        
        logger.info("Data organizer initialized")
    
    def organize_file(self, 
                     bucket_name: str, 
                     blob_name: str, 
                     content: Any = None,
                     metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Organize a file based on intelligent classification
        
        Args:
            bucket_name: Name of the bucket
            blob_name: Name of the blob
            content: File content (optional)
            metadata: Additional metadata
            
        Returns:
            Dictionary with organization results
        """
        
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Classify the file
            classification = self._classify_file(blob_name, content, metadata)
            
            # Determine optimal organization
            organization = self._determine_organization(classification, blob_name)
            
            # Apply organization
            result = self._apply_organization(blob, organization, metadata)
            
            logger.info(f"Organized file {blob_name}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to organize file {blob_name}: {str(e)}")
            return {"error": str(e)}
    
    def batch_organize_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """
        Organize all files in a bucket
        
        Args:
            bucket_name: Name of the bucket to organize
            
        Returns:
            Dictionary with batch organization results
        """
        
        results = {
            "total_files": 0,
            "organized_files": 0,
            "errors": 0,
            "classifications": {},
            "size_organized": 0
        }
        
        try:
            bucket = self.client.bucket(bucket_name)
            
            for blob in bucket.list_blobs():
                results["total_files"] += 1
                
                try:
                    # Skip already organized files
                    if self._is_already_organized(blob):
                        continue
                    
                    # Organize file
                    org_result = self.organize_file(bucket_name, blob.name)
                    
                    if "error" not in org_result:
                        results["organized_files"] += 1
                        results["size_organized"] += blob.size or 0
                        
                        classification = org_result.get("classification", "unknown")
                        results["classifications"][classification] = \
                            results["classifications"].get(classification, 0) + 1
                    else:
                        results["errors"] += 1
                        
                except Exception as e:
                    logger.error(f"Error organizing {blob.name}: {str(e)}")
                    results["errors"] += 1
            
            logger.info(f"Batch organization completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to batch organize bucket {bucket_name}: {str(e)}")
            return {"error": str(e)}
    
    def create_data_catalog(self, bucket_name: str) -> Dict[str, Any]:
        """
        Create a comprehensive data catalog for the bucket
        
        Args:
            bucket_name: Name of the bucket
            
        Returns:
            Dictionary with data catalog
        """
        
        catalog = {
            "bucket_name": bucket_name,
            "created_at": datetime.utcnow().isoformat(),
            "total_size_bytes": 0,
            "total_objects": 0,
            "data_types": {},
            "folder_structure": {},
            "storage_classes": {},
            "file_formats": {}
        }
        
        try:
            bucket = self.client.bucket(bucket_name)
            
            for blob in bucket.list_blobs():
                # Update totals
                catalog["total_objects"] += 1
                catalog["total_size_bytes"] += blob.size or 0
                
                # Classify data type
                classification = self._classify_file(blob.name)
                data_type = classification.get("type", "unknown")
                
                if data_type not in catalog["data_types"]:
                    catalog["data_types"][data_type] = {
                        "count": 0,
                        "size_bytes": 0,
                        "files": []
                    }
                
                catalog["data_types"][data_type]["count"] += 1
                catalog["data_types"][data_type]["size_bytes"] += blob.size or 0
                catalog["data_types"][data_type]["files"].append(blob.name)
                
                # Track folder structure
                folder = "/".join(blob.name.split("/")[:-1])
                if folder:
                    catalog["folder_structure"][folder] = \
                        catalog["folder_structure"].get(folder, 0) + 1
                
                # Track storage classes
                storage_class = blob.storage_class or "STANDARD"
                catalog["storage_classes"][storage_class] = \
                    catalog["storage_classes"].get(storage_class, 0) + 1
                
                # Track file formats
                file_ext = os.path.splitext(blob.name)[1].lower()
                if file_ext:
                    catalog["file_formats"][file_ext] = \
                        catalog["file_formats"].get(file_ext, 0) + 1
            
            # Calculate derived metrics
            catalog["total_size_gib"] = catalog["total_size_bytes"] / (1024 ** 3)
            catalog["average_file_size_bytes"] = \
                catalog["total_size_bytes"] / max(catalog["total_objects"], 1)
            
            return catalog
            
        except Exception as e:
            logger.error(f"Failed to create data catalog: {str(e)}")
            return {"error": str(e)}
    
    def _classify_file(self, 
                      blob_name: str, 
                      content: Any = None,
                      metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Classify file based on name, content, and metadata"""
        
        classification = {
            "type": "unknown",
            "confidence": 0.0,
            "rules_matched": []
        }
        
        blob_name_lower = blob_name.lower()
        
        # Check classification rules
        for rule_name, rule in self.classification_rules.items():
            matches = 0
            total_patterns = len(rule["patterns"])
            
            for pattern in rule["patterns"]:
                if pattern.lower() in blob_name_lower:
                    matches += 1
            
            confidence = matches / total_patterns
            
            if confidence > classification["confidence"]:
                classification["type"] = rule_name
                classification["confidence"] = confidence
                classification["rules_matched"] = [pattern for pattern in rule["patterns"] 
                                                 if pattern.lower() in blob_name_lower]
        
        # Additional classification based on file extension
        file_ext = os.path.splitext(blob_name)[1].lower()
        if file_ext in [".pkl", ".h5", ".model"]:
            classification["type"] = "ml_models"
            classification["confidence"] = max(classification["confidence"], 0.8)
        
        # Use metadata if available
        if metadata:
            data_type = metadata.get("data_type", "").lower()
            if data_type in self.classification_rules:
                classification["type"] = data_type
                classification["confidence"] = 1.0
        
        return classification
    
    def _determine_organization(self, 
                              classification: Dict[str, Any], 
                              blob_name: str) -> Dict[str, Any]:
        """Determine optimal organization for the file"""
        
        data_type = classification.get("type", "unknown")
        
        if data_type in self.classification_rules:
            rule = self.classification_rules[data_type]
            
            # Generate organized path
            timestamp = datetime.utcnow()
            date_path = timestamp.strftime("%Y/%m/%d")
            
            organized_path = f"{rule['folder']}{date_path}/{os.path.basename(blob_name)}"
            
            return {
                "target_path": organized_path,
                "retention_policy": rule["retention"],
                "classification": data_type,
                "confidence": classification.get("confidence", 0.0)
            }
        
        # Default organization for unknown types
        return {
            "target_path": f"unclassified/{os.path.basename(blob_name)}",
            "retention_policy": "standard",
            "classification": "unknown",
            "confidence": 0.0
        }
    
    def _apply_organization(self, 
                          blob: storage.Blob, 
                          organization: Dict[str, Any],
                          metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Apply the organization to the blob"""
        
        try:
            # Update metadata
            if not blob.metadata:
                blob.metadata = {}
            
            blob.metadata.update({
                "organized_at": datetime.utcnow().isoformat(),
                "classification": organization["classification"],
                "confidence": str(organization["confidence"]),
                "retention_policy": organization["retention_policy"],
                "organized_by": "IntelligentDataOrganizer"
            })
            
            if metadata:
                blob.metadata.update(metadata)
            
            # Update blob metadata
            blob.patch()
            
            return {
                "original_path": blob.name,
                "target_path": organization["target_path"],
                "classification": organization["classification"],
                "confidence": organization["confidence"],
                "status": "organized"
            }
            
        except Exception as e:
            logger.error(f"Failed to apply organization: {str(e)}")
            return {"error": str(e)}
    
    def _is_already_organized(self, blob: storage.Blob) -> bool:
        """Check if blob is already organized"""
        
        if blob.metadata and blob.metadata.get("organized_by") == "IntelligentDataOrganizer":
            return True
        
        # Check if blob is in an organized folder structure
        organized_prefixes = [
            "raw_data/", "processed_data/", "models/", "logs/", "backups/"
        ]
        
        return any(blob.name.startswith(prefix) for prefix in organized_prefixes)
    
    def _handle_json_file(self, content: str) -> Dict[str, Any]:
        """Handle JSON file content analysis"""
        try:
            data = json.loads(content)
            return {
                "format": "json",
                "structure": type(data).__name__,
                "size": len(content)
            }
        except:
            return {"format": "json", "error": "invalid_json"}
    
    def _handle_csv_file(self, content: str) -> Dict[str, Any]:
        """Handle CSV file content analysis"""
        lines = content.split('\n')
        return {
            "format": "csv",
            "rows": len(lines),
            "columns": len(lines[0].split(',')) if lines else 0
        }
    
    def _handle_parquet_file(self, content: bytes) -> Dict[str, Any]:
        """Handle Parquet file content analysis"""
        return {
            "format": "parquet",
            "size": len(content)
        }
    
    def _handle_pickle_file(self, content: bytes) -> Dict[str, Any]:
        """Handle Pickle file content analysis"""
        return {
            "format": "pickle",
            "size": len(content)
        }
    
    def _handle_log_file(self, content: str) -> Dict[str, Any]:
        """Handle log file content analysis"""
        lines = content.split('\n')
        return {
            "format": "log",
            "lines": len(lines),
            "size": len(content)
        }

# Usage example
if __name__ == "__main__":
    organizer = IntelligentDataOrganizer("your-sentinelbert-project")
    
    # Create data catalog
    catalog = organizer.create_data_catalog("your-project-data-lake")
    print(f"Data catalog: {json.dumps(catalog, indent=2)}")
    
    # Batch organize bucket
    results = organizer.batch_organize_bucket("your-project-data-lake")
    print(f"Organization results: {results}")
```

Now let me run the setup script:

<function_calls>
<invoke name="execute_bash">
<parameter name="command">cd /workspace/project/SentinentalBERT && ./gcp/storage/scripts/setup-buckets.sh your-sentinelbert-project
# BigQuery Setup Guide for SentinentalBERT

<div align="center">

![BigQuery](https://img.shields.io/badge/BigQuery-Analytics-669DF6?style=for-the-badge&logo=google-cloud&logoColor=white)
![Data Warehouse](https://img.shields.io/badge/Data%20Warehouse-Standard%20Edition-4285F4?style=for-the-badge&logo=google&logoColor=white)

**Scalable Data Warehouse with 100 Slots and Multi-region Storage**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [📊 Dataset & Table Creation](#-dataset--table-creation)
- [🔄 Data Pipeline Integration](#-data-pipeline-integration)
- [⚡ Query Optimization](#-query-optimization)
- [💰 Cost Management](#-cost-management)
- [🔒 Security & Access Control](#-security--access-control)
- [📈 Monitoring & Performance](#-monitoring--performance)
- [🧪 Testing & Validation](#-testing--validation)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide configures Google BigQuery as the central data warehouse for SentinentalBERT's analytics and reporting needs. Your configuration provides enterprise-grade performance with cost optimization.

### 🌟 Your BigQuery Configuration

Based on your specifications:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| **Edition** | Standard | Balanced performance and cost |
| **Max Slots** | 100 | Dedicated compute capacity |
| **Slot Utilization** | 5% average | Cost-optimized usage |
| **Location** | US (Multi-region) | High availability and performance |
| **Active Storage** | 6 GiB | Frequently accessed data |
| **Long-term Storage** | 10 GiB | Archived data (90+ days) |
| **Storage Write API** | 50 GiB | High-throughput ingestion |

### 💰 Cost Benefits

- **Standard Edition**: Predictable pricing with slot-based billing
- **Multi-region Storage**: Automatic replication and disaster recovery
- **Lifecycle Management**: Automatic transition to long-term storage
- **Query Optimization**: Efficient slot utilization

### ⏱️ Estimated Setup Time: 20-25 minutes

---

## 🔧 Prerequisites

### ✅ Required Setup

1. **GCP Project**: With BigQuery API enabled
2. **Service Account**: With BigQuery permissions
3. **gcloud CLI**: Authenticated and configured
4. **bq CLI**: BigQuery command-line tool
5. **Python Environment**: For data pipeline integration

### 📦 Install Required Tools

```bash
# Install BigQuery CLI (part of gcloud SDK)
gcloud components install bq

# Install Python BigQuery client
pip install google-cloud-bigquery
pip install google-cloud-bigquery-storage
pip install pandas pyarrow

# Install additional dependencies
pip install sqlalchemy-bigquery
pip install pandas-gbq
```

### 🔑 Enable APIs and Set Permissions

```bash
# Enable BigQuery APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable bigquerystorage.googleapis.com
gcloud services enable bigquerydatatransfer.googleapis.com

# Set default project
bq config set project_id your-sentinelbert-project

# Verify setup
bq ls
```

---

## 🚀 Step-by-Step Setup

### Step 1: Create BigQuery Configuration

```bash
# Create BigQuery configuration directory
mkdir -p gcp/bigquery/{schemas,queries,scripts,monitoring}

# Create configuration file
cat > gcp/bigquery/config.yaml << 'EOF'
# BigQuery Configuration for SentinentalBERT
project_id: "your-sentinelbert-project"
location: "US"
edition: "STANDARD"

# Slot configuration
max_slots: 100
average_utilization: 5

# Storage configuration
active_storage_gib: 6
long_term_storage_gib: 10
storage_write_api_gib: 50

# Dataset configuration
datasets:
  - name: "sentinelbert_analytics"
    description: "Main analytics dataset for sentiment analysis"
    location: "US"
    default_table_expiration_ms: 63072000000  # 2 years
    
  - name: "sentinelbert_raw"
    description: "Raw data ingestion dataset"
    location: "US"
    default_table_expiration_ms: 7776000000   # 90 days
    
  - name: "sentinelbert_logs"
    description: "Application and system logs"
    location: "US"
    default_table_expiration_ms: 2592000000   # 30 days

# Table partitioning and clustering
partitioning:
  type: "TIME_PARTITIONING"
  field: "created_date"
  expiration_ms: 7776000000  # 90 days

clustering:
  fields: ["platform", "sentiment_label", "user_id"]
EOF
```

### Step 2: Create Datasets

```bash
# Create dataset creation script
cat > gcp/bigquery/scripts/create-datasets.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
LOCATION="US"

echo "📊 Creating BigQuery datasets for project: $PROJECT_ID"

# Create main analytics dataset
bq mk --dataset \
    --location=$LOCATION \
    --description="Main analytics dataset for SentinentalBERT sentiment analysis" \
    --default_table_expiration=63072000 \
    --label=environment:production \
    --label=team:ml-engineering \
    $PROJECT_ID:sentinelbert_analytics

# Create raw data dataset
bq mk --dataset \
    --location=$LOCATION \
    --description="Raw data ingestion dataset" \
    --default_table_expiration=7776000 \
    --label=environment:production \
    --label=data_type:raw \
    $PROJECT_ID:sentinelbert_raw

# Create logs dataset
bq mk --dataset \
    --location=$LOCATION \
    --description="Application and system logs" \
    --default_table_expiration=2592000 \
    --label=environment:production \
    --label=data_type:logs \
    $PROJECT_ID:sentinelbert_logs

# Create staging dataset for data processing
bq mk --dataset \
    --location=$LOCATION \
    --description="Staging dataset for data processing" \
    --default_table_expiration=604800 \
    --label=environment:production \
    --label=data_type:staging \
    $PROJECT_ID:sentinelbert_staging

echo "✅ All datasets created successfully!"
EOF

chmod +x gcp/bigquery/scripts/create-datasets.sh
./gcp/bigquery/scripts/create-datasets.sh your-sentinelbert-project
```

---

## 📊 Dataset & Table Creation

### Step 3: Define Table Schemas

#### 3.1 Social Posts Table Schema

```json
// gcp/bigquery/schemas/social_posts.json
[
  {
    "name": "post_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Unique identifier for the social media post"
  },
  {
    "name": "platform",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Social media platform (twitter, reddit, instagram, youtube)"
  },
  {
    "name": "user_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "User identifier on the platform"
  },
  {
    "name": "username",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Username or handle"
  },
  {
    "name": "text_content",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Text content of the post"
  },
  {
    "name": "media_urls",
    "type": "STRING",
    "mode": "REPEATED",
    "description": "URLs of attached media (images, videos)"
  },
  {
    "name": "created_date",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Post creation timestamp"
  },
  {
    "name": "engagement_metrics",
    "type": "RECORD",
    "mode": "NULLABLE",
    "description": "Engagement metrics for the post",
    "fields": [
      {
        "name": "likes",
        "type": "INTEGER",
        "mode": "NULLABLE"
      },
      {
        "name": "shares",
        "type": "INTEGER",
        "mode": "NULLABLE"
      },
      {
        "name": "comments",
        "type": "INTEGER",
        "mode": "NULLABLE"
      },
      {
        "name": "views",
        "type": "INTEGER",
        "mode": "NULLABLE"
      }
    ]
  },
  {
    "name": "location",
    "type": "RECORD",
    "mode": "NULLABLE",
    "description": "Geographic location information",
    "fields": [
      {
        "name": "country",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "region",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "city",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "coordinates",
        "type": "GEOGRAPHY",
        "mode": "NULLABLE"
      }
    ]
  },
  {
    "name": "language",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Detected language of the content"
  },
  {
    "name": "hashtags",
    "type": "STRING",
    "mode": "REPEATED",
    "description": "Hashtags used in the post"
  },
  {
    "name": "mentions",
    "type": "STRING",
    "mode": "REPEATED",
    "description": "User mentions in the post"
  },
  {
    "name": "ingestion_timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "When the post was ingested into our system"
  },
  {
    "name": "raw_data",
    "type": "JSON",
    "mode": "NULLABLE",
    "description": "Original raw data from the platform API"
  }
]
```

#### 3.2 Sentiment Analysis Results Schema

```json
// gcp/bigquery/schemas/sentiment_analytics.json
[
  {
    "name": "analysis_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Unique identifier for the analysis"
  },
  {
    "name": "post_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Reference to the analyzed post"
  },
  {
    "name": "sentiment_label",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Sentiment classification (positive, negative, neutral)"
  },
  {
    "name": "sentiment_score",
    "type": "FLOAT",
    "mode": "REQUIRED",
    "description": "Sentiment score (-1.0 to 1.0)"
  },
  {
    "name": "confidence",
    "type": "FLOAT",
    "mode": "REQUIRED",
    "description": "Confidence score for the sentiment prediction"
  },
  {
    "name": "sentiment_scores",
    "type": "RECORD",
    "mode": "NULLABLE",
    "description": "Detailed sentiment scores",
    "fields": [
      {
        "name": "positive",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "negative",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "neutral",
        "type": "FLOAT",
        "mode": "NULLABLE"
      }
    ]
  },
  {
    "name": "emotions",
    "type": "RECORD",
    "mode": "NULLABLE",
    "description": "Emotion detection results",
    "fields": [
      {
        "name": "joy",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "anger",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "fear",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "sadness",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "surprise",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "disgust",
        "type": "FLOAT",
        "mode": "NULLABLE"
      }
    ]
  },
  {
    "name": "topics",
    "type": "STRING",
    "mode": "REPEATED",
    "description": "Identified topics in the content"
  },
  {
    "name": "keywords",
    "type": "RECORD",
    "mode": "REPEATED",
    "description": "Extracted keywords with relevance scores",
    "fields": [
      {
        "name": "keyword",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "relevance",
        "type": "FLOAT",
        "mode": "REQUIRED"
      }
    ]
  },
  {
    "name": "model_version",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Version of the ML model used for analysis"
  },
  {
    "name": "processing_time_ms",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "Time taken to process the analysis in milliseconds"
  },
  {
    "name": "analysis_timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "When the analysis was performed"
  }
]
```

#### 3.3 User Profiles Schema

```json
// gcp/bigquery/schemas/user_profiles.json
[
  {
    "name": "user_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Unique user identifier across platforms"
  },
  {
    "name": "platform_profiles",
    "type": "RECORD",
    "mode": "REPEATED",
    "description": "User profiles across different platforms",
    "fields": [
      {
        "name": "platform",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "platform_user_id",
        "type": "STRING",
        "mode": "REQUIRED"
      },
      {
        "name": "username",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "display_name",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "verified",
        "type": "BOOLEAN",
        "mode": "NULLABLE"
      },
      {
        "name": "followers_count",
        "type": "INTEGER",
        "mode": "NULLABLE"
      },
      {
        "name": "following_count",
        "type": "INTEGER",
        "mode": "NULLABLE"
      },
      {
        "name": "posts_count",
        "type": "INTEGER",
        "mode": "NULLABLE"
      },
      {
        "name": "account_created",
        "type": "TIMESTAMP",
        "mode": "NULLABLE"
      }
    ]
  },
  {
    "name": "behavioral_patterns",
    "type": "RECORD",
    "mode": "NULLABLE",
    "description": "Behavioral analysis results",
    "fields": [
      {
        "name": "authenticity_score",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "bot_probability",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "influence_score",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "engagement_rate",
        "type": "FLOAT",
        "mode": "NULLABLE"
      },
      {
        "name": "posting_frequency",
        "type": "FLOAT",
        "mode": "NULLABLE"
      }
    ]
  },
  {
    "name": "demographics",
    "type": "RECORD",
    "mode": "NULLABLE",
    "description": "Inferred demographic information",
    "fields": [
      {
        "name": "age_range",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "gender",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "location",
        "type": "STRING",
        "mode": "NULLABLE"
      },
      {
        "name": "interests",
        "type": "STRING",
        "mode": "REPEATED"
      }
    ]
  },
  {
    "name": "last_updated",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "When the profile was last updated"
  }
]
```

### Step 4: Create Tables with Optimization

```bash
# Create table creation script
cat > gcp/bigquery/scripts/create-tables.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
DATASET="sentinelbert_analytics"

echo "📋 Creating optimized BigQuery tables..."

# Create social_posts table with partitioning and clustering
bq mk --table \
    --time_partitioning_field=created_date \
    --time_partitioning_type=DAY \
    --time_partitioning_expiration=7776000 \
    --clustering_fields=platform,user_id,sentiment_label \
    --description="Social media posts with engagement metrics" \
    --label=table_type:fact \
    --label=data_source:social_media \
    $PROJECT_ID:$DATASET.social_posts \
    gcp/bigquery/schemas/social_posts.json

# Create sentiment_analytics table
bq mk --table \
    --time_partitioning_field=analysis_timestamp \
    --time_partitioning_type=DAY \
    --time_partitioning_expiration=7776000 \
    --clustering_fields=sentiment_label,model_version,post_id \
    --description="Sentiment analysis results" \
    --label=table_type:fact \
    --label=data_source:ml_analysis \
    $PROJECT_ID:$DATASET.sentiment_analytics \
    gcp/bigquery/schemas/sentiment_analytics.json

# Create user_profiles table
bq mk --table \
    --time_partitioning_field=last_updated \
    --time_partitioning_type=DAY \
    --clustering_fields=user_id \
    --description="User profiles and behavioral patterns" \
    --label=table_type:dimension \
    --label=data_source:user_data \
    $PROJECT_ID:$DATASET.user_profiles \
    gcp/bigquery/schemas/user_profiles.json

# Create aggregated views for common queries
echo "📊 Creating materialized views..."

# Daily sentiment summary view
bq mk --view \
    --description="Daily sentiment analysis summary" \
    --label=view_type:summary \
    $PROJECT_ID:$DATASET.daily_sentiment_summary \
    "$(cat gcp/bigquery/queries/daily_sentiment_summary.sql)"

# Platform performance view
bq mk --view \
    --description="Platform-wise performance metrics" \
    --label=view_type:analytics \
    $PROJECT_ID:$DATASET.platform_performance \
    "$(cat gcp/bigquery/queries/platform_performance.sql)"

echo "✅ All tables and views created successfully!"
EOF

chmod +x gcp/bigquery/scripts/create-tables.sh
./gcp/bigquery/scripts/create-tables.sh your-sentinelbert-project
```

### Step 5: Create Optimized Views

```sql
-- gcp/bigquery/queries/daily_sentiment_summary.sql
-- Daily sentiment analysis summary view
SELECT
  DATE(created_date) as analysis_date,
  platform,
  COUNT(*) as total_posts,
  COUNTIF(sentiment_label = 'positive') as positive_posts,
  COUNTIF(sentiment_label = 'negative') as negative_posts,
  COUNTIF(sentiment_label = 'neutral') as neutral_posts,
  AVG(sentiment_score) as avg_sentiment_score,
  AVG(confidence) as avg_confidence,
  ARRAY_AGG(DISTINCT topics IGNORE NULLS) as trending_topics
FROM `{project_id}.sentinelbert_analytics.social_posts` p
JOIN `{project_id}.sentinelbert_analytics.sentiment_analytics` s
  ON p.post_id = s.post_id
WHERE DATE(created_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY analysis_date, platform
ORDER BY analysis_date DESC, platform
```

```sql
-- gcp/bigquery/queries/platform_performance.sql
-- Platform-wise performance metrics view
SELECT
  platform,
  COUNT(DISTINCT p.user_id) as unique_users,
  COUNT(*) as total_posts,
  AVG(engagement_metrics.likes) as avg_likes,
  AVG(engagement_metrics.shares) as avg_shares,
  AVG(engagement_metrics.comments) as avg_comments,
  AVG(sentiment_score) as avg_sentiment,
  STDDEV(sentiment_score) as sentiment_volatility,
  COUNT(DISTINCT DATE(created_date)) as active_days,
  -- Engagement rate calculation
  SAFE_DIVIDE(
    SUM(engagement_metrics.likes + engagement_metrics.shares + engagement_metrics.comments),
    COUNT(*)
  ) as engagement_rate,
  -- Top hashtags
  ARRAY_AGG(hashtags IGNORE NULLS LIMIT 10) as top_hashtags
FROM `{project_id}.sentinelbert_analytics.social_posts` p
JOIN `{project_id}.sentinelbert_analytics.sentiment_analytics` s
  ON p.post_id = s.post_id
WHERE DATE(created_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY platform
ORDER BY total_posts DESC
```

---

## 🔄 Data Pipeline Integration

### Step 6: Create Data Ingestion Pipeline

```python
# gcp/bigquery/pipeline/bigquery_client.py
"""
BigQuery client for SentinentalBERT data pipeline
Handles data ingestion, querying, and optimization
"""

from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, WriteDisposition
from google.cloud.exceptions import NotFound
import pandas as pd
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SentinelBertBigQueryClient:
    """
    BigQuery client optimized for SentinentalBERT workloads
    Handles high-throughput ingestion and analytics queries
    """
    
    def __init__(self, project_id: str, location: str = "US"):
        self.project_id = project_id
        self.location = location
        self.client = bigquery.Client(project=project_id, location=location)
        self.dataset_id = "sentinelbert_analytics"
        
        logger.info(f"BigQuery client initialized for project: {project_id}")
    
    def insert_social_posts(self, posts: List[Dict[str, Any]]) -> bool:
        """
        Insert social media posts with optimized batch processing
        
        Args:
            posts: List of social media post dictionaries
            
        Returns:
            bool: Success status
        """
        
        table_id = f"{self.project_id}.{self.dataset_id}.social_posts"
        table = self.client.get_table(table_id)
        
        try:
            # Configure load job for optimal performance
            job_config = LoadJobConfig(
                write_disposition=WriteDisposition.WRITE_APPEND,
                schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
                ignore_unknown_values=True,
                max_bad_records=10
            )
            
            # Insert data
            errors = self.client.insert_rows_json(
                table, 
                posts, 
                row_ids=[post.get('post_id') for post in posts]
            )
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                return False
            
            logger.info(f"Successfully inserted {len(posts)} posts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert posts: {str(e)}")
            return False
    
    def insert_sentiment_analysis(self, analyses: List[Dict[str, Any]]) -> bool:
        """
        Insert sentiment analysis results
        
        Args:
            analyses: List of sentiment analysis dictionaries
            
        Returns:
            bool: Success status
        """
        
        table_id = f"{self.project_id}.{self.dataset_id}.sentiment_analytics"
        table = self.client.get_table(table_id)
        
        try:
            errors = self.client.insert_rows_json(
                table, 
                analyses,
                row_ids=[analysis.get('analysis_id') for analysis in analyses]
            )
            
            if errors:
                logger.error(f"BigQuery sentiment insert errors: {errors}")
                return False
            
            logger.info(f"Successfully inserted {len(analyses)} sentiment analyses")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert sentiment analyses: {str(e)}")
            return False
    
    def get_daily_sentiment_summary(self, days: int = 7) -> pd.DataFrame:
        """
        Get daily sentiment summary for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            DataFrame with daily sentiment summary
        """
        
        query = f"""
        SELECT
          DATE(created_date) as analysis_date,
          platform,
          COUNT(*) as total_posts,
          COUNTIF(sentiment_label = 'positive') as positive_posts,
          COUNTIF(sentiment_label = 'negative') as negative_posts,
          COUNTIF(sentiment_label = 'neutral') as neutral_posts,
          AVG(sentiment_score) as avg_sentiment_score,
          AVG(confidence) as avg_confidence
        FROM `{self.project_id}.{self.dataset_id}.social_posts` p
        JOIN `{self.project_id}.{self.dataset_id}.sentiment_analytics` s
          ON p.post_id = s.post_id
        WHERE DATE(created_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        GROUP BY analysis_date, platform
        ORDER BY analysis_date DESC, platform
        """
        
        try:
            df = self.client.query(query).to_dataframe()
            logger.info(f"Retrieved {len(df)} rows of daily sentiment summary")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get daily sentiment summary: {str(e)}")
            return pd.DataFrame()
    
    def get_trending_topics(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """
        Get trending topics in the last N hours
        
        Args:
            hours: Number of hours to analyze
            limit: Maximum number of topics to return
            
        Returns:
            List of trending topics with counts
        """
        
        query = f"""
        WITH topic_counts AS (
          SELECT
            topic,
            COUNT(*) as mention_count,
            AVG(sentiment_score) as avg_sentiment,
            COUNT(DISTINCT platform) as platform_count
          FROM `{self.project_id}.{self.dataset_id}.social_posts` p
          JOIN `{self.project_id}.{self.dataset_id}.sentiment_analytics` s
            ON p.post_id = s.post_id,
          UNNEST(topics) as topic
          WHERE created_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours} HOUR)
          GROUP BY topic
          HAVING mention_count >= 5
        )
        SELECT *
        FROM topic_counts
        ORDER BY mention_count DESC
        LIMIT {limit}
        """
        
        try:
            results = self.client.query(query).to_dataframe()
            topics = results.to_dict('records')
            logger.info(f"Retrieved {len(topics)} trending topics")
            return topics
            
        except Exception as e:
            logger.error(f"Failed to get trending topics: {str(e)}")
            return []
    
    def optimize_table_performance(self, table_name: str) -> bool:
        """
        Optimize table performance by updating clustering and partitioning
        
        Args:
            table_name: Name of the table to optimize
            
        Returns:
            bool: Success status
        """
        
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            # Get current table
            table = self.client.get_table(table_id)
            
            # Update clustering fields based on query patterns
            if table_name == "social_posts":
                clustering_fields = ["platform", "user_id", "created_date"]
            elif table_name == "sentiment_analytics":
                clustering_fields = ["sentiment_label", "model_version", "analysis_timestamp"]
            else:
                clustering_fields = None
            
            if clustering_fields:
                table.clustering_fields = clustering_fields
                table = self.client.update_table(table, ["clustering_fields"])
                logger.info(f"Updated clustering for {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize table {table_name}: {str(e)}")
            return False
    
    def get_query_performance_stats(self, query: str) -> Dict[str, Any]:
        """
        Get performance statistics for a query
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dictionary with performance metrics
        """
        
        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False
        )
        
        try:
            job = self.client.query(query, job_config=job_config)
            
            stats = {
                "total_bytes_processed": job.total_bytes_processed,
                "total_bytes_billed": job.total_bytes_billed,
                "estimated_cost_usd": (job.total_bytes_billed / (1024**4)) * 5.0,  # $5 per TB
                "cache_hit": job.cache_hit,
                "creation_time": job.creation_time,
                "query_plan": [stage.name for stage in job.query_plan] if job.query_plan else []
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get query performance stats: {str(e)}")
            return {}

# Usage example
if __name__ == "__main__":
    client = SentinelBertBigQueryClient("your-sentinelbert-project")
    
    # Example: Get daily sentiment summary
    summary = client.get_daily_sentiment_summary(days=7)
    print(f"Daily sentiment summary:\n{summary}")
    
    # Example: Get trending topics
    topics = client.get_trending_topics(hours=24)
    print(f"Trending topics: {topics}")
```

### Step 7: Create Streaming Ingestion Pipeline

```python
# gcp/bigquery/pipeline/streaming_ingestion.py
"""
Streaming data ingestion pipeline for BigQuery
Handles high-throughput data from Pub/Sub
"""

import asyncio
import json
from typing import Dict, List, Any
from google.cloud import pubsub_v1
from google.cloud import bigquery
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class StreamingBigQueryIngestion:
    """
    Streaming ingestion pipeline for BigQuery
    Processes messages from Pub/Sub and inserts into BigQuery
    """
    
    def __init__(self, project_id: str, subscription_name: str):
        self.project_id = project_id
        self.subscription_name = subscription_name
        self.subscriber = pubsub_v1.SubscriberClient()
        self.bq_client = SentinelBertBigQueryClient(project_id)
        self.batch_size = 100
        self.batch_timeout = 30  # seconds
        self.pending_messages = []
        
        # Subscription path
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_name
        )
        
        logger.info(f"Streaming ingestion initialized for subscription: {subscription_name}")
    
    def message_callback(self, message):
        """
        Callback function for processing Pub/Sub messages
        
        Args:
            message: Pub/Sub message
        """
        
        try:
            # Parse message data
            data = json.loads(message.data.decode('utf-8'))
            
            # Add to pending batch
            self.pending_messages.append(data)
            
            # Process batch if size threshold reached
            if len(self.pending_messages) >= self.batch_size:
                self._process_batch()
            
            # Acknowledge message
            message.ack()
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            message.nack()
    
    def _process_batch(self):
        """Process pending messages batch"""
        
        if not self.pending_messages:
            return
        
        try:
            # Separate different data types
            posts = []
            analyses = []
            
            for message in self.pending_messages:
                if message.get('type') == 'social_post':
                    posts.append(message['data'])
                elif message.get('type') == 'sentiment_analysis':
                    analyses.append(message['data'])
            
            # Insert data
            if posts:
                self.bq_client.insert_social_posts(posts)
            
            if analyses:
                self.bq_client.insert_sentiment_analysis(analyses)
            
            logger.info(f"Processed batch: {len(posts)} posts, {len(analyses)} analyses")
            
            # Clear pending messages
            self.pending_messages.clear()
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
    
    def start_streaming(self):
        """Start streaming ingestion"""
        
        # Configure flow control
        flow_control = pubsub_v1.types.FlowControl(max_messages=1000)
        
        logger.info("Starting streaming ingestion...")
        
        # Start pulling messages
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.message_callback,
            flow_control=flow_control
        )
        
        try:
            # Keep the main thread running
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            logger.info("Streaming ingestion stopped")

# Usage example
if __name__ == "__main__":
    ingestion = StreamingBigQueryIngestion(
        "your-sentinelbert-project",
        "sentiment-analysis-subscription"
    )
    
    ingestion.start_streaming()
```

---

## ⚡ Query Optimization

### Step 8: Create Optimized Query Templates

```sql
-- gcp/bigquery/queries/optimized_sentiment_analysis.sql
-- Optimized query for sentiment analysis with proper partitioning
WITH recent_posts AS (
  SELECT 
    post_id,
    platform,
    user_id,
    text_content,
    created_date,
    engagement_metrics
  FROM `{project_id}.sentinelbert_analytics.social_posts`
  WHERE DATE(created_date) = CURRENT_DATE()  -- Partition pruning
    AND platform IN UNNEST(@platforms)      -- Parameter for flexibility
),
sentiment_results AS (
  SELECT
    s.post_id,
    s.sentiment_label,
    s.sentiment_score,
    s.confidence,
    s.emotions,
    s.topics
  FROM `{project_id}.sentinelbert_analytics.sentiment_analytics` s
  WHERE DATE(s.analysis_timestamp) = CURRENT_DATE()  -- Partition pruning
    AND s.model_version = @model_version
)
SELECT
  p.platform,
  p.user_id,
  p.text_content,
  s.sentiment_label,
  s.sentiment_score,
  s.confidence,
  p.engagement_metrics.likes as likes,
  p.engagement_metrics.shares as shares,
  ARRAY_LENGTH(s.topics) as topic_count
FROM recent_posts p
JOIN sentiment_results s ON p.post_id = s.post_id
WHERE s.confidence > @min_confidence
ORDER BY s.sentiment_score DESC
LIMIT @limit_results
```

```sql
-- gcp/bigquery/queries/user_behavior_analysis.sql
-- Optimized user behavior analysis query
WITH user_activity AS (
  SELECT
    user_id,
    platform,
    COUNT(*) as post_count,
    AVG(engagement_metrics.likes) as avg_likes,
    AVG(engagement_metrics.shares) as avg_shares,
    STDDEV(engagement_metrics.likes) as likes_stddev,
    MIN(created_date) as first_post,
    MAX(created_date) as last_post,
    COUNT(DISTINCT DATE(created_date)) as active_days
  FROM `{project_id}.sentinelbert_analytics.social_posts`
  WHERE DATE(created_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL @analysis_days DAY)
  GROUP BY user_id, platform
),
user_sentiment AS (
  SELECT
    p.user_id,
    p.platform,
    AVG(s.sentiment_score) as avg_sentiment,
    STDDEV(s.sentiment_score) as sentiment_volatility,
    COUNTIF(s.sentiment_label = 'positive') / COUNT(*) as positive_ratio,
    COUNTIF(s.sentiment_label = 'negative') / COUNT(*) as negative_ratio
  FROM `{project_id}.sentinelbert_analytics.social_posts` p
  JOIN `{project_id}.sentinelbert_analytics.sentiment_analytics` s
    ON p.post_id = s.post_id
  WHERE DATE(p.created_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL @analysis_days DAY)
  GROUP BY p.user_id, p.platform
)
SELECT
  ua.user_id,
  ua.platform,
  ua.post_count,
  ua.avg_likes,
  ua.avg_shares,
  ua.active_days,
  us.avg_sentiment,
  us.sentiment_volatility,
  us.positive_ratio,
  us.negative_ratio,
  -- Engagement rate calculation
  SAFE_DIVIDE(ua.avg_likes + ua.avg_shares, ua.post_count) as engagement_rate,
  -- Activity consistency score
  SAFE_DIVIDE(ua.active_days, @analysis_days) as consistency_score,
  -- Influence score (simplified)
  LOG10(GREATEST(1, ua.avg_likes)) * us.positive_ratio as influence_score
FROM user_activity ua
JOIN user_sentiment us ON ua.user_id = us.user_id AND ua.platform = us.platform
WHERE ua.post_count >= @min_posts
ORDER BY influence_score DESC
LIMIT @limit_users
```

### Step 9: Create Query Performance Monitor

```python
# gcp/bigquery/monitoring/query_monitor.py
"""
Query performance monitoring for BigQuery
Tracks query costs, performance, and optimization opportunities
"""

from google.cloud import bigquery
from google.cloud import monitoring_v3
import time
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class BigQueryPerformanceMonitor:
    """Monitor BigQuery query performance and costs"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = bigquery.Client(project=project_id)
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        
        # Performance thresholds
        self.cost_threshold_usd = 1.0  # Alert if query costs > $1
        self.time_threshold_seconds = 30  # Alert if query takes > 30s
        self.bytes_threshold = 1024**3  # Alert if query processes > 1GB
    
    def monitor_query_job(self, job_id: str) -> Dict[str, Any]:
        """
        Monitor a specific query job
        
        Args:
            job_id: BigQuery job ID
            
        Returns:
            Dictionary with performance metrics
        """
        
        try:
            job = self.client.get_job(job_id)
            
            # Calculate metrics
            metrics = {
                "job_id": job_id,
                "state": job.state,
                "created": job.created.isoformat() if job.created else None,
                "started": job.started.isoformat() if job.started else None,
                "ended": job.ended.isoformat() if job.ended else None,
                "total_bytes_processed": job.total_bytes_processed,
                "total_bytes_billed": job.total_bytes_billed,
                "slot_ms": job.slot_millis,
                "total_slot_ms": job.total_slot_millis,
                "cache_hit": job.cache_hit,
                "estimated_cost_usd": self._calculate_cost(job.total_bytes_billed),
                "duration_seconds": self._calculate_duration(job),
                "efficiency_score": self._calculate_efficiency(job)
            }
            
            # Check for performance issues
            issues = self._identify_performance_issues(metrics)
            metrics["performance_issues"] = issues
            
            # Send metrics to Cloud Monitoring
            self._send_metrics_to_monitoring(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error monitoring job {job_id}: {str(e)}")
            return {}
    
    def get_daily_query_stats(self, days: int = 1) -> Dict[str, Any]:
        """
        Get daily query statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with daily statistics
        """
        
        # Query to get job statistics
        query = f"""
        SELECT
          DATE(creation_time) as query_date,
          COUNT(*) as total_queries,
          SUM(total_bytes_processed) as total_bytes_processed,
          SUM(total_bytes_billed) as total_bytes_billed,
          AVG(total_slot_ms) as avg_slot_ms,
          MAX(total_slot_ms) as max_slot_ms,
          COUNTIF(cache_hit) as cache_hits,
          COUNTIF(error_result IS NOT NULL) as error_count
        FROM `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND job_type = 'QUERY'
        GROUP BY query_date
        ORDER BY query_date DESC
        """
        
        try:
            results = self.client.query(query).to_dataframe()
            
            if not results.empty:
                stats = results.iloc[0].to_dict()
                stats["estimated_daily_cost_usd"] = self._calculate_cost(stats["total_bytes_billed"])
                stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_queries"] if stats["total_queries"] > 0 else 0
                stats["error_rate"] = stats["error_count"] / stats["total_queries"] if stats["total_queries"] > 0 else 0
                
                return stats
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {str(e)}")
            return {}
    
    def identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify query optimization opportunities
        
        Returns:
            List of optimization recommendations
        """
        
        opportunities = []
        
        # Query to find expensive queries
        expensive_queries = f"""
        SELECT
          query,
          total_bytes_processed,
          total_bytes_billed,
          total_slot_ms,
          creation_time
        FROM `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
          AND job_type = 'QUERY'
          AND total_bytes_billed > {self.bytes_threshold}
        ORDER BY total_bytes_billed DESC
        LIMIT 10
        """
        
        try:
            results = self.client.query(expensive_queries).to_dataframe()
            
            for _, row in results.iterrows():
                opportunity = {
                    "type": "expensive_query",
                    "query": row["query"][:200] + "..." if len(row["query"]) > 200 else row["query"],
                    "bytes_processed": row["total_bytes_processed"],
                    "estimated_cost": self._calculate_cost(row["total_bytes_billed"]),
                    "recommendations": self._generate_query_recommendations(row["query"])
                }
                opportunities.append(opportunity)
            
        except Exception as e:
            logger.error(f"Error identifying optimization opportunities: {str(e)}")
        
        return opportunities
    
    def _calculate_cost(self, bytes_billed: int) -> float:
        """Calculate query cost in USD"""
        if bytes_billed is None:
            return 0.0
        
        # BigQuery pricing: $5 per TB processed
        tb_processed = bytes_billed / (1024**4)
        return tb_processed * 5.0
    
    def _calculate_duration(self, job) -> float:
        """Calculate job duration in seconds"""
        if job.started and job.ended:
            return (job.ended - job.started).total_seconds()
        return 0.0
    
    def _calculate_efficiency(self, job) -> float:
        """Calculate query efficiency score (0-1)"""
        if not job.total_bytes_processed or not job.total_slot_millis:
            return 0.0
        
        # Simple efficiency metric: bytes processed per slot millisecond
        efficiency = job.total_bytes_processed / job.total_slot_millis
        
        # Normalize to 0-1 scale (this is a simplified calculation)
        return min(1.0, efficiency / 1000000)
    
    def _identify_performance_issues(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify performance issues"""
        issues = []
        
        if metrics.get("estimated_cost_usd", 0) > self.cost_threshold_usd:
            issues.append(f"High cost: ${metrics['estimated_cost_usd']:.2f}")
        
        if metrics.get("duration_seconds", 0) > self.time_threshold_seconds:
            issues.append(f"Long duration: {metrics['duration_seconds']:.1f}s")
        
        if metrics.get("total_bytes_processed", 0) > self.bytes_threshold:
            issues.append(f"Large data scan: {metrics['total_bytes_processed'] / (1024**3):.1f}GB")
        
        if not metrics.get("cache_hit", False):
            issues.append("Cache miss - consider query caching")
        
        return issues
    
    def _generate_query_recommendations(self, query: str) -> List[str]:
        """Generate optimization recommendations for a query"""
        recommendations = []
        
        query_lower = query.lower()
        
        if "select *" in query_lower:
            recommendations.append("Avoid SELECT * - specify only needed columns")
        
        if "where" not in query_lower:
            recommendations.append("Add WHERE clause to filter data")
        
        if "date(" in query_lower and "partition" not in query_lower:
            recommendations.append("Use partition pruning with date filters")
        
        if "group by" in query_lower and "limit" not in query_lower:
            recommendations.append("Consider adding LIMIT to reduce result size")
        
        if "join" in query_lower and "on" in query_lower:
            recommendations.append("Ensure JOIN conditions use clustered fields")
        
        return recommendations
    
    def _send_metrics_to_monitoring(self, metrics: Dict[str, Any]):
        """Send metrics to Cloud Monitoring"""
        
        try:
            # Create time series data
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            
            # Query cost metric
            if metrics.get("estimated_cost_usd"):
                point = monitoring_v3.Point({
                    "interval": interval,
                    "value": {"double_value": metrics["estimated_cost_usd"]}
                })
                
                series = monitoring_v3.TimeSeries({
                    "metric": {
                        "type": "custom.googleapis.com/bigquery/query_cost",
                        "labels": {"job_id": metrics["job_id"]}
                    },
                    "resource": {
                        "type": "global",
                        "labels": {"project_id": self.project_id}
                    },
                    "points": [point]
                })
                
                self.monitoring_client.create_time_series(
                    name=self.project_name,
                    time_series=[series]
                )
            
        except Exception as e:
            logger.error(f"Failed to send metrics to monitoring: {e}")

# Usage example
if __name__ == "__main__":
    monitor = BigQueryPerformanceMonitor("your-sentinelbert-project")
    
    # Get daily stats
    stats = monitor.get_daily_query_stats()
    print(f"Daily query stats: {stats}")
    
    # Get optimization opportunities
    opportunities = monitor.identify_optimization_opportunities()
    print(f"Optimization opportunities: {opportunities}")
```

---

## 💰 Cost Management

### Step 10: Implement Cost Controls

```python
# gcp/bigquery/cost_management/cost_controller.py
"""
BigQuery cost management and controls
Implements budget monitoring and cost optimization
"""

from google.cloud import bigquery
from google.cloud import billing_v1
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BigQueryCostController:
    """
    Cost management for BigQuery operations
    Monitors spending and implements cost controls
    """
    
    def __init__(self, project_id: str, monthly_budget_usd: float = 100.0):
        self.project_id = project_id
        self.monthly_budget_usd = monthly_budget_usd
        self.client = bigquery.Client(project=project_id)
        self.billing_client = billing_v1.CloudBillingClient()
        
        # Cost thresholds
        self.daily_budget_usd = monthly_budget_usd / 30
        self.query_cost_limit_usd = 5.0  # Max cost per query
        
        logger.info(f"Cost controller initialized with ${monthly_budget_usd}/month budget")
    
    def check_query_cost_before_execution(self, query: str) -> Dict[str, Any]:
        """
        Check query cost before execution
        
        Args:
            query: SQL query to check
            
        Returns:
            Dictionary with cost information and approval status
        """
        
        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False
        )
        
        try:
            job = self.client.query(query, job_config=job_config)
            
            estimated_cost = (job.total_bytes_processed / (1024**4)) * 5.0  # $5 per TB
            
            result = {
                "estimated_cost_usd": estimated_cost,
                "bytes_processed": job.total_bytes_processed,
                "approved": estimated_cost <= self.query_cost_limit_usd,
                "reason": ""
            }
            
            if not result["approved"]:
                result["reason"] = f"Query cost ${estimated_cost:.2f} exceeds limit ${self.query_cost_limit_usd}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking query cost: {str(e)}")
            return {
                "estimated_cost_usd": 0,
                "bytes_processed": 0,
                "approved": False,
                "reason": f"Error estimating cost: {str(e)}"
            }
    
    def get_current_month_spending(self) -> Dict[str, Any]:
        """
        Get current month's BigQuery spending
        
        Returns:
            Dictionary with spending information
        """
        
        # Query to get current month's job costs
        query = f"""
        SELECT
          SUM(total_bytes_billed) as total_bytes_billed,
          COUNT(*) as total_queries,
          AVG(total_bytes_billed) as avg_bytes_per_query
        FROM `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE DATE(creation_time) >= DATE_TRUNC(CURRENT_DATE(), MONTH)
          AND job_type = 'QUERY'
          AND state = 'DONE'
        """
        
        try:
            results = list(self.client.query(query))
            
            if results:
                row = results[0]
                total_bytes = row.total_bytes_billed or 0
                estimated_cost = (total_bytes / (1024**4)) * 5.0
                
                spending_info = {
                    "current_month_cost_usd": estimated_cost,
                    "monthly_budget_usd": self.monthly_budget_usd,
                    "budget_used_percentage": (estimated_cost / self.monthly_budget_usd) * 100,
                    "remaining_budget_usd": self.monthly_budget_usd - estimated_cost,
                    "total_queries": row.total_queries or 0,
                    "avg_cost_per_query": estimated_cost / max(1, row.total_queries or 1),
                    "days_remaining": (datetime.now().replace(day=1, month=datetime.now().month+1) - datetime.now()).days
                }
                
                return spending_info
            
            return {
                "current_month_cost_usd": 0,
                "monthly_budget_usd": self.monthly_budget_usd,
                "budget_used_percentage": 0,
                "remaining_budget_usd": self.monthly_budget_usd,
                "total_queries": 0,
                "avg_cost_per_query": 0,
                "days_remaining": 30
            }
            
        except Exception as e:
            logger.error(f"Error getting spending info: {str(e)}")
            return {}
    
    def implement_cost_controls(self) -> List[str]:
        """
        Implement cost control measures
        
        Returns:
            List of implemented controls
        """
        
        controls = []
        spending = self.get_current_month_spending()
        
        if not spending:
            return controls
        
        budget_used = spending.get("budget_used_percentage", 0)
        
        # Implement progressive cost controls
        if budget_used > 90:
            # Critical: Block expensive queries
            self.query_cost_limit_usd = 1.0
            controls.append("CRITICAL: Reduced query cost limit to $1.00")
            
        elif budget_used > 75:
            # Warning: Reduce query cost limit
            self.query_cost_limit_usd = 2.0
            controls.append("WARNING: Reduced query cost limit to $2.00")
            
        elif budget_used > 50:
            # Caution: Monitor closely
            controls.append("CAUTION: 50% budget used - monitoring closely")
        
        # Additional controls based on query patterns
        avg_cost = spending.get("avg_cost_per_query", 0)
        if avg_cost > 0.50:
            controls.append("High average query cost detected - review query optimization")
        
        return controls
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cost report
        
        Returns:
            Dictionary with cost analysis
        """
        
        spending = self.get_current_month_spending()
        controls = self.implement_cost_controls()
        
        # Get top expensive queries
        expensive_queries_query = f"""
        SELECT
          SUBSTR(query, 1, 100) as query_preview,
          total_bytes_billed,
          creation_time,
          user_email
        FROM `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
          AND job_type = 'QUERY'
          AND total_bytes_billed > 1073741824  -- > 1GB
        ORDER BY total_bytes_billed DESC
        LIMIT 10
        """
        
        try:
            expensive_queries = list(self.client.query(expensive_queries_query))
            
            report = {
                "spending_summary": spending,
                "cost_controls": controls,
                "expensive_queries": [
                    {
                        "query_preview": row.query_preview,
                        "estimated_cost_usd": (row.total_bytes_billed / (1024**4)) * 5.0,
                        "creation_time": row.creation_time.isoformat(),
                        "user_email": row.user_email
                    }
                    for row in expensive_queries
                ],
                "recommendations": self._generate_cost_recommendations(spending),
                "report_generated": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating cost report: {str(e)}")
            return {"error": str(e)}
    
    def _generate_cost_recommendations(self, spending: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        budget_used = spending.get("budget_used_percentage", 0)
        avg_cost = spending.get("avg_cost_per_query", 0)
        
        if budget_used > 75:
            recommendations.append("Consider implementing query result caching")
            recommendations.append("Review and optimize expensive queries")
            recommendations.append("Implement stricter query cost limits")
        
        if avg_cost > 0.10:
            recommendations.append("Focus on partition pruning in queries")
            recommendations.append("Avoid SELECT * queries")
            recommendations.append("Use clustering for frequently filtered columns")
        
        recommendations.append("Set up automated budget alerts")
        recommendations.append("Regular review of query patterns and costs")
        
        return recommendations

# Usage example
if __name__ == "__main__":
    controller = BigQueryCostController("your-sentinelbert-project", monthly_budget_usd=100.0)
    
    # Check query cost
    test_query = "SELECT * FROM `your-project.dataset.table` LIMIT 1000"
    cost_check = controller.check_query_cost_before_execution(test_query)
    print(f"Query cost check: {cost_check}")
    
    # Generate cost report
    report = controller.generate_cost_report()
    print(f"Cost report: {report}")
```

---

## 🔒 Security & Access Control

### Step 11: Configure Security

```bash
# Create security configuration script
cat > gcp/bigquery/scripts/configure-security.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}

echo "🔒 Configuring BigQuery security and access control..."

# Create BigQuery service account
gcloud iam service-accounts create bigquery-service \
    --display-name="BigQuery Service Account" \
    --description="Service account for BigQuery operations" || true

BQ_SA_EMAIL="bigquery-service@$PROJECT_ID.iam.gserviceaccount.com"

# Assign BigQuery roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BQ_SA_EMAIL" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$BQ_SA_EMAIL" \
    --role="roles/bigquery.jobUser"

# Create read-only analyst role
gcloud iam service-accounts create bigquery-analyst \
    --display-name="BigQuery Analyst" \
    --description="Read-only access for analysts" || true

ANALYST_SA_EMAIL="bigquery-analyst@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ANALYST_SA_EMAIL" \
    --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$ANALYST_SA_EMAIL" \
    --role="roles/bigquery.jobUser"

# Configure dataset-level permissions
echo "📊 Configuring dataset permissions..."

# Analytics dataset - full access for service account
bq add-iam-policy-binding \
    --member="serviceAccount:$BQ_SA_EMAIL" \
    --role="roles/bigquery.dataEditor" \
    $PROJECT_ID:sentinelbert_analytics

# Analytics dataset - read access for analysts
bq add-iam-policy-binding \
    --member="serviceAccount:$ANALYST_SA_EMAIL" \
    --role="roles/bigquery.dataViewer" \
    $PROJECT_ID:sentinelbert_analytics

# Raw dataset - restricted access
bq add-iam-policy-binding \
    --member="serviceAccount:$BQ_SA_EMAIL" \
    --role="roles/bigquery.dataEditor" \
    $PROJECT_ID:sentinelbert_raw

echo "✅ BigQuery security configuration completed!"
EOF

chmod +x gcp/bigquery/scripts/configure-security.sh
./gcp/bigquery/scripts/configure-security.sh your-sentinelbert-project
```

---

## 📈 Monitoring & Performance

### Step 12: Set Up Comprehensive Monitoring

```python
# gcp/bigquery/monitoring/bigquery_dashboard.py
"""
BigQuery monitoring dashboard
Creates comprehensive monitoring for performance and costs
"""

from google.cloud import monitoring_v3
from google.cloud import bigquery
import json
from typing import Dict, Any, List

class BigQueryDashboard:
    """Create and manage BigQuery monitoring dashboard"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.DashboardsServiceClient()
        self.project_name = f"projects/{project_id}"
    
    def create_dashboard(self) -> str:
        """
        Create comprehensive BigQuery monitoring dashboard
        
        Returns:
            Dashboard ID
        """
        
        dashboard_config = {
            "displayName": "SentinentalBERT BigQuery Monitoring",
            "mosaicLayout": {
                "tiles": [
                    self._create_query_cost_tile(),
                    self._create_query_performance_tile(),
                    self._create_slot_utilization_tile(),
                    self._create_data_volume_tile(),
                    self._create_error_rate_tile(),
                    self._create_cache_hit_rate_tile()
                ]
            }
        }
        
        try:
            dashboard = self.monitoring_client.create_dashboard(
                parent=self.project_name,
                dashboard=dashboard_config
            )
            
            dashboard_id = dashboard.name.split('/')[-1]
            print(f"✅ Dashboard created: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            print(f"❌ Error creating dashboard: {str(e)}")
            return ""
    
    def _create_query_cost_tile(self) -> Dict:
        """Create query cost monitoring tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "BigQuery Query Costs",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="bigquery_project"',
                                "aggregation": {
                                    "alignmentPeriod": "3600s",
                                    "perSeriesAligner": "ALIGN_RATE",
                                    "crossSeriesReducer": "REDUCE_SUM"
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
    
    def _create_query_performance_tile(self) -> Dict:
        """Create query performance monitoring tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Query Performance",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="bigquery_project"',
                                "aggregation": {
                                    "alignmentPeriod": "3600s",
                                    "perSeriesAligner": "ALIGN_MEAN"
                                }
                            }
                        },
                        "plotType": "LINE"
                    }],
                    "yAxis": {
                        "label": "Duration (seconds)",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_slot_utilization_tile(self) -> Dict:
        """Create slot utilization monitoring tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Slot Utilization",
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
                        "plotType": "STACKED_AREA"
                    }],
                    "yAxis": {
                        "label": "Slots Used",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_data_volume_tile(self) -> Dict:
        """Create data volume monitoring tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Data Volume Processed",
                "xyChart": {
                    "dataSets": [{
                        "timeSeriesQuery": {
                            "timeSeriesFilter": {
                                "filter": 'resource.type="bigquery_project"',
                                "aggregation": {
                                    "alignmentPeriod": "3600s",
                                    "perSeriesAligner": "ALIGN_RATE",
                                    "crossSeriesReducer": "REDUCE_SUM"
                                }
                            }
                        },
                        "plotType": "STACKED_BAR"
                    }],
                    "yAxis": {
                        "label": "Bytes Processed",
                        "scale": "LINEAR"
                    }
                }
            }
        }
    
    def _create_error_rate_tile(self) -> Dict:
        """Create error rate monitoring tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Query Error Rate",
                "scorecard": {
                    "timeSeriesQuery": {
                        "timeSeriesFilter": {
                            "filter": 'resource.type="bigquery_project"',
                            "aggregation": {
                                "alignmentPeriod": "3600s",
                                "perSeriesAligner": "ALIGN_RATE"
                            }
                        }
                    },
                    "sparkChartView": {
                        "sparkChartType": "SPARK_LINE"
                    }
                }
            }
        }
    
    def _create_cache_hit_rate_tile(self) -> Dict:
        """Create cache hit rate monitoring tile"""
        return {
            "width": 6,
            "height": 4,
            "widget": {
                "title": "Cache Hit Rate",
                "scorecard": {
                    "timeSeriesQuery": {
                        "timeSeriesFilter": {
                            "filter": 'resource.type="bigquery_project"',
                            "aggregation": {
                                "alignmentPeriod": "3600s",
                                "perSeriesAligner": "ALIGN_MEAN"
                            }
                        }
                    },
                    "gaugeView": {
                        "lowerBound": 0.0,
                        "upperBound": 1.0
                    }
                }
            }
        }

# Usage example
if __name__ == "__main__":
    dashboard = BigQueryDashboard("your-sentinelbert-project")
    dashboard_id = dashboard.create_dashboard()
    print(f"Dashboard created with ID: {dashboard_id}")
```

---

## 🧪 Testing & Validation

### Step 13: Create Test Suite

```bash
# Create comprehensive test script
cat > gcp/bigquery/scripts/test-bigquery.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
DATASET="sentinelbert_analytics"

echo "🧪 Testing BigQuery setup..."

# Test 1: Verify datasets exist
echo "📊 Testing dataset existence..."
for dataset in sentinelbert_analytics sentinelbert_raw sentinelbert_logs; do
    if bq ls -d $PROJECT_ID:$dataset > /dev/null 2>&1; then
        echo "✅ Dataset $dataset exists"
    else
        echo "❌ Dataset $dataset not found"
    fi
done

# Test 2: Verify tables exist
echo "📋 Testing table existence..."
for table in social_posts sentiment_analytics user_profiles; do
    if bq ls $PROJECT_ID:$DATASET.$table > /dev/null 2>&1; then
        echo "✅ Table $table exists"
    else
        echo "❌ Table $table not found"
    fi
done

# Test 3: Test data insertion
echo "💾 Testing data insertion..."
cat > /tmp/test_data.json << 'JSON'
{
  "post_id": "test_001",
  "platform": "twitter",
  "user_id": "test_user",
  "username": "testuser",
  "text_content": "This is a test post for BigQuery validation",
  "created_date": "2024-01-15T10:00:00Z",
  "engagement_metrics": {
    "likes": 10,
    "shares": 2,
    "comments": 1
  },
  "language": "en",
  "hashtags": ["test", "bigquery"],
  "ingestion_timestamp": "2024-01-15T10:01:00Z"
}
JSON

bq insert $PROJECT_ID:$DATASET.social_posts /tmp/test_data.json
if [ $? -eq 0 ]; then
    echo "✅ Test data insertion successful"
else
    echo "❌ Test data insertion failed"
fi

# Test 4: Test query performance
echo "⚡ Testing query performance..."
QUERY="SELECT COUNT(*) as total_posts FROM \`$PROJECT_ID.$DATASET.social_posts\` WHERE DATE(created_date) = CURRENT_DATE()"

start_time=$(date +%s)
bq query --use_legacy_sql=false "$QUERY" > /dev/null 2>&1
end_time=$(date +%s)
duration=$((end_time - start_time))

if [ $duration -lt 10 ]; then
    echo "✅ Query performance good: ${duration}s"
else
    echo "⚠️  Query performance slow: ${duration}s"
fi

# Test 5: Test cost estimation
echo "💰 Testing cost estimation..."
COST_QUERY="SELECT platform, COUNT(*) as posts FROM \`$PROJECT_ID.$DATASET.social_posts\` GROUP BY platform"
bq query --dry_run --use_legacy_sql=false "$COST_QUERY" > /tmp/cost_test.txt 2>&1

if grep -q "bytes processed" /tmp/cost_test.txt; then
    echo "✅ Cost estimation working"
else
    echo "❌ Cost estimation failed"
fi

# Cleanup
rm -f /tmp/test_data.json /tmp/cost_test.txt

echo "✅ BigQuery testing completed!"
EOF

chmod +x gcp/bigquery/scripts/test-bigquery.sh
./gcp/bigquery/scripts/test-bigquery.sh your-sentinelbert-project
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Quota Exceeded

**Error**: `Quota exceeded: Your project exceeded quota for concurrent queries`

**Solution**:
```bash
# Check current quotas
gcloud compute project-info describe --project=your-project

# Request quota increase
# Go to: https://console.cloud.google.com/iam-admin/quotas
# Filter: BigQuery API
# Request increase for concurrent queries
```

#### Issue 2: High Query Costs

**Problem**: Queries consuming too many slots/bytes

**Solution**:
```sql
-- Use partition pruning
SELECT * FROM table 
WHERE DATE(timestamp_column) = CURRENT_DATE()

-- Avoid SELECT *
SELECT specific_columns FROM table

-- Use LIMIT for testing
SELECT * FROM table LIMIT 1000
```

#### Issue 3: Slow Query Performance

**Problem**: Queries taking too long to execute

**Solution**:
```sql
-- Add clustering to frequently filtered columns
ALTER TABLE dataset.table 
CLUSTER BY column1, column2, column3

-- Use approximate aggregation for large datasets
SELECT APPROX_COUNT_DISTINCT(user_id) FROM table

-- Optimize JOINs
SELECT * FROM table1 t1
JOIN table2 t2 ON t1.clustered_column = t2.clustered_column
```

#### Issue 4: Permission Denied

**Error**: `Access Denied: BigQuery BigQuery: Permission denied`

**Solution**:
```bash
# Check current permissions
gcloud projects get-iam-policy your-project

# Add necessary role
gcloud projects add-iam-policy-binding your-project \
    --member="user:your-email@domain.com" \
    --role="roles/bigquery.dataEditor"
```

---

## 📞 Important Links & References

### 🔗 Essential Links

- **BigQuery Console**: https://console.cloud.google.com/bigquery
- **Quotas Console**: https://console.cloud.google.com/iam-admin/quotas
- **Billing Console**: https://console.cloud.google.com/billing
- **Monitoring Console**: https://console.cloud.google.com/monitoring

### 📚 Documentation References

- **BigQuery Documentation**: https://cloud.google.com/bigquery/docs
- **Standard SQL Reference**: https://cloud.google.com/bigquery/docs/reference/standard-sql
- **Best Practices**: https://cloud.google.com/bigquery/docs/best-practices-performance-overview
- **Cost Optimization**: https://cloud.google.com/bigquery/docs/best-practices-costs
- **Security**: https://cloud.google.com/bigquery/docs/access-control
- **Monitoring**: https://cloud.google.com/bigquery/docs/monitoring
- **Pricing**: https://cloud.google.com/bigquery/pricing

### 🛠️ Tools & Resources

- **bq CLI**: https://cloud.google.com/bigquery/docs/bq-command-line-tool
- **Python Client**: https://cloud.google.com/python/docs/reference/bigquery/latest
- **Query Validator**: https://cloud.google.com/bigquery/docs/dry-run-queries
- **Cost Calculator**: https://cloud.google.com/products/calculator

---

<div align="center">

**Next Steps**: Continue with [Pub/Sub Setup](./06-pubsub-setup.md) to configure your messaging infrastructure.

*Your BigQuery data warehouse is now configured with 100 slots, optimized storage, and comprehensive cost controls.*

</div>
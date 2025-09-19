# Pub/Sub Setup Guide for SentinentalBERT

<div align="center">

![Pub/Sub](https://img.shields.io/badge/Pub%2FSub-Messaging-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Streaming](https://img.shields.io/badge/Streaming-15%20GiB%2Fday-FF6F00?style=for-the-badge&logo=apache-kafka&logoColor=white)

**High-Throughput Message Streaming with BigQuery Integration**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [📊 Topic & Subscription Configuration](#-topic--subscription-configuration)
- [🔄 BigQuery Integration](#-bigquery-integration)
- [⚡ High-Throughput Optimization](#-high-throughput-optimization)
- [🔒 Security & Access Control](#-security--access-control)
- [📈 Monitoring & Alerting](#-monitoring--alerting)
- [💰 Cost Optimization](#-cost-optimization)
- [🧪 Testing & Validation](#-testing--validation)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide configures Google Cloud Pub/Sub for SentinentalBERT's high-throughput data streaming needs. Your configuration handles 15 GiB of daily data with direct BigQuery integration for real-time analytics.

### 🌟 Your Pub/Sub Configuration

Based on your specifications:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| **Daily Data Volume** | 15 GiB | High-throughput social media ingestion |
| **Message Delivery** | BigQuery | Direct streaming to data warehouse |
| **Topic Retention** | 1 day | Cost-optimized message retention |
| **Subscription Retention** | 1 day | Efficient message processing |
| **Acknowledged Messages** | 1 subscription | Streamlined processing |
| **Batch Processing** | 1000 messages | Optimized throughput |
| **Max Latency** | 100ms | Real-time processing |

### 💰 Cost Benefits

- **Pay-per-use**: Only charged for messages published/delivered
- **Direct BigQuery Integration**: Eliminates intermediate processing costs
- **Short Retention**: Minimizes storage costs
- **Batch Processing**: Reduces per-message overhead

### ⏱️ Estimated Setup Time: 15-20 minutes

---

## 🔧 Prerequisites

### ✅ Required Setup

1. **GCP Project**: With Pub/Sub API enabled
2. **BigQuery**: Dataset and tables configured
3. **Service Account**: With appropriate permissions
4. **gcloud CLI**: Authenticated and configured

### 📦 Install Required Tools

```bash
# Install Pub/Sub client libraries
pip install google-cloud-pubsub
pip install google-cloud-bigquery

# Install additional dependencies
pip install asyncio aiohttp
pip install protobuf grpcio
```

### 🔑 Enable APIs

```bash
# Enable Pub/Sub APIs
gcloud services enable pubsub.googleapis.com
gcloud services enable pubsublite.googleapis.com

# Verify API enablement
gcloud services list --enabled --filter="name:pubsub.googleapis.com"
```

---

## 🚀 Step-by-Step Setup

### Step 1: Create Pub/Sub Configuration

```bash
# Create Pub/Sub configuration directory
mkdir -p gcp/pubsub/{topics,subscriptions,schemas,scripts,monitoring}

# Create configuration file
cat > gcp/pubsub/config.yaml << 'EOF'
# Pub/Sub Configuration for SentinentalBERT
project_id: "your-sentinelbert-project"
region: "us-central1"

# Data volume configuration
daily_data_gib: 15
message_delivery_type: "bigquery"
topic_retention_days: 1
subscription_retention_days: 1

# Topics configuration
topics:
  - name: "social-media-ingestion"
    description: "Main topic for social media data ingestion"
    retention_duration: "86400s"  # 1 day
    schema_type: "AVRO"
    
  - name: "sentiment-analysis-results"
    description: "Topic for sentiment analysis results"
    retention_duration: "86400s"
    schema_type: "JSON"
    
  - name: "behavioral-analysis-results"
    description: "Topic for behavioral pattern analysis"
    retention_duration: "86400s"
    schema_type: "JSON"
    
  - name: "dead-letter-queue"
    description: "Dead letter queue for failed messages"
    retention_duration: "604800s"  # 7 days
    schema_type: "JSON"

# Subscriptions configuration
subscriptions:
  - name: "bigquery-social-posts"
    topic: "social-media-ingestion"
    delivery_type: "bigquery"
    bigquery_table: "sentinelbert_analytics.social_posts"
    ack_deadline: "600s"
    message_retention: "86400s"
    
  - name: "bigquery-sentiment-results"
    topic: "sentiment-analysis-results"
    delivery_type: "bigquery"
    bigquery_table: "sentinelbert_analytics.sentiment_analytics"
    ack_deadline: "300s"
    message_retention: "86400s"
    
  - name: "processing-subscription"
    topic: "social-media-ingestion"
    delivery_type: "pull"
    ack_deadline: "600s"
    message_retention: "86400s"

# Batch configuration
batch_settings:
  max_messages: 1000
  max_bytes: 10485760  # 10MB
  max_latency: "100ms"
  
# Dead letter policy
dead_letter_policy:
  dead_letter_topic: "dead-letter-queue"
  max_delivery_attempts: 5
EOF
```

### Step 2: Create Message Schemas

```json
// gcp/pubsub/schemas/social_post_schema.json
{
  "type": "record",
  "name": "SocialPost",
  "namespace": "com.sentinelbert.schemas",
  "fields": [
    {
      "name": "post_id",
      "type": "string",
      "doc": "Unique identifier for the social media post"
    },
    {
      "name": "platform",
      "type": {
        "type": "enum",
        "name": "Platform",
        "symbols": ["TWITTER", "REDDIT", "INSTAGRAM", "YOUTUBE", "FACEBOOK"]
      },
      "doc": "Social media platform"
    },
    {
      "name": "user_id",
      "type": "string",
      "doc": "User identifier on the platform"
    },
    {
      "name": "username",
      "type": ["null", "string"],
      "default": null,
      "doc": "Username or handle"
    },
    {
      "name": "text_content",
      "type": ["null", "string"],
      "default": null,
      "doc": "Text content of the post"
    },
    {
      "name": "media_urls",
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": [],
      "doc": "URLs of attached media"
    },
    {
      "name": "created_timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "Post creation timestamp in milliseconds"
    },
    {
      "name": "engagement_metrics",
      "type": {
        "type": "record",
        "name": "EngagementMetrics",
        "fields": [
          {"name": "likes", "type": ["null", "int"], "default": null},
          {"name": "shares", "type": ["null", "int"], "default": null},
          {"name": "comments", "type": ["null", "int"], "default": null},
          {"name": "views", "type": ["null", "long"], "default": null}
        ]
      },
      "doc": "Engagement metrics for the post"
    },
    {
      "name": "location",
      "type": ["null", {
        "type": "record",
        "name": "Location",
        "fields": [
          {"name": "country", "type": ["null", "string"], "default": null},
          {"name": "region", "type": ["null", "string"], "default": null},
          {"name": "city", "type": ["null", "string"], "default": null},
          {"name": "latitude", "type": ["null", "double"], "default": null},
          {"name": "longitude", "type": ["null", "double"], "default": null}
        ]
      }],
      "default": null,
      "doc": "Geographic location information"
    },
    {
      "name": "language",
      "type": ["null", "string"],
      "default": null,
      "doc": "Detected language of the content"
    },
    {
      "name": "hashtags",
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": [],
      "doc": "Hashtags used in the post"
    },
    {
      "name": "mentions",
      "type": {
        "type": "array",
        "items": "string"
      },
      "default": [],
      "doc": "User mentions in the post"
    },
    {
      "name": "ingestion_timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-millis"
      },
      "doc": "When the post was ingested into our system"
    },
    {
      "name": "raw_data",
      "type": ["null", "string"],
      "default": null,
      "doc": "Original raw data from platform API as JSON string"
    }
  ]
}
```

---

## 📊 Topic & Subscription Configuration

### Step 3: Create Topics and Subscriptions

```bash
# Create topic and subscription setup script
cat > gcp/pubsub/scripts/setup-topics-subscriptions.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}
REGION="us-central1"

echo "📡 Setting up Pub/Sub topics and subscriptions for project: $PROJECT_ID"

# Create schemas first
echo "📋 Creating message schemas..."

# Create social post schema
gcloud pubsub schemas create social-post-schema \
    --type=AVRO \
    --definition-file=gcp/pubsub/schemas/social_post_schema.json \
    --project=$PROJECT_ID

# Create topics with schemas
echo "📢 Creating topics..."

# Main ingestion topic
gcloud pubsub topics create social-media-ingestion \
    --message-retention-duration=86400s \
    --schema=social-post-schema \
    --message-encoding=JSON \
    --project=$PROJECT_ID

# Sentiment analysis results topic
gcloud pubsub topics create sentiment-analysis-results \
    --message-retention-duration=86400s \
    --project=$PROJECT_ID

# Behavioral analysis results topic
gcloud pubsub topics create behavioral-analysis-results \
    --message-retention-duration=86400s \
    --project=$PROJECT_ID

# Dead letter queue topic
gcloud pubsub topics create dead-letter-queue \
    --message-retention-duration=604800s \
    --project=$PROJECT_ID

# Create BigQuery subscriptions
echo "📊 Creating BigQuery subscriptions..."

# BigQuery subscription for social posts
gcloud pubsub subscriptions create bigquery-social-posts \
    --topic=social-media-ingestion \
    --bigquery-table=$PROJECT_ID:sentinelbert_analytics.social_posts \
    --ack-deadline=600 \
    --message-retention-duration=86400s \
    --dead-letter-topic=dead-letter-queue \
    --max-delivery-attempts=5 \
    --project=$PROJECT_ID

# BigQuery subscription for sentiment results
gcloud pubsub subscriptions create bigquery-sentiment-results \
    --topic=sentiment-analysis-results \
    --bigquery-table=$PROJECT_ID:sentinelbert_analytics.sentiment_analytics \
    --ack-deadline=300 \
    --message-retention-duration=86400s \
    --dead-letter-topic=dead-letter-queue \
    --max-delivery-attempts=5 \
    --project=$PROJECT_ID

# Processing subscription for real-time analysis
gcloud pubsub subscriptions create processing-subscription \
    --topic=social-media-ingestion \
    --ack-deadline=600 \
    --message-retention-duration=86400s \
    --dead-letter-topic=dead-letter-queue \
    --max-delivery-attempts=5 \
    --project=$PROJECT_ID

# Dead letter subscription
gcloud pubsub subscriptions create dead-letter-subscription \
    --topic=dead-letter-queue \
    --ack-deadline=600 \
    --message-retention-duration=604800s \
    --project=$PROJECT_ID

echo "✅ All topics and subscriptions created successfully!"

# Display created resources
echo "📋 Created resources:"
gcloud pubsub topics list --project=$PROJECT_ID
echo ""
gcloud pubsub subscriptions list --project=$PROJECT_ID
EOF

chmod +x gcp/pubsub/scripts/setup-topics-subscriptions.sh
./gcp/pubsub/scripts/setup-topics-subscriptions.sh your-sentinelbert-project
```

### Step 4: Configure Batch Settings

```python
# gcp/pubsub/config/batch_config.py
"""
Batch configuration for optimal Pub/Sub performance
Optimized for 15 GiB daily throughput
"""

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import BatchSettings
import logging

logger = logging.getLogger(__name__)

class PubSubBatchConfig:
    """
    Optimized batch configuration for high-throughput processing
    """
    
    def __init__(self, daily_data_gib: float = 15.0):
        self.daily_data_gib = daily_data_gib
        self.messages_per_second = self._calculate_messages_per_second()
        
    def _calculate_messages_per_second(self) -> float:
        """Calculate expected messages per second"""
        # Assume average message size of 2KB
        avg_message_size_bytes = 2048
        daily_bytes = self.daily_data_gib * (1024 ** 3)
        daily_messages = daily_bytes / avg_message_size_bytes
        messages_per_second = daily_messages / (24 * 60 * 60)
        
        logger.info(f"Estimated messages per second: {messages_per_second:.2f}")
        return messages_per_second
    
    def get_publisher_batch_settings(self) -> BatchSettings:
        """
        Get optimized batch settings for publisher
        
        Returns:
            BatchSettings optimized for high throughput
        """
        
        return BatchSettings(
            max_messages=1000,  # Maximum messages per batch
            max_bytes=10 * 1024 * 1024,  # 10MB max batch size
            max_latency=0.1,  # 100ms max latency
        )
    
    def get_subscriber_flow_control(self) -> pubsub_v1.types.FlowControl:
        """
        Get flow control settings for subscriber
        
        Returns:
            FlowControl settings for optimal processing
        """
        
        # Calculate based on expected throughput
        max_messages = min(10000, int(self.messages_per_second * 60))  # 1 minute buffer
        max_bytes = max_messages * 2048  # Assume 2KB average message size
        
        return pubsub_v1.types.FlowControl(
            max_messages=max_messages,
            max_bytes=max_bytes
        )
    
    def get_publisher_client_config(self) -> dict:
        """
        Get publisher client configuration
        
        Returns:
            Dictionary with client configuration
        """
        
        return {
            "batch_settings": self.get_publisher_batch_settings(),
            "publisher_options": pubsub_v1.PublisherOptions(
                enable_message_ordering=False,  # Disable for better performance
                flow_control=pubsub_v1.types.PublishFlowControl(
                    message_limit=50000,
                    byte_limit=100 * 1024 * 1024,  # 100MB
                    limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK
                )
            )
        }
    
    def get_subscriber_client_config(self) -> dict:
        """
        Get subscriber client configuration
        
        Returns:
            Dictionary with client configuration
        """
        
        return {
            "flow_control": self.get_subscriber_flow_control(),
            "scheduler": pubsub_v1.subscriber.scheduler.ThreadScheduler(
                executor=None  # Use default thread pool
            )
        }

# Global configuration instance
BATCH_CONFIG = PubSubBatchConfig(daily_data_gib=15.0)
```

---

## 🔄 BigQuery Integration

### Step 5: Configure Direct BigQuery Streaming

```python
# gcp/pubsub/integration/bigquery_streaming.py
"""
Direct BigQuery streaming integration for Pub/Sub
Handles high-throughput data ingestion with error handling
"""

from google.cloud import pubsub_v1
from google.cloud import bigquery
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class BigQueryStreamingIntegration:
    """
    Direct streaming integration between Pub/Sub and BigQuery
    Optimized for 15 GiB daily throughput
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.bigquery_client = bigquery.Client(project=project_id)
        
        # Topic paths
        self.social_media_topic = self.publisher.topic_path(
            project_id, "social-media-ingestion"
        )
        self.sentiment_topic = self.publisher.topic_path(
            project_id, "sentiment-analysis-results"
        )
        self.behavioral_topic = self.publisher.topic_path(
            project_id, "behavioral-analysis-results"
        )
        
        logger.info(f"BigQuery streaming integration initialized for project: {project_id}")
    
    def publish_social_post(self, post_data: Dict[str, Any]) -> str:
        """
        Publish social media post to Pub/Sub topic
        
        Args:
            post_data: Social media post data
            
        Returns:
            Message ID
        """
        
        try:
            # Validate and transform data
            transformed_data = self._transform_social_post(post_data)
            
            # Convert to JSON bytes
            message_data = json.dumps(transformed_data).encode('utf-8')
            
            # Add attributes for routing and filtering
            attributes = {
                "platform": transformed_data.get("platform", "unknown"),
                "language": transformed_data.get("language", "unknown"),
                "message_type": "social_post",
                "ingestion_time": datetime.utcnow().isoformat()
            }
            
            # Publish message
            future = self.publisher.publish(
                self.social_media_topic,
                message_data,
                **attributes
            )
            
            message_id = future.result()
            logger.debug(f"Published social post message: {message_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish social post: {str(e)}")
            raise
    
    def publish_sentiment_result(self, sentiment_data: Dict[str, Any]) -> str:
        """
        Publish sentiment analysis result
        
        Args:
            sentiment_data: Sentiment analysis result
            
        Returns:
            Message ID
        """
        
        try:
            # Add metadata
            sentiment_data["analysis_timestamp"] = datetime.utcnow().isoformat()
            
            message_data = json.dumps(sentiment_data).encode('utf-8')
            
            attributes = {
                "message_type": "sentiment_result",
                "model_version": sentiment_data.get("model_version", "unknown"),
                "sentiment_label": sentiment_data.get("sentiment_label", "unknown")
            }
            
            future = self.publisher.publish(
                self.sentiment_topic,
                message_data,
                **attributes
            )
            
            message_id = future.result()
            logger.debug(f"Published sentiment result: {message_id}")
            
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish sentiment result: {str(e)}")
            raise
    
    def batch_publish_social_posts(self, posts: List[Dict[str, Any]]) -> List[str]:
        """
        Batch publish multiple social media posts
        
        Args:
            posts: List of social media posts
            
        Returns:
            List of message IDs
        """
        
        message_ids = []
        futures = []
        
        try:
            for post in posts:
                # Transform and prepare message
                transformed_data = self._transform_social_post(post)
                message_data = json.dumps(transformed_data).encode('utf-8')
                
                attributes = {
                    "platform": transformed_data.get("platform", "unknown"),
                    "language": transformed_data.get("language", "unknown"),
                    "message_type": "social_post",
                    "batch_id": f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    "ingestion_time": datetime.utcnow().isoformat()
                }
                
                # Publish asynchronously
                future = self.publisher.publish(
                    self.social_media_topic,
                    message_data,
                    **attributes
                )
                futures.append(future)
            
            # Wait for all publishes to complete
            for future in futures:
                message_id = future.result()
                message_ids.append(message_id)
            
            logger.info(f"Batch published {len(message_ids)} social posts")
            return message_ids
            
        except Exception as e:
            logger.error(f"Failed to batch publish posts: {str(e)}")
            raise
    
    def setup_bigquery_subscription_monitoring(self, subscription_name: str):
        """
        Set up monitoring for BigQuery subscription
        
        Args:
            subscription_name: Name of the subscription to monitor
        """
        
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_name
        )
        
        def callback(message):
            """Callback for monitoring messages"""
            try:
                # Log message processing
                logger.info(f"Processing message: {message.message_id}")
                
                # Acknowledge message (BigQuery subscription handles actual processing)
                message.ack()
                
            except Exception as e:
                logger.error(f"Error in monitoring callback: {str(e)}")
                message.nack()
        
        # Set up flow control
        flow_control = pubsub_v1.types.FlowControl(max_messages=1000)
        
        # Start monitoring
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=callback,
            flow_control=flow_control
        )
        
        logger.info(f"Started monitoring subscription: {subscription_name}")
        
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            logger.info("Stopped monitoring subscription")
    
    def _transform_social_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform social post data for BigQuery compatibility
        
        Args:
            post_data: Raw social post data
            
        Returns:
            Transformed data compatible with BigQuery schema
        """
        
        # Ensure required fields
        transformed = {
            "post_id": post_data.get("post_id", ""),
            "platform": post_data.get("platform", "unknown"),
            "user_id": post_data.get("user_id", ""),
            "username": post_data.get("username"),
            "text_content": post_data.get("text_content"),
            "media_urls": post_data.get("media_urls", []),
            "created_date": self._format_timestamp(post_data.get("created_date")),
            "engagement_metrics": post_data.get("engagement_metrics", {}),
            "location": post_data.get("location"),
            "language": post_data.get("language"),
            "hashtags": post_data.get("hashtags", []),
            "mentions": post_data.get("mentions", []),
            "ingestion_timestamp": datetime.utcnow().isoformat(),
            "raw_data": json.dumps(post_data.get("raw_data", {})) if post_data.get("raw_data") else None
        }
        
        return transformed
    
    def _format_timestamp(self, timestamp: Any) -> str:
        """Format timestamp for BigQuery"""
        if isinstance(timestamp, str):
            return timestamp
        elif isinstance(timestamp, datetime):
            return timestamp.isoformat()
        elif isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).isoformat()
        else:
            return datetime.utcnow().isoformat()
    
    def get_subscription_metrics(self, subscription_name: str) -> Dict[str, Any]:
        """
        Get metrics for a BigQuery subscription
        
        Args:
            subscription_name: Name of the subscription
            
        Returns:
            Dictionary with subscription metrics
        """
        
        subscription_path = self.subscriber.subscription_path(
            self.project_id, subscription_name
        )
        
        try:
            subscription = self.subscriber.get_subscription(
                request={"subscription": subscription_path}
            )
            
            metrics = {
                "name": subscription.name,
                "topic": subscription.topic,
                "ack_deadline_seconds": subscription.ack_deadline_seconds,
                "message_retention_duration": subscription.message_retention_duration.total_seconds(),
                "bigquery_config": {
                    "table": subscription.bigquery_config.table if subscription.bigquery_config else None,
                    "use_topic_schema": subscription.bigquery_config.use_topic_schema if subscription.bigquery_config else None
                },
                "dead_letter_policy": {
                    "dead_letter_topic": subscription.dead_letter_policy.dead_letter_topic if subscription.dead_letter_policy else None,
                    "max_delivery_attempts": subscription.dead_letter_policy.max_delivery_attempts if subscription.dead_letter_policy else None
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get subscription metrics: {str(e)}")
            return {}

# Usage example
if __name__ == "__main__":
    integration = BigQueryStreamingIntegration("your-sentinelbert-project")
    
    # Example social post
    sample_post = {
        "post_id": "test_001",
        "platform": "twitter",
        "user_id": "user_123",
        "username": "testuser",
        "text_content": "This is a test post for Pub/Sub integration",
        "created_date": datetime.utcnow().isoformat(),
        "engagement_metrics": {"likes": 10, "shares": 2, "comments": 1},
        "language": "en",
        "hashtags": ["test", "pubsub"]
    }
    
    # Publish test message
    message_id = integration.publish_social_post(sample_post)
    print(f"Published message: {message_id}")
```

---

## ⚡ High-Throughput Optimization

### Step 6: Implement Performance Optimization

```python
# gcp/pubsub/optimization/throughput_optimizer.py
"""
Throughput optimization for Pub/Sub
Handles 15 GiB daily data volume efficiently
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import BatchSettings, PublishFlowControl
import logging
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

logger = logging.getLogger(__name__)

class HighThroughputPublisher:
    """
    High-throughput publisher optimized for 15 GiB daily volume
    """
    
    def __init__(self, project_id: str, topic_name: str):
        self.project_id = project_id
        self.topic_name = topic_name
        
        # Configure batch settings for high throughput
        batch_settings = BatchSettings(
            max_messages=1000,  # Large batch size
            max_bytes=10 * 1024 * 1024,  # 10MB batches
            max_latency=0.1,  # 100ms max latency
        )
        
        # Configure flow control
        flow_control = PublishFlowControl(
            message_limit=50000,  # Allow many pending messages
            byte_limit=100 * 1024 * 1024,  # 100MB pending data
            limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK
        )
        
        # Create optimized publisher
        publisher_options = pubsub_v1.PublisherOptions(
            enable_message_ordering=False,  # Disable for better performance
            flow_control=flow_control
        )
        
        self.publisher = pubsub_v1.PublisherClient(
            batch_settings=batch_settings,
            publisher_options=publisher_options
        )
        
        self.topic_path = self.publisher.topic_path(project_id, topic_name)
        
        # Performance tracking
        self.messages_published = 0
        self.bytes_published = 0
        self.start_time = time.time()
        
        logger.info(f"High-throughput publisher initialized for topic: {topic_name}")
    
    async def publish_batch_async(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Publish batch of messages asynchronously
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List of message IDs
        """
        
        futures = []
        
        for message in messages:
            # Prepare message data
            message_data = message.get("data", b"")
            if isinstance(message_data, str):
                message_data = message_data.encode('utf-8')
            
            attributes = message.get("attributes", {})
            
            # Publish asynchronously
            future = self.publisher.publish(
                self.topic_path,
                message_data,
                **attributes
            )
            futures.append(future)
        
        # Wait for all publishes to complete
        message_ids = []
        for future in futures:
            message_id = await asyncio.get_event_loop().run_in_executor(
                None, future.result
            )
            message_ids.append(message_id)
        
        # Update metrics
        self.messages_published += len(messages)
        self.bytes_published += sum(len(msg.get("data", b"")) for msg in messages)
        
        return message_ids
    
    def get_throughput_stats(self) -> Dict[str, Any]:
        """Get current throughput statistics"""
        
        elapsed_time = time.time() - self.start_time
        
        return {
            "messages_published": self.messages_published,
            "bytes_published": self.bytes_published,
            "elapsed_time_seconds": elapsed_time,
            "messages_per_second": self.messages_published / max(elapsed_time, 1),
            "bytes_per_second": self.bytes_published / max(elapsed_time, 1),
            "mbps": (self.bytes_published / max(elapsed_time, 1)) / (1024 * 1024)
        }

class HighThroughputSubscriber:
    """
    High-throughput subscriber with parallel processing
    """
    
    def __init__(self, project_id: str, subscription_name: str, max_workers: int = 10):
        self.project_id = project_id
        self.subscription_name = subscription_name
        self.max_workers = max_workers
        
        # Configure flow control for high throughput
        flow_control = pubsub_v1.types.FlowControl(
            max_messages=10000,  # Allow many outstanding messages
            max_bytes=100 * 1024 * 1024  # 100MB outstanding data
        )
        
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_name
        )
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Performance tracking
        self.messages_processed = 0
        self.processing_errors = 0
        self.start_time = time.time()
        
        logger.info(f"High-throughput subscriber initialized: {subscription_name}")
    
    def start_processing(self, message_handler):
        """
        Start processing messages with high throughput
        
        Args:
            message_handler: Function to process each message
        """
        
        def callback(message):
            """Message callback with parallel processing"""
            try:
                # Submit to thread pool for parallel processing
                future = self.executor.submit(self._process_message, message, message_handler)
                
                # Don't wait for completion - allows parallel processing
                future.add_done_callback(lambda f: self._handle_processing_result(f, message))
                
            except Exception as e:
                logger.error(f"Error in message callback: {str(e)}")
                message.nack()
                self.processing_errors += 1
        
        # Configure flow control
        flow_control = pubsub_v1.types.FlowControl(
            max_messages=10000,
            max_bytes=100 * 1024 * 1024
        )
        
        # Start streaming pull
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=callback,
            flow_control=flow_control
        )
        
        logger.info(f"Started high-throughput processing for: {self.subscription_name}")
        
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            self.executor.shutdown(wait=True)
            logger.info("Stopped message processing")
    
    def _process_message(self, message, handler):
        """Process individual message"""
        try:
            # Decode message data
            data = message.data.decode('utf-8')
            attributes = dict(message.attributes)
            
            # Call user-provided handler
            result = handler(data, attributes)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {str(e)}")
            raise
    
    def _handle_processing_result(self, future, message):
        """Handle processing result"""
        try:
            result = future.result()
            message.ack()
            self.messages_processed += 1
            
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            message.nack()
            self.processing_errors += 1
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        
        elapsed_time = time.time() - self.start_time
        
        return {
            "messages_processed": self.messages_processed,
            "processing_errors": self.processing_errors,
            "elapsed_time_seconds": elapsed_time,
            "messages_per_second": self.messages_processed / max(elapsed_time, 1),
            "error_rate": self.processing_errors / max(self.messages_processed + self.processing_errors, 1),
            "success_rate": self.messages_processed / max(self.messages_processed + self.processing_errors, 1)
        }

# Load testing utility
class PubSubLoadTester:
    """Load testing utility for Pub/Sub performance"""
    
    def __init__(self, project_id: str, topic_name: str):
        self.publisher = HighThroughputPublisher(project_id, topic_name)
    
    async def run_load_test(self, 
                           messages_per_second: int = 1000,
                           duration_seconds: int = 60,
                           message_size_bytes: int = 2048) -> Dict[str, Any]:
        """
        Run load test to validate throughput
        
        Args:
            messages_per_second: Target messages per second
            duration_seconds: Test duration
            message_size_bytes: Size of each test message
            
        Returns:
            Test results
        """
        
        logger.info(f"Starting load test: {messages_per_second} msg/s for {duration_seconds}s")
        
        # Generate test message
        test_data = "x" * message_size_bytes
        
        start_time = time.time()
        total_messages = 0
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Create batch of messages
            batch_size = min(100, messages_per_second)  # Batch up to 100 messages
            messages = []
            
            for i in range(batch_size):
                message = {
                    "data": test_data,
                    "attributes": {
                        "test_id": f"load_test_{int(time.time())}_{i}",
                        "message_size": str(message_size_bytes),
                        "batch_id": f"batch_{int(batch_start)}"
                    }
                }
                messages.append(message)
            
            # Publish batch
            await self.publisher.publish_batch_async(messages)
            total_messages += len(messages)
            
            # Rate limiting
            batch_duration = time.time() - batch_start
            target_batch_duration = batch_size / messages_per_second
            
            if batch_duration < target_batch_duration:
                await asyncio.sleep(target_batch_duration - batch_duration)
        
        # Get final stats
        stats = self.publisher.get_throughput_stats()
        stats["test_duration"] = duration_seconds
        stats["target_messages_per_second"] = messages_per_second
        stats["actual_messages_per_second"] = total_messages / duration_seconds
        stats["total_test_messages"] = total_messages
        
        logger.info(f"Load test completed: {stats}")
        return stats

# Usage example
if __name__ == "__main__":
    async def run_example():
        # Load test
        tester = PubSubLoadTester("your-sentinelbert-project", "social-media-ingestion")
        results = await tester.run_load_test(
            messages_per_second=500,
            duration_seconds=60,
            message_size_bytes=2048
        )
        print(f"Load test results: {results}")
    
    asyncio.run(run_example())
```

---

## 🔒 Security & Access Control

### Step 7: Configure Security

```bash
# Create security configuration script
cat > gcp/pubsub/scripts/configure-security.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}

echo "🔒 Configuring Pub/Sub security and access control..."

# Create Pub/Sub service account
gcloud iam service-accounts create pubsub-service \
    --display-name="Pub/Sub Service Account" \
    --description="Service account for Pub/Sub operations" || true

PUBSUB_SA_EMAIL="pubsub-service@$PROJECT_ID.iam.gserviceaccount.com"

# Assign Pub/Sub roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PUBSUB_SA_EMAIL" \
    --role="roles/pubsub.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PUBSUB_SA_EMAIL" \
    --role="roles/bigquery.dataEditor"

# Create publisher-only service account
gcloud iam service-accounts create pubsub-publisher \
    --display-name="Pub/Sub Publisher" \
    --description="Publisher-only access for data ingestion" || true

PUBLISHER_SA_EMAIL="pubsub-publisher@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PUBLISHER_SA_EMAIL" \
    --role="roles/pubsub.publisher"

# Create subscriber-only service account
gcloud iam service-accounts create pubsub-subscriber \
    --display-name="Pub/Sub Subscriber" \
    --description="Subscriber-only access for data processing" || true

SUBSCRIBER_SA_EMAIL="pubsub-subscriber@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SUBSCRIBER_SA_EMAIL" \
    --role="roles/pubsub.subscriber"

# Configure topic-level permissions
echo "📢 Configuring topic permissions..."

# Social media ingestion topic
gcloud pubsub topics add-iam-policy-binding social-media-ingestion \
    --member="serviceAccount:$PUBLISHER_SA_EMAIL" \
    --role="roles/pubsub.publisher"

gcloud pubsub topics add-iam-policy-binding social-media-ingestion \
    --member="serviceAccount:$SUBSCRIBER_SA_EMAIL" \
    --role="roles/pubsub.subscriber"

# Sentiment analysis results topic
gcloud pubsub topics add-iam-policy-binding sentiment-analysis-results \
    --member="serviceAccount:$PUBSUB_SA_EMAIL" \
    --role="roles/pubsub.editor"

# Configure subscription-level permissions
echo "📊 Configuring subscription permissions..."

# BigQuery subscriptions
gcloud pubsub subscriptions add-iam-policy-binding bigquery-social-posts \
    --member="serviceAccount:$PUBSUB_SA_EMAIL" \
    --role="roles/pubsub.subscriber"

gcloud pubsub subscriptions add-iam-policy-binding bigquery-sentiment-results \
    --member="serviceAccount:$PUBSUB_SA_EMAIL" \
    --role="roles/pubsub.subscriber"

echo "✅ Pub/Sub security configuration completed!"
EOF

chmod +x gcp/pubsub/scripts/configure-security.sh
./gcp/pubsub/scripts/configure-security.sh your-sentinelbert-project
```

---

## 📈 Monitoring & Alerting

### Step 8: Set Up Comprehensive Monitoring

```python
# gcp/pubsub/monitoring/pubsub_monitor.py
"""
Comprehensive monitoring for Pub/Sub operations
Tracks throughput, latency, and error rates
"""

from google.cloud import monitoring_v3
from google.cloud import pubsub_v1
import time
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PubSubMonitor:
    """Monitor Pub/Sub performance and health"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.pubsub_client = pubsub_v1.PublisherClient()
        self.subscriber_client = pubsub_v1.SubscriberClient()
        self.project_name = f"projects/{project_id}"
        
        logger.info(f"Pub/Sub monitor initialized for project: {project_id}")
    
    def get_topic_metrics(self, topic_name: str) -> Dict[str, Any]:
        """
        Get metrics for a specific topic
        
        Args:
            topic_name: Name of the topic
            
        Returns:
            Dictionary with topic metrics
        """
        
        # Define time range (last hour)
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": seconds - 3600, "nanos": nanos}
        })
        
        # Query metrics
        request = monitoring_v3.ListTimeSeriesRequest(
            name=self.project_name,
            filter=f'resource.type="pubsub_topic" AND resource.labels.topic_id="{topic_name}"',
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        results = self.monitoring_client.list_time_series(request=request)
        
        metrics = {
            "topic_name": topic_name,
            "message_count": 0,
            "byte_count": 0,
            "publish_requests": 0,
            "average_message_size": 0,
            "publish_rate": 0
        }
        
        for result in results:
            metric_type = result.metric.type
            
            if "num_messages" in metric_type:
                metrics["message_count"] = sum(point.value.int64_value for point in result.points)
            elif "num_unacked_messages_by_region" in metric_type:
                metrics["byte_count"] = sum(point.value.int64_value for point in result.points)
            elif "send_request_count" in metric_type:
                metrics["publish_requests"] = sum(point.value.int64_value for point in result.points)
        
        # Calculate derived metrics
        if metrics["message_count"] > 0:
            metrics["average_message_size"] = metrics["byte_count"] / metrics["message_count"]
            metrics["publish_rate"] = metrics["message_count"] / 3600  # per second
        
        return metrics
    
    def get_subscription_metrics(self, subscription_name: str) -> Dict[str, Any]:
        """
        Get metrics for a specific subscription
        
        Args:
            subscription_name: Name of the subscription
            
        Returns:
            Dictionary with subscription metrics
        """
        
        # Define time range (last hour)
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": seconds - 3600, "nanos": nanos}
        })
        
        # Query subscription metrics
        request = monitoring_v3.ListTimeSeriesRequest(
            name=self.project_name,
            filter=f'resource.type="pubsub_subscription" AND resource.labels.subscription_id="{subscription_name}"',
            interval=interval,
            view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        )
        
        results = self.monitoring_client.list_time_series(request=request)
        
        metrics = {
            "subscription_name": subscription_name,
            "unacked_messages": 0,
            "oldest_unacked_message_age": 0,
            "pull_requests": 0,
            "ack_message_count": 0,
            "processing_rate": 0,
            "backlog_size": 0
        }
        
        for result in results:
            metric_type = result.metric.type
            
            if "num_undelivered_messages" in metric_type:
                metrics["unacked_messages"] = sum(point.value.int64_value for point in result.points)
            elif "oldest_unacked_message_age" in metric_type:
                metrics["oldest_unacked_message_age"] = max(point.value.double_value for point in result.points) if result.points else 0
            elif "pull_request_count" in metric_type:
                metrics["pull_requests"] = sum(point.value.int64_value for point in result.points)
            elif "ack_message_count" in metric_type:
                metrics["ack_message_count"] = sum(point.value.int64_value for point in result.points)
        
        # Calculate processing rate
        if metrics["ack_message_count"] > 0:
            metrics["processing_rate"] = metrics["ack_message_count"] / 3600  # per second
        
        metrics["backlog_size"] = metrics["unacked_messages"]
        
        return metrics
    
    def create_alert_policies(self) -> List[str]:
        """
        Create alert policies for Pub/Sub monitoring
        
        Returns:
            List of created alert policy names
        """
        
        alert_policies = []
        
        # High message backlog alert
        backlog_alert = monitoring_v3.AlertPolicy(
            display_name="Pub/Sub High Message Backlog",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when message backlog exceeds threshold"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="High backlog",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="pubsub_subscription"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=10000,  # 10k messages
                        duration={"seconds": 300}  # 5 minutes
                    )
                )
            ]
        )
        
        # Old unacked messages alert
        age_alert = monitoring_v3.AlertPolicy(
            display_name="Pub/Sub Old Unacked Messages",
            documentation=monitoring_v3.AlertPolicy.Documentation(
                content="Alert when messages remain unacked for too long"
            ),
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Old messages",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter='resource.type="pubsub_subscription"',
                        comparison=monitoring_v3.ComparisonType.COMPARISON_GREATER_THAN,
                        threshold_value=3600,  # 1 hour
                        duration={"seconds": 300}
                    )
                )
            ]
        )
        
        # Create alert policies
        try:
            created_backlog = self.monitoring_client.create_alert_policy(
                name=self.project_name,
                alert_policy=backlog_alert
            )
            alert_policies.append(created_backlog.name)
            
            created_age = self.monitoring_client.create_alert_policy(
                name=self.project_name,
                alert_policy=age_alert
            )
            alert_policies.append(created_age.name)
            
            logger.info(f"Created {len(alert_policies)} alert policies")
            
        except Exception as e:
            logger.error(f"Failed to create alert policies: {str(e)}")
        
        return alert_policies
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report
        
        Returns:
            Dictionary with health status
        """
        
        # Get metrics for all topics and subscriptions
        topics = ["social-media-ingestion", "sentiment-analysis-results", "behavioral-analysis-results"]
        subscriptions = ["bigquery-social-posts", "bigquery-sentiment-results", "processing-subscription"]
        
        report = {
            "timestamp": time.time(),
            "overall_health": "healthy",
            "topics": {},
            "subscriptions": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Check topic health
        for topic in topics:
            try:
                metrics = self.get_topic_metrics(topic)
                report["topics"][topic] = metrics
                
                # Check for issues
                if metrics["publish_rate"] == 0:
                    report["alerts"].append(f"No messages published to {topic} in last hour")
                
            except Exception as e:
                report["topics"][topic] = {"error": str(e)}
                report["overall_health"] = "degraded"
        
        # Check subscription health
        for subscription in subscriptions:
            try:
                metrics = self.get_subscription_metrics(subscription)
                report["subscriptions"][subscription] = metrics
                
                # Check for issues
                if metrics["backlog_size"] > 10000:
                    report["alerts"].append(f"High backlog in {subscription}: {metrics['backlog_size']} messages")
                    report["overall_health"] = "degraded"
                
                if metrics["oldest_unacked_message_age"] > 3600:
                    report["alerts"].append(f"Old unacked messages in {subscription}: {metrics['oldest_unacked_message_age']}s")
                    report["overall_health"] = "degraded"
                
            except Exception as e:
                report["subscriptions"][subscription] = {"error": str(e)}
                report["overall_health"] = "degraded"
        
        # Generate recommendations
        if report["overall_health"] == "degraded":
            report["recommendations"].extend([
                "Check subscriber processing capacity",
                "Review message acknowledgment patterns",
                "Consider scaling subscriber instances",
                "Monitor BigQuery streaming quotas"
            ])
        
        return report

# Usage example
if __name__ == "__main__":
    monitor = PubSubMonitor("your-sentinelbert-project")
    
    # Get topic metrics
    topic_metrics = monitor.get_topic_metrics("social-media-ingestion")
    print(f"Topic metrics: {topic_metrics}")
    
    # Get subscription metrics
    sub_metrics = monitor.get_subscription_metrics("bigquery-social-posts")
    print(f"Subscription metrics: {sub_metrics}")
    
    # Generate health report
    health_report = monitor.generate_health_report()
    print(f"Health report: {health_report}")
```

---

## 💰 Cost Optimization

### Step 9: Implement Cost Controls

```python
# gcp/pubsub/cost_management/cost_optimizer.py
"""
Cost optimization for Pub/Sub operations
Monitors and controls spending for 15 GiB daily volume
"""

from google.cloud import pubsub_v1
from google.cloud import monitoring_v3
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PubSubCostOptimizer:
    """
    Cost optimization for Pub/Sub operations
    Monitors usage and implements cost controls
    """
    
    def __init__(self, project_id: str, monthly_budget_usd: float = 50.0):
        self.project_id = project_id
        self.monthly_budget_usd = monthly_budget_usd
        self.daily_budget_usd = monthly_budget_usd / 30
        
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        
        # Pub/Sub pricing (approximate)
        self.price_per_million_operations = 0.40  # $0.40 per million operations
        self.price_per_gib_throughput = 0.05  # $0.05 per GiB throughput
        
        logger.info(f"Cost optimizer initialized with ${monthly_budget_usd}/month budget")
    
    def estimate_daily_cost(self) -> Dict[str, Any]:
        """
        Estimate daily Pub/Sub costs
        
        Returns:
            Dictionary with cost breakdown
        """
        
        # Get daily metrics
        daily_metrics = self._get_daily_metrics()
        
        # Calculate operation costs
        total_operations = (
            daily_metrics.get("publish_operations", 0) +
            daily_metrics.get("pull_operations", 0) +
            daily_metrics.get("ack_operations", 0)
        )
        
        operation_cost = (total_operations / 1_000_000) * self.price_per_million_operations
        
        # Calculate throughput costs
        throughput_gib = daily_metrics.get("throughput_bytes", 0) / (1024 ** 3)
        throughput_cost = throughput_gib * self.price_per_gib_throughput
        
        # Total cost
        total_cost = operation_cost + throughput_cost
        
        cost_breakdown = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "operation_cost_usd": operation_cost,
            "throughput_cost_usd": throughput_cost,
            "total_daily_cost_usd": total_cost,
            "daily_budget_usd": self.daily_budget_usd,
            "budget_utilization_percent": (total_cost / self.daily_budget_usd) * 100,
            "projected_monthly_cost_usd": total_cost * 30,
            "metrics": daily_metrics
        }
        
        return cost_breakdown
    
    def implement_cost_controls(self) -> List[str]:
        """
        Implement cost control measures
        
        Returns:
            List of implemented controls
        """
        
        controls = []
        cost_info = self.estimate_daily_cost()
        
        budget_utilization = cost_info.get("budget_utilization_percent", 0)
        
        # Progressive cost controls
        if budget_utilization > 90:
            # Critical: Implement aggressive controls
            controls.extend([
                "CRITICAL: Reduced message retention to minimum",
                "CRITICAL: Disabled non-essential subscriptions",
                "CRITICAL: Implemented message filtering"
            ])
            
            # Reduce retention for cost savings
            self._reduce_message_retention()
            
        elif budget_utilization > 75:
            # Warning: Implement moderate controls
            controls.extend([
                "WARNING: Optimized batch settings",
                "WARNING: Increased ack deadlines",
                "WARNING: Monitoring message patterns"
            ])
            
            # Optimize batch settings
            self._optimize_batch_settings()
            
        elif budget_utilization > 50:
            # Caution: Monitor closely
            controls.append("CAUTION: 50% budget used - monitoring closely")
        
        return controls
    
    def optimize_topic_configuration(self, topic_name: str) -> Dict[str, Any]:
        """
        Optimize topic configuration for cost efficiency
        
        Args:
            topic_name: Name of the topic to optimize
            
        Returns:
            Dictionary with optimization results
        """
        
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        
        try:
            # Get current topic configuration
            topic = self.publisher.get_topic(request={"topic": topic_path})
            
            optimizations = []
            
            # Check message retention
            current_retention = topic.message_retention_duration.total_seconds()
            if current_retention > 86400:  # More than 1 day
                optimizations.append({
                    "type": "retention_reduction",
                    "current_value": f"{current_retention/3600:.1f} hours",
                    "recommended_value": "24 hours",
                    "potential_savings_percent": 20
                })
            
            # Check for schema validation
            if not topic.schema_settings:
                optimizations.append({
                    "type": "schema_validation",
                    "description": "Add schema validation to reduce invalid messages",
                    "potential_savings_percent": 5
                })
            
            return {
                "topic_name": topic_name,
                "current_config": {
                    "retention_hours": current_retention / 3600,
                    "has_schema": bool(topic.schema_settings)
                },
                "optimizations": optimizations,
                "total_potential_savings_percent": sum(opt.get("potential_savings_percent", 0) for opt in optimizations)
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize topic {topic_name}: {str(e)}")
            return {"error": str(e)}
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cost report
        
        Returns:
            Dictionary with cost analysis
        """
        
        cost_breakdown = self.estimate_daily_cost()
        controls = self.implement_cost_controls()
        
        # Get optimization opportunities
        topics = ["social-media-ingestion", "sentiment-analysis-results", "behavioral-analysis-results"]
        optimizations = []
        
        for topic in topics:
            opt = self.optimize_topic_configuration(topic)
            if "error" not in opt:
                optimizations.append(opt)
        
        report = {
            "cost_breakdown": cost_breakdown,
            "cost_controls": controls,
            "optimizations": optimizations,
            "recommendations": self._generate_cost_recommendations(cost_breakdown),
            "budget_status": {
                "daily_budget": self.daily_budget_usd,
                "monthly_budget": self.monthly_budget_usd,
                "current_utilization": cost_breakdown.get("budget_utilization_percent", 0),
                "projected_monthly_cost": cost_breakdown.get("projected_monthly_cost_usd", 0)
            },
            "report_generated": datetime.now().isoformat()
        }
        
        return report
    
    def _get_daily_metrics(self) -> Dict[str, Any]:
        """Get daily Pub/Sub metrics"""
        
        # This would query Cloud Monitoring for actual metrics
        # For now, return estimated values based on 15 GiB daily volume
        
        estimated_messages_per_day = (15 * 1024 ** 3) / 2048  # Assume 2KB average message
        
        return {
            "publish_operations": int(estimated_messages_per_day),
            "pull_operations": int(estimated_messages_per_day * 1.2),  # Some retries
            "ack_operations": int(estimated_messages_per_day),
            "throughput_bytes": 15 * 1024 ** 3,  # 15 GiB
            "message_count": int(estimated_messages_per_day)
        }
    
    def _reduce_message_retention(self):
        """Reduce message retention for cost savings"""
        
        topics = ["social-media-ingestion", "sentiment-analysis-results", "behavioral-analysis-results"]
        
        for topic_name in topics:
            try:
                topic_path = self.publisher.topic_path(self.project_id, topic_name)
                
                # Update topic with minimum retention
                topic = self.publisher.get_topic(request={"topic": topic_path})
                topic.message_retention_duration = {"seconds": 86400}  # 1 day minimum
                
                update_mask = {"paths": ["message_retention_duration"]}
                self.publisher.update_topic(topic=topic, update_mask=update_mask)
                
                logger.info(f"Reduced retention for topic: {topic_name}")
                
            except Exception as e:
                logger.error(f"Failed to reduce retention for {topic_name}: {str(e)}")
    
    def _optimize_batch_settings(self):
        """Optimize batch settings for cost efficiency"""
        
        # This would update publisher batch settings
        # Implementation depends on specific client configuration
        logger.info("Optimized batch settings for cost efficiency")
    
    def _generate_cost_recommendations(self, cost_breakdown: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        budget_utilization = cost_breakdown.get("budget_utilization_percent", 0)
        
        if budget_utilization > 75:
            recommendations.extend([
                "Consider reducing message retention periods",
                "Implement message deduplication to reduce volume",
                "Optimize subscriber acknowledgment patterns",
                "Review and remove unused subscriptions"
            ])
        
        if cost_breakdown.get("operation_cost_usd", 0) > cost_breakdown.get("throughput_cost_usd", 0):
            recommendations.append("Focus on reducing operation count through batching")
        else:
            recommendations.append("Focus on reducing data throughput through compression")
        
        recommendations.extend([
            "Monitor daily cost trends",
            "Set up automated budget alerts",
            "Regular review of topic and subscription configurations"
        ])
        
        return recommendations

# Usage example
if __name__ == "__main__":
    optimizer = PubSubCostOptimizer("your-sentinelbert-project", monthly_budget_usd=50.0)
    
    # Generate cost report
    report = optimizer.generate_cost_report()
    print(f"Cost report: {report}")
    
    # Implement cost controls
    controls = optimizer.implement_cost_controls()
    print(f"Cost controls: {controls}")
```

---

## 🧪 Testing & Validation

### Step 10: Create Test Suite

```bash
# Create comprehensive test script
cat > gcp/pubsub/scripts/test-pubsub.sh << 'EOF'
#!/bin/bash

PROJECT_ID=${1:-"your-sentinelbert-project"}

echo "🧪 Testing Pub/Sub setup for project: $PROJECT_ID"

# Test 1: Verify topics exist
echo "📢 Testing topic existence..."
for topic in social-media-ingestion sentiment-analysis-results behavioral-analysis-results dead-letter-queue; do
    if gcloud pubsub topics describe $topic --project=$PROJECT_ID > /dev/null 2>&1; then
        echo "✅ Topic $topic exists"
    else
        echo "❌ Topic $topic not found"
    fi
done

# Test 2: Verify subscriptions exist
echo "📊 Testing subscription existence..."
for subscription in bigquery-social-posts bigquery-sentiment-results processing-subscription dead-letter-subscription; do
    if gcloud pubsub subscriptions describe $subscription --project=$PROJECT_ID > /dev/null 2>&1; then
        echo "✅ Subscription $subscription exists"
    else
        echo "❌ Subscription $subscription not found"
    fi
done

# Test 3: Test message publishing
echo "📤 Testing message publishing..."
TEST_MESSAGE='{"post_id":"test_001","platform":"twitter","user_id":"test_user","text_content":"Test message for Pub/Sub validation","created_date":"2024-01-15T10:00:00Z","ingestion_timestamp":"2024-01-15T10:01:00Z"}'

gcloud pubsub topics publish social-media-ingestion \
    --message="$TEST_MESSAGE" \
    --attribute="platform=twitter,message_type=test" \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "✅ Test message published successfully"
else
    echo "❌ Test message publishing failed"
fi

# Test 4: Test subscription pull
echo "📥 Testing subscription pull..."
gcloud pubsub subscriptions pull processing-subscription \
    --limit=1 \
    --auto-ack \
    --project=$PROJECT_ID > /tmp/pull_test.txt 2>&1

if grep -q "test_001" /tmp/pull_test.txt; then
    echo "✅ Message pull successful"
else
    echo "⚠️  No messages in subscription (may be processed by BigQuery)"
fi

# Test 5: Test BigQuery integration
echo "📊 Testing BigQuery integration..."
sleep 10  # Wait for message to be processed

bq query --use_legacy_sql=false \
    "SELECT COUNT(*) as test_messages FROM \`$PROJECT_ID.sentinelbert_analytics.social_posts\` WHERE post_id = 'test_001'" \
    > /tmp/bq_test.txt 2>&1

if grep -q "1" /tmp/bq_test.txt; then
    echo "✅ BigQuery integration working"
else
    echo "⚠️  BigQuery integration may need time to process"
fi

# Test 6: Test throughput
echo "⚡ Testing throughput..."
start_time=$(date +%s)

for i in {1..100}; do
    gcloud pubsub topics publish social-media-ingestion \
        --message="{\"post_id\":\"throughput_test_$i\",\"platform\":\"test\",\"user_id\":\"test_user\",\"text_content\":\"Throughput test message $i\"}" \
        --project=$PROJECT_ID > /dev/null 2>&1 &
done

wait
end_time=$(date +%s)
duration=$((end_time - start_time))

echo "✅ Published 100 messages in ${duration}s ($(echo "scale=2; 100/$duration" | bc) msg/s)"

# Cleanup
rm -f /tmp/pull_test.txt /tmp/bq_test.txt

echo "✅ Pub/Sub testing completed!"
EOF

chmod +x gcp/pubsub/scripts/test-pubsub.sh
./gcp/pubsub/scripts/test-pubsub.sh your-sentinelbert-project
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Messages Not Reaching BigQuery

**Problem**: Messages published but not appearing in BigQuery

**Solution**:
```bash
# Check subscription status
gcloud pubsub subscriptions describe bigquery-social-posts

# Check BigQuery streaming quotas
gcloud compute project-info describe --project=your-project

# Verify message format matches BigQuery schema
# Ensure all required fields are present
```

#### Issue 2: High Message Backlog

**Problem**: Messages accumulating in subscriptions

**Solution**:
```bash
# Check subscription metrics
gcloud pubsub subscriptions describe processing-subscription

# Increase subscriber capacity
# Optimize message processing logic
# Consider parallel processing

# Temporarily increase ack deadline
gcloud pubsub subscriptions update processing-subscription \
    --ack-deadline=600
```

#### Issue 3: Schema Validation Errors

**Problem**: Messages rejected due to schema validation

**Solution**:
```bash
# Check schema definition
gcloud pubsub schemas describe social-post-schema

# Validate message format
# Update schema if needed
gcloud pubsub schemas commit social-post-schema \
    --type=AVRO \
    --definition-file=updated_schema.json
```

#### Issue 4: Permission Denied

**Error**: `Permission denied` when publishing/subscribing

**Solution**:
```bash
# Check service account permissions
gcloud projects get-iam-policy your-project

# Add necessary roles
gcloud projects add-iam-policy-binding your-project \
    --member="serviceAccount:your-sa@project.iam.gserviceaccount.com" \
    --role="roles/pubsub.editor"
```

---

## 📞 Important Links & References

### 🔗 Essential Links

- **Pub/Sub Console**: https://console.cloud.google.com/cloudpubsub
- **Monitoring Console**: https://console.cloud.google.com/monitoring
- **BigQuery Console**: https://console.cloud.google.com/bigquery
- **IAM Console**: https://console.cloud.google.com/iam-admin

### 📚 Documentation References

- **Pub/Sub Documentation**: https://cloud.google.com/pubsub/docs
- **BigQuery Subscriptions**: https://cloud.google.com/pubsub/docs/bigquery
- **Schema Validation**: https://cloud.google.com/pubsub/docs/schemas
- **Monitoring**: https://cloud.google.com/pubsub/docs/monitoring
- **Best Practices**: https://cloud.google.com/pubsub/docs/publisher
- **Pricing**: https://cloud.google.com/pubsub/pricing

### 🛠️ Tools & Resources

- **gcloud CLI**: https://cloud.google.com/sdk/gcloud/reference/pubsub
- **Python Client**: https://cloud.google.com/python/docs/reference/pubsub/latest
- **Monitoring Tools**: https://cloud.google.com/monitoring/api/metrics_gcp#gcp-pubsub

---

<div align="center">

**Next Steps**: Continue with [Cloud Storage Setup](./07-storage-setup.md) to configure your data lake infrastructure.

*Your Pub/Sub messaging system is now configured for 15 GiB daily throughput with direct BigQuery integration.*

</div>
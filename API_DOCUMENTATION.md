# SentinentalBERT API Documentation

<div align="center">

![API Version](https://img.shields.io/badge/API%20Version-v1.0.0-blue.svg)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-green.svg)
![Status](https://img.shields.io/badge/Status-Development-yellow.svg)

**Comprehensive REST API for Social Media Sentiment Analysis**

[🚀 Quick Start](#-quick-start) • [🔐 Authentication](#-authentication) • [📊 Endpoints](#-endpoints) • [📝 Examples](#-examples) • [🔧 SDKs](#-sdks)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [🔐 Authentication](#-authentication)
- [📊 Core Endpoints](#-core-endpoints)
- [🤖 NLP Service API](#-nlp-service-api)
- [📱 Social Media APIs](#-social-media-apis)
- [👥 User Management](#-user-management)
- [📈 Analytics & Reporting](#-analytics--reporting)
- [⚙️ System Administration](#️-system-administration)
- [📝 Request/Response Examples](#-requestresponse-examples)
- [🔧 Error Handling](#-error-handling)
- [📊 Rate Limiting](#-rate-limiting)
- [🔒 Security](#-security)
- [🧪 Testing](#-testing)
- [📚 SDKs & Libraries](#-sdks--libraries)

---

## 🎯 Overview

The SentinentalBERT API provides comprehensive access to advanced social media sentiment analysis, behavioral pattern detection, and influence scoring capabilities. Built with privacy compliance and legal authentication in mind, it offers enterprise-grade features for monitoring and analyzing social media content across multiple platforms.

### 🌟 Key Features

- **Real-time Sentiment Analysis**: Process text with advanced BERT models
- **Behavioral Pattern Detection**: Identify coordinated inauthentic behavior
- **Multi-platform Integration**: Support for X.com, Reddit, Instagram, YouTube
- **Privacy Compliance**: GDPR-compliant data processing with audit trails
- **Scalable Architecture**: High-throughput processing with auto-scaling
- **Comprehensive Analytics**: Detailed reporting and visualization capabilities

### 🏗️ API Architecture

```mermaid
graph TB
    subgraph "Client Applications"
        A[Web Dashboard]
        B[Mobile App]
        C[Third-party Integration]
    end
    
    subgraph "API Gateway"
        D[Nginx Reverse Proxy]
        E[Rate Limiting]
        F[Authentication]
    end
    
    subgraph "Core Services"
        G[Backend API<br/>Spring Boot]
        H[NLP Service<br/>FastAPI]
        I[Ingestion Service<br/>Rust]
    end
    
    subgraph "Data Layer"
        J[PostgreSQL]
        K[Redis Cache]
        L[Elasticsearch]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
    G --> J
    H --> K
    I --> L
```

---

## 🚀 Quick Start

### Base URLs

| Environment | Base URL | Description |
|-------------|----------|-------------|
| **Development** | `http://localhost:8080/api/v1` | Local development server |
| **Staging** | `https://staging-api.sentinelbert.com/v1` | Staging environment |
| **Production** | `https://api.sentinelbert.com/v1` | Production environment |

### Making Your First Request

```bash
# 1. Get authentication token
curl -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# 2. Use token for API requests
curl -X POST "http://localhost:8080/api/v1/analyze/sentiment" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["I love this product!", "This service is terrible."],
    "include_confidence": true
  }'
```

### Response Format

All API responses follow a consistent structure:

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789",
    "processing_time_ms": 245.7,
    "api_version": "v1.0.0"
  },
  "pagination": {
    // Only present for paginated responses
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

## 🔐 Authentication

### JWT Token Authentication

SentinentalBERT uses JWT (JSON Web Token) based authentication for secure API access.

#### Login Endpoint

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "remember_me": boolean
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "user_123",
      "username": "john_doe",
      "email": "john@example.com",
      "roles": ["analyst", "user"]
    }
  }
}
```

#### Token Refresh

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "string"
}
```

#### Using Authentication

Include the JWT token in the Authorization header for all authenticated requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API Key Authentication (Alternative)

For server-to-server communication, you can use API keys:

```http
X-API-Key: your_api_key_here
```

---

## 📊 Core Endpoints

### Health Check

Check the health status of all services.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "database": "connected",
      "cache": "connected",
      "nlp_service": "healthy",
      "ingestion_service": "healthy"
    },
    "uptime_seconds": 86400,
    "version": "1.0.0"
  }
}
```

### System Information

Get system information and statistics.

```http
GET /api/v1/system/info
```

**Response:**
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "build_date": "2024-01-15T10:00:00Z",
    "environment": "development",
    "features": {
      "sentiment_analysis": true,
      "behavioral_analysis": true,
      "real_time_processing": true
    },
    "statistics": {
      "total_posts_analyzed": 1500000,
      "total_users": 2500,
      "active_queries": 45
    }
  }
}
```

---

## 🤖 NLP Service API

### Sentiment Analysis

Analyze sentiment of text content using advanced BERT models.

#### Batch Sentiment Analysis

```http
POST /api/v1/analyze/sentiment
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "texts": [
    "I absolutely love this new product!",
    "This service is terrible and unreliable.",
    "The weather is nice today."
  ],
  "options": {
    "include_confidence": true,
    "include_emotions": false,
    "model_version": "v1.2.0",
    "language": "auto"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "text_id": 0,
        "text": "I absolutely love this new product!",
        "sentiment": {
          "label": "positive",
          "score": 0.92,
          "confidence": 0.89,
          "scores": {
            "positive": 0.92,
            "negative": 0.03,
            "neutral": 0.05
          }
        },
        "language": "en",
        "processing_time_ms": 245.7
      },
      {
        "text_id": 1,
        "text": "This service is terrible and unreliable.",
        "sentiment": {
          "label": "negative",
          "score": -0.85,
          "confidence": 0.91,
          "scores": {
            "positive": 0.02,
            "negative": 0.85,
            "neutral": 0.13
          }
        },
        "language": "en",
        "processing_time_ms": 198.3
      }
    ],
    "model_version": "v1.2.0",
    "total_processing_time_ms": 467.2
  }
}
```

#### Real-time Sentiment Analysis

```http
POST /api/v1/analyze/sentiment/realtime
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "text": "This is amazing!",
  "options": {
    "fast_mode": true,
    "cache_result": true
  }
}
```

### Behavioral Pattern Analysis

Detect coordinated inauthentic behavior and bot-like patterns.

```http
POST /api/v1/analyze/behavior
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "posts": [
    {
      "id": "post_123",
      "text": "Sample post content",
      "author": {
        "id": "user_456",
        "username": "john_doe",
        "followers_count": 1500,
        "verified": false,
        "account_age_days": 365
      },
      "metadata": {
        "timestamp": "2024-01-15T10:30:00Z",
        "platform": "twitter",
        "engagement": {
          "likes": 25,
          "shares": 5,
          "comments": 3
        }
      }
    }
  ],
  "analysis_types": [
    "amplification",
    "coordination",
    "bot_detection",
    "astroturfing"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "post_id": "post_123",
        "behavioral_patterns": [
          {
            "pattern_type": "authentic_engagement",
            "score": 0.85,
            "confidence": 0.78,
            "indicators": [
              "natural_language_patterns",
              "organic_engagement_timing",
              "diverse_interaction_patterns"
            ],
            "risk_level": "low"
          }
        ],
        "bot_probability": 0.12,
        "influence_score": 0.34,
        "authenticity_score": 0.88
      }
    ],
    "analysis_summary": {
      "total_posts": 1,
      "suspicious_posts": 0,
      "average_authenticity": 0.88,
      "patterns_detected": ["authentic_engagement"]
    }
  }
}
```

### Emotion Detection

Analyze emotional content in text using multi-dimensional emotion models.

```http
POST /api/v1/analyze/emotions
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "texts": [
    "I'm so excited about this opportunity!",
    "I'm really worried about the future."
  ],
  "emotion_model": "ekman_8", // joy, anger, fear, sadness, disgust, surprise, trust, anticipation
  "include_intensity": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "text_id": 0,
        "emotions": {
          "joy": 0.89,
          "anticipation": 0.76,
          "trust": 0.45,
          "surprise": 0.23,
          "anger": 0.02,
          "fear": 0.01,
          "sadness": 0.01,
          "disgust": 0.01
        },
        "dominant_emotion": "joy",
        "emotional_intensity": 0.82,
        "emotional_complexity": 0.34
      }
    ]
  }
}
```

---

## 📱 Social Media APIs

### Search and Monitor

Search for content across multiple social media platforms.

#### Multi-platform Search

```http
POST /api/v1/social/search
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "query": {
    "keywords": ["climate change", "global warming"],
    "hashtags": ["#climatechange", "#environment"],
    "mentions": ["@greta"],
    "exclude_keywords": ["spam", "advertisement"]
  },
  "platforms": ["twitter", "reddit", "instagram"],
  "filters": {
    "language": "en",
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-15T23:59:59Z"
    },
    "location": {
      "country": "US",
      "radius_km": 100,
      "coordinates": {
        "lat": 40.7128,
        "lng": -74.0060
      }
    },
    "engagement": {
      "min_likes": 10,
      "min_shares": 5
    }
  },
  "options": {
    "include_sentiment": true,
    "include_behavioral_analysis": true,
    "max_results": 100,
    "sort_by": "relevance" // relevance, date, engagement
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "post_789",
        "platform": "twitter",
        "text": "Climate change is the biggest challenge of our time. We need immediate action! #climatechange",
        "author": {
          "id": "user_456",
          "username": "climate_activist",
          "display_name": "Climate Activist",
          "verified": true,
          "followers_count": 15000
        },
        "metadata": {
          "created_at": "2024-01-15T14:30:00Z",
          "url": "https://twitter.com/climate_activist/status/123456789",
          "engagement": {
            "likes": 245,
            "shares": 67,
            "comments": 23
          },
          "location": {
            "country": "US",
            "city": "New York"
          }
        },
        "analysis": {
          "sentiment": {
            "label": "positive",
            "score": 0.78,
            "confidence": 0.85
          },
          "behavioral_patterns": [
            {
              "pattern_type": "authentic_advocacy",
              "score": 0.92,
              "confidence": 0.88
            }
          ],
          "topics": ["climate_change", "environmental_activism"],
          "language": "en"
        }
      }
    ],
    "summary": {
      "total_results": 1247,
      "platforms": {
        "twitter": 856,
        "reddit": 234,
        "instagram": 157
      },
      "sentiment_distribution": {
        "positive": 0.45,
        "negative": 0.32,
        "neutral": 0.23
      },
      "top_topics": ["climate_change", "renewable_energy", "sustainability"]
    }
  },
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total": 1247,
    "total_pages": 13
  }
}
```

#### Real-time Monitoring

Set up real-time monitoring for specific keywords or topics.

```http
POST /api/v1/social/monitor
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Climate Change Monitor",
  "description": "Monitor climate change discussions",
  "query": {
    "keywords": ["climate change", "global warming"],
    "hashtags": ["#climatechange"]
  },
  "platforms": ["twitter", "reddit"],
  "filters": {
    "language": "en",
    "min_engagement": 5
  },
  "notifications": {
    "webhook_url": "https://your-webhook.com/sentinelbert",
    "email": "alerts@yourcompany.com",
    "threshold": {
      "volume_spike": 2.0,
      "sentiment_change": 0.3
    }
  },
  "schedule": {
    "active": true,
    "frequency": "realtime" // realtime, hourly, daily
  }
}
```

### Platform-specific Endpoints

#### Twitter/X.com Integration

```http
GET /api/v1/social/twitter/user/{username}
Authorization: Bearer YOUR_JWT_TOKEN
```

```http
POST /api/v1/social/twitter/analyze-timeline
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "username": "climate_activist",
  "tweet_count": 50,
  "include_replies": false,
  "analysis_options": {
    "sentiment_trends": true,
    "topic_evolution": true,
    "engagement_patterns": true
  }
}
```

#### Reddit Integration

```http
GET /api/v1/social/reddit/subreddit/{subreddit_name}
Authorization: Bearer YOUR_JWT_TOKEN
```

```http
POST /api/v1/social/reddit/analyze-discussion
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "subreddit": "climate",
  "post_id": "abc123",
  "analysis_depth": "full", // basic, standard, full
  "include_comment_tree": true
}
```

---

## 👥 User Management

### User Registration

```http
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "organization": "Acme Corp",
  "role": "analyst",
  "terms_accepted": true,
  "privacy_policy_accepted": true
}
```

### User Profile Management

```http
GET /api/v1/users/profile
Authorization: Bearer YOUR_JWT_TOKEN
```

```http
PUT /api/v1/users/profile
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "preferences": {
    "timezone": "America/New_York",
    "language": "en",
    "notifications": {
      "email": true,
      "push": false,
      "webhook": true
    }
  }
}
```

### API Key Management

```http
POST /api/v1/users/api-keys
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Production API Key",
  "description": "API key for production integration",
  "permissions": ["read", "analyze"],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

---

## 📈 Analytics & Reporting

### Dashboard Data

Get aggregated data for dashboard visualization.

```http
GET /api/v1/analytics/dashboard
Authorization: Bearer YOUR_JWT_TOKEN
Query Parameters:
  - date_range: 7d, 30d, 90d, custom
  - start_date: 2024-01-01
  - end_date: 2024-01-15
  - platforms: twitter,reddit,instagram
  - metrics: sentiment,engagement,volume
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_posts": 125000,
      "total_users": 45000,
      "sentiment_score": 0.23,
      "engagement_rate": 0.045
    },
    "time_series": {
      "daily_volume": [
        {"date": "2024-01-01", "count": 1250},
        {"date": "2024-01-02", "count": 1340}
      ],
      "sentiment_trend": [
        {"date": "2024-01-01", "positive": 0.45, "negative": 0.32, "neutral": 0.23},
        {"date": "2024-01-02", "positive": 0.48, "negative": 0.29, "neutral": 0.23}
      ]
    },
    "top_topics": [
      {"topic": "climate_change", "count": 5670, "sentiment": 0.34},
      {"topic": "renewable_energy", "count": 3450, "sentiment": 0.67}
    ],
    "platform_breakdown": {
      "twitter": {"posts": 75000, "sentiment": 0.25},
      "reddit": {"posts": 35000, "sentiment": 0.18},
      "instagram": {"posts": 15000, "sentiment": 0.45}
    }
  }
}
```

### Custom Reports

Generate custom analytical reports.

```http
POST /api/v1/analytics/reports
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Weekly Climate Report",
  "type": "sentiment_analysis",
  "parameters": {
    "query": {
      "keywords": ["climate change"],
      "date_range": {
        "start": "2024-01-08T00:00:00Z",
        "end": "2024-01-15T23:59:59Z"
      }
    },
    "metrics": [
      "sentiment_distribution",
      "volume_trends",
      "top_influencers",
      "geographic_distribution"
    ],
    "format": "json", // json, pdf, csv
    "include_visualizations": true
  },
  "delivery": {
    "email": "reports@yourcompany.com",
    "webhook": "https://your-webhook.com/reports"
  }
}
```

### Export Data

Export analyzed data in various formats.

```http
POST /api/v1/analytics/export
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "query": {
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-15T23:59:59Z"
    },
    "platforms": ["twitter", "reddit"],
    "include_analysis": true
  },
  "format": "csv", // csv, json, xlsx
  "fields": [
    "post_id",
    "text",
    "author",
    "timestamp",
    "sentiment_score",
    "platform"
  ],
  "compression": "gzip"
}
```

---

## ⚙️ System Administration

### System Configuration

```http
GET /api/v1/admin/config
Authorization: Bearer YOUR_JWT_TOKEN
X-Admin-Role: administrator
```

```http
PUT /api/v1/admin/config
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
X-Admin-Role: administrator

{
  "rate_limits": {
    "requests_per_minute": 100,
    "requests_per_hour": 1000
  },
  "features": {
    "real_time_processing": true,
    "behavioral_analysis": true
  },
  "data_retention": {
    "posts": 90,
    "logs": 30,
    "analytics": 365
  }
}
```

### System Metrics

```http
GET /api/v1/admin/metrics
Authorization: Bearer YOUR_JWT_TOKEN
X-Admin-Role: administrator
```

### User Management (Admin)

```http
GET /api/v1/admin/users
Authorization: Bearer YOUR_JWT_TOKEN
X-Admin-Role: administrator
Query Parameters:
  - page: 1
  - per_page: 50
  - role: analyst,admin,user
  - status: active,inactive,suspended
```

```http
PUT /api/v1/admin/users/{user_id}/role
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
X-Admin-Role: administrator

{
  "role": "analyst",
  "permissions": ["read", "analyze", "export"]
}
```

---

## 🔧 Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
      "field": "texts",
      "issue": "Array must contain at least 1 item",
      "provided_value": []
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z",
    "documentation_url": "https://docs.sentinelbert.com/errors/validation-error"
  }
}
```

### HTTP Status Codes

| Status Code | Description | Usage |
|-------------|-------------|-------|
| **200** | OK | Successful request |
| **201** | Created | Resource created successfully |
| **400** | Bad Request | Invalid request data |
| **401** | Unauthorized | Authentication required |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **422** | Unprocessable Entity | Validation errors |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `AUTHENTICATION_REQUIRED` | No authentication token provided | Include Authorization header |
| `INVALID_TOKEN` | JWT token is invalid or expired | Refresh or obtain new token |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions | Contact administrator |
| `VALIDATION_ERROR` | Request data validation failed | Check request format |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist | Check resource ID |
| `SERVICE_UNAVAILABLE` | External service unavailable | Retry later |
| `QUOTA_EXCEEDED` | API quota limit reached | Upgrade plan or wait |

---

## 📊 Rate Limiting

### Rate Limit Headers

All API responses include rate limiting information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248600
X-RateLimit-Window: 3600
```

### Rate Limit Tiers

| Tier | Requests/Hour | Requests/Day | Concurrent | Features |
|------|---------------|--------------|------------|----------|
| **Free** | 100 | 1,000 | 5 | Basic sentiment analysis |
| **Basic** | 1,000 | 10,000 | 10 | + Behavioral analysis |
| **Pro** | 10,000 | 100,000 | 25 | + Real-time monitoring |
| **Enterprise** | Custom | Custom | Custom | + Custom models |

### Rate Limit Bypass

For high-volume applications, contact support for rate limit increases or custom quotas.

---

## 🔒 Security

### HTTPS/TLS

All API communications must use HTTPS with TLS 1.2 or higher.

### Request Signing (Optional)

For enhanced security, requests can be signed using HMAC-SHA256:

```http
X-Signature: sha256=5d41402abc4b2a76b9719d911017c592
X-Timestamp: 1642248600
```

### IP Whitelisting

Enterprise customers can restrict API access to specific IP addresses.

### CORS Policy

The API supports CORS for web applications:

```http
Access-Control-Allow-Origin: https://your-domain.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, X-API-Key
```

---

## 🧪 Testing

### Test Environment

Use the test environment for development and testing:

- **Base URL**: `https://test-api.sentinelbert.com/v1`
- **Test Data**: Pre-populated with sample data
- **Rate Limits**: Relaxed for testing
- **Authentication**: Test tokens available

### Postman Collection

Download our Postman collection for easy API testing:

```bash
curl -o sentinelbert-api.postman_collection.json \
  https://api.sentinelbert.com/v1/docs/postman
```

### OpenAPI Specification

Access the complete OpenAPI 3.0 specification:

```bash
curl https://api.sentinelbert.com/v1/openapi.json
```

---

## 📚 SDKs & Libraries

### Official SDKs

| Language | Repository | Documentation | Status |
|----------|------------|---------------|--------|
| **Python** | [sentinelbert-python](https://github.com/sentinelbert/python-sdk) | [Docs](https://python-sdk.sentinelbert.com) | ✅ Stable |
| **JavaScript** | [sentinelbert-js](https://github.com/sentinelbert/js-sdk) | [Docs](https://js-sdk.sentinelbert.com) | ✅ Stable |
| **Java** | [sentinelbert-java](https://github.com/sentinelbert/java-sdk) | [Docs](https://java-sdk.sentinelbert.com) | 🔄 Beta |
| **Go** | [sentinelbert-go](https://github.com/sentinelbert/go-sdk) | [Docs](https://go-sdk.sentinelbert.com) | 🔄 Beta |

### Python SDK Example

```python
from sentinelbert import SentinelBERTClient

# Initialize client
client = SentinelBERTClient(
    api_key="your_api_key_here",
    base_url="https://api.sentinelbert.com/v1"
)

# Analyze sentiment
result = client.analyze_sentiment([
    "I love this product!",
    "This service is terrible."
])

print(result.results[0].sentiment.label)  # "positive"
print(result.results[1].sentiment.score)  # -0.85
```

### JavaScript SDK Example

```javascript
import { SentinelBERTClient } from '@sentinelbert/js-sdk';

// Initialize client
const client = new SentinelBERTClient({
  apiKey: 'your_api_key_here',
  baseURL: 'https://api.sentinelbert.com/v1'
});

// Analyze sentiment
const result = await client.analyzeSentiment({
  texts: ['I love this product!', 'This service is terrible.'],
  options: { includeConfidence: true }
});

console.log(result.data.results[0].sentiment.label); // "positive"
```

---

## 📞 Support & Resources

### Documentation

- **API Reference**: https://docs.sentinelbert.com/api
- **Tutorials**: https://docs.sentinelbert.com/tutorials
- **Examples**: https://github.com/sentinelbert/examples
- **Changelog**: https://docs.sentinelbert.com/changelog

### Community

- **Discord**: https://discord.gg/sentinelbert
- **GitHub**: https://github.com/sentinelbert/api
- **Stack Overflow**: Tag `sentinelbert`
- **Reddit**: r/sentinelbert

### Support

- **Email**: api-support@sentinelbert.com
- **Status Page**: https://status.sentinelbert.com
- **Bug Reports**: https://github.com/sentinelbert/api/issues
- **Feature Requests**: https://feedback.sentinelbert.com

---

<div align="center">

**API Version**: v1.0.0  
**Last Updated**: January 15, 2024  
**Status**: Development  

*This documentation is automatically updated with each API release.*

</div>
# SentinelBERT API Reference

*Auto-generated API documentation*

## Overview

SentinelBERT provides RESTful APIs for social media sentiment analysis and behavioral pattern detection.

### Base URLs

- **Development**: `http://localhost:8080/api`
- **Production**: `https://your-domain.com/api`

### Authentication

All API endpoints require JWT authentication:

```
Authorization: Bearer <your-jwt-token>
```

## Core Endpoints

### Search API

**POST** `/api/v1/search`

Perform content searches across social media platforms.

```json
{
  "query": "climate change",
  "platforms": ["twitter", "reddit"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "sentiment_filter": "negative"
}
```

### Analytics API

**GET** `/api/v1/analytics/sentiment`

Get sentiment analysis results.

**GET** `/api/v1/analytics/trends`

Get trending topics and patterns.

### User Management API

**GET** `/api/v1/users`

List system users (admin only).

**POST** `/api/v1/users`

Create new user account.

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "timestamp": "2024-01-18T10:30:00Z"
}
```

## Error Handling

Error responses include appropriate HTTP status codes:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters"
  },
  "timestamp": "2024-01-18T10:30:00Z"
}
```

## Rate Limiting

- Standard endpoints: 100 requests/minute
- Search endpoints: 50 requests/minute
- Analysis endpoints: 20 requests/minute

---

*This documentation is automatically updated when API changes are detected.*

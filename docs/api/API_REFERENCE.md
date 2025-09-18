# SentinelBERT API Reference

## Overview

SentinelBERT provides RESTful APIs for social media sentiment analysis.

### Base URL
```
http://localhost:8080/api/v1
```

### Authentication
```
Authorization: Bearer <jwt-token>
```

## Endpoints

### Search API
- `POST /search` - Search social media content
- `GET /search/{id}` - Get search results
- `DELETE /search/{id}` - Delete search query

### Analytics API
- `GET /analytics/sentiment` - Get sentiment analysis
- `GET /analytics/trends` - Get trending topics
- `GET /analytics/influencers` - Get key influencers

### User Management
- `GET /users` - List users (admin only)
- `POST /users` - Create user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2024-01-18T10:30:00Z"
}
```

## Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

*For detailed API documentation, see the OpenAPI specification.*

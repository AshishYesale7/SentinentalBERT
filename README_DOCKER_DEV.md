# SentinentalBERT Docker Development Environment

This guide provides comprehensive instructions for setting up and running the SentinentalBERT project using Docker containers for development.

## 🚀 Quick Start

### Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (or legacy docker-compose 1.29+)
- **Git**: For cloning the repository
- **8GB+ RAM**: Recommended for running all services
- **10GB+ Disk Space**: For images and data

### One-Command Setup

```bash
# Clone and start the development environment
git clone https://github.com/bot-hexacon/SentinentalBERT.git
cd SentinentalBERT
./start-dev.sh
```

## 📋 Detailed Setup Instructions

### 1. Environment Configuration

Copy the development environment template:

```bash
cp .env.dev .env
```

Edit `.env` file to customize your configuration:

```bash
# Database passwords
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# API Keys (optional for development)
TWITTER_BEARER_TOKEN=your_twitter_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
# ... other API keys
```

### 2. Manual Docker Commands

If you prefer manual control over the startup process:

```bash
# Build the dashboard image
docker-compose -f docker-compose.dev.yml build streamlit-dashboard

# Start core services (databases)
docker-compose -f docker-compose.dev.yml up -d postgres redis elasticsearch

# Wait for databases to initialize (30-60 seconds)
docker-compose -f docker-compose.dev.yml logs postgres

# Start application services
docker-compose -f docker-compose.dev.yml up -d nlp-service backend-service evidence-service

# Start the main dashboard
docker-compose -f docker-compose.dev.yml up -d streamlit-dashboard

# Start monitoring tools
docker-compose -f docker-compose.dev.yml up -d adminer redis-commander prometheus grafana
```

### 3. Verify Installation

Check that all services are running:

```bash
docker-compose -f docker-compose.dev.yml ps
```

## 🌐 Service Access URLs

Once all services are running, you can access:

### Main Application
- **Streamlit Dashboard**: http://localhost:8501
  - Main viral content analysis interface
  - Real-time monitoring and detection
  - Evidence collection and reporting

### API Services
- **Backend API**: http://localhost:8080
  - RESTful API for all backend operations
  - Swagger UI: http://localhost:8080/swagger-ui.html
- **NLP Service**: http://localhost:8000
  - Sentiment analysis and text processing
  - API docs: http://localhost:8000/docs
- **Evidence Service**: http://localhost:8082
  - Evidence collection and storage
- **Ingestion Service**: http://localhost:8081
  - Social media data ingestion
- **Viral Detection**: http://localhost:8083
  - Viral content detection algorithms

### Database Administration
- **Adminer (PostgreSQL)**: http://localhost:8084
  - Server: `postgres`
  - Username: `sentinel`
  - Password: `sentinelpass123` (or your custom password)
  - Database: `sentinelbert`
- **Redis Commander**: http://localhost:8085
  - Redis database management interface

### Monitoring & Analytics
- **Prometheus**: http://localhost:9090
  - Metrics collection and monitoring
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`
  - Pre-configured dashboards for system monitoring
- **Elasticsearch**: http://localhost:9200
  - Search and analytics engine

## 🛠️ Development Workflow

### Starting Services

```bash
# Start all services
./start-dev.sh

# Start specific services only
docker-compose -f docker-compose.dev.yml up -d streamlit-dashboard nlp-service

# Start with logs visible
docker-compose -f docker-compose.dev.yml up streamlit-dashboard
```

### Stopping Services

```bash
# Stop all services
./start-dev.sh stop

# Or manually
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (clean slate)
docker-compose -f docker-compose.dev.yml down -v
```

### Viewing Logs

```bash
# All services
./start-dev.sh logs

# Specific service
./start-dev.sh logs streamlit-dashboard
docker-compose -f docker-compose.dev.yml logs -f streamlit-dashboard

# Multiple services
docker-compose -f docker-compose.dev.yml logs -f streamlit-dashboard nlp-service
```

### Restarting Services

```bash
# Restart all services
./start-dev.sh restart

# Restart specific service
docker-compose -f docker-compose.dev.yml restart streamlit-dashboard
```

## 🔧 Development Features

### Hot Reload

The development environment supports hot reload for:
- **Streamlit Dashboard**: Automatically reloads when Python files change
- **API Services**: Restart containers to pick up changes
- **Configuration**: Restart affected services after config changes

### Volume Mounts

Development volumes are mounted for easy editing:
- `./enhanced_viral_dashboard.py` → Container dashboard
- `./services/` → Service source code
- `./logs/` → Application logs
- `./evidence_storage/` → Evidence files
- `./temp_files/` → Temporary files

### Debug Mode

Enable debug features in `.env`:
```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENABLE_DEBUG_TOOLBAR=true
```

## 📊 Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Streamlit      │    │   Backend API   │    │   NLP Service   │
│  Dashboard      │◄──►│   (Spring)      │◄──►│   (FastAPI)     │
│  Port: 8501     │    │   Port: 8080    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │ Elasticsearch   │
│   Port: 5432    │    │   Port: 6379    │    │   Port: 9200    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using a port
lsof -i :8501
netstat -tulpn | grep 8501

# Kill process using port
kill -9 $(lsof -t -i:8501)
```

#### Memory Issues
```bash
# Check Docker memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Recommended: 8GB+ for full environment
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose -f docker-compose.dev.yml logs postgres

# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres
```

#### Service Won't Start
```bash
# Check service logs
docker-compose -f docker-compose.dev.yml logs [service-name]

# Rebuild service
docker-compose -f docker-compose.dev.yml build --no-cache [service-name]
docker-compose -f docker-compose.dev.yml up -d [service-name]
```

### Health Checks

```bash
# Check service health
docker-compose -f docker-compose.dev.yml ps

# Manual health checks
curl http://localhost:8501/_stcore/health  # Streamlit
curl http://localhost:8080/actuator/health # Backend
curl http://localhost:8000/health          # NLP Service
```

### Clean Reset

```bash
# Complete environment reset
./start-dev.sh clean

# Manual cleanup
docker-compose -f docker-compose.dev.yml down -v --rmi all
docker system prune -a --volumes
```

## 🔒 Security Notes

### Development Security

- **Default passwords** are used for development convenience
- **Ports are exposed** for easy access during development
- **CORS is enabled** for frontend development
- **CSRF protection is disabled** for API testing

### Production Considerations

- Change all default passwords
- Use environment-specific secrets
- Enable HTTPS/TLS
- Restrict port exposure
- Enable security features
- Use production Docker Compose file

## 📈 Performance Optimization

### Resource Allocation

Adjust resource limits in `docker-compose.dev.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 4G      # Increase for better performance
      cpus: '2.0'     # Allocate more CPU cores
    reservations:
      memory: 2G
      cpus: '1.0'
```

### Database Optimization

```bash
# PostgreSQL performance tuning
docker exec -it sentinelbert-postgres-dev psql -U sentinel -d sentinelbert -c "
  ALTER SYSTEM SET shared_buffers = '256MB';
  ALTER SYSTEM SET effective_cache_size = '1GB';
  SELECT pg_reload_conf();
"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
docker-compose -f docker-compose.dev.yml exec streamlit-dashboard python -m pytest tests/

# Run specific test
docker-compose -f docker-compose.dev.yml exec streamlit-dashboard python -m pytest tests/test_dashboard.py

# Run with coverage
docker-compose -f docker-compose.dev.yml exec streamlit-dashboard python -m pytest --cov=. tests/
```

### Integration Testing

```bash
# Test API endpoints
curl -X GET http://localhost:8080/api/health
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"text": "test"}'

# Test database connectivity
docker-compose -f docker-compose.dev.yml exec postgres psql -U sentinel -d sentinelbert -c "SELECT version();"
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in the development environment
4. Test thoroughly using the Docker setup
5. Submit a pull request

## 📞 Support

For issues with the Docker development environment:

1. Check the troubleshooting section above
2. Review service logs: `./start-dev.sh logs [service-name]`
3. Create an issue in the GitHub repository
4. Include relevant logs and system information

---

**Happy Development! 🚀**
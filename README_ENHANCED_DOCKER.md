# 🇮🇳 Enhanced SentinelBERT Docker Development Environment

## Indian Police Hackathon - Viral Tracking System

This enhanced Docker Compose setup provides a complete development environment for the SentinelBERT viral tracking system with VSCode integration, optimized for both Linux and macOS.

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (macOS) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **VSCode** with Docker extension (recommended)
- **8GB+ RAM** (16GB recommended)
- **10GB+ free disk space**

### One-Command Setup

```bash
./setup-enhanced-docker.sh
```

This script will:
- ✅ Check system requirements
- ✅ Create necessary directories
- ✅ Pull and build Docker images
- ✅ Start all services
- ✅ Test Twitter API connection
- ✅ Display access URLs

## 🏗️ Architecture Overview

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| **Enhanced Dashboard** | 12000, 12001, 8501 | Streamlit dashboard with viral tracking |
| **PostgreSQL** | 5432 | Primary database with enhanced schema |
| **Redis** | 6379 | Caching and session management |
| **Elasticsearch** | 9200, 9300 | Search and analytics engine |
| **Backend API** | 8080 | Spring Boot REST API |
| **NLP Service** | 8000 | Python NLP processing service |
| **Viral Detection** | 8083 | Enhanced viral tracking algorithms |
| **Evidence Service** | 8082 | Legal evidence collection |

### Development Tools

| Tool | Port | Credentials |
|------|------|-------------|
| **Adminer** | 8084 | Database management UI |
| **Redis Commander** | 8085 | admin/admin123 |
| **Elasticsearch Head** | 9100 | ES cluster management |
| **Grafana** | 3000 | admin/admin123 |
| **Prometheus** | 9090 | Metrics collection |
| **Jaeger** | 16686 | Distributed tracing |

## 🎯 Enhanced Features

### Viral Origin Tracking
- **Reverse Chronological Algorithm**: Traces content backwards through time
- **Network Traversal**: Maps influence networks and viral pathways  
- **Hybrid AI Analysis**: Combines multiple ML models for accuracy
- **Real-time Processing**: Live tracking with sub-second response times

### Court-Ready Evidence
- **Digital Signatures**: Cryptographic proof of evidence integrity
- **Chain of Custody**: Complete audit trail for legal proceedings
- **Automated Reports**: PDF generation with legal formatting
- **7-Year Retention**: Compliant with Indian legal requirements

### Social Media Integration
- **Twitter API v2**: Full access with provided credentials
- **Rate Limit Management**: Optimized for free tier usage
- **Multi-platform Support**: Twitter, Reddit, YouTube ready
- **Influence Scoring**: Advanced user influence calculations

## 🔧 Development Workflow

### VSCode Integration

1. **Open in VSCode**:
   ```bash
   code .
   ```

2. **Install Recommended Extensions**:
   - Python
   - Docker
   - YAML
   - SQL Tools

3. **Use Integrated Terminal**:
   - Environment variables auto-loaded
   - Docker Compose commands available
   - Database connections pre-configured

### Debugging

1. **Launch Dashboard**:
   - Press `F5` or use "Enhanced Dashboard" configuration
   - Breakpoints work in Python code
   - Live reload enabled

2. **Database Access**:
   - Use SQL Tools extension
   - Connection: "SentinelBERT PostgreSQL"
   - Or use Adminer at http://localhost:8084

3. **Log Monitoring**:
   ```bash
   docker-compose -f docker-compose.enhanced.yml logs -f
   ```

## 📊 Dashboard Access

### Primary Dashboard
- **URL**: http://localhost:12000
- **Features**: Full viral tracking interface
- **Tabs**: Analysis, Influence Network, Evidence, Reports

### Alternative Access
- **Port 12001**: Alternative dashboard port
- **Port 8501**: Standard Streamlit port

### Key Features
1. **Viral Origin Tracking Tab**:
   - Input: Username (@YesaleAshish) or Tweet URL
   - Algorithm: Select tracking method
   - Results: Interactive network visualization

2. **Evidence Collection**:
   - Automated screenshot capture
   - Digital signature generation
   - Legal report formatting

3. **Real-time Monitoring**:
   - Live viral coefficient tracking
   - Influence network updates
   - Performance metrics

## 🗄️ Database Schema

### Enhanced Tables
- `viral_tracking_sessions`: Main tracking records
- `viral_posts`: Social media content
- `viral_chains`: Propagation pathways
- `network_analysis`: Graph analytics
- `evidence_records`: Legal evidence
- `user_influence_scores`: Influence metrics

### Sample Queries
```sql
-- View active tracking sessions
SELECT * FROM viral_tracking_summary WHERE status = 'active';

-- Top influencers by platform
SELECT * FROM top_influencers WHERE platform = 'twitter' LIMIT 10;

-- Performance metrics
SELECT * FROM tracking_performance_summary;
```

## 🔐 Security & Compliance

### Data Protection
- **Encryption**: All data encrypted at rest and in transit
- **Access Control**: Role-based permissions
- **Audit Logging**: Complete activity tracking
- **GDPR Compliance**: Data retention and deletion policies

### Legal Requirements
- **Evidence Integrity**: SHA-256 hashing
- **Chain of Custody**: Immutable audit trail
- **Court Admissibility**: Formatted legal reports
- **Retention Policy**: 7-year automatic retention

## 🚀 Deployment Options

### Development (Current)
```bash
docker-compose -f docker-compose.enhanced.yml up -d
```

### Production
```bash
docker-compose -f docker-compose.yml up -d
```

### Scaling
```bash
docker-compose -f docker-compose.enhanced.yml up -d --scale viral-detection=3
```

## 🧪 Testing

### API Testing
```bash
# Test Twitter API connection
python3 test_twitter_api.py

# Run simple demo
python3 simple_demo_test.py

# Quick functionality test
python3 quick_demo_test.py
```

### Load Testing
```bash
# Start load test
./setup-enhanced-docker.sh test
```

### Health Checks
```bash
# Check service status
docker-compose -f docker-compose.enhanced.yml ps

# View service health
curl http://localhost:12000/_stcore/health
```

## 📈 Monitoring & Observability

### Metrics (Prometheus)
- **URL**: http://localhost:9090
- **Metrics**: API response times, error rates, resource usage
- **Alerts**: Automated threshold monitoring

### Dashboards (Grafana)
- **URL**: http://localhost:3000
- **Login**: admin/admin123
- **Dashboards**: System metrics, application performance, viral tracking analytics

### Tracing (Jaeger)
- **URL**: http://localhost:16686
- **Features**: Request tracing, performance bottlenecks, error tracking

## 🛠️ Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Check port usage
   netstat -tulpn | grep :12000
   
   # Kill conflicting process
   sudo kill -9 <PID>
   ```

2. **Memory Issues**:
   ```bash
   # Check Docker memory usage
   docker stats
   
   # Increase Docker memory limit in Docker Desktop
   ```

3. **Database Connection**:
   ```bash
   # Test database connection
   docker exec -it sentinelbert-postgres-enhanced psql -U sentinel -d sentinelbert
   ```

4. **Service Not Starting**:
   ```bash
   # Check logs
   docker-compose -f docker-compose.enhanced.yml logs <service-name>
   
   # Restart specific service
   docker-compose -f docker-compose.enhanced.yml restart <service-name>
   ```

### Performance Optimization

1. **Reduce Memory Usage**:
   - Edit `docker-compose.enhanced.yml`
   - Lower memory limits in `deploy.resources.limits`

2. **Disable Unused Services**:
   ```bash
   # Comment out services in docker-compose.enhanced.yml
   # Restart with reduced services
   ```

3. **Enable GPU Support**:
   ```bash
   # Set CUDA_VISIBLE_DEVICES in .env.enhanced
   export CUDA_VISIBLE_DEVICES=0
   ```

## 🔄 Maintenance

### Regular Tasks

1. **Update Images**:
   ```bash
   docker-compose -f docker-compose.enhanced.yml pull
   docker-compose -f docker-compose.enhanced.yml up -d
   ```

2. **Clean Up**:
   ```bash
   # Clean Docker system
   ./setup-enhanced-docker.sh clean
   
   # Remove unused volumes
   docker volume prune
   ```

3. **Backup Data**:
   ```bash
   # Backup database
   docker exec sentinelbert-postgres-enhanced pg_dump -U sentinel sentinelbert > backup.sql
   
   # Backup evidence
   tar -czf evidence_backup.tar.gz evidence_storage/
   ```

### Log Rotation
```bash
# Configure log rotation in /etc/logrotate.d/docker
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
```

## 🎯 Hackathon Demo Guide

### Quick Demo Steps

1. **Start System**:
   ```bash
   ./setup-enhanced-docker.sh
   ```

2. **Open Dashboard**:
   - Navigate to http://localhost:12000
   - Click "Influence Network" tab
   - Select "VIRAL ORIGIN TRACKING"

3. **Test Tracking**:
   - Input: `@YesaleAshish`
   - Algorithm: `Enhanced Tracking`
   - Click "Start Tracking"

4. **View Results**:
   - Network visualization appears
   - Confidence score displayed
   - Evidence automatically collected

5. **Generate Report**:
   - Click "Generate Court Report"
   - PDF downloaded with legal formatting
   - Digital signature included

### Demo Data
- **Test User**: @YesaleAshish (authenticated)
- **Sample Tweet**: 1970201504155160937
- **Expected Confidence**: 80%+
- **Processing Time**: <3 seconds

## 📞 Support

### Documentation
- **Architecture**: `ARCHITECTURE_DIAGRAM.md`
- **API Reference**: `docs/api/`
- **Deployment**: `DEPLOYMENT_GUIDE.md`

### Community
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Project Wiki

### Contact
- **Team**: Indian Police Hackathon Team
- **Email**: Contact through GitHub
- **Demo**: Available for live demonstration

---

## 🏆 Indian Police Hackathon 2024

This enhanced Docker environment is specifically designed for the Indian Police Hackathon, providing:

- ✅ **Court-ready evidence collection**
- ✅ **Real-time viral tracking**
- ✅ **Legal compliance features**
- ✅ **Scalable architecture**
- ✅ **Professional deployment**

**Ready for production deployment in law enforcement environments.**
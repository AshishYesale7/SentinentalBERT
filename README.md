# SentinelBERT - Multi-Platform Sentiment & Behavioral Pattern Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](https://kubernetes.io/)
[![Security](https://img.shields.io/badge/Security-Hardened-green.svg)](./SECURITY_FIXES_APPLIED.md)
[![wakatime](https://wakatime.com/badge/github/AshishYesale7/SentinentalBERT.svg)](https://wakatime.com/badge/github/AshishYesale7/SentinentalBERT)

SentinelBERT is a comprehensive social media intelligence platform designed for law enforcement and security agencies to monitor, analyze, and understand sentiment patterns and behavioral trends across multiple social media platforms in real-time.

## 🚨 SECURITY UPDATE
**This project has been completely security-hardened!** All critical vulnerabilities have been fixed, including hardcoded passwords, weak authentication, and Docker security issues. See [SECURITY_FIXES_APPLIED.md](./SECURITY_FIXES_APPLIED.md) for details.

## 🆕 InsideOut Secure Platform
A production-ready, legally compliant platform for law enforcement is available in [`INSIDEOUT_SECURE_SKELETON/`](./INSIDEOUT_SECURE_SKELETON/). This includes warrant verification, chain of custody, and constitutional compliance features. See [INSIDEOUT_INTEGRATION_GUIDE.md](./INSIDEOUT_INTEGRATION_GUIDE.md) for integration details.

## Key Features

- **Multi-Platform Data Ingestion**: Collect data from X.com, Instagram, Reddit, Facebook, and more
- **Advanced NLP Analysis**: BERT-based sentiment analysis and behavioral pattern detection
- **Real-time Processing**: High-throughput data pipeline with Rust and Python
- **Interactive Dashboards**: React-based visualization with timeline views and analytics
- **Geographic Analysis**: Location-based filtering and mapping capabilities
- **Influence Scoring**: Identify key influencers and content amplifiers
- **Security-First**: Enterprise-grade security with encryption and audit trails
- **Scalable Architecture**: Kubernetes-ready with auto-scaling capabilities

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  Ingestion      │───▶│   Processing    │
│                 │    │   Pipeline      │    │    Pipeline     │
│ • X.com API     │    │ • Rust ETL      │    │ • Python BERT   │
│ • Instagram API │    │ • Rate Limiting │    │ • Sentiment     │
│ • Reddit API    │    │ • Data Cleaning │    │ • Behavioral    │
│ • Other APIs    │    │ • Validation    │    │ • Influence     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │◀───│   Backend       │───▶│    Storage      │
│   Dashboard     │    │   Services      │    │    Layer        │
│                 │    │                 │    │                 │
│ • React/Flutter │    │ • Spring Boot   │    │ • PostgreSQL    │
│ • Timeline View │    │ • REST APIs     │    │ • ElasticSearch │
│ • Analytics     │    │ • WebSocket     │    │ • Redis Cache   │
│ • Region Filter │    │ • Auth Service  │    │ • Object Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### Prerequisites

- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Memory**: 16GB+ RAM (32GB recommended for production)
- **Storage**: 50GB+ free disk space
- **Docker**: Docker Engine 20.10+ and Docker Compose 2.0+
- **Network**: Internet connection for API access and model downloads
- **Optional**: NVIDIA GPU with 8GB+ VRAM for ML acceleration

### Automated Setup (Recommended)

The fastest way to get SentinelBERT running is using our automated setup script:

```bash
# Clone the repository
git clone https://github.com/your-org/SentinelBERT.git
cd SentinelBERT

# Run automated setup
chmod +x setup.sh
./setup.sh

# For production deployment with GPU support
./setup.sh --prod --gpu

# For development with hot reload
./setup.sh --dev

# Clean installation (removes existing data)
./setup.sh --clean
```

The setup script will:
- Check system requirements
- Install missing dependencies
- Generate secure passwords and keys
- Initialize databases and indices
- Build and deploy all services
- Verify deployment health
- Set up monitoring dashboards

### Manual Setup

If you prefer manual setup or need custom configuration:

#### 1. Clone and Configure

```bash
git clone https://github.com/your-org/SentinelBERT.git
cd SentinelBERT

# Copy and edit environment configuration
cp .env.example .env
nano .env  # Add your API keys and configuration

#for MacOs users 
curl -fsSL https://raw.githubusercontent.com/AshishYesale7/SentinentalBERT/main/setup_insideout_macos.sh | bash

```

#### 2. Get Free API Keys

Before starting, obtain free API keys from these platforms:

**Twitter/X.com API (Essential Access - Free)**
```bash
# Visit: https://developer.twitter.com/
# Apply for Essential Access
# Create app and generate Bearer Token
# Free tier: 500K tweets/month, 300 requests per 15 minutes
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Reddit API (Free)**
```bash
# Visit: https://www.reddit.com/prefs/apps
# Create new application (script type)
# Free tier: 100 requests/minute, 1000 requests/hour
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

**YouTube Data API (Free)**
```bash
# Visit: https://console.cloud.google.com/
# Enable YouTube Data API v3
# Create API Key
# Free tier: 10,000 units/day
YOUTUBE_API_KEY=your_api_key_here
```

#### 3. Initialize Environment

```bash
# Create necessary directories
mkdir -p data/{postgres,redis,elasticsearch,models}
mkdir -p logs/{ingestion,nlp,backend,frontend}

# Generate secure passwords
openssl rand -base64 32  # Use for JWT_SECRET
openssl rand -base64 32  # Use for ENCRYPTION_KEY
```

#### 4. Deploy Services

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f nlp-service
```

#### 5. Verify Deployment

```bash
# Wait for services to initialize (2-3 minutes)
sleep 180

# Check service health
curl http://localhost:8000/health  # NLP Service
curl http://localhost:8080/api/actuator/health  # Backend
curl http://localhost:3000/health  # Frontend

# Initialize ElasticSearch indices
curl -X PUT "localhost:9200/social_posts" \
  -H "Content-Type: application/json" \
  -d '{"settings": {"number_of_shards": 3}}'
```

### Access Points

Once deployment is complete, access these services:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend Dashboard** | http://localhost:3000 | admin / admin123 |
| **Backend API** | http://localhost:8080/api | JWT Token Required |
| **API Documentation** | http://localhost:8080/swagger-ui.html | - |
| **Grafana Monitoring** | http://localhost:3001 | admin / admin123 |
| **Prometheus Metrics** | http://localhost:9090 | - |
| **Jaeger Tracing** | http://localhost:16686 | - |
| **ElasticSearch** | http://localhost:9200 | - |

### Quick Commands

Use these commands for common operations:

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart nlp-service

# View real-time logs
docker-compose logs -f

# Check service status
docker-compose ps

# Scale services
docker-compose up -d --scale nlp-service=3

# Clean restart (removes data)
docker-compose down -v
docker-compose up -d --build

# Update services
git pull
docker-compose build
docker-compose up -d
```

### First-Time Setup Checklist

After successful deployment:

- [ ] **Access Dashboard**: Visit http://localhost:3000 and login with admin/admin123
- [ ] **Change Default Password**: Update admin password in user settings
- [ ] **Add API Keys**: Edit `.env` file with your social media API keys
- [ ] **Test Search**: Perform a test search with keywords like "climate change"
- [ ] **Check Monitoring**: Verify Grafana dashboards are loading data
- [ ] **Review Logs**: Ensure no error messages in service logs
- [ ] **Configure Alerts**: Set up email/Slack notifications (optional)

### Performance Optimization

For better performance:

```bash
# Enable GPU support (if NVIDIA GPU available)
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# Increase memory limits for ML processing
export COMPOSE_FILE=docker-compose.yml:docker-compose.performance.yml
docker-compose up -d

# Scale NLP service for higher throughput
docker-compose up -d --scale nlp-service=3
```

## Technology Stack

### Data Ingestion Layer (Rust)
- **Tokio**: Asynchronous runtime for high-concurrency
- **Reqwest**: HTTP client with retry logic and rate limiting
- **SQLx**: Type-safe database interactions
- **Apache Kafka**: Event streaming and message queuing

### NLP Processing Layer (Python)
- **Transformers**: Hugging Face BERT models and fine-tuning
- **PyTorch**: Deep learning framework
- **FastAPI**: High-performance API framework
- **Celery**: Distributed task processing

### Backend Services (Spring Boot - Java)
- **Spring Security**: Authentication and authorization
- **Spring Data JPA**: Database abstraction layer
- **Spring WebSocket**: Real-time communication
- **Spring Cloud Gateway**: API gateway and routing

### Storage Layer
- **PostgreSQL**: Primary database with partitioning
- **ElasticSearch**: Full-text search and analytics
- **Redis**: Caching and session management
- **Object Storage**: Media file storage

### Frontend (React/TypeScript)
- **Material-UI**: Component library
- **Recharts**: Data visualization
- **Leaflet**: Interactive maps
- **Socket.IO**: Real-time updates

## Development Setup

### Local Development

```bash
# Install dependencies for each service
cd services/ingestion && cargo build
cd ../nlp && pip install -r requirements.txt
cd ../backend && mvn install
cd ../../frontend && npm install

# Start development servers
docker-compose -f docker-compose.dev.yml up
```

### Running Tests

```bash
# Rust tests
cd services/ingestion && cargo test

# Python tests
cd services/nlp && pytest

# Java tests
cd services/backend && mvn test

# Frontend tests
cd frontend && npm test
```

## Monitoring & Observability

### Metrics Collection
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **Jaeger**: Distributed tracing

### Key Metrics Monitored
- Data ingestion rates and latency
- NLP processing throughput
- API response times
- Database performance
- Cache hit rates
- Error rates and alerts

### Health Checks
```bash
# Check service health
curl http://localhost:8080/actuator/health
curl http://localhost:8000/health
curl http://localhost:8081/health
```

## Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication support
- Session management

### Data Protection
- Encryption at rest and in transit
- PII data anonymization
- Field-level encryption for sensitive data
- Secure API key management

### Audit & Compliance
- Comprehensive audit logging
- Data retention policies
- GDPR compliance features
- Access control monitoring

## Configuration

### Environment Variables

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# API Keys
TWITTER_BEARER_TOKEN=your_twitter_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Security
JWT_SECRET=your_jwt_secret_key

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password
```

### Service Configuration

Each service can be configured through:
- Environment variables
- Configuration files (`config.toml`, `application.yml`, etc.)
- Kubernetes ConfigMaps and Secrets

## Deployment

### Docker Deployment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale nlp-service=3 --scale backend-service=2
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n sentinelbert

# Scale deployments
kubectl scale deployment nlp-service --replicas=3 -n sentinelbert
```

### CI/CD Pipeline

The project includes GitHub Actions workflows for:
- Automated testing
- Docker image building
- Kubernetes deployment
- Security scanning

## API Documentation

### REST API Endpoints

- **Search API**: `/api/v1/search` - Perform content searches
- **Analytics API**: `/api/v1/analytics` - Get sentiment and trend analysis
- **Users API**: `/api/v1/users` - User management
- **Export API**: `/api/v1/export` - Data export functionality

### WebSocket Events

- `query_update` - Real-time query result updates
- `new_content` - New content matching active queries
- `sentiment_update` - Sentiment analysis updates

### API Documentation

- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **OpenAPI Spec**: http://localhost:8080/v3/api-docs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Write comprehensive tests
- Update documentation
- Ensure security best practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### 🌐 Documentation Website
**Visit our comprehensive documentation website**: [https://AshishYesale7.github.io/SentinentalBERT/](https://AshishYesale7.github.io/SentinentalBERT/)

The documentation website features:
- 🎨 **Beautiful Interface**: Responsive design with dark/light themes
- 🔍 **Advanced Search**: Full-text search across all documentation
- 🤖 **AI-Generated Content**: Automatically updated with code changes
- 📱 **Mobile-Optimized**: Perfect experience on all devices
- ⚡ **Fast & Reliable**: Python-based static site generator for optimal performance

### 📚 Documentation Files
- [System Design](SYSTEM_DESIGN.md) - Comprehensive system architecture
- [Architecture Diagrams](ARCHITECTURE_DIAGRAM.md) - Visual system overview
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Detailed deployment instructions
- [Executive Summary](EXECUTIVE_SUMMARY.md) - Business case and ROI analysis
- [Project Status](PROJECT_STATUS.md) - Development roadmap and status
- [API Reference](docs/api.md) - Detailed API documentation

### 🤖 AI Documentation System
Our documentation is powered by an advanced AI system that:
- **Automatically generates** comprehensive documentation when code changes
- **Maintains consistency** across all documentation files
- **Deploys to GitHub Pages** for beautiful online access
- **Validates accuracy** and keeps content up-to-date

### Getting Help
- Create an issue for bug reports
- Use discussions for questions
- Check the wiki for additional documentation

### Contact
- Email: support@sentinelbert.com
- Slack: #sentinelbert-support

## Roadmap

### Phase 1 (Current)
- Multi-platform data ingestion
- BERT-based sentiment analysis
- Real-time dashboard
- Basic behavioral pattern detection

### Phase 2 (Next 6 months)
- Image and video sentiment analysis
- Advanced behavioral pattern recognition
- Enhanced geographic analysis
- Mobile application

### Phase 3 (6-12 months)
- Predictive trend analysis
- Automated alert system
- Advanced network analysis
- Multi-language support

### Phase 4 (12+ months)
- AI-powered threat detection
- Cross-platform user tracking
- Advanced visualization tools
- Integration with external systems

---

**Built with care for law enforcement and security professionals**
## 🔒 Security & Compliance

### Security Features (✅ IMPLEMENTED)
- **JWT Authentication**: Token-based authentication with role-based permissions
- **Encrypted Communications**: TLS/SSL for all service communications
- **Secure Database Access**: Environment-based credentials, no hardcoded passwords
- **Container Security**: Non-root execution, read-only filesystems, security options
- **Audit Logging**: Comprehensive logging for all security events

### Legal Compliance (🆕 AVAILABLE IN INSIDEOUT)
- **Warrant Verification**: Real-time legal authority validation
- **Chain of Custody**: Cryptographic evidence tracking
- **Constitutional Compliance**: 4th Amendment protection checks
- **Court-Admissible Evidence**: Tamper-proof evidence handling
- **Data Retention Policies**: Automated compliance with legal requirements

### Quick Security Setup
```bash
# 1. Copy environment template
cp .env.template .env

# 2. Set secure passwords (REQUIRED)
# Edit .env and set:
# - POSTGRES_PASSWORD=your-secure-password
# - REDIS_PASSWORD=your-secure-password  
# - JWT_SECRET=your-256-bit-secret

# 3. Deploy with security hardening
docker-compose up -d
```

## 📚 Documentation

- [📋 Documentation Index](docs/INDEX.md) - Complete documentation overview
- [🚀 Quick Start](docs/QUICK_START.md) - Get started quickly
- [🔧 Deployment Guide](DEPLOYMENT_GUIDE.md) - Deployment instructions
- [🔒 Security Fixes Applied](SECURITY_FIXES_APPLIED.md) - **CRITICAL: Security updates**
- [🏛️ InsideOut Integration](INSIDEOUT_INTEGRATION_GUIDE.md) - **NEW: Legal compliance platform**
- [📡 API Reference](docs/api/API_REFERENCE.md) - API documentation
- [🏗️ System Design](SYSTEM_DESIGN.md) - Technical architecture
- [🔍 Security Analysis](COMPREHENSIVE_SECURITY_ANALYSIS.md) - Complete vulnerability assessment

---

*Documentation is automatically maintained and updated.*

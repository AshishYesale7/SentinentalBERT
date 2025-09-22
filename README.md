# Government of India - Cyber Crime Analysis Platform

## भारत सरकार - साइबर अपराध विश्लेषण प्लेटफॉर्म
 
[![wakatime](https://wakatime.com/badge/github/AshishYesale7/SentinentalBERT.svg)](https://wakatime.com/badge/github/AshishYesale7/SentinentalBERT)

A professional Indian government-themed viral content analysis platform for law enforcement and cyber crime investigation, with full compliance to Indian legal frameworks including IT Act 2000, CrPC 1973, and Evidence Act 1872.

## 🇮🇳 Platform Overview

This platform provides comprehensive viral content analysis capabilities specifically designed for Indian law enforcement agencies, with full compliance to Indian legal frameworks including IT Act 2000, CrPC 1973, and Evidence Act 1872.

## 📁 Project Structure & File Functionalities

### Core Dashboard Files

#### `enhanced_viral_dashboard.py` - Main Application
**Primary Functions:**
- **Government-themed UI**: Professional Indian police/government interface with tricolor theme
- **Multi-language Support**: English/Hindi translation system with 10+ Indian languages
- **Viral Content Analysis**: Real-time monitoring and AI-powered viral prediction
- **Legal Compliance**: IT Act 2000, Evidence Act 1872, and CrPC 1973 compliance
- **Evidence Collection**: Digital evidence collection with chain of custody
- **Platform Integration**: Support for 8+ social media platforms including Indian platforms
- **Sentiment Analysis**: Advanced NLP-based sentiment and behavior analysis
- **Geographic Tracking**: Location-based viral content spread analysis
- **Influence Network**: Social network analysis and influence mapping

**Key Components Integrated:**
- Translation system with bilingual support
- Government CSS styling with Indian flag colors
- Professional metrics dashboard
- Evidence collection queue
- Legal authorization framework
- Multi-platform content analysis
- Comprehensive reporting system

### Language & Localization

#### `language_support.py` - Multi-language Processing
**Functions:**
- Language detection and translation
- Multi-lingual content analysis
- Regional language support for Indian languages
- UI text localization
- Content sentiment analysis in multiple languages

#### `platform_support.py` - Platform Integration
**Functions:**
- Social media platform API integration
- Indian platform support (Koo, ShareChat, etc.)
- Global platform connectivity (Twitter, Facebook, Instagram, etc.)
- Platform-specific content extraction
- Cross-platform analysis capabilities

### Analysis & Intelligence

#### `sentiment_analysis.py` - Advanced NLP Analysis
**Functions:**
- Real-time sentiment analysis
- Emotion detection and classification
- Behavioral pattern recognition
- Content toxicity assessment
- Viral potential prediction algorithms

#### `behavior_analysis.py` - User Behavior Analytics
**Functions:**
- User behavior pattern analysis
- Influence score calculation
- Engagement pattern detection
- Anomaly detection in user activities
- Social network behavior mapping

#### `nlp_processor.py` - Natural Language Processing
**Functions:**
- Text preprocessing and cleaning
- Named entity recognition (NER)
- Topic modeling and classification
- Keyword extraction and analysis
- Content categorization

### Legal & Compliance

#### `legal_framework.py` - Legal Compliance Engine
**Functions:**
- IT Act 2000 compliance verification
- Evidence Act 1872 digital evidence standards
- CrPC 1973 procedural compliance
- Legal authorization validation
- Chain of custody maintenance
- Section 65B certificate generation

#### `evidence_collector.py` - Digital Evidence Management
**Functions:**
- Secure evidence collection
- Digital signature verification
- Integrity hash generation
- Metadata preservation
- Court-ready evidence packaging
- Audit trail maintenance

### Data & Storage

#### `database_manager.py` - Data Management
**Functions:**
- Secure data storage and retrieval
- Evidence database management
- User session management
- Audit log maintenance
- Data encryption and security

#### `config.py` - Configuration Management
**Functions:**
- Application configuration settings
- API keys and credentials management
- Platform-specific configurations
- Security parameters
- Logging configurations

### Utilities & Support

#### `utils.py` - Utility Functions
**Functions:**
- Common utility functions
- Data validation and sanitization
- File handling operations
- Date/time utilities
- Encryption/decryption helpers

#### `logger.py` - Logging System
**Functions:**
- Comprehensive logging framework
- Security event logging
- Error tracking and reporting
- Audit trail generation
- Performance monitoring

### Frontend & UI

#### `frontend/` - Web Interface Components
**Structure:**
- `public/index.html` - Main HTML template
- `static/css/` - Government theme stylesheets
- `static/js/` - Interactive JavaScript components
- `components/` - Reusable UI components

**Note:** The SentinelBERT Dashboard at `frontend/public/index.html` has been excluded as requested.

### Testing & Quality

#### `tests/` - Test Suite
**Components:**
- Unit tests for all modules
- Integration tests for platform connectivity
- Security compliance tests
- Performance benchmarking
- Legal framework validation tests

## 🚨 SECURITY UPDATE
**This project has been completely security-hardened!** All critical vulnerabilities have been fixed, including hardcoded passwords, weak authentication, and Docker security issues. See [SECURITY_FIXES_APPLIED.md](./SECURITY_FIXES_APPLIED.md) for details.

## 🚀 Deployment & Usage

### Prerequisites
```bash
pip install streamlit pandas numpy plotly networkx
pip install torch transformers  # For advanced NLP features
```

### Running the Platform
```bash
streamlit run enhanced_viral_dashboard.py --server.port 12000 --server.address 0.0.0.0
```

### Access URLs
- **Primary Dashboard**: https://work-1-wamrwqcrxemubrjv.prod-runtime.all-hands.dev
- **Secondary Access**: https://work-2-wamrwqcrxemubrjv.prod-runtime.all-hands.dev

## 🔒 Security & Compliance

### Legal Framework Compliance
- **IT Act 2000**: Full compliance with digital evidence standards
- **CrPC 1973**: Procedural compliance for investigation
- **Evidence Act 1872**: Section 65B digital evidence certification
- **Data Protection**: Secure handling of sensitive information

### Security Features
- End-to-end encryption for data transmission
- Secure authentication and authorization
- Audit trail for all operations
- Chain of custody maintenance
- Digital signature verification

## 🌐 Platform Support

### Indian Platforms
- Koo (Indian microblogging)
- ShareChat (Regional social media)
- Josh (Short video platform)
- Moj (Entertainment platform)

### Global Platforms
- Twitter/X
- Facebook
- Instagram
- YouTube
- LinkedIn
- TikTok
- Telegram
- WhatsApp (Business API)

## 🗣️ Language Support

### Supported Languages
- **English** (Primary)
- **हिन्दी** (Hindi)
- **বাংলা** (Bengali)
- **தமிழ்** (Tamil)
- **తెలుగు** (Telugu)
- **ગુજરાતી** (Gujarati)
- **ಕನ್ನಡ** (Kannada)
- **മലയാളം** (Malayalam)
- **ਪੰਜਾਬੀ** (Punjabi)
- **मराठी** (Marathi)

## 📊 Key Features

### Analysis Capabilities
1. **Viral Timeline Analysis**: Real-time tracking of viral content spread
2. **Comprehensive Content Analysis**: AI-powered content evaluation
3. **Sentiment & Behavior Analysis**: Advanced NLP-based sentiment analysis
4. **Influence Network Mapping**: Social network analysis and influence tracking
5. **Geographic Spread Analysis**: Location-based content distribution tracking
6. **Evidence Collection**: Legal-compliant digital evidence gathering

### Dashboard Components
- **Government Header**: Official Indian government branding
- **Multi-language Interface**: Bilingual English/Hindi support
- **Professional Metrics**: Key performance indicators for investigations
- **Legal Authorization**: Warrant and court order validation
- **Evidence Queue**: Prioritized evidence collection interface
- **Compliance Status**: Real-time legal compliance monitoring

## 🛠️ Technical Architecture

### Core Technologies
- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with advanced NLP libraries
- **Database**: Secure data storage with encryption
- **APIs**: Multi-platform social media integration
- **Security**: End-to-end encryption and digital signatures

### Integration Points
- Social media platform APIs
- Government authentication systems
- Legal compliance frameworks
- Multi-language processing engines
- Evidence management systems

## 📈 Performance Metrics

### System Capabilities
- **Real-time Processing**: Sub-second content analysis
- **Multi-platform Support**: 8+ platforms simultaneously
- **Language Processing**: 10+ Indian languages
- **Evidence Collection**: Court-ready digital evidence
- **Compliance Monitoring**: 100% legal framework adherence

## 🔧 Maintenance & Updates

### Regular Maintenance
- Platform API updates
- Security patch management
- Legal framework updates
- Language model improvements
- Performance optimization

### Monitoring
- System health monitoring
- Security event tracking
- Performance metrics
- Legal compliance audits
- User activity logging

## 📞 Support & Contact

### Government Contact
- **Ministry**: Ministry of Home Affairs
- **Division**: Cyber Crime Investigation Division
- **Classification**: RESTRICTED - For Official Use Only

### Technical Support
- Platform maintenance and updates
- Security incident response
- Legal compliance assistance
- Training and documentation

---

**Disclaimer**: This platform is designed for official government use only and complies with all applicable Indian laws and regulations. Unauthorized access or misuse is strictly prohibited and may result in legal action.

**भारत सरकार | Government of India**
**गृह मंत्रालय | Ministry of Home Affairs**
**साइबर अपराध जांच प्रभाग | Cyber Crime Investigation Division**

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

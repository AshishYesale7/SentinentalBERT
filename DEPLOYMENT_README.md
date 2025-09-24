# SentinelBERT Deployment Guide

Complete deployment guide for SentinelBERT Social Media Analytics Platform.

## 🚀 Quick Start

The fastest way to get SentinelBERT running:

```bash
chmod +x quick-start.sh
./quick-start.sh
```

This script will automatically detect your system and recommend the best deployment method.

## 📋 Prerequisites

### For All Deployments
- **Operating System**: macOS 10.15+ or Linux (Ubuntu 18.04+, CentOS 7+)
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 10GB free space
- **Network**: Internet connection for downloading dependencies

### For Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

### For Native Deployment
- Python 3.8+
- Node.js 16+
- npm 8+

## 🐳 Docker Deployment (Recommended)

### Quick Docker Setup
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh deploy
```

### Docker Commands
```bash
# Deploy all services
./docker-deploy.sh deploy

# Check status
./docker-deploy.sh status

# View logs
./docker-deploy.sh logs

# Stop services
./docker-deploy.sh stop

# Clean everything
./docker-deploy.sh clean

# Restart services
./docker-deploy.sh restart
```

### What Docker Deployment Includes
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ NLP service (BERT-based)
- ✅ Streamlit dashboard
- ✅ React frontend
- ✅ Automatic health checks
- ✅ Service orchestration
- ✅ Volume persistence

## 💻 Native Deployment

### Quick Native Setup
```bash
chmod +x native-deploy.sh
./native-deploy.sh deploy
```

### Native Commands
```bash
# Deploy all services
./native-deploy.sh deploy

# Check status
./native-deploy.sh status

# View logs
./native-deploy.sh logs

# Stop services
./native-deploy.sh stop

# Clean deployment
./native-deploy.sh clean

# Restart services
./native-deploy.sh restart
```

### What Native Deployment Includes
- ✅ Python virtual environment
- ✅ NLP service (FastAPI + BERT)
- ✅ Streamlit dashboard
- ✅ React frontend (if Node.js available)
- ✅ Process management
- ✅ Health monitoring

## 🔧 Universal Deployment Script

For advanced users who want full control:

```bash
chmod +x deploy.sh

# Docker deployment
./deploy.sh --docker

# Native deployment
./deploy.sh --native

# Development mode
./deploy.sh --native --dev

# Force reinstall
./deploy.sh --native --force

# Check status
./deploy.sh --status

# View logs
./deploy.sh --logs

# Stop services
./deploy.sh --stop

# Clean deployment
./deploy.sh --clean
```

## 🌐 Access URLs

After successful deployment, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:12000 | Government-style analytics interface |
| **React Frontend** | http://localhost:12001 | Modern web interface |
| **NLP API** | http://localhost:8000 | BERT-based sentiment analysis API |
| **API Documentation** | http://localhost:8000/docs | Interactive API documentation |

## 🔑 API Configuration

### Required API Keys

Update the `.env` file with your API keys:

```bash
# Twitter/X API
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key
```

### Getting API Keys

#### Twitter/X API
1. Visit [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Generate API keys and tokens

#### Reddit API
1. Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new application
3. Note the client ID and secret

#### YouTube API
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3
3. Create credentials (API key)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │Streamlit Dashboard│    │   NLP Service   │
│   (Port 12001)  │    │   (Port 12000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────────────────────────────────┐
         │              Core Services                  │
         │  ┌─────────────┐  ┌─────────────────────┐   │
         │  │ PostgreSQL  │  │  Redis Cache        │   │
         │  │ (Optional)  │  │  (Optional)         │   │
         │  └─────────────┘  └─────────────────────┘   │
         └─────────────────────────────────────────────┘
```

## 🔍 Service Details

### NLP Service (Port 8000)
- **Technology**: FastAPI + PyTorch + Transformers
- **Features**: BERT sentiment analysis, real-time processing
- **Endpoints**: `/analyze`, `/health`, `/docs`

### Streamlit Dashboard (Port 12000)
- **Technology**: Streamlit + Python
- **Features**: Government-style interface, real-time analytics
- **Capabilities**: Social media monitoring, viral detection

### React Frontend (Port 12001)
- **Technology**: React + TypeScript + Material-UI
- **Features**: Modern web interface, interactive charts
- **Capabilities**: Real-time updates, responsive design

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :12000
lsof -i :12001

# Kill processes if needed
sudo kill -9 <PID>
```

#### Docker Issues
```bash
# Restart Docker daemon
sudo systemctl restart docker  # Linux
# or restart Docker Desktop on macOS

# Clean Docker system
docker system prune -a
```

#### Python Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-complete.txt
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove and reinstall node_modules
rm -rf frontend/node_modules
cd frontend && npm install
```

### Service Health Checks

#### Check NLP Service
```bash
curl http://localhost:8000/health
```

#### Check Streamlit Dashboard
```bash
curl http://localhost:12000
```

#### Check React Frontend
```bash
curl http://localhost:12001
```

### Log Locations

#### Docker Deployment
```bash
# View all logs
docker-compose -f docker-compose.simple.yml logs -f

# View specific service logs
docker logs sentinelbert-nlp
docker logs sentinelbert-streamlit
```

#### Native Deployment
```bash
# Log files location
ls -la logs/

# View specific logs
tail -f logs/nlp_service.log
tail -f logs/streamlit.log
tail -f logs/frontend.log
```

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong passwords for database connections
- Rotate API keys regularly

### Network Security
- Services bind to localhost by default
- Use reverse proxy for production deployments
- Enable HTTPS for production

### Data Protection
- Social media data is processed locally
- No data is sent to external services (except APIs)
- Implement proper access controls for production

## 🚀 Production Deployment

### Additional Steps for Production

1. **Use Environment-Specific Configurations**
   ```bash
   cp .env .env.production
   # Edit .env.production with production values
   ```

2. **Set Up Reverse Proxy**
   - Use Nginx or Apache
   - Enable HTTPS with SSL certificates
   - Configure proper security headers

3. **Database Setup**
   - Use managed PostgreSQL service
   - Set up regular backups
   - Configure connection pooling

4. **Monitoring**
   - Set up application monitoring
   - Configure log aggregation
   - Implement health checks

5. **Scaling**
   - Use container orchestration (Kubernetes)
   - Implement load balancing
   - Set up auto-scaling

## 📊 Performance Optimization

### System Requirements by Scale

| Scale | RAM | CPU | Storage | Concurrent Users |
|-------|-----|-----|---------|------------------|
| **Development** | 8GB | 4 cores | 10GB | 1-5 |
| **Small Team** | 16GB | 8 cores | 50GB | 5-20 |
| **Department** | 32GB | 16 cores | 100GB | 20-100 |
| **Enterprise** | 64GB+ | 32+ cores | 500GB+ | 100+ |

### Optimization Tips

1. **NLP Service**
   - Use GPU acceleration for BERT models
   - Implement model caching
   - Batch process requests

2. **Database**
   - Index frequently queried columns
   - Use connection pooling
   - Implement query optimization

3. **Frontend**
   - Enable gzip compression
   - Use CDN for static assets
   - Implement lazy loading

## 🆘 Support

### Getting Help

1. **Check Logs**: Always check service logs first
2. **Review Documentation**: Read this guide thoroughly
3. **System Requirements**: Ensure your system meets requirements
4. **Clean Deployment**: Try cleaning and redeploying

### Common Solutions

| Problem | Solution |
|---------|----------|
| Services won't start | Check port availability and dependencies |
| API errors | Verify API keys in .env file |
| Frontend not loading | Ensure Node.js dependencies are installed |
| Database connection issues | Check PostgreSQL service status |
| Memory issues | Increase system RAM or reduce concurrent processes |

## 📝 Development

### Development Mode

For development with hot reload:

```bash
# Native development mode
./native-deploy.sh deploy

# Or using main script
./deploy.sh --native --dev
```

### Code Structure

```
SentinentalBERT/
├── services/
│   ├── nlp/                 # NLP service (FastAPI)
│   ├── realtime/           # Real-time data connectors
│   └── viral_detection/    # Viral content detection
├── frontend/               # React frontend
├── enhanced_viral_dashboard.py  # Streamlit dashboard
├── deploy.sh              # Universal deployment script
├── docker-deploy.sh       # Docker-specific deployment
├── native-deploy.sh       # Native deployment script
└── quick-start.sh         # Quick start script
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with deployment scripts
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 👥 Team

**Team: Code X**
- Advanced Social Media Analytics
- Government-Grade Security
- Real-time Monitoring Solutions

---

*For additional support or questions, please refer to the project documentation or contact the development team.*
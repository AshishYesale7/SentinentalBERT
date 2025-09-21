# 🍎 Enhanced InsideOut Platform - macOS Deployment Guide

## 📋 OVERVIEW

This comprehensive guide provides step-by-step instructions for deploying the Enhanced InsideOut Platform on macOS systems. The platform is specifically designed for Indian law enforcement with complete legal framework compliance, multilingual support, and global platform integration.

---

## 🎯 QUICK START (Automated Deployment)

### One-Command Installation:
```bash
curl -fsSL https://raw.githubusercontent.com/bot-text/SentinentalBERT/main/setup_insideout_macos.sh | bash
```

### Manual Download and Run:
```bash
# Download the deployment script
curl -O https://raw.githubusercontent.com/bot-text/SentinentalBERT/main/setup_insideout_macos.sh

# Make it executable
chmod +x setup_insideout_macos.sh

# Run the deployment
./setup_insideout_macos.sh
```

---

## 🔧 SYSTEM REQUIREMENTS

### Minimum Requirements:
- **macOS**: 10.15 (Catalina) or later
- **RAM**: 8GB (16GB recommended)
- **Storage**: 5GB free space
- **Architecture**: Intel x86_64 or Apple Silicon (M1/M2)
- **Internet**: Stable broadband connection

### Recommended Requirements:
- **macOS**: 12.0 (Monterey) or later
- **RAM**: 16GB or more
- **Storage**: 10GB free space
- **Processor**: Multi-core (4+ cores recommended)

---

## 📦 WHAT GETS INSTALLED

### Development Tools:
- ✅ **Xcode Command Line Tools** - Essential development utilities
- ✅ **Homebrew** - Package manager for macOS
- ✅ **Git** - Version control system
- ✅ **Essential CLI Tools** - curl, wget, jq, tree, htop

### Programming Languages:
- ✅ **Python 3.11** - Core platform language
- ✅ **Node.js 18** - JavaScript runtime for web components
- ✅ **pip & npm** - Package managers

### Containerization:
- ✅ **Docker Desktop** - Container platform
- ✅ **Docker Compose** - Multi-container orchestration

### Databases:
- ✅ **PostgreSQL 14** - Primary database
- ✅ **Redis** - Caching and session storage

### Python Libraries:
- ✅ **Streamlit** - Web dashboard framework
- ✅ **Pandas, NumPy** - Data processing
- ✅ **Matplotlib, Seaborn, Plotly** - Visualization
- ✅ **Scikit-learn** - Machine learning
- ✅ **Transformers, PyTorch** - NLP and AI models
- ✅ **NLTK, spaCy** - Natural language processing
- ✅ **Indic-NLP** - Indian language processing
- ✅ **Requests, BeautifulSoup** - Web scraping
- ✅ **Cryptography** - Security and encryption
- ✅ **FastAPI, Flask** - API frameworks

---

## 🚀 DEPLOYMENT PROCESS

### Phase 1: System Preparation
1. **System Requirements Check**
   - Verifies macOS version compatibility
   - Checks available disk space (5GB minimum)
   - Validates system architecture (Intel/Apple Silicon)
   - Tests internet connectivity

2. **Development Tools Installation**
   - Installs Xcode Command Line Tools
   - Sets up Homebrew package manager
   - Installs essential CLI utilities

### Phase 2: Runtime Environment Setup
3. **Python Environment**
   - Installs Python 3.11 via Homebrew
   - Creates virtual environment
   - Installs all required Python packages
   - Downloads NLTK data and spaCy models

4. **Node.js Environment**
   - Installs Node.js 18 and npm
   - Installs global packages (yarn, pm2, nodemon)

5. **Docker Installation**
   - Downloads and installs Docker Desktop
   - Configures Docker for the platform
   - Installs Docker Compose

### Phase 3: Database Setup
6. **Database Services**
   - Installs and configures PostgreSQL 14
   - Installs and configures Redis
   - Creates InsideOut database
   - Starts database services

### Phase 4: Platform Deployment
7. **Repository Setup**
   - Clones Enhanced InsideOut Platform repository
   - Sets up project structure
   - Configures environment variables

8. **Configuration**
   - Creates .env configuration file
   - Sets up logging directories
   - Configures security settings
   - Prepares evidence storage

### Phase 5: Testing & Validation
9. **Integration Testing**
   - Runs comprehensive test suite
   - Validates all components
   - Verifies legal framework compliance
   - Tests multilingual support

10. **Final Setup**
    - Creates desktop shortcuts
    - Generates launch scripts
    - Provides access instructions

---

## 🔧 MANUAL INSTALLATION STEPS

If you prefer manual installation or need to troubleshoot:

### Step 1: Install Xcode Command Line Tools
```bash
xcode-select --install
```

### Step 2: Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 3: Install Python and Dependencies
```bash
# Install Python
brew install python@3.11

# Create project directory
mkdir -p ~/InsideOut-Platform
cd ~/InsideOut-Platform

# Clone repository
git clone https://github.com/bot-text/SentinentalBERT.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt  # If requirements.txt exists
# Or install manually:
pip install streamlit pandas numpy matplotlib seaborn plotly
pip install scikit-learn transformers torch
pip install nltk spacy textblob langdetect indic-nlp-library
pip install requests beautifulsoup4 selenium
pip install cryptography sqlalchemy redis fastapi
```

### Step 4: Install Node.js
```bash
brew install node@18
npm install -g yarn pm2 nodemon
```

### Step 5: Install Docker Desktop
```bash
# Download Docker Desktop from https://www.docker.com/products/docker-desktop/
# Or use Homebrew cask:
brew install --cask docker
```

### Step 6: Install Databases
```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14
createdb insideout_db

# Install Redis
brew install redis
brew services start redis
```

### Step 7: Configure Environment
```bash
# Create .env file with your configuration
cp .env.example .env  # If example exists
# Edit .env with your API keys and settings
```

### Step 8: Run Tests
```bash
cd ~/InsideOut-Platform
source venv/bin/activate
python test_enhanced_integration.py
```

### Step 9: Start Platform
```bash
streamlit run enhanced_viral_dashboard.py --server.port 8080
```

---

## 🔑 CONFIGURATION

### Environment Variables (.env file):
```bash
# Application Settings
APP_NAME=InsideOut
APP_VERSION=2.0
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8080

# Database URLs
DATABASE_URL=postgresql://localhost:5432/insideout_db
REDIS_URL=redis://localhost:6379

# Security Keys (auto-generated)
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Legal Framework
LEGAL_FRAMEWORK_ENABLED=true
EVIDENCE_STORAGE_PATH=./evidence_storage
CHAIN_OF_CUSTODY_ENABLED=true

# Multilingual Support
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,hi,bn,ta,te
UI_TRANSLATION_ENABLED=true

# Platform API Keys (Add your keys)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
YOUTUBE_API_KEY=your_youtube_api_key
KOO_API_KEY=your_koo_api_key
SHARECHAT_API_KEY=your_sharechat_api_key
```

### API Keys Setup:
1. **Twitter/X API**: https://developer.twitter.com/
2. **Facebook API**: https://developers.facebook.com/
3. **Instagram API**: https://developers.facebook.com/docs/instagram
4. **YouTube API**: https://developers.google.com/youtube/
5. **Koo API**: Contact Koo developer support
6. **ShareChat API**: Contact ShareChat developer support

---

## 🚀 STARTING THE PLATFORM

### Method 1: Desktop Shortcut
- Double-click "InsideOut Platform" app on Desktop
- Platform will open in Terminal and browser

### Method 2: Command Line
```bash
cd ~/InsideOut-Platform
source venv/bin/activate
streamlit run enhanced_viral_dashboard.py --server.port 8080
```

### Method 3: Launch Script
```bash
~/InsideOut-Platform/launch_insideout.sh
```

### Access URLs:
- **Main Dashboard**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs (if FastAPI is running)

---

## 🧪 TESTING

### Run All Tests:
```bash
cd ~/InsideOut-Platform
source venv/bin/activate
python test_enhanced_integration.py
```

### Test Components:
- ✅ **Legal Framework Test** - Authorization, evidence collection, chain of custody
- ✅ **Multilingual Support Test** - Language detection, UI translation
- ✅ **Global Platform Test** - Content extraction, viral analysis
- ✅ **Integration Test** - End-to-end workflow validation

### Expected Results:
```
🚀 Starting Enhanced InsideOut Platform Integration Tests
======================================================================
🔍 Testing Indian Legal Framework...
✅ Legal authorization created
✅ Evidence collected
✅ Evidence integrity verified
✅ Chain of custody entry added
✅ Court report generated

🌐 Testing Enhanced Multilingual Support...
✅ Language detection successful: hi, bn, ta, te, en
✅ UI translations available for all languages
✅ Multilingual analysis successful

🌍 Testing Global Platform Support...
✅ Platform support comprehensive: 7 platforms supported
✅ Content extraction successful for all platforms
✅ Platform features well supported

🔗 Testing Component Integration...
✅ All services initialized successfully
✅ Integration test: Cross-platform analysis successful

======================================================================
📊 TEST RESULTS SUMMARY
======================================================================
Legal Framework                ✅ PASSED
Multilingual Support           ✅ PASSED
Global Platform Support        ✅ PASSED
Integration                    ✅ PASSED
----------------------------------------------------------------------
Overall Success Rate: 4/4 (100.0%)

🎉 ALL TESTS PASSED! Enhanced InsideOut Platform is ready for deployment.
```

---

## 🔧 TROUBLESHOOTING

### Common Issues and Solutions:

#### 1. Xcode Command Line Tools Installation Fails
```bash
# Try manual installation
sudo xcode-select --reset
xcode-select --install
```

#### 2. Homebrew Installation Issues
```bash
# For Apple Silicon Macs, ensure correct PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### 3. Python Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

#### 4. Docker Desktop Not Starting
- Ensure Docker Desktop is installed in /Applications/
- Start Docker Desktop manually from Applications folder
- Wait for Docker to fully initialize before continuing

#### 5. Database Connection Issues
```bash
# Restart PostgreSQL
brew services restart postgresql@14

# Restart Redis
brew services restart redis

# Check if services are running
brew services list | grep -E "(postgresql|redis)"
```

#### 6. Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080

# Kill process if needed
kill -9 <PID>

# Or use different port
streamlit run enhanced_viral_dashboard.py --server.port 8081
```

#### 7. Permission Issues
```bash
# Fix permissions for project directory
chmod -R 755 ~/InsideOut-Platform
chown -R $(whoami) ~/InsideOut-Platform
```

#### 8. Missing Dependencies
```bash
# Reinstall Python dependencies
cd ~/InsideOut-Platform
source venv/bin/activate
pip install --upgrade --force-reinstall -r requirements.txt
```

---

## 📊 PERFORMANCE OPTIMIZATION

### System Optimization:
1. **Memory Management**
   - Close unnecessary applications
   - Monitor memory usage with Activity Monitor
   - Consider increasing swap space if needed

2. **Database Performance**
   - Regularly vacuum PostgreSQL database
   - Monitor Redis memory usage
   - Configure appropriate cache sizes

3. **Network Optimization**
   - Use stable internet connection
   - Configure firewall to allow required ports
   - Monitor API rate limits

### Platform Optimization:
```bash
# Set environment variables for better performance
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
export PYTHONUNBUFFERED=1
```

---

## 🔒 SECURITY CONSIDERATIONS

### Security Best Practices:
1. **API Keys Management**
   - Store API keys in .env file (never commit to git)
   - Use environment-specific keys
   - Regularly rotate API keys

2. **Database Security**
   - Use strong passwords for database connections
   - Enable SSL for database connections in production
   - Regular database backups

3. **Evidence Security**
   - Enable encryption for evidence storage
   - Implement proper access controls
   - Maintain audit logs

4. **Network Security**
   - Use HTTPS in production
   - Configure proper firewall rules
   - Monitor for suspicious activities

---

## 📚 ADDITIONAL RESOURCES

### Documentation:
- **Platform Summary**: `~/InsideOut-Platform/ENHANCED_PLATFORM_SUMMARY.md`
- **Change Catalog**: `~/InsideOut-Platform/CHANGE_CATALOG.md`
- **API Documentation**: Available in code comments
- **Legal Framework Guide**: Integrated in platform

### Support Files:
- **Deployment Log**: `~/InsideOut-Platform/deployment.log`
- **Test Reports**: `~/InsideOut-Platform/enhanced_integration_test_report.json`
- **Environment Config**: `~/InsideOut-Platform/.env`

### External Resources:
- **GitHub Repository**: https://github.com/bot-text/SentinentalBERT
- **Streamlit Documentation**: https://docs.streamlit.io/
- **Python Documentation**: https://docs.python.org/3.11/
- **Docker Documentation**: https://docs.docker.com/

---

## 🆘 SUPPORT

### Getting Help:
1. **Check Logs**: Review deployment.log for error details
2. **Run Tests**: Execute test suite to identify issues
3. **Documentation**: Refer to platform documentation
4. **Community**: Check GitHub issues and discussions

### Reporting Issues:
1. **Gather Information**:
   - macOS version and architecture
   - Error messages and logs
   - Steps to reproduce the issue

2. **Create Issue**:
   - Use GitHub issue tracker
   - Provide detailed description
   - Include relevant logs and screenshots

---

## 🎉 SUCCESS INDICATORS

### Deployment Success:
- ✅ All system requirements met
- ✅ All dependencies installed successfully
- ✅ Database services running
- ✅ All tests passing (100% success rate)
- ✅ Dashboard accessible at http://localhost:8080
- ✅ All features operational

### Platform Ready:
- ✅ Legal framework compliance active
- ✅ Multilingual UI functional
- ✅ Global platform support operational
- ✅ Evidence collection system ready
- ✅ Cross-platform analysis working
- ✅ Real-time monitoring active

---

## 🚀 NEXT STEPS

After successful deployment:

1. **Configure API Keys**
   - Add your social media platform API credentials
   - Test platform connections

2. **Legal Setup**
   - Configure legal authorization settings
   - Set up evidence storage policies
   - Train officers on legal compliance features

3. **Operational Deployment**
   - Set up monitoring and alerting
   - Configure backup procedures
   - Establish maintenance schedules

4. **Training**
   - Train law enforcement officers
   - Provide user manuals and guides
   - Set up support procedures

---

*This deployment guide ensures a complete, secure, and legally compliant installation of the Enhanced InsideOut Platform on macOS systems, specifically designed for Indian law enforcement operations.*
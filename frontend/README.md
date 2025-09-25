# SentinelBERT React NLP Dashboard

A modern React-based dashboard for real-time sentiment analysis and NLP processing using the SentinelBERT platform.

## 🚀 Features

- **Real-time Sentiment Analysis**: BERT-based sentiment classification with confidence scores
- **Behavioral Analysis**: User influence scoring and pattern detection
- **System Monitoring**: Service health, model status, and resource usage tracking
- **Modern UI**: Material-UI components with responsive design
- **Performance Metrics**: Processing time and accuracy measurements
- **Language Detection**: Automatic language identification

## 🛠️ Technology Stack

- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Material-UI (MUI)**: Professional UI components
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing
- **Redux Toolkit**: State management
- **Recharts**: Data visualization
- **Socket.io**: Real-time communication

## 📋 Prerequisites

- **Node.js**: Version 16 or higher
- **npm**: Version 8 or higher
- **NLP Service**: Backend service running on port 8001

## 🚀 Quick Start

### Option 1: Using the dedicated script
```bash
# From the SentinentalBERT root directory
./start-react-dashboard.sh
```

### Option 2: Manual setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment configuration
cat > .env << 'EOF'
DANGEROUSLY_DISABLE_HOST_CHECK=true
BROWSER=none
HOST=0.0.0.0
PORT=12001
WDS_SOCKET_HOST=0.0.0.0
WDS_SOCKET_PORT=12001
EOF

# Start development server
npm start
```

### Option 3: Using the main quick-start script
```bash
# From the SentinentalBERT root directory
./quick-start.sh
# Select native deployment option
```

## 🌐 Access URLs

Once running, the dashboard will be available at:
- **Local**: http://localhost:12001
- **Network**: http://0.0.0.0:12001
- **Production**: https://work-2-zxloxdkgvioudmud.prod-runtime.all-hands.dev

## 📊 Dashboard Features

### Main Dashboard
- **Service Status**: Real-time health monitoring
- **Model Status**: BERT model loading status
- **GPU Status**: Hardware acceleration availability
- **Active Requests**: Current processing load
- **Memory Usage**: Resource consumption tracking

### Analysis Page
- **Text Input**: Multi-line text analysis support
- **Sentiment Results**: Positive/Negative/Neutral classification
- **Confidence Scores**: Analysis reliability metrics
- **Behavioral Analysis**: Influence scoring
- **Processing Time**: Performance measurements

## 🔧 Configuration

### Environment Variables
The dashboard uses the following environment variables:

```env
DANGEROUSLY_DISABLE_HOST_CHECK=true  # Allow external access
BROWSER=none                         # Disable auto-browser opening
HOST=0.0.0.0                        # Bind to all interfaces
PORT=12001                          # Dashboard port
WDS_SOCKET_HOST=0.0.0.0             # WebSocket host
WDS_SOCKET_PORT=12001               # WebSocket port
```

### API Configuration
The dashboard connects to the NLP service at:
- **Default URL**: http://localhost:8001
- **Health Endpoint**: /health
- **Analysis Endpoint**: /api/posts/analyze

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Run Tests with Coverage
```bash
npm test -- --coverage
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
npm run lint:fix
```

## 🏗️ Building for Production

```bash
# Build optimized production bundle
npm run build

# The build artifacts will be stored in the `build/` directory
```

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t sentinelbert-frontend .

# Run container
docker run -p 12001:80 sentinelbert-frontend
```

## 🔍 Troubleshooting

### Common Issues

1. **"Invalid Host header" Error**
   - Ensure `.env` file contains `DANGEROUSLY_DISABLE_HOST_CHECK=true`
   - Restart the development server

2. **NLP Service Connection Failed**
   - Verify NLP service is running on port 8001
   - Check `http://localhost:8001/health`

3. **Port Already in Use**
   - Change PORT in `.env` file
   - Kill existing processes: `lsof -ti:12001 | xargs kill`

4. **Dependencies Installation Failed**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules: `rm -rf node_modules`
   - Reinstall: `npm install`

### Logs and Debugging

```bash
# View React development server logs
tail -f react_server.log

# Check running processes
ps aux | grep node

# Check port usage
lsof -i :12001
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
│   └── index.html         # HTML template
├── src/                   # Source code
│   ├── components/        # Reusable components
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx  # Main dashboard
│   │   └── AnalysisPage.tsx # Analysis interface
│   ├── services/         # API services
│   ├── App.tsx           # Main application
│   └── index.tsx         # Entry point
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run linting and tests
6. Submit a pull request

## 📄 License

This project is part of the SentinelBERT platform and follows the same licensing terms.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section above
2. Review the main SentinelBERT documentation
3. Check service logs for error details
4. Ensure all prerequisites are met

---

**Note**: This dashboard requires the SentinelBERT NLP service to be running for full functionality. Make sure to start the backend services before using the dashboard.
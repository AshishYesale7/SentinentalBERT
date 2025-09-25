# macOS Docker Deployment Fix Guide

## 🚨 Issue Description
You're experiencing Docker API version compatibility errors on macOS:
```
request returned 500 Internal Server Error for API route and version http://%2FUsers%2Fashishyesale%2F.docker%2Frun%2Fdocker.sock/v1.51/...
```

This indicates a Docker client/daemon version mismatch or Docker Desktop connectivity issues.

## 🔧 Quick Fixes (Try in Order)

### Fix 1: Restart Docker Desktop
```bash
# Stop Docker Desktop completely
pkill -f Docker

# Wait 10 seconds
sleep 10

# Start Docker Desktop
open -a Docker

# Wait for Docker to fully start (2-3 minutes)
sleep 120

# Test Docker
docker version
```

### Fix 2: Reset Docker Desktop
```bash
# Reset Docker Desktop to factory defaults
# Go to Docker Desktop > Troubleshoot > Reset to factory defaults
# OR use command line:
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/.docker

# Restart Docker Desktop
open -a Docker
```

### Fix 3: Update Docker Desktop
```bash
# Check current version
docker version

# Download latest Docker Desktop from:
# https://docs.docker.com/desktop/install/mac-install/

# Or use Homebrew
brew install --cask docker
```

### Fix 4: Use Docker Machine (Alternative)
```bash
# Install Docker Machine
brew install docker-machine

# Create a new machine
docker-machine create --driver virtualbox default

# Set environment
eval $(docker-machine env default)

# Test
docker version
```

## 🛠️ Comprehensive Solution Script

Create and run this script to fix Docker issues:

```bash
#!/bin/bash
# macos_docker_fix.sh

echo "🔧 macOS Docker Fix Script"
echo "=========================="

# Function to check Docker status
check_docker() {
    if docker version >/dev/null 2>&1; then
        echo "✅ Docker is working"
        return 0
    else
        echo "❌ Docker is not working"
        return 1
    fi
}

# Function to restart Docker Desktop
restart_docker_desktop() {
    echo "🔄 Restarting Docker Desktop..."
    pkill -f Docker
    sleep 10
    open -a Docker
    echo "⏳ Waiting for Docker to start (120 seconds)..."
    sleep 120
}

# Function to check and fix API version
fix_api_version() {
    echo "🔧 Setting Docker API version compatibility..."
    export DOCKER_API_VERSION=1.40
    echo "export DOCKER_API_VERSION=1.40" >> ~/.zshrc
    echo "export DOCKER_API_VERSION=1.40" >> ~/.bash_profile
}

# Main execution
echo "1️⃣ Checking current Docker status..."
if ! check_docker; then
    echo "2️⃣ Attempting to restart Docker Desktop..."
    restart_docker_desktop
    
    if ! check_docker; then
        echo "3️⃣ Setting API version compatibility..."
        fix_api_version
        
        if ! check_docker; then
            echo "❌ Docker still not working. Manual intervention required."
            echo "Please try:"
            echo "- Update Docker Desktop to latest version"
            echo "- Reset Docker Desktop to factory defaults"
            echo "- Restart your Mac"
            exit 1
        fi
    fi
fi

echo "✅ Docker is now working properly!"
docker version
```

## 🐳 Alternative: Use Simplified Docker Compose

Create a macOS-compatible docker-compose file:

```yaml
# docker-compose.macos.yml
services:
  postgres:
    image: postgres:13-alpine  # Use older, more stable version
    container_name: sentinelbert-postgres-macos
    environment:
      POSTGRES_DB: sentinelbert
      POSTGRES_USER: sentinel
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-sentinel123}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine  # Use older, more stable version
    container_name: sentinelbert-redis-macos
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  streamlit-app:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    container_name: sentinelbert-app-macos
    ports:
      - "12000:12000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://sentinel:${POSTGRES_PASSWORD:-sentinel123}@postgres:5432/sentinelbert
      - REDIS_URL=redis://redis:6379
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## 🚀 Quick Deployment Commands

```bash
# Navigate to project directory
cd /path/to/SentinentalBERT

# Set environment variables
export POSTGRES_PASSWORD=sentinel123

# Use the macOS-compatible compose file
docker-compose -f docker-compose.macos.yml up -d

# Check status
docker-compose -f docker-compose.macos.yml ps

# View logs
docker-compose -f docker-compose.macos.yml logs -f
```

## 🔍 Troubleshooting Commands

```bash
# Check Docker Desktop status
docker system info

# Check available images
docker images

# Check running containers
docker ps -a

# Clean up Docker system
docker system prune -a

# Check Docker Desktop logs
tail -f ~/Library/Containers/com.docker.docker/Data/log/vm/dockerd.log
```

## 📱 Docker Desktop Settings

Ensure these settings in Docker Desktop:
1. **Resources > Memory**: At least 4GB
2. **Resources > Disk**: At least 20GB free
3. **Features in Development**: Enable "Use containerd for pulling and storing images"
4. **Docker Engine**: Add this configuration:
   ```json
   {
     "experimental": false,
     "debug": true,
     "api-cors-header": "*"
   }
   ```

## 🆘 If All Else Fails

### Option 1: Use Podman (Docker Alternative)
```bash
# Install Podman
brew install podman

# Initialize Podman machine
podman machine init
podman machine start

# Use podman instead of docker
alias docker=podman
```

### Option 2: Use Lima + Docker
```bash
# Install Lima
brew install lima

# Create Docker environment
limactl start template://docker

# Use Lima Docker
export DOCKER_HOST=$(limactl list docker --format 'unix://{{.Dir}}/sock/docker.sock')
```

### Option 3: Native Python Deployment
```bash
# Skip Docker entirely and run natively
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run enhanced_viral_dashboard.py --server.port 12000
```

## 📞 Support

If you continue experiencing issues:
1. Check Docker Desktop version compatibility with your macOS version
2. Ensure you have sufficient disk space (20GB+)
3. Try running Docker Desktop as administrator
4. Check for conflicting virtualization software (VMware, VirtualBox)

---

**Note**: The API version error (v1.51) suggests you might have a very new Docker client with an older daemon. The fixes above should resolve this compatibility issue.
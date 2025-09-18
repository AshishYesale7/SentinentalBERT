# =============================================================================
# SentinelBERT Frontend Dockerfile (React)
# =============================================================================
# 
# This Dockerfile builds the React-based dashboard frontend.
# It uses multi-stage builds for optimization and serves via Nginx.
# 
# Build stages:
# 1. Builder stage: Build React application with Node.js
# 2. Runtime stage: Serve static files with Nginx
# 
# Usage:
#   docker build -t sentinelbert-frontend .
#   docker run -p 3000:80 sentinelbert-frontend
# 
# Build arguments:
#   NODE_VERSION: Node.js version (default: 18)
#   BUILD_MODE: production or development (default: production)
# 
# =============================================================================

# -----------------------------------------------------------------------------
# Builder Stage - Build React application
# -----------------------------------------------------------------------------
ARG NODE_VERSION=18
FROM node:${NODE_VERSION}-alpine as builder

# Build arguments
ARG BUILD_MODE=production
ARG REACT_APP_VERSION=1.0.0

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apk add --no-cache \
    # Build tools
    python3 \
    make \
    g++ \
    # Git for dependency resolution
    git \
    # Curl for health checks
    curl

# Set Node.js environment
ENV NODE_ENV=${BUILD_MODE}
ENV CI=true
ENV GENERATE_SOURCEMAP=false

# Copy package files first for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production --silent

# Copy source code
COPY public/ ./public/
COPY src/ ./src/
COPY tsconfig.json ./
COPY .env* ./

# Set build-time environment variables
ENV REACT_APP_VERSION=${REACT_APP_VERSION}
ENV REACT_APP_BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build the React application
RUN npm run build

# Optimize build output
RUN npm run build:analyze 2>/dev/null || true

# Remove source maps in production
RUN if [ "$BUILD_MODE" = "production" ]; then \
        find build -name "*.map" -type f -delete; \
    fi

# -----------------------------------------------------------------------------
# Runtime Stage - Nginx web server
# -----------------------------------------------------------------------------
FROM nginx:1.25-alpine as runtime

# Install runtime dependencies
RUN apk add --no-cache \
    # Curl for health checks
    curl \
    # Timezone data
    tzdata \
    # Process monitoring
    procps

# Create non-root user for Nginx
RUN addgroup -g 1001 -S sentinelbert && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G sentinelbert -g sentinelbert sentinelbert

# Copy built React application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-default.conf /etc/nginx/conf.d/default.conf

# Create necessary directories and set permissions
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/run && \
    chown -R sentinelbert:sentinelbert /var/cache/nginx /var/log/nginx /var/run /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Create health check endpoint
RUN echo '<!DOCTYPE html><html><head><title>Health Check</title></head><body><h1>OK</h1></body></html>' > /usr/share/nginx/html/health

# Switch to non-root user
USER sentinelbert

# Set environment variables
ENV NGINX_WORKER_PROCESSES=auto
ENV NGINX_WORKER_CONNECTIONS=1024
ENV NGINX_KEEPALIVE_TIMEOUT=65
ENV NGINX_CLIENT_MAX_BODY_SIZE=10m

# Expose HTTP port
EXPOSE 80

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Default command to run Nginx
CMD ["nginx", "-g", "daemon off;"]

# -----------------------------------------------------------------------------
# Development Stage - Development server with hot reload
# -----------------------------------------------------------------------------
FROM node:${NODE_VERSION}-alpine as development

# Install development dependencies
RUN apk add --no-cache \
    git \
    curl \
    vim

# Set working directory
WORKDIR /app

# Set development environment
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV WATCHPACK_POLLING=true

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including dev dependencies)
RUN npm ci --silent

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S sentinelbert && \
    adduser -S -D -H -u 1001 -h /app -s /bin/sh -G sentinelbert -g sentinelbert sentinelbert && \
    chown -R sentinelbert:sentinelbert /app

# Switch to non-root user
USER sentinelbert

# Expose development server port
EXPOSE 3000

# Health check for development server
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Development command with hot reload
CMD ["npm", "start"]

# -----------------------------------------------------------------------------
# Production Stage - Additional production optimizations
# -----------------------------------------------------------------------------
FROM runtime as production

# Switch back to root for configuration
USER root

# Install additional production tools
RUN apk add --no-cache \
    # Log rotation
    logrotate \
    # Monitoring tools
    htop

# Configure log rotation
RUN echo '/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 sentinelbert sentinelbert
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}' > /etc/logrotate.d/nginx

# Production Nginx configuration with optimizations
COPY nginx-production.conf /etc/nginx/nginx.conf

# Enable gzip compression for better performance
RUN echo 'gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml;' > /etc/nginx/conf.d/gzip.conf

# Security headers configuration
RUN echo 'add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src '\''self'\''; script-src '\''self'\''; style-src '\''self'\'' '\''unsafe-inline'\''; img-src '\''self'\'' data: https:; font-src '\''self'\''; connect-src '\''self'\'' ws: wss:;" always;' > /etc/nginx/conf.d/security.conf

# Switch back to non-root user
USER sentinelbert

# Production environment variables
ENV NGINX_WORKER_PROCESSES=auto
ENV NGINX_WORKER_CONNECTIONS=2048
ENV NGINX_KEEPALIVE_TIMEOUT=30
ENV NGINX_CLIENT_MAX_BODY_SIZE=1m

# Production command
CMD ["nginx", "-g", "daemon off;"]

# -----------------------------------------------------------------------------
# Metadata and Labels
# -----------------------------------------------------------------------------
LABEL maintainer="SentinelBERT Team <team@sentinelbert.com>"
LABEL version="1.0.0"
LABEL description="SentinelBERT Frontend Dashboard (React)"
LABEL org.opencontainers.image.title="SentinelBERT Frontend"
LABEL org.opencontainers.image.description="React-based dashboard for social media analysis"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="SentinelBERT"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/your-org/SentinelBERT"

# Frontend-specific labels
LABEL frontend.framework="React"
LABEL frontend.framework.version="18.2.0"
LABEL frontend.server="Nginx"
LABEL frontend.server.version="1.25"

# Security labels
LABEL security.non-root="true"
LABEL security.user="sentinelbert"
LABEL security.capabilities="none"

# Build information
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.version=$VERSION
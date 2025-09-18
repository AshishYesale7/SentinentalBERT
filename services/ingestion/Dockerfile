# =============================================================================
# SentinelBERT Ingestion Service Dockerfile (Rust)
# =============================================================================
# 
# This Dockerfile builds the high-performance Rust-based data ingestion service.
# It uses multi-stage builds for optimization and security.
# 
# Build stages:
# 1. Builder stage: Compile Rust application with optimizations
# 2. Runtime stage: Minimal runtime environment with security hardening
# 
# Usage:
#   docker build -t sentinelbert-ingestion .
#   docker run -p 8081:8081 sentinelbert-ingestion
# 
# Build arguments:
#   RUST_VERSION: Rust toolchain version (default: 1.75)
#   BUILD_MODE: release or debug (default: release)
# 
# =============================================================================

# -----------------------------------------------------------------------------
# Builder Stage - Compile Rust application
# -----------------------------------------------------------------------------
FROM rust:1.75-slim as builder

# Build arguments
ARG BUILD_MODE=release
ARG RUST_VERSION=1.75

# Set working directory
WORKDIR /app

# Install system dependencies required for compilation
RUN apt-get update && apt-get install -y \
    # Build essentials
    build-essential \
    # SSL/TLS support
    pkg-config \
    libssl-dev \
    # PostgreSQL client library
    libpq-dev \
    # Additional tools
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install specific Rust toolchain if different from base image
RUN if [ "$RUST_VERSION" != "1.75" ]; then \
        rustup install $RUST_VERSION && \
        rustup default $RUST_VERSION; \
    fi

# Copy dependency manifests first for better Docker layer caching
COPY Cargo.toml Cargo.lock ./

# Create a dummy main.rs to build dependencies
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    echo "// dummy" > src/lib.rs

# Build dependencies (this layer will be cached unless Cargo.toml changes)
RUN if [ "$BUILD_MODE" = "release" ]; then \
        cargo build --release; \
    else \
        cargo build; \
    fi

# Remove dummy source files
RUN rm -rf src/

# Copy actual source code
COPY src/ ./src/

# Build the application with optimizations
RUN if [ "$BUILD_MODE" = "release" ]; then \
        cargo build --release && \
        cp target/release/sentinel-ingestion /app/sentinel-ingestion; \
    else \
        cargo build && \
        cp target/debug/sentinel-ingestion /app/sentinel-ingestion; \
    fi

# Strip binary to reduce size (release mode only)
RUN if [ "$BUILD_MODE" = "release" ]; then \
        strip /app/sentinel-ingestion; \
    fi

# -----------------------------------------------------------------------------
# Runtime Stage - Minimal runtime environment
# -----------------------------------------------------------------------------
FROM debian:bookworm-slim as runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    # SSL certificates for HTTPS requests
    ca-certificates \
    # PostgreSQL client library (runtime)
    libpq5 \
    # SSL/TLS runtime library
    libssl3 \
    # Curl for health checks
    curl \
    # Timezone data
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r sentinelbert && \
    useradd -r -g sentinelbert -d /app -s /sbin/nologin \
    -c "SentinelBERT Ingestion Service" sentinelbert

# Set working directory
WORKDIR /app

# Copy compiled binary from builder stage
COPY --from=builder /app/sentinel-ingestion /app/sentinel-ingestion

# Copy configuration files
COPY config.toml /app/config.toml

# Create directories for logs and data
RUN mkdir -p /var/log/sentinelbert /app/data && \
    chown -R sentinelbert:sentinelbert /app /var/log/sentinelbert

# Set executable permissions
RUN chmod +x /app/sentinel-ingestion

# Switch to non-root user
USER sentinelbert

# Set environment variables
ENV RUST_LOG=info
ENV RUST_BACKTRACE=1
ENV CONFIG_FILE=/app/config.toml

# Expose service port
EXPOSE 8081

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Set resource limits (can be overridden by docker-compose)
# These are soft limits for the container
ENV MEMORY_LIMIT=1G
ENV CPU_LIMIT=1.0

# Default command to run the service
CMD ["/app/sentinel-ingestion", "--config", "/app/config.toml"]

# -----------------------------------------------------------------------------
# Metadata and Labels
# -----------------------------------------------------------------------------
LABEL maintainer="SentinelBERT Team <team@sentinelbert.com>"
LABEL version="1.0.0"
LABEL description="SentinelBERT High-Performance Data Ingestion Service"
LABEL org.opencontainers.image.title="SentinelBERT Ingestion Service"
LABEL org.opencontainers.image.description="Rust-based social media data ingestion service"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="SentinelBERT"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/your-org/SentinelBERT"
LABEL org.opencontainers.image.documentation="https://github.com/your-org/SentinelBERT/blob/main/README.md"

# Security labels
LABEL security.non-root="true"
LABEL security.user="sentinelbert"
LABEL security.capabilities="none"

# Build information (will be populated by CI/CD)
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.revision=$VCS_REF
LABEL org.opencontainers.image.version=$VERSION
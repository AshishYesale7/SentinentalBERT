# =============================================================================
# SentinelBERT Backend Service Dockerfile (Spring Boot/Java)
# =============================================================================
# 
# This Dockerfile builds the Spring Boot backend service for API orchestration.
# It uses multi-stage builds for optimization and includes JVM tuning.
# 
# Build stages:
# 1. Builder stage: Compile Java application with Maven
# 2. Runtime stage: Optimized JRE environment with security hardening
# 
# Usage:
#   docker build -t sentinelbert-backend .
#   docker run -p 8080:8080 sentinelbert-backend
# 
# Build arguments:
#   JAVA_VERSION: Java version (default: 17)
#   MAVEN_VERSION: Maven version (default: 3.9)
# 
# =============================================================================

# -----------------------------------------------------------------------------
# Builder Stage - Compile Java application
# -----------------------------------------------------------------------------
ARG JAVA_VERSION=17
ARG MAVEN_VERSION=3.9

FROM maven:${MAVEN_VERSION}-openjdk-${JAVA_VERSION}-slim as builder

# Build arguments
ARG MAVEN_OPTS="-Dmaven.repo.local=/root/.m2/repository -Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.transfer.Slf4jMavenTransferListener=WARN -Dorg.slf4j.simpleLogger.showDateTime=true -Djava.awt.headless=true"
ARG MAVEN_CLI_OPTS="--batch-mode --errors --fail-at-end --show-version -DinstallAtEnd=true -DdeployAtEnd=true"

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    # Git for dependency resolution
    git \
    # Curl for health checks
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Maven configuration files first for better caching
COPY pom.xml ./
COPY .mvn/ ./.mvn/
COPY mvnw ./

# Make Maven wrapper executable
RUN chmod +x ./mvnw

# Download dependencies (this layer will be cached unless pom.xml changes)
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src/ ./src/

# Build the application
RUN ./mvnw clean package -DskipTests ${MAVEN_CLI_OPTS}

# Extract JAR layers for better Docker layer caching
RUN java -Djarmode=layertools -jar target/*.jar extract

# -----------------------------------------------------------------------------
# Runtime Stage - Optimized JRE environment
# -----------------------------------------------------------------------------
FROM openjdk:${JAVA_VERSION}-jre-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    # SSL certificates
    ca-certificates \
    # Curl for health checks
    curl \
    # Timezone data
    tzdata \
    # Process monitoring tools
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r sentinelbert && \
    useradd -r -g sentinelbert -d /app -s /sbin/nologin \
    -c "SentinelBERT Backend Service" sentinelbert

# Set working directory
WORKDIR /app

# Copy JAR layers from builder stage (in order of change frequency)
COPY --from=builder /app/dependencies/ ./
COPY --from=builder /app/spring-boot-loader/ ./
COPY --from=builder /app/snapshot-dependencies/ ./
COPY --from=builder /app/application/ ./

# Create directories for logs and data
RUN mkdir -p /var/log/sentinelbert /app/data /app/config && \
    chown -R sentinelbert:sentinelbert /app /var/log/sentinelbert

# Copy application configuration
COPY src/main/resources/application*.yml /app/config/

# Switch to non-root user
USER sentinelbert

# Set JVM environment variables for optimization
ENV JAVA_OPTS="-Xmx2g -Xms1g \
    -XX:+UseG1GC \
    -XX:MaxGCPauseMillis=200 \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseCGroupMemoryLimitForHeap \
    -XX:+UseContainerSupport \
    -Djava.security.egd=file:/dev/./urandom \
    -Djava.awt.headless=true \
    -Dfile.encoding=UTF-8 \
    -Duser.timezone=UTC"

# Spring Boot specific environment variables
ENV SPRING_PROFILES_ACTIVE=docker \
    SPRING_CONFIG_LOCATION=classpath:/application.yml,classpath:/application-docker.yml,file:/app/config/ \
    LOGGING_FILE_PATH=/var/log/sentinelbert \
    LOGGING_LEVEL_ROOT=INFO \
    MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE=health,metrics,prometheus,info

# Application-specific environment variables
ENV SERVER_PORT=8080 \
    SERVER_SERVLET_CONTEXT_PATH=/api \
    MANAGEMENT_SERVER_PORT=8081 \
    MANAGEMENT_ENDPOINTS_WEB_BASE_PATH=/actuator

# Security environment variables
ENV SECURITY_REQUIRE_SSL=false \
    SECURITY_SESSIONS_CREATION_POLICY=stateless

# Database connection pool settings
ENV SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE=20 \
    SPRING_DATASOURCE_HIKARI_MINIMUM_IDLE=5 \
    SPRING_DATASOURCE_HIKARI_CONNECTION_TIMEOUT=30000 \
    SPRING_DATASOURCE_HIKARI_IDLE_TIMEOUT=600000 \
    SPRING_DATASOURCE_HIKARI_MAX_LIFETIME=1800000

# Redis connection settings
ENV SPRING_REDIS_TIMEOUT=2000 \
    SPRING_REDIS_LETTUCE_POOL_MAX_ACTIVE=8 \
    SPRING_REDIS_LETTUCE_POOL_MAX_IDLE=8 \
    SPRING_REDIS_LETTUCE_POOL_MIN_IDLE=0

# Expose application port
EXPOSE 8080

# Expose management port for health checks and metrics
EXPOSE 8081

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8081/actuator/health || exit 1

# Set resource limits
ENV MEMORY_LIMIT=2G \
    CPU_LIMIT=1.0

# Default command to run the Spring Boot application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/BOOT-INF/lib/*.jar"]

# Alternative entrypoint for debugging
# ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 -jar /app/BOOT-INF/lib/*.jar"]

# -----------------------------------------------------------------------------
# Development Stage - Additional development tools
# -----------------------------------------------------------------------------
FROM runtime as development

# Switch back to root to install development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    # Development tools
    vim \
    nano \
    # System monitoring
    htop \
    top \
    # Network tools
    netcat-openbsd \
    telnet \
    # JVM debugging tools
    jstack \
    jmap \
    jstat \
    # Process management
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install additional JVM debugging tools
RUN curl -L https://github.com/jvm-profiling-tools/async-profiler/releases/download/v2.9/async-profiler-2.9-linux-x64.tar.gz \
    | tar -xzC /opt/ && \
    ln -s /opt/async-profiler-2.9-linux-x64/profiler.sh /usr/local/bin/profiler

# Switch back to non-root user
USER sentinelbert

# Development JVM options with debugging enabled
ENV JAVA_OPTS_DEV="-Xmx2g -Xms1g \
    -XX:+UseG1GC \
    -XX:MaxGCPauseMillis=200 \
    -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005 \
    -Djava.security.egd=file:/dev/./urandom \
    -Djava.awt.headless=true \
    -Dspring.devtools.restart.enabled=true \
    -Dspring.devtools.livereload.enabled=true"

# Expose debugging port
EXPOSE 5005

# Development command with debugging enabled
CMD ["sh", "-c", "java $JAVA_OPTS_DEV -jar /app/BOOT-INF/lib/*.jar"]

# -----------------------------------------------------------------------------
# Production Stage - Additional production optimizations
# -----------------------------------------------------------------------------
FROM runtime as production

# Production JVM options with additional optimizations
ENV JAVA_OPTS_PROD="-Xmx2g -Xms2g \
    -XX:+UseG1GC \
    -XX:MaxGCPauseMillis=200 \
    -XX:+UseStringDeduplication \
    -XX:+OptimizeStringConcat \
    -XX:+UseCompressedOops \
    -XX:+UseCompressedClassPointers \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseCGroupMemoryLimitForHeap \
    -XX:+UseContainerSupport \
    -XX:InitialRAMPercentage=50.0 \
    -XX:MaxRAMPercentage=80.0 \
    -Djava.security.egd=file:/dev/./urandom \
    -Djava.awt.headless=true \
    -Dfile.encoding=UTF-8 \
    -Duser.timezone=UTC \
    -Dspring.jmx.enabled=false"

# Production Spring profiles
ENV SPRING_PROFILES_ACTIVE=docker,production

# Disable development features
ENV SPRING_DEVTOOLS_RESTART_ENABLED=false \
    SPRING_DEVTOOLS_LIVERELOAD_ENABLED=false

# Production logging configuration
ENV LOGGING_LEVEL_ROOT=WARN \
    LOGGING_LEVEL_COM_SENTINELBERT=INFO \
    LOGGING_PATTERN_CONSOLE="%d{yyyy-MM-dd HH:mm:ss} - %msg%n" \
    LOGGING_PATTERN_FILE="%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"

# Production command
CMD ["sh", "-c", "java $JAVA_OPTS_PROD -jar /app/BOOT-INF/lib/*.jar"]

# -----------------------------------------------------------------------------
# Metadata and Labels
# -----------------------------------------------------------------------------
LABEL maintainer="SentinelBERT Team <team@sentinelbert.com>"
LABEL version="1.0.0"
LABEL description="SentinelBERT Backend API Service (Spring Boot)"
LABEL org.opencontainers.image.title="SentinelBERT Backend Service"
LABEL org.opencontainers.image.description="Spring Boot backend service for API orchestration"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="SentinelBERT"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/your-org/SentinelBERT"

# Java-specific labels
LABEL java.version="${JAVA_VERSION}"
LABEL java.vendor="OpenJDK"
LABEL framework="Spring Boot"
LABEL framework.version="3.2.0"

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
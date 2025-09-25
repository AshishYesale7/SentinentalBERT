# Docker Build Fixes for macOS Deployment

## Issues Identified and Fixed

### 1. Frontend Dockerfile Issue (Line 65)
**Problem**: 
```dockerfile
ENV REACT_APP_BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```
Docker ENV doesn't support command substitution during build time.

**Solution**: 
```dockerfile
ARG REACT_APP_VERSION=1.0.0
ARG REACT_APP_BUILD_DATE
ENV REACT_APP_VERSION=${REACT_APP_VERSION}
RUN if [ -z "$REACT_APP_BUILD_DATE" ]; then \
        export REACT_APP_BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ"); \
    fi && \
    echo "REACT_APP_BUILD_DATE=${REACT_APP_BUILD_DATE}" >> .env.local
```

### 2. NLP Service Dockerfile Issues (Multiple Lines)
**Problem**: Multi-line RUN commands with Python code were not properly formatted:
```dockerfile
RUN python -c "
from transformers import AutoTokenizer, AutoModel
import torch
...
"
```

**Solution**: Converted to single-line format with proper escaping:
```dockerfile
RUN python -c "\
from transformers import AutoTokenizer, AutoModel; \
import torch; \
..."
```

### 3. Docker Compose Version Warning
**Problem**: 
```yaml
version: '3.8'
```
The `version` field is deprecated in newer Docker Compose versions.

**Solution**: Remove the version field entirely (optional fix for warnings).

## Files Modified

1. **`frontend/Dockerfile`** - Fixed ENV command substitution issue
2. **`services/nlp/Dockerfile`** - Fixed multiple multi-line RUN commands:
   - BERT model download section (lines 128-148)
   - Additional models download section (lines 146-153)
   - Model warmup section (lines 211-221)

## Testing Tools Created

### 1. `test-docker-build.sh`
A comprehensive test script that builds each Docker image individually to identify issues:
```bash
chmod +x test-docker-build.sh
./test-docker-build.sh
```

### 2. `docker-compose.test.yml`
A minimal docker-compose file for testing individual services:
```bash
docker-compose -f docker-compose.test.yml build
```

### 3. `fix-docker-compose-version.sh`
Script to remove deprecated version fields from docker-compose files:
```bash
chmod +x fix-docker-compose-version.sh
./fix-docker-compose-version.sh
```

## How to Test the Fixes

### Option 1: Test Individual Builds
```bash
# Test the fixes
./test-docker-build.sh

# If successful, run the quick-start script
./quick-start.sh
```

### Option 2: Test with Docker Compose
```bash
# Test specific services
docker-compose -f docker-compose.test.yml build frontend-test
docker-compose -f docker-compose.test.yml build nlp-test
docker-compose -f docker-compose.test.yml build streamlit-test
```

### Option 3: Direct Docker Build
```bash
# Test frontend build
docker build -t test-frontend \
  --build-arg REACT_APP_VERSION=1.0.0 \
  --build-arg REACT_APP_BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  ./frontend

# Test NLP service build
docker build -t test-nlp ./services/nlp

# Test Streamlit dashboard build
docker build -t test-streamlit -f Dockerfile.dashboard .
```

## Expected Results

After applying these fixes, you should see:
- ✅ No more "Syntax error - can't find = in" errors
- ✅ No more "dockerfile parse error" messages
- ✅ Successful Docker image builds
- ⚠️ Version warnings may still appear but won't cause build failures

## Next Steps

1. Run `./test-docker-build.sh` to verify all fixes work
2. If tests pass, run `./quick-start.sh` again
3. The deployment should now complete successfully

## Troubleshooting

If you still encounter issues:

1. **Check Docker version**: Ensure you have Docker Desktop 4.0+ on macOS
2. **Check available disk space**: Docker builds require significant space
3. **Check memory allocation**: Increase Docker Desktop memory to 8GB+
4. **Clear Docker cache**: Run `docker system prune -a` if needed

## Additional Notes

- The fixes maintain full functionality while ensuring Docker compatibility
- Build arguments are now properly handled for environment variables
- Multi-line Python scripts are converted to single-line format for Docker compatibility
- All original functionality is preserved
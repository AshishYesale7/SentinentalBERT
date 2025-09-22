# InsideOut Platform Test Suite

This directory contains comprehensive test suites for validating the InsideOut platform deployment, functionality, and security.

## Test Categories

### 1. Deployment Tests
- **`test_final_deployment_validation.py`** - Complete deployment validation with security checks
- **`test_complete_deployment.py`** - Comprehensive deployment testing
- **`test_docker_deployment_simple.py`** - Simple Docker deployment validation
- **`test_docker_deployment.py`** - Full Docker deployment testing
- **`test_deployment_validation.py`** - Basic deployment validation

### 2. Platform Compatibility Tests
- **`test_macos_compatibility.py`** - macOS deployment compatibility testing
- **`test_full_deployment_simulation.py`** - Full deployment simulation

### 3. Security Tests
- **`test_static_security_validation.py`** - Static security analysis
- **`test_authentication_functionality.py`** - Authentication system testing
- **`test_enhanced_integration.py`** - Enhanced security integration tests

### 4. Functionality Tests
- **`test_core_functionality.py`** - Core platform functionality
- **`test_viral_analysis.py`** - Viral content detection testing

## Running Tests

### Prerequisites
1. Ensure Docker and Docker Compose are installed
2. Copy `.env.example` to `.env` and configure all required variables
3. Install Python dependencies: `pip install -r requirements.txt`

### Individual Test Execution

```bash
# Run final deployment validation (recommended)
python tests/test_final_deployment_validation.py

# Run macOS compatibility test
python tests/test_macos_compatibility.py

# Run security validation
python tests/test_static_security_validation.py

# Run authentication tests
python tests/test_authentication_functionality.py
```

### Batch Test Execution

```bash
# Run all deployment tests
for test in tests/test_*deployment*.py; do
    echo "Running $test..."
    python "$test"
done

# Run all security tests
for test in tests/test_*security*.py tests/test_*authentication*.py; do
    echo "Running $test..."
    python "$test"
done
```

## Test Results

Each test generates:
- **Console output** with real-time progress and results
- **Log files** (`.log`) with detailed execution information
- **JSON results** (`*_results.json`) with structured test outcomes

## Test Status Codes

- **Exit Code 0**: All tests passed
- **Exit Code 1**: Critical failures detected
- **Exit Code 2**: Tests passed with warnings
- **Exit Code 130**: Tests interrupted by user

## Recommended Test Sequence

1. **Platform Readiness**: `test_final_deployment_validation.py`
2. **Security Validation**: `test_static_security_validation.py`
3. **Authentication**: `test_authentication_functionality.py`
4. **Platform Compatibility**: `test_macos_compatibility.py` (if on macOS)
5. **Core Functionality**: `test_core_functionality.py`

## Test Environment Setup

### Docker Services
Tests require the following Docker services to be running:
```bash
docker compose up -d postgres redis
```

### Environment Variables
Ensure these critical variables are set in `.env`:
```
POSTGRES_PASSWORD=<secure_password>
REDIS_PASSWORD=<secure_password>
JWT_SECRET=<32_character_secret>
WARRANT_VERIFICATION_ENDPOINT=<legal_system_endpoint>
EVIDENCE_CHAIN_ENDPOINT=<evidence_system_endpoint>
```

## Security Considerations

- Tests validate security configurations but do not expose sensitive data
- All test data is ephemeral and cleaned up after execution
- Production credentials should never be used in test environments
- Tests verify but do not modify security settings

## Troubleshooting

### Common Issues

1. **Docker Connection Errors**
   - Ensure Docker daemon is running
   - Check Docker Compose services: `docker compose ps`

2. **Database Connection Failures**
   - Verify PostgreSQL container is healthy: `docker compose logs postgres`
   - Check Redis connectivity: `docker compose logs redis`

3. **Permission Errors**
   - Ensure test files are executable: `chmod +x tests/*.py`
   - Check Docker socket permissions

4. **Environment Variable Issues**
   - Verify `.env` file exists and is properly formatted
   - Check for missing required variables

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=debug
python tests/test_name.py
```

## Contributing

When adding new tests:
1. Follow the naming convention: `test_<category>_<description>.py`
2. Include comprehensive error handling and cleanup
3. Generate both console output and JSON results
4. Document test purpose and requirements
5. Add entry to this README

## Test Coverage

Current test coverage includes:
- ✅ Docker deployment validation
- ✅ Database connectivity and functionality
- ✅ Security configuration validation
- ✅ Authentication system testing
- ✅ Platform compatibility (Linux/macOS)
- ✅ Core service health checks
- ✅ Environment configuration validation
- ⚠️  API endpoint testing (partial)
- ⚠️  End-to-end workflow testing (partial)
- ❌ Load testing (not implemented)
- ❌ Performance benchmarking (not implemented)

## Next Steps

See `REMAINING_TASKS.md` for outstanding test development and validation tasks.
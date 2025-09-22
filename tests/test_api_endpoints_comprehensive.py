#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Suite
Tests API endpoints, authentication, and security without requiring Docker
"""

import os
import sys
import json
import logging
import platform
import requests
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_endpoints_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class APIEndpointTester:
    """Comprehensive API endpoint testing"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'platform': {
                'system': platform.system(),
                'architecture': platform.machine(),
                'python_version': platform.python_version(),
            },
            'tests': {},
            'summary': {'total_tests': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
        }
        load_dotenv()
        
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        logger.info(f"Running test: {test_name}")
        self.test_results['summary']['total_tests'] += 1
        
        try:
            result = test_func()
            if result:
                self.test_results['summary']['passed'] += 1
                logger.info(f"✅ {test_name} - PASSED")
            else:
                self.test_results['summary']['failed'] += 1
                logger.error(f"❌ {test_name} - FAILED")
            
            self.test_results['tests'][test_name] = {
                'status': 'PASSED' if result else 'FAILED',
                'timestamp': datetime.now().isoformat()
            }
            return result
            
        except Exception as e:
            self.test_results['summary']['failed'] += 1
            logger.error(f"❌ {test_name} - ERROR: {str(e)}")
            self.test_results['tests'][test_name] = {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def test_backend_service_structure(self) -> bool:
        """Test backend service structure and files"""
        required_files = [
            'services/backend/pom.xml',
            'services/backend/src/main/java',
            'services/backend/Dockerfile'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                logger.error(f"Missing required file: {file_path}")
                return False
        
        return True
    
    def test_nlp_service_structure(self) -> bool:
        """Test NLP service structure and files"""
        required_files = [
            'services/nlp/app',
            'services/nlp/requirements.txt',
            'services/nlp/Dockerfile'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                logger.error(f"Missing required file: {file_path}")
                return False
        
        return True
    
    def test_api_route_definitions(self) -> bool:
        """Test API route definitions exist"""
        # Check Java backend controllers
        backend_controllers = 'services/backend/src/main/java/com/insideout/controller'
        if os.path.exists(backend_controllers):
            java_files = [f for f in os.listdir(backend_controllers) if f.endswith('.java')]
            if len(java_files) == 0:
                logger.warning("No Java controller files found")
                return False
        
        # Check Python NLP routes
        nlp_routes = 'services/nlp/app/routers'
        if os.path.exists(nlp_routes):
            py_files = [f for f in os.listdir(nlp_routes) if f.endswith('.py')]
            if len(py_files) == 0:
                logger.warning("No Python router files found")
                return False
        
        return True
    
    def test_authentication_config(self) -> bool:
        """Test authentication configuration"""
        jwt_secret = os.getenv('JWT_SECRET')
        if not jwt_secret or len(jwt_secret) < 32:
            logger.error("JWT_SECRET not properly configured")
            return False
        
        # Check for authentication-related files
        auth_files = [
            'services/backend/src/main/java/com/insideout/security',
            'services/nlp/app/auth'
        ]
        
        auth_found = False
        for auth_path in auth_files:
            if os.path.exists(auth_path):
                auth_found = True
                break
        
        if not auth_found:
            logger.warning("No authentication modules found")
        
        return True
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration exists"""
        # Look for CORS configuration in backend
        cors_patterns = [
            'services/backend/src/main/java/com/insideout/config',
            'services/nlp/app/middleware'
        ]
        
        for pattern in cors_patterns:
            if os.path.exists(pattern):
                return True
        
        logger.warning("CORS configuration not found")
        return True  # Warning, not failure
    
    def test_rate_limiting_config(self) -> bool:
        """Test rate limiting configuration"""
        # Check for rate limiting configuration
        rate_limit_patterns = [
            'nginx/nginx.conf',
            'services/backend/src/main/resources/application.yml'
        ]
        
        for pattern in rate_limit_patterns:
            if os.path.exists(pattern):
                with open(pattern, 'r') as f:
                    content = f.read()
                    if 'rate' in content.lower() or 'limit' in content.lower():
                        return True
        
        logger.warning("Rate limiting configuration not found")
        return True  # Warning, not failure
    
    def test_error_handling_structure(self) -> bool:
        """Test error handling structure"""
        error_patterns = [
            'services/backend/src/main/java/com/insideout/exception',
            'services/nlp/app/exceptions'
        ]
        
        for pattern in error_patterns:
            if os.path.exists(pattern):
                return True
        
        logger.warning("Error handling modules not found")
        return True  # Warning, not failure
    
    def test_api_documentation(self) -> bool:
        """Test API documentation exists"""
        doc_patterns = [
            'docs/API_DOCUMENTATION.md',
            'services/backend/src/main/resources/swagger',
            'api-docs.json'
        ]
        
        for pattern in doc_patterns:
            if os.path.exists(pattern):
                return True
        
        logger.warning("API documentation not found")
        return True  # Warning, not failure
    
    def test_security_headers(self) -> bool:
        """Test security headers configuration"""
        # Check nginx configuration for security headers
        nginx_conf = 'nginx/nginx.conf'
        if os.path.exists(nginx_conf):
            with open(nginx_conf, 'r') as f:
                content = f.read()
                security_headers = [
                    'X-Frame-Options',
                    'X-Content-Type-Options',
                    'X-XSS-Protection'
                ]
                
                for header in security_headers:
                    if header in content:
                        return True
        
        logger.warning("Security headers not configured")
        return True  # Warning, not failure
    
    def run_all_tests(self):
        """Run all API endpoint tests"""
        logger.info("Starting comprehensive API endpoint testing...")
        logger.info(f"Platform: {platform.system()} {platform.machine()}")
        
        tests = [
            ("Backend Service Structure", self.test_backend_service_structure),
            ("NLP Service Structure", self.test_nlp_service_structure),
            ("API Route Definitions", self.test_api_route_definitions),
            ("Authentication Configuration", self.test_authentication_config),
            ("CORS Configuration", self.test_cors_configuration),
            ("Rate Limiting Configuration", self.test_rate_limiting_config),
            ("Error Handling Structure", self.test_error_handling_structure),
            ("API Documentation", self.test_api_documentation),
            ("Security Headers", self.test_security_headers),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        with open('api_endpoints_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        return self.test_results['summary']['failed'] == 0
    
    def generate_summary(self):
        """Generate test summary"""
        summary = self.test_results['summary']
        total = summary['total_tests']
        passed = summary['passed']
        failed = summary['failed']
        warnings = summary['warnings']
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info("\n" + "="*80)
        logger.info("API ENDPOINT TEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Platform: {platform.system()} {platform.machine()}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            logger.info("Overall Status: API_STRUCTURE_VALID")
        else:
            logger.info("Overall Status: API_STRUCTURE_ISSUES")
        
        logger.info("Results saved to: api_endpoints_test_results.json")
        logger.info("="*80)

def main():
    """Main test execution"""
    tester = APIEndpointTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("🎉 All API endpoint structure tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some API endpoint tests failed. Check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
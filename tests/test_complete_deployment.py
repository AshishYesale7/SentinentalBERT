#!/usr/bin/env python3
"""
Comprehensive Deployment Test Suite
Tests the complete SentinentalBERT platform with security fixes
"""

import os
import sys
import json
import time
import requests
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentTester:
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.get_environment_info(),
            'tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        self.base_url = "http://localhost"
        self.services = {
            'nlp': 8001,
            'backend': 8080,
            'frontend': 3000,
            'postgres': 5432,
            'redis': 6379,
            'elasticsearch': 9200
        }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get system environment information"""
        try:
            return {
                'os': os.uname().sysname,
                'kernel': os.uname().release,
                'architecture': os.uname().machine,
                'python_version': sys.version,
                'docker_version': subprocess.check_output(['docker', '--version'], text=True).strip(),
                'docker_compose_version': subprocess.check_output(['docker', 'compose', 'version'], text=True).strip()
            }
        except Exception as e:
            logger.error(f"Failed to get environment info: {e}")
            return {'error': str(e)}
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        logger.info(f"Running test: {test_name}")
        self.test_results['summary']['total_tests'] += 1
        
        try:
            result = test_func()
            if result.get('status') == 'passed':
                self.test_results['summary']['passed'] += 1
                logger.info(f"✅ {test_name} - PASSED")
            elif result.get('status') == 'warning':
                self.test_results['summary']['warnings'] += 1
                logger.warning(f"⚠️  {test_name} - WARNING: {result.get('message', '')}")
            else:
                self.test_results['summary']['failed'] += 1
                logger.error(f"❌ {test_name} - FAILED: {result.get('message', '')}")
            
            self.test_results['tests'][test_name] = result
            return result.get('status') == 'passed'
            
        except Exception as e:
            self.test_results['summary']['failed'] += 1
            error_msg = f"Exception in {test_name}: {str(e)}"
            logger.error(f"❌ {test_name} - ERROR: {error_msg}")
            self.test_results['tests'][test_name] = {
                'status': 'failed',
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            }
            return False
    
    def test_environment_setup(self) -> Dict[str, Any]:
        """Test environment configuration"""
        issues = []
        
        # Check .env file exists
        if not os.path.exists('.env'):
            issues.append("Missing .env file")
        else:
            # Check required environment variables
            required_vars = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'ELASTIC_PASSWORD', 'JWT_SECRET']
            with open('.env', 'r') as f:
                env_content = f.read()
                for var in required_vars:
                    if f"{var}=" not in env_content:
                        issues.append(f"Missing {var} in .env file")
                    elif f"{var}=your-" in env_content:
                        issues.append(f"{var} still has template value")
        
        # Check Docker Compose file
        if not os.path.exists('docker-compose.yml'):
            issues.append("Missing docker-compose.yml file")
        
        return {
            'status': 'passed' if not issues else 'failed',
            'message': '; '.join(issues) if issues else 'Environment setup is correct',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'env_file_exists': os.path.exists('.env'),
                'compose_file_exists': os.path.exists('docker-compose.yml'),
                'issues': issues
            }
        }
    
    def test_docker_security_config(self) -> Dict[str, Any]:
        """Test Docker security configuration"""
        issues = []
        warnings = []
        
        try:
            with open('docker-compose.yml', 'r') as f:
                compose_content = f.read()
                
                # Check for security improvements
                if 'no-new-privileges:true' not in compose_content:
                    warnings.append("no-new-privileges security option not found")
                
                # Check for removed default passwords
                if 'sentinel123' in compose_content or 'redis123' in compose_content:
                    issues.append("Found hardcoded passwords in docker-compose.yml")
                
                # Check for environment variable usage
                if '${POSTGRES_PASSWORD}' not in compose_content:
                    issues.append("POSTGRES_PASSWORD not using environment variable")
                
                # Check for external port exposure (should be commented out)
                if '"5432:5432"' in compose_content and '# ports:' not in compose_content:
                    warnings.append("Database port may be exposed externally")
        
        except Exception as e:
            issues.append(f"Failed to read docker-compose.yml: {e}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else 'Docker security configuration is correct',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_service_startup(self) -> Dict[str, Any]:
        """Test Docker services startup"""
        logger.info("Starting Docker services...")
        
        try:
            # Stop any existing containers
            subprocess.run(['docker', 'compose', 'down'], capture_output=True, text=True)
            
            # Start services
            result = subprocess.run(
                ['docker', 'compose', 'up', '-d'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                return {
                    'status': 'failed',
                    'message': f"Docker compose up failed: {result.stderr}",
                    'timestamp': datetime.now().isoformat(),
                    'details': {
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode
                    }
                }
            
            # Wait for services to be ready
            logger.info("Waiting for services to be ready...")
            time.sleep(30)
            
            # Check container status
            status_result = subprocess.run(
                ['docker', 'compose', 'ps'],
                capture_output=True,
                text=True
            )
            
            return {
                'status': 'passed',
                'message': 'Docker services started successfully',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'container_status': status_result.stdout,
                    'startup_logs': result.stdout
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'message': 'Docker compose startup timed out after 5 minutes',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f"Service startup failed: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def test_service_health(self) -> Dict[str, Any]:
        """Test service health endpoints"""
        service_status = {}
        failed_services = []
        
        # Test NLP service
        try:
            response = requests.get(f"{self.base_url}:{self.services['nlp']}/health", timeout=10)
            service_status['nlp'] = {
                'status_code': response.status_code,
                'accessible': response.status_code == 200
            }
            if response.status_code != 200:
                failed_services.append(f"NLP service (port {self.services['nlp']})")
        except Exception as e:
            service_status['nlp'] = {'error': str(e), 'accessible': False}
            failed_services.append(f"NLP service (port {self.services['nlp']}): {e}")
        
        # Test backend service
        try:
            response = requests.get(f"{self.base_url}:{self.services['backend']}/actuator/health", timeout=10)
            service_status['backend'] = {
                'status_code': response.status_code,
                'accessible': response.status_code == 200
            }
            if response.status_code != 200:
                failed_services.append(f"Backend service (port {self.services['backend']})")
        except Exception as e:
            service_status['backend'] = {'error': str(e), 'accessible': False}
            failed_services.append(f"Backend service (port {self.services['backend']}): {e}")
        
        # Test frontend service
        try:
            response = requests.get(f"{self.base_url}:{self.services['frontend']}", timeout=10)
            service_status['frontend'] = {
                'status_code': response.status_code,
                'accessible': response.status_code == 200
            }
            if response.status_code != 200:
                failed_services.append(f"Frontend service (port {self.services['frontend']})")
        except Exception as e:
            service_status['frontend'] = {'error': str(e), 'accessible': False}
            failed_services.append(f"Frontend service (port {self.services['frontend']}): {e}")
        
        return {
            'status': 'passed' if not failed_services else 'failed',
            'message': 'All services are healthy' if not failed_services else f"Failed services: {', '.join(failed_services)}",
            'timestamp': datetime.now().isoformat(),
            'details': service_status
        }
    
    def test_authentication_security(self) -> Dict[str, Any]:
        """Test JWT authentication and security"""
        issues = []
        
        # Test unauthenticated access (should fail)
        try:
            response = requests.post(
                f"{self.base_url}:{self.services['nlp']}/analyze",
                json={"texts": ["test"]},
                timeout=10
            )
            if response.status_code != 401 and response.status_code != 403:
                issues.append(f"Unauthenticated access allowed (status: {response.status_code})")
        except Exception as e:
            issues.append(f"Failed to test unauthenticated access: {e}")
        
        # Test with invalid token (should fail)
        try:
            headers = {"Authorization": "Bearer invalid-token"}
            response = requests.post(
                f"{self.base_url}:{self.services['nlp']}/analyze",
                json={"texts": ["test"]},
                headers=headers,
                timeout=10
            )
            if response.status_code != 401 and response.status_code != 403:
                issues.append(f"Invalid token access allowed (status: {response.status_code})")
        except Exception as e:
            issues.append(f"Failed to test invalid token access: {e}")
        
        return {
            'status': 'passed' if not issues else 'failed',
            'message': 'Authentication security is working' if not issues else '; '.join(issues),
            'timestamp': datetime.now().isoformat(),
            'details': {'issues': issues}
        }
    
    def test_database_security(self) -> Dict[str, Any]:
        """Test database security configuration"""
        issues = []
        
        # Check if database ports are not exposed externally
        try:
            # Try to connect to PostgreSQL from outside (should fail)
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 5432))
            sock.close()
            
            if result == 0:
                issues.append("PostgreSQL port 5432 is exposed externally")
        except Exception as e:
            # This is expected if port is not exposed
            pass
        
        # Check Docker container security
        try:
            result = subprocess.run(
                ['docker', 'inspect', 'sentinelbert-postgres'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                inspect_data = json.loads(result.stdout)[0]
                
                # Check if running as non-root
                user = inspect_data.get('Config', {}).get('User', '')
                if not user or user == 'root':
                    issues.append("PostgreSQL container may be running as root")
                
                # Check security options
                security_opt = inspect_data.get('HostConfig', {}).get('SecurityOpt', [])
                if 'no-new-privileges:true' not in security_opt:
                    issues.append("no-new-privileges security option not set")
        except Exception as e:
            issues.append(f"Failed to inspect PostgreSQL container: {e}")
        
        return {
            'status': 'passed' if not issues else 'warning',
            'message': 'Database security is configured correctly' if not issues else '; '.join(issues),
            'timestamp': datetime.now().isoformat(),
            'details': {'issues': issues}
        }
    
    def test_insideout_platform(self) -> Dict[str, Any]:
        """Test InsideOut secure platform availability"""
        issues = []
        
        # Check if InsideOut directory exists
        insideout_path = 'INSIDEOUT_SECURE_SKELETON'
        if not os.path.exists(insideout_path):
            issues.append("INSIDEOUT_SECURE_SKELETON directory not found")
        else:
            # Check key components
            required_components = [
                'auth', 'legal', 'evidence', 'analysis', 
                'api', 'monitoring', 'config', 'tests'
            ]
            for component in required_components:
                if not os.path.exists(os.path.join(insideout_path, component)):
                    issues.append(f"Missing InsideOut component: {component}")
            
            # Check Docker compose file
            if not os.path.exists(os.path.join(insideout_path, 'docker-compose.secure.yml')):
                issues.append("Missing docker-compose.secure.yml for InsideOut platform")
        
        return {
            'status': 'passed' if not issues else 'failed',
            'message': 'InsideOut platform is available' if not issues else '; '.join(issues),
            'timestamp': datetime.now().isoformat(),
            'details': {
                'insideout_path_exists': os.path.exists(insideout_path),
                'issues': issues
            }
        }
    
    def cleanup_services(self):
        """Clean up Docker services"""
        try:
            logger.info("Cleaning up Docker services...")
            subprocess.run(['docker', 'compose', 'down'], capture_output=True, text=True)
            logger.info("Services cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to clean up services: {e}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment tests"""
        logger.info("Starting comprehensive deployment test suite...")
        
        # Test sequence
        tests = [
            ('Environment Setup', self.test_environment_setup),
            ('Docker Security Config', self.test_docker_security_config),
            ('Service Startup', self.test_service_startup),
            ('Service Health', self.test_service_health),
            ('Authentication Security', self.test_authentication_security),
            ('Database Security', self.test_database_security),
            ('InsideOut Platform', self.test_insideout_platform)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"DEPLOYMENT TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Overall status
        if failed == 0:
            overall_status = "PASSED" if warnings == 0 else "PASSED_WITH_WARNINGS"
        else:
            overall_status = "FAILED"
        
        self.test_results['overall_status'] = overall_status
        logger.info(f"Overall Status: {overall_status}")
        
        # Save results
        with open('deployment_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: deployment_test_results.json")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = DeploymentTester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_status'] == 'FAILED':
            sys.exit(1)
        elif results['overall_status'] == 'PASSED_WITH_WARNINGS':
            sys.exit(2)  # Warning exit code
        else:
            sys.exit(0)  # Success
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        tester.cleanup_services()
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        tester.cleanup_services()
        sys.exit(1)
    finally:
        tester.cleanup_services()

if __name__ == "__main__":
    main()
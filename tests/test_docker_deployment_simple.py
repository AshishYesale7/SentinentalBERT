#!/usr/bin/env python3
"""
Simple Docker Deployment Test Suite
Tests Docker containers without requiring external port access
"""

import os
import sys
import json
import subprocess
import logging
import redis
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docker_deployment_simple_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleDockerTester:
    """Simple Docker deployment testing"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'total_tests': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
        }
        self.load_env_vars()
        
    def load_env_vars(self):
        """Load environment variables from .env file"""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
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
            return result.get('status') in ['passed', 'warning']
            
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
    
    def test_container_status(self) -> Dict[str, Any]:
        """Test that containers are running"""
        issues = []
        warnings = []
        passed_checks = []
        
        try:
            # Get container status
            result = subprocess.run(['docker', 'compose', 'ps', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                issues.append("Could not get Docker Compose status")
            else:
                containers = json.loads(result.stdout) if result.stdout.strip() else []
                
                required_services = ['postgres', 'redis']
                running_services = []
                
                for container in containers:
                    service_name = container.get('Service', '')
                    state = container.get('State', '')
                    health = container.get('Health', '')
                    
                    if service_name in required_services:
                        if state == 'running':
                            if health in ['healthy', '']:
                                passed_checks.append(f"Service {service_name} is running and healthy")
                                running_services.append(service_name)
                            else:
                                warnings.append(f"Service {service_name} running but health: {health}")
                        else:
                            issues.append(f"Service {service_name} not running (state: {state})")
                
                missing_services = set(required_services) - set(running_services)
                if missing_services:
                    issues.append(f"Missing services: {', '.join(missing_services)}")
                
        except Exception as e:
            issues.append(f"Error checking container status: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Container status: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_database_health(self) -> Dict[str, Any]:
        """Test database health using Docker exec"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Test PostgreSQL health
        try:
            result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                   'pg_isready', '-U', 'sentinelbert', '-d', 'sentinelbert'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                passed_checks.append("PostgreSQL is accepting connections")
                
                # Test basic SQL query
                sql_result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                           'psql', '-U', 'sentinelbert', '-d', 'sentinelbert', 
                                           '-c', 'SELECT version();'], 
                                          capture_output=True, text=True, timeout=10)
                
                if sql_result.returncode == 0:
                    passed_checks.append("PostgreSQL SQL queries working")
                else:
                    warnings.append("PostgreSQL SQL query test failed")
            else:
                issues.append("PostgreSQL is not accepting connections")
                
        except Exception as e:
            issues.append(f"PostgreSQL health check failed: {str(e)}")
        
        # Test Redis health (Redis is exposed on port 6379)
        try:
            redis_config = {
                'host': 'localhost',
                'port': 6379,
                'password': os.getenv('REDIS_PASSWORD', 'SecureRedisPassword123!'),
                'decode_responses': True
            }
            
            r = redis.Redis(**redis_config)
            
            if r.ping():
                passed_checks.append("Redis is accepting connections")
                
                # Test basic operations
                test_key = 'health_check'
                r.set(test_key, 'ok', ex=10)
                if r.get(test_key) == 'ok':
                    passed_checks.append("Redis read/write operations working")
                    r.delete(test_key)
                else:
                    warnings.append("Redis read/write test failed")
            else:
                issues.append("Redis ping failed")
                
        except Exception as e:
            issues.append(f"Redis health check failed: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Database health: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_security_features(self) -> Dict[str, Any]:
        """Test security features in containers"""
        issues = []
        warnings = []
        passed_checks = []
        
        try:
            # Check Docker Compose configuration for security features
            result = subprocess.run(['docker', 'compose', 'config'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                config_content = result.stdout
                
                security_features = [
                    ('no-new-privileges', 'no-new-privileges security option'),
                    ('read_only', 'read-only filesystem option'),
                    ('user:', 'non-root user configuration'),
                    ('${', 'environment variable usage')
                ]
                
                for feature, description in security_features:
                    if feature in config_content:
                        passed_checks.append(f"{description} found")
                    else:
                        warnings.append(f"{description} not found")
            else:
                warnings.append("Could not validate Docker Compose configuration")
            
            # Test container users
            containers = [
                ('postgres', 'sentinelbert-postgres'),
                ('redis', 'sentinelbert-redis')
            ]
            
            for service, container in containers:
                try:
                    result = subprocess.run(['docker', 'exec', container, 'whoami'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        user = result.stdout.strip()
                        if user != 'root':
                            passed_checks.append(f"Container {service} running as non-root: {user}")
                        else:
                            warnings.append(f"Container {service} running as root")
                except:
                    warnings.append(f"Could not check user for {service}")
            
        except Exception as e:
            warnings.append(f"Error checking security features: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Security features: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_environment_configuration(self) -> Dict[str, Any]:
        """Test environment configuration"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check .env file exists and has required variables
        if os.path.exists('.env'):
            passed_checks.append(".env file exists")
            
            with open('.env', 'r') as f:
                env_content = f.read()
                
                required_vars = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'JWT_SECRET']
                for var in required_vars:
                    if f"{var}=" in env_content:
                        passed_checks.append(f"Environment variable {var} configured")
                    else:
                        issues.append(f"Missing environment variable: {var}")
            
            # Check file permissions
            stat_info = os.stat('.env')
            permissions = oct(stat_info.st_mode)[-3:]
            if permissions in ['600', '640', '644']:
                passed_checks.append(f".env file permissions: {permissions}")
            else:
                warnings.append(f".env file permissions ({permissions}) may be insecure")
        else:
            issues.append(".env file not found")
        
        # Check Docker Compose file
        if os.path.exists('docker-compose.yml'):
            passed_checks.append("docker-compose.yml file exists")
        else:
            issues.append("docker-compose.yml file not found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Environment config: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        logger.info("Starting simple Docker deployment test suite...")
        
        tests = [
            ('Container Status', self.test_container_status),
            ('Database Health', self.test_database_health),
            ('Security Features', self.test_security_features),
            ('Environment Configuration', self.test_environment_configuration)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*70}")
        logger.info(f"SIMPLE DOCKER DEPLOYMENT TEST SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        logger.info(f"Success Rate: {((passed + warnings)/total)*100:.1f}%")
        
        # Overall status
        if failed == 0:
            overall_status = "DOCKER_READY" if warnings == 0 else "DOCKER_READY_WITH_WARNINGS"
        else:
            overall_status = "DOCKER_ISSUES"
        
        self.test_results['overall_status'] = overall_status
        logger.info(f"Overall Status: {overall_status}")
        
        # Save results
        with open('docker_deployment_simple_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Results saved to: docker_deployment_simple_results.json")
        return self.test_results

def main():
    """Main test execution"""
    tester = SimpleDockerTester()
    
    try:
        results = tester.run_all_tests()
        
        if results['overall_status'] == 'DOCKER_ISSUES':
            sys.exit(1)
        elif results['overall_status'] == 'DOCKER_READY_WITH_WARNINGS':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
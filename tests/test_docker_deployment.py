#!/usr/bin/env python3
"""
Docker Deployment Test Suite
Tests actual Docker containers and services
"""

import os
import sys
import json
import time
import socket
import subprocess
import logging
import psycopg2
import redis
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docker_deployment_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DockerDeploymentTester:
    """Test actual Docker deployment"""
    
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
        
        # Load environment variables
        self.load_env_vars()
        
    def load_env_vars(self):
        """Load environment variables from .env file"""
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        try:
            # Get Docker info
            docker_info = {}
            try:
                result = subprocess.run(['docker', 'info', '--format', 'json'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    docker_info = json.loads(result.stdout)
            except:
                docker_info = {'error': 'Could not get Docker info'}
            
            # Get running containers
            containers = []
            try:
                result = subprocess.run(['docker', 'compose', 'ps', '--format', 'json'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    containers = json.loads(result.stdout) if result.stdout.strip() else []
            except:
                containers = []
            
            return {
                'os': os.uname().sysname,
                'kernel': os.uname().release,
                'architecture': os.uname().machine,
                'python_version': sys.version,
                'docker_info': docker_info,
                'running_containers': containers,
                'working_directory': os.getcwd()
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
    
    def test_docker_services_status(self) -> Dict[str, Any]:
        """Test Docker services are running and healthy"""
        issues = []
        warnings = []
        passed_checks = []
        
        try:
            # Get container status
            result = subprocess.run(['docker', 'compose', 'ps', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                issues.append("Could not get Docker Compose status")
                return {
                    'status': 'failed',
                    'message': 'Docker Compose not accessible',
                    'timestamp': datetime.now().isoformat()
                }
            
            containers = json.loads(result.stdout) if result.stdout.strip() else []
            
            # Check required services
            required_services = ['postgres', 'redis']
            running_services = []
            
            for container in containers:
                service_name = container.get('Service', '')
                state = container.get('State', '')
                health = container.get('Health', '')
                
                if service_name in required_services:
                    if state == 'running':
                        if health in ['healthy', '']:  # Some services don't have health checks
                            passed_checks.append(f"Service {service_name} is running and healthy")
                            running_services.append(service_name)
                        else:
                            warnings.append(f"Service {service_name} is running but health status: {health}")
                    else:
                        issues.append(f"Service {service_name} is not running (state: {state})")
            
            # Check if all required services are running
            missing_services = set(required_services) - set(running_services)
            if missing_services:
                issues.append(f"Missing services: {', '.join(missing_services)}")
            
            # Test port connectivity
            port_tests = [
                ('PostgreSQL', 5432),
                ('Redis', 6379)
            ]
            
            for service_name, port in port_tests:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(5)
                        result = s.connect_ex(('localhost', port))
                        if result == 0:
                            passed_checks.append(f"{service_name} port {port} is accessible")
                        else:
                            warnings.append(f"{service_name} port {port} is not accessible")
                except Exception as e:
                    warnings.append(f"Error testing {service_name} port {port}: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error checking Docker services: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Docker services: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues,
                'running_services': running_services
            }
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity and basic operations"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Test PostgreSQL
        try:
            postgres_config = {
                'host': 'localhost',
                'port': 5432,
                'database': os.getenv('POSTGRES_DB', 'sentinelbert'),
                'user': os.getenv('POSTGRES_USER', 'sentinelbert'),
                'password': os.getenv('POSTGRES_PASSWORD', 'SecurePassword123!')
            }
            
            conn = psycopg2.connect(**postgres_config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            passed_checks.append(f"PostgreSQL connection successful: {version[:50]}...")
            
            # Test table creation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    test_data VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            # Test insert
            cursor.execute("INSERT INTO test_table (test_data) VALUES (%s);", ('deployment_test',))
            
            # Test select
            cursor.execute("SELECT COUNT(*) FROM test_table WHERE test_data = %s;", ('deployment_test',))
            count = cursor.fetchone()[0]
            
            if count > 0:
                passed_checks.append("PostgreSQL read/write operations successful")
            else:
                warnings.append("PostgreSQL write operation may have failed")
            
            # Cleanup
            cursor.execute("DELETE FROM test_table WHERE test_data = %s;", ('deployment_test',))
            conn.commit()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            issues.append(f"PostgreSQL connectivity test failed: {str(e)}")
        
        # Test Redis
        try:
            redis_config = {
                'host': 'localhost',
                'port': 6379,
                'password': os.getenv('REDIS_PASSWORD', 'SecureRedisPassword123!'),
                'decode_responses': True
            }
            
            r = redis.Redis(**redis_config)
            
            # Test ping
            if r.ping():
                passed_checks.append("Redis connection successful")
            else:
                issues.append("Redis ping failed")
            
            # Test set/get
            test_key = 'deployment_test'
            test_value = 'test_value_123'
            
            r.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            retrieved_value = r.get(test_key)
            
            if retrieved_value == test_value:
                passed_checks.append("Redis read/write operations successful")
            else:
                warnings.append("Redis write/read operation may have failed")
            
            # Cleanup
            r.delete(test_key)
            
        except Exception as e:
            issues.append(f"Redis connectivity test failed: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Database connectivity: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_security_configuration(self) -> Dict[str, Any]:
        """Test security configuration in running containers"""
        issues = []
        warnings = []
        passed_checks = []
        
        try:
            # Check container security settings
            result = subprocess.run(['docker', 'compose', 'config'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                config_content = result.stdout
                
                # Check for security options
                if 'no-new-privileges' in config_content:
                    passed_checks.append("no-new-privileges security option found")
                else:
                    warnings.append("no-new-privileges security option not found")
                
                if 'read_only' in config_content:
                    passed_checks.append("read-only filesystem option found")
                else:
                    warnings.append("read-only filesystem option not found")
                
                # Check environment variable usage
                if '${' in config_content:
                    passed_checks.append("Environment variables are being used")
                else:
                    issues.append("Environment variables not being used properly")
            else:
                warnings.append("Could not validate Docker Compose configuration")
            
            # Check running container security
            containers = ['sentinelbert-postgres', 'sentinelbert-redis']
            for container in containers:
                try:
                    # Check if container is running as non-root (where applicable)
                    result = subprocess.run(['docker', 'exec', container, 'whoami'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        user = result.stdout.strip()
                        if user != 'root':
                            passed_checks.append(f"Container {container} running as non-root user: {user}")
                        else:
                            warnings.append(f"Container {container} running as root (may be expected)")
                except:
                    warnings.append(f"Could not check user for container {container}")
            
        except Exception as e:
            warnings.append(f"Error checking security configuration: {str(e)}")
        
        # Check environment file security
        if os.path.exists('.env'):
            stat_info = os.stat('.env')
            permissions = oct(stat_info.st_mode)[-3:]
            if permissions in ['600', '640']:
                passed_checks.append(f".env file has secure permissions ({permissions})")
            else:
                warnings.append(f".env file permissions ({permissions}) could be more restrictive")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Security configuration: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_resource_usage(self) -> Dict[str, Any]:
        """Test resource usage of running containers"""
        issues = []
        warnings = []
        passed_checks = []
        
        try:
            # Get container stats
            result = subprocess.run(['docker', 'stats', '--no-stream', '--format', 
                                   'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 4:
                            container = parts[0]
                            cpu_perc = parts[1].replace('%', '')
                            mem_usage = parts[2]
                            mem_perc = parts[3].replace('%', '')
                            
                            try:
                                cpu_val = float(cpu_perc)
                                mem_val = float(mem_perc)
                                
                                # Check reasonable resource usage
                                if cpu_val < 50:  # Less than 50% CPU
                                    passed_checks.append(f"Container {container} CPU usage is reasonable: {cpu_perc}%")
                                else:
                                    warnings.append(f"Container {container} high CPU usage: {cpu_perc}%")
                                
                                if mem_val < 80:  # Less than 80% memory
                                    passed_checks.append(f"Container {container} memory usage is reasonable: {mem_perc}%")
                                else:
                                    warnings.append(f"Container {container} high memory usage: {mem_perc}%")
                                
                                passed_checks.append(f"Container {container} resource stats: CPU {cpu_perc}%, Memory {mem_usage}")
                                
                            except ValueError:
                                warnings.append(f"Could not parse resource stats for {container}")
            else:
                warnings.append("Could not get container resource statistics")
                
        except Exception as e:
            warnings.append(f"Error checking resource usage: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Resource usage: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Docker deployment tests"""
        logger.info("Starting Docker deployment test suite...")
        
        # Test sequence
        tests = [
            ('Docker Services Status', self.test_docker_services_status),
            ('Database Connectivity', self.test_database_connectivity),
            ('Security Configuration', self.test_security_configuration),
            ('Resource Usage', self.test_resource_usage)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*70}")
        logger.info(f"DOCKER DEPLOYMENT TEST SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        logger.info(f"Success Rate: {((passed + warnings)/total)*100:.1f}%")
        
        # Overall status
        if failed == 0:
            overall_status = "DOCKER_DEPLOYMENT_READY" if warnings == 0 else "DOCKER_DEPLOYMENT_READY_WITH_WARNINGS"
        else:
            overall_status = "DOCKER_DEPLOYMENT_ISSUES"
        
        self.test_results['overall_status'] = overall_status
        logger.info(f"Overall Status: {overall_status}")
        
        # Save results
        with open('docker_deployment_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: docker_deployment_test_results.json")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = DockerDeploymentTester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_status'] == 'DOCKER_DEPLOYMENT_ISSUES':
            sys.exit(1)
        elif results['overall_status'] == 'DOCKER_DEPLOYMENT_READY_WITH_WARNINGS':
            sys.exit(2)  # Warning exit code
        else:
            sys.exit(0)  # Success
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Final Deployment Validation Test Suite
Comprehensive testing of the InsideOut platform deployment
"""

import os
import sys
import json
import subprocess
import logging
import redis
import platform
import time
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_deployment_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FinalDeploymentValidator:
    """Final deployment validation for InsideOut platform"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'platform': {
                'system': platform.system(),
                'architecture': platform.machine(),
                'python_version': platform.python_version(),
                'kernel': platform.release() if hasattr(platform, 'release') else 'unknown'
            },
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
    
    def test_platform_readiness(self) -> Dict[str, Any]:
        """Test platform readiness for deployment"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check platform compatibility
        system = platform.system()
        if system == 'Linux':
            passed_checks.append("Linux platform - fully supported")
        elif system == 'Darwin':  # macOS
            passed_checks.append("macOS platform - supported with considerations")
            warnings.append("macOS may require additional Docker configuration")
        else:
            warnings.append(f"Platform {system} not officially tested")
        
        # Check Python version
        python_version = platform.python_version()
        major, minor = map(int, python_version.split('.')[:2])
        
        if major == 3 and minor >= 8:
            passed_checks.append(f"Python {python_version} is compatible")
        else:
            issues.append(f"Python {python_version} may not be compatible (requires 3.8+)")
        
        # Check Docker availability
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                docker_version = result.stdout.strip()
                passed_checks.append(f"Docker available: {docker_version}")
            else:
                issues.append("Docker not available")
        except:
            issues.append("Docker not found")
        
        # Check Docker Compose availability
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                compose_version = result.stdout.strip()
                passed_checks.append(f"Docker Compose available: {compose_version}")
            else:
                issues.append("Docker Compose not available")
        except:
            issues.append("Docker Compose not found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Platform readiness: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_core_infrastructure(self) -> Dict[str, Any]:
        """Test core infrastructure components"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check if core services are running
        try:
            result = subprocess.run(['docker', 'compose', 'ps', '--services', '--filter', 'status=running'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                core_services = ['postgres', 'redis']
                for service in core_services:
                    if service in running_services:
                        passed_checks.append(f"Core service {service} is running")
                    else:
                        issues.append(f"Core service {service} is not running")
                
                # Check health status
                health_result = subprocess.run(['docker', 'compose', 'ps', '--format', 'json'], 
                                             capture_output=True, text=True, timeout=10)
                
                if health_result.returncode == 0 and health_result.stdout.strip():
                    for line in health_result.stdout.strip().split('\n'):
                        if line.strip():
                            try:
                                container = json.loads(line)
                                service_name = container.get('Service', '')
                                health = container.get('Health', '')
                                state = container.get('State', '')
                                
                                if service_name in core_services:
                                    if state == 'running':
                                        if health in ['healthy', '']:
                                            passed_checks.append(f"Service {service_name} is healthy")
                                        else:
                                            warnings.append(f"Service {service_name} health: {health}")
                            except json.JSONDecodeError:
                                warnings.append(f"Could not parse container status")
            else:
                issues.append("Could not check Docker services status")
                
        except Exception as e:
            issues.append(f"Error checking infrastructure: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Core infrastructure: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_database_functionality(self) -> Dict[str, Any]:
        """Test database functionality"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Test PostgreSQL
        try:
            # Test connection
            result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                   'pg_isready', '-U', 'sentinel', '-d', 'sentinelbert'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                passed_checks.append("PostgreSQL connection successful")
                
                # Test basic query
                query_result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                             'psql', '-U', 'sentinel', '-d', 'sentinelbert', 
                                             '-c', 'SELECT current_timestamp;'], 
                                            capture_output=True, text=True, timeout=10)
                
                if query_result.returncode == 0:
                    passed_checks.append("PostgreSQL queries working")
                    
                    # Test table operations
                    create_result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                                  'psql', '-U', 'sentinel', '-d', 'sentinelbert', 
                                                  '-c', '''CREATE TABLE IF NOT EXISTS deployment_test (
                                                      id SERIAL PRIMARY KEY,
                                                      test_data VARCHAR(100),
                                                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                                  );'''], 
                                                 capture_output=True, text=True, timeout=10)
                    
                    if create_result.returncode == 0:
                        # Test insert and select
                        insert_result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                                      'psql', '-U', 'sentinel', '-d', 'sentinelbert', 
                                                      '-c', "INSERT INTO deployment_test (test_data) VALUES ('final_validation');"], 
                                                     capture_output=True, text=True, timeout=10)
                        
                        if insert_result.returncode == 0:
                            select_result = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                                          'psql', '-U', 'sentinel', '-d', 'sentinelbert', 
                                                          '-c', "SELECT COUNT(*) FROM deployment_test WHERE test_data = 'final_validation';"], 
                                                         capture_output=True, text=True, timeout=10)
                            
                            if select_result.returncode == 0 and '1' in select_result.stdout:
                                passed_checks.append("PostgreSQL CRUD operations working")
                            else:
                                warnings.append("PostgreSQL CRUD operations may have issues")
                        
                        # Cleanup
                        subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                      'psql', '-U', 'sentinel', '-d', 'sentinelbert', 
                                      '-c', 'DROP TABLE IF EXISTS deployment_test;'], 
                                     capture_output=True, text=True, timeout=10)
                    else:
                        warnings.append("PostgreSQL table operations failed")
                else:
                    warnings.append("PostgreSQL query test failed")
            else:
                issues.append("PostgreSQL connection failed")
                
        except Exception as e:
            issues.append(f"PostgreSQL test failed: {str(e)}")
        
        # Test Redis
        try:
            redis_config = {
                'host': 'localhost',
                'port': 6379,
                'password': os.getenv('REDIS_PASSWORD', 'SecureRedis2024!'),
                'decode_responses': True
            }
            
            r = redis.Redis(**redis_config)
            
            if r.ping():
                passed_checks.append("Redis connection successful")
                
                # Test operations
                test_key = 'final_validation_test'
                test_value = 'deployment_success'
                
                r.set(test_key, test_value, ex=60)
                retrieved_value = r.get(test_key)
                
                if retrieved_value == test_value:
                    passed_checks.append("Redis CRUD operations working")
                    
                    # Test additional operations
                    r.lpush('test_list', 'item1', 'item2')
                    list_length = r.llen('test_list')
                    
                    if list_length == 2:
                        passed_checks.append("Redis list operations working")
                    else:
                        warnings.append("Redis list operations may have issues")
                    
                    # Cleanup
                    r.delete(test_key, 'test_list')
                else:
                    warnings.append("Redis CRUD operations failed")
            else:
                issues.append("Redis ping failed")
                
        except Exception as e:
            issues.append(f"Redis test failed: {str(e)}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Database functionality: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_security_configuration(self) -> Dict[str, Any]:
        """Test security configuration"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check environment variables
        required_env_vars = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'JWT_SECRET']
        for var in required_env_vars:
            value = os.getenv(var)
            if value:
                if len(value) >= 12:  # Minimum password length
                    passed_checks.append(f"Environment variable {var} is set with adequate length")
                else:
                    warnings.append(f"Environment variable {var} may be too short")
            else:
                issues.append(f"Missing environment variable: {var}")
        
        # Check .env file permissions
        if os.path.exists('.env'):
            stat_info = os.stat('.env')
            permissions = oct(stat_info.st_mode)[-3:]
            if permissions in ['600', '640']:
                passed_checks.append(f".env file has secure permissions ({permissions})")
            else:
                warnings.append(f".env file permissions ({permissions}) could be more restrictive")
        else:
            issues.append(".env file not found")
        
        # Check Docker security features
        try:
            result = subprocess.run(['docker', 'compose', 'config'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                config_content = result.stdout
                
                security_features = [
                    ('no-new-privileges', 'no-new-privileges security option'),
                    ('read_only', 'read-only filesystem option'),
                    ('user:', 'non-root user configuration')
                ]
                
                for feature, description in security_features:
                    if feature in config_content:
                        passed_checks.append(f"Security feature: {description}")
                    else:
                        warnings.append(f"Missing security feature: {description}")
            else:
                warnings.append("Could not validate Docker security configuration")
                
        except Exception as e:
            warnings.append(f"Error checking security configuration: {str(e)}")
        
        # Check container users
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
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Security configuration: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_insideout_platform_components(self) -> Dict[str, Any]:
        """Test InsideOut platform components"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check required files exist
        required_files = [
            'docker-compose.yml',
            '.env',
            'requirements.txt'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                passed_checks.append(f"Required file exists: {file_path}")
            else:
                issues.append(f"Missing required file: {file_path}")
        
        # Check critical directories
        required_dirs = [
            'src',
            'database',
            'services'
        ]
        
        for dir_path in required_dirs:
            if os.path.isdir(dir_path):
                passed_checks.append(f"Required directory exists: {dir_path}")
            else:
                warnings.append(f"Directory not found: {dir_path}")
        
        # Check InsideOut specific components
        insideout_components = [
            'src/auth',
            'src/nlp',
            'src/evidence',
            'services/legal_compliance',
            'services/viral_detection'
        ]
        
        for component in insideout_components:
            if os.path.exists(component):
                passed_checks.append(f"InsideOut component exists: {component}")
            else:
                warnings.append(f"InsideOut component not found: {component}")
        
        # Check configuration completeness
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
                
                platform_vars = [
                    'WARRANT_VERIFICATION_ENDPOINT',
                    'EVIDENCE_CHAIN_ENDPOINT',
                    'ENABLE_RATE_LIMITING'
                ]
                
                for var in platform_vars:
                    if f"{var}=" in env_content:
                        passed_checks.append(f"Platform configuration {var} present")
                    else:
                        warnings.append(f"Platform configuration {var} not configured")
        
        # Check if authentication system files exist
        auth_files = [
            'src/auth/auth_service.py',
            'src/auth/jwt_handler.py',
            'src/auth/rbac.py'
        ]
        
        auth_files_exist = sum(1 for f in auth_files if os.path.exists(f))
        if auth_files_exist >= 2:
            passed_checks.append(f"Authentication system files present ({auth_files_exist}/3)")
        else:
            warnings.append(f"Authentication system incomplete ({auth_files_exist}/3 files)")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"InsideOut platform: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_deployment_readiness(self) -> Dict[str, Any]:
        """Test overall deployment readiness"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check if we can start core services
        try:
            # Check current service status
            result = subprocess.run(['docker', 'compose', 'ps', '--services', '--filter', 'status=running'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                if 'postgres' in running_services and 'redis' in running_services:
                    passed_checks.append("Core services are running successfully")
                else:
                    warnings.append("Not all core services are running")
            
            # Test if we can connect to databases
            postgres_test = subprocess.run(['docker', 'compose', 'exec', '-T', 'postgres', 
                                          'pg_isready', '-U', 'sentinel', '-d', 'sentinelbert'], 
                                         capture_output=True, text=True, timeout=5)
            
            if postgres_test.returncode == 0:
                passed_checks.append("PostgreSQL is ready for connections")
            else:
                issues.append("PostgreSQL is not ready")
            
            # Test Redis
            try:
                r = redis.Redis(host='localhost', port=6379, 
                              password=os.getenv('REDIS_PASSWORD', 'SecureRedis2024!'))
                if r.ping():
                    passed_checks.append("Redis is ready for connections")
                else:
                    issues.append("Redis is not responding")
            except:
                issues.append("Redis connection failed")
                
        except Exception as e:
            issues.append(f"Error testing deployment readiness: {str(e)}")
        
        # Check if essential configuration is complete
        config_checks = [
            ('.env', 'Environment configuration file'),
            ('docker-compose.yml', 'Docker Compose configuration'),
            ('requirements.txt', 'Python dependencies')
        ]
        
        for file_path, description in config_checks:
            if os.path.exists(file_path):
                passed_checks.append(f"{description} is present")
            else:
                issues.append(f"Missing {description}")
        
        # Check platform compatibility
        system = platform.system()
        if system in ['Linux', 'Darwin']:
            passed_checks.append(f"Platform {system} is supported")
        else:
            warnings.append(f"Platform {system} compatibility unknown")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Deployment readiness: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment validation tests"""
        logger.info("Starting final deployment validation...")
        logger.info(f"Platform: {self.test_results['platform']['system']} {self.test_results['platform']['architecture']}")
        logger.info(f"Python: {self.test_results['platform']['python_version']}")
        
        tests = [
            ('Platform Readiness', self.test_platform_readiness),
            ('Core Infrastructure', self.test_core_infrastructure),
            ('Database Functionality', self.test_database_functionality),
            ('Security Configuration', self.test_security_configuration),
            ('InsideOut Platform Components', self.test_insideout_platform_components),
            ('Deployment Readiness', self.test_deployment_readiness)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"FINAL DEPLOYMENT VALIDATION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Platform: {self.test_results['platform']['system']} {self.test_results['platform']['architecture']}")
        logger.info(f"Python: {self.test_results['platform']['python_version']}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        
        if total > 0:
            success_rate = ((passed + warnings) / total) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        else:
            success_rate = 0
            logger.info("Success Rate: 0.0%")
        
        # Overall status determination
        if failed == 0:
            if warnings == 0:
                overall_status = "DEPLOYMENT_READY"
            elif warnings <= 3:
                overall_status = "DEPLOYMENT_READY_WITH_MINOR_WARNINGS"
            else:
                overall_status = "DEPLOYMENT_READY_WITH_WARNINGS"
        elif failed <= 2 and passed >= 4:
            overall_status = "DEPLOYMENT_MOSTLY_READY"
        else:
            overall_status = "DEPLOYMENT_NEEDS_ATTENTION"
        
        self.test_results['overall_status'] = overall_status
        self.test_results['success_rate'] = success_rate
        
        logger.info(f"Overall Status: {overall_status}")
        
        # Save results
        with open('final_deployment_validation_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: final_deployment_validation_results.json")
        
        # Generate recommendations
        self.generate_recommendations()
        
        return self.test_results
    
    def generate_recommendations(self):
        """Generate deployment recommendations based on test results"""
        recommendations = []
        
        # Analyze test results
        for test_name, result in self.test_results['tests'].items():
            if result.get('status') == 'failed':
                recommendations.append(f"❌ Fix issues in {test_name}: {result.get('message', '')}")
            elif result.get('status') == 'warning':
                recommendations.append(f"⚠️  Address warnings in {test_name}: {result.get('message', '')}")
        
        # Add general recommendations
        if self.test_results['platform']['system'] == 'Darwin':
            recommendations.append("📝 macOS users: Ensure Docker Desktop is configured with adequate resources")
        
        recommendations.append("🔒 Review security configurations before production deployment")
        recommendations.append("📊 Consider setting up monitoring and logging for production")
        recommendations.append("🧪 Run integration tests with actual data before production use")
        
        logger.info(f"\n{'='*80}")
        logger.info("DEPLOYMENT RECOMMENDATIONS")
        logger.info(f"{'='*80}")
        
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"{i}. {rec}")
        
        self.test_results['recommendations'] = recommendations

def main():
    """Main test execution"""
    validator = FinalDeploymentValidator()
    
    try:
        results = validator.run_all_tests()
        
        # Exit with appropriate code based on status
        status = results['overall_status']
        if status == 'DEPLOYMENT_READY':
            sys.exit(0)
        elif 'WARNING' in status or 'MOSTLY_READY' in status:
            sys.exit(2)  # Warning exit code
        else:
            sys.exit(1)  # Failure exit code
            
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Validation suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
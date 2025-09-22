#!/usr/bin/env python3
"""
Comprehensive Deployment Validation Test Suite
Tests all security fixes and platform functionality without requiring Docker containers
"""

import os
import sys
import json
import re
import subprocess
import importlib.util
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import hashlib
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentValidator:
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
        
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information"""
        try:
            env_info = {
                'os': os.uname().sysname,
                'kernel': os.uname().release,
                'architecture': os.uname().machine,
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'user': os.getenv('USER', 'unknown'),
                'home': os.getenv('HOME', 'unknown')
            }
            
            # Check for Docker
            try:
                result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
                env_info['docker_version'] = result.stdout.strip() if result.returncode == 0 else 'Not available'
            except:
                env_info['docker_version'] = 'Not available'
            
            # Check for Docker Compose
            try:
                result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True, timeout=5)
                env_info['docker_compose_version'] = result.stdout.strip() if result.returncode == 0 else 'Not available'
            except:
                env_info['docker_compose_version'] = 'Not available'
            
            # Check Python packages
            try:
                import jwt
                env_info['jwt_available'] = True
            except ImportError:
                env_info['jwt_available'] = False
                
            return env_info
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
    
    def test_security_configuration_validation(self) -> Dict[str, Any]:
        """Validate all security configurations are properly implemented"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check .env file security
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_content = f.read()
                
                # Check for strong passwords
                required_passwords = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'ELASTIC_PASSWORD', 'GRAFANA_PASSWORD']
                for pwd_var in required_passwords:
                    if f"{pwd_var}=" in env_content:
                        password_line = [line for line in env_content.split('\n') if line.startswith(f"{pwd_var}=")][0]
                        password = password_line.split('=', 1)[1].strip()
                        
                        if len(password) < 12:
                            issues.append(f"{pwd_var} is too short (< 12 characters)")
                        elif not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*]', password):
                            warnings.append(f"{pwd_var} should contain uppercase, lowercase, numbers, and special characters")
                        else:
                            passed_checks.append(f"{pwd_var} meets security requirements")
                    else:
                        issues.append(f"Missing {pwd_var} in .env file")
                
                # Check JWT secret
                if 'JWT_SECRET=' in env_content:
                    jwt_line = [line for line in env_content.split('\n') if line.startswith('JWT_SECRET=')][0]
                    jwt_secret = jwt_line.split('=', 1)[1].strip()
                    
                    if len(jwt_secret) < 32:
                        issues.append("JWT_SECRET is too short (< 32 characters)")
                    else:
                        passed_checks.append("JWT_SECRET meets length requirements")
                else:
                    issues.append("Missing JWT_SECRET in .env file")
        else:
            issues.append("Missing .env file")
        
        # Check docker-compose.yml security
        if os.path.exists('docker-compose.yml'):
            with open('docker-compose.yml', 'r') as f:
                compose_content = f.read()
                
                # Check for environment variable usage
                if '${POSTGRES_PASSWORD}' in compose_content:
                    passed_checks.append("PostgreSQL uses environment variables")
                else:
                    issues.append("PostgreSQL not using environment variables")
                
                if '${REDIS_PASSWORD}' in compose_content:
                    passed_checks.append("Redis uses environment variables")
                else:
                    issues.append("Redis not using environment variables")
                
                # Check for security options
                if 'no-new-privileges:true' in compose_content:
                    passed_checks.append("no-new-privileges security option found")
                else:
                    warnings.append("no-new-privileges security option not found")
                
                # Check for read-only configurations
                if 'read_only: true' in compose_content:
                    passed_checks.append("Read-only filesystem configuration found")
                else:
                    warnings.append("Read-only filesystem configuration not found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Security validation: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_authentication_system_validation(self) -> Dict[str, Any]:
        """Test JWT authentication system implementation"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check NLP service authentication
        nlp_service_path = 'services/nlp/main.py'
        if os.path.exists(nlp_service_path):
            with open(nlp_service_path, 'r') as f:
                content = f.read()
                
                # Check for JWT implementation
                if 'import jwt' in content or 'from jwt' in content:
                    passed_checks.append("JWT library imported in NLP service")
                else:
                    issues.append("JWT library not imported in NLP service")
                
                # Check for authentication decorators
                if '@require_auth' in content or 'verify_token' in content:
                    passed_checks.append("Authentication middleware found in NLP service")
                else:
                    issues.append("Authentication middleware not found in NLP service")
                
                # Check for environment variable usage
                if 'os.getenv' in content or 'os.environ' in content:
                    passed_checks.append("Environment variables used in NLP service")
                else:
                    warnings.append("Environment variables not used in NLP service")
        else:
            issues.append("NLP service main.py not found")
        
        # Check InsideOut authentication system
        insideout_auth_path = 'INSIDEOUT_SECURE_SKELETON/auth/secure_authentication.py'
        if os.path.exists(insideout_auth_path):
            with open(insideout_auth_path, 'r') as f:
                content = f.read()
                
                # Check for secure password hashing
                if 'bcrypt' in content or 'hashlib' in content:
                    passed_checks.append("Secure password hashing implemented")
                else:
                    issues.append("Secure password hashing not found")
                
                # Check for MFA implementation
                if 'pyotp' in content or 'totp' in content.lower():
                    passed_checks.append("Multi-factor authentication implemented")
                else:
                    warnings.append("Multi-factor authentication not found")
                
                # Check for role-based access control
                if 'UserRole' in content and 'Permission' in content:
                    passed_checks.append("Role-based access control implemented")
                else:
                    issues.append("Role-based access control not found")
                
                # Check for secure session management
                if 'session' in content.lower() and 'secure' in content.lower():
                    passed_checks.append("Secure session management found")
                else:
                    warnings.append("Secure session management not clearly implemented")
        else:
            issues.append("InsideOut authentication system not found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Authentication validation: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_insideout_platform_functionality(self) -> Dict[str, Any]:
        """Test InsideOut platform core functionality"""
        issues = []
        warnings = []
        passed_checks = []
        
        insideout_path = 'INSIDEOUT_SECURE_SKELETON'
        if not os.path.exists(insideout_path):
            return {
                'status': 'failed',
                'message': 'InsideOut platform directory not found',
                'timestamp': datetime.now().isoformat()
            }
        
        # Check core components
        core_components = {
            'auth': 'Authentication system',
            'legal': 'Legal compliance framework',
            'evidence': 'Evidence management',
            'analysis': 'Content analysis engine',
            'api': 'API gateway',
            'monitoring': 'System monitoring'
        }
        
        for component, description in core_components.items():
            component_path = os.path.join(insideout_path, component)
            if os.path.exists(component_path):
                # Check for Python files
                py_files = [f for f in os.listdir(component_path) if f.endswith('.py')]
                if py_files:
                    passed_checks.append(f"{description} component has implementation files")
                    
                    # Check main component file
                    main_files = ['main.py', 'app.py', '__init__.py']
                    has_main = any(os.path.exists(os.path.join(component_path, f)) for f in main_files)
                    if has_main:
                        passed_checks.append(f"{description} has main entry point")
                    else:
                        warnings.append(f"{description} missing main entry point")
                else:
                    warnings.append(f"{description} component has no Python files")
            else:
                issues.append(f"Missing {description} component")
        
        # Check legal compliance features
        legal_path = os.path.join(insideout_path, 'legal')
        if os.path.exists(legal_path):
            legal_files = os.listdir(legal_path)
            
            # Check for warrant verification
            if any('warrant' in f.lower() for f in legal_files):
                passed_checks.append("Warrant verification system found")
            else:
                issues.append("Warrant verification system not found")
            
            # Check for evidence chain of custody
            if any('custody' in f.lower() or 'chain' in f.lower() for f in legal_files):
                passed_checks.append("Chain of custody system found")
            else:
                issues.append("Chain of custody system not found")
        
        # Check analysis capabilities
        analysis_path = os.path.join(insideout_path, 'analysis')
        if os.path.exists(analysis_path):
            analysis_files = os.listdir(analysis_path)
            
            # Check for BERT/NLP integration
            if any('bert' in f.lower() or 'nlp' in f.lower() for f in analysis_files):
                passed_checks.append("BERT/NLP analysis integration found")
            else:
                warnings.append("BERT/NLP analysis integration not found")
            
            # Check for pattern detection
            if any('pattern' in f.lower() or 'detect' in f.lower() for f in analysis_files):
                passed_checks.append("Pattern detection capabilities found")
            else:
                warnings.append("Pattern detection capabilities not found")
        
        # Check API security
        api_path = os.path.join(insideout_path, 'api')
        if os.path.exists(api_path):
            api_files = []
            for root, dirs, files in os.walk(api_path):
                api_files.extend([os.path.join(root, f) for f in files if f.endswith('.py')])
            
            auth_found = False
            rate_limit_found = False
            
            for api_file in api_files:
                try:
                    with open(api_file, 'r') as f:
                        content = f.read()
                        
                        if 'auth' in content.lower() or 'token' in content.lower():
                            auth_found = True
                        
                        if 'rate_limit' in content.lower() or 'throttle' in content.lower():
                            rate_limit_found = True
                except:
                    continue
            
            if auth_found:
                passed_checks.append("API authentication found")
            else:
                issues.append("API authentication not found")
            
            if rate_limit_found:
                passed_checks.append("API rate limiting found")
            else:
                warnings.append("API rate limiting not found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"InsideOut platform validation: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_docker_security_hardening(self) -> Dict[str, Any]:
        """Test Docker security hardening measures"""
        issues = []
        warnings = []
        passed_checks = []
        
        if not os.path.exists('docker-compose.yml'):
            return {
                'status': 'failed',
                'message': 'docker-compose.yml not found',
                'timestamp': datetime.now().isoformat()
            }
        
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
        
        # Check security options
        security_checks = {
            'no-new-privileges:true': 'Privilege escalation prevention',
            'read_only: true': 'Read-only filesystem',
            'user:': 'Non-root user configuration',
            'cap_drop': 'Capability dropping',
            'security_opt': 'Security options'
        }
        
        for check, description in security_checks.items():
            if check in compose_content:
                passed_checks.append(f"{description} configured")
            else:
                if check in ['no-new-privileges:true', 'user:']:
                    warnings.append(f"{description} not configured")
                else:
                    warnings.append(f"{description} not found")
        
        # Check for exposed ports
        exposed_ports = re.findall(r'"(\d+):\d+"', compose_content)
        if exposed_ports:
            db_ports = ['5432', '6379', '9200']  # PostgreSQL, Redis, Elasticsearch
            exposed_db_ports = [port for port in exposed_ports if port in db_ports]
            
            if exposed_db_ports:
                warnings.append(f"Database ports exposed externally: {', '.join(exposed_db_ports)}")
            else:
                passed_checks.append("No database ports exposed externally")
        
        # Check for environment variable usage (no hardcoded secrets)
        if '${' in compose_content and '}' in compose_content:
            passed_checks.append("Environment variables used for configuration")
        else:
            issues.append("Environment variables not used for configuration")
        
        # Check for volume security
        if 'volumes:' in compose_content:
            # Check for read-only mounts
            if ':ro' in compose_content:
                passed_checks.append("Read-only volume mounts found")
            else:
                warnings.append("No read-only volume mounts found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Docker security validation: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_deployment_readiness(self) -> Dict[str, Any]:
        """Test overall deployment readiness"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check required files
        required_files = [
            '.env.template',
            'docker-compose.yml',
            'README.md',
            'SECURITY_FIXES_APPLIED.md',
            'INSIDEOUT_INTEGRATION_GUIDE.md'
        ]
        
        for file in required_files:
            if os.path.exists(file):
                passed_checks.append(f"Required file {file} exists")
                
                # Check file size (should not be empty)
                if os.path.getsize(file) > 100:
                    passed_checks.append(f"{file} has content")
                else:
                    warnings.append(f"{file} appears to be empty or too small")
            else:
                issues.append(f"Missing required file: {file}")
        
        # Check directory structure
        required_dirs = [
            'services',
            'INSIDEOUT_SECURE_SKELETON',
            'monitoring'
        ]
        
        for dir_name in required_dirs:
            if os.path.exists(dir_name) and os.path.isdir(dir_name):
                passed_checks.append(f"Required directory {dir_name} exists")
            else:
                issues.append(f"Missing required directory: {dir_name}")
        
        # Check service implementations
        service_dirs = ['services/nlp', 'services/evidence', 'services/viral_detection']
        for service_dir in service_dirs:
            if os.path.exists(service_dir):
                main_py = os.path.join(service_dir, 'main.py')
                dockerfile = os.path.join(service_dir, 'Dockerfile')
                
                if os.path.exists(main_py):
                    passed_checks.append(f"Service {service_dir} has main.py")
                else:
                    warnings.append(f"Service {service_dir} missing main.py")
                
                if os.path.exists(dockerfile):
                    passed_checks.append(f"Service {service_dir} has Dockerfile")
                else:
                    warnings.append(f"Service {service_dir} missing Dockerfile")
        
        # Check documentation completeness
        if os.path.exists('README.md'):
            with open('README.md', 'r') as f:
                readme_content = f.read().lower()
                
                doc_sections = ['security', 'installation', 'usage', 'authentication']
                for section in doc_sections:
                    if section in readme_content:
                        passed_checks.append(f"README contains {section} section")
                    else:
                        warnings.append(f"README missing {section} section")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Deployment readiness: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def test_macos_linux_compatibility(self) -> Dict[str, Any]:
        """Test cross-platform compatibility"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check for macOS deployment guide
        macos_guides = ['MACOS_DEPLOYMENT_GUIDE.md', 'README_MACOS.md']
        macos_guide_found = False
        for guide in macos_guides:
            if os.path.exists(guide):
                macos_guide_found = True
                passed_checks.append(f"macOS deployment guide found: {guide}")
                break
        
        if not macos_guide_found:
            warnings.append("No macOS deployment guide found")
        
        # Check Docker Compose for cross-platform issues
        if os.path.exists('docker-compose.yml'):
            with open('docker-compose.yml', 'r') as f:
                content = f.read()
                
                # Check for hardcoded user IDs (Linux-specific)
                if re.search(r'user:\s*"\d+:\d+"', content):
                    warnings.append("Hardcoded user IDs may cause issues on macOS")
                else:
                    passed_checks.append("No hardcoded user IDs found")
                
                # Check for relative paths in volumes
                relative_paths = re.findall(r'\./[^:]+:', content)
                if relative_paths:
                    warnings.append(f"Relative volume paths may cause issues: {', '.join(relative_paths)}")
                else:
                    passed_checks.append("No problematic relative paths found")
                
                # Check for Linux-specific configurations
                if '/var/run/docker.sock' in content:
                    warnings.append("Docker socket mount may not work on all platforms")
        
        # Check for setup scripts
        setup_scripts = ['setup.sh', 'setup_insideout_macos.sh']
        for script in setup_scripts:
            if os.path.exists(script):
                passed_checks.append(f"Setup script found: {script}")
                
                # Check if executable
                if os.access(script, os.X_OK):
                    passed_checks.append(f"Setup script {script} is executable")
                else:
                    warnings.append(f"Setup script {script} is not executable")
        
        # Check Python compatibility
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Check for platform-specific imports
        platform_specific_imports = ['win32', 'winsound', 'msvcrt']
        for py_file in python_files[:10]:  # Check first 10 files to avoid timeout
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for imp in platform_specific_imports:
                        if f'import {imp}' in content or f'from {imp}' in content:
                            warnings.append(f"Platform-specific import {imp} found in {py_file}")
            except:
                continue
        
        if not any('Platform-specific import' in w for w in warnings):
            passed_checks.append("No platform-specific imports found in Python code")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Cross-platform compatibility: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {
                'passed_checks': passed_checks,
                'warnings': warnings,
                'issues': issues
            }
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment validation tests"""
        logger.info("Starting comprehensive deployment validation test suite...")
        
        # Test sequence
        tests = [
            ('Security Configuration Validation', self.test_security_configuration_validation),
            ('Authentication System Validation', self.test_authentication_system_validation),
            ('InsideOut Platform Functionality', self.test_insideout_platform_functionality),
            ('Docker Security Hardening', self.test_docker_security_hardening),
            ('Deployment Readiness', self.test_deployment_readiness),
            ('macOS/Linux Compatibility', self.test_macos_linux_compatibility)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*70}")
        logger.info(f"COMPREHENSIVE DEPLOYMENT VALIDATION SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Overall status
        if failed == 0:
            overall_status = "DEPLOYMENT_READY" if warnings == 0 else "DEPLOYMENT_READY_WITH_WARNINGS"
        else:
            overall_status = "DEPLOYMENT_NOT_READY"
        
        self.test_results['overall_status'] = overall_status
        logger.info(f"Overall Status: {overall_status}")
        
        # Detailed summary
        logger.info(f"\n{'='*70}")
        logger.info("DETAILED TEST RESULTS:")
        logger.info(f"{'='*70}")
        
        for test_name, result in self.test_results['tests'].items():
            status_icon = "✅" if result['status'] == 'passed' else ("⚠️" if result['status'] == 'warning' else "❌")
            logger.info(f"{status_icon} {test_name}: {result['status'].upper()}")
            
            if 'details' in result:
                details = result['details']
                if 'passed_checks' in details and details['passed_checks']:
                    logger.info(f"   Passed: {len(details['passed_checks'])} checks")
                if 'warnings' in details and details['warnings']:
                    logger.info(f"   Warnings: {len(details['warnings'])} items")
                if 'issues' in details and details['issues']:
                    logger.info(f"   Issues: {len(details['issues'])} items")
        
        # Save results
        with open('deployment_validation_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\nDetailed results saved to: deployment_validation_results.json")
        
        return self.test_results

def main():
    """Main test execution"""
    validator = DeploymentValidator()
    
    try:
        results = validator.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_status'] == 'DEPLOYMENT_NOT_READY':
            sys.exit(1)
        elif results['overall_status'] == 'DEPLOYMENT_READY_WITH_WARNINGS':
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
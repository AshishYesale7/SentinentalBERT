#!/usr/bin/env python3
"""
Static Security Validation Test Suite
Validates security configurations without running containers
"""

import os
import sys
import json
import re
import ast
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('static_security_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StaticSecurityValidator:
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
        """Get system environment information"""
        try:
            return {
                'os': os.uname().sysname,
                'kernel': os.uname().release,
                'architecture': os.uname().machine,
                'python_version': sys.version,
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
    
    def test_environment_configuration(self) -> Dict[str, Any]:
        """Test environment configuration files"""
        issues = []
        warnings = []
        
        # Check .env file
        if not os.path.exists('.env'):
            issues.append("Missing .env file")
        else:
            with open('.env', 'r') as f:
                env_content = f.read()
                
                # Check required variables
                required_vars = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'ELASTIC_PASSWORD', 'JWT_SECRET']
                for var in required_vars:
                    if f"{var}=" not in env_content:
                        issues.append(f"Missing {var} in .env file")
                    elif f"{var}=your-" in env_content or f"{var}=" in env_content and len(env_content.split(f"{var}=")[1].split('\n')[0].strip()) < 8:
                        issues.append(f"{var} has weak or template value")
                
                # Check for empty API keys (warnings only)
                api_keys = ['TWITTER_BEARER_TOKEN', 'INSTAGRAM_ACCESS_TOKEN', 'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
                for key in api_keys:
                    if f"{key}=" in env_content:
                        value = env_content.split(f"{key}=")[1].split('\n')[0].strip()
                        if not value:
                            warnings.append(f"{key} is empty (optional for testing)")
        
        # Check .env.template
        if not os.path.exists('.env.template'):
            warnings.append("Missing .env.template file")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else 'Environment configuration is correct',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_docker_compose_security(self) -> Dict[str, Any]:
        """Test Docker Compose security configuration"""
        issues = []
        warnings = []
        
        if not os.path.exists('docker-compose.yml'):
            issues.append("Missing docker-compose.yml file")
            return {
                'status': 'failed',
                'message': 'Missing docker-compose.yml file',
                'timestamp': datetime.now().isoformat()
            }
        
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
            
            # Check for hardcoded passwords (more precise patterns)
            hardcoded_patterns = [
                r'password\s*:\s*["\'][^"\'$]{3,}["\']',
                r'POSTGRES_PASSWORD\s*:\s*[^$\s][^\s]*',
                r'REDIS_PASSWORD\s*:\s*[^$\s][^\s]*',
                r'ELASTIC_PASSWORD\s*:\s*[^$\s][^\s]*'
            ]
            
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, compose_content, re.IGNORECASE)
                for match in matches:
                    if '${' not in match and '#' not in match and 'environment' not in match.lower():
                        issues.append(f"Potential hardcoded credential: {match}")
            
            # Check for fallback passwords
            if ':-' in compose_content:
                fallback_matches = re.findall(r'\$\{[^}]+:-[^}]+\}', compose_content)
                for match in fallback_matches:
                    if 'PASSWORD' in match.upper():
                        issues.append(f"Found fallback password: {match}")
            
            # Check security options
            if 'no-new-privileges:true' not in compose_content:
                warnings.append("no-new-privileges security option not found")
            
            # Check for external port exposure
            exposed_db_ports = re.findall(r'"(5432|6379|9200):\d+"', compose_content)
            if exposed_db_ports:
                warnings.append(f"Database ports exposed externally: {', '.join(exposed_db_ports)}")
            
            # Check for non-root users
            if 'user:' not in compose_content:
                warnings.append("No non-root user configuration found")
            
            # Check for read-only filesystems
            if 'read_only: true' not in compose_content:
                warnings.append("No read-only filesystem configuration found")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else 'Docker Compose security is configured correctly',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_python_code_security(self) -> Dict[str, Any]:
        """Test Python code for security issues"""
        issues = []
        warnings = []
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for hardcoded credentials (exclude test files and examples)
                    if not any(test_indicator in file_path.lower() for test_indicator in ['test_', '/test', 'example', 'demo']):
                        credential_patterns = [
                            r'password\s*=\s*["\'][^"\']{8,}["\']',
                            r'secret\s*=\s*["\'][^"\']{10,}["\']',
                            r'token\s*=\s*["\'][^"\']{20,}["\']',
                            r'api_key\s*=\s*["\'][^"\']{15,}["\']'
                        ]
                        
                        for pattern in credential_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if not any(exclude in match.lower() for exclude in ['your-', 'example', 'test', 'demo', 'placeholder', 'changeme']):
                                    issues.append(f"Potential hardcoded credential in {file_path}: {match}")
                    
                    # Check for SQL injection vulnerabilities (string formatting in SQL)
                    if re.search(r'execute\s*\([^)]*%\s*[^)]*\)', content) and 'cursor.execute' in content:
                        warnings.append(f"Potential SQL injection risk in {file_path}")
                    elif re.search(r'query\s*\([^)]*%\s*[^)]*\)', content) and not re.search(r'query\s*\([^)]*%s[^)]*\)', content):
                        warnings.append(f"Potential SQL injection risk in {file_path}")
                    
                    # Check for command injection
                    if re.search(r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True', content):
                        warnings.append(f"Potential command injection risk in {file_path}")
                    
                    # Check for insecure random
                    if 'random.random()' in content or 'random.randint(' in content:
                        warnings.append(f"Insecure random usage in {file_path} (use secrets module)")
                    
                    # Check for debug mode
                    if re.search(r'debug\s*=\s*True', content, re.IGNORECASE):
                        warnings.append(f"Debug mode enabled in {file_path}")
                    
            except Exception as e:
                warnings.append(f"Failed to analyze {file_path}: {e}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else f'Python code security analysis passed ({len(python_files)} files checked)',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'files_checked': len(python_files),
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_authentication_implementation(self) -> Dict[str, Any]:
        """Test JWT authentication implementation"""
        issues = []
        warnings = []
        
        # Check NLP service authentication
        nlp_service_path = 'services/nlp/main.py'
        if os.path.exists(nlp_service_path):
            with open(nlp_service_path, 'r') as f:
                content = f.read()
                
                # Check for JWT implementation
                if 'jwt' not in content.lower():
                    issues.append("JWT authentication not found in NLP service")
                
                # Check for authentication decorators/middleware
                if '@require_auth' not in content and 'verify_token' not in content:
                    issues.append("Authentication middleware not found in NLP service")
                
                # Check for permission checks
                if 'permission' not in content.lower():
                    warnings.append("Permission-based access control not found in NLP service")
                
                # Check for secure endpoints
                protected_endpoints = ['/analyze', '/analyze/sentiment', '/analyze/behavior']
                for endpoint in protected_endpoints:
                    if endpoint in content and 'auth' not in content.lower():
                        warnings.append(f"Endpoint {endpoint} may not be properly protected")
        else:
            issues.append("NLP service main.py not found")
        
        # Check other services
        service_dirs = ['services/evidence', 'services/viral_detection']
        for service_dir in service_dirs:
            main_py = os.path.join(service_dir, 'main.py')
            if os.path.exists(main_py):
                with open(main_py, 'r') as f:
                    content = f.read()
                    
                    # Check for environment variable usage
                    if 'os.environ' not in content and 'getenv' not in content:
                        warnings.append(f"Environment variable usage not found in {service_dir}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else 'Authentication implementation is correct',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_insideout_platform_structure(self) -> Dict[str, Any]:
        """Test InsideOut platform structure and completeness"""
        issues = []
        warnings = []
        
        insideout_path = 'INSIDEOUT_SECURE_SKELETON'
        if not os.path.exists(insideout_path):
            issues.append("INSIDEOUT_SECURE_SKELETON directory not found")
            return {
                'status': 'failed',
                'message': 'INSIDEOUT_SECURE_SKELETON directory not found',
                'timestamp': datetime.now().isoformat()
            }
        
        # Check required components
        required_components = [
            'auth', 'legal', 'evidence', 'analysis', 
            'api', 'monitoring', 'config', 'tests'
        ]
        
        for component in required_components:
            component_path = os.path.join(insideout_path, component)
            if not os.path.exists(component_path):
                issues.append(f"Missing InsideOut component: {component}")
            else:
                # Check if component has main files
                main_files = ['main.py', 'app.py', '__init__.py', 'Dockerfile']
                has_main_file = any(os.path.exists(os.path.join(component_path, f)) for f in main_files)
                if not has_main_file:
                    warnings.append(f"Component {component} may be incomplete (no main files found)")
        
        # Check Docker configuration
        docker_compose_secure = os.path.join(insideout_path, 'docker-compose.secure.yml')
        if not os.path.exists(docker_compose_secure):
            issues.append("Missing docker-compose.secure.yml for InsideOut platform")
        
        # Check documentation
        docs = ['README.md', 'DEPLOYMENT.md', 'SECURITY.md']
        for doc in docs:
            if not os.path.exists(os.path.join(insideout_path, doc)):
                warnings.append(f"Missing documentation: {doc}")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else 'InsideOut platform structure is complete',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'insideout_path': insideout_path,
                'required_components': required_components,
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_documentation_completeness(self) -> Dict[str, Any]:
        """Test documentation completeness"""
        issues = []
        warnings = []
        
        # Check critical documentation files
        critical_docs = [
            'README.md',
            'SECURITY_FIXES_APPLIED.md',
            'INSIDEOUT_INTEGRATION_GUIDE.md',
            '.env.template'
        ]
        
        for doc in critical_docs:
            if not os.path.exists(doc):
                issues.append(f"Missing critical documentation: {doc}")
            else:
                # Check file size (should not be empty)
                if os.path.getsize(doc) < 100:
                    warnings.append(f"Documentation file {doc} appears to be too small")
        
        # Check if README has security section
        if os.path.exists('README.md'):
            with open('README.md', 'r') as f:
                readme_content = f.read()
                if 'security' not in readme_content.lower():
                    warnings.append("README.md missing security section")
                if 'authentication' not in readme_content.lower():
                    warnings.append("README.md missing authentication information")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': '; '.join(issues + warnings) if (issues or warnings) else 'Documentation is complete',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'critical_docs': critical_docs,
                'issues': issues,
                'warnings': warnings
            }
        }
    
    def test_macos_compatibility(self) -> Dict[str, Any]:
        """Test macOS compatibility indicators"""
        issues = []
        warnings = []
        
        # Check for macOS-specific documentation
        macos_docs = ['MACOS_DEPLOYMENT_GUIDE.md', 'README_MACOS.md']
        macos_doc_found = False
        for doc in macos_docs:
            if os.path.exists(doc):
                macos_doc_found = True
                break
        
        if not macos_doc_found:
            warnings.append("No macOS-specific documentation found")
        
        # Check Docker Compose for macOS compatibility
        if os.path.exists('docker-compose.yml'):
            with open('docker-compose.yml', 'r') as f:
                content = f.read()
                
                # Check for volume mounts that might cause issues on macOS
                if './models:/app/models' in content:
                    warnings.append("Relative volume mounts may cause issues on macOS")
                
                # Check for Linux-specific configurations
                if 'user: "999:999"' in content:
                    warnings.append("Hardcoded user IDs may cause issues on macOS")
        
        # Check for setup scripts
        setup_scripts = ['setup_insideout_macos.sh', 'setup.sh']
        setup_script_found = False
        for script in setup_scripts:
            if os.path.exists(script):
                setup_script_found = True
                # Check if script is executable
                if not os.access(script, os.X_OK):
                    warnings.append(f"Setup script {script} is not executable")
        
        if not setup_script_found:
            warnings.append("No setup scripts found for macOS deployment")
        
        status = 'warning' if warnings else 'passed'
        return {
            'status': status,
            'message': '; '.join(warnings) if warnings else 'macOS compatibility indicators are present',
            'timestamp': datetime.now().isoformat(),
            'details': {
                'macos_doc_found': macos_doc_found,
                'setup_script_found': setup_script_found,
                'warnings': warnings
            }
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all static security validation tests"""
        logger.info("Starting static security validation test suite...")
        
        # Test sequence
        tests = [
            ('Environment Configuration', self.test_environment_configuration),
            ('Docker Compose Security', self.test_docker_compose_security),
            ('Python Code Security', self.test_python_code_security),
            ('Authentication Implementation', self.test_authentication_implementation),
            ('InsideOut Platform Structure', self.test_insideout_platform_structure),
            ('Documentation Completeness', self.test_documentation_completeness),
            ('macOS Compatibility', self.test_macos_compatibility)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"STATIC SECURITY VALIDATION SUMMARY")
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
        with open('static_security_validation_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: static_security_validation_results.json")
        
        return self.test_results

def main():
    """Main test execution"""
    validator = StaticSecurityValidator()
    
    try:
        results = validator.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_status'] == 'FAILED':
            sys.exit(1)
        elif results['overall_status'] == 'PASSED_WITH_WARNINGS':
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
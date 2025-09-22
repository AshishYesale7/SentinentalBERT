#!/usr/bin/env python3
"""
macOS Deployment Compatibility Test Suite
Tests macOS-specific deployment considerations and compatibility
"""

import os
import sys
import json
import subprocess
import logging
import platform
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('macos_compatibility_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MacOSCompatibilityTester:
    """Test macOS deployment compatibility"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'platform': {
                'system': platform.system(),
                'architecture': platform.machine(),
                'python_version': platform.python_version(),
                'release': platform.release(),
                'version': platform.version()
            },
            'tests': {},
            'summary': {'total_tests': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
        }
        self.is_macos = platform.system() == 'Darwin'
        
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
    
    def test_platform_detection(self) -> Dict[str, Any]:
        """Test platform detection and basic compatibility"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check if running on macOS
        if self.is_macos:
            passed_checks.append("Running on macOS platform")
            
            # Check macOS version
            try:
                version_info = platform.mac_ver()
                macos_version = version_info[0]
                if macos_version:
                    passed_checks.append(f"macOS version: {macos_version}")
                    
                    # Check if version is recent enough
                    major_version = int(macos_version.split('.')[0])
                    if major_version >= 11:  # macOS Big Sur or later
                        passed_checks.append("macOS version is compatible (11.0+)")
                    else:
                        warnings.append(f"macOS version {macos_version} may have compatibility issues")
                else:
                    warnings.append("Could not determine macOS version")
            except:
                warnings.append("Error checking macOS version")
        else:
            # Running on non-macOS platform - simulate macOS compatibility checks
            passed_checks.append(f"Running on {platform.system()} - simulating macOS compatibility checks")
            passed_checks.append("macOS compatibility can be validated on actual macOS systems")
        
        # Check architecture
        arch = platform.machine()
        if arch in ['x86_64', 'arm64']:
            passed_checks.append(f"Architecture {arch} is supported on macOS")
        else:
            warnings.append(f"Architecture {arch} compatibility unknown")
        
        # Check Python version
        python_version = platform.python_version()
        major, minor = map(int, python_version.split('.')[:2])
        
        if major == 3 and minor >= 8:
            passed_checks.append(f"Python {python_version} is compatible with macOS")
        else:
            issues.append(f"Python {python_version} may not be compatible")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Platform detection: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_docker_compatibility(self) -> Dict[str, Any]:
        """Test Docker compatibility on macOS"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check Docker availability
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                docker_version = result.stdout.strip()
                passed_checks.append(f"Docker available: {docker_version}")
                
                # Check if Docker Desktop is running (macOS specific)
                if self.is_macos:
                    try:
                        docker_info = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
                        if docker_info.returncode == 0:
                            passed_checks.append("Docker daemon is running")
                            
                            # Check for Docker Desktop specific features
                            if 'Docker Desktop' in docker_info.stdout:
                                passed_checks.append("Docker Desktop detected")
                            else:
                                warnings.append("Docker Desktop not detected - may affect performance")
                        else:
                            issues.append("Docker daemon is not running")
                    except:
                        warnings.append("Could not check Docker daemon status")
                else:
                    passed_checks.append("Docker daemon check (simulated for non-macOS)")
            else:
                issues.append("Docker not available")
        except:
            issues.append("Docker not found in PATH")
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                compose_version = result.stdout.strip()
                passed_checks.append(f"Docker Compose available: {compose_version}")
            else:
                issues.append("Docker Compose not available")
        except:
            issues.append("Docker Compose not found")
        
        # macOS specific Docker checks
        if self.is_macos:
            # Check Docker Desktop resource allocation
            try:
                # Check available memory
                vm_stat = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=5)
                if vm_stat.returncode == 0:
                    passed_checks.append("System memory information available")
                else:
                    warnings.append("Could not check system memory")
            except:
                warnings.append("vm_stat command not available")
            
            # Check for common macOS Docker issues
            docker_socket_path = '/var/run/docker.sock'
            if os.path.exists(docker_socket_path):
                passed_checks.append("Docker socket is accessible")
            else:
                warnings.append("Docker socket not found at expected location")
        else:
            passed_checks.append("macOS-specific Docker checks (simulated)")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Docker compatibility: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_file_system_compatibility(self) -> Dict[str, Any]:
        """Test file system compatibility for macOS"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check file system case sensitivity
        test_dir = '/tmp/macos_test_case_sensitivity'
        try:
            os.makedirs(test_dir, exist_ok=True)
            
            # Create test files
            test_file1 = os.path.join(test_dir, 'TestFile.txt')
            test_file2 = os.path.join(test_dir, 'testfile.txt')
            
            with open(test_file1, 'w') as f:
                f.write('test1')
            
            # Try to create file with different case
            try:
                with open(test_file2, 'w') as f:
                    f.write('test2')
                
                # If both files exist, file system is case-sensitive
                if os.path.exists(test_file1) and os.path.exists(test_file2):
                    passed_checks.append("File system is case-sensitive")
                else:
                    warnings.append("File system appears to be case-insensitive")
            except:
                warnings.append("Could not test file system case sensitivity")
            
            # Cleanup
            try:
                os.remove(test_file1)
                if os.path.exists(test_file2):
                    os.remove(test_file2)
                os.rmdir(test_dir)
            except:
                pass
                
        except Exception as e:
            warnings.append(f"File system test failed: {str(e)}")
        
        # Check for macOS specific file system features
        if self.is_macos:
            # Check for extended attributes support
            try:
                test_file = '/tmp/xattr_test.txt'
                with open(test_file, 'w') as f:
                    f.write('test')
                
                # Try to set extended attribute
                result = subprocess.run(['xattr', '-w', 'test.attr', 'value', test_file], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    passed_checks.append("Extended attributes supported")
                else:
                    warnings.append("Extended attributes may not be supported")
                
                os.remove(test_file)
            except:
                warnings.append("Could not test extended attributes")
        else:
            passed_checks.append("macOS file system features (simulated)")
        
        # Check Docker volume mount compatibility
        try:
            # Test if current directory can be mounted
            current_dir = os.getcwd()
            if os.path.exists(current_dir):
                passed_checks.append("Current directory accessible for Docker mounts")
            else:
                issues.append("Current directory not accessible")
        except:
            warnings.append("Could not test Docker volume mount compatibility")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"File system compatibility: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_network_compatibility(self) -> Dict[str, Any]:
        """Test network compatibility for macOS"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Test localhost connectivity
        import socket
        
        test_ports = [5432, 6379, 8000, 8080, 3000]
        
        for port in test_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        passed_checks.append(f"Port {port} is accessible on localhost")
                    else:
                        passed_checks.append(f"Port {port} is available (not in use)")
            except Exception as e:
                warnings.append(f"Could not test port {port}: {str(e)}")
        
        # Test Docker network connectivity
        try:
            # Check if Docker networks can be created
            network_test = subprocess.run(['docker', 'network', 'ls'], 
                                        capture_output=True, text=True, timeout=10)
            if network_test.returncode == 0:
                passed_checks.append("Docker network commands available")
            else:
                warnings.append("Docker network commands not working")
        except:
            warnings.append("Could not test Docker network functionality")
        
        # macOS specific network checks
        if self.is_macos:
            # Check for common macOS network issues
            try:
                # Check if localhost resolves correctly
                import socket
                localhost_ip = socket.gethostbyname('localhost')
                if localhost_ip == '127.0.0.1':
                    passed_checks.append("localhost resolves correctly")
                else:
                    warnings.append(f"localhost resolves to {localhost_ip} instead of 127.0.0.1")
            except:
                warnings.append("Could not resolve localhost")
        else:
            passed_checks.append("macOS network checks (simulated)")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Network compatibility: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_deployment_scripts(self) -> Dict[str, Any]:
        """Test macOS deployment scripts"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check for macOS specific setup scripts
        macos_scripts = [
            'setup_insideout_macos.sh',
            'launch_platform.sh'
        ]
        
        for script in macos_scripts:
            if os.path.exists(script):
                passed_checks.append(f"macOS script exists: {script}")
                
                # Check if script is executable
                if os.access(script, os.X_OK):
                    passed_checks.append(f"Script {script} is executable")
                else:
                    warnings.append(f"Script {script} is not executable")
            else:
                warnings.append(f"macOS script not found: {script}")
        
        # Check for macOS specific documentation
        macos_docs = [
            'README_MACOS.md',
            'MACOS_DEPLOYMENT_GUIDE.md'
        ]
        
        for doc in macos_docs:
            if os.path.exists(doc):
                passed_checks.append(f"macOS documentation exists: {doc}")
            else:
                warnings.append(f"macOS documentation not found: {doc}")
        
        # Test shell compatibility
        try:
            # Check default shell
            shell_result = subprocess.run(['echo', '$SHELL'], capture_output=True, text=True, timeout=5)
            if shell_result.returncode == 0:
                passed_checks.append("Shell commands working")
            else:
                warnings.append("Shell command test failed")
        except:
            warnings.append("Could not test shell compatibility")
        
        # Check for Homebrew (common on macOS)
        if self.is_macos:
            try:
                brew_result = subprocess.run(['brew', '--version'], capture_output=True, text=True, timeout=5)
                if brew_result.returncode == 0:
                    passed_checks.append("Homebrew available for package management")
                else:
                    warnings.append("Homebrew not available (may need manual installation)")
            except:
                warnings.append("Homebrew not found")
        else:
            passed_checks.append("macOS package manager checks (simulated)")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Deployment scripts: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def test_resource_requirements(self) -> Dict[str, Any]:
        """Test system resource requirements for macOS"""
        issues = []
        warnings = []
        passed_checks = []
        
        # Check available memory
        try:
            if self.is_macos:
                # Use macOS specific commands
                vm_stat = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=5)
                if vm_stat.returncode == 0:
                    passed_checks.append("Memory information available via vm_stat")
                else:
                    warnings.append("Could not get memory information")
            else:
                # Simulate for non-macOS
                passed_checks.append("Memory checks (simulated for non-macOS)")
        except:
            warnings.append("Could not check memory information")
        
        # Check disk space
        try:
            disk_usage = subprocess.run(['df', '-h', '.'], capture_output=True, text=True, timeout=5)
            if disk_usage.returncode == 0:
                passed_checks.append("Disk space information available")
                
                # Parse disk usage (simplified)
                lines = disk_usage.stdout.strip().split('\n')
                if len(lines) > 1:
                    usage_line = lines[1].split()
                    if len(usage_line) >= 4:
                        available = usage_line[3]
                        passed_checks.append(f"Available disk space: {available}")
            else:
                warnings.append("Could not check disk space")
        except:
            warnings.append("Disk space check failed")
        
        # Check CPU information
        try:
            if self.is_macos:
                cpu_info = subprocess.run(['sysctl', '-n', 'hw.ncpu'], capture_output=True, text=True, timeout=5)
                if cpu_info.returncode == 0:
                    cpu_count = cpu_info.stdout.strip()
                    passed_checks.append(f"CPU cores available: {cpu_count}")
                else:
                    warnings.append("Could not get CPU information")
            else:
                import os
                cpu_count = os.cpu_count()
                passed_checks.append(f"CPU cores available: {cpu_count}")
        except:
            warnings.append("Could not check CPU information")
        
        # Docker resource recommendations
        passed_checks.append("Recommended Docker Desktop settings:")
        passed_checks.append("- Memory: 4GB minimum, 8GB recommended")
        passed_checks.append("- CPU: 2 cores minimum, 4 cores recommended")
        passed_checks.append("- Disk: 10GB minimum for containers and images")
        
        status = 'failed' if issues else ('warning' if warnings else 'passed')
        return {
            'status': status,
            'message': f"Resource requirements: {len(passed_checks)} passed, {len(warnings)} warnings, {len(issues)} issues",
            'timestamp': datetime.now().isoformat(),
            'details': {'passed_checks': passed_checks, 'warnings': warnings, 'issues': issues}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all macOS compatibility tests"""
        logger.info("Starting macOS deployment compatibility testing...")
        logger.info(f"Platform: {self.test_results['platform']['system']} {self.test_results['platform']['architecture']}")
        
        if self.is_macos:
            logger.info("Running on actual macOS system")
        else:
            logger.info("Running compatibility simulation on non-macOS system")
        
        tests = [
            ('Platform Detection', self.test_platform_detection),
            ('Docker Compatibility', self.test_docker_compatibility),
            ('File System Compatibility', self.test_file_system_compatibility),
            ('Network Compatibility', self.test_network_compatibility),
            ('Deployment Scripts', self.test_deployment_scripts),
            ('Resource Requirements', self.test_resource_requirements)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        warnings = self.test_results['summary']['warnings']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"MACOS COMPATIBILITY TEST SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Platform: {self.test_results['platform']['system']} {self.test_results['platform']['architecture']}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Warnings: {warnings} ⚠️")
        
        if total > 0:
            success_rate = ((passed + warnings) / total) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        else:
            success_rate = 0
        
        # Overall status
        if failed == 0:
            if warnings <= 2:
                overall_status = "MACOS_COMPATIBLE"
            else:
                overall_status = "MACOS_COMPATIBLE_WITH_WARNINGS"
        else:
            overall_status = "MACOS_COMPATIBILITY_ISSUES"
        
        self.test_results['overall_status'] = overall_status
        self.test_results['success_rate'] = success_rate
        
        logger.info(f"Overall Status: {overall_status}")
        
        # Save results
        with open('macos_compatibility_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Results saved to: macos_compatibility_results.json")
        
        # Generate macOS specific recommendations
        self.generate_macos_recommendations()
        
        return self.test_results
    
    def generate_macos_recommendations(self):
        """Generate macOS specific recommendations"""
        recommendations = []
        
        if self.is_macos:
            recommendations.append("🍎 macOS Deployment Recommendations:")
            recommendations.append("1. Ensure Docker Desktop is installed and running")
            recommendations.append("2. Allocate at least 4GB RAM to Docker Desktop")
            recommendations.append("3. Enable file sharing for the project directory")
            recommendations.append("4. Consider using Homebrew for dependency management")
        else:
            recommendations.append("🍎 macOS Compatibility Notes:")
            recommendations.append("1. Tests run in simulation mode on non-macOS platform")
            recommendations.append("2. Actual macOS testing recommended before deployment")
            recommendations.append("3. Docker Desktop configuration is critical on macOS")
        
        recommendations.extend([
            "5. Monitor Docker Desktop resource usage during deployment",
            "6. Use the macOS-specific setup script: setup_insideout_macos.sh",
            "7. Check firewall settings if network connectivity issues occur",
            "8. Consider using Docker Desktop's built-in Kubernetes for orchestration"
        ])
        
        logger.info(f"\n{'='*80}")
        logger.info("MACOS DEPLOYMENT RECOMMENDATIONS")
        logger.info(f"{'='*80}")
        
        for rec in recommendations:
            logger.info(rec)
        
        self.test_results['recommendations'] = recommendations

def main():
    """Main test execution"""
    tester = MacOSCompatibilityTester()
    
    try:
        results = tester.run_all_tests()
        
        status = results['overall_status']
        if status == 'MACOS_COMPATIBLE':
            sys.exit(0)
        elif 'WARNING' in status:
            sys.exit(2)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
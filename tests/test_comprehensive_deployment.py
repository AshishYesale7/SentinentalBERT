#!/usr/bin/env python3
"""
Comprehensive Deployment Test Suite for SentinentalBERT Platform
Tests all major components and functionality
"""

import os
import sys
import time
import json
import requests
import subprocess
import jwt
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ComprehensiveDeploymentTest:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.results = []
        self.load_environment()
        
    def load_environment(self):
        """Load environment variables"""
        env_path = os.path.join(self.base_dir, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            self.jwt_secret = os.getenv('JWT_SECRET')
            print(f"✅ Environment loaded from {env_path}")
        else:
            print(f"❌ Environment file not found at {env_path}")
            self.jwt_secret = 'insecure-default-change-in-production'
    
    def generate_jwt_token(self, permissions=None):
        """Generate JWT token for testing"""
        if permissions is None:
            permissions = ['nlp:analyze', 'nlp:sentiment', 'admin:models']
        
        payload = {
            'officer_id': 'test_officer_comprehensive',
            'role': 'admin',
            'permissions': permissions,
            'exp': int(time.time()) + 3600
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def test_environment_configuration(self):
        """Test environment configuration"""
        print("\n🔧 Testing Environment Configuration...")
        
        required_vars = [
            'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD',
            'REDIS_PASSWORD', 'JWT_SECRET', 'ELASTICSEARCH_PASSWORD',
            'GRAFANA_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.results.append({
                'test': 'Environment Configuration',
                'status': 'FAIL',
                'message': f'Missing variables: {missing_vars}'
            })
            return False
        
        # Check JWT secret strength
        jwt_secret = os.getenv('JWT_SECRET')
        if len(jwt_secret) < 32:
            self.results.append({
                'test': 'Environment Configuration',
                'status': 'WARN',
                'message': 'JWT secret should be at least 32 characters'
            })
        else:
            self.results.append({
                'test': 'Environment Configuration',
                'status': 'PASS',
                'message': 'All environment variables configured'
            })
            return True
    
    def test_file_structure(self):
        """Test project file structure"""
        print("\n📁 Testing File Structure...")
        
        required_files = [
            '.env',
            'docker-compose.yml',
            'services/nlp/main.py',
            'services/nlp/main_simple.py',
            'services/nlp/requirements.txt',
            'DEPLOYMENT_GUIDE.md',
            'REMAINING_TASKS.md'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(self.base_dir, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.results.append({
                'test': 'File Structure',
                'status': 'FAIL',
                'message': f'Missing files: {missing_files}'
            })
            return False
        else:
            self.results.append({
                'test': 'File Structure',
                'status': 'PASS',
                'message': 'All required files present'
            })
            return True
    
    def test_nlp_service_health(self):
        """Test NLP service health endpoint"""
        print("\n🏥 Testing NLP Service Health...")
        
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get('status') == 'healthy':
                    self.results.append({
                        'test': 'NLP Service Health',
                        'status': 'PASS',
                        'message': f'Service healthy: {health_data}'
                    })
                    return True
                else:
                    self.results.append({
                        'test': 'NLP Service Health',
                        'status': 'FAIL',
                        'message': f'Service unhealthy: {health_data}'
                    })
                    return False
            else:
                self.results.append({
                    'test': 'NLP Service Health',
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}: {response.text}'
                })
                return False
        except requests.exceptions.RequestException as e:
            self.results.append({
                'test': 'NLP Service Health',
                'status': 'FAIL',
                'message': f'Connection error: {str(e)}'
            })
            return False
    
    def test_jwt_authentication(self):
        """Test JWT authentication"""
        print("\n🔐 Testing JWT Authentication...")
        
        # Test without token
        try:
            response = requests.post('http://localhost:8000/analyze', 
                                   json={'texts': ['test']}, timeout=5)
            if response.status_code in [401, 403]:  # Accept both 401 and 403
                print("  ✅ Correctly rejected request without token")
            else:
                self.results.append({
                    'test': 'JWT Authentication',
                    'status': 'FAIL',
                    'message': f'Should reject requests without token, got {response.status_code}'
                })
                return False
        except requests.exceptions.RequestException as e:
            self.results.append({
                'test': 'JWT Authentication',
                'status': 'FAIL',
                'message': f'Connection error: {str(e)}'
            })
            return False
        
        # Test with invalid token
        try:
            headers = {'Authorization': 'Bearer invalid-token'}
            response = requests.post('http://localhost:8000/analyze',
                                   headers=headers, json={'texts': ['test']}, timeout=5)
            if response.status_code in [401, 403]:  # Accept both 401 and 403
                print("  ✅ Correctly rejected invalid token")
            else:
                self.results.append({
                    'test': 'JWT Authentication',
                    'status': 'FAIL',
                    'message': f'Should reject invalid tokens, got {response.status_code}'
                })
                return False
        except requests.exceptions.RequestException as e:
            self.results.append({
                'test': 'JWT Authentication',
                'status': 'FAIL',
                'message': f'Connection error: {str(e)}'
            })
            return False
        
        self.results.append({
            'test': 'JWT Authentication',
            'status': 'PASS',
            'message': 'Authentication working correctly'
        })
        return True
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        print("\n🧠 Testing Sentiment Analysis...")
        
        token = self.generate_jwt_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        test_data = {
            'texts': [
                'This is a wonderful day!',
                'I hate this terrible situation',
                'This is a neutral statement'
            ],
            'include_behavioral_analysis': True,
            'include_influence_score': True
        }
        
        try:
            response = requests.post('http://localhost:8000/analyze',
                                   headers=headers, json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                if 'results' not in result:
                    self.results.append({
                        'test': 'Sentiment Analysis',
                        'status': 'FAIL',
                        'message': 'Missing results in response'
                    })
                    return False
                
                if len(result['results']) != 3:
                    self.results.append({
                        'test': 'Sentiment Analysis',
                        'status': 'FAIL',
                        'message': f'Expected 3 results, got {len(result["results"])}'
                    })
                    return False
                
                # Check sentiment values
                for i, res in enumerate(result['results']):
                    sentiment = res.get('sentiment', {})
                    if not all(key in sentiment for key in ['positive', 'negative', 'neutral', 'confidence']):
                        self.results.append({
                            'test': 'Sentiment Analysis',
                            'status': 'FAIL',
                            'message': f'Missing sentiment fields in result {i}'
                        })
                        return False
                
                self.results.append({
                    'test': 'Sentiment Analysis',
                    'status': 'PASS',
                    'message': f'Analyzed {len(result["results"])} texts successfully'
                })
                return True
            else:
                self.results.append({
                    'test': 'Sentiment Analysis',
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}: {response.text}'
                })
                return False
                
        except requests.exceptions.RequestException as e:
            self.results.append({
                'test': 'Sentiment Analysis',
                'status': 'FAIL',
                'message': f'Connection error: {str(e)}'
            })
            return False
    
    def test_behavioral_analysis(self):
        """Test behavioral pattern detection"""
        print("\n🎭 Testing Behavioral Analysis...")
        
        token = self.generate_jwt_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test text with aggressive patterns
        test_data = {
            'texts': ['I AM SO ANGRY! This is terrible!!!'],
            'include_behavioral_analysis': True
        }
        
        try:
            response = requests.post('http://localhost:8000/analyze',
                                   headers=headers, json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                first_result = result['results'][0]
                
                if 'behavioral_patterns' in first_result:
                    patterns = first_result['behavioral_patterns']
                    if patterns and any(p.get('pattern_type') == 'aggressive' for p in patterns):
                        self.results.append({
                            'test': 'Behavioral Analysis',
                            'status': 'PASS',
                            'message': 'Correctly detected aggressive pattern'
                        })
                        return True
                    else:
                        self.results.append({
                            'test': 'Behavioral Analysis',
                            'status': 'WARN',
                            'message': 'Did not detect expected aggressive pattern'
                        })
                        return True
                else:
                    self.results.append({
                        'test': 'Behavioral Analysis',
                        'status': 'FAIL',
                        'message': 'Missing behavioral_patterns in response'
                    })
                    return False
            else:
                self.results.append({
                    'test': 'Behavioral Analysis',
                    'status': 'FAIL',
                    'message': f'HTTP {response.status_code}: {response.text}'
                })
                return False
                
        except requests.exceptions.RequestException as e:
            self.results.append({
                'test': 'Behavioral Analysis',
                'status': 'FAIL',
                'message': f'Connection error: {str(e)}'
            })
            return False
    
    def test_api_endpoints(self):
        """Test various API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        
        token = self.generate_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        endpoints = [
            ('GET', '/health', None, 200),
            ('GET', '/models', None, 200),
            ('GET', '/stats', None, 200),
            ('POST', '/analyze/sentiment', {'texts': ['test']}, 200)
        ]
        
        passed = 0
        total = len(endpoints)
        
        for method, endpoint, data, expected_status in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f'http://localhost:8000{endpoint}',
                                          headers=headers, timeout=5)
                else:
                    response = requests.post(f'http://localhost:8000{endpoint}',
                                           headers=headers, json=data, timeout=5)
                
                if response.status_code == expected_status:
                    print(f"  ✅ {method} {endpoint}: {response.status_code}")
                    passed += 1
                else:
                    print(f"  ❌ {method} {endpoint}: {response.status_code} (expected {expected_status})")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {method} {endpoint}: Connection error - {str(e)}")
        
        if passed == total:
            self.results.append({
                'test': 'API Endpoints',
                'status': 'PASS',
                'message': f'All {total} endpoints working'
            })
            return True
        else:
            self.results.append({
                'test': 'API Endpoints',
                'status': 'FAIL',
                'message': f'{passed}/{total} endpoints working'
            })
            return False
    
    def test_service_process(self):
        """Test if NLP service process is running"""
        print("\n⚙️  Testing Service Process...")
        
        try:
            # Check if process is running on port 8000
            result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True)
            if ':8000' in result.stdout:
                self.results.append({
                    'test': 'Service Process',
                    'status': 'PASS',
                    'message': 'NLP service running on port 8000'
                })
                return True
            else:
                self.results.append({
                    'test': 'Service Process',
                    'status': 'FAIL',
                    'message': 'No service found on port 8000'
                })
                return False
        except Exception as e:
            self.results.append({
                'test': 'Service Process',
                'status': 'WARN',
                'message': f'Could not check process: {str(e)}'
            })
            return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Deployment Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_environment_configuration,
            self.test_file_structure,
            self.test_service_process,
            self.test_nlp_service_health,
            self.test_jwt_authentication,
            self.test_sentiment_analysis,
            self.test_behavioral_analysis,
            self.test_api_endpoints
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.results.append({
                    'test': test.__name__,
                    'status': 'ERROR',
                    'message': f'Test error: {str(e)}'
                })
        
        # Count results
        for result in self.results:
            if result['status'] == 'PASS':
                passed += 1
            elif result['status'] == 'FAIL' or result['status'] == 'ERROR':
                failed += 1
            elif result['status'] == 'WARN':
                warnings += 1
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for result in self.results:
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌',
                'WARN': '⚠️',
                'ERROR': '💥'
            }.get(result['status'], '❓')
            
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result['message']:
                print(f"   {result['message']}")
        
        print("\n" + "=" * 60)
        print(f"📈 OVERALL RESULTS:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⚠️  Warnings: {warnings}")
        print(f"   ⏱️  Duration: {duration:.2f} seconds")
        
        # Overall status
        if failed == 0:
            if warnings == 0:
                print(f"\n🎉 ALL TESTS PASSED! System is fully operational.")
                return True
            else:
                print(f"\n✅ TESTS PASSED WITH WARNINGS. System is operational with minor issues.")
                return True
        else:
            print(f"\n❌ TESTS FAILED. {failed} critical issues need to be addressed.")
            return False

def main():
    """Main test execution"""
    tester = ComprehensiveDeploymentTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
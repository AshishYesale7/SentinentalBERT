#!/usr/bin/env python3
"""
Authentication Functionality Test Suite
Tests JWT authentication and permission-based access control without requiring running services
"""

import os
import sys
import json
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockJWTHandler:
    """Mock JWT handler for testing authentication without external dependencies"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')
    
    def _base64_url_encode(self, data: bytes) -> str:
        """Base64 URL encode"""
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
    
    def _base64_url_decode(self, data: str) -> bytes:
        """Base64 URL decode"""
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)
    
    def create_token(self, payload: Dict[str, Any]) -> str:
        """Create a JWT token"""
        # Header
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        # Add expiration if not present
        if 'exp' not in payload:
            payload['exp'] = int(time.time()) + 3600  # 1 hour
        
        # Encode header and payload
        header_encoded = self._base64_url_encode(json.dumps(header).encode())
        payload_encoded = self._base64_url_encode(json.dumps(payload).encode())
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            self.secret_key,
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature_encoded = self._base64_url_encode(signature)
        
        return f"{message}.{signature_encoded}"
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_encoded, payload_encoded, signature_encoded = parts
            
            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = hmac.new(
                self.secret_key,
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            actual_signature = self._base64_url_decode(signature_encoded)
            
            if not hmac.compare_digest(expected_signature, actual_signature):
                return None
            
            # Decode payload
            payload_json = self._base64_url_decode(payload_encoded).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Check expiration
            if 'exp' in payload and payload['exp'] < time.time():
                return None
            
            return payload
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

class AuthenticationTester:
    """Test authentication functionality"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', 'test-secret-key-for-development-only')
        self.jwt_handler = MockJWTHandler(self.jwt_secret)
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0
            }
        }
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results"""
        logger.info(f"Running test: {test_name}")
        self.test_results['summary']['total_tests'] += 1
        
        try:
            result = test_func()
            if result.get('status') == 'passed':
                self.test_results['summary']['passed'] += 1
                logger.info(f"✅ {test_name} - PASSED")
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
    
    def test_jwt_token_creation(self) -> Dict[str, Any]:
        """Test JWT token creation"""
        try:
            # Test payload
            payload = {
                'user_id': 'test_user',
                'role': 'investigator',
                'permissions': ['read_posts', 'analyze_content'],
                'iat': int(time.time())
            }
            
            # Create token
            token = self.jwt_handler.create_token(payload)
            
            # Verify token structure
            parts = token.split('.')
            if len(parts) != 3:
                return {
                    'status': 'failed',
                    'message': 'Token does not have 3 parts',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Verify token can be decoded
            decoded = self.jwt_handler.verify_token(token)
            if not decoded:
                return {
                    'status': 'failed',
                    'message': 'Token verification failed',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Verify payload matches
            for key in ['user_id', 'role', 'permissions']:
                if decoded.get(key) != payload[key]:
                    return {
                        'status': 'failed',
                        'message': f'Payload mismatch for {key}',
                        'timestamp': datetime.now().isoformat()
                    }
            
            return {
                'status': 'passed',
                'message': 'JWT token creation and verification successful',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'token_length': len(token),
                    'decoded_payload': decoded
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'JWT token creation error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_token_expiration(self) -> Dict[str, Any]:
        """Test JWT token expiration handling"""
        try:
            # Create expired token
            expired_payload = {
                'user_id': 'test_user',
                'role': 'investigator',
                'exp': int(time.time()) - 3600  # Expired 1 hour ago
            }
            
            expired_token = self.jwt_handler.create_token(expired_payload)
            
            # Verify expired token is rejected
            decoded = self.jwt_handler.verify_token(expired_token)
            if decoded is not None:
                return {
                    'status': 'failed',
                    'message': 'Expired token was accepted',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Create valid token
            valid_payload = {
                'user_id': 'test_user',
                'role': 'investigator',
                'exp': int(time.time()) + 3600  # Expires in 1 hour
            }
            
            valid_token = self.jwt_handler.create_token(valid_payload)
            
            # Verify valid token is accepted
            decoded = self.jwt_handler.verify_token(valid_token)
            if decoded is None:
                return {
                    'status': 'failed',
                    'message': 'Valid token was rejected',
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'status': 'passed',
                'message': 'Token expiration handling works correctly',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Token expiration test error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_role_based_permissions(self) -> Dict[str, Any]:
        """Test role-based access control"""
        try:
            # Define role permissions
            role_permissions = {
                'admin': ['read_posts', 'analyze_content', 'manage_users', 'access_evidence'],
                'investigator': ['read_posts', 'analyze_content', 'access_evidence'],
                'analyst': ['read_posts', 'analyze_content'],
                'viewer': ['read_posts']
            }
            
            test_cases = [
                {
                    'role': 'admin',
                    'required_permission': 'manage_users',
                    'should_have_access': True
                },
                {
                    'role': 'investigator',
                    'required_permission': 'access_evidence',
                    'should_have_access': True
                },
                {
                    'role': 'analyst',
                    'required_permission': 'access_evidence',
                    'should_have_access': False
                },
                {
                    'role': 'viewer',
                    'required_permission': 'analyze_content',
                    'should_have_access': False
                }
            ]
            
            failed_cases = []
            
            for case in test_cases:
                role = case['role']
                required_permission = case['required_permission']
                should_have_access = case['should_have_access']
                
                # Create token with role
                payload = {
                    'user_id': f'test_{role}',
                    'role': role,
                    'permissions': role_permissions[role]
                }
                
                token = self.jwt_handler.create_token(payload)
                decoded = self.jwt_handler.verify_token(token)
                
                if not decoded:
                    failed_cases.append(f"Token verification failed for role {role}")
                    continue
                
                has_permission = required_permission in decoded.get('permissions', [])
                
                if has_permission != should_have_access:
                    failed_cases.append(
                        f"Role {role} permission check failed for {required_permission}: "
                        f"expected {should_have_access}, got {has_permission}"
                    )
            
            if failed_cases:
                return {
                    'status': 'failed',
                    'message': f'Role-based permission failures: {"; ".join(failed_cases)}',
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'status': 'passed',
                'message': f'Role-based permissions working correctly for {len(test_cases)} test cases',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Role-based permission test error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_token_tampering_detection(self) -> Dict[str, Any]:
        """Test detection of tampered tokens"""
        try:
            # Create valid token
            payload = {
                'user_id': 'test_user',
                'role': 'viewer',
                'permissions': ['read_posts']
            }
            
            valid_token = self.jwt_handler.create_token(payload)
            parts = valid_token.split('.')
            
            # Create tampered payload by modifying the base64 encoded payload
            tampered_payload = json.dumps({
                'user_id': 'test_user',
                'role': 'admin',  # Changed from viewer to admin
                'permissions': ['read_posts', 'manage_users'],  # Added permission
                'exp': int(time.time()) + 3600
            })
            tampered_payload_encoded = self.jwt_handler._base64_url_encode(tampered_payload.encode())
            tampered_token = f"{parts[0]}.{tampered_payload_encoded}.{parts[2]}"
            
            # Test various tampering scenarios
            tampering_tests = [
                {
                    'name': 'Modified payload',
                    'token': tampered_token,
                    'should_be_valid': False
                },
                {
                    'name': 'Modified signature',
                    'token': valid_token[:-5] + 'XXXXX',
                    'should_be_valid': False
                },
                {
                    'name': 'Extra parts',
                    'token': valid_token + '.extra',
                    'should_be_valid': False
                },
                {
                    'name': 'Missing parts',
                    'token': '.'.join(valid_token.split('.')[:-1]),
                    'should_be_valid': False
                },
                {
                    'name': 'Original token',
                    'token': valid_token,
                    'should_be_valid': True
                }
            ]
            
            failed_tests = []
            
            for test in tampering_tests:
                decoded = self.jwt_handler.verify_token(test['token'])
                is_valid = decoded is not None
                
                if is_valid != test['should_be_valid']:
                    failed_tests.append(
                        f"{test['name']}: expected valid={test['should_be_valid']}, got valid={is_valid}"
                    )
            
            if failed_tests:
                return {
                    'status': 'failed',
                    'message': f'Token tampering detection failures: {"; ".join(failed_tests)}',
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'status': 'passed',
                'message': f'Token tampering detection working correctly for {len(tampering_tests)} test cases',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Token tampering detection test error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_authentication_flow_simulation(self) -> Dict[str, Any]:
        """Test complete authentication flow simulation"""
        try:
            # Simulate login process
            login_credentials = {
                'officer_id': 'OFF-001',
                'badge_number': 'DCP-001',
                'department': 'Delhi Police Cyber Crime'
            }
            
            # Create authentication token
            auth_payload = {
                'officer_id': login_credentials['officer_id'],
                'badge_number': login_credentials['badge_number'],
                'department': login_credentials['department'],
                'role': 'investigator',
                'permissions': ['read_posts', 'analyze_content', 'access_evidence'],
                'login_time': int(time.time()),
                'session_id': hashlib.md5(f"{login_credentials['officer_id']}{time.time()}".encode()).hexdigest()
            }
            
            auth_token = self.jwt_handler.create_token(auth_payload)
            
            # Simulate API requests with token
            api_requests = [
                {
                    'endpoint': '/api/posts/search',
                    'required_permission': 'read_posts',
                    'should_succeed': True
                },
                {
                    'endpoint': '/api/analysis/sentiment',
                    'required_permission': 'analyze_content',
                    'should_succeed': True
                },
                {
                    'endpoint': '/api/evidence/collect',
                    'required_permission': 'access_evidence',
                    'should_succeed': True
                },
                {
                    'endpoint': '/api/admin/users',
                    'required_permission': 'manage_users',
                    'should_succeed': False
                }
            ]
            
            failed_requests = []
            
            for request in api_requests:
                # Verify token
                decoded = self.jwt_handler.verify_token(auth_token)
                if not decoded:
                    failed_requests.append(f"Token verification failed for {request['endpoint']}")
                    continue
                
                # Check permission
                has_permission = request['required_permission'] in decoded.get('permissions', [])
                
                if has_permission != request['should_succeed']:
                    failed_requests.append(
                        f"Permission check failed for {request['endpoint']}: "
                        f"expected {request['should_succeed']}, got {has_permission}"
                    )
            
            if failed_requests:
                return {
                    'status': 'failed',
                    'message': f'Authentication flow failures: {"; ".join(failed_requests)}',
                    'timestamp': datetime.now().isoformat()
                }
            
            return {
                'status': 'passed',
                'message': f'Authentication flow simulation successful for {len(api_requests)} API requests',
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'officer_id': auth_payload['officer_id'],
                    'session_id': auth_payload['session_id'],
                    'permissions': auth_payload['permissions']
                }
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Authentication flow simulation error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all authentication tests"""
        logger.info("Starting authentication functionality test suite...")
        
        # Test sequence
        tests = [
            ('JWT Token Creation', self.test_jwt_token_creation),
            ('Token Expiration', self.test_token_expiration),
            ('Role-Based Permissions', self.test_role_based_permissions),
            ('Token Tampering Detection', self.test_token_tampering_detection),
            ('Authentication Flow Simulation', self.test_authentication_flow_simulation)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate summary
        total = self.test_results['summary']['total_tests']
        passed = self.test_results['summary']['passed']
        failed = self.test_results['summary']['failed']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"AUTHENTICATION FUNCTIONALITY TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed} ✅")
        logger.info(f"Failed: {failed} ❌")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Overall status
        overall_status = "AUTHENTICATION_WORKING" if failed == 0 else "AUTHENTICATION_ISSUES"
        self.test_results['overall_status'] = overall_status
        logger.info(f"Overall Status: {overall_status}")
        
        # Save results
        with open('authentication_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: authentication_test_results.json")
        
        return self.test_results

def main():
    """Main test execution"""
    tester = AuthenticationTester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results['overall_status'] == 'AUTHENTICATION_ISSUES':
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
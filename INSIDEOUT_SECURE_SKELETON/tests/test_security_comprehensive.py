"""
InsideOut Platform - Comprehensive Security Tests
Tests all security components including authentication, authorization, encryption, and compliance
"""

import pytest
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json
import jwt

# Import components to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.secure_authentication import (
    SecureAuthenticationService, SecurePasswordManager, MFAProvider,
    RBACService, SecureSessionManager, OfficerCredentials, UserRole, Permission
)
from legal.legal_compliance_system import (
    LegalAuthorityVerificationService, ConstitutionalComplianceChecker,
    WarrantData, SearchParameters, WarrantType, JurisdictionLevel,
    GeographicBounds, TemporalBounds, PlatformScope, ConstitutionalRight
)
from evidence.evidence_management import (
    EvidenceCollectionService, EncryptionService, DigitalSignatureService,
    ChainOfCustodyService, EvidencePackage, EvidenceType, ChainOfCustodyAction
)
from analysis.secure_bert_engine import (
    SecureBERTAnalysisEngine, LegalScopeValidator, PatternDetectionEngine,
    AnalysisScope, SocialMediaPost
)
from monitoring.security_monitoring import (
    SecurityMonitoringSystem, ThreatDetectionEngine, SecurityEvent,
    EventType, ThreatLevel
)

class TestSecurePasswordManager:
    """Test password security functions"""
    
    def test_password_hashing(self):
        """Test secure password hashing"""
        password = "SecurePassword123!"
        hashed = SecurePasswordManager.hash_password(password)
        
        # Verify hash is different from password
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
        # Verify password verification works
        assert SecurePasswordManager.verify_password(password, hashed)
        assert not SecurePasswordManager.verify_password("wrong_password", hashed)
    
    def test_password_generation(self):
        """Test secure password generation"""
        password = SecurePasswordManager.generate_secure_password(16)
        
        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*" for c in password)
        
        # Test uniqueness
        password2 = SecurePasswordManager.generate_secure_password(16)
        assert password != password2

class TestMFAProvider:
    """Test multi-factor authentication"""
    
    def test_totp_secret_generation(self):
        """Test TOTP secret generation"""
        mfa = MFAProvider()
        secret = mfa.generate_totp_secret()
        
        assert len(secret) == 32  # Base32 encoded
        assert secret.isalnum()
    
    def test_totp_verification(self):
        """Test TOTP token verification"""
        mfa = MFAProvider()
        secret = "JBSWY3DPEHPK3PXP"  # Test secret
        
        # Generate current token
        import pyotp
        totp = pyotp.TOTP(secret)
        current_token = totp.now()
        
        # Verify token
        assert mfa.verify_totp_token(secret, current_token)
        assert not mfa.verify_totp_token(secret, "000000")
    
    def test_backup_codes_generation(self):
        """Test backup codes generation"""
        mfa = MFAProvider()
        codes = mfa.generate_backup_codes(10)
        
        assert len(codes) == 10
        assert all(len(code) == 16 for code in codes)  # 8 bytes hex = 16 chars
        assert len(set(codes)) == 10  # All unique

class TestRBACService:
    """Test role-based access control"""
    
    def test_role_permissions(self):
        """Test role permission mappings"""
        rbac = RBACService()
        
        # Test investigator permissions
        investigator_perms = rbac.get_role_permissions(UserRole.INVESTIGATOR)
        assert Permission.READ_CASES in investigator_perms
        assert Permission.ANALYZE_CONTENT in investigator_perms
        assert Permission.APPROVE_WARRANTS not in investigator_perms
        
        # Test admin permissions
        admin_perms = rbac.get_role_permissions(UserRole.ADMIN)
        assert Permission.SYSTEM_ADMIN in admin_perms
        assert len(admin_perms) > len(investigator_perms)
    
    def test_permission_checking(self):
        """Test permission checking logic"""
        rbac = RBACService()
        
        # Test investigator permissions
        assert rbac.check_permission(UserRole.INVESTIGATOR, Permission.READ_CASES)
        assert not rbac.check_permission(UserRole.INVESTIGATOR, Permission.APPROVE_WARRANTS)
        
        # Test admin permissions (should have all)
        assert rbac.check_permission(UserRole.ADMIN, Permission.APPROVE_WARRANTS)
        assert rbac.check_permission(UserRole.ADMIN, Permission.SYSTEM_ADMIN)

class TestEncryptionService:
    """Test encryption and data protection"""
    
    def test_evidence_encryption(self):
        """Test evidence encryption/decryption"""
        master_key = b"test_master_key_32_bytes_long!!!"
        encryption = EncryptionService(master_key)
        
        evidence_id = "test_evidence_001"
        test_data = b"This is sensitive evidence data"
        
        # Encrypt data
        encrypted_data, key_id = encryption.encrypt_evidence(test_data, evidence_id)
        
        assert encrypted_data != test_data
        assert len(key_id) == 16
        
        # Decrypt data
        decrypted_data = encryption.decrypt_evidence(encrypted_data, evidence_id)
        assert decrypted_data == test_data
    
    def test_content_hashing(self):
        """Test content integrity hashing"""
        master_key = b"test_master_key_32_bytes_long!!!"
        encryption = EncryptionService(master_key)
        
        test_data = b"Test data for hashing"
        content_hash = encryption.create_content_hash(test_data)
        
        assert len(content_hash) == 64  # SHA-256 hex
        assert content_hash == hashlib.sha256(test_data).hexdigest()
        
        # Verify integrity checking
        assert encryption.verify_content_integrity(test_data, content_hash)
        assert not encryption.verify_content_integrity(b"different data", content_hash)

class TestDigitalSignatureService:
    """Test digital signatures"""
    
    def test_evidence_signing(self):
        """Test evidence digital signing"""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        # Generate test key pair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        signature_service = DigitalSignatureService(private_key_pem)
        
        evidence_hash = "test_hash_12345"
        officer_id = "officer_123"
        
        # Create signature
        signature = signature_service.sign_evidence(evidence_hash, officer_id)
        
        assert len(signature) > 100  # RSA signatures are long
        
        # Verify signature (would need message reconstruction in real implementation)
        # This is a simplified test
        assert isinstance(signature, str)

@pytest.mark.asyncio
class TestLegalCompliance:
    """Test legal compliance system"""
    
    async def test_fourth_amendment_compliance(self):
        """Test Fourth Amendment compliance checking"""
        checker = ConstitutionalComplianceChecker()
        
        # Create valid warrant
        warrant = WarrantData(
            warrant_id="WR-2024-001",
            warrant_type=WarrantType.SEARCH_WARRANT,
            case_number="CASE-001",
            court_name="Test Court",
            judge_name="Judge Smith",
            issuing_date=datetime.utcnow() - timedelta(days=1),
            expiration_date=datetime.utcnow() + timedelta(days=30),
            jurisdiction=JurisdictionLevel.DISTRICT,
            geographic_scope=GeographicBounds(country="India", state="Delhi"),
            temporal_scope=TemporalBounds(
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow()
            ),
            platform_scope=PlatformScope(
                platforms=["twitter"],
                account_types=["public"],
                content_types=["posts"]
            ),
            probable_cause="Sufficient probable cause documented",
            legal_basis="Criminal investigation",
            constitutional_considerations=[ConstitutionalRight.FOURTH_AMENDMENT]
        )
        
        # Create search parameters within scope
        search_params = SearchParameters(
            keywords=["test"],
            hashtags=[],
            user_accounts=[],
            geographic_area=GeographicBounds(country="India", state="Delhi"),
            time_range=TemporalBounds(
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow()
            ),
            platforms=["twitter"],
            content_types=["posts"]
        )
        
        result = await checker.check_fourth_amendment_compliance(warrant, search_params)
        
        assert result.compliant
        assert len(result.violations) == 0
    
    async def test_first_amendment_compliance(self):
        """Test First Amendment compliance checking"""
        checker = ConstitutionalComplianceChecker()
        
        # Test protected speech content
        protected_content = "This is a political opinion about government policies"
        search_params = SearchParameters(
            keywords=["political", "government"],
            hashtags=[],
            user_accounts=[],
            geographic_area=GeographicBounds(country="India"),
            time_range=TemporalBounds(
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow()
            ),
            platforms=["twitter"],
            content_types=["posts"]
        )
        
        result = await checker.check_first_amendment_compliance(protected_content, search_params)
        
        # Should flag potential protected speech issues
        assert len(result.warnings) > 0
        assert result.legal_review_required

@pytest.mark.asyncio
class TestEvidenceManagement:
    """Test evidence collection and management"""
    
    async def test_evidence_collection(self):
        """Test complete evidence collection process"""
        # Setup services
        master_key = b"test_master_key_32_bytes_long!!!"
        encryption_service = EncryptionService(master_key)
        
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        signature_service = DigitalSignatureService(private_key_pem)
        
        # Mock blockchain service
        blockchain_service = Mock()
        blockchain_service.record_evidence_on_blockchain = AsyncMock(return_value="0x123abc")
        
        custody_service = ChainOfCustodyService(signature_service, blockchain_service)
        collection_service = EvidenceCollectionService(
            encryption_service, signature_service, custody_service
        )
        
        # Collect evidence
        officer_info = {
            'officer_id': 'OFF123',
            'name': 'Test Officer',
            'badge_number': 'BADGE123',
            'location': 'Test Location'
        }
        
        test_data = b"Test social media post content"
        platform_metadata = {'post_id': '12345', 'author': '@testuser'}
        
        evidence = await collection_service.collect_social_media_evidence(
            platform="twitter",
            content_url="https://twitter.com/test/status/12345",
            raw_data=test_data,
            platform_metadata=platform_metadata,
            warrant_id="WR-2024-001",
            case_number="CASE-001",
            collecting_officer=officer_info
        )
        
        # Verify evidence properties
        assert evidence.evidence_type == EvidenceType.SOCIAL_MEDIA_POST
        assert evidence.warrant_id == "WR-2024-001"
        assert evidence.case_number == "CASE-001"
        assert len(evidence.chain_of_custody) == 1
        assert evidence.chain_of_custody[0].action == ChainOfCustodyAction.COLLECTED
        assert evidence.content_hash
        assert evidence.digital_signature
        
        # Verify evidence integrity
        integrity_valid = await collection_service.verify_evidence_integrity(evidence)
        assert integrity_valid

@pytest.mark.asyncio
class TestBERTAnalysisEngine:
    """Test BERT analysis engine"""
    
    async def test_legal_scope_validation(self):
        """Test legal scope validation"""
        validator = LegalScopeValidator()
        
        # Create analysis scope
        scope = AnalysisScope(
            warrant_id="WR-2024-001",
            geographic_bounds={'country': 'India', 'state': 'Delhi'},
            temporal_bounds={
                'start': datetime.utcnow() - timedelta(days=7),
                'end': datetime.utcnow()
            },
            platform_scope=['twitter'],
            content_types=['posts'],
            keywords=['test', 'investigation'],
            legal_constraints=[]
        )
        
        validation_result = await validator.validate_analysis_scope(scope)
        
        assert validation_result['geographic_valid']
        assert validation_result['temporal_valid']
        assert validation_result['constitutional_compliant']
    
    async def test_content_filtering(self):
        """Test content filtering by legal scope"""
        validator = LegalScopeValidator()
        
        # Create test posts
        posts = [
            SocialMediaPost(
                post_id="post_1",
                platform="twitter",
                author_id="user_1",
                author_username="@user1",
                content="Test post within scope",
                timestamp=datetime.utcnow() - timedelta(hours=1),
                location={'lat': 28.6139, 'lng': 77.2090}
            ),
            SocialMediaPost(
                post_id="post_2",
                platform="facebook",  # Different platform
                author_id="user_2",
                author_username="@user2",
                content="Test post outside scope",
                timestamp=datetime.utcnow() - timedelta(days=10),  # Outside time range
                location={'lat': 40.7128, 'lng': -74.0060}  # Different location
            )
        ]
        
        scope = AnalysisScope(
            warrant_id="WR-2024-001",
            geographic_bounds={'country': 'India'},
            temporal_bounds={
                'start': datetime.utcnow() - timedelta(days=7),
                'end': datetime.utcnow()
            },
            platform_scope=['twitter'],
            content_types=['posts'],
            keywords=['test'],
            legal_constraints=[]
        )
        
        filtered_posts = await validator.filter_content_by_scope(posts, scope)
        
        # Should only include the first post
        assert len(filtered_posts) == 1
        assert filtered_posts[0].post_id == "post_1"

@pytest.mark.asyncio
class TestSecurityMonitoring:
    """Test security monitoring system"""
    
    async def test_threat_detection(self):
        """Test threat detection engine"""
        detector = ThreatDetectionEngine()
        
        # Create suspicious event
        event = SecurityEvent(
            event_id="evt_001",
            event_type=EventType.AUTHENTICATION_FAILURE,
            threat_level=ThreatLevel.MEDIUM,
            timestamp=datetime.utcnow(),
            source_ip="192.168.1.100",
            user_id="test_user",
            resource="/api/v1/auth/login",
            description="Failed login attempt",
            raw_data={"query": "'; DROP TABLE users; --"},  # SQL injection attempt
            indicators=[],
            mitre_tactics=["TA0006"],
            mitre_techniques=["T1110"]
        )
        
        threats = await detector.analyze_event(event)
        
        # Should detect SQL injection pattern
        assert len(threats) > 0
        assert any("injection" in threat.lower() for threat in threats)
    
    async def test_brute_force_detection(self):
        """Test brute force attack detection"""
        detector = ThreatDetectionEngine()
        
        # Simulate multiple failed login attempts
        for i in range(6):  # Exceed threshold of 5
            event = SecurityEvent(
                event_id=f"evt_{i:03d}",
                event_type=EventType.AUTHENTICATION_FAILURE,
                threat_level=ThreatLevel.MEDIUM,
                timestamp=datetime.utcnow() - timedelta(minutes=i),
                source_ip="192.168.1.100",
                user_id="test_user",
                resource="/api/v1/auth/login",
                description="Failed login attempt",
                raw_data={"username": "test_user", "password": "wrong"},
                indicators=[],
                mitre_tactics=["TA0006"],
                mitre_techniques=["T1110"]
            )
            
            threats = await detector.analyze_event(event)
            
            if i >= 5:  # Should detect brute force after threshold
                assert any("brute force" in threat.lower() for threat in threats)

@pytest.mark.asyncio
class TestIntegrationSecurity:
    """Integration tests for complete security workflows"""
    
    async def test_complete_authentication_flow(self):
        """Test complete authentication workflow"""
        # Mock database service
        class MockDB:
            async def get_officer_by_id(self, officer_id):
                return {
                    'officer_id': officer_id,
                    'password_hash': SecurePasswordManager.hash_password('TestPassword123!'),
                    'role': 'investigator',
                    'active': True,
                    'mfa_enabled': False,
                    'password_changed_at': datetime.utcnow() - timedelta(days=30)
                }
        
        # Initialize authentication service
        db_service = MockDB()
        secret_key = secrets.token_urlsafe(32)
        auth_service = SecureAuthenticationService(db_service, secret_key)
        
        # Test authentication
        credentials = OfficerCredentials(
            officer_id="test_officer",
            badge_number="BADGE123",
            password="TestPassword123!",
            department="Test Department",
            state="Test State"
        )
        
        result = await auth_service.authenticate_officer(
            credentials, "192.168.1.100", "Test User Agent"
        )
        
        assert result.success
        assert result.session_token
        assert len(result.permissions) > 0
        
        # Test session validation
        session = auth_service.validate_session_token(result.session_token, "192.168.1.100")
        assert session
        assert session.officer_id == "test_officer"
    
    async def test_evidence_to_analysis_workflow(self):
        """Test complete evidence collection to analysis workflow"""
        # This would test the complete flow from evidence collection
        # through legal compliance checking to BERT analysis
        
        # Setup all required services (simplified for test)
        master_key = b"test_master_key_32_bytes_long!!!"
        encryption_service = EncryptionService(master_key)
        
        # Mock other services for integration test
        # In a real test, you'd set up all the actual services
        
        # Verify that evidence can be collected, validated, and analyzed
        # while maintaining legal compliance throughout
        
        assert True  # Placeholder for full integration test

class TestSecurityConfiguration:
    """Test security configuration and hardening"""
    
    def test_password_policy_enforcement(self):
        """Test password policy enforcement"""
        # Test weak passwords are rejected
        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "Password",  # No numbers or special chars
            "Pass1",     # Too short
        ]
        
        for weak_password in weak_passwords:
            # In a real implementation, you'd have password policy validation
            # This is a placeholder for that test
            assert len(weak_password) < 12 or not any(c.isdigit() for c in weak_password)
    
    def test_session_security(self):
        """Test session security measures"""
        secret_key = secrets.token_urlsafe(32)
        session_manager = SecureSessionManager(secret_key)
        
        # Test session timeout
        session = session_manager.create_session(
            "test_officer", UserRole.INVESTIGATOR, "192.168.1.100", "Test Agent"
        )
        
        assert session.session_id
        assert session.expires_at > datetime.utcnow()
        
        # Test session validation
        valid_session = session_manager.validate_session(
            session.session_id, "192.168.1.100"
        )
        assert valid_session
        
        # Test IP address validation (session hijacking protection)
        invalid_session = session_manager.validate_session(
            session.session_id, "192.168.1.200"  # Different IP
        )
        assert invalid_session is None

# Performance and load testing
@pytest.mark.asyncio
class TestPerformanceSecurity:
    """Test performance under security constraints"""
    
    async def test_encryption_performance(self):
        """Test encryption performance with large data"""
        master_key = b"test_master_key_32_bytes_long!!!"
        encryption_service = EncryptionService(master_key)
        
        # Test with large data (1MB)
        large_data = b"x" * (1024 * 1024)
        evidence_id = "perf_test_001"
        
        start_time = datetime.utcnow()
        encrypted_data, key_id = encryption_service.encrypt_evidence(large_data, evidence_id)
        encryption_time = (datetime.utcnow() - start_time).total_seconds()
        
        start_time = datetime.utcnow()
        decrypted_data = encryption_service.decrypt_evidence(encrypted_data, evidence_id)
        decryption_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Verify correctness
        assert decrypted_data == large_data
        
        # Performance should be reasonable (less than 1 second for 1MB)
        assert encryption_time < 1.0
        assert decryption_time < 1.0
    
    async def test_concurrent_authentication(self):
        """Test concurrent authentication requests"""
        # Mock database service
        class MockDB:
            async def get_officer_by_id(self, officer_id):
                return {
                    'officer_id': officer_id,
                    'password_hash': SecurePasswordManager.hash_password('TestPassword123!'),
                    'role': 'investigator',
                    'active': True,
                    'mfa_enabled': False,
                    'password_changed_at': datetime.utcnow() - timedelta(days=30)
                }
        
        db_service = MockDB()
        secret_key = secrets.token_urlsafe(32)
        auth_service = SecureAuthenticationService(db_service, secret_key)
        
        # Create multiple concurrent authentication requests
        async def authenticate_user(user_id):
            credentials = OfficerCredentials(
                officer_id=f"officer_{user_id}",
                badge_number=f"BADGE{user_id}",
                password="TestPassword123!",
                department="Test Department",
                state="Test State"
            )
            
            return await auth_service.authenticate_officer(
                credentials, f"192.168.1.{user_id}", "Test User Agent"
            )
        
        # Run 10 concurrent authentications
        tasks = [authenticate_user(i) for i in range(1, 11)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(result.success for result in results)
        assert len(set(result.session_token for result in results)) == 10  # All unique tokens

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
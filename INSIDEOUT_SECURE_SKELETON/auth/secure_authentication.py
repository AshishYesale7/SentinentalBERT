"""
InsideOut Platform - Secure Authentication System
Implements multi-factor authentication, RBAC, and secure session management
"""

import asyncio
import hashlib
import secrets
import jwt
import pyotp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

# Configure secure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Defined user roles with specific permissions"""
    INVESTIGATOR = "investigator"
    SUPERVISOR = "supervisor" 
    ADMIN = "admin"
    ANALYST = "analyst"
    LEGAL_OFFICER = "legal_officer"

class Permission(Enum):
    """Granular permissions for RBAC"""
    READ_CASES = "read_cases"
    ANALYZE_CONTENT = "analyze_content"
    APPROVE_WARRANTS = "approve_warrants"
    MANAGE_USERS = "manage_users"
    ACCESS_EVIDENCE = "access_evidence"
    GENERATE_REPORTS = "generate_reports"
    SYSTEM_ADMIN = "system_admin"
    LEGAL_REVIEW = "legal_review"

@dataclass
class OfficerCredentials:
    """Secure officer credentials structure"""
    officer_id: str
    badge_number: str
    password: str
    digital_certificate: Optional[str] = None
    department: str = ""
    state: str = ""

@dataclass
class AuthResult:
    """Authentication result with security context"""
    success: bool
    officer_id: Optional[str] = None
    session_token: Optional[str] = None
    mfa_required: bool = False
    mfa_token: Optional[str] = None
    permissions: List[Permission] = None
    error_message: Optional[str] = None
    requires_password_change: bool = False

@dataclass
class SecureSession:
    """Secure session with encryption and expiration"""
    session_id: str
    officer_id: str
    role: UserRole
    permissions: List[Permission]
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    mfa_verified: bool = False

class SecurePasswordManager:
    """Secure password management with bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with secure salt"""
        salt = bcrypt.gensalt(rounds=12)  # High cost factor for security
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate cryptographically secure password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

class MFAProvider:
    """Multi-Factor Authentication provider"""
    
    def __init__(self):
        self.totp_issuer = "InsideOut-Platform"
    
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for new user"""
        return pyotp.random_base32()
    
    def generate_totp_qr_url(self, officer_id: str, secret: str) -> str:
        """Generate QR code URL for TOTP setup"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=officer_id,
            issuer_name=self.totp_issuer
        )
    
    def verify_totp_token(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 30-second window
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA recovery"""
        return [secrets.token_hex(8) for _ in range(count)]

class RBACService:
    """Role-Based Access Control service"""
    
    # Define role permissions mapping
    ROLE_PERMISSIONS = {
        UserRole.INVESTIGATOR: [
            Permission.READ_CASES,
            Permission.ANALYZE_CONTENT,
            Permission.ACCESS_EVIDENCE,
            Permission.GENERATE_REPORTS
        ],
        UserRole.SUPERVISOR: [
            Permission.READ_CASES,
            Permission.ANALYZE_CONTENT,
            Permission.APPROVE_WARRANTS,
            Permission.ACCESS_EVIDENCE,
            Permission.GENERATE_REPORTS,
            Permission.LEGAL_REVIEW
        ],
        UserRole.ADMIN: [
            Permission.READ_CASES,
            Permission.ANALYZE_CONTENT,
            Permission.APPROVE_WARRANTS,
            Permission.MANAGE_USERS,
            Permission.ACCESS_EVIDENCE,
            Permission.GENERATE_REPORTS,
            Permission.SYSTEM_ADMIN,
            Permission.LEGAL_REVIEW
        ],
        UserRole.ANALYST: [
            Permission.READ_CASES,
            Permission.ANALYZE_CONTENT,
            Permission.GENERATE_REPORTS
        ],
        UserRole.LEGAL_OFFICER: [
            Permission.READ_CASES,
            Permission.APPROVE_WARRANTS,
            Permission.LEGAL_REVIEW,
            Permission.ACCESS_EVIDENCE
        ]
    }
    
    def get_role_permissions(self, role: UserRole) -> List[Permission]:
        """Get permissions for a specific role"""
        return self.ROLE_PERMISSIONS.get(role, [])
    
    def check_permission(self, role: UserRole, permission: Permission) -> bool:
        """Check if role has specific permission"""
        role_permissions = self.get_role_permissions(role)
        return permission in role_permissions or Permission.SYSTEM_ADMIN in role_permissions
    
    def validate_action(self, session: SecureSession, required_permission: Permission) -> bool:
        """Validate if session has permission for action"""
        return required_permission in session.permissions

class SecureSessionManager:
    """Secure session management with encryption"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        self.sessions: Dict[str, SecureSession] = {}
        self.session_timeout = timedelta(hours=8)  # 8-hour session timeout
        self.activity_timeout = timedelta(minutes=30)  # 30-minute inactivity timeout
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def create_session(self, officer_id: str, role: UserRole, 
                      ip_address: str, user_agent: str) -> SecureSession:
        """Create new secure session"""
        session_id = self._generate_session_id()
        now = datetime.utcnow()
        
        rbac = RBACService()
        permissions = rbac.get_role_permissions(role)
        
        session = SecureSession(
            session_id=session_id,
            officer_id=officer_id,
            role=role,
            permissions=permissions,
            created_at=now,
            expires_at=now + self.session_timeout,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        logger.info(f"Session created for officer {officer_id}: {session_id}")
        return session
    
    def validate_session(self, session_id: str, ip_address: str) -> Optional[SecureSession]:
        """Validate and refresh session"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        now = datetime.utcnow()
        
        # Check session expiration
        if now > session.expires_at:
            self.destroy_session(session_id)
            logger.warning(f"Session expired for officer {session.officer_id}")
            return None
        
        # Check inactivity timeout
        if now - session.last_activity > self.activity_timeout:
            self.destroy_session(session_id)
            logger.warning(f"Session timed out due to inactivity for officer {session.officer_id}")
            return None
        
        # Validate IP address (basic session hijacking protection)
        if session.ip_address != ip_address:
            self.destroy_session(session_id)
            logger.error(f"Session hijacking attempt detected for officer {session.officer_id}")
            return None
        
        # Update last activity
        session.last_activity = now
        return session
    
    def destroy_session(self, session_id: str):
        """Destroy session securely"""
        if session_id in self.sessions:
            officer_id = self.sessions[session_id].officer_id
            del self.sessions[session_id]
            logger.info(f"Session destroyed for officer {officer_id}: {session_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if now > session.expires_at or (now - session.last_activity) > self.activity_timeout
        ]
        
        for session_id in expired_sessions:
            self.destroy_session(session_id)

class AuditLogger:
    """Security audit logging service"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
        handler = logging.FileHandler('/var/log/insideout/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_authentication_attempt(self, officer_id: str, success: bool, 
                                 ip_address: str, user_agent: str, reason: str = ""):
        """Log authentication attempts"""
        status = "SUCCESS" if success else "FAILURE"
        self.audit_logger.info(
            f"AUTH_{status} - Officer: {officer_id} - IP: {ip_address} - "
            f"UserAgent: {user_agent} - Reason: {reason}"
        )
    
    def log_permission_check(self, officer_id: str, permission: str, 
                           granted: bool, resource: str = ""):
        """Log permission checks"""
        status = "GRANTED" if granted else "DENIED"
        self.audit_logger.info(
            f"PERMISSION_{status} - Officer: {officer_id} - Permission: {permission} - "
            f"Resource: {resource}"
        )
    
    def log_session_event(self, officer_id: str, event: str, session_id: str, 
                         ip_address: str = ""):
        """Log session events"""
        self.audit_logger.info(
            f"SESSION_{event} - Officer: {officer_id} - Session: {session_id} - "
            f"IP: {ip_address}"
        )

class SecureAuthenticationService:
    """Main authentication service with comprehensive security"""
    
    def __init__(self, database_service, secret_key: str):
        self.db = database_service
        self.password_manager = SecurePasswordManager()
        self.mfa_provider = MFAProvider()
        self.rbac_service = RBACService()
        self.session_manager = SecureSessionManager(secret_key)
        self.audit_logger = AuditLogger()
        
        # JWT configuration
        self.jwt_secret = secret_key
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration = timedelta(hours=1)
    
    async def authenticate_officer(self, credentials: OfficerCredentials, 
                                 ip_address: str, user_agent: str) -> AuthResult:
        """
        Authenticate officer with comprehensive security checks
        """
        try:
            # 1. Validate officer exists and is active
            officer = await self.db.get_officer_by_id(credentials.officer_id)
            if not officer or not officer.get('active', False):
                self.audit_logger.log_authentication_attempt(
                    credentials.officer_id, False, ip_address, user_agent, 
                    "Officer not found or inactive"
                )
                return AuthResult(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # 2. Verify password
            if not self.password_manager.verify_password(
                credentials.password, officer['password_hash']
            ):
                self.audit_logger.log_authentication_attempt(
                    credentials.officer_id, False, ip_address, user_agent,
                    "Invalid password"
                )
                return AuthResult(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # 3. Check if password change is required
            password_age = datetime.utcnow() - officer.get('password_changed_at', datetime.min)
            if password_age > timedelta(days=90):  # 90-day password policy
                return AuthResult(
                    success=False,
                    requires_password_change=True,
                    error_message="Password change required"
                )
            
            # 4. Check if MFA is required
            if officer.get('mfa_enabled', False):
                mfa_token = self._generate_mfa_token(credentials.officer_id)
                return AuthResult(
                    success=False,
                    mfa_required=True,
                    mfa_token=mfa_token,
                    error_message="MFA verification required"
                )
            
            # 5. Create secure session
            role = UserRole(officer['role'])
            session = self.session_manager.create_session(
                credentials.officer_id, role, ip_address, user_agent
            )
            
            # 6. Generate JWT token
            jwt_token = self._generate_jwt_token(session)
            
            # 7. Log successful authentication
            self.audit_logger.log_authentication_attempt(
                credentials.officer_id, True, ip_address, user_agent
            )
            
            return AuthResult(
                success=True,
                officer_id=credentials.officer_id,
                session_token=jwt_token,
                permissions=session.permissions
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            self.audit_logger.log_authentication_attempt(
                credentials.officer_id, False, ip_address, user_agent,
                f"System error: {str(e)}"
            )
            return AuthResult(
                success=False,
                error_message="Authentication system error"
            )
    
    async def verify_mfa_token(self, mfa_token: str, totp_code: str, 
                             ip_address: str, user_agent: str) -> AuthResult:
        """Verify MFA token and complete authentication"""
        try:
            # Decode MFA token to get officer ID
            officer_id = self._decode_mfa_token(mfa_token)
            if not officer_id:
                return AuthResult(
                    success=False,
                    error_message="Invalid MFA token"
                )
            
            # Get officer MFA secret
            officer = await self.db.get_officer_by_id(officer_id)
            if not officer or not officer.get('mfa_secret'):
                return AuthResult(
                    success=False,
                    error_message="MFA not configured"
                )
            
            # Verify TOTP code
            if not self.mfa_provider.verify_totp_token(officer['mfa_secret'], totp_code):
                self.audit_logger.log_authentication_attempt(
                    officer_id, False, ip_address, user_agent,
                    "Invalid MFA code"
                )
                return AuthResult(
                    success=False,
                    error_message="Invalid MFA code"
                )
            
            # Create secure session
            role = UserRole(officer['role'])
            session = self.session_manager.create_session(
                officer_id, role, ip_address, user_agent
            )
            session.mfa_verified = True
            
            # Generate JWT token
            jwt_token = self._generate_jwt_token(session)
            
            # Log successful MFA authentication
            self.audit_logger.log_authentication_attempt(
                officer_id, True, ip_address, user_agent, "MFA verified"
            )
            
            return AuthResult(
                success=True,
                officer_id=officer_id,
                session_token=jwt_token,
                permissions=session.permissions
            )
            
        except Exception as e:
            logger.error(f"MFA verification error: {str(e)}")
            return AuthResult(
                success=False,
                error_message="MFA verification error"
            )
    
    def validate_session_token(self, token: str, ip_address: str) -> Optional[SecureSession]:
        """Validate JWT session token"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            session_id = payload.get('session_id')
            
            if not session_id:
                return None
            
            # Validate session
            session = self.session_manager.validate_session(session_id, ip_address)
            return session
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    def check_permission(self, session: SecureSession, permission: Permission, 
                        resource: str = "") -> bool:
        """Check if session has required permission"""
        granted = self.rbac_service.validate_action(session, permission)
        
        self.audit_logger.log_permission_check(
            session.officer_id, permission.value, granted, resource
        )
        
        return granted
    
    def logout(self, session_id: str, ip_address: str):
        """Secure logout"""
        session = self.sessions.get(session_id)
        if session:
            self.audit_logger.log_session_event(
                session.officer_id, "LOGOUT", session_id, ip_address
            )
            self.session_manager.destroy_session(session_id)
    
    def _generate_jwt_token(self, session: SecureSession) -> str:
        """Generate JWT token for session"""
        payload = {
            'session_id': session.session_id,
            'officer_id': session.officer_id,
            'role': session.role.value,
            'permissions': [p.value for p in session.permissions],
            'exp': datetime.utcnow() + self.jwt_expiration,
            'iat': datetime.utcnow(),
            'mfa_verified': session.mfa_verified
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _generate_mfa_token(self, officer_id: str) -> str:
        """Generate temporary MFA token"""
        payload = {
            'officer_id': officer_id,
            'type': 'mfa',
            'exp': datetime.utcnow() + timedelta(minutes=5)  # 5-minute expiration
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _decode_mfa_token(self, token: str) -> Optional[str]:
        """Decode MFA token to get officer ID"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            if payload.get('type') == 'mfa':
                return payload.get('officer_id')
        except jwt.InvalidTokenError:
            pass
        return None

# Example usage and testing
async def main():
    """Example usage of the secure authentication system"""
    
    # Mock database service (replace with actual implementation)
    class MockDatabaseService:
        async def get_officer_by_id(self, officer_id: str):
            # Mock officer data
            return {
                'officer_id': officer_id,
                'badge_number': 'BADGE123',
                'password_hash': SecurePasswordManager.hash_password(os.getenv('ADMIN_PASSWORD', 'ChangeMe123!')),
                'role': 'investigator',
                'active': True,
                'mfa_enabled': True,
                'mfa_secret': 'JBSWY3DPEHPK3PXP',
                'password_changed_at': datetime.utcnow() - timedelta(days=30)
            }
    
    # Initialize authentication service
    db_service = MockDatabaseService()
    secret_key = secrets.token_urlsafe(32)
    auth_service = SecureAuthenticationService(db_service, secret_key)
    
    # Test authentication
    credentials = OfficerCredentials(
        officer_id="officer123",
        badge_number="BADGE123",
        password=os.getenv('ADMIN_PASSWORD', 'ChangeMe123!'),
        department="Cyber Crime",
        state="Delhi"
    )
    
    result = await auth_service.authenticate_officer(
        credentials, "192.168.1.100", "Mozilla/5.0..."
    )
    
    print(f"Authentication result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
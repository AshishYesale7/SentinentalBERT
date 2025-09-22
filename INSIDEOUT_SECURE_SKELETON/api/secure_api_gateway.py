"""
InsideOut Platform - Secure API Gateway
Implements secure API endpoints with authentication, authorization, and rate limiting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import secrets
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
from cryptography.fernet import Fernet
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our secure services
from auth.secure_authentication import SecureAuthenticationService, SecureSession, Permission
from legal.legal_compliance_system import LegalAuthorityVerificationService, WarrantData, SearchParameters
from evidence.evidence_management import EvidenceCollectionService, EvidencePackage
from analysis.secure_bert_engine import SecureBERTAnalysisEngine, AnalysisScope, SocialMediaPost

class APIEndpoint(Enum):
    """API endpoint categories"""
    AUTHENTICATION = "authentication"
    LEGAL_COMPLIANCE = "legal_compliance"
    EVIDENCE_MANAGEMENT = "evidence_management"
    CONTENT_ANALYSIS = "content_analysis"
    REPORTING = "reporting"
    SYSTEM_ADMIN = "system_admin"

# Pydantic models for API requests/responses
class AuthenticationRequest(BaseModel):
    officer_id: str = Field(..., min_length=3, max_length=50)
    badge_number: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    department: str = Field(..., max_length=255)
    state: str = Field(..., max_length=100)

class MFAVerificationRequest(BaseModel):
    mfa_token: str = Field(..., min_length=10)
    totp_code: str = Field(..., min_length=6, max_length=6)

class AuthenticationResponse(BaseModel):
    success: bool
    session_token: Optional[str] = None
    mfa_required: bool = False
    mfa_token: Optional[str] = None
    permissions: List[str] = []
    error_message: Optional[str] = None

class WarrantVerificationRequest(BaseModel):
    warrant_id: str = Field(..., min_length=5, max_length=100)
    case_number: str = Field(..., min_length=5, max_length=100)
    court_name: str = Field(..., max_length=255)
    judge_name: str = Field(..., max_length=255)
    issuing_date: datetime
    expiration_date: datetime
    probable_cause: str = Field(..., min_length=50)

class SearchRequest(BaseModel):
    warrant_id: str = Field(..., min_length=5, max_length=100)
    keywords: List[str] = Field(..., min_items=1, max_items=20)
    platforms: List[str] = Field(..., min_items=1, max_items=10)
    geographic_bounds: Dict[str, Any]
    temporal_bounds: Dict[str, Any]
    content_types: List[str] = Field(default=['posts'])

class EvidenceCollectionRequest(BaseModel):
    warrant_id: str = Field(..., min_length=5, max_length=100)
    case_number: str = Field(..., min_length=5, max_length=100)
    platform: str = Field(..., max_length=50)
    content_urls: List[str] = Field(..., min_items=1, max_items=100)

class AnalysisRequest(BaseModel):
    warrant_id: str = Field(..., min_length=5, max_length=100)
    evidence_ids: List[str] = Field(..., min_items=1, max_items=1000)
    analysis_types: List[str] = Field(default=['pattern_detection'])
    geographic_scope: Dict[str, Any]
    temporal_scope: Dict[str, Any]

class ComplianceResponse(BaseModel):
    compliant: bool
    violations: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []
    legal_review_required: bool = False

class EvidenceResponse(BaseModel):
    evidence_id: str
    status: str
    collected_at: datetime
    court_admissible: bool
    chain_of_custody_entries: int

class AnalysisResponse(BaseModel):
    analysis_id: str
    patterns_detected: int
    confidence_score: float
    geographic_clusters: int
    temporal_patterns: int
    legal_compliance: Dict[str, bool]

class RateLimiter:
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
        # Rate limits by endpoint and user role
        self.rate_limits = {
            'authentication': {'requests': 10, 'window': 300},  # 10 per 5 minutes
            'search': {'requests': 100, 'window': 3600},        # 100 per hour
            'analysis': {'requests': 50, 'window': 3600},       # 50 per hour
            'evidence': {'requests': 200, 'window': 3600},      # 200 per hour
            'admin': {'requests': 1000, 'window': 3600}         # 1000 per hour for admins
        }
    
    async def check_rate_limit(self, key: str, endpoint: str, user_role: str = 'user') -> bool:
        """Check if request is within rate limits"""
        # Determine rate limit based on endpoint and role
        if user_role == 'admin':
            limit_config = self.rate_limits.get('admin')
        else:
            limit_config = self.rate_limits.get(endpoint, {'requests': 60, 'window': 3600})
        
        rate_key = f"rate_limit:{key}:{endpoint}"
        
        # Get current count
        current = await self.redis.get(rate_key)
        if current is None:
            # First request in window
            await self.redis.setex(rate_key, limit_config['window'], 1)
            return True
        
        current_count = int(current)
        if current_count >= limit_config['requests']:
            return False
        
        # Increment counter
        await self.redis.incr(rate_key)
        return True

class SecurityMiddleware:
    """Security middleware for request validation and logging"""
    
    def __init__(self, auth_service: SecureAuthenticationService):
        self.auth_service = auth_service
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'union\s+select',
            r'drop\s+table',
            r'exec\s*\(',
            r'system\s*\('
        ]
    
    async def validate_request(self, request: Request) -> Dict[str, Any]:
        """Validate incoming request for security threats"""
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        
        # Check blocked IPs
        if client_ip in self.blocked_ips:
            raise HTTPException(status_code=403, detail="IP address blocked")
        
        # Check for suspicious patterns in request
        request_body = await request.body()
        request_str = str(request_body) + str(request.query_params) + user_agent
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, request_str, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected from {client_ip}: {pattern}")
                # Could implement automatic IP blocking here
                raise HTTPException(status_code=400, detail="Invalid request")
        
        return {
            'client_ip': client_ip,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow()
        }

class SecureAPIGateway:
    """Main API Gateway with comprehensive security"""
    
    def __init__(self, 
                 auth_service: SecureAuthenticationService,
                 legal_service: LegalAuthorityVerificationService,
                 evidence_service: EvidenceCollectionService,
                 analysis_engine: SecureBERTAnalysisEngine,
                 redis_url: str = "redis://localhost:6379"):
        
        self.auth_service = auth_service
        self.legal_service = legal_service
        self.evidence_service = evidence_service
        self.analysis_engine = analysis_engine
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="InsideOut Platform API",
            description="Secure API for law enforcement social media analysis",
            version="1.0.0",
            docs_url=None,  # Disable docs in production
            redoc_url=None  # Disable redoc in production
        )
        
        # Initialize Redis for rate limiting and caching
        self.redis = redis.from_url(redis_url)
        self.rate_limiter = RateLimiter(self.redis)
        
        # Initialize security middleware
        self.security_middleware = SecurityMiddleware(auth_service)
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Setup security headers
        self._setup_security_headers()
    
    def _setup_middleware(self):
        """Setup security middleware"""
        
        # CORS middleware (restrictive for production)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://insideout.gov.in"],  # Only allow official domain
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["insideout.gov.in", "*.insideout.gov.in"]
        )
        
        # Custom security middleware
        @self.app.middleware("http")
        async def security_middleware(request: Request, call_next):
            # Validate request security
            security_info = await self.security_middleware.validate_request(request)
            
            # Add security headers
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
            
            return response
    
    def _setup_security_headers(self):
        """Setup additional security headers"""
        
        @self.app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            
            # Remove server information
            if "server" in response.headers:
                del response.headers["server"]
            
            # Add custom security headers
            response.headers["X-API-Version"] = "1.0.0"
            response.headers["X-Rate-Limit-Policy"] = "Enforced"
            
            return response
    
    async def get_current_session(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> SecureSession:
        """Dependency to get current authenticated session"""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Extract IP from request (would need request context)
        client_ip = "127.0.0.1"  # Placeholder - get from request context
        
        session = self.auth_service.validate_session_token(credentials.credentials, client_ip)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        return session
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission"""
        def permission_checker(session: SecureSession = Depends(self.get_current_session)):
            if not self.auth_service.check_permission(session, permission):
                raise HTTPException(status_code=403, detail=f"Permission required: {permission.value}")
            return session
        return permission_checker
    
    async def check_rate_limit(self, request: Request, endpoint: str, session: SecureSession):
        """Check rate limits for request"""
        client_ip = request.client.host
        rate_key = f"{session.officer_id}:{client_ip}"
        
        if not await self.rate_limiter.check_rate_limit(rate_key, endpoint, session.role.value):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Authentication endpoints
        @self.app.post("/api/v1/auth/login", response_model=AuthenticationResponse)
        async def login(request: Request, auth_request: AuthenticationRequest):
            """Authenticate officer and create session"""
            await self.check_rate_limit(request, 'authentication', None)
            
            from auth.secure_authentication import OfficerCredentials
            credentials = OfficerCredentials(
                officer_id=auth_request.officer_id,
                badge_number=auth_request.badge_number,
                password=auth_request.password,
                department=auth_request.department,
                state=auth_request.state
            )
            
            result = await self.auth_service.authenticate_officer(
                credentials, request.client.host, request.headers.get('user-agent', '')
            )
            
            return AuthenticationResponse(
                success=result.success,
                session_token=result.session_token,
                mfa_required=result.mfa_required,
                mfa_token=result.mfa_token,
                permissions=[p.value for p in result.permissions] if result.permissions else [],
                error_message=result.error_message
            )
        
        @self.app.post("/api/v1/auth/mfa-verify", response_model=AuthenticationResponse)
        async def verify_mfa(request: Request, mfa_request: MFAVerificationRequest):
            """Verify MFA token and complete authentication"""
            await self.check_rate_limit(request, 'authentication', None)
            
            result = await self.auth_service.verify_mfa_token(
                mfa_request.mfa_token,
                mfa_request.totp_code,
                request.client.host,
                request.headers.get('user-agent', '')
            )
            
            return AuthenticationResponse(
                success=result.success,
                session_token=result.session_token,
                permissions=[p.value for p in result.permissions] if result.permissions else [],
                error_message=result.error_message
            )
        
        @self.app.post("/api/v1/auth/logout")
        async def logout(session: SecureSession = Depends(self.get_current_session)):
            """Logout and destroy session"""
            self.auth_service.logout(session.session_id, session.ip_address)
            return {"message": "Logged out successfully"}
        
        # Legal compliance endpoints
        @self.app.post("/api/v1/legal/verify-warrant", response_model=ComplianceResponse)
        async def verify_warrant(
            request: Request,
            warrant_request: WarrantVerificationRequest,
            session: SecureSession = Depends(self.require_permission(Permission.APPROVE_WARRANTS))
        ):
            """Verify warrant authority and compliance"""
            await self.check_rate_limit(request, 'legal', session)
            
            # Convert request to WarrantData (simplified)
            from legal.legal_compliance_system import WarrantData, WarrantType, JurisdictionLevel, GeographicBounds, TemporalBounds, PlatformScope, ConstitutionalRight
            
            warrant = WarrantData(
                warrant_id=warrant_request.warrant_id,
                warrant_type=WarrantType.SEARCH_WARRANT,
                case_number=warrant_request.case_number,
                court_name=warrant_request.court_name,
                judge_name=warrant_request.judge_name,
                issuing_date=warrant_request.issuing_date,
                expiration_date=warrant_request.expiration_date,
                jurisdiction=JurisdictionLevel.DISTRICT,
                geographic_scope=GeographicBounds(country="India"),
                temporal_scope=TemporalBounds(
                    start_date=warrant_request.issuing_date,
                    end_date=warrant_request.expiration_date
                ),
                platform_scope=PlatformScope(
                    platforms=['twitter', 'facebook'],
                    account_types=['public'],
                    content_types=['posts']
                ),
                probable_cause=warrant_request.probable_cause,
                legal_basis="Criminal investigation",
                constitutional_considerations=[ConstitutionalRight.FOURTH_AMENDMENT]
            )
            
            result = await self.legal_service.verify_warrant_authority(warrant)
            
            return ComplianceResponse(
                compliant=result.compliant,
                violations=result.violations,
                warnings=result.warnings,
                recommendations=result.recommendations,
                legal_review_required=result.legal_review_required
            )
        
        @self.app.post("/api/v1/legal/validate-search", response_model=ComplianceResponse)
        async def validate_search(
            request: Request,
            search_request: SearchRequest,
            session: SecureSession = Depends(self.require_permission(Permission.ANALYZE_CONTENT))
        ):
            """Validate search parameters against warrant scope"""
            await self.check_rate_limit(request, 'search', session)
            
            # This would validate search parameters against warrant
            # Simplified implementation
            return ComplianceResponse(
                compliant=True,
                violations=[],
                warnings=[],
                recommendations=[]
            )
        
        # Evidence management endpoints
        @self.app.post("/api/v1/evidence/collect", response_model=List[EvidenceResponse])
        async def collect_evidence(
            request: Request,
            collection_request: EvidenceCollectionRequest,
            session: SecureSession = Depends(self.require_permission(Permission.ACCESS_EVIDENCE))
        ):
            """Collect social media evidence"""
            await self.check_rate_limit(request, 'evidence', session)
            
            evidence_responses = []
            
            for url in collection_request.content_urls:
                # This would actually collect the content from the URL
                # For now, create mock evidence
                sample_data = f"Mock content from {url}".encode()
                
                officer_info = {
                    'officer_id': session.officer_id,
                    'name': 'Officer Name',  # Would get from session
                    'badge_number': 'BADGE123',  # Would get from session
                    'location': 'Police HQ'
                }
                
                evidence = await self.evidence_service.collect_social_media_evidence(
                    platform=collection_request.platform,
                    content_url=url,
                    raw_data=sample_data,
                    platform_metadata={'url': url, 'collected_at': datetime.utcnow().isoformat()},
                    warrant_id=collection_request.warrant_id,
                    case_number=collection_request.case_number,
                    collecting_officer=officer_info
                )
                
                evidence_responses.append(EvidenceResponse(
                    evidence_id=evidence.evidence_id,
                    status=evidence.status.value,
                    collected_at=evidence.collected_at,
                    court_admissible=evidence.court_admissible,
                    chain_of_custody_entries=len(evidence.chain_of_custody)
                ))
            
            return evidence_responses
        
        @self.app.get("/api/v1/evidence/{evidence_id}")
        async def get_evidence(
            evidence_id: str,
            session: SecureSession = Depends(self.require_permission(Permission.ACCESS_EVIDENCE))
        ):
            """Get evidence details"""
            # This would retrieve evidence from database
            return {"evidence_id": evidence_id, "status": "retrieved"}
        
        # Content analysis endpoints
        @self.app.post("/api/v1/analysis/patterns", response_model=AnalysisResponse)
        async def analyze_patterns(
            request: Request,
            analysis_request: AnalysisRequest,
            session: SecureSession = Depends(self.require_permission(Permission.ANALYZE_CONTENT))
        ):
            """Analyze content patterns using BERT"""
            await self.check_rate_limit(request, 'analysis', session)
            
            # Create analysis scope
            analysis_scope = AnalysisScope(
                warrant_id=analysis_request.warrant_id,
                geographic_bounds=analysis_request.geographic_scope,
                temporal_bounds=analysis_request.temporal_scope,
                platform_scope=['twitter', 'facebook'],
                content_types=['posts'],
                keywords=[],
                legal_constraints=[]
            )
            
            # Mock posts for analysis (would retrieve from evidence)
            mock_posts = [
                SocialMediaPost(
                    post_id=f"post_{i}",
                    platform="twitter",
                    author_id=f"user_{i}",
                    author_username=f"@user{i}",
                    content=f"Sample content {i}",
                    timestamp=datetime.utcnow() - timedelta(hours=i),
                    location={'lat': 28.6139, 'lng': 77.2090},
                    engagement={'likes': i*10, 'shares': i*5, 'comments': i*2}
                )
                for i in range(5)
            ]
            
            result = await self.analysis_engine.analyze_content_patterns(
                mock_posts, analysis_scope, session.officer_id
            )
            
            return AnalysisResponse(
                analysis_id=result.analysis_id,
                patterns_detected=len(result.patterns),
                confidence_score=result.confidence_scores.get('overall', 0.0),
                geographic_clusters=len(result.geographic_clusters),
                temporal_patterns=len(result.temporal_patterns),
                legal_compliance=result.legal_compliance
            )
        
        # Health check endpoint
        @self.app.get("/api/v1/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # System admin endpoints
        @self.app.get("/api/v1/admin/stats")
        async def get_system_stats(
            session: SecureSession = Depends(self.require_permission(Permission.SYSTEM_ADMIN))
        ):
            """Get system statistics"""
            return {
                "active_sessions": len(self.auth_service.session_manager.sessions),
                "total_requests": "N/A",  # Would track in Redis
                "system_health": "healthy"
            }
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the secure API server"""
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            ssl_keyfile="/etc/ssl/private/insideout.key",  # SSL certificate
            ssl_certfile="/etc/ssl/certs/insideout.crt",
            ssl_version=3,  # TLS 1.3
            access_log=True,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()

# Example usage
async def main():
    """Example usage of secure API gateway"""
    
    # Initialize services (mock implementations)
    class MockDatabaseService:
        async def get_officer_by_id(self, officer_id: str):
            return {
                'officer_id': officer_id,
                'password_hash': 'hashed_password',
                'role': 'investigator',
                'active': True,
                'mfa_enabled': False
            }
    
    # Initialize services
    from auth.secure_authentication import SecureAuthenticationService
    from legal.legal_compliance_system import LegalAuthorityVerificationService
    from evidence.evidence_management import EvidenceCollectionService, EncryptionService, DigitalSignatureService, ChainOfCustodyService, BlockchainService
    from analysis.secure_bert_engine import SecureBERTAnalysisEngine
    
    db_service = MockDatabaseService()
    secret_key = secrets.token_urlsafe(32)
    
    auth_service = SecureAuthenticationService(db_service, secret_key)
    legal_service = LegalAuthorityVerificationService("http://court-api", "api-key")
    
    # Initialize evidence service components
    master_key = b"secure_master_key_32_bytes_long!!"
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
    
    blockchain_service = BlockchainService("http://localhost:8545", "0x123", "0xkey")
    custody_service = ChainOfCustodyService(signature_service, blockchain_service)
    evidence_service = EvidenceCollectionService(encryption_service, signature_service, custody_service)
    
    analysis_engine = SecureBERTAnalysisEngine()
    
    # Initialize API gateway
    api_gateway = SecureAPIGateway(
        auth_service=auth_service,
        legal_service=legal_service,
        evidence_service=evidence_service,
        analysis_engine=analysis_engine
    )
    
    # Start server
    logger.info("Starting InsideOut Platform API Gateway")
    await api_gateway.start_server()

if __name__ == "__main__":
    asyncio.run(main())
"""
InsideOut Platform - Legal Compliance System
Implements warrant verification, constitutional compliance, and evidence standards
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import aiohttp
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WarrantType(Enum):
    """Types of legal warrants"""
    SEARCH_WARRANT = "search_warrant"
    SURVEILLANCE_ORDER = "surveillance_order"
    SUBPOENA = "subpoena"
    COURT_ORDER = "court_order"
    EMERGENCY_ORDER = "emergency_order"

class JurisdictionLevel(Enum):
    """Jurisdiction levels for legal authority"""
    FEDERAL = "federal"
    STATE = "state"
    DISTRICT = "district"
    LOCAL = "local"

class ConstitutionalRight(Enum):
    """Constitutional rights that must be protected"""
    FOURTH_AMENDMENT = "fourth_amendment"  # Search and seizure
    FIRST_AMENDMENT = "first_amendment"    # Free speech
    FIFTH_AMENDMENT = "fifth_amendment"    # Due process
    FOURTEENTH_AMENDMENT = "fourteenth_amendment"  # Equal protection

class ComplianceStatus(Enum):
    """Compliance check status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_REVIEW = "requires_review"
    PENDING_APPROVAL = "pending_approval"

@dataclass
class GeographicBounds:
    """Geographic boundaries for warrant scope"""
    country: str
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[Dict] = None  # Lat/lng bounds
    radius_km: Optional[float] = None

@dataclass
class TemporalBounds:
    """Temporal boundaries for warrant scope"""
    start_date: datetime
    end_date: datetime
    timezone: str = "UTC"

@dataclass
class PlatformScope:
    """Social media platforms covered by warrant"""
    platforms: List[str]  # e.g., ['twitter', 'facebook', 'instagram']
    account_types: List[str]  # e.g., ['public', 'private']
    content_types: List[str]  # e.g., ['posts', 'messages', 'media']

@dataclass
class WarrantData:
    """Complete warrant information"""
    warrant_id: str
    warrant_type: WarrantType
    case_number: str
    court_name: str
    judge_name: str
    issuing_date: datetime
    expiration_date: datetime
    jurisdiction: JurisdictionLevel
    
    # Scope limitations
    geographic_scope: GeographicBounds
    temporal_scope: TemporalBounds
    platform_scope: PlatformScope
    
    # Legal basis
    probable_cause: str
    legal_basis: str
    constitutional_considerations: List[ConstitutionalRight]
    
    # Digital signature for authenticity
    digital_signature: Optional[str] = None
    court_seal: Optional[str] = None
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class SearchParameters:
    """Parameters for social media search"""
    keywords: List[str]
    hashtags: List[str]
    user_accounts: List[str]
    geographic_area: GeographicBounds
    time_range: TemporalBounds
    platforms: List[str]
    content_types: List[str]

@dataclass
class ComplianceResult:
    """Result of compliance check"""
    status: ComplianceStatus
    compliant: bool
    violations: List[str]
    warnings: List[str]
    recommendations: List[str]
    legal_review_required: bool = False
    approval_required: bool = False

@dataclass
class EvidenceMetadata:
    """Metadata for collected evidence"""
    evidence_id: str
    warrant_id: str
    collection_timestamp: datetime
    platform: str
    content_type: str
    original_url: str
    content_hash: str
    chain_of_custody: List[Dict]
    legal_holds: List[str]

class CourtSystemAPI:
    """Interface to court system for warrant verification"""
    
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def verify_warrant(self, warrant_id: str) -> Dict:
        """Verify warrant with court system"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                f"{self.api_endpoint}/warrants/{warrant_id}/verify",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Court API error: {response.status}")
                    return {'valid': False, 'error': 'Court system unavailable'}
                    
        except Exception as e:
            logger.error(f"Court API connection error: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    async def check_warrant_status(self, warrant_id: str) -> Dict:
        """Check current status of warrant"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(
                f"{self.api_endpoint}/warrants/{warrant_id}/status",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {'status': 'unknown', 'error': 'Status check failed'}
                    
        except Exception as e:
            logger.error(f"Warrant status check error: {str(e)}")
            return {'status': 'unknown', 'error': str(e)}

class ConstitutionalComplianceChecker:
    """Checks for constitutional compliance"""
    
    def __init__(self):
        self.protected_speech_keywords = [
            'protest', 'demonstration', 'political', 'religion', 'opinion',
            'criticism', 'dissent', 'activism', 'petition', 'assembly'
        ]
    
    async def check_fourth_amendment_compliance(self, 
                                              warrant: WarrantData,
                                              search_params: SearchParameters) -> ComplianceResult:
        """Check Fourth Amendment (search and seizure) compliance"""
        violations = []
        warnings = []
        recommendations = []
        
        # Check if warrant exists and is valid
        if not warrant:
            violations.append("No warrant provided for search")
        
        # Check warrant expiration
        if warrant and datetime.utcnow() > warrant.expiration_date:
            violations.append("Warrant has expired")
        
        # Check geographic scope
        if not self._is_search_within_geographic_scope(search_params.geographic_area, 
                                                      warrant.geographic_scope):
            violations.append("Search exceeds warrant geographic scope")
        
        # Check temporal scope
        if not self._is_search_within_temporal_scope(search_params.time_range,
                                                    warrant.temporal_scope):
            violations.append("Search exceeds warrant temporal scope")
        
        # Check platform scope
        if not self._is_search_within_platform_scope(search_params.platforms,
                                                    warrant.platform_scope):
            violations.append("Search exceeds warrant platform scope")
        
        # Check for overly broad search
        if self._is_search_overly_broad(search_params):
            warnings.append("Search parameters may be overly broad")
            recommendations.append("Consider narrowing search parameters")
        
        # Check probable cause documentation
        if not warrant.probable_cause or len(warrant.probable_cause.strip()) < 50:
            violations.append("Insufficient probable cause documentation")
        
        return ComplianceResult(
            status=ComplianceStatus.COMPLIANT if not violations else ComplianceStatus.NON_COMPLIANT,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            legal_review_required=len(warnings) > 0
        )
    
    async def check_first_amendment_compliance(self, 
                                             content: str,
                                             search_params: SearchParameters) -> ComplianceResult:
        """Check First Amendment (free speech) compliance"""
        violations = []
        warnings = []
        recommendations = []
        
        # Check for protected speech content
        content_lower = content.lower()
        protected_speech_found = any(
            keyword in content_lower for keyword in self.protected_speech_keywords
        )
        
        if protected_speech_found:
            warnings.append("Content may contain protected political/religious speech")
            recommendations.append("Ensure collection is narrowly tailored to criminal activity")
        
        # Check for broad keyword searches that might chill speech
        broad_keywords = ['government', 'police', 'politics', 'religion', 'protest']
        if any(keyword in search_params.keywords for keyword in broad_keywords):
            warnings.append("Search keywords may capture protected speech")
            recommendations.append("Use more specific keywords related to criminal activity")
        
        # Check for targeting based on viewpoint
        political_keywords = ['democrat', 'republican', 'liberal', 'conservative']
        if any(keyword in search_params.keywords for keyword in political_keywords):
            violations.append("Search appears to target specific political viewpoints")
        
        return ComplianceResult(
            status=ComplianceStatus.REQUIRES_REVIEW if warnings else ComplianceStatus.COMPLIANT,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            legal_review_required=True if warnings or violations else False
        )
    
    def _is_search_within_geographic_scope(self, search_area: GeographicBounds, 
                                         warrant_scope: GeographicBounds) -> bool:
        """Check if search is within warrant geographic scope"""
        # Country level check
        if search_area.country != warrant_scope.country:
            return False
        
        # State level check
        if warrant_scope.state and search_area.state != warrant_scope.state:
            return False
        
        # District level check
        if warrant_scope.district and search_area.district != warrant_scope.district:
            return False
        
        # City level check
        if warrant_scope.city and search_area.city != warrant_scope.city:
            return False
        
        # Coordinate bounds check (if specified)
        if warrant_scope.coordinates and search_area.coordinates:
            return self._check_coordinate_bounds(search_area.coordinates, 
                                               warrant_scope.coordinates)
        
        return True
    
    def _is_search_within_temporal_scope(self, search_time: TemporalBounds,
                                       warrant_scope: TemporalBounds) -> bool:
        """Check if search is within warrant temporal scope"""
        return (search_time.start_date >= warrant_scope.start_date and
                search_time.end_date <= warrant_scope.end_date)
    
    def _is_search_within_platform_scope(self, search_platforms: List[str],
                                       warrant_scope: PlatformScope) -> bool:
        """Check if search platforms are within warrant scope"""
        return all(platform in warrant_scope.platforms for platform in search_platforms)
    
    def _is_search_overly_broad(self, search_params: SearchParameters) -> bool:
        """Check if search parameters are overly broad"""
        # Check for very generic keywords
        generic_keywords = ['the', 'and', 'or', 'a', 'an', 'is', 'are']
        if any(keyword in search_params.keywords for keyword in generic_keywords):
            return True
        
        # Check for very long time ranges (more than 1 year)
        time_range = search_params.time_range.end_date - search_params.time_range.start_date
        if time_range > timedelta(days=365):
            return True
        
        # Check for too many platforms
        if len(search_params.platforms) > 5:
            return True
        
        return False
    
    def _check_coordinate_bounds(self, search_coords: Dict, warrant_coords: Dict) -> bool:
        """Check if search coordinates are within warrant bounds"""
        # Simple bounding box check
        return (search_coords['min_lat'] >= warrant_coords['min_lat'] and
                search_coords['max_lat'] <= warrant_coords['max_lat'] and
                search_coords['min_lng'] >= warrant_coords['min_lng'] and
                search_coords['max_lng'] <= warrant_coords['max_lng'])

class GDPRComplianceChecker:
    """GDPR and privacy compliance checker"""
    
    def __init__(self):
        self.sensitive_data_categories = [
            'racial_origin', 'political_opinions', 'religious_beliefs',
            'trade_union_membership', 'genetic_data', 'biometric_data',
            'health_data', 'sex_life', 'sexual_orientation'
        ]
    
    async def check_data_minimization(self, 
                                    collected_data: Dict,
                                    warrant_scope: WarrantData) -> ComplianceResult:
        """Check GDPR data minimization compliance"""
        violations = []
        warnings = []
        recommendations = []
        
        # Check if data collection is limited to warrant scope
        if not self._is_data_relevant_to_investigation(collected_data, warrant_scope):
            violations.append("Collected data exceeds investigation scope")
        
        # Check for sensitive personal data
        sensitive_data_found = self._detect_sensitive_data(collected_data)
        if sensitive_data_found:
            warnings.append(f"Sensitive personal data detected: {', '.join(sensitive_data_found)}")
            recommendations.append("Implement additional safeguards for sensitive data")
        
        # Check retention period
        if not self._has_appropriate_retention_policy(warrant_scope):
            violations.append("No appropriate data retention policy specified")
        
        return ComplianceResult(
            status=ComplianceStatus.COMPLIANT if not violations else ComplianceStatus.NON_COMPLIANT,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            legal_review_required=len(sensitive_data_found) > 0
        )
    
    def _is_data_relevant_to_investigation(self, data: Dict, warrant: WarrantData) -> bool:
        """Check if collected data is relevant to investigation"""
        # This would implement logic to check data relevance
        # For now, return True as placeholder
        return True
    
    def _detect_sensitive_data(self, data: Dict) -> List[str]:
        """Detect sensitive personal data categories"""
        detected = []
        data_str = json.dumps(data).lower()
        
        # Simple keyword detection (would be more sophisticated in practice)
        if any(word in data_str for word in ['race', 'ethnicity', 'racial']):
            detected.append('racial_origin')
        if any(word in data_str for word in ['political', 'democrat', 'republican']):
            detected.append('political_opinions')
        if any(word in data_str for word in ['religion', 'christian', 'muslim', 'jewish']):
            detected.append('religious_beliefs')
        if any(word in data_str for word in ['health', 'medical', 'disease']):
            detected.append('health_data')
        
        return detected
    
    def _has_appropriate_retention_policy(self, warrant: WarrantData) -> bool:
        """Check if appropriate retention policy is specified"""
        # Check if warrant specifies retention period
        return hasattr(warrant, 'retention_period') and warrant.retention_period is not None

class LegalAuthorityVerificationService:
    """Service to verify legal authority for data collection"""
    
    def __init__(self, court_api_endpoint: str, court_api_key: str):
        self.court_api = CourtSystemAPI(court_api_endpoint, court_api_key)
        self.constitutional_checker = ConstitutionalComplianceChecker()
        self.gdpr_checker = GDPRComplianceChecker()
        
        # Digital signature verification
        self.court_public_keys = {}  # Would load from secure key store
    
    async def verify_warrant_authority(self, warrant: WarrantData) -> ComplianceResult:
        """Comprehensive warrant authority verification"""
        violations = []
        warnings = []
        recommendations = []
        
        async with self.court_api as court:
            # 1. Verify warrant with court system
            court_verification = await court.verify_warrant(warrant.warrant_id)
            if not court_verification.get('valid', False):
                violations.append(f"Warrant verification failed: {court_verification.get('error', 'Unknown error')}")
            
            # 2. Check warrant status
            status_check = await court.check_warrant_status(warrant.warrant_id)
            if status_check.get('status') not in ['active', 'valid']:
                violations.append(f"Warrant status invalid: {status_check.get('status', 'unknown')}")
            
            # 3. Verify digital signature
            if not self._verify_digital_signature(warrant):
                violations.append("Warrant digital signature verification failed")
            
            # 4. Check expiration
            if datetime.utcnow() > warrant.expiration_date:
                violations.append("Warrant has expired")
            
            # 5. Validate jurisdiction
            if not self._validate_jurisdiction(warrant):
                violations.append("Warrant jurisdiction validation failed")
        
        return ComplianceResult(
            status=ComplianceStatus.COMPLIANT if not violations else ComplianceStatus.NON_COMPLIANT,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    async def validate_search_compliance(self, 
                                       warrant: WarrantData,
                                       search_params: SearchParameters) -> ComplianceResult:
        """Validate search parameters against warrant and constitutional requirements"""
        
        # Check Fourth Amendment compliance
        fourth_amendment_result = await self.constitutional_checker.check_fourth_amendment_compliance(
            warrant, search_params
        )
        
        # Check First Amendment compliance (would need content for full check)
        first_amendment_result = await self.constitutional_checker.check_first_amendment_compliance(
            "", search_params  # Empty content for parameter check
        )
        
        # Combine results
        all_violations = fourth_amendment_result.violations + first_amendment_result.violations
        all_warnings = fourth_amendment_result.warnings + first_amendment_result.warnings
        all_recommendations = fourth_amendment_result.recommendations + first_amendment_result.recommendations
        
        overall_compliant = fourth_amendment_result.compliant and first_amendment_result.compliant
        legal_review_required = (fourth_amendment_result.legal_review_required or 
                               first_amendment_result.legal_review_required)
        
        return ComplianceResult(
            status=ComplianceStatus.COMPLIANT if overall_compliant else ComplianceStatus.NON_COMPLIANT,
            compliant=overall_compliant,
            violations=all_violations,
            warnings=all_warnings,
            recommendations=all_recommendations,
            legal_review_required=legal_review_required
        )
    
    async def validate_evidence_collection(self, 
                                         evidence_metadata: EvidenceMetadata,
                                         warrant: WarrantData) -> ComplianceResult:
        """Validate evidence collection compliance"""
        violations = []
        warnings = []
        recommendations = []
        
        # Check if evidence collection is within warrant scope
        if not self._is_evidence_within_scope(evidence_metadata, warrant):
            violations.append("Evidence collection exceeds warrant scope")
        
        # Check chain of custody
        if not evidence_metadata.chain_of_custody:
            violations.append("No chain of custody documentation")
        elif len(evidence_metadata.chain_of_custody) == 0:
            violations.append("Empty chain of custody")
        
        # Check evidence integrity
        if not evidence_metadata.content_hash:
            violations.append("No content hash for evidence integrity")
        
        # Check collection timestamp
        if evidence_metadata.collection_timestamp > datetime.utcnow():
            violations.append("Evidence collection timestamp is in the future")
        
        # Check if collection is within warrant time bounds
        if not (warrant.temporal_scope.start_date <= evidence_metadata.collection_timestamp <= warrant.temporal_scope.end_date):
            violations.append("Evidence collection outside warrant temporal scope")
        
        return ComplianceResult(
            status=ComplianceStatus.COMPLIANT if not violations else ComplianceStatus.NON_COMPLIANT,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def _verify_digital_signature(self, warrant: WarrantData) -> bool:
        """Verify warrant digital signature"""
        if not warrant.digital_signature:
            return False
        
        # In practice, this would verify the signature using the court's public key
        # For now, return True as placeholder
        return True
    
    def _validate_jurisdiction(self, warrant: WarrantData) -> bool:
        """Validate warrant jurisdiction"""
        # Check if jurisdiction level is appropriate for the case
        valid_jurisdictions = [JurisdictionLevel.FEDERAL, JurisdictionLevel.STATE, 
                             JurisdictionLevel.DISTRICT, JurisdictionLevel.LOCAL]
        return warrant.jurisdiction in valid_jurisdictions
    
    def _is_evidence_within_scope(self, evidence: EvidenceMetadata, warrant: WarrantData) -> bool:
        """Check if evidence is within warrant scope"""
        # Check platform scope
        if evidence.platform not in warrant.platform_scope.platforms:
            return False
        
        # Check content type scope
        if evidence.content_type not in warrant.platform_scope.content_types:
            return False
        
        # Additional scope checks would go here
        return True

# Example usage
async def main():
    """Example usage of legal compliance system"""
    
    # Create sample warrant
    warrant = WarrantData(
        warrant_id="WR-2024-001",
        warrant_type=WarrantType.SEARCH_WARRANT,
        case_number="CASE-2024-001",
        court_name="District Court of Delhi",
        judge_name="Justice Smith",
        issuing_date=datetime.utcnow() - timedelta(days=1),
        expiration_date=datetime.utcnow() + timedelta(days=30),
        jurisdiction=JurisdictionLevel.DISTRICT,
        geographic_scope=GeographicBounds(
            country="India",
            state="Delhi",
            district="Central Delhi"
        ),
        temporal_scope=TemporalBounds(
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        ),
        platform_scope=PlatformScope(
            platforms=["twitter", "facebook"],
            account_types=["public"],
            content_types=["posts", "comments"]
        ),
        probable_cause="Suspected terrorist activity based on intelligence reports",
        legal_basis="Prevention of Terrorism Act",
        constitutional_considerations=[ConstitutionalRight.FOURTH_AMENDMENT]
    )
    
    # Create search parameters
    search_params = SearchParameters(
        keywords=["terrorism", "bomb", "attack"],
        hashtags=["#terror"],
        user_accounts=["@suspect123"],
        geographic_area=GeographicBounds(country="India", state="Delhi"),
        time_range=TemporalBounds(
            start_date=datetime.utcnow() - timedelta(days=7),
            end_date=datetime.utcnow()
        ),
        platforms=["twitter"],
        content_types=["posts"]
    )
    
    # Initialize legal authority service
    legal_service = LegalAuthorityVerificationService(
        court_api_endpoint="https://court-api.gov.in",
        court_api_key="test-api-key"
    )
    
    # Verify warrant authority
    warrant_result = await legal_service.verify_warrant_authority(warrant)
    print(f"Warrant verification: {warrant_result}")
    
    # Validate search compliance
    search_result = await legal_service.validate_search_compliance(warrant, search_params)
    print(f"Search compliance: {search_result}")

if __name__ == "__main__":
    asyncio.run(main())
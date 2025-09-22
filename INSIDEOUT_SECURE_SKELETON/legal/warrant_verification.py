"""
InsideOut Platform - Warrant Verification System
Implements secure warrant validation and legal authority verification
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

logger = logging.getLogger(__name__)

class WarrantType(Enum):
    """Types of legal warrants supported"""
    SEARCH_WARRANT = "search_warrant"
    SURVEILLANCE_WARRANT = "surveillance_warrant"
    DATA_COLLECTION_WARRANT = "data_collection_warrant"
    EMERGENCY_ORDER = "emergency_order"

class WarrantStatus(Enum):
    """Warrant validation status"""
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    INVALID = "invalid"

@dataclass
class WarrantDetails:
    """Secure warrant information structure"""
    warrant_id: str
    warrant_type: WarrantType
    issuing_court: str
    judge_name: str
    case_number: str
    issued_date: datetime
    expiry_date: datetime
    scope: List[str]
    target_platforms: List[str]
    requesting_agency: str
    officer_badge: str
    digital_signature: str
    verification_hash: str

class WarrantVerificationSystem:
    """Secure warrant verification and validation system"""
    
    def __init__(self):
        self.encryption_key = self._load_or_generate_key()
        self.public_key = self._load_court_public_key()
        self.verified_warrants = {}
        
    def _load_or_generate_key(self) -> bytes:
        """Load or generate encryption key for warrant storage"""
        key_path = os.getenv('WARRANT_ENCRYPTION_KEY_PATH', '/secure/warrant.key')
        
        try:
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    return f.read()
            else:
                # Generate new key for development
                key = Fernet.generate_key()
                logger.warning("Generated new warrant encryption key - use secure key management in production")
                return key
        except Exception as e:
            logger.error(f"Failed to load warrant encryption key: {e}")
            return Fernet.generate_key()
    
    def _load_court_public_key(self) -> Optional[rsa.RSAPublicKey]:
        """Load court's public key for digital signature verification"""
        key_path = os.getenv('COURT_PUBLIC_KEY_PATH', '/secure/court_public.pem')
        
        try:
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    return serialization.load_pem_public_key(f.read())
            else:
                logger.warning("Court public key not found - signature verification disabled")
                return None
        except Exception as e:
            logger.error(f"Failed to load court public key: {e}")
            return None
    
    def verify_warrant_signature(self, warrant: WarrantDetails) -> bool:
        """Verify digital signature of warrant"""
        if not self.public_key:
            logger.warning("Cannot verify warrant signature - no public key available")
            return False
        
        try:
            # Create verification data
            warrant_data = f"{warrant.warrant_id}{warrant.case_number}{warrant.issued_date.isoformat()}"
            warrant_bytes = warrant_data.encode('utf-8')
            
            # Verify signature
            signature_bytes = bytes.fromhex(warrant.digital_signature)
            
            self.public_key.verify(
                signature_bytes,
                warrant_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.info(f"Warrant {warrant.warrant_id} signature verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Warrant signature verification failed: {e}")
            return False
    
    def validate_warrant_authority(self, warrant: WarrantDetails) -> Tuple[bool, str]:
        """Validate warrant issuing authority and jurisdiction"""
        
        # Check issuing court authority
        authorized_courts = os.getenv('AUTHORIZED_COURTS', '').split(',')
        if authorized_courts and warrant.issuing_court not in authorized_courts:
            return False, f"Court {warrant.issuing_court} not in authorized list"
        
        # Check requesting agency authority
        authorized_agencies = os.getenv('AUTHORIZED_AGENCIES', '').split(',')
        if authorized_agencies and warrant.requesting_agency not in authorized_agencies:
            return False, f"Agency {warrant.requesting_agency} not authorized"
        
        # Validate case number format
        if not re.match(r'^[A-Z]{2,4}-\d{4}-\d+$', warrant.case_number):
            return False, "Invalid case number format"
        
        # Check warrant scope
        if not warrant.scope:
            return False, "Warrant scope cannot be empty"
        
        # Validate target platforms
        supported_platforms = ['twitter', 'facebook', 'instagram', 'telegram', 'whatsapp']
        invalid_platforms = [p for p in warrant.target_platforms if p.lower() not in supported_platforms]
        if invalid_platforms:
            return False, f"Unsupported platforms: {', '.join(invalid_platforms)}"
        
        return True, "Warrant authority validated"
    
    def check_warrant_validity(self, warrant: WarrantDetails) -> WarrantStatus:
        """Check current validity status of warrant"""
        
        current_time = datetime.now()
        
        # Check if expired
        if current_time > warrant.expiry_date:
            return WarrantStatus.EXPIRED
        
        # Check if not yet effective
        if current_time < warrant.issued_date:
            return WarrantStatus.PENDING
        
        # Check revocation list
        revoked_warrants = os.getenv('REVOKED_WARRANTS', '').split(',')
        if warrant.warrant_id in revoked_warrants:
            return WarrantStatus.REVOKED
        
        return WarrantStatus.VALID
    
    def verify_warrant(self, warrant_data: Dict) -> Tuple[bool, str, Optional[WarrantDetails]]:
        """Complete warrant verification process"""
        
        try:
            # Parse warrant data
            warrant = WarrantDetails(
                warrant_id=warrant_data['warrant_id'],
                warrant_type=WarrantType(warrant_data['warrant_type']),
                issuing_court=warrant_data['issuing_court'],
                judge_name=warrant_data['judge_name'],
                case_number=warrant_data['case_number'],
                issued_date=datetime.fromisoformat(warrant_data['issued_date']),
                expiry_date=datetime.fromisoformat(warrant_data['expiry_date']),
                scope=warrant_data['scope'],
                target_platforms=warrant_data['target_platforms'],
                requesting_agency=warrant_data['requesting_agency'],
                officer_badge=warrant_data['officer_badge'],
                digital_signature=warrant_data['digital_signature'],
                verification_hash=warrant_data['verification_hash']
            )
            
            # Step 1: Verify digital signature
            if not self.verify_warrant_signature(warrant):
                return False, "Digital signature verification failed", None
            
            # Step 2: Validate issuing authority
            authority_valid, authority_msg = self.validate_warrant_authority(warrant)
            if not authority_valid:
                return False, f"Authority validation failed: {authority_msg}", None
            
            # Step 3: Check warrant validity
            status = self.check_warrant_validity(warrant)
            if status != WarrantStatus.VALID:
                return False, f"Warrant status: {status.value}", None
            
            # Step 4: Verify hash integrity
            calculated_hash = self._calculate_warrant_hash(warrant)
            if calculated_hash != warrant.verification_hash:
                return False, "Warrant hash verification failed", None
            
            # Store verified warrant
            self.verified_warrants[warrant.warrant_id] = {
                'warrant': warrant,
                'verified_at': datetime.now(),
                'verification_officer': warrant.officer_badge
            }
            
            logger.info(f"Warrant {warrant.warrant_id} successfully verified")
            return True, "Warrant verification successful", warrant
            
        except Exception as e:
            logger.error(f"Warrant verification error: {e}")
            return False, f"Verification error: {str(e)}", None
    
    def _calculate_warrant_hash(self, warrant: WarrantDetails) -> str:
        """Calculate verification hash for warrant integrity"""
        hash_data = (
            f"{warrant.warrant_id}{warrant.case_number}{warrant.issued_date.isoformat()}"
            f"{warrant.expiry_date.isoformat()}{warrant.requesting_agency}{warrant.officer_badge}"
        )
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def get_warrant_permissions(self, warrant_id: str) -> Optional[Dict]:
        """Get permissions and scope for verified warrant"""
        if warrant_id not in self.verified_warrants:
            return None
        
        warrant_info = self.verified_warrants[warrant_id]
        warrant = warrant_info['warrant']
        
        return {
            'warrant_id': warrant_id,
            'platforms': warrant.target_platforms,
            'scope': warrant.scope,
            'expires_at': warrant.expiry_date.isoformat(),
            'requesting_agency': warrant.requesting_agency,
            'case_number': warrant.case_number
        }
    
    def log_warrant_usage(self, warrant_id: str, action: str, target: str, officer_id: str):
        """Log warrant usage for audit trail"""
        if warrant_id not in self.verified_warrants:
            logger.error(f"Attempted to use unverified warrant: {warrant_id}")
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'warrant_id': warrant_id,
            'action': action,
            'target': target,
            'officer_id': officer_id,
            'case_number': self.verified_warrants[warrant_id]['warrant'].case_number
        }
        
        # Log to secure audit file
        audit_file = os.getenv('WARRANT_AUDIT_LOG', '/secure/warrant_audit.log')
        try:
            with open(audit_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write warrant audit log: {e}")
        
        logger.info(f"Warrant usage logged: {warrant_id} - {action} on {target}")

# Example usage and testing
if __name__ == "__main__":
    import re
    
    # Initialize verification system
    verifier = WarrantVerificationSystem()
    
    # Example warrant data
    sample_warrant = {
        'warrant_id': 'WRT-2024-001',
        'warrant_type': 'data_collection_warrant',
        'issuing_court': 'Delhi High Court',
        'judge_name': 'Justice A.K. Sharma',
        'case_number': 'CRL-2024-123',
        'issued_date': '2024-01-15T10:00:00',
        'expiry_date': '2024-12-15T23:59:59',
        'scope': ['social_media_posts', 'user_profiles', 'connection_data'],
        'target_platforms': ['twitter', 'facebook', 'instagram'],
        'requesting_agency': 'Delhi Police Cyber Crime',
        'officer_badge': 'DCP-001',
        'digital_signature': '1234567890abcdef',  # Would be actual signature
        'verification_hash': 'abcdef1234567890'   # Would be actual hash
    }
    
    # Test warrant verification
    is_valid, message, warrant_obj = verifier.verify_warrant(sample_warrant)
    print(f"Warrant verification: {is_valid}")
    print(f"Message: {message}")
    
    if is_valid:
        permissions = verifier.get_warrant_permissions('WRT-2024-001')
        print(f"Warrant permissions: {permissions}")
        
        # Log usage
        verifier.log_warrant_usage('WRT-2024-001', 'data_collection', 'twitter_user_123', 'DCP-001')
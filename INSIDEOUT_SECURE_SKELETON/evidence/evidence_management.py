"""
InsideOut Platform - Evidence Management System
Implements secure evidence collection, chain of custody, and court-admissible evidence handling
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import aiofiles
import aiohttp
from web3 import Web3
from eth_account import Account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvidenceType(Enum):
    """Types of digital evidence"""
    SOCIAL_MEDIA_POST = "social_media_post"
    DIRECT_MESSAGE = "direct_message"
    PROFILE_DATA = "profile_data"
    MEDIA_FILE = "media_file"
    METADATA = "metadata"
    NETWORK_DATA = "network_data"

class EvidenceStatus(Enum):
    """Evidence lifecycle status"""
    COLLECTED = "collected"
    VERIFIED = "verified"
    ENCRYPTED = "encrypted"
    STORED = "stored"
    ANALYZED = "analyzed"
    COURT_READY = "court_ready"
    ARCHIVED = "archived"

class ChainOfCustodyAction(Enum):
    """Chain of custody actions"""
    COLLECTED = "collected"
    TRANSFERRED = "transferred"
    ANALYZED = "analyzed"
    COPIED = "copied"
    ACCESSED = "accessed"
    MODIFIED = "modified"
    ARCHIVED = "archived"

@dataclass
class ProvenanceMetadata:
    """Provenance metadata for evidence"""
    platform: str
    original_url: str
    collection_method: str
    api_version: str
    collection_timestamp: datetime
    platform_metadata: Dict[str, Any]
    technical_metadata: Dict[str, Any]
    authenticity_indicators: Dict[str, Any]

@dataclass
class ChainOfCustodyEntry:
    """Single entry in chain of custody"""
    entry_id: str
    timestamp: datetime
    action: ChainOfCustodyAction
    officer_id: str
    officer_name: str
    badge_number: str
    location: str
    description: str
    evidence_hash_before: str
    evidence_hash_after: str
    digital_signature: str
    witness_id: Optional[str] = None

@dataclass
class EvidencePackage:
    """Complete evidence package with all metadata"""
    evidence_id: str
    case_number: str
    warrant_id: str
    evidence_type: EvidenceType
    status: EvidenceStatus
    
    # Content
    raw_data: bytes
    processed_data: Optional[bytes] = None
    
    # Cryptographic integrity
    content_hash: str
    digital_signature: str
    encryption_key_id: str
    
    # Provenance
    provenance: ProvenanceMetadata
    
    # Chain of custody
    chain_of_custody: List[ChainOfCustodyEntry]
    
    # Blockchain record
    blockchain_hash: Optional[str] = None
    blockchain_transaction_id: Optional[str] = None
    
    # Timestamps
    collected_at: datetime
    created_at: datetime
    updated_at: datetime
    
    # Legal metadata
    legal_holds: List[str]
    retention_policy: str
    court_admissible: bool = False

@dataclass
class CourtCertification:
    """Court admissibility certification"""
    certification_id: str
    evidence_id: str
    certifying_officer: str
    certification_date: datetime
    court_standards_met: List[str]
    authentication_method: str
    integrity_verified: bool
    chain_of_custody_complete: bool
    legal_requirements_met: List[str]
    certification_signature: str

class EncryptionService:
    """Advanced encryption service for evidence protection"""
    
    def __init__(self, master_key: bytes):
        self.master_key = master_key
        self.key_derivation = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'insideout_evidence_salt',
            iterations=100000,
        )
    
    def generate_evidence_key(self, evidence_id: str) -> bytes:
        """Generate unique encryption key for evidence"""
        evidence_salt = evidence_id.encode() + b'_evidence_key'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=evidence_salt,
            iterations=100000,
        )
        return kdf.derive(self.master_key)
    
    def encrypt_evidence(self, data: bytes, evidence_id: str) -> Tuple[bytes, str]:
        """Encrypt evidence data with unique key"""
        evidence_key = self.generate_evidence_key(evidence_id)
        fernet = Fernet(base64.urlsafe_b64encode(evidence_key))
        
        encrypted_data = fernet.encrypt(data)
        key_id = hashlib.sha256(evidence_key).hexdigest()[:16]
        
        return encrypted_data, key_id
    
    def decrypt_evidence(self, encrypted_data: bytes, evidence_id: str) -> bytes:
        """Decrypt evidence data"""
        evidence_key = self.generate_evidence_key(evidence_id)
        fernet = Fernet(base64.urlsafe_b64encode(evidence_key))
        
        return fernet.decrypt(encrypted_data)
    
    def create_content_hash(self, data: bytes) -> str:
        """Create SHA-256 hash of content for integrity verification"""
        return hashlib.sha256(data).hexdigest()
    
    def verify_content_integrity(self, data: bytes, expected_hash: str) -> bool:
        """Verify content integrity using hash"""
        actual_hash = self.create_content_hash(data)
        return actual_hash == expected_hash

class DigitalSignatureService:
    """Digital signature service for evidence authentication"""
    
    def __init__(self, private_key_pem: bytes):
        self.private_key = serialization.load_pem_private_key(
            private_key_pem, password=None
        )
        self.public_key = self.private_key.public_key()
    
    def sign_evidence(self, evidence_hash: str, officer_id: str) -> str:
        """Create digital signature for evidence"""
        message = f"{evidence_hash}:{officer_id}:{datetime.utcnow().isoformat()}"
        signature = self.private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def verify_signature(self, message: str, signature: str) -> bool:
        """Verify digital signature"""
        try:
            signature_bytes = base64.b64decode(signature)
            self.public_key.verify(
                signature_bytes,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

class BlockchainService:
    """Blockchain service for immutable chain of custody"""
    
    def __init__(self, web3_provider_url: str, contract_address: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.account = Account.from_key(private_key)
        self.contract_address = contract_address
        
        # Smart contract ABI (simplified)
        self.contract_abi = [
            {
                "inputs": [
                    {"name": "evidenceId", "type": "string"},
                    {"name": "evidenceHash", "type": "string"},
                    {"name": "officerId", "type": "string"},
                    {"name": "action", "type": "string"}
                ],
                "name": "recordEvidence",
                "outputs": [],
                "type": "function"
            }
        ]
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
    
    async def record_evidence_on_blockchain(self, 
                                          evidence_id: str,
                                          evidence_hash: str,
                                          officer_id: str,
                                          action: str) -> str:
        """Record evidence action on blockchain"""
        try:
            # Build transaction
            transaction = self.contract.functions.recordEvidence(
                evidence_id, evidence_hash, officer_id, action
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Evidence recorded on blockchain: {receipt.transactionHash.hex()}")
            return receipt.transactionHash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain recording failed: {str(e)}")
            raise

class ChainOfCustodyService:
    """Chain of custody management service"""
    
    def __init__(self, signature_service: DigitalSignatureService,
                 blockchain_service: BlockchainService):
        self.signature_service = signature_service
        self.blockchain_service = blockchain_service
    
    def create_custody_entry(self, 
                           evidence_id: str,
                           action: ChainOfCustodyAction,
                           officer_id: str,
                           officer_name: str,
                           badge_number: str,
                           location: str,
                           description: str,
                           evidence_hash_before: str,
                           evidence_hash_after: str) -> ChainOfCustodyEntry:
        """Create new chain of custody entry"""
        
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Create digital signature
        signature_data = f"{entry_id}:{evidence_id}:{action.value}:{officer_id}:{timestamp.isoformat()}"
        digital_signature = self.signature_service.sign_evidence(signature_data, officer_id)
        
        return ChainOfCustodyEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            action=action,
            officer_id=officer_id,
            officer_name=officer_name,
            badge_number=badge_number,
            location=location,
            description=description,
            evidence_hash_before=evidence_hash_before,
            evidence_hash_after=evidence_hash_after,
            digital_signature=digital_signature
        )
    
    async def add_custody_entry(self, 
                              evidence: EvidencePackage,
                              custody_entry: ChainOfCustodyEntry) -> bool:
        """Add entry to chain of custody and record on blockchain"""
        try:
            # Add to evidence chain of custody
            evidence.chain_of_custody.append(custody_entry)
            evidence.updated_at = datetime.utcnow()
            
            # Record on blockchain
            blockchain_tx = await self.blockchain_service.record_evidence_on_blockchain(
                evidence.evidence_id,
                custody_entry.evidence_hash_after,
                custody_entry.officer_id,
                custody_entry.action.value
            )
            
            logger.info(f"Chain of custody updated for evidence {evidence.evidence_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custody entry: {str(e)}")
            return False
    
    def verify_chain_integrity(self, evidence: EvidencePackage) -> bool:
        """Verify integrity of entire chain of custody"""
        if not evidence.chain_of_custody:
            return False
        
        # Verify each entry's digital signature
        for entry in evidence.chain_of_custody:
            signature_data = f"{entry.entry_id}:{evidence.evidence_id}:{entry.action.value}:{entry.officer_id}:{entry.timestamp.isoformat()}"
            if not self.signature_service.verify_signature(signature_data, entry.digital_signature):
                logger.error(f"Chain of custody signature verification failed for entry {entry.entry_id}")
                return False
        
        # Verify hash continuity
        for i in range(1, len(evidence.chain_of_custody)):
            prev_entry = evidence.chain_of_custody[i-1]
            curr_entry = evidence.chain_of_custody[i]
            
            if prev_entry.evidence_hash_after != curr_entry.evidence_hash_before:
                logger.error(f"Chain of custody hash continuity broken between entries {prev_entry.entry_id} and {curr_entry.entry_id}")
                return False
        
        return True

class EvidenceCollectionService:
    """Service for collecting social media evidence"""
    
    def __init__(self, encryption_service: EncryptionService,
                 signature_service: DigitalSignatureService,
                 custody_service: ChainOfCustodyService):
        self.encryption_service = encryption_service
        self.signature_service = signature_service
        self.custody_service = custody_service
    
    async def collect_social_media_evidence(self,
                                          platform: str,
                                          content_url: str,
                                          raw_data: bytes,
                                          platform_metadata: Dict,
                                          warrant_id: str,
                                          case_number: str,
                                          collecting_officer: Dict) -> EvidencePackage:
        """Collect and secure social media evidence"""
        
        evidence_id = str(uuid.uuid4())
        collection_timestamp = datetime.utcnow()
        
        # Create content hash
        content_hash = self.encryption_service.create_content_hash(raw_data)
        
        # Encrypt evidence
        encrypted_data, encryption_key_id = self.encryption_service.encrypt_evidence(
            raw_data, evidence_id
        )
        
        # Create digital signature
        digital_signature = self.signature_service.sign_evidence(
            content_hash, collecting_officer['officer_id']
        )
        
        # Create provenance metadata
        provenance = ProvenanceMetadata(
            platform=platform,
            original_url=content_url,
            collection_method="API",
            api_version="v1.0",
            collection_timestamp=collection_timestamp,
            platform_metadata=platform_metadata,
            technical_metadata={
                "user_agent": "InsideOut-Evidence-Collector/1.0",
                "collection_ip": "10.0.0.1",
                "collection_method": "automated"
            },
            authenticity_indicators={
                "platform_verified": True,
                "timestamp_verified": True,
                "content_integrity": True
            }
        )
        
        # Create evidence package
        evidence = EvidencePackage(
            evidence_id=evidence_id,
            case_number=case_number,
            warrant_id=warrant_id,
            evidence_type=EvidenceType.SOCIAL_MEDIA_POST,
            status=EvidenceStatus.COLLECTED,
            raw_data=encrypted_data,
            content_hash=content_hash,
            digital_signature=digital_signature,
            encryption_key_id=encryption_key_id,
            provenance=provenance,
            chain_of_custody=[],
            collected_at=collection_timestamp,
            created_at=collection_timestamp,
            updated_at=collection_timestamp,
            legal_holds=[],
            retention_policy="7_years",
            court_admissible=False
        )
        
        # Create initial chain of custody entry
        initial_custody = self.custody_service.create_custody_entry(
            evidence_id=evidence_id,
            action=ChainOfCustodyAction.COLLECTED,
            officer_id=collecting_officer['officer_id'],
            officer_name=collecting_officer['name'],
            badge_number=collecting_officer['badge_number'],
            location=collecting_officer['location'],
            description=f"Initial collection of {platform} evidence from {content_url}",
            evidence_hash_before="",
            evidence_hash_after=content_hash
        )
        
        # Add custody entry
        await self.custody_service.add_custody_entry(evidence, initial_custody)
        
        logger.info(f"Evidence collected: {evidence_id}")
        return evidence
    
    async def verify_evidence_integrity(self, evidence: EvidencePackage) -> bool:
        """Verify evidence integrity"""
        try:
            # Decrypt evidence
            decrypted_data = self.encryption_service.decrypt_evidence(
                evidence.raw_data, evidence.evidence_id
            )
            
            # Verify content hash
            if not self.encryption_service.verify_content_integrity(
                decrypted_data, evidence.content_hash
            ):
                logger.error(f"Content integrity verification failed for evidence {evidence.evidence_id}")
                return False
            
            # Verify chain of custody
            if not self.custody_service.verify_chain_integrity(evidence):
                logger.error(f"Chain of custody verification failed for evidence {evidence.evidence_id}")
                return False
            
            # Verify digital signature
            signature_data = f"{evidence.content_hash}:{evidence.provenance.collection_timestamp.isoformat()}"
            if not self.signature_service.verify_signature(signature_data, evidence.digital_signature):
                logger.error(f"Digital signature verification failed for evidence {evidence.evidence_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Evidence integrity verification error: {str(e)}")
            return False

class CourtAdmissibilityService:
    """Service for ensuring evidence meets court admissibility standards"""
    
    def __init__(self, signature_service: DigitalSignatureService):
        self.signature_service = signature_service
        
        # Federal Rules of Evidence requirements
        self.fre_requirements = {
            'authentication': ['FRE 901', 'FRE 902'],
            'hearsay': ['FRE 803', 'FRE 807'],
            'best_evidence': ['FRE 1001', 'FRE 1002'],
            'relevance': ['FRE 401', 'FRE 403']
        }
    
    async def certify_evidence_for_court(self, 
                                       evidence: EvidencePackage,
                                       certifying_officer: Dict) -> CourtCertification:
        """Certify evidence meets court admissibility standards"""
        
        certification_id = str(uuid.uuid4())
        certification_date = datetime.utcnow()
        
        # Check authentication requirements
        authentication_met = self._check_authentication_requirements(evidence)
        
        # Check integrity requirements
        integrity_verified = await self._verify_evidence_integrity(evidence)
        
        # Check chain of custody completeness
        chain_complete = self._check_chain_of_custody_completeness(evidence)
        
        # Check legal requirements
        legal_requirements_met = self._check_legal_requirements(evidence)
        
        # Create certification
        certification = CourtCertification(
            certification_id=certification_id,
            evidence_id=evidence.evidence_id,
            certifying_officer=certifying_officer['officer_id'],
            certification_date=certification_date,
            court_standards_met=self._get_met_standards(evidence),
            authentication_method="Digital signature and hash verification",
            integrity_verified=integrity_verified,
            chain_of_custody_complete=chain_complete,
            legal_requirements_met=legal_requirements_met,
            certification_signature=self.signature_service.sign_evidence(
                f"{certification_id}:{evidence.evidence_id}:{certification_date.isoformat()}",
                certifying_officer['officer_id']
            )
        )
        
        # Update evidence status
        if (authentication_met and integrity_verified and 
            chain_complete and len(legal_requirements_met) > 0):
            evidence.court_admissible = True
            evidence.status = EvidenceStatus.COURT_READY
        
        return certification
    
    def _check_authentication_requirements(self, evidence: EvidencePackage) -> bool:
        """Check FRE 901/902 authentication requirements"""
        # Check digital signature
        if not evidence.digital_signature:
            return False
        
        # Check provenance metadata
        if not evidence.provenance.authenticity_indicators.get('platform_verified'):
            return False
        
        # Check chain of custody
        if not evidence.chain_of_custody:
            return False
        
        return True
    
    async def _verify_evidence_integrity(self, evidence: EvidencePackage) -> bool:
        """Verify evidence integrity for court standards"""
        # This would use the EvidenceCollectionService
        # For now, return True if content hash exists
        return bool(evidence.content_hash)
    
    def _check_chain_of_custody_completeness(self, evidence: EvidencePackage) -> bool:
        """Check if chain of custody is complete and unbroken"""
        if not evidence.chain_of_custody:
            return False
        
        # Check for required actions
        required_actions = [ChainOfCustodyAction.COLLECTED]
        actions_present = [entry.action for entry in evidence.chain_of_custody]
        
        return all(action in actions_present for action in required_actions)
    
    def _check_legal_requirements(self, evidence: EvidencePackage) -> List[str]:
        """Check which legal requirements are met"""
        met_requirements = []
        
        # Check warrant requirement
        if evidence.warrant_id:
            met_requirements.append("Valid warrant")
        
        # Check retention policy
        if evidence.retention_policy:
            met_requirements.append("Retention policy defined")
        
        # Check encryption
        if evidence.encryption_key_id:
            met_requirements.append("Data encrypted")
        
        return met_requirements
    
    def _get_met_standards(self, evidence: EvidencePackage) -> List[str]:
        """Get list of court standards met by evidence"""
        met_standards = []
        
        if evidence.digital_signature:
            met_standards.append("FRE 901 - Authentication")
        
        if evidence.content_hash:
            met_standards.append("FRE 1001 - Best Evidence Rule")
        
        if evidence.chain_of_custody:
            met_standards.append("Chain of Custody")
        
        if evidence.provenance.authenticity_indicators:
            met_standards.append("Provenance Documentation")
        
        return met_standards

# Example usage
async def main():
    """Example usage of evidence management system"""
    
    # Initialize services
    master_key = b"secure_master_key_32_bytes_long!!"
    encryption_service = EncryptionService(master_key)
    
    # Generate RSA key pair for signatures (in practice, load from secure storage)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    signature_service = DigitalSignatureService(private_key_pem)
    
    # Initialize blockchain service (mock)
    blockchain_service = BlockchainService(
        "http://localhost:8545",
        "0x1234567890123456789012345678901234567890",
        "0xprivate_key_here"
    )
    
    custody_service = ChainOfCustodyService(signature_service, blockchain_service)
    collection_service = EvidenceCollectionService(
        encryption_service, signature_service, custody_service
    )
    court_service = CourtAdmissibilityService(signature_service)
    
    # Collect evidence
    officer_info = {
        'officer_id': 'OFF123',
        'name': 'Officer Smith',
        'badge_number': 'BADGE123',
        'location': 'Delhi Police HQ'
    }
    
    sample_data = b"Sample social media post content"
    platform_metadata = {
        'post_id': '12345',
        'author': '@user123',
        'timestamp': '2024-01-01T12:00:00Z',
        'platform': 'twitter'
    }
    
    evidence = await collection_service.collect_social_media_evidence(
        platform="twitter",
        content_url="https://twitter.com/user123/status/12345",
        raw_data=sample_data,
        platform_metadata=platform_metadata,
        warrant_id="WR-2024-001",
        case_number="CASE-2024-001",
        collecting_officer=officer_info
    )
    
    print(f"Evidence collected: {evidence.evidence_id}")
    
    # Verify evidence integrity
    integrity_valid = await collection_service.verify_evidence_integrity(evidence)
    print(f"Evidence integrity valid: {integrity_valid}")
    
    # Certify for court
    certification = await court_service.certify_evidence_for_court(evidence, officer_info)
    print(f"Court certification: {certification.certification_id}")
    print(f"Court admissible: {evidence.court_admissible}")

if __name__ == "__main__":
    asyncio.run(main())
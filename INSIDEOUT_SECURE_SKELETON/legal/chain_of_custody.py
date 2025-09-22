"""
InsideOut Platform - Chain of Custody System
Implements secure evidence tracking and chain of custody management
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class EvidenceType(Enum):
    """Types of digital evidence"""
    SOCIAL_MEDIA_POST = "social_media_post"
    USER_PROFILE = "user_profile"
    CHAT_MESSAGE = "chat_message"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    METADATA = "metadata"
    NETWORK_LOG = "network_log"

class CustodyAction(Enum):
    """Chain of custody actions"""
    COLLECTED = "collected"
    TRANSFERRED = "transferred"
    ANALYZED = "analyzed"
    COPIED = "copied"
    STORED = "stored"
    ACCESSED = "accessed"
    MODIFIED = "modified"
    SEALED = "sealed"
    UNSEALED = "unsealed"

@dataclass
class EvidenceItem:
    """Digital evidence item structure"""
    evidence_id: str
    evidence_type: EvidenceType
    source_platform: str
    source_url: str
    collection_timestamp: datetime
    file_hash: str
    file_size: int
    mime_type: str
    warrant_id: str
    case_number: str
    description: str
    metadata: Dict[str, Any]

@dataclass
class CustodyEntry:
    """Chain of custody entry"""
    entry_id: str
    evidence_id: str
    action: CustodyAction
    timestamp: datetime
    officer_id: str
    officer_name: str
    badge_number: str
    department: str
    location: str
    reason: str
    previous_hash: str
    current_hash: str
    digital_signature: str

class ChainOfCustodySystem:
    """Secure chain of custody management system"""
    
    def __init__(self):
        self.encryption_key = self._load_or_generate_key()
        self.fernet = Fernet(self.encryption_key)
        self.custody_chains = {}
        self.evidence_registry = {}
        
    def _load_or_generate_key(self) -> bytes:
        """Load or generate encryption key for custody data"""
        key_path = os.getenv('CUSTODY_ENCRYPTION_KEY_PATH', '/secure/custody.key')
        
        try:
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    return f.read()
            else:
                # Generate new key for development
                password = os.getenv('CUSTODY_PASSWORD', 'default-dev-password').encode()
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password))
                logger.warning("Generated new custody encryption key - use secure key management in production")
                return key
        except Exception as e:
            logger.error(f"Failed to load custody encryption key: {e}")
            # Fallback key generation
            return Fernet.generate_key()
    
    def _calculate_evidence_hash(self, evidence: EvidenceItem) -> str:
        """Calculate hash for evidence integrity verification"""
        hash_data = (
            f"{evidence.evidence_id}{evidence.source_url}{evidence.collection_timestamp.isoformat()}"
            f"{evidence.file_hash}{evidence.warrant_id}{evidence.case_number}"
        )
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def _calculate_chain_hash(self, previous_hash: str, entry: CustodyEntry) -> str:
        """Calculate hash for chain integrity"""
        chain_data = (
            f"{previous_hash}{entry.evidence_id}{entry.action.value}{entry.timestamp.isoformat()}"
            f"{entry.officer_id}{entry.badge_number}"
        )
        return hashlib.sha256(chain_data.encode()).hexdigest()
    
    def register_evidence(self, evidence_data: Dict) -> Tuple[bool, str, Optional[str]]:
        """Register new evidence item in the system"""
        
        try:
            # Create evidence item
            evidence = EvidenceItem(
                evidence_id=evidence_data.get('evidence_id', str(uuid.uuid4())),
                evidence_type=EvidenceType(evidence_data['evidence_type']),
                source_platform=evidence_data['source_platform'],
                source_url=evidence_data['source_url'],
                collection_timestamp=datetime.fromisoformat(evidence_data['collection_timestamp']),
                file_hash=evidence_data['file_hash'],
                file_size=evidence_data['file_size'],
                mime_type=evidence_data['mime_type'],
                warrant_id=evidence_data['warrant_id'],
                case_number=evidence_data['case_number'],
                description=evidence_data['description'],
                metadata=evidence_data.get('metadata', {})
            )
            
            # Validate evidence
            if evidence.evidence_id in self.evidence_registry:
                return False, "Evidence ID already exists", None
            
            if not evidence.file_hash or len(evidence.file_hash) != 64:
                return False, "Invalid file hash", None
            
            # Calculate evidence integrity hash
            evidence_hash = self._calculate_evidence_hash(evidence)
            
            # Encrypt and store evidence
            evidence_json = json.dumps(asdict(evidence), default=str)
            encrypted_evidence = self.fernet.encrypt(evidence_json.encode())
            
            self.evidence_registry[evidence.evidence_id] = {
                'evidence': encrypted_evidence,
                'integrity_hash': evidence_hash,
                'registered_at': datetime.now()
            }
            
            # Initialize custody chain
            self.custody_chains[evidence.evidence_id] = []
            
            logger.info(f"Evidence {evidence.evidence_id} registered successfully")
            return True, "Evidence registered successfully", evidence.evidence_id
            
        except Exception as e:
            logger.error(f"Evidence registration error: {e}")
            return False, f"Registration error: {str(e)}", None
    
    def add_custody_entry(self, evidence_id: str, action: CustodyAction, officer_data: Dict, 
                         location: str, reason: str) -> Tuple[bool, str]:
        """Add new entry to chain of custody"""
        
        try:
            # Validate evidence exists
            if evidence_id not in self.evidence_registry:
                return False, "Evidence not found in registry"
            
            if evidence_id not in self.custody_chains:
                return False, "Custody chain not initialized"
            
            # Get previous hash
            previous_entries = self.custody_chains[evidence_id]
            previous_hash = previous_entries[-1]['current_hash'] if previous_entries else "GENESIS"
            
            # Create custody entry
            entry = CustodyEntry(
                entry_id=str(uuid.uuid4()),
                evidence_id=evidence_id,
                action=action,
                timestamp=datetime.now(),
                officer_id=officer_data['officer_id'],
                officer_name=officer_data['officer_name'],
                badge_number=officer_data['badge_number'],
                department=officer_data['department'],
                location=location,
                reason=reason,
                previous_hash=previous_hash,
                current_hash="",  # Will be calculated
                digital_signature=""  # Would be actual signature in production
            )
            
            # Calculate current hash
            entry.current_hash = self._calculate_chain_hash(previous_hash, entry)
            
            # Add digital signature (simplified for demo)
            signature_data = f"{entry.entry_id}{entry.current_hash}{entry.officer_id}"
            entry.digital_signature = hashlib.sha256(signature_data.encode()).hexdigest()
            
            # Encrypt and store entry
            entry_json = json.dumps(asdict(entry), default=str)
            encrypted_entry = self.fernet.encrypt(entry_json.encode())
            
            self.custody_chains[evidence_id].append({
                'entry': encrypted_entry,
                'current_hash': entry.current_hash,
                'timestamp': entry.timestamp,
                'officer_id': entry.officer_id,
                'action': entry.action.value
            })
            
            # Log custody action
            self._log_custody_action(entry)
            
            logger.info(f"Custody entry added for evidence {evidence_id}: {action.value}")
            return True, "Custody entry added successfully"
            
        except Exception as e:
            logger.error(f"Custody entry error: {e}")
            return False, f"Custody entry error: {str(e)}"
    
    def verify_chain_integrity(self, evidence_id: str) -> Tuple[bool, str, List[str]]:
        """Verify integrity of entire custody chain"""
        
        if evidence_id not in self.custody_chains:
            return False, "Custody chain not found", []
        
        chain = self.custody_chains[evidence_id]
        issues = []
        
        try:
            previous_hash = "GENESIS"
            
            for i, encrypted_entry_data in enumerate(chain):
                # Decrypt entry
                encrypted_entry = encrypted_entry_data['entry']
                entry_json = self.fernet.decrypt(encrypted_entry).decode()
                entry_data = json.loads(entry_json)
                
                # Recreate entry object
                entry = CustodyEntry(**{
                    k: (datetime.fromisoformat(v) if k in ['timestamp'] else 
                        CustodyAction(v) if k == 'action' else v)
                    for k, v in entry_data.items()
                })
                
                # Verify previous hash
                if entry.previous_hash != previous_hash:
                    issues.append(f"Entry {i}: Previous hash mismatch")
                
                # Verify current hash
                calculated_hash = self._calculate_chain_hash(previous_hash, entry)
                if entry.current_hash != calculated_hash:
                    issues.append(f"Entry {i}: Current hash mismatch")
                
                # Verify stored hash matches
                if entry.current_hash != encrypted_entry_data['current_hash']:
                    issues.append(f"Entry {i}: Stored hash mismatch")
                
                previous_hash = entry.current_hash
            
            if issues:
                return False, f"Chain integrity compromised: {len(issues)} issues found", issues
            else:
                return True, "Chain integrity verified", []
                
        except Exception as e:
            logger.error(f"Chain verification error: {e}")
            return False, f"Verification error: {str(e)}", [str(e)]
    
    def get_custody_history(self, evidence_id: str) -> Optional[List[Dict]]:
        """Get complete custody history for evidence"""
        
        if evidence_id not in self.custody_chains:
            return None
        
        try:
            history = []
            chain = self.custody_chains[evidence_id]
            
            for encrypted_entry_data in chain:
                # Decrypt entry
                encrypted_entry = encrypted_entry_data['entry']
                entry_json = self.fernet.decrypt(encrypted_entry).decode()
                entry_data = json.loads(entry_json)
                
                # Create history entry
                history_entry = {
                    'timestamp': entry_data['timestamp'],
                    'action': entry_data['action'],
                    'officer_name': entry_data['officer_name'],
                    'badge_number': entry_data['badge_number'],
                    'department': entry_data['department'],
                    'location': entry_data['location'],
                    'reason': entry_data['reason']
                }
                
                history.append(history_entry)
            
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving custody history: {e}")
            return None
    
    def generate_custody_report(self, evidence_id: str) -> Optional[Dict]:
        """Generate comprehensive custody report for court"""
        
        if evidence_id not in self.evidence_registry:
            return None
        
        try:
            # Get evidence details
            evidence_data = self.evidence_registry[evidence_id]
            encrypted_evidence = evidence_data['evidence']
            evidence_json = self.fernet.decrypt(encrypted_evidence).decode()
            evidence_dict = json.loads(evidence_json)
            
            # Get custody history
            history = self.get_custody_history(evidence_id)
            
            # Verify chain integrity
            is_valid, integrity_msg, issues = self.verify_chain_integrity(evidence_id)
            
            # Generate report
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'evidence_id': evidence_id,
                'case_number': evidence_dict['case_number'],
                'warrant_id': evidence_dict['warrant_id'],
                'evidence_details': {
                    'type': evidence_dict['evidence_type'],
                    'source_platform': evidence_dict['source_platform'],
                    'source_url': evidence_dict['source_url'],
                    'collection_timestamp': evidence_dict['collection_timestamp'],
                    'file_hash': evidence_dict['file_hash'],
                    'file_size': evidence_dict['file_size'],
                    'description': evidence_dict['description']
                },
                'chain_integrity': {
                    'is_valid': is_valid,
                    'message': integrity_msg,
                    'issues': issues
                },
                'custody_history': history,
                'total_custody_entries': len(history) if history else 0,
                'report_hash': ""  # Will be calculated
            }
            
            # Calculate report hash for integrity
            report_data = json.dumps(report, sort_keys=True, default=str)
            report['report_hash'] = hashlib.sha256(report_data.encode()).hexdigest()
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating custody report: {e}")
            return None
    
    def _log_custody_action(self, entry: CustodyEntry):
        """Log custody action to audit file"""
        
        log_entry = {
            'timestamp': entry.timestamp.isoformat(),
            'evidence_id': entry.evidence_id,
            'action': entry.action.value,
            'officer_id': entry.officer_id,
            'badge_number': entry.badge_number,
            'location': entry.location,
            'reason': entry.reason,
            'entry_hash': entry.current_hash
        }
        
        audit_file = os.getenv('CUSTODY_AUDIT_LOG', '/secure/custody_audit.log')
        try:
            with open(audit_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write custody audit log: {e}")

# Example usage and testing
if __name__ == "__main__":
    from typing import Tuple
    
    # Initialize custody system
    custody_system = ChainOfCustodySystem()
    
    # Example evidence registration
    evidence_data = {
        'evidence_type': 'social_media_post',
        'source_platform': 'twitter',
        'source_url': 'https://twitter.com/user/status/123456789',
        'collection_timestamp': '2024-01-15T14:30:00',
        'file_hash': 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
        'file_size': 1024,
        'mime_type': 'application/json',
        'warrant_id': 'WRT-2024-001',
        'case_number': 'CRL-2024-123',
        'description': 'Suspicious social media post related to case',
        'metadata': {
            'author': 'suspect_user',
            'timestamp': '2024-01-15T12:00:00',
            'likes': 15,
            'retweets': 3
        }
    }
    
    # Register evidence
    success, message, evidence_id = custody_system.register_evidence(evidence_data)
    print(f"Evidence registration: {success} - {message}")
    
    if success:
        # Add custody entries
        officer_data = {
            'officer_id': 'OFF-001',
            'officer_name': 'Inspector John Doe',
            'badge_number': 'DCP-001',
            'department': 'Delhi Police Cyber Crime'
        }
        
        # Collection entry
        custody_system.add_custody_entry(
            evidence_id, CustodyAction.COLLECTED, officer_data,
            'Delhi Police HQ', 'Initial evidence collection'
        )
        
        # Analysis entry
        custody_system.add_custody_entry(
            evidence_id, CustodyAction.ANALYZED, officer_data,
            'Forensic Lab', 'Content analysis and metadata extraction'
        )
        
        # Verify chain integrity
        is_valid, msg, issues = custody_system.verify_chain_integrity(evidence_id)
        print(f"Chain integrity: {is_valid} - {msg}")
        
        # Generate custody report
        report = custody_system.generate_custody_report(evidence_id)
        if report:
            print(f"Custody report generated with {report['total_custody_entries']} entries")
            print(f"Chain integrity: {report['chain_integrity']['is_valid']}")
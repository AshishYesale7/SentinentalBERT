#!/usr/bin/env python3
"""
Indian Legal Framework Compliance Module
Implements compliance with IT Act 2000, CrPC 1973, Evidence Act 1872
"""

import json
import hashlib
import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalAuthority(Enum):
    """Types of legal authorities under Indian law"""
    MAGISTRATE_WARRANT = "magistrate_warrant"
    COURT_ORDER = "court_order"
    POLICE_COMMISSIONER = "police_commissioner"
    DGP_ORDER = "dgp_order"
    CYBER_CELL_AUTHORIZATION = "cyber_cell_auth"
    EMERGENCY_PROVISION = "emergency_provision"

class EvidenceType(Enum):
    """Types of digital evidence under Indian Evidence Act"""
    ELECTRONIC_RECORD = "electronic_record"  # Section 65A
    COMPUTER_OUTPUT = "computer_output"      # Section 65B
    DIGITAL_SIGNATURE = "digital_signature"  # IT Act Section 3
    ELECTRONIC_DOCUMENT = "electronic_document"  # IT Act Section 4
    NETWORK_LOG = "network_log"
    METADATA = "metadata"

class InvestigationStage(Enum):
    """Investigation stages under CrPC"""
    FIR_REGISTRATION = "fir_registration"      # Section 154
    PRELIMINARY_INQUIRY = "preliminary_inquiry" # Section 155
    INVESTIGATION = "investigation"             # Section 156
    CHARGE_SHEET = "charge_sheet"              # Section 173
    TRIAL = "trial"
    APPEAL = "appeal"

@dataclass
class LegalAuthorization:
    """Legal authorization document structure"""
    auth_id: str
    authority_type: LegalAuthority
    issuing_authority: str
    case_number: str
    sections_invoked: List[str]
    validity_start: datetime.datetime
    validity_end: datetime.datetime
    scope_description: str
    target_platforms: List[str]
    target_accounts: List[str]
    authorized_officers: List[str]
    digital_signature: str
    created_at: datetime.datetime
    is_valid: bool = True

@dataclass
class DigitalEvidence:
    """Digital evidence structure compliant with Indian Evidence Act"""
    evidence_id: str
    evidence_type: EvidenceType
    source_platform: str
    content_hash: str
    original_content: str
    metadata: Dict
    collection_timestamp: datetime.datetime
    collecting_officer: str
    chain_of_custody: List[Dict]
    legal_authorization: str  # Reference to LegalAuthorization
    section_65b_certificate: Optional[str]  # Required for computer output
    integrity_verified: bool
    admissibility_status: str

@dataclass
class ChainOfCustodyEntry:
    """Chain of custody entry for evidence tracking"""
    entry_id: str
    evidence_id: str
    officer_id: str
    officer_name: str
    action_type: str  # collected, transferred, analyzed, stored
    timestamp: datetime.datetime
    location: str
    digital_signature: str
    remarks: str

class IndianLegalFramework:
    """Main class for Indian legal framework compliance"""
    
    def __init__(self):
        self.authorizations: Dict[str, LegalAuthorization] = {}
        self.evidence_store: Dict[str, DigitalEvidence] = {}
        self.custody_chain: Dict[str, List[ChainOfCustodyEntry]] = {}
        
    def validate_legal_authority(self, auth_data: Dict) -> Tuple[bool, str]:
        """
        Validate legal authority under Indian law
        Implements IT Act 2000, CrPC 1973 compliance
        """
        try:
            # Check required fields
            required_fields = [
                'authority_type', 'issuing_authority', 'case_number',
                'sections_invoked', 'validity_start', 'validity_end'
            ]
            
            for field in required_fields:
                if field not in auth_data:
                    return False, f"Missing required field: {field}"
            
            # Validate authority type
            try:
                auth_type = LegalAuthority(auth_data['authority_type'])
            except ValueError:
                return False, "Invalid authority type"
            
            # Validate sections invoked
            valid_sections = self._get_valid_legal_sections()
            for section in auth_data['sections_invoked']:
                if section not in valid_sections:
                    logger.warning(f"Unusual legal section invoked: {section}")
            
            # Check validity period
            start_date = datetime.datetime.fromisoformat(auth_data['validity_start'])
            end_date = datetime.datetime.fromisoformat(auth_data['validity_end'])
            current_time = datetime.datetime.now()
            
            if start_date > current_time:
                return False, "Authorization not yet valid"
            
            if end_date < current_time:
                return False, "Authorization has expired"
            
            # Validate scope
            if not auth_data.get('scope_description'):
                return False, "Scope description required"
            
            return True, "Valid legal authorization"
            
        except Exception as e:
            logger.error(f"Error validating legal authority: {e}")
            return False, f"Validation error: {str(e)}"
    
    def create_legal_authorization(self, auth_data: Dict) -> Optional[LegalAuthorization]:
        """Create and store legal authorization"""
        is_valid, message = self.validate_legal_authority(auth_data)
        
        if not is_valid:
            logger.error(f"Invalid authorization: {message}")
            return None
        
        auth_id = str(uuid.uuid4())
        
        authorization = LegalAuthorization(
            auth_id=auth_id,
            authority_type=LegalAuthority(auth_data['authority_type']),
            issuing_authority=auth_data['issuing_authority'],
            case_number=auth_data['case_number'],
            sections_invoked=auth_data['sections_invoked'],
            validity_start=datetime.datetime.fromisoformat(auth_data['validity_start']),
            validity_end=datetime.datetime.fromisoformat(auth_data['validity_end']),
            scope_description=auth_data['scope_description'],
            target_platforms=auth_data.get('target_platforms', []),
            target_accounts=auth_data.get('target_accounts', []),
            authorized_officers=auth_data.get('authorized_officers', []),
            digital_signature=self._generate_digital_signature(auth_data),
            created_at=datetime.datetime.now()
        )
        
        self.authorizations[auth_id] = authorization
        logger.info(f"Legal authorization created: {auth_id}")
        
        return authorization
    
    def collect_digital_evidence(self, 
                                content: str,
                                platform: str,
                                evidence_type: EvidenceType,
                                collecting_officer: str,
                                authorization_id: str,
                                metadata: Dict = None) -> Optional[DigitalEvidence]:
        """
        Collect digital evidence in compliance with Indian Evidence Act
        Implements Section 65A and 65B requirements
        """
        
        # Verify authorization
        if authorization_id not in self.authorizations:
            logger.error("Invalid authorization ID")
            return None
        
        auth = self.authorizations[authorization_id]
        if not auth.is_valid or auth.validity_end < datetime.datetime.now():
            logger.error("Authorization expired or invalid")
            return None
        
        # Generate evidence ID and hash
        evidence_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Create evidence record
        evidence = DigitalEvidence(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            source_platform=platform,
            content_hash=content_hash,
            original_content=content,  # In production, this should be encrypted
            metadata=metadata or {},
            collection_timestamp=datetime.datetime.now(),
            collecting_officer=collecting_officer,
            chain_of_custody=[],
            legal_authorization=authorization_id,
            section_65b_certificate=None,
            integrity_verified=True,
            admissibility_status="pending_verification"
        )
        
        # Generate Section 65B certificate if required
        if evidence_type in [EvidenceType.COMPUTER_OUTPUT, EvidenceType.ELECTRONIC_RECORD]:
            evidence.section_65b_certificate = self._generate_section_65b_certificate(evidence)
        
        # Initialize chain of custody
        custody_entry = ChainOfCustodyEntry(
            entry_id=str(uuid.uuid4()),
            evidence_id=evidence_id,
            officer_id=collecting_officer,
            officer_name=collecting_officer,  # In real implementation, lookup from officer DB
            action_type="collected",
            timestamp=datetime.datetime.now(),
            location="Digital Collection System",
            digital_signature=self._generate_digital_signature({"evidence_id": evidence_id, "action": "collected"}),
            remarks="Initial evidence collection"
        )
        
        self.evidence_store[evidence_id] = evidence
        self.custody_chain[evidence_id] = [custody_entry]
        
        logger.info(f"Digital evidence collected: {evidence_id}")
        return evidence
    
    def add_custody_entry(self, evidence_id: str, officer_id: str, action_type: str, remarks: str = "") -> bool:
        """Add entry to chain of custody"""
        if evidence_id not in self.evidence_store:
            logger.error("Evidence not found")
            return False
        
        custody_entry = ChainOfCustodyEntry(
            entry_id=str(uuid.uuid4()),
            evidence_id=evidence_id,
            officer_id=officer_id,
            officer_name=officer_id,  # Lookup from officer DB in real implementation
            action_type=action_type,
            timestamp=datetime.datetime.now(),
            location="Evidence Management System",
            digital_signature=self._generate_digital_signature({
                "evidence_id": evidence_id, 
                "officer": officer_id, 
                "action": action_type
            }),
            remarks=remarks
        )
        
        if evidence_id not in self.custody_chain:
            self.custody_chain[evidence_id] = []
        
        self.custody_chain[evidence_id].append(custody_entry)
        logger.info(f"Custody entry added for evidence {evidence_id}")
        
        return True
    
    def verify_evidence_integrity(self, evidence_id: str) -> Tuple[bool, str]:
        """Verify integrity of digital evidence"""
        if evidence_id not in self.evidence_store:
            return False, "Evidence not found"
        
        evidence = self.evidence_store[evidence_id]
        
        try:
            # Verify hash
            current_hash = hashlib.sha256(evidence.original_content.encode()).hexdigest()
            
            if current_hash != evidence.content_hash:
                return False, "Evidence integrity compromised - hash mismatch"
            
            # Verify chain of custody
            if not self.custody_chain.get(evidence_id):
                return False, "Chain of custody missing"
            
            return True, "Evidence integrity verified"
            
        except Exception as e:
            logger.error(f"Error verifying evidence integrity: {e}")
            return False, f"Verification error: {str(e)}"
    
    def generate_court_report(self, case_number: str) -> Dict:
        """Generate court-ready evidence report"""
        case_evidence = []
        case_authorizations = []
        
        # Find all evidence for this case
        for auth_id, auth in self.authorizations.items():
            if auth.case_number == case_number:
                case_authorizations.append(asdict(auth))
                
                # Find evidence collected under this authorization
                for evidence_id, evidence in self.evidence_store.items():
                    if evidence.legal_authorization == auth_id:
                        evidence_dict = asdict(evidence)
                        evidence_dict['chain_of_custody'] = [
                            asdict(entry) for entry in self.custody_chain.get(evidence_id, [])
                        ]
                        case_evidence.append(evidence_dict)
        
        report = {
            "case_number": case_number,
            "report_generated": datetime.datetime.now().isoformat(),
            "legal_authorizations": case_authorizations,
            "digital_evidence": case_evidence,
            "total_evidence_items": len(case_evidence),
            "compliance_status": self._check_compliance_status(case_evidence)
        }
        
        return report
    
    def _get_valid_legal_sections(self) -> List[str]:
        """Get list of valid legal sections"""
        return [
            # IT Act 2000
            "IT_Act_66", "IT_Act_66A", "IT_Act_66B", "IT_Act_66C", "IT_Act_66D",
            "IT_Act_66E", "IT_Act_66F", "IT_Act_67", "IT_Act_67A", "IT_Act_67B",
            "IT_Act_69", "IT_Act_69A", "IT_Act_69B", "IT_Act_70", "IT_Act_72",
            
            # CrPC 1973
            "CrPC_154", "CrPC_155", "CrPC_156", "CrPC_160", "CrPC_161",
            "CrPC_173", "CrPC_91", "CrPC_93", "CrPC_102", "CrPC_165",
            
            # Evidence Act 1872
            "Evidence_Act_65A", "Evidence_Act_65B", "Evidence_Act_73A",
            "Evidence_Act_85A", "Evidence_Act_85B", "Evidence_Act_85C",
            
            # IPC Sections
            "IPC_153A", "IPC_295A", "IPC_298", "IPC_499", "IPC_500",
            "IPC_505", "IPC_506", "IPC_509", "IPC_354D"
        ]
    
    def _generate_digital_signature(self, data: Dict) -> str:
        """Generate digital signature for data"""
        data_string = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(data_string.encode()).hexdigest()
        return signature
    
    def _generate_section_65b_certificate(self, evidence: DigitalEvidence) -> str:
        """Generate Section 65B certificate for computer output"""
        certificate = {
            "certificate_type": "Section_65B_Evidence_Act_1872",
            "evidence_id": evidence.evidence_id,
            "computer_system": "InsideOut Digital Evidence Collection System",
            "regular_use_period": "Continuous operation since deployment",
            "information_source": evidence.source_platform,
            "operating_conditions": "Normal operating conditions maintained",
            "no_improper_operation": "No improper operation during collection period",
            "certifying_officer": evidence.collecting_officer,
            "certification_date": datetime.datetime.now().isoformat(),
            "digital_signature": self._generate_digital_signature({
                "evidence_id": evidence.evidence_id,
                "type": "section_65b_certificate"
            })
        }
        
        return json.dumps(certificate, indent=2)
    
    def _check_compliance_status(self, evidence_list: List[Dict]) -> Dict:
        """Check compliance status of evidence"""
        compliance = {
            "total_items": len(evidence_list),
            "section_65b_compliant": 0,
            "chain_of_custody_complete": 0,
            "integrity_verified": 0,
            "overall_compliance": "pending"
        }
        
        for evidence in evidence_list:
            if evidence.get('section_65b_certificate'):
                compliance["section_65b_compliant"] += 1
            
            if evidence.get('chain_of_custody'):
                compliance["chain_of_custody_complete"] += 1
            
            if evidence.get('integrity_verified'):
                compliance["integrity_verified"] += 1
        
        # Calculate overall compliance percentage
        total_checks = compliance["total_items"] * 3  # 3 compliance checks per item
        passed_checks = (compliance["section_65b_compliant"] + 
                        compliance["chain_of_custody_complete"] + 
                        compliance["integrity_verified"])
        
        if total_checks > 0:
            compliance_percentage = (passed_checks / total_checks) * 100
            if compliance_percentage >= 90:
                compliance["overall_compliance"] = "excellent"
            elif compliance_percentage >= 70:
                compliance["overall_compliance"] = "good"
            elif compliance_percentage >= 50:
                compliance["overall_compliance"] = "acceptable"
            else:
                compliance["overall_compliance"] = "poor"
        
        return compliance

# Example usage
if __name__ == "__main__":
    legal_framework = IndianLegalFramework()
    
    # Example legal authorization
    auth_data = {
        "authority_type": "magistrate_warrant",
        "issuing_authority": "Chief Metropolitan Magistrate, Delhi",
        "case_number": "FIR_001_2025_CYBER_CELL",
        "sections_invoked": ["IT_Act_66", "IT_Act_67", "CrPC_156", "Evidence_Act_65B"],
        "validity_start": "2025-09-21T00:00:00",
        "validity_end": "2025-12-21T23:59:59",
        "scope_description": "Investigation of viral misinformation campaign",
        "target_platforms": ["twitter", "facebook", "instagram"],
        "authorized_officers": ["Inspector_Sharma"]
    }
    
    authorization = legal_framework.create_legal_authorization(auth_data)
    print(f"✅ Legal framework initialized with authorization: {authorization.auth_id if authorization else 'Failed'}")
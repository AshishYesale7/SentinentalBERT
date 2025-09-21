#!/usr/bin/env python3
"""
InsideOut Evidence Management Service
Handles legal compliance, chain-of-custody, and encrypted evidence storage
"""

import asyncio
import logging
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="InsideOut Evidence Management Service", version="1.0.0")
security = HTTPBearer()

# Models
class WarrantDetails(BaseModel):
    warrant_id: str
    court_name: str
    judge_name: str
    case_number: str
    issued_date: datetime
    expiry_date: datetime
    scope: List[str]  # List of platforms/data types authorized
    jurisdiction: str
    digital_signature: str

class OfficerCredentials(BaseModel):
    officer_id: str
    badge_number: str
    name: str
    rank: str
    department: str
    phone: str
    email: str
    digital_certificate: str

class EvidenceItem(BaseModel):
    content_id: str
    platform: str
    content_type: str  # 'post', 'image', 'video', 'profile'
    content_data: Dict[str, Any]
    metadata: Dict[str, Any]
    provenance_data: Dict[str, Any]
    collection_timestamp: datetime

class EvidencePackage(BaseModel):
    collection_id: str
    warrant_id: str
    officer_id: str
    collection_timestamp: datetime
    evidence_items: List[EvidenceItem]
    legal_authority_verified: bool
    evidence_hash: str
    blockchain_hash: Optional[str] = None

class ChainOfCustodyRecord(BaseModel):
    record_id: str
    evidence_id: str
    officer_id: str
    officer_name: str
    action: str  # 'collected', 'transferred', 'analyzed', 'stored', 'accessed'
    timestamp: datetime
    digital_signature: str
    location: Optional[Dict] = None
    device_info: Optional[Dict] = None
    notes: Optional[str] = None

# Evidence Management System
class EvidenceManager:
    def __init__(self):
        # Initialize encryption
        self.encryption_key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Database connections
        self.pg_conn = psycopg2.connect(
            host='postgres',
            database='insideout',
            user='insideout',
            password='password'
        )
        
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        
        # Blockchain service (mock for now)
        self.blockchain_endpoint = os.getenv('BLOCKCHAIN_ENDPOINT', 'http://blockchain:8545')
        
        logger.info("Evidence Management System initialized")
    
    def _load_or_generate_key(self) -> bytes:
        """Load or generate encryption key"""
        key_file = '/app/data/encryption.key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    async def verify_legal_authority(self, warrant: WarrantDetails, officer: OfficerCredentials) -> Dict:
        """Verify legal authority before evidence collection"""
        validation_result = {
            'is_valid': False,
            'warrant_id': warrant.warrant_id,
            'officer_id': officer.officer_id,
            'validation_timestamp': datetime.utcnow(),
            'validation_errors': []
        }
        
        try:
            # Validate warrant authenticity
            if not await self._validate_warrant(warrant):
                validation_result['validation_errors'].append('Invalid or expired warrant')
                return validation_result
            
            # Verify officer credentials
            if not await self._verify_officer_credentials(officer):
                validation_result['validation_errors'].append('Invalid officer credentials')
                return validation_result
            
            # Check warrant scope and jurisdiction
            if not self._check_warrant_scope(warrant):
                validation_result['validation_errors'].append('Warrant scope insufficient for requested data')
                return validation_result
            
            # Check warrant expiry
            if warrant.expiry_date < datetime.utcnow():
                validation_result['validation_errors'].append('Warrant has expired')
                return validation_result
            
            validation_result['is_valid'] = True
            logger.info(f"Legal authority verified for warrant {warrant.warrant_id} and officer {officer.officer_id}")
            
        except Exception as e:
            logger.error(f"Error verifying legal authority: {str(e)}")
            validation_result['validation_errors'].append(f"Verification system error: {str(e)}")
        
        return validation_result
    
    async def _validate_warrant(self, warrant: WarrantDetails) -> bool:
        """Validate warrant with court system (mock implementation)"""
        try:
            # In production, this would connect to court database
            # For now, we'll do basic validation
            
            # Check required fields
            required_fields = ['warrant_id', 'court_name', 'judge_name', 'case_number']
            for field in required_fields:
                if not getattr(warrant, field):
                    return False
            
            # Validate digital signature (simplified)
            if not warrant.digital_signature or len(warrant.digital_signature) < 64:
                return False
            
            # Check warrant format
            if not warrant.warrant_id.startswith('WRT-'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating warrant: {str(e)}")
            return False
    
    async def _verify_officer_credentials(self, officer: OfficerCredentials) -> bool:
        """Verify officer credentials with police database"""
        try:
            # Check with police database
            with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM police_officers 
                    WHERE officer_id = %s AND badge_number = %s AND active = true
                """, (officer.officer_id, officer.badge_number))
                
                officer_record = cursor.fetchone()
                if not officer_record:
                    return False
                
                # Verify digital certificate (simplified)
                if not officer.digital_certificate:
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Error verifying officer credentials: {str(e)}")
            return False
    
    def _check_warrant_scope(self, warrant: WarrantDetails) -> bool:
        """Check if warrant scope covers requested data types"""
        try:
            # Check if warrant scope includes social media data
            required_scopes = ['social_media', 'digital_communications']
            return any(scope in warrant.scope for scope in required_scopes)
            
        except Exception as e:
            logger.error(f"Error checking warrant scope: {str(e)}")
            return False
    
    async def collect_evidence(self, content_ids: List[str], warrant: WarrantDetails, 
                             officer: OfficerCredentials) -> EvidencePackage:
        """Collect evidence with proper legal authority"""
        try:
            # Verify legal authority
            legal_authority = await self.verify_legal_authority(warrant, officer)
            if not legal_authority['is_valid']:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Unauthorized evidence collection: {legal_authority['validation_errors']}"
                )
            
            # Generate collection ID
            collection_id = f"EC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
            
            # Collect evidence items
            evidence_items = []
            for content_id in content_ids:
                evidence_item = await self._collect_single_evidence(content_id)
                if evidence_item:
                    evidence_items.append(evidence_item)
            
            if not evidence_items:
                raise HTTPException(status_code=404, detail="No evidence items found")
            
            # Create evidence package
            evidence_package = EvidencePackage(
                collection_id=collection_id,
                warrant_id=warrant.warrant_id,
                officer_id=officer.officer_id,
                collection_timestamp=datetime.utcnow(),
                evidence_items=evidence_items,
                legal_authority_verified=True,
                evidence_hash=self._calculate_evidence_hash(evidence_items)
            )
            
            # Encrypt and store evidence
            encrypted_package = await self._encrypt_and_store_evidence(evidence_package)
            
            # Create initial chain-of-custody record
            await self._create_custody_record(
                evidence_package.collection_id,
                officer.officer_id,
                officer.name,
                'collected'
            )
            
            # Store in blockchain (if available)
            blockchain_hash = await self._store_in_blockchain(evidence_package)
            evidence_package.blockchain_hash = blockchain_hash
            
            logger.info(f"Evidence collected: {collection_id} with {len(evidence_items)} items")
            return evidence_package
            
        except Exception as e:
            logger.error(f"Error collecting evidence: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Evidence collection failed: {str(e)}")
    
    async def _collect_single_evidence(self, content_id: str) -> Optional[EvidenceItem]:
        """Collect single piece of evidence with full provenance"""
        try:
            with self.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get content data
                cursor.execute("""
                    SELECT sp.*, up.username, up.display_name, up.follower_count,
                           up.verification_status, up.account_created
                    FROM social_posts sp
                    LEFT JOIN user_profiles up ON sp.author_id = up.id
                    WHERE sp.id = %s
                """, (content_id,))
                
                content_data = cursor.fetchone()
                if not content_data:
                    return None
                
                # Get provenance metadata
                provenance_data = await self._collect_provenance_metadata(content_id)
                
                # Create evidence item
                evidence_item = EvidenceItem(
                    content_id=content_id,
                    platform=content_data['platform'],
                    content_type='post',
                    content_data=dict(content_data),
                    metadata={
                        'collection_method': 'api',
                        'content_hash': hashlib.sha256(content_data['content'].encode()).hexdigest(),
                        'collection_ip': self._get_collection_ip(),
                        'user_agent': 'InsideOut-Evidence-Collector/1.0'
                    },
                    provenance_data=provenance_data,
                    collection_timestamp=datetime.utcnow()
                )
                
                return evidence_item
                
        except Exception as e:
            logger.error(f"Error collecting evidence for {content_id}: {str(e)}")
            return None
    
    async def _collect_provenance_metadata(self, content_id: str) -> Dict:
        """Collect complete provenance metadata for evidence"""
        try:
            provenance = {
                'original_url': f"https://platform.com/post/{content_id}",
                'collection_timestamp': datetime.utcnow().isoformat(),
                'server_logs': [],
                'ip_addresses': [],
                'device_fingerprints': [],
                'api_response_headers': {},
                'content_modifications': []
            }
            
            # In production, this would collect:
            # - Server logs from platform APIs
            # - IP address traces
            # - Device fingerprints
            # - Complete API response metadata
            # - Content modification history
            
            # Mock data for demonstration
            provenance['server_logs'] = [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'server': 'api.platform.com',
                    'request_id': str(uuid.uuid4()),
                    'response_code': 200
                }
            ]
            
            return provenance
            
        except Exception as e:
            logger.error(f"Error collecting provenance metadata: {str(e)}")
            return {}
    
    def _calculate_evidence_hash(self, evidence_items: List[EvidenceItem]) -> str:
        """Calculate cryptographic hash of evidence package"""
        try:
            # Combine all evidence data
            combined_data = ""
            for item in evidence_items:
                combined_data += json.dumps(item.dict(), sort_keys=True, default=str)
            
            # Calculate SHA-256 hash
            return hashlib.sha256(combined_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating evidence hash: {str(e)}")
            return ""
    
    async def _encrypt_and_store_evidence(self, evidence_package: EvidencePackage) -> str:
        """Encrypt evidence package and store securely"""
        try:
            # Serialize evidence package
            evidence_json = json.dumps(evidence_package.dict(), default=str)
            
            # Encrypt data
            encrypted_data = self.cipher_suite.encrypt(evidence_json.encode())
            
            # Store in database
            with self.pg_conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO evidence_collection 
                    (id, collection_id, warrant_id, officer_id, officer_name,
                     collection_timestamp, legal_authority_verified, evidence_hash,
                     encrypted_data, encryption_key_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    evidence_package.collection_id,
                    evidence_package.warrant_id,
                    evidence_package.officer_id,
                    'Officer Name',  # Would get from officer data
                    evidence_package.collection_timestamp,
                    evidence_package.legal_authority_verified,
                    evidence_package.evidence_hash,
                    encrypted_data,
                    'key-001'  # Key identifier
                ))
                
                self.pg_conn.commit()
            
            return evidence_package.collection_id
            
        except Exception as e:
            logger.error(f"Error encrypting and storing evidence: {str(e)}")
            raise
    
    async def _create_custody_record(self, evidence_id: str, officer_id: str, 
                                   officer_name: str, action: str) -> ChainOfCustodyRecord:
        """Create chain-of-custody record"""
        try:
            record = ChainOfCustodyRecord(
                record_id=str(uuid.uuid4()),
                evidence_id=evidence_id,
                officer_id=officer_id,
                officer_name=officer_name,
                action=action,
                timestamp=datetime.utcnow(),
                digital_signature=self._create_digital_signature(evidence_id, officer_id),
                location=self._get_officer_location(officer_id),
                device_info=self._get_device_fingerprint()
            )
            
            # Store in database
            with self.pg_conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO chain_of_custody
                    (id, evidence_id, record_id, officer_id, officer_name,
                     action_type, action_timestamp, digital_signature,
                     location_data, device_fingerprint)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    evidence_id,
                    record.record_id,
                    officer_id,
                    officer_name,
                    action,
                    record.timestamp,
                    record.digital_signature,
                    json.dumps(record.location) if record.location else None,
                    json.dumps(record.device_info) if record.device_info else None
                ))
                
                self.pg_conn.commit()
            
            # Store in blockchain
            blockchain_hash = await self._store_custody_in_blockchain(record)
            
            logger.info(f"Custody record created: {record.record_id}")
            return record
            
        except Exception as e:
            logger.error(f"Error creating custody record: {str(e)}")
            raise
    
    def _create_digital_signature(self, evidence_id: str, officer_id: str) -> str:
        """Create digital signature for custody record"""
        try:
            # In production, this would use proper PKI
            data_to_sign = f"{evidence_id}:{officer_id}:{datetime.utcnow().isoformat()}"
            signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
            return signature
            
        except Exception as e:
            logger.error(f"Error creating digital signature: {str(e)}")
            return ""
    
    def _get_officer_location(self, officer_id: str) -> Dict:
        """Get officer's current location"""
        # Mock implementation
        return {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'address': 'New Delhi Police Headquarters',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_device_fingerprint(self) -> Dict:
        """Get device fingerprint for audit trail"""
        return {
            'hostname': os.uname().nodename,
            'platform': os.uname().sysname,
            'ip_address': self._get_collection_ip(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_collection_ip(self) -> str:
        """Get IP address of collection system"""
        try:
            # In production, get actual IP
            return '192.168.1.100'
        except:
            return 'unknown'
    
    async def _store_in_blockchain(self, evidence_package: EvidencePackage) -> Optional[str]:
        """Store evidence hash in blockchain for immutability"""
        try:
            # Mock blockchain storage
            blockchain_data = {
                'collection_id': evidence_package.collection_id,
                'evidence_hash': evidence_package.evidence_hash,
                'timestamp': evidence_package.collection_timestamp.isoformat(),
                'warrant_id': evidence_package.warrant_id
            }
            
            # In production, this would interact with actual blockchain
            blockchain_hash = hashlib.sha256(json.dumps(blockchain_data).encode()).hexdigest()
            
            logger.info(f"Evidence stored in blockchain: {blockchain_hash}")
            return blockchain_hash
            
        except Exception as e:
            logger.error(f"Error storing in blockchain: {str(e)}")
            return None
    
    async def _store_custody_in_blockchain(self, record: ChainOfCustodyRecord) -> Optional[str]:
        """Store custody record in blockchain"""
        try:
            blockchain_data = {
                'record_id': record.record_id,
                'evidence_id': record.evidence_id,
                'action': record.action,
                'timestamp': record.timestamp.isoformat(),
                'officer_id': record.officer_id,
                'digital_signature': record.digital_signature
            }
            
            blockchain_hash = hashlib.sha256(json.dumps(blockchain_data).encode()).hexdigest()
            
            # Update custody record with blockchain hash
            with self.pg_conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE chain_of_custody 
                    SET blockchain_hash = %s 
                    WHERE record_id = %s
                """, (blockchain_hash, record.record_id))
                self.pg_conn.commit()
            
            return blockchain_hash
            
        except Exception as e:
            logger.error(f"Error storing custody in blockchain: {str(e)}")
            return None

# Initialize global evidence manager
evidence_manager = EvidenceManager()

# API Endpoints
@app.post("/verify-authority")
async def verify_legal_authority(warrant: WarrantDetails, officer: OfficerCredentials):
    """Verify legal authority for evidence collection"""
    return await evidence_manager.verify_legal_authority(warrant, officer)

@app.post("/collect-evidence", response_model=EvidencePackage)
async def collect_evidence(
    content_ids: List[str],
    warrant: WarrantDetails,
    officer: OfficerCredentials
):
    """Collect evidence with legal authority"""
    return await evidence_manager.collect_evidence(content_ids, warrant, officer)

@app.post("/custody-record")
async def create_custody_record(
    evidence_id: str,
    officer_id: str,
    officer_name: str,
    action: str
):
    """Create chain-of-custody record"""
    return await evidence_manager._create_custody_record(evidence_id, officer_id, officer_name, action)

@app.get("/evidence/{collection_id}")
async def get_evidence_package(collection_id: str):
    """Get evidence package details"""
    try:
        with evidence_manager.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM evidence_collection WHERE collection_id = %s
            """, (collection_id,))
            
            evidence_data = cursor.fetchone()
            if not evidence_data:
                raise HTTPException(status_code=404, detail="Evidence package not found")
            
            return {
                "collection_id": evidence_data['collection_id'],
                "warrant_id": evidence_data['warrant_id'],
                "officer_id": evidence_data['officer_id'],
                "collection_timestamp": evidence_data['collection_timestamp'],
                "evidence_hash": evidence_data['evidence_hash'],
                "blockchain_hash": evidence_data.get('blockchain_hash')
            }
            
    except Exception as e:
        logger.error(f"Error getting evidence package: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/custody-chain/{evidence_id}")
async def get_custody_chain(evidence_id: str):
    """Get complete chain-of-custody for evidence"""
    try:
        with evidence_manager.pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM chain_of_custody 
                WHERE evidence_id = %s 
                ORDER BY action_timestamp
            """, (evidence_id,))
            
            custody_records = cursor.fetchall()
            
            return {
                "evidence_id": evidence_id,
                "total_records": len(custody_records),
                "custody_chain": [dict(record) for record in custody_records]
            }
            
    except Exception as e:
        logger.error(f"Error getting custody chain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "evidence-management",
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
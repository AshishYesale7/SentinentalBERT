"""
InsideOut Platform - Security Monitoring System
Implements comprehensive security monitoring, SIEM, and incident response
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import re
from collections import defaultdict, deque
import aiofiles
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(Enum):
    """Security event types"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHORIZATION_FAILURE = "authorization_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    SYSTEM_ERROR = "system_error"
    CONFIGURATION_CHANGE = "configuration_change"
    NETWORK_ANOMALY = "network_anomaly"
    MALWARE_DETECTION = "malware_detection"
    INTRUSION_ATTEMPT = "intrusion_attempt"

class IncidentStatus(Enum):
    """Incident response status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: EventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    resource: str
    description: str
    raw_data: Dict[str, Any]
    indicators: List[str]
    mitre_tactics: List[str]  # MITRE ATT&CK tactics
    mitre_techniques: List[str]  # MITRE ATT&CK techniques

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    incident_id: str
    title: str
    description: str
    threat_level: ThreatLevel
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str]
    events: List[SecurityEvent]
    indicators_of_compromise: List[str]
    affected_systems: List[str]
    response_actions: List[str]
    timeline: List[Dict[str, Any]]

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    indicator: str
    indicator_type: str  # ip, domain, hash, etc.
    threat_level: ThreatLevel
    description: str
    source: str
    first_seen: datetime
    last_seen: datetime
    tags: List[str]

class SecurityMetrics:
    """Prometheus metrics for security monitoring"""
    
    def __init__(self):
        # Authentication metrics
        self.auth_attempts = Counter('insideout_auth_attempts_total', 
                                   'Total authentication attempts', 
                                   ['result', 'user_type'])
        
        self.auth_failures = Counter('insideout_auth_failures_total',
                                   'Authentication failures',
                                   ['reason', 'source_ip'])
        
        # Authorization metrics
        self.authz_checks = Counter('insideout_authorization_checks_total',
                                  'Authorization checks',
                                  ['resource', 'action', 'result'])
        
        # Security events
        self.security_events = Counter('insideout_security_events_total',
                                     'Security events',
                                     ['event_type', 'threat_level'])
        
        # System metrics
        self.active_sessions = Gauge('insideout_active_sessions',
                                   'Number of active user sessions')
        
        self.failed_requests = Counter('insideout_failed_requests_total',
                                     'Failed requests',
                                     ['endpoint', 'error_type'])
        
        # Response times
        self.request_duration = Histogram('insideout_request_duration_seconds',
                                        'Request duration',
                                        ['endpoint', 'method'])
        
        # Threat metrics
        self.threats_detected = Counter('insideout_threats_detected_total',
                                      'Threats detected',
                                      ['threat_type', 'severity'])
        
        self.incidents_created = Counter('insideout_incidents_created_total',
                                       'Security incidents created',
                                       ['severity'])

class ThreatDetectionEngine:
    """Advanced threat detection using behavioral analysis"""
    
    def __init__(self):
        self.failed_auth_threshold = 5
        self.time_window_minutes = 15
        self.suspicious_patterns = [
            r'(?i)(union|select|insert|delete|drop|create|alter)\s+',
            r'(?i)<script[^>]*>.*?</script>',
            r'(?i)javascript:',
            r'(?i)(exec|system|cmd|shell)',
            r'(?i)(\.\./){3,}',
            r'(?i)(passwd|shadow|hosts|config)',
        ]
        
        # Behavioral baselines
        self.user_baselines = defaultdict(dict)
        self.ip_reputation = defaultdict(int)
        
        # Recent events for correlation
        self.recent_events = deque(maxlen=10000)
    
    async def analyze_event(self, event: SecurityEvent) -> List[str]:
        """Analyze event for threats and return indicators"""
        threats = []
        
        # Pattern-based detection
        pattern_threats = self._detect_malicious_patterns(event)
        threats.extend(pattern_threats)
        
        # Behavioral analysis
        behavioral_threats = await self._analyze_behavioral_anomalies(event)
        threats.extend(behavioral_threats)
        
        # Correlation analysis
        correlation_threats = self._correlate_with_recent_events(event)
        threats.extend(correlation_threats)
        
        # IP reputation check
        ip_threats = await self._check_ip_reputation(event)
        threats.extend(ip_threats)
        
        # Add to recent events for future correlation
        self.recent_events.append(event)
        
        return threats
    
    def _detect_malicious_patterns(self, event: SecurityEvent) -> List[str]:
        """Detect malicious patterns in event data"""
        threats = []
        
        # Check raw data for suspicious patterns
        event_text = json.dumps(event.raw_data).lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, event_text):
                threats.append(f"Malicious pattern detected: {pattern}")
        
        # Check for SQL injection
        if re.search(r'(?i)(union|select).*?(from|where)', event_text):
            threats.append("Potential SQL injection attempt")
        
        # Check for XSS
        if re.search(r'(?i)<script|javascript:|on\w+\s*=', event_text):
            threats.append("Potential XSS attempt")
        
        # Check for command injection
        if re.search(r'(?i)(;|\||\&\&)\s*(cat|ls|ps|whoami|id)', event_text):
            threats.append("Potential command injection")
        
        return threats
    
    async def _analyze_behavioral_anomalies(self, event: SecurityEvent) -> List[str]:
        """Analyze behavioral anomalies"""
        threats = []
        
        if not event.user_id:
            return threats
        
        user_baseline = self.user_baselines.get(event.user_id, {})
        
        # Check authentication frequency
        if event.event_type == EventType.AUTHENTICATION_FAILURE:
            recent_failures = self._count_recent_events(
                event.user_id, EventType.AUTHENTICATION_FAILURE, 
                timedelta(minutes=self.time_window_minutes)
            )
            
            if recent_failures >= self.failed_auth_threshold:
                threats.append(f"Brute force attack detected: {recent_failures} failures")
        
        # Check unusual access times
        current_hour = event.timestamp.hour
        typical_hours = user_baseline.get('typical_hours', set())
        
        if typical_hours and current_hour not in typical_hours:
            if len(typical_hours) > 5:  # Only if we have enough baseline data
                threats.append("Unusual access time detected")
        else:
            # Update baseline
            if 'typical_hours' not in user_baseline:
                user_baseline['typical_hours'] = set()
            user_baseline['typical_hours'].add(current_hour)
        
        # Check unusual IP addresses
        typical_ips = user_baseline.get('typical_ips', set())
        if typical_ips and event.source_ip not in typical_ips:
            if len(typical_ips) > 2:  # Only if we have baseline data
                threats.append("Access from unusual IP address")
        else:
            # Update baseline
            if 'typical_ips' not in user_baseline:
                user_baseline['typical_ips'] = set()
            user_baseline['typical_ips'].add(event.source_ip)
        
        # Update user baseline
        self.user_baselines[event.user_id] = user_baseline
        
        return threats
    
    def _correlate_with_recent_events(self, event: SecurityEvent) -> List[str]:
        """Correlate event with recent events"""
        threats = []
        
        # Look for patterns in recent events
        recent_same_ip = [
            e for e in self.recent_events 
            if e.source_ip == event.source_ip and 
            (event.timestamp - e.timestamp) < timedelta(minutes=30)
        ]
        
        # Check for scanning behavior
        if len(recent_same_ip) > 20:
            unique_resources = set(e.resource for e in recent_same_ip)
            if len(unique_resources) > 10:
                threats.append("Potential scanning/reconnaissance activity")
        
        # Check for coordinated attacks
        if event.event_type == EventType.AUTHENTICATION_FAILURE:
            recent_auth_failures = [
                e for e in self.recent_events
                if e.event_type == EventType.AUTHENTICATION_FAILURE and
                (event.timestamp - e.timestamp) < timedelta(minutes=5)
            ]
            
            unique_ips = set(e.source_ip for e in recent_auth_failures)
            if len(unique_ips) > 5:
                threats.append("Potential distributed brute force attack")
        
        return threats
    
    async def _check_ip_reputation(self, event: SecurityEvent) -> List[str]:
        """Check IP reputation against threat intelligence"""
        threats = []
        
        # Update IP reputation based on behavior
        if event.event_type in [EventType.AUTHENTICATION_FAILURE, EventType.SUSPICIOUS_ACTIVITY]:
            self.ip_reputation[event.source_ip] -= 1
        elif event.event_type == EventType.AUTHENTICATION_SUCCESS:
            self.ip_reputation[event.source_ip] += 1
        
        # Check reputation score
        reputation = self.ip_reputation.get(event.source_ip, 0)
        if reputation < -10:
            threats.append(f"Low reputation IP address: {event.source_ip}")
        
        # TODO: Integrate with external threat intelligence feeds
        # This would check against known malicious IPs, domains, etc.
        
        return threats
    
    def _count_recent_events(self, user_id: str, event_type: EventType, 
                           time_window: timedelta) -> int:
        """Count recent events of specific type for user"""
        cutoff_time = datetime.utcnow() - time_window
        
        count = 0
        for event in self.recent_events:
            if (event.user_id == user_id and 
                event.event_type == event_type and 
                event.timestamp > cutoff_time):
                count += 1
        
        return count

class IncidentResponseSystem:
    """Automated incident response system"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.incidents = {}
        self.response_playbooks = self._load_response_playbooks()
    
    def _load_response_playbooks(self) -> Dict[str, List[str]]:
        """Load incident response playbooks"""
        return {
            'brute_force_attack': [
                'Block source IP address',
                'Notify security team',
                'Review authentication logs',
                'Check for successful logins from same IP',
                'Update threat intelligence'
            ],
            'sql_injection': [
                'Block malicious requests',
                'Review application logs',
                'Check database for unauthorized access',
                'Notify development team',
                'Update WAF rules'
            ],
            'unusual_access': [
                'Verify user identity',
                'Check for account compromise',
                'Review recent user activity',
                'Consider temporary account suspension',
                'Notify user and supervisor'
            ],
            'system_error': [
                'Check system health',
                'Review error logs',
                'Notify system administrators',
                'Monitor for cascading failures'
            ]
        }
    
    async def create_incident(self, events: List[SecurityEvent], 
                            threat_indicators: List[str]) -> SecurityIncident:
        """Create security incident from events"""
        incident_id = hashlib.md5(
            f"{events[0].event_id}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Determine threat level
        threat_level = max(event.threat_level for event in events)
        
        # Generate title and description
        title = self._generate_incident_title(events, threat_indicators)
        description = self._generate_incident_description(events, threat_indicators)
        
        # Identify affected systems
        affected_systems = list(set(event.resource for event in events))
        
        # Get response actions from playbooks
        response_actions = self._get_response_actions(threat_indicators)
        
        incident = SecurityIncident(
            incident_id=incident_id,
            title=title,
            description=description,
            threat_level=threat_level,
            status=IncidentStatus.OPEN,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            assigned_to=None,
            events=events,
            indicators_of_compromise=threat_indicators,
            affected_systems=affected_systems,
            response_actions=response_actions,
            timeline=[{
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'Incident created',
                'details': f'Created from {len(events)} security events'
            }]
        )
        
        # Store incident
        self.incidents[incident_id] = incident
        await self._store_incident_in_redis(incident)
        
        # Trigger automated response
        await self._trigger_automated_response(incident)
        
        logger.info(f"Security incident created: {incident_id} - {title}")
        return incident
    
    def _generate_incident_title(self, events: List[SecurityEvent], 
                                indicators: List[str]) -> str:
        """Generate incident title"""
        if any('brute force' in indicator.lower() for indicator in indicators):
            return "Brute Force Attack Detected"
        elif any('injection' in indicator.lower() for indicator in indicators):
            return "Injection Attack Detected"
        elif any('unusual' in indicator.lower() for indicator in indicators):
            return "Unusual Access Pattern Detected"
        elif any('scanning' in indicator.lower() for indicator in indicators):
            return "Network Scanning Activity Detected"
        else:
            return f"Security Incident - {events[0].event_type.value}"
    
    def _generate_incident_description(self, events: List[SecurityEvent], 
                                     indicators: List[str]) -> str:
        """Generate incident description"""
        description = f"Security incident involving {len(events)} events:\n\n"
        
        # Event summary
        event_types = defaultdict(int)
        source_ips = set()
        users = set()
        
        for event in events:
            event_types[event.event_type.value] += 1
            source_ips.add(event.source_ip)
            if event.user_id:
                users.add(event.user_id)
        
        description += "Event Summary:\n"
        for event_type, count in event_types.items():
            description += f"- {event_type}: {count}\n"
        
        description += f"\nSource IPs: {', '.join(source_ips)}\n"
        if users:
            description += f"Affected Users: {', '.join(users)}\n"
        
        description += f"\nThreat Indicators:\n"
        for indicator in indicators:
            description += f"- {indicator}\n"
        
        return description
    
    def _get_response_actions(self, indicators: List[str]) -> List[str]:
        """Get response actions based on threat indicators"""
        actions = set()
        
        for indicator in indicators:
            if 'brute force' in indicator.lower():
                actions.update(self.response_playbooks.get('brute_force_attack', []))
            elif 'injection' in indicator.lower():
                actions.update(self.response_playbooks.get('sql_injection', []))
            elif 'unusual' in indicator.lower():
                actions.update(self.response_playbooks.get('unusual_access', []))
        
        return list(actions)
    
    async def _store_incident_in_redis(self, incident: SecurityIncident):
        """Store incident in Redis for persistence"""
        incident_data = asdict(incident)
        # Convert datetime objects to ISO strings
        incident_data['created_at'] = incident.created_at.isoformat()
        incident_data['updated_at'] = incident.updated_at.isoformat()
        
        await self.redis.setex(
            f"incident:{incident.incident_id}",
            86400 * 30,  # 30 days
            json.dumps(incident_data, default=str)
        )
    
    async def _trigger_automated_response(self, incident: SecurityIncident):
        """Trigger automated response actions"""
        if incident.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            # Send immediate alerts
            await self._send_alert(incident)
        
        # Execute automated response actions
        for action in incident.response_actions:
            if 'Block source IP' in action:
                await self._block_ip_addresses(incident)
            elif 'Notify' in action:
                await self._send_notification(incident, action)
    
    async def _send_alert(self, incident: SecurityIncident):
        """Send security alert"""
        alert_data = {
            'incident_id': incident.incident_id,
            'title': incident.title,
            'threat_level': incident.threat_level.value,
            'description': incident.description,
            'timestamp': incident.created_at.isoformat()
        }
        
        # Store alert in Redis for processing by alert system
        await self.redis.lpush('security_alerts', json.dumps(alert_data))
        logger.critical(f"Security alert sent: {incident.title}")
    
    async def _block_ip_addresses(self, incident: SecurityIncident):
        """Block malicious IP addresses"""
        ips_to_block = set()
        
        for event in incident.events:
            if any('brute force' in indicator.lower() or 'scanning' in indicator.lower() 
                   for indicator in incident.indicators_of_compromise):
                ips_to_block.add(event.source_ip)
        
        for ip in ips_to_block:
            # Add to blocked IPs list
            await self.redis.sadd('blocked_ips', ip)
            await self.redis.expire('blocked_ips', 86400)  # 24 hours
            logger.warning(f"IP address blocked: {ip}")
    
    async def _send_notification(self, incident: SecurityIncident, action: str):
        """Send notification to relevant teams"""
        notification = {
            'incident_id': incident.incident_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'details': incident.description
        }
        
        await self.redis.lpush('notifications', json.dumps(notification))
        logger.info(f"Notification sent: {action}")

class SecurityMonitoringSystem:
    """Main security monitoring system"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.metrics = SecurityMetrics()
        self.threat_detector = ThreatDetectionEngine()
        self.incident_response = IncidentResponseSystem(self.redis)
        
        # Event processing queue
        self.event_queue = asyncio.Queue()
        self.processing_tasks = []
        
        # Start metrics server
        start_http_server(8090)
        logger.info("Security monitoring system initialized")
    
    async def start(self):
        """Start security monitoring"""
        # Start event processing tasks
        for i in range(3):  # 3 worker tasks
            task = asyncio.create_task(self._process_events())
            self.processing_tasks.append(task)
        
        logger.info("Security monitoring started")
    
    async def stop(self):
        """Stop security monitoring"""
        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        await self.redis.close()
        
        logger.info("Security monitoring stopped")
    
    async def log_security_event(self, event: SecurityEvent):
        """Log security event for processing"""
        # Update metrics
        self.metrics.security_events.labels(
            event_type=event.event_type.value,
            threat_level=event.threat_level.value
        ).inc()
        
        # Add to processing queue
        await self.event_queue.put(event)
        
        # Store in Redis for persistence
        await self._store_event_in_redis(event)
    
    async def _process_events(self):
        """Process security events"""
        while True:
            try:
                event = await self.event_queue.get()
                
                # Analyze event for threats
                threat_indicators = await self.threat_detector.analyze_event(event)
                
                if threat_indicators:
                    # Create incident if threats detected
                    await self.incident_response.create_incident([event], threat_indicators)
                    
                    # Update threat metrics
                    self.metrics.threats_detected.labels(
                        threat_type=event.event_type.value,
                        severity=event.threat_level.value
                    ).inc()
                
                self.event_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing security event: {str(e)}")
    
    async def _store_event_in_redis(self, event: SecurityEvent):
        """Store event in Redis"""
        event_data = asdict(event)
        event_data['timestamp'] = event.timestamp.isoformat()
        
        # Store individual event
        await self.redis.setex(
            f"event:{event.event_id}",
            86400 * 7,  # 7 days
            json.dumps(event_data, default=str)
        )
        
        # Add to time-series for analysis
        await self.redis.zadd(
            'security_events_timeline',
            {event.event_id: event.timestamp.timestamp()}
        )
    
    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get data for security dashboard"""
        # Get recent events
        recent_events_ids = await self.redis.zrevrange(
            'security_events_timeline', 0, 100
        )
        
        # Get incident counts
        incident_count = len(self.incident_response.incidents)
        
        # Get blocked IPs
        blocked_ips = await self.redis.scard('blocked_ips')
        
        # Get threat statistics
        threat_stats = defaultdict(int)
        for event_id in recent_events_ids[:50]:  # Last 50 events
            event_data = await self.redis.get(f"event:{event_id}")
            if event_data:
                event = json.loads(event_data)
                threat_stats[event['threat_level']] += 1
        
        return {
            'recent_events_count': len(recent_events_ids),
            'active_incidents': incident_count,
            'blocked_ips': blocked_ips,
            'threat_distribution': dict(threat_stats),
            'system_status': 'operational',
            'last_updated': datetime.utcnow().isoformat()
        }

# Example usage
async def main():
    """Example usage of security monitoring system"""
    
    # Initialize monitoring system
    monitoring = SecurityMonitoringSystem()
    await monitoring.start()
    
    # Create sample security events
    events = [
        SecurityEvent(
            event_id="evt_001",
            event_type=EventType.AUTHENTICATION_FAILURE,
            threat_level=ThreatLevel.MEDIUM,
            timestamp=datetime.utcnow(),
            source_ip="192.168.1.100",
            user_id="officer123",
            resource="/api/v1/auth/login",
            description="Failed login attempt",
            raw_data={"username": "officer123", "password": "wrong_password"},
            indicators=[],
            mitre_tactics=["TA0006"],  # Credential Access
            mitre_techniques=["T1110"]  # Brute Force
        ),
        SecurityEvent(
            event_id="evt_002",
            event_type=EventType.SUSPICIOUS_ACTIVITY,
            threat_level=ThreatLevel.HIGH,
            timestamp=datetime.utcnow(),
            source_ip="10.0.0.50",
            user_id=None,
            resource="/api/v1/search",
            description="Suspicious SQL injection attempt",
            raw_data={"query": "'; DROP TABLE users; --"},
            indicators=["sql_injection"],
            mitre_tactics=["TA0001"],  # Initial Access
            mitre_techniques=["T1190"]  # Exploit Public-Facing Application
        )
    ]
    
    # Log events
    for event in events:
        await monitoring.log_security_event(event)
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Get dashboard data
    dashboard_data = await monitoring.get_security_dashboard_data()
    print("Security Dashboard Data:")
    print(json.dumps(dashboard_data, indent=2))
    
    # Stop monitoring
    await monitoring.stop()

if __name__ == "__main__":
    asyncio.run(main())
"""
InsideOut Platform - Secure Configuration Management
Implements secure configuration with environment variables and secrets management
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from cryptography.fernet import Fernet
import base64
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class SecurityLevel(Enum):
    """Security levels for different components"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str  # Encrypted in production
    ssl_mode: str = "require"
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str
    port: int
    password: str  # Encrypted in production
    database: int = 0
    ssl: bool = True
    connection_pool_size: int = 50

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str  # Encrypted
    encryption_key: str  # Encrypted
    session_timeout_hours: int = 8
    mfa_required: bool = True
    password_policy: Dict[str, Any] = None
    rate_limiting: Dict[str, Any] = None
    allowed_origins: list = None

@dataclass
class LegalConfig:
    """Legal compliance configuration"""
    court_api_endpoint: str
    court_api_key: str  # Encrypted
    warrant_verification_required: bool = True
    constitutional_compliance_checks: bool = True
    gdpr_compliance: bool = True
    data_retention_days: int = 2555  # 7 years

@dataclass
class BlockchainConfig:
    """Blockchain configuration"""
    provider_url: str
    contract_address: str
    private_key: str  # Encrypted
    gas_limit: int = 200000
    gas_price_gwei: int = 20

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: str = "INFO"
    audit_log_enabled: bool = True
    metrics_enabled: bool = True
    prometheus_endpoint: str = "http://prometheus:9090"
    grafana_endpoint: str = "http://grafana:3000"
    jaeger_endpoint: str = "http://jaeger:14268"

@dataclass
class APIConfig:
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8080
    ssl_enabled: bool = True
    ssl_cert_path: str = "/etc/ssl/certs/insideout.crt"
    ssl_key_path: str = "/etc/ssl/private/insideout.key"
    cors_enabled: bool = True
    rate_limiting_enabled: bool = True
    request_timeout_seconds: int = 30

class SecureConfigManager:
    """Secure configuration manager with encryption and validation"""
    
    def __init__(self, environment: Environment = Environment.PRODUCTION):
        self.environment = environment
        self.config_encryption_key = self._get_or_create_config_key()
        self.cipher = Fernet(self.config_encryption_key)
        
        # Load configuration
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.security = self._load_security_config()
        self.legal = self._load_legal_config()
        self.blockchain = self._load_blockchain_config()
        self.monitoring = self._load_monitoring_config()
        self.api = self._load_api_config()
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"Configuration loaded for environment: {environment.value}")
    
    def _get_or_create_config_key(self) -> bytes:
        """Get or create configuration encryption key"""
        key_env = os.getenv('INSIDEOUT_CONFIG_KEY')
        if key_env:
            return base64.urlsafe_b64decode(key_env.encode())
        
        # Generate new key (should be stored securely in production)
        key = Fernet.generate_key()
        logger.warning("Generated new configuration encryption key - store securely!")
        return key
    
    def _encrypt_secret(self, value: str) -> str:
        """Encrypt a secret value"""
        if not value:
            return value
        return self.cipher.encrypt(value.encode()).decode()
    
    def _decrypt_secret(self, encrypted_value: str) -> str:
        """Decrypt a secret value"""
        if not encrypted_value:
            return encrypted_value
        try:
            return self.cipher.decrypt(encrypted_value.encode()).decode()
        except Exception:
            # If decryption fails, assume it's already decrypted (for development)
            return encrypted_value
    
    def _get_env_var(self, key: str, default: Any = None, required: bool = False, 
                    encrypted: bool = False) -> Any:
        """Get environment variable with optional decryption"""
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(f"Required environment variable {key} not set")
        
        if encrypted and value:
            value = self._decrypt_secret(value)
        
        return value
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            host=self._get_env_var('DB_HOST', 'localhost', required=True),
            port=int(self._get_env_var('DB_PORT', 5432)),
            database=self._get_env_var('DB_NAME', 'insideout', required=True),
            username=self._get_env_var('DB_USERNAME', 'insideout', required=True),
            password=self._get_env_var('DB_PASSWORD', required=True, encrypted=True),
            ssl_mode=self._get_env_var('DB_SSL_MODE', 'require'),
            connection_pool_size=int(self._get_env_var('DB_POOL_SIZE', 20)),
            max_overflow=int(self._get_env_var('DB_MAX_OVERFLOW', 30)),
            pool_timeout=int(self._get_env_var('DB_POOL_TIMEOUT', 30))
        )
    
    def _load_redis_config(self) -> RedisConfig:
        """Load Redis configuration"""
        return RedisConfig(
            host=self._get_env_var('REDIS_HOST', 'localhost', required=True),
            port=int(self._get_env_var('REDIS_PORT', 6379)),
            password=self._get_env_var('REDIS_PASSWORD', required=True, encrypted=True),
            database=int(self._get_env_var('REDIS_DB', 0)),
            ssl=self._get_env_var('REDIS_SSL', 'true').lower() == 'true',
            connection_pool_size=int(self._get_env_var('REDIS_POOL_SIZE', 50))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        password_policy = {
            'min_length': int(self._get_env_var('PASSWORD_MIN_LENGTH', 12)),
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special_chars': True,
            'max_age_days': int(self._get_env_var('PASSWORD_MAX_AGE_DAYS', 90)),
            'history_count': int(self._get_env_var('PASSWORD_HISTORY_COUNT', 5))
        }
        
        rate_limiting = {
            'authentication': {'requests': 10, 'window': 300},
            'search': {'requests': 100, 'window': 3600},
            'analysis': {'requests': 50, 'window': 3600},
            'evidence': {'requests': 200, 'window': 3600}
        }
        
        allowed_origins = [
            'https://insideout.gov.in',
            'https://dashboard.insideout.gov.in'
        ]
        
        return SecurityConfig(
            jwt_secret=self._get_env_var('JWT_SECRET', required=True, encrypted=True),
            encryption_key=self._get_env_var('ENCRYPTION_KEY', required=True, encrypted=True),
            session_timeout_hours=int(self._get_env_var('SESSION_TIMEOUT_HOURS', 8)),
            mfa_required=self._get_env_var('MFA_REQUIRED', 'true').lower() == 'true',
            password_policy=password_policy,
            rate_limiting=rate_limiting,
            allowed_origins=allowed_origins
        )
    
    def _load_legal_config(self) -> LegalConfig:
        """Load legal compliance configuration"""
        return LegalConfig(
            court_api_endpoint=self._get_env_var('COURT_API_ENDPOINT', required=True),
            court_api_key=self._get_env_var('COURT_API_KEY', required=True, encrypted=True),
            warrant_verification_required=self._get_env_var('WARRANT_VERIFICATION_REQUIRED', 'true').lower() == 'true',
            constitutional_compliance_checks=self._get_env_var('CONSTITUTIONAL_COMPLIANCE', 'true').lower() == 'true',
            gdpr_compliance=self._get_env_var('GDPR_COMPLIANCE', 'true').lower() == 'true',
            data_retention_days=int(self._get_env_var('DATA_RETENTION_DAYS', 2555))
        )
    
    def _load_blockchain_config(self) -> BlockchainConfig:
        """Load blockchain configuration"""
        return BlockchainConfig(
            provider_url=self._get_env_var('BLOCKCHAIN_PROVIDER_URL', required=True),
            contract_address=self._get_env_var('BLOCKCHAIN_CONTRACT_ADDRESS', required=True),
            private_key=self._get_env_var('BLOCKCHAIN_PRIVATE_KEY', required=True, encrypted=True),
            gas_limit=int(self._get_env_var('BLOCKCHAIN_GAS_LIMIT', 200000)),
            gas_price_gwei=int(self._get_env_var('BLOCKCHAIN_GAS_PRICE_GWEI', 20))
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        """Load monitoring configuration"""
        return MonitoringConfig(
            log_level=self._get_env_var('LOG_LEVEL', 'INFO'),
            audit_log_enabled=self._get_env_var('AUDIT_LOG_ENABLED', 'true').lower() == 'true',
            metrics_enabled=self._get_env_var('METRICS_ENABLED', 'true').lower() == 'true',
            prometheus_endpoint=self._get_env_var('PROMETHEUS_ENDPOINT', 'http://prometheus:9090'),
            grafana_endpoint=self._get_env_var('GRAFANA_ENDPOINT', 'http://grafana:3000'),
            jaeger_endpoint=self._get_env_var('JAEGER_ENDPOINT', 'http://jaeger:14268')
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration"""
        return APIConfig(
            host=self._get_env_var('API_HOST', '0.0.0.0'),
            port=int(self._get_env_var('API_PORT', 8080)),
            ssl_enabled=self._get_env_var('API_SSL_ENABLED', 'true').lower() == 'true',
            ssl_cert_path=self._get_env_var('API_SSL_CERT_PATH', '/etc/ssl/certs/insideout.crt'),
            ssl_key_path=self._get_env_var('API_SSL_KEY_PATH', '/etc/ssl/private/insideout.key'),
            cors_enabled=self._get_env_var('API_CORS_ENABLED', 'true').lower() == 'true',
            rate_limiting_enabled=self._get_env_var('API_RATE_LIMITING_ENABLED', 'true').lower() == 'true',
            request_timeout_seconds=int(self._get_env_var('API_REQUEST_TIMEOUT', 30))
        )
    
    def _validate_configuration(self):
        """Validate configuration for security and completeness"""
        errors = []
        warnings = []
        
        # Database validation
        if not self.database.password:
            errors.append("Database password not configured")
        
        if self.database.ssl_mode not in ['require', 'verify-full']:
            warnings.append("Database SSL mode should be 'require' or 'verify-full' for production")
        
        # Security validation
        if len(self.security.jwt_secret) < 32:
            errors.append("JWT secret must be at least 32 characters")
        
        if not self.security.mfa_required and self.environment == Environment.PRODUCTION:
            warnings.append("MFA should be required in production")
        
        # Legal validation
        if not self.legal.warrant_verification_required and self.environment == Environment.PRODUCTION:
            errors.append("Warrant verification must be required in production")
        
        # API validation
        if not self.api.ssl_enabled and self.environment == Environment.PRODUCTION:
            errors.append("SSL must be enabled in production")
        
        if not os.path.exists(self.api.ssl_cert_path) and self.api.ssl_enabled:
            warnings.append(f"SSL certificate not found: {self.api.ssl_cert_path}")
        
        # Log validation results
        if errors:
            logger.error(f"Configuration validation errors: {errors}")
            raise ValueError(f"Configuration validation failed: {errors}")
        
        if warnings:
            logger.warning(f"Configuration validation warnings: {warnings}")
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return (f"postgresql://{self.database.username}:{self.database.password}@"
                f"{self.database.host}:{self.database.port}/{self.database.database}"
                f"?sslmode={self.database.ssl_mode}")
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        protocol = "rediss" if self.redis.ssl else "redis"
        return f"{protocol}://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.database}"
    
    def export_config_template(self, file_path: str):
        """Export configuration template for deployment"""
        template = {
            "# Database Configuration": None,
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "insideout",
            "DB_USERNAME": "insideout",
            "DB_PASSWORD": "ENCRYPTED_PASSWORD_HERE",
            "DB_SSL_MODE": "require",
            
            "# Redis Configuration": None,
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "REDIS_PASSWORD": "ENCRYPTED_PASSWORD_HERE",
            "REDIS_SSL": "true",
            
            "# Security Configuration": None,
            "JWT_SECRET": "ENCRYPTED_JWT_SECRET_HERE",
            "ENCRYPTION_KEY": "ENCRYPTED_ENCRYPTION_KEY_HERE",
            "SESSION_TIMEOUT_HOURS": "8",
            "MFA_REQUIRED": "true",
            
            "# Legal Configuration": None,
            "COURT_API_ENDPOINT": "https://court-api.gov.in",
            "COURT_API_KEY": "ENCRYPTED_API_KEY_HERE",
            "WARRANT_VERIFICATION_REQUIRED": "true",
            
            "# Blockchain Configuration": None,
            "BLOCKCHAIN_PROVIDER_URL": "https://ethereum-node.gov.in",
            "BLOCKCHAIN_CONTRACT_ADDRESS": "0x...",
            "BLOCKCHAIN_PRIVATE_KEY": "ENCRYPTED_PRIVATE_KEY_HERE",
            
            "# API Configuration": None,
            "API_HOST": "0.0.0.0",
            "API_PORT": "8080",
            "API_SSL_ENABLED": "true",
            "API_SSL_CERT_PATH": "/etc/ssl/certs/insideout.crt",
            "API_SSL_KEY_PATH": "/etc/ssl/private/insideout.key"
        }
        
        with open(file_path, 'w') as f:
            for key, value in template.items():
                if value is None:
                    f.write(f"\n{key}\n")
                else:
                    f.write(f"{key}={value}\n")
        
        logger.info(f"Configuration template exported to {file_path}")
    
    def encrypt_secrets_for_deployment(self, secrets: Dict[str, str]) -> Dict[str, str]:
        """Encrypt secrets for secure deployment"""
        encrypted_secrets = {}
        for key, value in secrets.items():
            encrypted_secrets[key] = self._encrypt_secret(value)
        return encrypted_secrets
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; media-src 'none'; object-src 'none'; child-src 'none'; frame-ancestors 'none'; form-action 'self'; base-uri 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), speaker=(), vibrate=(), fullscreen=(self), sync-xhr=()"
        }

# Global configuration instance
config_manager: Optional[SecureConfigManager] = None

def get_config() -> SecureConfigManager:
    """Get global configuration instance"""
    global config_manager
    if config_manager is None:
        env = Environment(os.getenv('INSIDEOUT_ENVIRONMENT', 'production'))
        config_manager = SecureConfigManager(env)
    return config_manager

def initialize_config(environment: Environment = Environment.PRODUCTION) -> SecureConfigManager:
    """Initialize configuration with specific environment"""
    global config_manager
    config_manager = SecureConfigManager(environment)
    return config_manager

# Example usage
if __name__ == "__main__":
    # Initialize configuration
    config = initialize_config(Environment.DEVELOPMENT)
    
    # Print configuration summary (without secrets)
    print(f"Environment: {config.environment.value}")
    print(f"Database Host: {config.database.host}")
    print(f"API Port: {config.api.port}")
    print(f"SSL Enabled: {config.api.ssl_enabled}")
    print(f"MFA Required: {config.security.mfa_required}")
    
    # Export configuration template
    config.export_config_template("insideout.env.template")
    
    # Example of encrypting secrets
    secrets = {
        "DB_PASSWORD": "super_secure_password",
        "JWT_SECRET": "very_long_jwt_secret_key_here",
        "COURT_API_KEY": "court_api_key_here"
    }
    
    encrypted_secrets = config.encrypt_secrets_for_deployment(secrets)
    print("Encrypted secrets for deployment:")
    for key, value in encrypted_secrets.items():
        print(f"{key}={value}")
-- InsideOut Platform Enhanced Database Schema
-- Extends existing SentinentalBERT schema with viral detection and evidence management

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Viral Content Clusters Table
CREATE TABLE IF NOT EXISTS viral_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_hash VARCHAR(64) UNIQUE NOT NULL,
    original_post_id VARCHAR(255) NOT NULL,
    similarity_threshold DECIMAL(3,2) NOT NULL DEFAULT 0.85,
    viral_score DECIMAL(10,4) NOT NULL DEFAULT 0.0,
    first_detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_posts INTEGER DEFAULT 0,
    total_reach BIGINT DEFAULT 0,
    geographic_spread JSONB,
    influence_network JSONB,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'monitored', 'resolved'
    priority_level VARCHAR(10) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    
    CONSTRAINT viral_score_range CHECK (viral_score >= 0 AND viral_score <= 10),
    CONSTRAINT similarity_threshold_range CHECK (similarity_threshold >= 0 AND similarity_threshold <= 1)
);

-- Indexes for viral_clusters
CREATE INDEX IF NOT EXISTS idx_viral_clusters_score ON viral_clusters (viral_score DESC);
CREATE INDEX IF NOT EXISTS idx_viral_clusters_detected ON viral_clusters (first_detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_viral_clusters_status ON viral_clusters (status);
CREATE INDEX IF NOT EXISTS idx_viral_clusters_priority ON viral_clusters (priority_level);
CREATE INDEX IF NOT EXISTS idx_viral_clusters_geographic USING GIN (geographic_spread);

-- Content Propagation Chain Table
CREATE TABLE IF NOT EXISTS content_propagation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cluster_id UUID REFERENCES viral_clusters(id) ON DELETE CASCADE,
    post_id VARCHAR(255) NOT NULL,
    parent_post_id VARCHAR(255),
    author_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    propagation_level INTEGER NOT NULL DEFAULT 0,
    propagation_timestamp TIMESTAMP NOT NULL,
    influence_score DECIMAL(10,4) DEFAULT 0.0,
    reach_estimate BIGINT DEFAULT 0,
    engagement_metrics JSONB,
    content_similarity DECIMAL(3,2) DEFAULT 0.0,
    
    UNIQUE(cluster_id, post_id)
);

-- Indexes for content_propagation
CREATE INDEX IF NOT EXISTS idx_propagation_cluster_level ON content_propagation (cluster_id, propagation_level);
CREATE INDEX IF NOT EXISTS idx_propagation_timestamp ON content_propagation (propagation_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_propagation_author ON content_propagation (author_id);
CREATE INDEX IF NOT EXISTS idx_propagation_platform ON content_propagation (platform);

-- Police Officers Table
CREATE TABLE IF NOT EXISTS police_officers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    officer_id VARCHAR(50) UNIQUE NOT NULL,
    badge_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    rank VARCHAR(100) NOT NULL,
    department VARCHAR(255) NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    digital_certificate TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    permissions JSONB DEFAULT '[]'::jsonb
);

-- Indexes for police_officers
CREATE INDEX IF NOT EXISTS idx_officers_badge ON police_officers (badge_number);
CREATE INDEX IF NOT EXISTS idx_officers_department ON police_officers (department);
CREATE INDEX IF NOT EXISTS idx_officers_state ON police_officers (state);
CREATE INDEX IF NOT EXISTS idx_officers_active ON police_officers (active);

-- Evidence Collection Table
CREATE TABLE IF NOT EXISTS evidence_collection (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id VARCHAR(255) UNIQUE NOT NULL,
    warrant_id VARCHAR(255) NOT NULL,
    officer_id VARCHAR(255) NOT NULL,
    officer_name VARCHAR(255) NOT NULL,
    collection_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    legal_authority_verified BOOLEAN NOT NULL DEFAULT false,
    evidence_hash VARCHAR(64) NOT NULL,
    blockchain_hash VARCHAR(64),
    encrypted_data BYTEA, -- Encrypted evidence package
    encryption_key_id VARCHAR(255) NOT NULL,
    case_number VARCHAR(255),
    court_name VARCHAR(255),
    judge_name VARCHAR(255),
    evidence_type VARCHAR(50) DEFAULT 'social_media', -- 'social_media', 'digital_communication', 'metadata'
    status VARCHAR(20) DEFAULT 'collected' -- 'collected', 'analyzed', 'submitted', 'archived'
);

-- Indexes for evidence_collection
CREATE INDEX IF NOT EXISTS idx_evidence_warrant ON evidence_collection (warrant_id);
CREATE INDEX IF NOT EXISTS idx_evidence_officer ON evidence_collection (officer_id);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence_collection (case_number);
CREATE INDEX IF NOT EXISTS idx_evidence_timestamp ON evidence_collection (collection_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_status ON evidence_collection (status);

-- Chain of Custody Table
CREATE TABLE IF NOT EXISTS chain_of_custody (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id UUID REFERENCES evidence_collection(id) ON DELETE CASCADE,
    record_id VARCHAR(255) UNIQUE NOT NULL,
    officer_id VARCHAR(255) NOT NULL,
    officer_name VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 'collected', 'transferred', 'analyzed', 'stored', 'accessed', 'exported'
    action_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    digital_signature VARCHAR(512) NOT NULL,
    blockchain_hash VARCHAR(64) NOT NULL,
    location_data JSONB,
    device_fingerprint VARCHAR(255),
    notes TEXT,
    previous_officer_id VARCHAR(255) -- For transfers
);

-- Indexes for chain_of_custody
CREATE INDEX IF NOT EXISTS idx_custody_evidence ON chain_of_custody (evidence_id);
CREATE INDEX IF NOT EXISTS idx_custody_timestamp ON chain_of_custody (action_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_custody_officer ON chain_of_custody (officer_id);
CREATE INDEX IF NOT EXISTS idx_custody_action ON chain_of_custody (action_type);

-- Indian Geographic Data Table
CREATE TABLE IF NOT EXISTS indian_geographic_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_name VARCHAR(100) NOT NULL,
    state_code VARCHAR(10) NOT NULL,
    district_name VARCHAR(100),
    city_name VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    population BIGINT,
    police_station_code VARCHAR(20),
    jurisdiction_level VARCHAR(20) DEFAULT 'district', -- 'state', 'district', 'city', 'station'
    area_sq_km DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for indian_geographic_data
CREATE INDEX IF NOT EXISTS idx_geo_state_district ON indian_geographic_data (state_name, district_name);
CREATE INDEX IF NOT EXISTS idx_geo_coordinates ON indian_geographic_data (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_geo_police_station ON indian_geographic_data (police_station_code);
CREATE INDEX IF NOT EXISTS idx_geo_jurisdiction ON indian_geographic_data (jurisdiction_level);

-- Multi-language Content Table
CREATE TABLE IF NOT EXISTS multilingual_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id VARCHAR(255) NOT NULL,
    original_language VARCHAR(10) NOT NULL,
    detected_languages JSONB NOT NULL DEFAULT '[]'::jsonb, -- Array of detected languages with confidence
    translated_content JSONB DEFAULT '{}'::jsonb, -- Translations in different languages
    language_confidence DECIMAL(3,2) DEFAULT 0.0,
    translation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(post_id)
);

-- Indexes for multilingual_content
CREATE INDEX IF NOT EXISTS idx_multilingual_post ON multilingual_content (post_id);
CREATE INDEX IF NOT EXISTS idx_multilingual_language ON multilingual_content (original_language);
CREATE INDEX IF NOT EXISTS idx_multilingual_detected USING GIN (detected_languages);

-- Warrant Registry Table
CREATE TABLE IF NOT EXISTS warrant_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warrant_id VARCHAR(255) UNIQUE NOT NULL,
    court_name VARCHAR(255) NOT NULL,
    judge_name VARCHAR(255) NOT NULL,
    case_number VARCHAR(255) NOT NULL,
    issued_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    scope JSONB NOT NULL DEFAULT '[]'::jsonb, -- Array of authorized data types/platforms
    jurisdiction VARCHAR(255) NOT NULL,
    digital_signature TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'revoked', 'executed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_dates CHECK (expiry_date > issued_date)
);

-- Indexes for warrant_registry
CREATE INDEX IF NOT EXISTS idx_warrant_id ON warrant_registry (warrant_id);
CREATE INDEX IF NOT EXISTS idx_warrant_case ON warrant_registry (case_number);
CREATE INDEX IF NOT EXISTS idx_warrant_status ON warrant_registry (status);
CREATE INDEX IF NOT EXISTS idx_warrant_expiry ON warrant_registry (expiry_date);
CREATE INDEX IF NOT EXISTS idx_warrant_scope USING GIN (scope);

-- System Configuration Table
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general',
    is_sensitive BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default system configurations
INSERT INTO system_config (config_key, config_value, description, category) VALUES
('viral_detection.similarity_threshold', '0.85', 'Default similarity threshold for viral content detection', 'viral_detection'),
('viral_detection.min_cluster_size', '2', 'Minimum number of posts required to form a viral cluster', 'viral_detection'),
('evidence.encryption_algorithm', '"AES-256"', 'Encryption algorithm for evidence storage', 'security'),
('evidence.retention_days', '2555', 'Evidence retention period in days (7 years)', 'compliance'),
('ui.default_language', '"hi"', 'Default UI language (Hindi)', 'interface'),
('ui.supported_languages', '["hi", "en", "ta", "te", "bn", "mr", "gu"]', 'Supported UI languages', 'interface'),
('geo.default_center', '{"lat": 20.5937, "lng": 78.9629}', 'Default map center (India)', 'geographic'),
('alerts.high_priority_threshold', '7.0', 'Viral score threshold for high priority alerts', 'monitoring')
ON CONFLICT (config_key) DO NOTHING;

-- Insert sample Indian geographic data
INSERT INTO indian_geographic_data (state_name, state_code, district_name, city_name, latitude, longitude, population, police_station_code, jurisdiction_level) VALUES
('Delhi', 'DL', 'New Delhi', 'New Delhi', 28.6139, 77.2090, 32941000, 'DL001', 'state'),
('Maharashtra', 'MH', 'Mumbai', 'Mumbai', 19.0760, 72.8777, 20411000, 'MH001', 'district'),
('Karnataka', 'KA', 'Bangalore Urban', 'Bangalore', 12.9716, 77.5946, 13608000, 'KA001', 'district'),
('Tamil Nadu', 'TN', 'Chennai', 'Chennai', 13.0827, 80.2707, 11503000, 'TN001', 'district'),
('West Bengal', 'WB', 'Kolkata', 'Kolkata', 22.5726, 88.3639, 15134000, 'WB001', 'district'),
('Rajasthan', 'RJ', 'Jaipur', 'Jaipur', 26.9124, 75.7873, 3073000, 'RJ001', 'district'),
('Gujarat', 'GJ', 'Ahmedabad', 'Ahmedabad', 23.0225, 72.5714, 8450000, 'GJ001', 'district'),
('Telangana', 'TG', 'Hyderabad', 'Hyderabad', 17.3850, 78.4867, 10004000, 'TG001', 'district'),
('Uttar Pradesh', 'UP', 'Lucknow', 'Lucknow', 26.8467, 80.9462, 3382000, 'UP001', 'district'),
('Punjab', 'PB', 'Chandigarh', 'Chandigarh', 30.7333, 76.7794, 1179000, 'PB001', 'district')
ON CONFLICT DO NOTHING;

-- Insert sample police officers
INSERT INTO police_officers (officer_id, badge_number, name, rank, department, state, district, phone, email, active) VALUES
('OFF001', 'DL12345', 'Inspector Rajesh Sharma', 'Inspector', 'Delhi Police', 'Delhi', 'New Delhi', '+91-9876543210', 'r.sharma@delhipolice.gov.in', true),
('OFF002', 'MH67890', 'Sub-Inspector Priya Patel', 'Sub-Inspector', 'Mumbai Police', 'Maharashtra', 'Mumbai', '+91-9876543211', 'p.patel@mumbaipolice.gov.in', true),
('OFF003', 'KA11111', 'Assistant Commissioner Suresh Kumar', 'Assistant Commissioner', 'Bangalore Police', 'Karnataka', 'Bangalore Urban', '+91-9876543212', 's.kumar@bangalorepolice.gov.in', true),
('OFF004', 'TN22222', 'Inspector Lakshmi Devi', 'Inspector', 'Chennai Police', 'Tamil Nadu', 'Chennai', '+91-9876543213', 'l.devi@chennaipolice.gov.in', true),
('OFF005', 'WB33333', 'Sub-Inspector Amit Roy', 'Sub-Inspector', 'Kolkata Police', 'West Bengal', 'Kolkata', '+91-9876543214', 'a.roy@kolkatapolice.gov.in', true)
ON CONFLICT (officer_id) DO NOTHING;
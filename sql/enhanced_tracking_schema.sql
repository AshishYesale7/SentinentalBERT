-- Enhanced Viral Tracking Schema for SentinelBERT
-- Indian Police Hackathon - Court-Ready Evidence System

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create enhanced tracking tables
CREATE TABLE IF NOT EXISTS viral_tracking_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    input_data TEXT NOT NULL,
    input_type VARCHAR(50) NOT NULL,
    tracking_algorithm VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    confidence_score DECIMAL(5,4) DEFAULT 0.0,
    api_calls_used INTEGER DEFAULT 0,
    processing_time_seconds DECIMAL(10,3) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS viral_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES viral_tracking_sessions(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    post_id VARCHAR(255) NOT NULL,
    author_id VARCHAR(255) NOT NULL,
    author_handle VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_url TEXT,
    timestamp_posted TIMESTAMP WITH TIME ZONE NOT NULL,
    engagement_metrics JSONB DEFAULT '{}'::jsonb,
    mentions TEXT[],
    hashtags TEXT[],
    is_retweet BOOLEAN DEFAULT FALSE,
    is_original BOOLEAN DEFAULT FALSE,
    parent_post_id VARCHAR(255),
    chain_position INTEGER DEFAULT 0,
    influence_score DECIMAL(10,6) DEFAULT 0.0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, platform, post_id)
);

CREATE TABLE IF NOT EXISTS viral_chains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES viral_tracking_sessions(id) ON DELETE CASCADE,
    original_post_id UUID REFERENCES viral_posts(id),
    chain_length INTEGER NOT NULL,
    total_engagement BIGINT DEFAULT 0,
    spread_velocity DECIMAL(10,6) DEFAULT 0.0,
    time_span_hours DECIMAL(10,3) DEFAULT 0.0,
    viral_coefficient DECIMAL(5,4) DEFAULT 0.0,
    peak_activity_hour INTEGER,
    geographic_spread JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS network_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES viral_tracking_sessions(id) ON DELETE CASCADE,
    total_nodes INTEGER NOT NULL,
    total_edges INTEGER NOT NULL,
    network_density DECIMAL(5,4) DEFAULT 0.0,
    is_connected BOOLEAN DEFAULT FALSE,
    clustering_coefficient DECIMAL(5,4) DEFAULT 0.0,
    average_path_length DECIMAL(10,6) DEFAULT 0.0,
    central_nodes JSONB DEFAULT '[]'::jsonb,
    origin_candidates JSONB DEFAULT '[]'::jsonb,
    influence_distribution JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES viral_tracking_sessions(id) ON DELETE CASCADE,
    evidence_type VARCHAR(100) NOT NULL,
    evidence_hash VARCHAR(255) NOT NULL,
    file_path TEXT,
    file_size BIGINT,
    digital_signature TEXT,
    chain_of_custody JSONB DEFAULT '[]'::jsonb,
    legal_metadata JSONB DEFAULT '{}'::jsonb,
    retention_until DATE,
    is_court_ready BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS api_usage_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES viral_tracking_sessions(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    rate_limit_remaining INTEGER,
    rate_limit_reset TIMESTAMP WITH TIME ZONE,
    request_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    request_metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS user_influence_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    follower_count BIGINT DEFAULT 0,
    following_count BIGINT DEFAULT 0,
    total_posts BIGINT DEFAULT 0,
    average_engagement DECIMAL(10,6) DEFAULT 0.0,
    influence_score DECIMAL(10,6) DEFAULT 0.0,
    verification_status BOOLEAN DEFAULT FALSE,
    account_age_days INTEGER DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, user_id)
);

CREATE TABLE IF NOT EXISTS tracking_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES viral_tracking_sessions(id) ON DELETE CASCADE,
    algorithm_used VARCHAR(100) NOT NULL,
    accuracy_score DECIMAL(5,4) DEFAULT 0.0,
    precision_score DECIMAL(5,4) DEFAULT 0.0,
    recall_score DECIMAL(5,4) DEFAULT 0.0,
    f1_score DECIMAL(5,4) DEFAULT 0.0,
    processing_time_seconds DECIMAL(10,3) NOT NULL,
    memory_usage_mb INTEGER DEFAULT 0,
    api_calls_count INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0.0,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_viral_tracking_sessions_status ON viral_tracking_sessions(status);
CREATE INDEX IF NOT EXISTS idx_viral_tracking_sessions_created_at ON viral_tracking_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_viral_tracking_sessions_algorithm ON viral_tracking_sessions(tracking_algorithm);

CREATE INDEX IF NOT EXISTS idx_viral_posts_session_id ON viral_posts(session_id);
CREATE INDEX IF NOT EXISTS idx_viral_posts_platform_post_id ON viral_posts(platform, post_id);
CREATE INDEX IF NOT EXISTS idx_viral_posts_author_handle ON viral_posts(author_handle);
CREATE INDEX IF NOT EXISTS idx_viral_posts_timestamp ON viral_posts(timestamp_posted);
CREATE INDEX IF NOT EXISTS idx_viral_posts_is_original ON viral_posts(is_original);

CREATE INDEX IF NOT EXISTS idx_viral_chains_session_id ON viral_chains(session_id);
CREATE INDEX IF NOT EXISTS idx_viral_chains_original_post_id ON viral_chains(original_post_id);

CREATE INDEX IF NOT EXISTS idx_network_analysis_session_id ON network_analysis(session_id);

CREATE INDEX IF NOT EXISTS idx_evidence_records_session_id ON evidence_records(session_id);
CREATE INDEX IF NOT EXISTS idx_evidence_records_evidence_type ON evidence_records(evidence_type);
CREATE INDEX IF NOT EXISTS idx_evidence_records_is_court_ready ON evidence_records(is_court_ready);

CREATE INDEX IF NOT EXISTS idx_api_usage_platform ON api_usage_tracking(platform);
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage_tracking(request_timestamp);

CREATE INDEX IF NOT EXISTS idx_user_influence_platform_user ON user_influence_scores(platform, user_id);
CREATE INDEX IF NOT EXISTS idx_user_influence_score ON user_influence_scores(influence_score DESC);

CREATE INDEX IF NOT EXISTS idx_tracking_performance_session_id ON tracking_performance_metrics(session_id);
CREATE INDEX IF NOT EXISTS idx_tracking_performance_algorithm ON tracking_performance_metrics(algorithm_used);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_viral_tracking_sessions_metadata_gin ON viral_tracking_sessions USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_viral_posts_engagement_gin ON viral_posts USING GIN (engagement_metrics);
CREATE INDEX IF NOT EXISTS idx_viral_posts_metadata_gin ON viral_posts USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_network_analysis_central_nodes_gin ON network_analysis USING GIN (central_nodes);
CREATE INDEX IF NOT EXISTS idx_network_analysis_origin_candidates_gin ON network_analysis USING GIN (origin_candidates);

-- Create text search indexes
CREATE INDEX IF NOT EXISTS idx_viral_posts_content_trgm ON viral_posts USING GIN (content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_viral_posts_hashtags_gin ON viral_posts USING GIN (hashtags);
CREATE INDEX IF NOT EXISTS idx_viral_posts_mentions_gin ON viral_posts USING GIN (mentions);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_viral_tracking_sessions_updated_at 
    BEFORE UPDATE ON viral_tracking_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW viral_tracking_summary AS
SELECT 
    vts.id,
    vts.session_id,
    vts.input_data,
    vts.input_type,
    vts.tracking_algorithm,
    vts.status,
    vts.confidence_score,
    vts.api_calls_used,
    vts.processing_time_seconds,
    vts.created_at,
    vts.completed_at,
    vc.chain_length,
    vc.total_engagement,
    vc.spread_velocity,
    vc.viral_coefficient,
    na.total_nodes,
    na.total_edges,
    na.network_density,
    COUNT(vp.id) as total_posts,
    COUNT(CASE WHEN vp.is_original THEN 1 END) as original_posts_count
FROM viral_tracking_sessions vts
LEFT JOIN viral_chains vc ON vts.id = vc.session_id
LEFT JOIN network_analysis na ON vts.id = na.session_id
LEFT JOIN viral_posts vp ON vts.id = vp.session_id
GROUP BY vts.id, vc.id, na.id;

CREATE OR REPLACE VIEW top_influencers AS
SELECT 
    platform,
    username,
    user_id,
    influence_score,
    follower_count,
    average_engagement,
    verification_status,
    last_activity,
    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY influence_score DESC) as rank
FROM user_influence_scores
WHERE calculated_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

CREATE OR REPLACE VIEW tracking_performance_summary AS
SELECT 
    algorithm_used,
    COUNT(*) as total_sessions,
    AVG(accuracy_score) as avg_accuracy,
    AVG(processing_time_seconds) as avg_processing_time,
    AVG(api_calls_count) as avg_api_calls,
    AVG(success_rate) as avg_success_rate,
    MIN(created_at) as first_used,
    MAX(created_at) as last_used
FROM tracking_performance_metrics
GROUP BY algorithm_used;

-- Insert default configuration data
INSERT INTO user_influence_scores (platform, user_id, username, influence_score, calculated_at)
VALUES 
    ('twitter', '835527957481459713', 'YesaleAshish', 0.75, CURRENT_TIMESTAMP)
ON CONFLICT (platform, user_id) DO UPDATE SET
    influence_score = EXCLUDED.influence_score,
    calculated_at = EXCLUDED.calculated_at;

-- Create stored procedures for common operations
CREATE OR REPLACE FUNCTION create_tracking_session(
    p_input_data TEXT,
    p_input_type VARCHAR(50),
    p_algorithm VARCHAR(100)
) RETURNS UUID AS $$
DECLARE
    session_uuid UUID;
    session_id_str VARCHAR(255);
BEGIN
    session_uuid := uuid_generate_v4();
    session_id_str := 'track_' || EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT || '_' || SUBSTRING(session_uuid::TEXT, 1, 8);
    
    INSERT INTO viral_tracking_sessions (
        id, session_id, input_data, input_type, tracking_algorithm, status
    ) VALUES (
        session_uuid, session_id_str, p_input_data, p_input_type, p_algorithm, 'active'
    );
    
    RETURN session_uuid;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION complete_tracking_session(
    p_session_id UUID,
    p_confidence_score DECIMAL(5,4),
    p_api_calls INTEGER,
    p_processing_time DECIMAL(10,3)
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE viral_tracking_sessions 
    SET 
        status = 'completed',
        confidence_score = p_confidence_score,
        api_calls_used = p_api_calls,
        processing_time_seconds = p_processing_time,
        completed_at = CURRENT_TIMESTAMP
    WHERE id = p_session_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean old data (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_tracking_data(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM viral_tracking_sessions 
    WHERE created_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL
    AND status IN ('completed', 'failed');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sentinel;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sentinel;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sentinel;

-- Create sample data for testing
DO $$
DECLARE
    test_session_id UUID;
BEGIN
    -- Create a test tracking session
    test_session_id := create_tracking_session(
        '@YesaleAshish',
        'username',
        'reverse_chronological'
    );
    
    -- Add sample viral post
    INSERT INTO viral_posts (
        session_id, platform, post_id, author_id, author_handle,
        content, post_url, timestamp_posted, is_original,
        engagement_metrics, hashtags
    ) VALUES (
        test_session_id,
        'twitter',
        '1970201504155160937',
        '835527957481459713',
        'YesaleAshish',
        'Today I coded 12 hrs 52 mins towards my @WakaTime goal of coding 1 hr per day ✔️',
        'https://twitter.com/i/status/1970201504155160937',
        CURRENT_TIMESTAMP - INTERVAL '1 day',
        TRUE,
        '{"likes": 0, "retweets": 0, "replies": 0}',
        ARRAY['coding', 'wakatime']
    );
    
    -- Complete the test session
    PERFORM complete_tracking_session(test_session_id, 0.85, 3, 2.5);
    
END $$;

-- Create materialized view for dashboard performance
CREATE MATERIALIZED VIEW IF NOT EXISTS dashboard_stats AS
SELECT 
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
    AVG(confidence_score) as avg_confidence,
    AVG(processing_time_seconds) as avg_processing_time,
    SUM(api_calls_used) as total_api_calls,
    COUNT(DISTINCT DATE(created_at)) as active_days,
    MAX(created_at) as last_activity
FROM viral_tracking_sessions
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_dashboard_stats_unique ON dashboard_stats ((1));

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW dashboard_stats;

-- Create function to refresh dashboard stats
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW dashboard_stats;
END;
$$ LANGUAGE plpgsql;

-- Create notification for real-time updates
CREATE OR REPLACE FUNCTION notify_tracking_update()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('tracking_update', json_build_object(
        'session_id', NEW.session_id,
        'status', NEW.status,
        'confidence_score', NEW.confidence_score
    )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tracking_session_notify
    AFTER INSERT OR UPDATE ON viral_tracking_sessions
    FOR EACH ROW EXECUTE FUNCTION notify_tracking_update();

-- Final success message
DO $$
BEGIN
    RAISE NOTICE 'Enhanced Viral Tracking Schema created successfully!';
    RAISE NOTICE 'Tables created: %, Views created: %, Functions created: %', 
        (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'viral_%' OR table_name LIKE '%tracking%' OR table_name LIKE 'evidence_%' OR table_name LIKE 'api_usage%' OR table_name LIKE 'user_influence%'),
        (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public'),
        (SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public' AND routine_type = 'FUNCTION');
END $$;
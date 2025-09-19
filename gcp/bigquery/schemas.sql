-- BigQuery schemas for SentinentalBERT
-- This file contains all table definitions for the analytics dataset

-- Social media posts table (partitioned by date)
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.social_posts` (
  post_id STRING NOT NULL,
  platform STRING NOT NULL,
  author_id STRING,
  author_username STRING,
  author_display_name STRING,
  author_followers_count INT64,
  author_verified BOOL,
  content TEXT,
  content_type STRING, -- text, image, video, link
  language STRING,
  created_at TIMESTAMP NOT NULL,
  ingested_at TIMESTAMP NOT NULL,
  url STRING,
  engagement_metrics STRUCT<
    likes INT64,
    shares INT64,
    comments INT64,
    views INT64,
    reactions ARRAY<STRUCT<type STRING, count INT64>>
  >,
  location STRUCT<
    country STRING,
    region STRING,
    city STRING,
    coordinates STRUCT<lat FLOAT64, lng FLOAT64>
  >,
  hashtags ARRAY<STRING>,
  mentions ARRAY<STRING>,
  media_urls ARRAY<STRING>,
  parent_post_id STRING, -- for replies/retweets
  is_retweet BOOL,
  is_reply BOOL,
  raw_data JSON,
  processing_status STRING DEFAULT 'pending'
)
PARTITION BY DATE(created_at)
CLUSTER BY platform, author_id, language
OPTIONS(
  description="Social media posts from all platforms",
  partition_expiration_days=1095, -- 3 years
  require_partition_filter=true
);

-- Sentiment analysis results table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.sentiment_analysis` (
  analysis_id STRING NOT NULL,
  post_id STRING NOT NULL,
  model_version STRING NOT NULL,
  sentiment_score FLOAT64, -- -1 to 1
  sentiment_label STRING, -- negative, neutral, positive
  confidence_score FLOAT64, -- 0 to 1
  emotion_scores STRUCT<
    anger FLOAT64,
    fear FLOAT64,
    joy FLOAT64,
    sadness FLOAT64,
    surprise FLOAT64,
    disgust FLOAT64,
    trust FLOAT64,
    anticipation FLOAT64
  >,
  topics ARRAY<STRUCT<
    topic STRING,
    relevance_score FLOAT64
  >>,
  keywords ARRAY<STRUCT<
    keyword STRING,
    importance_score FLOAT64
  >>,
  analyzed_at TIMESTAMP NOT NULL,
  processing_time_ms INT64
)
PARTITION BY DATE(analyzed_at)
CLUSTER BY sentiment_label, post_id
OPTIONS(
  description="Sentiment analysis results for social media posts"
);

-- Behavioral patterns table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.behavioral_patterns` (
  pattern_id STRING NOT NULL,
  author_id STRING NOT NULL,
  platform STRING NOT NULL,
  pattern_type STRING, -- posting_frequency, sentiment_trend, topic_focus, etc.
  pattern_data JSON,
  confidence_score FLOAT64,
  time_window STRUCT<
    start_date DATE,
    end_date DATE
  >,
  detected_at TIMESTAMP NOT NULL,
  is_anomaly BOOL,
  risk_score FLOAT64 -- 0 to 1
)
PARTITION BY DATE(detected_at)
CLUSTER BY author_id, pattern_type, platform
OPTIONS(
  description="Detected behavioral patterns for users"
);

-- Influence scoring table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.influence_scores` (
  author_id STRING NOT NULL,
  platform STRING NOT NULL,
  influence_score FLOAT64, -- 0 to 100
  reach_score FLOAT64,
  engagement_rate FLOAT64,
  content_quality_score FLOAT64,
  network_centrality FLOAT64,
  follower_quality_score FLOAT64,
  posting_consistency FLOAT64,
  topic_authority ARRAY<STRUCT<
    topic STRING,
    authority_score FLOAT64
  >>,
  calculated_at TIMESTAMP NOT NULL,
  calculation_period STRUCT<
    start_date DATE,
    end_date DATE
  >
)
PARTITION BY DATE(calculated_at)
CLUSTER BY platform, author_id
OPTIONS(
  description="Influence scores for social media users"
);

-- Content origin tracking table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.content_origins` (
  content_hash STRING NOT NULL,
  original_post_id STRING NOT NULL,
  original_author_id STRING NOT NULL,
  original_platform STRING NOT NULL,
  original_timestamp TIMESTAMP NOT NULL,
  content_text TEXT,
  content_type STRING,
  spread_metrics STRUCT<
    total_shares INT64,
    total_platforms INT64,
    reach_estimate INT64,
    viral_coefficient FLOAT64
  >,
  variations ARRAY<STRUCT<
    post_id STRING,
    platform STRING,
    author_id STRING,
    timestamp TIMESTAMP,
    similarity_score FLOAT64,
    modification_type STRING
  >>,
  tracked_since TIMESTAMP NOT NULL,
  last_updated TIMESTAMP NOT NULL
)
PARTITION BY DATE(original_timestamp)
CLUSTER BY content_hash, original_platform
OPTIONS(
  description="Content origin tracking and spread analysis"
);

-- Geographic analysis table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.geographic_analysis` (
  analysis_id STRING NOT NULL,
  region_code STRING NOT NULL, -- ISO country/region code
  region_name STRING NOT NULL,
  coordinates STRUCT<
    center_lat FLOAT64,
    center_lng FLOAT64,
    bounds STRUCT<
      north FLOAT64,
      south FLOAT64,
      east FLOAT64,
      west FLOAT64
    >
  >,
  time_period STRUCT<
    start_date DATE,
    end_date DATE
  >,
  metrics STRUCT<
    total_posts INT64,
    unique_authors INT64,
    avg_sentiment FLOAT64,
    dominant_topics ARRAY<STRING>,
    trending_hashtags ARRAY<STRING>,
    engagement_rate FLOAT64
  >,
  calculated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(calculated_at)
CLUSTER BY region_code, time_period.start_date
OPTIONS(
  description="Geographic analysis of social media activity"
);

-- Search queries and alerts table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.search_queries` (
  query_id STRING NOT NULL,
  user_id STRING NOT NULL,
  query_text STRING NOT NULL,
  query_parameters JSON,
  platforms ARRAY<STRING>,
  date_range STRUCT<
    start_date DATE,
    end_date DATE
  >,
  filters JSON,
  created_at TIMESTAMP NOT NULL,
  last_executed TIMESTAMP,
  is_active BOOL DEFAULT true,
  alert_threshold STRUCT<
    volume_threshold INT64,
    sentiment_threshold FLOAT64,
    engagement_threshold FLOAT64
  >,
  results_count INT64,
  execution_count INT64
)
PARTITION BY DATE(created_at)
CLUSTER BY user_id, is_active
OPTIONS(
  description="User search queries and alert configurations"
);

-- Data quality metrics table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.data_quality_metrics` (
  metric_id STRING NOT NULL,
  table_name STRING NOT NULL,
  metric_type STRING NOT NULL, -- completeness, accuracy, consistency, timeliness
  metric_value FLOAT64,
  threshold_value FLOAT64,
  status STRING, -- pass, warning, fail
  details JSON,
  measured_at TIMESTAMP NOT NULL,
  measurement_period STRUCT<
    start_timestamp TIMESTAMP,
    end_timestamp TIMESTAMP
  >
)
PARTITION BY DATE(measured_at)
CLUSTER BY table_name, metric_type, status
OPTIONS(
  description="Data quality monitoring metrics"
);

-- Processing jobs tracking table
CREATE TABLE IF NOT EXISTS `${project_id}.sentinelbert_${environment}.processing_jobs` (
  job_id STRING NOT NULL,
  job_type STRING NOT NULL, -- ingestion, sentiment_analysis, pattern_detection, etc.
  status STRING NOT NULL, -- pending, running, completed, failed
  platform STRING,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  duration_seconds INT64,
  records_processed INT64,
  records_failed INT64,
  error_message STRING,
  job_config JSON,
  resource_usage STRUCT<
    cpu_seconds FLOAT64,
    memory_gb_seconds FLOAT64,
    storage_gb FLOAT64
  >,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY job_type, status, platform
OPTIONS(
  description="Processing jobs tracking and monitoring"
);

-- Create views for common queries

-- Recent posts with sentiment
CREATE OR REPLACE VIEW `${project_id}.sentinelbert_${environment}.posts_with_sentiment` AS
SELECT 
  p.post_id,
  p.platform,
  p.author_username,
  p.content,
  p.created_at,
  p.engagement_metrics,
  s.sentiment_score,
  s.sentiment_label,
  s.confidence_score,
  s.emotion_scores
FROM `${project_id}.sentinelbert_${environment}.social_posts` p
LEFT JOIN `${project_id}.sentinelbert_${environment}.sentiment_analysis` s
  ON p.post_id = s.post_id
WHERE p.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY);

-- Top influencers by platform
CREATE OR REPLACE VIEW `${project_id}.sentinelbert_${environment}.top_influencers` AS
SELECT 
  author_id,
  platform,
  influence_score,
  reach_score,
  engagement_rate,
  ROW_NUMBER() OVER (PARTITION BY platform ORDER BY influence_score DESC) as rank
FROM `${project_id}.sentinelbert_${environment}.influence_scores`
WHERE calculated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
QUALIFY rank <= 100;

-- Trending topics by region
CREATE OR REPLACE VIEW `${project_id}.sentinelbert_${environment}.trending_topics_by_region` AS
SELECT 
  g.region_name,
  topic.topic,
  COUNT(*) as mention_count,
  AVG(s.sentiment_score) as avg_sentiment
FROM `${project_id}.sentinelbert_${environment}.geographic_analysis` g,
UNNEST(g.metrics.dominant_topics) as topic
LEFT JOIN `${project_id}.sentinelbert_${environment}.social_posts` p
  ON p.location.country = g.region_code
LEFT JOIN `${project_id}.sentinelbert_${environment}.sentiment_analysis` s
  ON p.post_id = s.post_id
WHERE g.calculated_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY g.region_name, topic.topic
ORDER BY mention_count DESC;

-- Content spread analysis
CREATE OR REPLACE VIEW `${project_id}.sentinelbert_${environment}.viral_content` AS
SELECT 
  co.content_hash,
  co.original_post_id,
  co.original_author_id,
  co.original_platform,
  co.original_timestamp,
  co.spread_metrics.total_shares,
  co.spread_metrics.total_platforms,
  co.spread_metrics.viral_coefficient,
  ARRAY_LENGTH(co.variations) as variation_count
FROM `${project_id}.sentinelbert_${environment}.content_origins` co
WHERE co.spread_metrics.viral_coefficient > 1.0
ORDER BY co.spread_metrics.viral_coefficient DESC;
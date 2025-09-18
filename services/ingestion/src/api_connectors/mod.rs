/*
 * =============================================================================
 * SentinelBERT API Connectors Module
 * =============================================================================
 * 
 * This module provides connectors for various social media platforms using
 * their free tier APIs. Each connector implements the common ApiConnector trait
 * to ensure consistent behavior across different platforms.
 * 
 * Supported Platforms:
 * - Twitter/X.com (Essential Access - Free)
 * - Reddit (Free API)
 * - YouTube (Data API v3 - Free tier)
 * - Instagram (Basic Display API - Free)
 * - Telegram (Bot API - Free)
 * 
 * Features:
 * - Rate limiting compliance for each platform
 * - Error handling and retry logic
 * - Data normalization across platforms
 * - Privacy-compliant data collection
 * - Configurable search parameters
 * 
 * Usage:
 * ```rust
 * use crate::api_connectors::{TwitterConnector, RedditConnector};
 * 
 * let twitter = TwitterConnector::new(bearer_token);
 * let posts = twitter.search("climate change", &search_params).await?;
 * ```
 * 
 * =============================================================================
 */

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use anyhow::{Result, Error};

// Re-export all connector modules
pub mod twitter;
pub mod reddit;
pub mod youtube;
pub mod instagram;
pub mod telegram;

// Re-export connector structs for easy access
pub use twitter::TwitterConnector;
pub use reddit::RedditConnector;
pub use youtube::YouTubeConnector;
pub use instagram::InstagramConnector;
pub use telegram::TelegramConnector;

/// Common search parameters used across all platforms
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchParams {
    /// Search query string
    pub query: String,
    
    /// Maximum number of results to return
    pub max_results: Option<u32>,
    
    /// Start date for search (ISO 8601 format)
    pub start_date: Option<DateTime<Utc>>,
    
    /// End date for search (ISO 8601 format)
    pub end_date: Option<DateTime<Utc>>,
    
    /// Language filter (ISO 639-1 codes)
    pub language: Option<String>,
    
    /// Geographic location filter
    pub location: Option<GeoLocation>,
    
    /// Content type filter
    pub content_type: Option<ContentType>,
    
    /// Additional platform-specific parameters
    pub extra_params: HashMap<String, String>,
}

/// Geographic location for filtering content
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeoLocation {
    /// Latitude coordinate
    pub latitude: f64,
    
    /// Longitude coordinate
    pub longitude: f64,
    
    /// Radius in kilometers
    pub radius_km: f64,
    
    /// Location name (optional)
    pub name: Option<String>,
}

/// Content type enumeration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ContentType {
    /// Text-only posts
    Text,
    
    /// Posts with images
    Image,
    
    /// Posts with videos
    Video,
    
    /// Posts with links
    Link,
    
    /// All content types
    All,
}

/// Normalized social media post structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SocialPost {
    /// Unique identifier for the post
    pub id: String,
    
    /// Platform where the post originated
    pub platform: String,
    
    /// Post content/text
    pub content: String,
    
    /// Author information (anonymized for privacy)
    pub author: AuthorInfo,
    
    /// Post creation timestamp
    pub created_at: DateTime<Utc>,
    
    /// Post metrics (likes, shares, etc.)
    pub metrics: PostMetrics,
    
    /// Geographic information (if available)
    pub location: Option<GeoLocation>,
    
    /// Language of the post
    pub language: Option<String>,
    
    /// Media attachments
    pub media: Vec<MediaAttachment>,
    
    /// Hashtags used in the post
    pub hashtags: Vec<String>,
    
    /// Mentioned users (anonymized)
    pub mentions: Vec<String>,
    
    /// URLs mentioned in the post
    pub urls: Vec<String>,
    
    /// Platform-specific metadata
    pub metadata: HashMap<String, serde_json::Value>,
    
    /// Privacy compliance flags
    pub privacy_flags: PrivacyFlags,
}

/// Author information (privacy-compliant)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthorInfo {
    /// Anonymized author ID (hashed)
    pub id_hash: String,
    
    /// Display username (may be anonymized)
    pub username: String,
    
    /// Account verification status
    pub verified: bool,
    
    /// Follower count (if public)
    pub follower_count: Option<u64>,
    
    /// Account creation date (if available)
    pub account_created: Option<DateTime<Utc>>,
    
    /// Account type (personal, business, etc.)
    pub account_type: Option<String>,
}

/// Post engagement metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PostMetrics {
    /// Number of likes/reactions
    pub likes: u64,
    
    /// Number of shares/retweets
    pub shares: u64,
    
    /// Number of comments/replies
    pub comments: u64,
    
    /// Number of views (if available)
    pub views: Option<u64>,
    
    /// Engagement rate (calculated)
    pub engagement_rate: Option<f64>,
}

/// Media attachment information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaAttachment {
    /// Media type (image, video, audio)
    pub media_type: String,
    
    /// Media URL (may be proxied for privacy)
    pub url: String,
    
    /// Alternative text description
    pub alt_text: Option<String>,
    
    /// Media dimensions
    pub dimensions: Option<MediaDimensions>,
    
    /// File size in bytes
    pub file_size: Option<u64>,
}

/// Media dimensions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaDimensions {
    pub width: u32,
    pub height: u32,
}

/// Privacy compliance flags
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrivacyFlags {
    /// Whether personal identifiers have been anonymized
    pub anonymized: bool,
    
    /// Whether the post contains potentially sensitive content
    pub sensitive_content: bool,
    
    /// Whether location data has been generalized
    pub location_generalized: bool,
    
    /// Data retention policy applied
    pub retention_policy: String,
    
    /// Consent status for data processing
    pub consent_status: ConsentStatus,
}

/// Consent status for data processing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConsentStatus {
    /// Explicit consent given
    Explicit,
    
    /// Implied consent (public post)
    Implied,
    
    /// Legitimate interest basis
    LegitimateInterest,
    
    /// Unknown consent status
    Unknown,
}

/// Rate limiting information
#[derive(Debug, Clone)]
pub struct RateLimitInfo {
    /// Requests remaining in current window
    pub remaining: u32,
    
    /// Total requests allowed per window
    pub limit: u32,
    
    /// Time when rate limit window resets
    pub reset_time: DateTime<Utc>,
    
    /// Current rate limit window duration
    pub window_duration: chrono::Duration,
}

/// API connector error types
#[derive(Debug, thiserror::Error)]
pub enum ConnectorError {
    /// Rate limit exceeded
    #[error("Rate limit exceeded. Reset at: {reset_time}")]
    RateLimitExceeded { reset_time: DateTime<Utc> },
    
    /// Authentication failed
    #[error("Authentication failed: {message}")]
    AuthenticationFailed { message: String },
    
    /// Invalid API key or token
    #[error("Invalid API credentials")]
    InvalidCredentials,
    
    /// Network request failed
    #[error("Network request failed: {source}")]
    NetworkError { source: reqwest::Error },
    
    /// API returned an error
    #[error("API error: {code} - {message}")]
    ApiError { code: u16, message: String },
    
    /// Data parsing failed
    #[error("Failed to parse response data: {source}")]
    ParseError { source: serde_json::Error },
    
    /// Configuration error
    #[error("Configuration error: {message}")]
    ConfigError { message: String },
    
    /// Generic error
    #[error("Connector error: {message}")]
    Generic { message: String },
}

/// Common trait for all API connectors
#[async_trait]
pub trait ApiConnector: Send + Sync {
    /// Get the platform name
    fn platform_name(&self) -> &'static str;
    
    /// Check if the connector is properly configured
    fn is_configured(&self) -> bool;
    
    /// Get current rate limit status
    async fn get_rate_limit_status(&self) -> Result<RateLimitInfo, ConnectorError>;
    
    /// Search for posts matching the given parameters
    async fn search_posts(&self, params: &SearchParams) -> Result<Vec<SocialPost>, ConnectorError>;
    
    /// Get a specific post by ID
    async fn get_post_by_id(&self, post_id: &str) -> Result<Option<SocialPost>, ConnectorError>;
    
    /// Get posts from a specific user (if supported)
    async fn get_user_posts(&self, user_id: &str, limit: Option<u32>) -> Result<Vec<SocialPost>, ConnectorError>;
    
    /// Get trending topics (if supported by platform)
    async fn get_trending_topics(&self, location: Option<&str>) -> Result<Vec<String>, ConnectorError>;
    
    /// Validate API credentials
    async fn validate_credentials(&self) -> Result<bool, ConnectorError>;
    
    /// Get platform-specific configuration requirements
    fn get_config_requirements(&self) -> Vec<ConfigRequirement>;
}

/// Configuration requirement for API connectors
#[derive(Debug, Clone)]
pub struct ConfigRequirement {
    /// Configuration key name
    pub key: String,
    
    /// Human-readable description
    pub description: String,
    
    /// Whether this configuration is required
    pub required: bool,
    
    /// Example value
    pub example: Option<String>,
    
    /// Where to obtain this configuration
    pub source_url: Option<String>,
}

/// Privacy configuration for data processing
#[derive(Debug, Clone)]
pub struct PrivacyConfig {
    /// Salt for hashing user IDs
    pub salt: String,
    
    /// Location precision in kilometers
    pub location_precision_km: f64,
    
    /// Data retention policy
    pub retention_policy: String,
    
    /// Whether to remove sensitive content
    pub filter_sensitive_content: bool,
}

impl Default for PrivacyConfig {
    fn default() -> Self {
        Self {
            salt: "default_salt_change_in_production".to_string(),
            location_precision_km: 10.0, // 10km precision
            retention_policy: "2_years".to_string(),
            filter_sensitive_content: true,
        }
    }
}
/*
 * SentinelBERT Data Models
 * 
 * This module defines the core data structures used throughout the ingestion service.
 * All models are designed to be serializable for storage and network transmission.
 * 
 * Key Design Principles:
 * - Platform-agnostic data representation
 * - Rich metadata for analysis
 * - Privacy-conscious field handling
 * - Extensible structure for future platforms
 * 
 * Author: SentinelBERT Team
 * License: MIT
 */

// External imports for date/time handling, serialization, and data structures
use chrono::{DateTime, Utc};                    // UTC timestamp handling
use serde::{Deserialize, Serialize};            // JSON serialization/deserialization
use std::collections::HashMap;                  // Key-value mappings for flexible data
use uuid::Uuid;                                 // Unique identifier generation

/**
 * SocialPost - Core data structure representing a social media post
 * 
 * This structure normalizes posts from different platforms into a unified format.
 * It includes all necessary metadata for sentiment analysis and behavioral pattern detection.
 * 
 * Privacy Note: All PII fields are handled according to data protection regulations.
 * Author IDs are hashed before storage to protect user privacy.
 */
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SocialPost {
    /// Unique identifier for this post (UUID format)
    pub id: String,
    
    /// Source platform (Twitter, Instagram, Reddit, etc.)
    pub platform: Platform,
    
    /// Main text content of the post (sanitized for PII)
    pub content: String,
    
    /// Hashed author identifier (not the original user ID for privacy)
    pub author_id: String,
    
    /// Public username/handle (as displayed on platform)
    pub author_username: String,
    
    /// Display name if different from username (optional)
    pub author_display_name: Option<String>,
    
    /// UTC timestamp when the post was created
    pub created_at: DateTime<Utc>,
    
    /// Engagement metrics (likes, shares, comments, etc.)
    pub engagement_metrics: EngagementMetrics,
    
    /// Additional metadata about the post
    pub metadata: PostMetadata,
    
    /// Geographic information if available and permitted
    pub geographic_data: Option<GeographicData>,
    
    /// URLs to attached media (images, videos, etc.)
    pub media_urls: Vec<String>,
    
    /// Extracted hashtags from the content
    pub hashtags: Vec<String>,
    
    /// Extracted user mentions from the content
    pub mentions: Vec<String>,
    
    /// Detected language code (ISO 639-1 format)
    pub language: Option<String>,
    
    /// Raw platform-specific data for debugging/analysis
    pub raw_data: serde_json::Value,
}

/**
 * Platform - Enumeration of supported social media platforms
 * 
 * This enum defines all social media platforms that the ingestion service can handle.
 * Each platform has its own API connector and data normalization logic.
 * 
 * Adding new platforms requires:
 * 1. Adding the variant here
 * 2. Implementing the Display trait case
 * 3. Creating a platform-specific connector
 * 4. Adding API configuration
 */
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Platform {
    /// Twitter/X.com - Microblogging platform
    Twitter,
    
    /// Instagram - Photo/video sharing platform
    Instagram,
    
    /// Reddit - Discussion forum platform
    Reddit,
    
    /// Facebook - Social networking platform (public pages only)
    Facebook,
    
    /// Telegram - Messaging platform (public channels only)
    Telegram,
    
    /// TikTok - Short-form video platform
    TikTok,
    
    /// YouTube - Video sharing platform (comments and community posts)
    YouTube,
}

/**
 * Display implementation for Platform enum
 * 
 * Converts platform enum variants to lowercase string representations
 * used in configuration files, database storage, and API endpoints.
 */
impl std::fmt::Display for Platform {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Platform::Twitter => write!(f, "twitter"),
            Platform::Instagram => write!(f, "instagram"),
            Platform::Reddit => write!(f, "reddit"),
            Platform::Facebook => write!(f, "facebook"),
            Platform::Telegram => write!(f, "telegram"),
            Platform::TikTok => write!(f, "tiktok"),
            Platform::YouTube => write!(f, "youtube"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EngagementMetrics {
    pub likes: u64,
    pub shares: u64,
    pub comments: u64,
    pub views: Option<u64>,
    pub reactions: HashMap<String, u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PostMetadata {
    pub post_type: PostType,
    pub is_verified_author: bool,
    pub is_promoted: bool,
    pub reply_to: Option<String>,
    pub thread_id: Option<String>,
    pub edit_history: Vec<DateTime<Utc>>,
    pub content_warnings: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PostType {
    Original,
    Reply,
    Repost,
    Quote,
    Story,
    Live,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GeographicData {
    pub latitude: Option<f64>,
    pub longitude: Option<f64>,
    pub country: Option<String>,
    pub region: Option<String>,
    pub city: Option<String>,
    pub timezone: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserProfile {
    pub id: String,
    pub platform: Platform,
    pub username: String,
    pub display_name: Option<String>,
    pub bio: Option<String>,
    pub follower_count: u64,
    pub following_count: u64,
    pub post_count: u64,
    pub verified: bool,
    pub account_created: Option<DateTime<Utc>>,
    pub profile_image_url: Option<String>,
    pub location: Option<String>,
    pub website: Option<String>,
    pub last_updated: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IngestionJob {
    pub id: Uuid,
    pub platform: Platform,
    pub job_type: JobType,
    pub parameters: JobParameters,
    pub status: JobStatus,
    pub created_at: DateTime<Utc>,
    pub started_at: Option<DateTime<Utc>>,
    pub completed_at: Option<DateTime<Utc>>,
    pub error_message: Option<String>,
    pub retry_count: u32,
    pub max_retries: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum JobType {
    KeywordSearch,
    HashtagSearch,
    UserTimeline,
    TrendingTopics,
    LocationBased,
    FollowNetwork,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobParameters {
    pub keywords: Vec<String>,
    pub hashtags: Vec<String>,
    pub users: Vec<String>,
    pub locations: Vec<String>,
    pub date_range: Option<DateRange>,
    pub limit: Option<u32>,
    pub include_retweets: bool,
    pub include_replies: bool,
    pub language_filter: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DateRange {
    pub start: DateTime<Utc>,
    pub end: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum JobStatus {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
    Retrying,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RateLimitInfo {
    pub platform: Platform,
    pub endpoint: String,
    pub requests_remaining: u32,
    pub reset_time: DateTime<Utc>,
    pub window_size: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IngestionMetrics {
    pub platform: Platform,
    pub posts_collected: u64,
    pub users_discovered: u64,
    pub api_calls_made: u64,
    pub errors_encountered: u64,
    pub rate_limit_hits: u64,
    pub processing_time_ms: u64,
    pub timestamp: DateTime<Utc>,
}

impl SocialPost {
    pub fn new(
        platform: Platform,
        content: String,
        author_id: String,
        author_username: String,
    ) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            platform,
            content,
            author_id,
            author_username,
            author_display_name: None,
            created_at: Utc::now(),
            engagement_metrics: EngagementMetrics {
                likes: 0,
                shares: 0,
                comments: 0,
                views: None,
                reactions: HashMap::new(),
            },
            metadata: PostMetadata {
                post_type: PostType::Original,
                is_verified_author: false,
                is_promoted: false,
                reply_to: None,
                thread_id: None,
                edit_history: vec![],
                content_warnings: vec![],
            },
            geographic_data: None,
            media_urls: vec![],
            hashtags: vec![],
            mentions: vec![],
            language: None,
            raw_data: serde_json::Value::Null,
        }
    }

    pub fn extract_hashtags(&mut self) {
        let hashtag_regex = regex::Regex::new(r"#\w+").unwrap();
        self.hashtags = hashtag_regex
            .find_iter(&self.content)
            .map(|m| m.as_str().to_string())
            .collect();
    }

    pub fn extract_mentions(&mut self) {
        let mention_regex = regex::Regex::new(r"@\w+").unwrap();
        self.mentions = mention_regex
            .find_iter(&self.content)
            .map(|m| m.as_str().to_string())
            .collect();
    }

    pub fn calculate_engagement_score(&self) -> f64 {
        let likes_weight = 1.0;
        let shares_weight = 3.0;
        let comments_weight = 2.0;
        let views_weight = 0.1;

        let likes_score = self.engagement_metrics.likes as f64 * likes_weight;
        let shares_score = self.engagement_metrics.shares as f64 * shares_weight;
        let comments_score = self.engagement_metrics.comments as f64 * comments_weight;
        let views_score = self.engagement_metrics.views.unwrap_or(0) as f64 * views_weight;

        likes_score + shares_score + comments_score + views_score
    }
}

impl UserProfile {
    pub fn calculate_influence_score(&self) -> f64 {
        let follower_ratio = if self.following_count > 0 {
            self.follower_count as f64 / self.following_count as f64
        } else {
            self.follower_count as f64
        };

        let post_engagement = if self.post_count > 0 {
            self.follower_count as f64 / self.post_count as f64
        } else {
            0.0
        };

        let verification_bonus = if self.verified { 1.5 } else { 1.0 };
        let account_age_bonus = self.account_created
            .map(|created| {
                let age_days = (Utc::now() - created).num_days() as f64;
                (age_days / 365.0).min(5.0) // Cap at 5 years
            })
            .unwrap_or(0.0);

        (follower_ratio.ln() + post_engagement.ln() + account_age_bonus) * verification_bonus
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_social_post_creation() {
        let post = SocialPost::new(
            Platform::Twitter,
            "Test post #hashtag @mention".to_string(),
            "user123".to_string(),
            "testuser".to_string(),
        );

        assert_eq!(post.platform, Platform::Twitter);
        assert_eq!(post.content, "Test post #hashtag @mention");
        assert_eq!(post.author_id, "user123");
        assert_eq!(post.author_username, "testuser");
    }

    #[test]
    fn test_hashtag_extraction() {
        let mut post = SocialPost::new(
            Platform::Twitter,
            "This is a #test post with #multiple #hashtags".to_string(),
            "user123".to_string(),
            "testuser".to_string(),
        );

        post.extract_hashtags();
        assert_eq!(post.hashtags.len(), 3);
        assert!(post.hashtags.contains(&"#test".to_string()));
        assert!(post.hashtags.contains(&"#multiple".to_string()));
        assert!(post.hashtags.contains(&"#hashtags".to_string()));
    }

    #[test]
    fn test_engagement_score_calculation() {
        let mut post = SocialPost::new(
            Platform::Twitter,
            "Test post".to_string(),
            "user123".to_string(),
            "testuser".to_string(),
        );

        post.engagement_metrics.likes = 100;
        post.engagement_metrics.shares = 50;
        post.engagement_metrics.comments = 25;
        post.engagement_metrics.views = Some(1000);

        let score = post.calculate_engagement_score();
        assert!(score > 0.0);
    }

    #[test]
    fn test_influence_score_calculation() {
        let profile = UserProfile {
            id: "user123".to_string(),
            platform: Platform::Twitter,
            username: "testuser".to_string(),
            display_name: Some("Test User".to_string()),
            bio: None,
            follower_count: 10000,
            following_count: 1000,
            post_count: 500,
            verified: true,
            account_created: Some(Utc::now() - chrono::Duration::days(365)),
            profile_image_url: None,
            location: None,
            website: None,
            last_updated: Utc::now(),
        };

        let influence_score = profile.calculate_influence_score();
        assert!(influence_score > 0.0);
    }
}
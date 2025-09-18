/*
 * =============================================================================
 * Reddit API Connector for SentinelBERT
 * =============================================================================
 * 
 * This module implements the Reddit API connector using the free tier access.
 * It provides comprehensive Reddit post and comment search capabilities while
 * respecting rate limits and privacy requirements.
 * 
 * Reddit API Free Tier Features:
 * - 100 requests per minute
 * - 1000 requests per hour
 * - Access to public subreddits and posts
 * - Search functionality across Reddit
 * - User post history (public posts only)
 * 
 * Rate Limits (Free Tier):
 * - 100 requests per minute
 * - 1000 requests per hour
 * - OAuth2 authentication required
 * 
 * Setup Instructions:
 * 1. Visit https://www.reddit.com/prefs/apps
 * 2. Create a new application (script type)
 * 3. Note the client ID and client secret
 * 4. Add to environment:
 *    REDDIT_CLIENT_ID=your_client_id
 *    REDDIT_CLIENT_SECRET=your_client_secret
 *    REDDIT_USER_AGENT=SentinelBERT/1.0 (by /u/yourusername)
 * 
 * Privacy Compliance:
 * - User IDs and usernames are hashed for anonymization
 * - Location data is generalized when available
 * - Sensitive content detection and filtering
 * - GDPR-compliant data processing
 * 
 * =============================================================================
 */

use super::*;
use async_trait::async_trait;
use reqwest::{Client, header::{HeaderMap, HeaderValue, AUTHORIZATION, USER_AGENT}};
use serde::{Deserialize, Serialize};
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tokio::time::sleep;
use chrono::{DateTime, Utc, TimeZone};
use tracing::{info, warn, error, debug};
use base64::{Engine as _, engine::general_purpose};

/// Reddit API connector implementation
/// 
/// This connector uses Reddit's API with OAuth2 authentication to search
/// and collect posts and comments for sentiment analysis.
pub struct RedditConnector {
    /// HTTP client for API requests
    client: Client,
    
    /// Reddit client ID
    client_id: String,
    
    /// Reddit client secret
    client_secret: String,
    
    /// OAuth2 access token
    access_token: tokio::sync::RwLock<Option<String>>,
    
    /// Token expiration time
    token_expires_at: tokio::sync::RwLock<Option<DateTime<Utc>>>,
    
    /// Privacy configuration
    privacy_config: PrivacyConfig,
    
    /// Rate limiting state
    rate_limit_state: tokio::sync::RwLock<RateLimitState>,
    
    /// Base API URL
    base_url: String,
    
    /// OAuth URL
    oauth_url: String,
    
    /// User agent string
    user_agent: String,
}

/// Internal rate limiting state for Reddit
#[derive(Debug, Clone)]
struct RateLimitState {
    /// Requests made in current minute
    requests_this_minute: u32,
    
    /// Requests made in current hour
    requests_this_hour: u32,
    
    /// Current minute window start
    minute_window_start: DateTime<Utc>,
    
    /// Current hour window start
    hour_window_start: DateTime<Utc>,
    
    /// Last request timestamp
    last_request: Option<DateTime<Utc>>,
}

impl Default for RateLimitState {
    fn default() -> Self {
        let now = Utc::now();
        Self {
            requests_this_minute: 0,
            requests_this_hour: 0,
            minute_window_start: now,
            hour_window_start: now,
            last_request: None,
        }
    }
}

/// Reddit OAuth2 token response
#[derive(Debug, Deserialize)]
struct RedditTokenResponse {
    access_token: String,
    token_type: String,
    expires_in: u64,
    scope: String,
}

/// Reddit API listing response
#[derive(Debug, Deserialize)]
struct RedditListing {
    kind: String,
    data: RedditListingData,
}

/// Reddit listing data
#[derive(Debug, Deserialize)]
struct RedditListingData {
    after: Option<String>,
    before: Option<String>,
    children: Vec<RedditThing>,
    dist: Option<u32>,
    modhash: Option<String>,
}

/// Reddit thing (post or comment)
#[derive(Debug, Deserialize)]
struct RedditThing {
    kind: String,
    data: serde_json::Value,
}

/// Reddit post data
#[derive(Debug, Deserialize)]
struct RedditPost {
    id: String,
    title: Option<String>,
    selftext: Option<String>,
    author: Option<String>,
    author_fullname: Option<String>,
    subreddit: String,
    subreddit_id: String,
    created_utc: f64,
    score: i64,
    upvote_ratio: Option<f64>,
    num_comments: u64,
    permalink: String,
    url: Option<String>,
    domain: Option<String>,
    is_video: Option<bool>,
    media: Option<serde_json::Value>,
    preview: Option<serde_json::Value>,
    thumbnail: Option<String>,
    gilded: Option<u32>,
    stickied: Option<bool>,
    locked: Option<bool>,
    archived: Option<bool>,
    over_18: Option<bool>,
    spoiler: Option<bool>,
    link_flair_text: Option<String>,
    author_flair_text: Option<String>,
    distinguished: Option<String>,
    edited: Option<serde_json::Value>,
    all_awardings: Option<Vec<serde_json::Value>>,
}

/// Reddit comment data
#[derive(Debug, Deserialize)]
struct RedditComment {
    id: String,
    body: Option<String>,
    author: Option<String>,
    author_fullname: Option<String>,
    subreddit: String,
    created_utc: f64,
    score: i64,
    ups: Option<i64>,
    downs: Option<i64>,
    permalink: String,
    parent_id: String,
    link_id: String,
    depth: Option<u32>,
    gilded: Option<u32>,
    stickied: Option<bool>,
    distinguished: Option<String>,
    edited: Option<serde_json::Value>,
    controversiality: Option<u32>,
    all_awardings: Option<Vec<serde_json::Value>>,
}

/// Reddit search response
#[derive(Debug, Deserialize)]
struct RedditSearchResponse {
    kind: String,
    data: RedditSearchData,
}

/// Reddit search data
#[derive(Debug, Deserialize)]
struct RedditSearchData {
    after: Option<String>,
    before: Option<String>,
    children: Vec<RedditThing>,
    dist: Option<u32>,
}

impl RedditConnector {
    /// Create a new Reddit connector
    /// 
    /// # Arguments
    /// * `client_id` - Reddit application client ID
    /// * `client_secret` - Reddit application client secret
    /// * `privacy_config` - Privacy configuration for data processing
    /// 
    /// # Example
    /// ```rust
    /// let connector = RedditConnector::new(
    ///     "your_client_id".to_string(),
    ///     "your_client_secret".to_string(),
    ///     PrivacyConfig::default()
    /// );
    /// ```
    pub fn new(client_id: String, client_secret: String, privacy_config: PrivacyConfig) -> Self {
        let user_agent = std::env::var("REDDIT_USER_AGENT")
            .unwrap_or_else(|_| "SentinelBERT/1.0 (Law Enforcement Analytics)".to_string());

        let mut headers = HeaderMap::new();
        headers.insert(
            USER_AGENT,
            HeaderValue::from_str(&user_agent).expect("Invalid user agent")
        );

        let client = Client::builder()
            .default_headers(headers)
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            client,
            client_id,
            client_secret,
            access_token: tokio::sync::RwLock::new(None),
            token_expires_at: tokio::sync::RwLock::new(None),
            privacy_config,
            rate_limit_state: tokio::sync::RwLock::new(RateLimitState::default()),
            base_url: "https://oauth.reddit.com".to_string(),
            oauth_url: "https://www.reddit.com/api/v1/access_token".to_string(),
            user_agent,
        }
    }

    /// Get or refresh OAuth2 access token
    async fn get_access_token(&self) -> Result<String, ConnectorError> {
        // Check if we have a valid token
        {
            let token = self.access_token.read().await;
            let expires_at = self.token_expires_at.read().await;
            
            if let (Some(token), Some(expires_at)) = (token.as_ref(), expires_at.as_ref()) {
                if Utc::now() < *expires_at {
                    return Ok(token.clone());
                }
            }
        }

        // Need to get a new token
        info!("Requesting new Reddit OAuth2 token");
        
        let auth_string = format!("{}:{}", self.client_id, self.client_secret);
        let auth_header = format!("Basic {}", general_purpose::STANDARD.encode(auth_string));

        let params = [
            ("grant_type", "client_credentials"),
            ("scope", "read"),
        ];

        let response = self.client
            .post(&self.oauth_url)
            .header(AUTHORIZATION, auth_header)
            .header(USER_AGENT, &self.user_agent)
            .form(&params)
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(ConnectorError::AuthenticationFailed {
                message: format!("OAuth2 token request failed: {}", error_text),
            });
        }

        let token_response: RedditTokenResponse = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Calculate expiration time (subtract 5 minutes for safety)
        let expires_at = Utc::now() + chrono::Duration::seconds(token_response.expires_in as i64 - 300);

        // Store the token
        {
            let mut token = self.access_token.write().await;
            let mut expires = self.token_expires_at.write().await;
            *token = Some(token_response.access_token.clone());
            *expires = Some(expires_at);
        }

        info!("Successfully obtained Reddit OAuth2 token");
        Ok(token_response.access_token)
    }

    /// Wait for rate limit if necessary
    async fn wait_for_rate_limit(&self) -> Result<(), ConnectorError> {
        let mut state = self.rate_limit_state.write().await;
        let now = Utc::now();

        // Reset minute window if needed
        if now - state.minute_window_start >= chrono::Duration::minutes(1) {
            state.requests_this_minute = 0;
            state.minute_window_start = now;
        }

        // Reset hour window if needed
        if now - state.hour_window_start >= chrono::Duration::hours(1) {
            state.requests_this_hour = 0;
            state.hour_window_start = now;
        }

        // Check rate limits
        if state.requests_this_minute >= 100 {
            let wait_until = state.minute_window_start + chrono::Duration::minutes(1);
            let wait_duration = (wait_until - now).to_std()
                .map_err(|_| ConnectorError::Generic { 
                    message: "Invalid wait duration".to_string() 
                })?;
            
            warn!("Reddit minute rate limit exceeded, waiting {:?}", wait_duration);
            drop(state); // Release the lock before sleeping
            sleep(wait_duration).await;
            return Ok(());
        }

        if state.requests_this_hour >= 1000 {
            let wait_until = state.hour_window_start + chrono::Duration::hours(1);
            let wait_duration = (wait_until - now).to_std()
                .map_err(|_| ConnectorError::Generic { 
                    message: "Invalid wait duration".to_string() 
                })?;
            
            warn!("Reddit hour rate limit exceeded, waiting {:?}", wait_duration);
            drop(state); // Release the lock before sleeping
            sleep(wait_duration).await;
            return Ok(());
        }

        // Ensure minimum 600ms between requests (100 requests/minute)
        if let Some(last_request) = state.last_request {
            let elapsed = now - last_request;
            if elapsed < chrono::Duration::milliseconds(600) {
                let wait_time = chrono::Duration::milliseconds(600) - elapsed;
                if let Ok(wait_duration) = wait_time.to_std() {
                    drop(state);
                    sleep(wait_duration).await;
                    return Ok(());
                }
            }
        }

        // Update counters
        state.requests_this_minute += 1;
        state.requests_this_hour += 1;
        state.last_request = Some(now);

        Ok(())
    }

    /// Convert Reddit post to normalized SocialPost
    fn convert_post_to_social_post(&self, post: &RedditPost) -> SocialPost {
        // Create author info
        let author = AuthorInfo {
            id_hash: super::utils::anonymize_user_id(
                &post.author_fullname.as_deref().unwrap_or("unknown"), 
                &self.privacy_config.salt
            ),
            username: post.author.as_deref().unwrap_or("deleted").to_string(),
            verified: post.distinguished.is_some(),
            follower_count: None, // Not available in Reddit API
            account_created: None, // Would require separate API call
            account_type: Some("reddit".to_string()),
        };

        // Create metrics
        let metrics = PostMetrics {
            likes: if post.score > 0 { post.score as u64 } else { 0 },
            shares: 0, // Reddit doesn't have shares
            comments: post.num_comments,
            views: None, // Not available in Reddit API
            engagement_rate: None, // Will be calculated later
        };

        // Combine title and selftext for content
        let content = match (&post.title, &post.selftext) {
            (Some(title), Some(selftext)) if !selftext.is_empty() => {
                format!("{}\n\n{}", title, selftext)
            },
            (Some(title), _) => title.clone(),
            (None, Some(selftext)) => selftext.clone(),
            _ => String::new(),
        };

        // Extract hashtags and mentions from content
        let hashtags = super::utils::extract_hashtags(&content);
        let mentions = super::utils::extract_mentions(&content)
            .into_iter()
            .map(|mention| super::utils::anonymize_user_id(&mention, &self.privacy_config.salt))
            .collect();
        let urls = super::utils::extract_urls(&content);

        // Add post URL if it's a link post
        let mut all_urls = urls;
        if let Some(url) = &post.url {
            if url != &format!("https://www.reddit.com{}", post.permalink) {
                all_urls.push(url.clone());
            }
        }

        // Create media attachments
        let media = self.extract_media_from_post(post);

        // Parse creation date
        let created_at = Utc.timestamp_opt(post.created_utc as i64, 0)
            .single()
            .unwrap_or_else(Utc::now);

        // Create metadata
        let mut metadata = HashMap::new();
        metadata.insert("subreddit".to_string(), serde_json::Value::String(post.subreddit.clone()));
        metadata.insert("subreddit_id".to_string(), serde_json::Value::String(post.subreddit_id.clone()));
        metadata.insert("permalink".to_string(), serde_json::Value::String(post.permalink.clone()));
        metadata.insert("score".to_string(), serde_json::Value::Number(serde_json::Number::from(post.score)));
        
        if let Some(upvote_ratio) = post.upvote_ratio {
            metadata.insert("upvote_ratio".to_string(), serde_json::Value::Number(
                serde_json::Number::from_f64(upvote_ratio).unwrap_or(serde_json::Number::from(0))
            ));
        }
        
        if let Some(gilded) = post.gilded {
            metadata.insert("gilded".to_string(), serde_json::Value::Number(serde_json::Number::from(gilded)));
        }
        
        metadata.insert("over_18".to_string(), serde_json::Value::Bool(post.over_18.unwrap_or(false)));
        metadata.insert("spoiler".to_string(), serde_json::Value::Bool(post.spoiler.unwrap_or(false)));
        metadata.insert("locked".to_string(), serde_json::Value::Bool(post.locked.unwrap_or(false)));
        metadata.insert("archived".to_string(), serde_json::Value::Bool(post.archived.unwrap_or(false)));

        if let Some(flair) = &post.link_flair_text {
            metadata.insert("link_flair".to_string(), serde_json::Value::String(flair.clone()));
        }

        // Create privacy flags
        let privacy_flags = PrivacyFlags {
            anonymized: true,
            sensitive_content: super::utils::contains_sensitive_content(&content) || 
                              post.over_18.unwrap_or(false),
            location_generalized: false, // Reddit doesn't provide location data
            retention_policy: self.privacy_config.retention_policy.clone(),
            consent_status: ConsentStatus::Implied, // Public posts imply consent
        };

        let mut post = SocialPost {
            id: post.id.clone(),
            platform: "reddit".to_string(),
            content,
            author,
            created_at,
            metrics,
            location: None, // Reddit doesn't provide location data
            language: None, // Reddit doesn't provide language detection
            media,
            hashtags,
            mentions,
            urls: all_urls,
            metadata,
            privacy_flags,
        };

        // Apply privacy compliance processing
        super::utils::apply_privacy_compliance(&mut post, &self.privacy_config);

        post
    }

    /// Extract media attachments from Reddit post
    fn extract_media_from_post(&self, post: &RedditPost) -> Vec<MediaAttachment> {
        let mut media = Vec::new();

        // Check for video
        if post.is_video.unwrap_or(false) {
            if let Some(media_data) = &post.media {
                if let Some(reddit_video) = media_data.get("reddit_video") {
                    if let Some(fallback_url) = reddit_video.get("fallback_url") {
                        if let Some(url) = fallback_url.as_str() {
                            media.push(MediaAttachment {
                                media_type: "video".to_string(),
                                url: url.to_string(),
                                alt_text: None,
                                dimensions: None,
                                file_size: None,
                            });
                        }
                    }
                }
            }
        }

        // Check for images in preview
        if let Some(preview_data) = &post.preview {
            if let Some(images) = preview_data.get("images") {
                if let Some(images_array) = images.as_array() {
                    for image in images_array {
                        if let Some(source) = image.get("source") {
                            if let Some(url) = source.get("url").and_then(|u| u.as_str()) {
                                let dimensions = if let (Some(width), Some(height)) = (
                                    source.get("width").and_then(|w| w.as_u64()),
                                    source.get("height").and_then(|h| h.as_u64())
                                ) {
                                    Some(MediaDimensions {
                                        width: width as u32,
                                        height: height as u32,
                                    })
                                } else {
                                    None
                                };

                                media.push(MediaAttachment {
                                    media_type: "image".to_string(),
                                    url: url.replace("&amp;", "&"), // Decode HTML entities
                                    alt_text: None,
                                    dimensions,
                                    file_size: None,
                                });
                            }
                        }
                    }
                }
            }
        }

        // Check thumbnail
        if let Some(thumbnail) = &post.thumbnail {
            if thumbnail != "self" && thumbnail != "default" && thumbnail.starts_with("http") {
                media.push(MediaAttachment {
                    media_type: "image".to_string(),
                    url: thumbnail.clone(),
                    alt_text: Some("thumbnail".to_string()),
                    dimensions: None,
                    file_size: None,
                });
            }
        }

        media
    }

    /// Build search URL with parameters
    fn build_search_url(&self, params: &SearchParams) -> String {
        let mut url = format!("{}/search", self.base_url);
        let mut query_params = vec![
            ("q".to_string(), params.query.clone()),
            ("type".to_string(), "link".to_string()),
            ("sort".to_string(), "relevance".to_string()),
            ("limit".to_string(), params.max_results.unwrap_or(25).min(100).to_string()),
        ];

        // Add time filter if dates are specified
        if params.start_date.is_some() || params.end_date.is_some() {
            // Reddit doesn't support exact date ranges, use time filter
            query_params.push(("t".to_string(), "all".to_string()));
        }

        // Build final URL
        let query_string = query_params.iter()
            .map(|(k, v)| format!("{}={}", urlencoding::encode(k), urlencoding::encode(v)))
            .collect::<Vec<_>>()
            .join("&");

        format!("{}?{}", url, query_string)
    }
}

#[async_trait]
impl ApiConnector for RedditConnector {
    fn platform_name(&self) -> &'static str {
        "reddit"
    }

    fn is_configured(&self) -> bool {
        !self.client_id.is_empty() && !self.client_secret.is_empty()
    }

    async fn get_rate_limit_status(&self) -> Result<RateLimitInfo, ConnectorError> {
        let state = self.rate_limit_state.read().await;
        let now = Utc::now();
        
        // Calculate remaining requests for the more restrictive limit
        let minute_remaining = 100 - state.requests_this_minute;
        let hour_remaining = 1000 - state.requests_this_hour;
        let remaining = minute_remaining.min(hour_remaining);
        
        // Calculate next reset time
        let minute_reset = state.minute_window_start + chrono::Duration::minutes(1);
        let hour_reset = state.hour_window_start + chrono::Duration::hours(1);
        let reset_time = if minute_remaining < hour_remaining {
            minute_reset
        } else {
            hour_reset
        };

        Ok(RateLimitInfo {
            remaining,
            limit: 100, // Per minute limit
            reset_time,
            window_duration: chrono::Duration::minutes(1),
        })
    }

    async fn search_posts(&self, params: &SearchParams) -> Result<Vec<SocialPost>, ConnectorError> {
        info!("Searching Reddit for: {}", params.query);
        
        // Get access token
        let token = self.get_access_token().await?;
        
        // Wait for rate limit if necessary
        self.wait_for_rate_limit().await?;

        // Build search URL
        let url = self.build_search_url(params);
        debug!("Reddit search URL: {}", url);

        // Make API request
        let response = self.client
            .get(&url)
            .header(AUTHORIZATION, format!("Bearer {}", token))
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        // Check response status
        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(ConnectorError::ApiError {
                code: status.as_u16(),
                message: format!("Reddit API error: {}", error_text),
            });
        }

        // Parse response
        let search_response: RedditListing = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Convert posts to normalized format
        let mut posts = Vec::new();
        for child in search_response.data.children {
            if child.kind == "t3" { // t3 = link/post
                match serde_json::from_value::<RedditPost>(child.data) {
                    Ok(reddit_post) => {
                        let social_post = self.convert_post_to_social_post(&reddit_post);
                        posts.push(social_post);
                    },
                    Err(e) => {
                        warn!("Failed to parse Reddit post: {}", e);
                        continue;
                    }
                }
            }
        }

        info!("Retrieved {} posts from Reddit", posts.len());
        Ok(posts)
    }

    async fn get_post_by_id(&self, post_id: &str) -> Result<Option<SocialPost>, ConnectorError> {
        info!("Getting Reddit post by ID: {}", post_id);
        
        // Get access token
        let token = self.get_access_token().await?;
        
        // Wait for rate limit if necessary
        self.wait_for_rate_limit().await?;

        // Build URL for single post lookup
        let url = format!("{}/by_id/t3_{}", self.base_url, post_id);

        // Make API request
        let response = self.client
            .get(&url)
            .header(AUTHORIZATION, format!("Bearer {}", token))
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        // Check response status
        if response.status().as_u16() == 404 {
            return Ok(None);
        }

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(ConnectorError::ApiError {
                code: status.as_u16(),
                message: format!("Reddit API error: {}", error_text),
            });
        }

        // Parse response
        let listing: RedditListing = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Extract post data
        if let Some(child) = listing.data.children.first() {
            if child.kind == "t3" {
                match serde_json::from_value::<RedditPost>(child.data.clone()) {
                    Ok(reddit_post) => {
                        let social_post = self.convert_post_to_social_post(&reddit_post);
                        Ok(Some(social_post))
                    },
                    Err(e) => {
                        Err(ConnectorError::ParseError { source: e })
                    }
                }
            } else {
                Ok(None)
            }
        } else {
            Ok(None)
        }
    }

    async fn get_user_posts(&self, user_id: &str, limit: Option<u32>) -> Result<Vec<SocialPost>, ConnectorError> {
        info!("Getting Reddit user posts for: {}", user_id);
        
        // Get access token
        let token = self.get_access_token().await?;
        
        // Wait for rate limit if necessary
        self.wait_for_rate_limit().await?;

        // Build URL for user posts
        let url = format!(
            "{}/user/{}/submitted?limit={}",
            self.base_url,
            user_id,
            limit.unwrap_or(25).min(100)
        );

        // Make API request
        let response = self.client
            .get(&url)
            .header(AUTHORIZATION, format!("Bearer {}", token))
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        // Check response status
        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(ConnectorError::ApiError {
                code: status.as_u16(),
                message: format!("Reddit API error: {}", error_text),
            });
        }

        // Parse response
        let listing: RedditListing = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Convert posts to normalized format
        let mut posts = Vec::new();
        for child in listing.data.children {
            if child.kind == "t3" { // t3 = link/post
                match serde_json::from_value::<RedditPost>(child.data) {
                    Ok(reddit_post) => {
                        let social_post = self.convert_post_to_social_post(&reddit_post);
                        posts.push(social_post);
                    },
                    Err(e) => {
                        warn!("Failed to parse Reddit post: {}", e);
                        continue;
                    }
                }
            }
        }

        info!("Retrieved {} user posts from Reddit", posts.len());
        Ok(posts)
    }

    async fn get_trending_topics(&self, _location: Option<&str>) -> Result<Vec<String>, ConnectorError> {
        info!("Getting trending subreddits from Reddit");
        
        // Get access token
        let token = self.get_access_token().await?;
        
        // Wait for rate limit if necessary
        self.wait_for_rate_limit().await?;

        // Get popular subreddits as trending topics
        let url = format!("{}/subreddits/popular?limit=50", self.base_url);

        // Make API request
        let response = self.client
            .get(&url)
            .header(AUTHORIZATION, format!("Bearer {}", token))
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        // Check response status
        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(ConnectorError::ApiError {
                code: status.as_u16(),
                message: format!("Reddit API error: {}", error_text),
            });
        }

        // Parse response
        let listing: RedditListing = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Extract subreddit names
        let mut topics = Vec::new();
        for child in listing.data.children {
            if child.kind == "t5" { // t5 = subreddit
                if let Some(display_name) = child.data.get("display_name") {
                    if let Some(name) = display_name.as_str() {
                        topics.push(format!("r/{}", name));
                    }
                }
            }
        }

        info!("Retrieved {} trending topics from Reddit", topics.len());
        Ok(topics)
    }

    async fn validate_credentials(&self) -> Result<bool, ConnectorError> {
        info!("Validating Reddit API credentials");
        
        match self.get_access_token().await {
            Ok(_) => {
                info!("Reddit API credentials are valid");
                Ok(true)
            },
            Err(ConnectorError::AuthenticationFailed { .. }) => {
                error!("Reddit API credentials are invalid");
                Ok(false)
            },
            Err(e) => Err(e),
        }
    }

    fn get_config_requirements(&self) -> Vec<ConfigRequirement> {
        vec![
            ConfigRequirement {
                key: "REDDIT_CLIENT_ID".to_string(),
                description: "Reddit application client ID".to_string(),
                required: true,
                example: Some("abcdefghijklmn".to_string()),
                source_url: Some("https://www.reddit.com/prefs/apps".to_string()),
            },
            ConfigRequirement {
                key: "REDDIT_CLIENT_SECRET".to_string(),
                description: "Reddit application client secret".to_string(),
                required: true,
                example: Some("1234567890abcdefghijklmnopqrstuvwxyz".to_string()),
                source_url: Some("https://www.reddit.com/prefs/apps".to_string()),
            },
            ConfigRequirement {
                key: "REDDIT_USER_AGENT".to_string(),
                description: "User agent string for Reddit API requests".to_string(),
                required: false,
                example: Some("SentinelBERT/1.0 (by /u/yourusername)".to_string()),
                source_url: Some("https://github.com/reddit-archive/reddit/wiki/API".to_string()),
            },
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_reddit_connector_creation() {
        let connector = RedditConnector::new(
            "test_client_id".to_string(),
            "test_client_secret".to_string(),
            PrivacyConfig::default()
        );
        
        assert_eq!(connector.platform_name(), "reddit");
        assert!(connector.is_configured());
    }

    #[test]
    fn test_build_search_url() {
        let connector = RedditConnector::new(
            "test_client_id".to_string(),
            "test_client_secret".to_string(),
            PrivacyConfig::default()
        );
        
        let params = SearchParams {
            query: "climate change".to_string(),
            max_results: Some(50),
            start_date: None,
            end_date: None,
            language: None,
            location: None,
            content_type: None,
            extra_params: HashMap::new(),
        };
        
        let url = connector.build_search_url(&params);
        assert!(url.contains("climate%20change"));
        assert!(url.contains("limit=50"));
    }

    #[test]
    fn test_config_requirements() {
        let connector = RedditConnector::new(
            "test_client_id".to_string(),
            "test_client_secret".to_string(),
            PrivacyConfig::default()
        );
        
        let requirements = connector.get_config_requirements();
        assert_eq!(requirements.len(), 3);
        assert_eq!(requirements[0].key, "REDDIT_CLIENT_ID");
        assert_eq!(requirements[1].key, "REDDIT_CLIENT_SECRET");
        assert_eq!(requirements[2].key, "REDDIT_USER_AGENT");
    }
}
/*
 * =============================================================================
 * Twitter/X.com API Connector for SentinelBERT
 * =============================================================================
 * 
 * This module implements the Twitter API v2 connector using the Essential Access
 * free tier. It provides comprehensive tweet search and data collection capabilities
 * while respecting rate limits and privacy requirements.
 * 
 * Twitter API v2 Essential Access Features:
 * - 500,000 tweets per month
 * - 300 requests per 15 minutes for search
 * - Real-time tweet search
 * - User timeline access
 * - Tweet metrics and engagement data
 * 
 * Rate Limits (Essential Access):
 * - Tweet search: 300 requests/15min, 1 request/second
 * - User lookup: 300 requests/15min
 * - Tweet lookup: 300 requests/15min
 * 
 * Setup Instructions:
 * 1. Visit https://developer.twitter.com/
 * 2. Apply for Essential Access (free)
 * 3. Create a new app in the developer portal
 * 4. Generate Bearer Token
 * 5. Add token to environment: TWITTER_BEARER_TOKEN=your_token_here
 * 
 * Privacy Compliance:
 * - User IDs are hashed for anonymization
 * - Location data is generalized to protect privacy
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

/// Twitter API v2 connector implementation
/// 
/// This connector uses Twitter's API v2 with Essential Access (free tier)
/// to search and collect tweets for sentiment analysis.
pub struct TwitterConnector {
    /// HTTP client for API requests
    client: Client,
    
    /// Bearer token for authentication
    bearer_token: String,
    
    /// Privacy configuration
    privacy_config: PrivacyConfig,
    
    /// Rate limiting state
    rate_limit_state: tokio::sync::RwLock<RateLimitState>,
    
    /// Base API URL
    base_url: String,
}

/// Internal rate limiting state
#[derive(Debug, Clone)]
struct RateLimitState {
    /// Remaining requests in current window
    remaining: u32,
    
    /// Total requests allowed per window
    limit: u32,
    
    /// Window reset time
    reset_time: DateTime<Utc>,
    
    /// Last request timestamp
    last_request: Option<DateTime<Utc>>,
}

impl Default for RateLimitState {
    fn default() -> Self {
        Self {
            remaining: 300, // Default for Essential Access
            limit: 300,
            reset_time: Utc::now() + chrono::Duration::minutes(15),
            last_request: None,
        }
    }
}

/// Twitter API v2 search response structure
#[derive(Debug, Deserialize)]
struct TwitterSearchResponse {
    data: Option<Vec<TwitterTweet>>,
    includes: Option<TwitterIncludes>,
    meta: TwitterMeta,
    errors: Option<Vec<TwitterError>>,
}

/// Twitter tweet data structure
#[derive(Debug, Deserialize)]
struct TwitterTweet {
    id: String,
    text: String,
    author_id: Option<String>,
    created_at: Option<String>,
    public_metrics: Option<TwitterMetrics>,
    geo: Option<TwitterGeo>,
    lang: Option<String>,
    entities: Option<TwitterEntities>,
    attachments: Option<TwitterAttachments>,
    context_annotations: Option<Vec<TwitterContextAnnotation>>,
    referenced_tweets: Option<Vec<TwitterReferencedTweet>>,
}

/// Twitter user data structure
#[derive(Debug, Deserialize)]
struct TwitterUser {
    id: String,
    username: String,
    name: String,
    verified: Option<bool>,
    public_metrics: Option<TwitterUserMetrics>,
    created_at: Option<String>,
    description: Option<String>,
    profile_image_url: Option<String>,
}

/// Twitter metrics structure
#[derive(Debug, Deserialize)]
struct TwitterMetrics {
    retweet_count: Option<u64>,
    like_count: Option<u64>,
    reply_count: Option<u64>,
    quote_count: Option<u64>,
    impression_count: Option<u64>,
}

/// Twitter user metrics structure
#[derive(Debug, Deserialize)]
struct TwitterUserMetrics {
    followers_count: Option<u64>,
    following_count: Option<u64>,
    tweet_count: Option<u64>,
    listed_count: Option<u64>,
}

/// Twitter geographic information
#[derive(Debug, Deserialize)]
struct TwitterGeo {
    coordinates: Option<TwitterCoordinates>,
    place_id: Option<String>,
}

/// Twitter coordinates
#[derive(Debug, Deserialize)]
struct TwitterCoordinates {
    #[serde(rename = "type")]
    coord_type: String,
    coordinates: Vec<f64>,
}

/// Twitter entities (hashtags, mentions, URLs)
#[derive(Debug, Deserialize)]
struct TwitterEntities {
    hashtags: Option<Vec<TwitterHashtag>>,
    mentions: Option<Vec<TwitterMention>>,
    urls: Option<Vec<TwitterUrl>>,
    annotations: Option<Vec<TwitterAnnotation>>,
}

/// Twitter hashtag
#[derive(Debug, Deserialize)]
struct TwitterHashtag {
    start: usize,
    end: usize,
    tag: String,
}

/// Twitter mention
#[derive(Debug, Deserialize)]
struct TwitterMention {
    start: usize,
    end: usize,
    username: String,
    id: Option<String>,
}

/// Twitter URL
#[derive(Debug, Deserialize)]
struct TwitterUrl {
    start: usize,
    end: usize,
    url: String,
    expanded_url: Option<String>,
    display_url: Option<String>,
    unwound_url: Option<String>,
}

/// Twitter annotation
#[derive(Debug, Deserialize)]
struct TwitterAnnotation {
    start: usize,
    end: usize,
    probability: f64,
    #[serde(rename = "type")]
    annotation_type: String,
    normalized_text: Option<String>,
}

/// Twitter attachments
#[derive(Debug, Deserialize)]
struct TwitterAttachments {
    media_keys: Option<Vec<String>>,
    poll_ids: Option<Vec<String>>,
}

/// Twitter context annotation
#[derive(Debug, Deserialize)]
struct TwitterContextAnnotation {
    domain: TwitterContextDomain,
    entity: TwitterContextEntity,
}

/// Twitter context domain
#[derive(Debug, Deserialize)]
struct TwitterContextDomain {
    id: String,
    name: String,
    description: Option<String>,
}

/// Twitter context entity
#[derive(Debug, Deserialize)]
struct TwitterContextEntity {
    id: String,
    name: String,
    description: Option<String>,
}

/// Twitter referenced tweet
#[derive(Debug, Deserialize)]
struct TwitterReferencedTweet {
    #[serde(rename = "type")]
    ref_type: String,
    id: String,
}

/// Twitter includes (users, media, places)
#[derive(Debug, Deserialize)]
struct TwitterIncludes {
    users: Option<Vec<TwitterUser>>,
    media: Option<Vec<TwitterMedia>>,
    places: Option<Vec<TwitterPlace>>,
    tweets: Option<Vec<TwitterTweet>>,
}

/// Twitter media
#[derive(Debug, Deserialize)]
struct TwitterMedia {
    media_key: String,
    #[serde(rename = "type")]
    media_type: String,
    url: Option<String>,
    preview_image_url: Option<String>,
    alt_text: Option<String>,
    width: Option<u32>,
    height: Option<u32>,
    duration_ms: Option<u64>,
    public_metrics: Option<TwitterMediaMetrics>,
}

/// Twitter media metrics
#[derive(Debug, Deserialize)]
struct TwitterMediaMetrics {
    view_count: Option<u64>,
}

/// Twitter place
#[derive(Debug, Deserialize)]
struct TwitterPlace {
    id: String,
    full_name: String,
    name: String,
    country: Option<String>,
    country_code: Option<String>,
    geo: Option<serde_json::Value>,
    place_type: Option<String>,
}

/// Twitter API response metadata
#[derive(Debug, Deserialize)]
struct TwitterMeta {
    result_count: Option<u32>,
    next_token: Option<String>,
    previous_token: Option<String>,
    newest_id: Option<String>,
    oldest_id: Option<String>,
}

/// Twitter API error
#[derive(Debug, Deserialize)]
struct TwitterError {
    title: String,
    detail: Option<String>,
    #[serde(rename = "type")]
    error_type: Option<String>,
    resource_type: Option<String>,
    parameter: Option<String>,
    value: Option<String>,
}

impl TwitterConnector {
    /// Create a new Twitter connector
    /// 
    /// # Arguments
    /// * `bearer_token` - Twitter API Bearer Token (Essential Access)
    /// * `privacy_config` - Privacy configuration for data processing
    /// 
    /// # Example
    /// ```rust
    /// let connector = TwitterConnector::new(
    ///     "your_bearer_token".to_string(),
    ///     PrivacyConfig::default()
    /// );
    /// ```
    pub fn new(bearer_token: String, privacy_config: PrivacyConfig) -> Self {
        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", bearer_token))
                .expect("Invalid bearer token format")
        );
        headers.insert(
            USER_AGENT,
            HeaderValue::from_static("SentinelBERT/1.0 (Law Enforcement Analytics)")
        );

        let client = Client::builder()
            .default_headers(headers)
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            client,
            bearer_token,
            privacy_config,
            rate_limit_state: tokio::sync::RwLock::new(RateLimitState::default()),
            base_url: "https://api.twitter.com/2".to_string(),
        }
    }

    /// Wait for rate limit if necessary
    async fn wait_for_rate_limit(&self) -> Result<(), ConnectorError> {
        let state = self.rate_limit_state.read().await;
        
        if state.remaining == 0 {
            let now = Utc::now();
            if now < state.reset_time {
                let wait_duration = (state.reset_time - now).to_std()
                    .map_err(|_| ConnectorError::Generic { 
                        message: "Invalid wait duration".to_string() 
                    })?;
                
                warn!("Rate limit exceeded, waiting {:?} until reset", wait_duration);
                drop(state); // Release the lock before sleeping
                sleep(wait_duration).await;
            }
        }
        
        // Ensure minimum 1 second between requests for Essential Access
        if let Some(last_request) = state.last_request {
            let elapsed = Utc::now() - last_request;
            if elapsed < chrono::Duration::seconds(1) {
                let wait_time = chrono::Duration::seconds(1) - elapsed;
                if let Ok(wait_duration) = wait_time.to_std() {
                    drop(state);
                    sleep(wait_duration).await;
                }
            }
        }
        
        Ok(())
    }

    /// Update rate limit state from response headers
    async fn update_rate_limit(&self, headers: &HeaderMap) {
        let mut state = self.rate_limit_state.write().await;
        
        if let Some(remaining) = headers.get("x-rate-limit-remaining") {
            if let Ok(remaining_str) = remaining.to_str() {
                if let Ok(remaining_val) = remaining_str.parse::<u32>() {
                    state.remaining = remaining_val;
                }
            }
        }
        
        if let Some(limit) = headers.get("x-rate-limit-limit") {
            if let Ok(limit_str) = limit.to_str() {
                if let Ok(limit_val) = limit_str.parse::<u32>() {
                    state.limit = limit_val;
                }
            }
        }
        
        if let Some(reset) = headers.get("x-rate-limit-reset") {
            if let Ok(reset_str) = reset.to_str() {
                if let Ok(reset_timestamp) = reset_str.parse::<i64>() {
                    state.reset_time = Utc.timestamp_opt(reset_timestamp, 0).single()
                        .unwrap_or_else(|| Utc::now() + chrono::Duration::minutes(15));
                }
            }
        }
        
        state.last_request = Some(Utc::now());
    }

    /// Convert Twitter tweet to normalized SocialPost
    fn convert_tweet_to_post(
        &self,
        tweet: &TwitterTweet,
        users: &Option<Vec<TwitterUser>>,
        media: &Option<Vec<TwitterMedia>>,
        places: &Option<Vec<TwitterPlace>>,
    ) -> SocialPost {
        // Find author information
        let author = if let Some(author_id) = &tweet.author_id {
            if let Some(users) = users {
                users.iter()
                    .find(|u| u.id == *author_id)
                    .map(|u| self.convert_user_to_author(u))
                    .unwrap_or_else(|| self.create_anonymous_author(author_id))
            } else {
                self.create_anonymous_author(author_id)
            }
        } else {
            self.create_anonymous_author("unknown")
        };

        // Extract metrics
        let metrics = if let Some(public_metrics) = &tweet.public_metrics {
            PostMetrics {
                likes: public_metrics.like_count.unwrap_or(0),
                shares: public_metrics.retweet_count.unwrap_or(0) + 
                       public_metrics.quote_count.unwrap_or(0),
                comments: public_metrics.reply_count.unwrap_or(0),
                views: public_metrics.impression_count,
                engagement_rate: None, // Will be calculated later
            }
        } else {
            PostMetrics {
                likes: 0,
                shares: 0,
                comments: 0,
                views: None,
                engagement_rate: None,
            }
        };

        // Extract location
        let location = tweet.geo.as_ref().and_then(|geo| {
            geo.coordinates.as_ref().map(|coords| {
                if coords.coordinates.len() >= 2 {
                    GeoLocation {
                        longitude: coords.coordinates[0],
                        latitude: coords.coordinates[1],
                        radius_km: 1.0, // Default radius
                        name: None,
                    }
                } else {
                    GeoLocation {
                        latitude: 0.0,
                        longitude: 0.0,
                        radius_km: 1.0,
                        name: None,
                    }
                }
            })
        });

        // Extract hashtags
        let hashtags = tweet.entities.as_ref()
            .and_then(|e| e.hashtags.as_ref())
            .map(|tags| tags.iter().map(|t| t.tag.clone()).collect())
            .unwrap_or_default();

        // Extract mentions
        let mentions = tweet.entities.as_ref()
            .and_then(|e| e.mentions.as_ref())
            .map(|mentions| mentions.iter().map(|m| {
                super::utils::anonymize_user_id(&m.username, &self.privacy_config.salt)
            }).collect())
            .unwrap_or_default();

        // Extract URLs
        let urls = tweet.entities.as_ref()
            .and_then(|e| e.urls.as_ref())
            .map(|urls| urls.iter().map(|u| {
                u.expanded_url.as_ref()
                    .or(u.unwound_url.as_ref())
                    .unwrap_or(&u.url)
                    .clone()
            }).collect())
            .unwrap_or_default();

        // Extract media attachments
        let media_attachments = if let Some(attachments) = &tweet.attachments {
            if let Some(media_keys) = &attachments.media_keys {
                if let Some(media_list) = media {
                    media_keys.iter()
                        .filter_map(|key| {
                            media_list.iter().find(|m| m.media_key == *key)
                        })
                        .map(|m| self.convert_twitter_media_to_attachment(m))
                        .collect()
                } else {
                    Vec::new()
                }
            } else {
                Vec::new()
            }
        } else {
            Vec::new()
        };

        // Parse creation date
        let created_at = tweet.created_at.as_ref()
            .and_then(|date_str| DateTime::parse_from_rfc3339(date_str).ok())
            .map(|dt| dt.with_timezone(&Utc))
            .unwrap_or_else(Utc::now);

        // Create metadata
        let mut metadata = HashMap::new();
        metadata.insert("tweet_id".to_string(), serde_json::Value::String(tweet.id.clone()));
        
        if let Some(context_annotations) = &tweet.context_annotations {
            let contexts: Vec<serde_json::Value> = context_annotations.iter()
                .map(|ctx| serde_json::json!({
                    "domain": ctx.domain.name,
                    "entity": ctx.entity.name
                }))
                .collect();
            metadata.insert("context_annotations".to_string(), serde_json::Value::Array(contexts));
        }

        if let Some(referenced_tweets) = &tweet.referenced_tweets {
            let refs: Vec<serde_json::Value> = referenced_tweets.iter()
                .map(|rt| serde_json::json!({
                    "type": rt.ref_type,
                    "id": rt.id
                }))
                .collect();
            metadata.insert("referenced_tweets".to_string(), serde_json::Value::Array(refs));
        }

        // Create privacy flags
        let privacy_flags = PrivacyFlags {
            anonymized: true,
            sensitive_content: super::utils::contains_sensitive_content(&tweet.text),
            location_generalized: location.is_some(),
            retention_policy: self.privacy_config.retention_policy.clone(),
            consent_status: ConsentStatus::Implied, // Public tweets imply consent
        };

        let mut post = SocialPost {
            id: tweet.id.clone(),
            platform: "twitter".to_string(),
            content: tweet.text.clone(),
            author,
            created_at,
            metrics,
            location,
            language: tweet.lang.clone(),
            media: media_attachments,
            hashtags,
            mentions,
            urls,
            metadata,
            privacy_flags,
        };

        // Apply privacy compliance processing
        super::utils::apply_privacy_compliance(&mut post, &self.privacy_config);

        post
    }

    /// Convert Twitter user to AuthorInfo
    fn convert_user_to_author(&self, user: &TwitterUser) -> AuthorInfo {
        let follower_count = user.public_metrics.as_ref()
            .and_then(|m| m.followers_count);

        let account_created = user.created_at.as_ref()
            .and_then(|date_str| DateTime::parse_from_rfc3339(date_str).ok())
            .map(|dt| dt.with_timezone(&Utc));

        AuthorInfo {
            id_hash: super::utils::anonymize_user_id(&user.id, &self.privacy_config.salt),
            username: user.username.clone(),
            verified: user.verified.unwrap_or(false),
            follower_count,
            account_created,
            account_type: Some("twitter".to_string()),
        }
    }

    /// Create anonymous author info
    fn create_anonymous_author(&self, user_id: &str) -> AuthorInfo {
        AuthorInfo {
            id_hash: super::utils::anonymize_user_id(user_id, &self.privacy_config.salt),
            username: "anonymous".to_string(),
            verified: false,
            follower_count: None,
            account_created: None,
            account_type: Some("twitter".to_string()),
        }
    }

    /// Convert Twitter media to MediaAttachment
    fn convert_twitter_media_to_attachment(&self, media: &TwitterMedia) -> MediaAttachment {
        let dimensions = if let (Some(width), Some(height)) = (media.width, media.height) {
            Some(MediaDimensions { width, height })
        } else {
            None
        };

        MediaAttachment {
            media_type: media.media_type.clone(),
            url: media.url.as_ref()
                .or(media.preview_image_url.as_ref())
                .unwrap_or(&"".to_string())
                .clone(),
            alt_text: media.alt_text.clone(),
            dimensions,
            file_size: None, // Not provided by Twitter API
        }
    }

    /// Build search query URL with parameters
    fn build_search_url(&self, params: &SearchParams) -> String {
        let mut url = format!("{}/tweets/search/recent", self.base_url);
        let mut query_params = vec![
            ("query".to_string(), params.query.clone()),
            ("max_results".to_string(), params.max_results.unwrap_or(10).min(100).to_string()),
        ];

        // Add tweet fields
        query_params.push((
            "tweet.fields".to_string(),
            "id,text,author_id,created_at,public_metrics,geo,lang,entities,attachments,context_annotations,referenced_tweets".to_string()
        ));

        // Add user fields
        query_params.push((
            "user.fields".to_string(),
            "id,username,name,verified,public_metrics,created_at,description".to_string()
        ));

        // Add media fields
        query_params.push((
            "media.fields".to_string(),
            "media_key,type,url,preview_image_url,alt_text,width,height,duration_ms,public_metrics".to_string()
        ));

        // Add place fields
        query_params.push((
            "place.fields".to_string(),
            "id,full_name,name,country,country_code,geo,place_type".to_string()
        ));

        // Add expansions
        query_params.push((
            "expansions".to_string(),
            "author_id,attachments.media_keys,geo.place_id,referenced_tweets.id".to_string()
        ));

        // Add date filters
        if let Some(start_date) = params.start_date {
            query_params.push(("start_time".to_string(), start_date.to_rfc3339()));
        }

        if let Some(end_date) = params.end_date {
            query_params.push(("end_time".to_string(), end_date.to_rfc3339()));
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
impl ApiConnector for TwitterConnector {
    fn platform_name(&self) -> &'static str {
        "twitter"
    }

    fn is_configured(&self) -> bool {
        !self.bearer_token.is_empty()
    }

    async fn get_rate_limit_status(&self) -> Result<RateLimitInfo, ConnectorError> {
        let state = self.rate_limit_state.read().await;
        Ok(RateLimitInfo {
            remaining: state.remaining,
            limit: state.limit,
            reset_time: state.reset_time,
            window_duration: chrono::Duration::minutes(15),
        })
    }

    async fn search_posts(&self, params: &SearchParams) -> Result<Vec<SocialPost>, ConnectorError> {
        info!("Searching Twitter for: {}", params.query);
        
        // Wait for rate limit if necessary
        self.wait_for_rate_limit().await?;

        // Build search URL
        let url = self.build_search_url(params);
        debug!("Twitter search URL: {}", url);

        // Make API request
        let response = self.client
            .get(&url)
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        // Update rate limit state
        self.update_rate_limit(response.headers()).await;

        // Check response status
        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(ConnectorError::ApiError {
                code: status.as_u16(),
                message: format!("Twitter API error: {}", error_text),
            });
        }

        // Parse response
        let search_response: TwitterSearchResponse = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Handle API errors
        if let Some(errors) = search_response.errors {
            let error_messages: Vec<String> = errors.iter()
                .map(|e| format!("{}: {}", e.title, e.detail.as_deref().unwrap_or("No details")))
                .collect();
            
            return Err(ConnectorError::ApiError {
                code: 400,
                message: format!("Twitter API errors: {}", error_messages.join(", ")),
            });
        }

        // Convert tweets to normalized posts
        let posts = if let Some(tweets) = search_response.data {
            tweets.iter()
                .map(|tweet| self.convert_tweet_to_post(
                    tweet,
                    &search_response.includes.as_ref().and_then(|i| i.users.as_ref()),
                    &search_response.includes.as_ref().and_then(|i| i.media.as_ref()),
                    &search_response.includes.as_ref().and_then(|i| i.places.as_ref()),
                ))
                .collect()
        } else {
            Vec::new()
        };

        info!("Retrieved {} tweets from Twitter", posts.len());
        Ok(posts)
    }

    async fn get_post_by_id(&self, post_id: &str) -> Result<Option<SocialPost>, ConnectorError> {
        info!("Getting Twitter post by ID: {}", post_id);
        
        // Wait for rate limit if necessary
        self.wait_for_rate_limit().await?;

        // Build URL for single tweet lookup
        let url = format!(
            "{}/tweets/{}?tweet.fields=id,text,author_id,created_at,public_metrics,geo,lang,entities,attachments,context_annotations,referenced_tweets&user.fields=id,username,name,verified,public_metrics,created_at&media.fields=media_key,type,url,preview_image_url,alt_text,width,height&expansions=author_id,attachments.media_keys",
            self.base_url, post_id
        );

        // Make API request
        let response = self.client
            .get(&url)
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        // Update rate limit state
        self.update_rate_limit(response.headers()).await;

        // Check response status
        if response.status().as_u16() == 404 {
            return Ok(None);
        }

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            
            return Err(ConnectorError::ApiError {
                code: status.as_u16(),
                message: format!("Twitter API error: {}", error_text),
            });
        }

        // Parse response
        let tweet_response: serde_json::Value = response
            .json()
            .await
            .map_err(|e| ConnectorError::ParseError { 
                source: serde_json::Error::custom(e.to_string()) 
            })?;

        // Extract tweet data
        if let Some(tweet_data) = tweet_response.get("data") {
            let tweet: TwitterTweet = serde_json::from_value(tweet_data.clone())
                .map_err(|e| ConnectorError::ParseError { source: e })?;

            let includes = tweet_response.get("includes")
                .and_then(|i| serde_json::from_value(i.clone()).ok());

            let post = self.convert_tweet_to_post(
                &tweet,
                &includes.as_ref().and_then(|i: &TwitterIncludes| i.users.as_ref()),
                &includes.as_ref().and_then(|i: &TwitterIncludes| i.media.as_ref()),
                &includes.as_ref().and_then(|i: &TwitterIncludes| i.places.as_ref()),
            );

            Ok(Some(post))
        } else {
            Ok(None)
        }
    }

    async fn get_user_posts(&self, user_id: &str, limit: Option<u32>) -> Result<Vec<SocialPost>, ConnectorError> {
        // Twitter API v2 Essential Access doesn't support user timeline
        // This would require Academic Research or higher tier
        Err(ConnectorError::ConfigError {
            message: "User timeline access requires Twitter API Academic Research access or higher".to_string(),
        })
    }

    async fn get_trending_topics(&self, _location: Option<&str>) -> Result<Vec<String>, ConnectorError> {
        // Trending topics require Twitter API v1.1 or higher tier access
        Err(ConnectorError::ConfigError {
            message: "Trending topics require Twitter API v1.1 or higher tier access".to_string(),
        })
    }

    async fn validate_credentials(&self) -> Result<bool, ConnectorError> {
        info!("Validating Twitter API credentials");
        
        // Make a simple search request to validate credentials
        let url = format!(
            "{}/tweets/search/recent?query=test&max_results=10",
            self.base_url
        );

        let response = self.client
            .get(&url)
            .send()
            .await
            .map_err(|e| ConnectorError::NetworkError { source: e })?;

        match response.status().as_u16() {
            200 => {
                info!("Twitter API credentials are valid");
                Ok(true)
            },
            401 => {
                error!("Twitter API credentials are invalid");
                Ok(false)
            },
            _ => {
                let error_text = response.text().await.unwrap_or_default();
                Err(ConnectorError::ApiError {
                    code: response.status().as_u16(),
                    message: format!("Credential validation failed: {}", error_text),
                })
            }
        }
    }

    fn get_config_requirements(&self) -> Vec<ConfigRequirement> {
        vec![
            ConfigRequirement {
                key: "TWITTER_BEARER_TOKEN".to_string(),
                description: "Twitter API Bearer Token (Essential Access)".to_string(),
                required: true,
                example: Some("AAAAAAAAAAAAAAAAAAAAAMLheAAAAAAA0%2BuSeid%2BULvsea4JtiGRiSDSJSI%3DEUifiRBkKG5E2XzMDjRfl76ZC9Ub0wnz4XsNiRVBChTYbJcE3F".to_string()),
                source_url: Some("https://developer.twitter.com/en/portal/dashboard".to_string()),
            },
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_twitter_connector_creation() {
        let connector = TwitterConnector::new(
            "test_token".to_string(),
            PrivacyConfig::default()
        );
        
        assert_eq!(connector.platform_name(), "twitter");
        assert!(connector.is_configured());
    }

    #[test]
    fn test_build_search_url() {
        let connector = TwitterConnector::new(
            "test_token".to_string(),
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
        assert!(url.contains("max_results=50"));
    }

    #[test]
    fn test_config_requirements() {
        let connector = TwitterConnector::new(
            "test_token".to_string(),
            PrivacyConfig::default()
        );
        
        let requirements = connector.get_config_requirements();
        assert_eq!(requirements.len(), 1);
        assert_eq!(requirements[0].key, "TWITTER_BEARER_TOKEN");
        assert!(requirements[0].required);
    }
}
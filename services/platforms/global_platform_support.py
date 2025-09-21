#!/usr/bin/env python3
"""
Global Social Media Platform Support for InsideOut
Supports major global and regional platforms for content analysis
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Types of social media platforms"""
    MICROBLOGGING = "microblogging"  # Twitter, Mastodon
    SOCIAL_NETWORK = "social_network"  # Facebook, LinkedIn
    MEDIA_SHARING = "media_sharing"  # Instagram, TikTok, YouTube
    MESSAGING = "messaging"  # WhatsApp, Telegram, Signal
    FORUM = "forum"  # Reddit, Discord
    PROFESSIONAL = "professional"  # LinkedIn, Xing
    REGIONAL = "regional"  # WeChat, Koo, ShareChat

class ContentType(Enum):
    """Types of content supported"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    POLL = "poll"

class GeographicScope(Enum):
    """Geographic scope of platforms"""
    GLOBAL = "global"
    REGIONAL = "regional"
    NATIONAL = "national"
    LOCAL = "local"

@dataclass
class PlatformConfig:
    """Configuration for each supported platform"""
    platform_id: str
    name: str
    platform_type: PlatformType
    geographic_scope: GeographicScope
    primary_regions: List[str]
    content_types: List[ContentType]
    max_content_length: int
    supports_hashtags: bool
    supports_mentions: bool
    supports_reposting: bool
    api_available: bool
    rate_limits: Dict[str, int]
    content_patterns: Dict[str, str]
    metadata_fields: List[str]
    viral_indicators: List[str]

class GlobalPlatformSupport:
    """Global platform support system"""
    
    def __init__(self):
        self.platforms = self._initialize_platforms()
        self.content_extractors = self._initialize_extractors()
        
    def _initialize_platforms(self) -> Dict[str, PlatformConfig]:
        """Initialize supported platforms"""
        platforms = {}
        
        # Global Platforms
        global_platforms = [
            # Microblogging Platforms
            PlatformConfig(
                platform_id="twitter",
                name="Twitter/X",
                platform_type=PlatformType.MICROBLOGGING,
                geographic_scope=GeographicScope.GLOBAL,
                primary_regions=["Global"],
                content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO],
                max_content_length=280,
                supports_hashtags=True,
                supports_mentions=True,
                supports_reposting=True,
                api_available=True,
                rate_limits={"posts": 300, "searches": 180},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "mention": r"@[\w]+",
                    "url": r"https?://[^\s]+",
                    "retweet": r"RT @[\w]+:"
                },
                metadata_fields=["tweet_id", "user_id", "timestamp", "location", "device", "engagement"],
                viral_indicators=["retweet_count", "like_count", "reply_count", "quote_count"]
            ),
            
            # Social Networks
            PlatformConfig(
                platform_id="facebook",
                name="Facebook",
                platform_type=PlatformType.SOCIAL_NETWORK,
                geographic_scope=GeographicScope.GLOBAL,
                primary_regions=["Global"],
                content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO, ContentType.LIVE_STREAM],
                max_content_length=63206,
                supports_hashtags=True,
                supports_mentions=True,
                supports_reposting=True,
                api_available=True,
                rate_limits={"posts": 200, "searches": 100},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "mention": r"@[\w\s]+",
                    "url": r"https?://[^\s]+",
                    "share": r"shared.*post"
                },
                metadata_fields=["post_id", "user_id", "timestamp", "location", "privacy_setting", "engagement"],
                viral_indicators=["share_count", "like_count", "comment_count", "reaction_count"]
            ),
            
            # Media Sharing Platforms
            PlatformConfig(
                platform_id="instagram",
                name="Instagram",
                platform_type=PlatformType.MEDIA_SHARING,
                geographic_scope=GeographicScope.GLOBAL,
                primary_regions=["Global"],
                content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.STORY],
                max_content_length=2200,
                supports_hashtags=True,
                supports_mentions=True,
                supports_reposting=False,
                api_available=True,
                rate_limits={"posts": 100, "searches": 60},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "mention": r"@[\w\.]+",
                    "url": r"https?://[^\s]+",
                    "story": r"story|stories"
                },
                metadata_fields=["post_id", "user_id", "timestamp", "location", "media_type", "engagement"],
                viral_indicators=["like_count", "comment_count", "save_count", "share_count"]
            ),
            
            PlatformConfig(
                platform_id="youtube",
                name="YouTube",
                platform_type=PlatformType.MEDIA_SHARING,
                geographic_scope=GeographicScope.GLOBAL,
                primary_regions=["Global"],
                content_types=[ContentType.VIDEO, ContentType.LIVE_STREAM],
                max_content_length=5000,
                supports_hashtags=True,
                supports_mentions=False,
                supports_reposting=False,
                api_available=True,
                rate_limits={"videos": 100, "searches": 100},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "url": r"https?://[^\s]+",
                    "timestamp": r"\d{1,2}:\d{2}",
                    "channel": r"@[\w]+"
                },
                metadata_fields=["video_id", "channel_id", "timestamp", "duration", "category", "engagement"],
                viral_indicators=["view_count", "like_count", "comment_count", "share_count", "subscriber_gain"]
            ),
            
            PlatformConfig(
                platform_id="tiktok",
                name="TikTok",
                platform_type=PlatformType.MEDIA_SHARING,
                geographic_scope=GeographicScope.GLOBAL,
                primary_regions=["Global", "Asia", "Americas", "Europe"],
                content_types=[ContentType.VIDEO, ContentType.LIVE_STREAM],
                max_content_length=2200,
                supports_hashtags=True,
                supports_mentions=True,
                supports_reposting=True,
                api_available=True,
                rate_limits={"videos": 100, "searches": 50},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "mention": r"@[\w\.]+",
                    "sound": r"original sound|trending sound",
                    "duet": r"duet with @[\w\.]+"
                },
                metadata_fields=["video_id", "user_id", "timestamp", "sound_id", "effects", "engagement"],
                viral_indicators=["view_count", "like_count", "share_count", "comment_count", "duet_count"]
            ),
            
            # Regional/Indian Platforms
            PlatformConfig(
                platform_id="koo",
                name="Koo",
                platform_type=PlatformType.MICROBLOGGING,
                geographic_scope=GeographicScope.NATIONAL,
                primary_regions=["India"],
                content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO],
                max_content_length=400,
                supports_hashtags=True,
                supports_mentions=True,
                supports_reposting=True,
                api_available=True,
                rate_limits={"posts": 200, "searches": 100},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "mention": r"@[\w]+",
                    "rekoo": r"Re-Koo",
                    "language": r"[\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+"
                },
                metadata_fields=["koo_id", "user_id", "timestamp", "language", "location", "engagement"],
                viral_indicators=["rekoo_count", "like_count", "comment_count", "share_count"]
            ),
            
            PlatformConfig(
                platform_id="sharechat",
                name="ShareChat",
                platform_type=PlatformType.SOCIAL_NETWORK,
                geographic_scope=GeographicScope.NATIONAL,
                primary_regions=["India"],
                content_types=[ContentType.TEXT, ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO],
                max_content_length=1000,
                supports_hashtags=True,
                supports_mentions=True,
                supports_reposting=True,
                api_available=False,
                rate_limits={"posts": 150},
                content_patterns={
                    "hashtag": r"#[\w\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "mention": r"@[\w]+",
                    "language": r"[\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F]+",
                    "regional": r"(भारत|ভারত|இந்தியா|భారత్)"
                },
                metadata_fields=["post_id", "user_id", "timestamp", "language", "state", "engagement"],
                viral_indicators=["share_count", "like_count", "comment_count", "download_count"]
            )
        ]
        
        for platform in global_platforms:
            platforms[platform.platform_id] = platform
            
        return platforms
    
    def _initialize_extractors(self) -> Dict[str, Any]:
        """Initialize content extractors for each platform"""
        return {
            platform_id: self._create_content_extractor(config)
            for platform_id, config in self.platforms.items()
        }
    
    def _create_content_extractor(self, config: PlatformConfig) -> Dict[str, Any]:
        """Create content extractor for a platform"""
        return {
            "patterns": config.content_patterns,
            "metadata_fields": config.metadata_fields,
            "viral_indicators": config.viral_indicators,
            "content_types": [ct.value for ct in config.content_types]
        }
    
    def get_supported_platforms(self) -> Dict[str, Dict]:
        """Get list of all supported platforms"""
        return {
            platform_id: {
                "name": config.name,
                "type": config.platform_type.value,
                "scope": config.geographic_scope.value,
                "regions": config.primary_regions,
                "content_types": [ct.value for ct in config.content_types],
                "api_available": config.api_available,
                "supports_hashtags": config.supports_hashtags,
                "supports_mentions": config.supports_mentions,
                "supports_reposting": config.supports_reposting
            }
            for platform_id, config in self.platforms.items()
        }
    
    def get_indian_platforms(self) -> Dict[str, Dict]:
        """Get platforms popular in India"""
        indian_platforms = {}
        
        for platform_id, config in self.platforms.items():
            if ("India" in config.primary_regions or 
                config.geographic_scope == GeographicScope.GLOBAL or
                platform_id in ["koo", "sharechat"]):
                indian_platforms[platform_id] = {
                    "name": config.name,
                    "type": config.platform_type.value,
                    "indian_specific": "India" in config.primary_regions,
                    "content_types": [ct.value for ct in config.content_types],
                    "supports_indian_languages": self._supports_indian_languages(config)
                }
        
        return indian_platforms
    
    def _supports_indian_languages(self, config: PlatformConfig) -> bool:
        """Check if platform supports Indian languages"""
        indian_script_patterns = [
            r"[\u0900-\u097F]",  # Devanagari
            r"[\u0980-\u09FF]",  # Bengali
            r"[\u0B80-\u0BFF]",  # Tamil
            r"[\u0C00-\u0C7F]"   # Telugu
        ]
        
        for pattern_name, pattern in config.content_patterns.items():
            for indian_pattern in indian_script_patterns:
                if indian_pattern in pattern:
                    return True
        
        return False
    
    def extract_content_metadata(self, platform_id: str, content: str, raw_metadata: Dict = None) -> Dict:
        """Extract metadata from content for specific platform"""
        if platform_id not in self.platforms:
            logger.error(f"Unsupported platform: {platform_id}")
            return {}
        
        config = self.platforms[platform_id]
        extractor = self.content_extractors[platform_id]
        
        extracted_metadata = {
            "platform": platform_id,
            "platform_name": config.name,
            "content_length": len(content),
            "timestamp": datetime.now().isoformat(),
            "extracted_elements": {},
            "viral_potential": self._calculate_viral_potential(platform_id, content, raw_metadata or {}),
            "content_classification": self._classify_platform_content(platform_id, content)
        }
        
        # Extract platform-specific elements
        for element_type, pattern in extractor["patterns"].items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.UNICODE)
            if matches:
                extracted_metadata["extracted_elements"][element_type] = {
                    "count": len(matches),
                    "items": matches[:10]  # Limit to first 10 matches
                }
        
        # Add raw metadata if provided
        if raw_metadata:
            extracted_metadata["raw_metadata"] = raw_metadata
            
            # Extract viral indicators from raw metadata
            viral_data = {}
            for indicator in extractor["viral_indicators"]:
                if indicator in raw_metadata:
                    viral_data[indicator] = raw_metadata[indicator]
            
            if viral_data:
                extracted_metadata["viral_metrics"] = viral_data
        
        return extracted_metadata
    
    def _calculate_viral_potential(self, platform_id: str, content: str, metadata: Dict) -> Dict:
        """Calculate viral potential based on platform-specific factors"""
        config = self.platforms[platform_id]
        
        potential_score = 0.0
        factors = {}
        
        # Content length factor
        optimal_length = config.max_content_length * 0.7  # 70% of max is often optimal
        length_factor = min(1.0, len(content) / optimal_length) if optimal_length > 0 else 0.5
        factors["length_factor"] = length_factor
        potential_score += length_factor * 0.2
        
        # Hashtag factor (if supported)
        if config.supports_hashtags:
            hashtag_pattern = config.content_patterns.get("hashtag", "")
            if hashtag_pattern:
                hashtags = re.findall(hashtag_pattern, content)
                hashtag_factor = min(1.0, len(hashtags) / 5)  # Optimal: 3-5 hashtags
                factors["hashtag_factor"] = hashtag_factor
                potential_score += hashtag_factor * 0.3
        
        # Mention factor (if supported)
        if config.supports_mentions:
            mention_pattern = config.content_patterns.get("mention", "")
            if mention_pattern:
                mentions = re.findall(mention_pattern, content)
                mention_factor = min(1.0, len(mentions) / 3)  # Optimal: 1-3 mentions
                factors["mention_factor"] = mention_factor
                potential_score += mention_factor * 0.2
        
        return {
            "score": min(1.0, potential_score),
            "factors": factors,
            "classification": self._classify_viral_potential(potential_score)
        }
    
    def _classify_viral_potential(self, score: float) -> str:
        """Classify viral potential based on score"""
        if score >= 0.8:
            return "very_high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "very_low"
    
    def _classify_platform_content(self, platform_id: str, content: str) -> str:
        """Classify content type based on platform and content"""
        config = self.platforms[platform_id]
        content_lower = content.lower()
        
        # Platform-specific classification
        if config.platform_type == PlatformType.MICROBLOGGING:
            if any(word in content_lower for word in ["breaking", "urgent", "alert"]):
                return "news_update"
            elif any(word in content_lower for word in ["opinion", "think", "believe"]):
                return "opinion"
            else:
                return "general_post"
        
        elif config.platform_type == PlatformType.MEDIA_SHARING:
            if any(word in content_lower for word in ["tutorial", "how to", "guide"]):
                return "educational"
            elif any(word in content_lower for word in ["funny", "lol", "haha"]):
                return "entertainment"
            else:
                return "media_content"
        
        return "general"
    
    def analyze_cross_platform_spread(self, content_items: List[Dict]) -> Dict:
        """Analyze how content spreads across multiple platforms"""
        if not content_items:
            return {}
        
        platform_distribution = {}
        content_timeline = []
        viral_metrics = {}
        
        for item in content_items:
            platform = item.get("platform", "unknown")
            timestamp = item.get("timestamp", "")
            
            # Platform distribution
            if platform not in platform_distribution:
                platform_distribution[platform] = {
                    "count": 0,
                    "total_engagement": 0,
                    "avg_viral_score": 0
                }
            
            platform_distribution[platform]["count"] += 1
            
            # Viral metrics
            if "viral_metrics" in item:
                for metric, value in item["viral_metrics"].items():
                    if metric not in viral_metrics:
                        viral_metrics[metric] = {"total": 0, "platforms": set()}
                    viral_metrics[metric]["total"] += value
                    viral_metrics[metric]["platforms"].add(platform)
            
            # Timeline
            content_timeline.append({
                "platform": platform,
                "timestamp": timestamp,
                "viral_score": item.get("viral_potential", {}).get("score", 0)
            })
        
        # Sort timeline
        content_timeline.sort(key=lambda x: x["timestamp"])
        
        # Calculate cross-platform metrics
        total_platforms = len(platform_distribution)
        primary_platform = max(platform_distribution.items(), key=lambda x: x[1]["count"])[0] if platform_distribution else "unknown"
        
        analysis = {
            "total_platforms": total_platforms,
            "primary_platform": primary_platform,
            "platform_distribution": platform_distribution,
            "content_timeline": content_timeline,
            "viral_metrics_summary": {
                metric: {
                    "total": data["total"],
                    "platform_count": len(data["platforms"]),
                    "platforms": list(data["platforms"])
                }
                for metric, data in viral_metrics.items()
            },
            "cross_platform_score": self._calculate_cross_platform_score(platform_distribution, total_platforms),
            "spread_pattern": self._analyze_spread_pattern(content_timeline)
        }
        
        return analysis
    
    def _calculate_cross_platform_score(self, distribution: Dict, total_platforms: int) -> float:
        """Calculate cross-platform viral score"""
        if total_platforms <= 1:
            return 0.0
        
        # Base score from platform diversity
        diversity_score = min(1.0, total_platforms / 10)  # Max score at 10+ platforms
        
        # Engagement distribution score
        total_engagement = sum(data["count"] for data in distribution.values())
        if total_engagement > 0:
            # Calculate entropy for even distribution
            entropy = 0
            for data in distribution.values():
                p = data["count"] / total_engagement
                if p > 0:
                    entropy -= p * (p ** 0.5)  # Modified entropy calculation
            
            distribution_score = min(1.0, entropy)
        else:
            distribution_score = 0.0
        
        return (diversity_score * 0.6 + distribution_score * 0.4)
    
    def _analyze_spread_pattern(self, timeline: List[Dict]) -> str:
        """Analyze the pattern of content spread"""
        if len(timeline) < 2:
            return "single_platform"
        
        # Check if content appeared on multiple platforms simultaneously
        timestamps = [item["timestamp"] for item in timeline]
        unique_timestamps = set(timestamps)
        
        if len(unique_timestamps) == 1:
            return "simultaneous_spread"
        elif len(timeline) <= 3:
            return "limited_spread"
        else:
            # Analyze viral scores over time
            viral_scores = [item["viral_score"] for item in timeline]
            if len(viral_scores) >= 3:
                if viral_scores[-1] > viral_scores[0] * 2:
                    return "exponential_growth"
                elif viral_scores[-1] > viral_scores[0]:
                    return "steady_growth"
                else:
                    return "declining_spread"
            
            return "sequential_spread"

# Example usage
if __name__ == "__main__":
    platform_support = GlobalPlatformSupport()
    
    # Test platform support
    print(f"Total supported platforms: {len(platform_support.get_supported_platforms())}")
    print(f"Indian platforms: {len(platform_support.get_indian_platforms())}")
    
    # Test content extraction
    test_content = "Breaking news! #ViralContent spreading across social media @everyone please share #India"
    
    for platform_id in ["twitter", "facebook", "koo"]:
        if platform_id in platform_support.platforms:
            metadata = platform_support.extract_content_metadata(platform_id, test_content)
            print(f"\n{platform_id.upper()} Analysis:")
            print(f"Viral potential: {metadata.get('viral_potential', {}).get('score', 0):.2f}")
            print(f"Classification: {metadata.get('content_classification', 'unknown')}")
            print(f"Extracted elements: {list(metadata.get('extracted_elements', {}).keys())}")
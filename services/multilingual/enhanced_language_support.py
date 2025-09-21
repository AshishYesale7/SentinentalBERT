#!/usr/bin/env python3
"""
Enhanced Multilingual Support for InsideOut Platform
Supports Indian languages and global content analysis
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageFamily(Enum):
    """Language families supported"""
    INDO_ARYAN = "indo_aryan"
    DRAVIDIAN = "dravidian"
    SINO_TIBETAN = "sino_tibetan"
    GERMANIC = "germanic"
    ROMANCE = "romance"
    SEMITIC = "semitic"
    JAPONIC = "japonic"
    KOREANIC = "koreanic"

@dataclass
class LanguageConfig:
    """Configuration for each supported language"""
    code: str
    name: str
    native_name: str
    family: LanguageFamily
    script: str
    rtl: bool  # Right-to-left writing
    official_status: str  # official, regional, minority
    speakers_millions: float
    content_detection_patterns: List[str]
    ui_translations: Dict[str, str]

class EnhancedLanguageSupport:
    """Enhanced multilingual support system"""
    
    def __init__(self):
        self.languages = self._initialize_languages()
        
    def _initialize_languages(self) -> Dict[str, LanguageConfig]:
        """Initialize supported languages"""
        languages = {}
        
        # Indian Languages (Constitutional Languages)
        indian_languages = [
            # Indo-Aryan Languages
            LanguageConfig("hi", "Hindi", "हिन्दी", LanguageFamily.INDO_ARYAN, "Devanagari", False, "official", 600.0,
                          [r'[\u0900-\u097F]', r'(है|हैं|का|की|के|में|से|को|पर|और|या|भी)'],
                          self._get_hindi_translations()),
            
            LanguageConfig("bn", "Bengali", "বাংলা", LanguageFamily.INDO_ARYAN, "Bengali", False, "official", 300.0,
                          [r'[\u0980-\u09FF]', r'(আছে|আর|এর|এবং|কিন্তু|যে|যা|হয়|করে)'],
                          self._get_bengali_translations()),
            
            LanguageConfig("ta", "Tamil", "தமிழ்", LanguageFamily.DRAVIDIAN, "Tamil", False, "official", 80.0,
                          [r'[\u0B80-\u0BFF]', r'(இருக்கிறது|இருக்கின்றன|ன்|ல்|க்கு|ஆக|உடன்|மற்றும்)'],
                          self._get_tamil_translations()),
            
            LanguageConfig("te", "Telugu", "తెలుగు", LanguageFamily.DRAVIDIAN, "Telugu", False, "official", 95.0,
                          [r'[\u0C00-\u0C7F]', r'(ఉంది|ఉన్నాయి|యొక్క|లో|కు|కోసం|తో|మరియు)'],
                          self._get_telugu_translations()),
            
            LanguageConfig("en", "English", "English", LanguageFamily.GERMANIC, "Latin", False, "global", 1500.0,
                          [r'[a-zA-Z]', r'(is|are|the|and|or|but|in|on|at|to|for|with)'],
                          self._get_english_translations()),
        ]
        
        for lang in indian_languages:
            languages[lang.code] = lang
            
        return languages
    
    def detect_language(self, text: str) -> List[Tuple[str, float]]:
        """Detect language(s) in text with confidence scores"""
        if not text.strip():
            return []
        
        language_scores = {}
        
        for lang_code, lang_config in self.languages.items():
            score = 0.0
            text_length = len(text)
            
            # Check script patterns
            for pattern in lang_config.content_detection_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Calculate score based on character coverage
                    matched_chars = sum(len(match) for match in matches)
                    script_score = min(1.0, matched_chars / text_length)
                    score = max(score, script_score)
            
            if score > 0.1:  # Minimum threshold
                language_scores[lang_code] = score
        
        # Sort by confidence score
        sorted_languages = sorted(language_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_languages[:3]  # Return top 3 matches
    
    def get_ui_translation(self, lang_code: str, key: str) -> str:
        """Get UI translation for specific language"""
        if lang_code in self.languages and key in self.languages[lang_code].ui_translations:
            return self.languages[lang_code].ui_translations[key]
        
        # Fallback to English
        if key in self.languages.get('en', LanguageConfig('en', '', '', LanguageFamily.GERMANIC, '', False, '', 0, [], {})).ui_translations:
            return self.languages['en'].ui_translations[key]
        
        return key  # Return key if no translation found
    
    def get_supported_languages(self) -> Dict[str, Dict]:
        """Get list of all supported languages"""
        return {
            code: {
                "name": lang.name,
                "native_name": lang.native_name,
                "family": lang.family.value,
                "script": lang.script,
                "rtl": lang.rtl,
                "official_status": lang.official_status,
                "speakers_millions": lang.speakers_millions
            }
            for code, lang in self.languages.items()
        }
    
    def analyze_multilingual_content(self, content: str) -> Dict:
        """Analyze content for multiple languages"""
        detected_languages = self.detect_language(content)
        
        analysis = {
            "content_length": len(content),
            "detected_languages": detected_languages,
            "primary_language": detected_languages[0][0] if detected_languages else "unknown",
            "is_multilingual": len(detected_languages) > 1,
            "language_distribution": {},
            "script_analysis": self._analyze_scripts(content),
            "content_classification": self._classify_content_type(content)
        }
        
        # Calculate language distribution
        total_score = sum(score for _, score in detected_languages)
        if total_score > 0:
            for lang_code, score in detected_languages:
                analysis["language_distribution"][lang_code] = {
                    "percentage": (score / total_score) * 100,
                    "language_name": self.languages[lang_code].name,
                    "native_name": self.languages[lang_code].native_name
                }
        
        return analysis
    
    def _analyze_scripts(self, text: str) -> Dict:
        """Analyze scripts used in text"""
        script_patterns = {
            "Latin": r'[a-zA-Z]',
            "Devanagari": r'[\u0900-\u097F]',
            "Bengali": r'[\u0980-\u09FF]',
            "Tamil": r'[\u0B80-\u0BFF]',
            "Telugu": r'[\u0C00-\u0C7F]',
        }
        
        script_analysis = {}
        text_length = len(text)
        
        for script_name, pattern in script_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                char_count = len(matches)
                percentage = (char_count / text_length) * 100
                script_analysis[script_name] = {
                    "character_count": char_count,
                    "percentage": percentage
                }
        
        return script_analysis
    
    def _classify_content_type(self, content: str) -> str:
        """Classify type of content"""
        content_lower = content.lower()
        
        # Social media indicators
        if any(indicator in content_lower for indicator in ['#', '@', 'rt ', 'retweet', 'share', 'like']):
            return "social_media"
        
        # News indicators
        if any(indicator in content_lower for indicator in ['breaking', 'news', 'report', 'according to']):
            return "news"
        
        return "general"
    
    # UI Translation Methods
    def _get_hindi_translations(self) -> Dict[str, str]:
        return {
            "dashboard_title": "इनसाइडआउट - वायरल सामग्री विश्लेषण प्लेटफॉर्म",
            "government_text": "भारत सरकार",
            "active_clusters": "सक्रिय वायरल क्लस्टर",
            "evidence_packages": "साक्ष्य पैकेज",
            "high_priority": "उच्च प्राथमिकता मामले",
            "officers_active": "सक्रिय अधिकारी",
            "viral_timeline": "वायरल सामग्री समयरेखा",
            "influence_network": "प्रभाव नेटवर्क विश्लेषण",
            "geographic_spread": "भौगोलिक प्रसार",
            "evidence_collection": "साक्ष्य संग्रह स्थिति",
            "collect_evidence": "साक्ष्य एकत्रित करें",
            "view_details": "विवरण देखें",
            "original_source": "मूल स्रोत",
            "viral_score": "वायरल स्कोर",
            "propagation_chain": "प्रसार श्रृंखला",
            "platform_filter": "प्लेटफॉर्म फिल्टर",
            "time_range": "समय सीमा",
            "location_filter": "स्थान फिल्टर",
            "search_placeholder": "वायरल सामग्री खोजने के लिए कीवर्ड दर्ज करें..."
        }
    
    def _get_bengali_translations(self) -> Dict[str, str]:
        return {
            "dashboard_title": "ইনসাইডআউট - ভাইরাল কন্টেন্ট বিশ্লেষণ প্ল্যাটফর্ম",
            "government_text": "ভারত সরকার",
            "active_clusters": "সক্রিয় ভাইরাল ক্লাস্টার",
            "evidence_packages": "প্রমাণ প্যাকেজ",
            "high_priority": "উচ্চ অগ্রাধিকার মামলা",
            "officers_active": "সক্রিয় কর্মকর্তা"
        }
    
    def _get_tamil_translations(self) -> Dict[str, str]:
        return {
            "dashboard_title": "இன்சைட்அவுட் - வைரல் உள்ளடக்க பகுப்பாய்வு தளம்",
            "government_text": "இந்திய அரசு",
            "active_clusters": "செயலில் உள்ள வைரல் கிளஸ்டர்கள்",
            "evidence_packages": "சாக்ஷி தொகுப்புகள்",
            "high_priority": "அதிக முன்னுரிமை வழக்குகள்",
            "officers_active": "செயலில் உள்ள அதிகாரிகள்"
        }
    
    def _get_telugu_translations(self) -> Dict[str, str]:
        return {
            "dashboard_title": "ఇన్‌సైడ్‌అవుట్ - వైరల్ కంటెంట్ విశ్లేషణ ప్లాట్‌ఫారమ్",
            "government_text": "భారత ప్రభుత్వం",
            "active_clusters": "క్రియాశీల వైరల్ క్లస్టర్లు",
            "evidence_packages": "సాక్ష్య ప్యాకేజీలు",
            "high_priority": "అధిక ప్రాధాన్యత కేసులు",
            "officers_active": "క్రియాశీల అధికారులు"
        }
    
    def _get_english_translations(self) -> Dict[str, str]:
        return {
            "dashboard_title": "InsideOut - Viral Content Analysis Platform",
            "government_text": "Government of India",
            "active_clusters": "Active Viral Clusters",
            "evidence_packages": "Evidence Packages",
            "high_priority": "High Priority Cases",
            "officers_active": "Officers Active",
            "viral_timeline": "Viral Content Timeline",
            "influence_network": "Influence Network Analysis",
            "geographic_spread": "Geographic Spread",
            "evidence_collection": "Evidence Collection Status",
            "collect_evidence": "Collect Evidence",
            "view_details": "View Details",
            "original_source": "Original Source",
            "viral_score": "Viral Score",
            "propagation_chain": "Propagation Chain",
            "platform_filter": "Platform Filter",
            "time_range": "Time Range",
            "location_filter": "Location Filter",
            "search_placeholder": "Enter keywords to search viral content..."
        }

# Example usage
if __name__ == "__main__":
    lang_support = EnhancedLanguageSupport()
    
    # Test language detection
    test_texts = [
        "यह एक हिंदी वाक्य है।",
        "এটি একটি বাংলা বাক্য।",
        "இது ஒரு தமிழ் வாக்கியம்.",
        "This is an English sentence."
    ]
    
    for text in test_texts:
        detected = lang_support.detect_language(text)
        print(f"Text: {text}")
        print(f"Detected: {detected}")
        print("-" * 50)
    
    print(f"Total supported languages: {len(lang_support.get_supported_languages())}")
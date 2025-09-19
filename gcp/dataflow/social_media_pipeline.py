"""
Apache Beam pipeline for processing social media data
Reads from Pub/Sub, processes data, and writes to BigQuery
"""

import argparse
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io import ReadFromPubSub, WriteToBigQuery
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms import window

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParsePubSubMessage(beam.DoFn):
    """Parse Pub/Sub messages and extract social media data"""
    
    def process(self, element):
        try:
            # Parse the JSON message
            data = json.loads(element.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['post_id', 'platform', 'content', 'created_at']
            if not all(field in data for field in required_fields):
                logger.warning(f"Missing required fields in message: {data}")
                return
            
            # Add processing timestamp
            data['processed_at'] = datetime.utcnow().isoformat()
            
            yield data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

class CleanAndValidateData(beam.DoFn):
    """Clean and validate social media data"""
    
    def __init__(self):
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def process(self, element):
        try:
            # Clean content text
            content = element.get('content', '')
            if content:
                # Remove excessive whitespace
                content = re.sub(r'\s+', ' ', content).strip()
                element['content'] = content
                
                # Extract additional metadata
                element['content_length'] = len(content)
                element['word_count'] = len(content.split())
                element['has_urls'] = bool(self.url_pattern.search(content))
                element['url_count'] = len(self.url_pattern.findall(content))
            
            # Validate and clean author information
            if 'author_info' in element and element['author_info']:
                author = element['author_info']
                element['author_username'] = author.get('username', '').lower()
                element['author_display_name'] = author.get('display_name', '')
                element['author_followers_count'] = max(0, author.get('followers_count', 0))
                element['author_verified'] = bool(author.get('verified', False))
            
            # Validate engagement metrics
            if 'engagement_metrics' in element:
                metrics = element['engagement_metrics']
                for key in ['likes', 'shares', 'comments', 'views']:
                    if key in metrics:
                        metrics[key] = max(0, int(metrics.get(key, 0)))
            
            # Clean and validate location data
            if 'location' in element and element['location']:
                location = element['location']
                if 'coordinates' in location:
                    coords = location['coordinates']
                    if isinstance(coords, dict) and 'lat' in coords and 'lng' in coords:
                        try:
                            lat = float(coords['lat'])
                            lng = float(coords['lng'])
                            if -90 <= lat <= 90 and -180 <= lng <= 180:
                                element['location']['coordinates'] = {'lat': lat, 'lng': lng}
                            else:
                                element['location']['coordinates'] = None
                        except (ValueError, TypeError):
                            element['location']['coordinates'] = None
            
            # Validate timestamps
            for timestamp_field in ['created_at', 'ingested_at', 'processed_at']:
                if timestamp_field in element:
                    try:
                        # Ensure timestamp is in ISO format
                        if isinstance(element[timestamp_field], str):
                            datetime.fromisoformat(element[timestamp_field].replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"Invalid timestamp format for {timestamp_field}: {element[timestamp_field]}")
                        element[timestamp_field] = datetime.utcnow().isoformat()
            
            # Set processing status
            element['processing_status'] = 'cleaned'
            
            yield element
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            # Yield with error status for monitoring
            element['processing_status'] = 'error'
            element['error_message'] = str(e)
            yield element

class DeduplicateData(beam.DoFn):
    """Remove duplicate posts based on post_id and platform"""
    
    def __init__(self):
        self.seen_posts = set()
    
    def process(self, element):
        try:
            post_key = f"{element['platform']}:{element['post_id']}"
            
            if post_key not in self.seen_posts:
                self.seen_posts.add(post_key)
                element['is_duplicate'] = False
                yield element
            else:
                logger.info(f"Duplicate post detected: {post_key}")
                element['is_duplicate'] = True
                element['processing_status'] = 'duplicate'
                # Still yield for monitoring purposes
                yield element
                
        except Exception as e:
            logger.error(f"Error in deduplication: {e}")
            element['processing_status'] = 'error'
            element['error_message'] = str(e)
            yield element

class EnrichWithMetadata(beam.DoFn):
    """Enrich data with additional metadata and classifications"""
    
    def __init__(self):
        # Language detection patterns (simplified)
        self.language_patterns = {
            'en': re.compile(r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b', re.IGNORECASE),
            'es': re.compile(r'\b(el|la|los|las|y|o|pero|en|con|de|por|para)\b', re.IGNORECASE),
            'fr': re.compile(r'\b(le|la|les|et|ou|mais|dans|avec|de|par|pour)\b', re.IGNORECASE),
        }
        
        # Content type classification
        self.news_keywords = ['breaking', 'news', 'report', 'update', 'alert', 'announced']
        self.opinion_keywords = ['think', 'believe', 'opinion', 'feel', 'personally']
        
    def detect_language(self, text: str) -> str:
        """Simple language detection based on common words"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        scores = {}
        
        for lang, pattern in self.language_patterns.items():
            matches = len(pattern.findall(text_lower))
            scores[lang] = matches
        
        if scores:
            detected_lang = max(scores, key=scores.get)
            if scores[detected_lang] > 0:
                return detected_lang
        
        return 'unknown'
    
    def classify_content_type(self, content: str) -> str:
        """Classify content type based on keywords and patterns"""
        if not content:
            return 'unknown'
        
        content_lower = content.lower()
        
        # Check for news content
        if any(keyword in content_lower for keyword in self.news_keywords):
            return 'news'
        
        # Check for opinion content
        if any(keyword in content_lower for keyword in self.opinion_keywords):
            return 'opinion'
        
        # Check for questions
        if '?' in content:
            return 'question'
        
        # Default to general
        return 'general'
    
    def process(self, element):
        try:
            content = element.get('content', '')
            
            # Detect language if not provided or uncertain
            if not element.get('language') or element.get('language') == 'unknown':
                element['language'] = self.detect_language(content)
            
            # Classify content type
            element['content_classification'] = self.classify_content_type(content)
            
            # Calculate engagement rate
            if 'engagement_metrics' in element and 'author_followers_count' in element:
                metrics = element['engagement_metrics']
                followers = element.get('author_followers_count', 0)
                
                if followers > 0:
                    total_engagement = sum([
                        metrics.get('likes', 0),
                        metrics.get('shares', 0),
                        metrics.get('comments', 0)
                    ])
                    element['engagement_rate'] = total_engagement / followers
                else:
                    element['engagement_rate'] = 0.0
            
            # Add processing metadata
            element['enrichment_timestamp'] = datetime.utcnow().isoformat()
            element['processing_status'] = 'enriched'
            
            yield element
            
        except Exception as e:
            logger.error(f"Error enriching data: {e}")
            element['processing_status'] = 'error'
            element['error_message'] = str(e)
            yield element

class FormatForBigQuery(beam.DoFn):
    """Format data for BigQuery insertion"""
    
    def process(self, element):
        try:
            # Create BigQuery row
            row = {
                'post_id': element['post_id'],
                'platform': element['platform'],
                'author_id': element.get('author_id', ''),
                'author_username': element.get('author_username', ''),
                'author_display_name': element.get('author_display_name', ''),
                'author_followers_count': element.get('author_followers_count', 0),
                'author_verified': element.get('author_verified', False),
                'content': element.get('content', ''),
                'content_type': element.get('content_classification', 'general'),
                'language': element.get('language', 'unknown'),
                'created_at': element.get('created_at'),
                'ingested_at': element.get('ingested_at'),
                'url': element.get('url', ''),
                'engagement_metrics': {
                    'likes': element.get('engagement_metrics', {}).get('likes', 0),
                    'shares': element.get('engagement_metrics', {}).get('shares', 0),
                    'comments': element.get('engagement_metrics', {}).get('comments', 0),
                    'views': element.get('engagement_metrics', {}).get('views', 0)
                },
                'location': element.get('location', {}),
                'hashtags': element.get('hashtags', []),
                'mentions': element.get('mentions', []),
                'media_urls': element.get('media_urls', []),
                'parent_post_id': element.get('parent_post_id'),
                'is_retweet': element.get('is_retweet', False),
                'is_reply': element.get('is_reply', False),
                'raw_data': element.get('raw_data', {}),
                'processing_status': element.get('processing_status', 'processed')
            }
            
            yield row
            
        except Exception as e:
            logger.error(f"Error formatting for BigQuery: {e}")

def run_pipeline(argv=None):
    """Run the social media processing pipeline"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_subscription',
        required=True,
        help='Pub/Sub subscription to read from'
    )
    parser.add_argument(
        '--output_table',
        required=True,
        help='BigQuery table to write to (project:dataset.table)'
    )
    parser.add_argument(
        '--window_size',
        type=int,
        default=60,
        help='Window size in seconds for processing'
    )
    
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    # Pipeline options
    pipeline_options = PipelineOptions(pipeline_args)
    
    # BigQuery schema
    table_schema = {
        'fields': [
            {'name': 'post_id', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'platform', 'type': 'STRING', 'mode': 'REQUIRED'},
            {'name': 'author_id', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'author_username', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'author_display_name', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'author_followers_count', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'author_verified', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
            {'name': 'content', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'content_type', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'language', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'created_at', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
            {'name': 'ingested_at', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
            {'name': 'url', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'engagement_metrics', 'type': 'RECORD', 'mode': 'NULLABLE', 'fields': [
                {'name': 'likes', 'type': 'INTEGER', 'mode': 'NULLABLE'},
                {'name': 'shares', 'type': 'INTEGER', 'mode': 'NULLABLE'},
                {'name': 'comments', 'type': 'INTEGER', 'mode': 'NULLABLE'},
                {'name': 'views', 'type': 'INTEGER', 'mode': 'NULLABLE'}
            ]},
            {'name': 'location', 'type': 'JSON', 'mode': 'NULLABLE'},
            {'name': 'hashtags', 'type': 'STRING', 'mode': 'REPEATED'},
            {'name': 'mentions', 'type': 'STRING', 'mode': 'REPEATED'},
            {'name': 'media_urls', 'type': 'STRING', 'mode': 'REPEATED'},
            {'name': 'parent_post_id', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'is_retweet', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
            {'name': 'is_reply', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
            {'name': 'raw_data', 'type': 'JSON', 'mode': 'NULLABLE'},
            {'name': 'processing_status', 'type': 'STRING', 'mode': 'NULLABLE'}
        ]
    }
    
    with beam.Pipeline(options=pipeline_options) as pipeline:
        
        # Read from Pub/Sub
        messages = (
            pipeline
            | 'Read from Pub/Sub' >> ReadFromPubSub(
                subscription=known_args.input_subscription,
                with_attributes=False
            )
        )
        
        # Process messages
        processed_data = (
            messages
            | 'Parse Messages' >> beam.ParDo(ParsePubSubMessage())
            | 'Window into Fixed Intervals' >> beam.WindowInto(
                FixedWindows(known_args.window_size)
            )
            | 'Clean and Validate' >> beam.ParDo(CleanAndValidateData())
            | 'Deduplicate' >> beam.ParDo(DeduplicateData())
            | 'Enrich with Metadata' >> beam.ParDo(EnrichWithMetadata())
        )
        
        # Filter out duplicates and errors for main table
        clean_data = (
            processed_data
            | 'Filter Clean Data' >> beam.Filter(
                lambda x: x.get('processing_status') not in ['duplicate', 'error']
            )
            | 'Format for BigQuery' >> beam.ParDo(FormatForBigQuery())
        )
        
        # Write to BigQuery
        clean_data | 'Write to BigQuery' >> WriteToBigQuery(
            table=known_args.output_table,
            schema=table_schema,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )
        
        # Handle errors and duplicates (optional: write to separate table or dead letter queue)
        error_data = (
            processed_data
            | 'Filter Error Data' >> beam.Filter(
                lambda x: x.get('processing_status') in ['duplicate', 'error']
            )
            | 'Log Errors' >> beam.Map(
                lambda x: logger.warning(f"Processing issue: {x.get('processing_status')} - {x.get('post_id')}")
            )
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run_pipeline()
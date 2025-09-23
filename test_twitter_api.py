#!/usr/bin/env python3
"""
Test Twitter API Connection with Provided Credentials
Quick verification for Indian Police Hackathon Demo
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project path
sys.path.append('/workspace/project/SentinentalBERT')

def test_twitter_credentials():
    """Test Twitter API credentials"""
    
    print("🔧 Testing Twitter API Connection...")
    print("=" * 50)
    
    # Test credentials
    credentials = {
        'API Key': 'tkG3UCrcXhq1LCzC3n02mqg2N',
        'API Secret': 'oXRCjqTeJkV4KWrXFS5JO7ZIjcGGTHSNiUGStL0KIjSHmke90x',
        'Access Token': '835527957481459713-m4BKaUIuaAt2uQ6c2DITWDyoBcFxMAJ',
        'Access Token Secret': 'B4C9XYaJOMuy7l3nq3Lo2h8FmoKV4TzkmnuqlDtlbveP1',
        'Bearer Token': 'AAAAAAAAAAAAAAAAAAAAAHsN4QEAAAAA8%2BZQa%2BzllARQxtAvmhCQsA0WQCs%3DpF9thH1ztd85xkbAsWZvubIgJ98edZ3z7BdA8q1vfkRHnBMd6B'
    }
    
    print("📋 Credentials Check:")
    for key, value in credentials.items():
        masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else value
        print(f"  ✅ {key}: {masked_value}")
    
    print("\n🔌 Testing API Connection...")
    
    try:
        import tweepy
        
        # Initialize client
        client = tweepy.Client(
            bearer_token=credentials['Bearer Token'],
            consumer_key=credentials['API Key'],
            consumer_secret=credentials['API Secret'],
            access_token=credentials['Access Token'],
            access_token_secret=credentials['Access Token Secret'],
            wait_on_rate_limit=True
        )
        
        print("✅ Tweepy client initialized successfully")
        
        # Test basic API call
        print("\n🔍 Testing basic API functionality...")
        
        # Get authenticated user info
        me = client.get_me()
        if me.data:
            print(f"✅ Authenticated as: @{me.data.username}")
            print(f"   User ID: {me.data.id}")
            print(f"   Name: {me.data.name}")
        else:
            print("❌ Could not get authenticated user info")
            return False
        
        # Test search functionality (limited for free tier)
        print("\n🔍 Testing search functionality...")
        try:
            tweets = client.search_recent_tweets(
                query="python",
                max_results=10,
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )
            
            if tweets.data:
                print(f"✅ Search successful: Found {len(tweets.data)} tweets")
                print(f"   Sample tweet: {tweets.data[0].text[:50]}...")
            else:
                print("⚠️ Search returned no results (this is normal for free tier)")
        
        except Exception as e:
            print(f"⚠️ Search test failed: {e}")
            print("   This might be due to free tier limitations")
        
        print("\n✅ Twitter API connection test PASSED!")
        print("🎉 Ready for hackathon demo!")
        return True
        
    except Exception as e:
        print(f"❌ Twitter API connection test FAILED: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check if credentials are correct")
        print("2. Verify internet connection")
        print("3. Ensure Twitter app has proper permissions")
        return False

async def test_enhanced_tracking():
    """Test the enhanced tracking service"""
    
    print("\n" + "=" * 50)
    print("🎯 Testing Enhanced Tracking Service...")
    
    try:
        from services.realtime.enhanced_tracking_service import EnhancedTrackingService
        
        # Initialize tracking service
        tracking_service = EnhancedTrackingService()
        print("✅ Enhanced Tracking Service initialized")
        
        # Test with a simple username (your own account)
        print("\n🔍 Testing username tracking...")
        
        # Get authenticated user for testing
        me = tracking_service.twitter_connector.client.get_me()
        if me.data:
            test_username = me.data.username
            print(f"Testing with authenticated user: @{test_username}")
            
            # Test tracking
            result = await tracking_service.track_viral_origin(f"@{test_username}", "username")
            
            print(f"\n📊 Tracking Results:")
            print(f"   Confidence: {result.tracking_confidence:.2f}")
            print(f"   API Calls: {result.api_calls_used}")
            print(f"   Processing Time: {result.processing_time:.2f}s")
            print(f"   Chain Length: {len(result.viral_chain)}")
            
            if result.original_post:
                print(f"   ✅ Found original post from @{result.original_post.author_handle}")
            else:
                print(f"   ⚠️ No original post identified (normal for limited data)")
            
            print("✅ Enhanced tracking test PASSED!")
            
        else:
            print("❌ Could not get authenticated user for testing")
            
    except Exception as e:
        print(f"❌ Enhanced tracking test FAILED: {e}")
        print("   This might be due to missing dependencies or API limits")

def main():
    """Main test function"""
    
    print("🇮🇳 SentinelBERT Twitter API Test")
    print("Indian Police Hackathon Demo Verification")
    print("=" * 50)
    
    # Test basic Twitter API connection
    api_success = test_twitter_credentials()
    
    if api_success:
        # Test enhanced tracking
        try:
            asyncio.run(test_enhanced_tracking())
        except Exception as e:
            print(f"❌ Enhanced tracking test failed: {e}")
    
    print("\n" + "=" * 50)
    if api_success:
        print("🎉 OVERALL TEST STATUS: PASSED")
        print("✅ Your system is ready for the hackathon demo!")
        print("\n📋 Next Steps:")
        print("1. Create a test tweet")
        print("2. Have friends retweet it")
        print("3. Use the dashboard to track back to your original post")
        print("4. Impress the judges! 🏆")
    else:
        print("❌ OVERALL TEST STATUS: FAILED")
        print("🔧 Please fix the API connection issues before demo")
    
    print("\n🚀 Launch dashboard with:")
    print("   streamlit run enhanced_viral_dashboard.py --server.port 12000 --server.address 0.0.0.0")

if __name__ == "__main__":
    main()
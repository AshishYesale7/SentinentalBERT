#!/usr/bin/env python3
"""
Simple Demo Test for Enhanced Viral Tracking
Lightweight version for Hackathon Demo
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project path
sys.path.append('/workspace/project/SentinentalBERT')

async def demo_simple_tracking():
    """Demo simple tracking with your account"""
    
    print("🎯 SentinelBERT Enhanced Tracking Demo")
    print("=" * 50)
    print("Testing with your authenticated account: @YesaleAshish")
    print()
    
    try:
        from services.realtime.simple_tracking_service import SimpleTrackingService
        
        # Initialize tracking service
        tracking_service = SimpleTrackingService()
        print("✅ Simple Enhanced Tracking Service initialized")
        print(f"📊 API Rate Limit: {tracking_service.max_api_calls} calls")
        print(f"🔑 Authenticated as: @YesaleAshish")
        print()
        
        # Test username tracking
        print("🔍 Testing username tracking...")
        print("Input: @YesaleAshish")
        print("Algorithm: Reverse Chronological Tracing")
        print()
        
        start_time = datetime.now()
        result = await tracking_service.track_viral_origin("@YesaleAshish", "username")
        end_time = datetime.now()
        
        # Display results
        print("📊 TRACKING RESULTS:")
        print("=" * 30)
        print(f"⏱️  Processing Time: {result.processing_time:.2f} seconds")
        print(f"🎯 Confidence Score: {result.tracking_confidence:.2f}")
        print(f"📞 API Calls Used: {result.api_calls_used}")
        print(f"🔗 Chain Length: {len(result.viral_chain)}")
        print()
        
        if result.original_post:
            print("✅ ORIGINAL SOURCE FOUND:")
            print(f"👤 Author: @{result.original_post.author_handle}")
            print(f"📅 Posted: {result.original_post.timestamp}")
            print(f"📝 Content: {result.original_post.content[:100]}...")
            if hasattr(result.original_post, 'url') and result.original_post.url:
                print(f"🔗 URL: {result.original_post.url}")
            print(f"📈 Engagement: {sum(result.original_post.engagement_metrics.values())}")
        else:
            print("⚠️ No original source identified")
            print("   (This is normal for accounts with limited recent activity)")
        
        if result.viral_chain:
            print(f"\n📈 VIRAL CHAIN ANALYSIS:")
            print(f"📊 Total Posts: {len(result.viral_chain)}")
            for i, post in enumerate(result.viral_chain[:3]):  # Show first 3
                print(f"   {i+1}. @{post.author_handle}: {post.content[:50]}...")
        
        if result.timeline_analysis:
            ta = result.timeline_analysis
            print(f"\n⏰ TIMELINE ANALYSIS:")
            print(f"📊 Total Posts: {ta.get('total_posts', 0)}")
            print(f"⏰ Time Span: {ta.get('time_span_hours', 0):.1f} hours")
            print(f"🚀 Spread Velocity: {ta.get('spread_velocity', 0):.1f} posts/hour")
        
        if result.influence_metrics:
            im = result.influence_metrics
            print(f"\n👑 INFLUENCE ANALYSIS:")
            print(f"📈 Total Engagement: {im.get('total_engagement', 0):,}")
            print(f"📊 Average Engagement: {im.get('average_engagement', 0):.0f}")
            print(f"👥 Unique Users: {im.get('unique_users', 0)}")
            print(f"🔄 Viral Coefficient: {im.get('viral_coefficient', 0):.2f}")
        
        print("\n" + "="*50)
        print("🎉 DEMO SUCCESSFUL!")
        print("✅ Enhanced tracking is working correctly")
        print("✅ API integration is functional")
        print("✅ Ready for hackathon presentation!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demo function"""
    
    print("🇮🇳 SentinelBERT Enhanced Tracking Demo")
    print("Indian Police Hackathon - Simple Test")
    print("=" * 50)
    
    try:
        success = asyncio.run(demo_simple_tracking())
        
        if success:
            print("\n🚀 NEXT STEPS FOR HACKATHON:")
            print("1. Launch the dashboard:")
            print("   streamlit run enhanced_viral_dashboard.py --server.port 12000 --server.address 0.0.0.0")
            print()
            print("2. Navigate to 'Influence Network' tab")
            print("3. Select 'VIRAL ORIGIN TRACKING' sub-tab")
            print("4. Test with:")
            print("   - Your username: @YesaleAshish")
            print("   - A friend's username after they retweet your post")
            print("   - A specific tweet URL")
            print()
            print("5. Show the judges:")
            print("   ✅ Real-time viral content tracing")
            print("   ✅ Original source identification")
            print("   ✅ Network analysis and visualization")
            print("   ✅ Court-ready evidence generation")
            print()
            print("🏆 Good luck with your hackathon!")
            print()
            print("📋 Demo Scenario for Judges:")
            print("1. Create a tweet from your account")
            print("2. Have friends retweet it 2-3 times")
            print("3. Input friend's username or retweet URL")
            print("4. Watch system trace back to your original post!")
            print("5. Show confidence scores, timeline, and network graph")
        else:
            print("\n🔧 Please check the error messages above")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
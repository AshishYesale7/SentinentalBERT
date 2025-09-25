#!/usr/bin/env python3
"""
Test script to check NLP service imports and identify issues
"""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a module and report results"""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except ImportError as e:
        print(f"❌ {description}: FAILED - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: ERROR - {e}")
        return False

def main():
    print("Testing NLP Service Dependencies...")
    print("=" * 50)
    
    # Test basic dependencies
    success_count = 0
    total_tests = 0
    
    tests = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("torch", "PyTorch"),
        ("transformers", "Hugging Face Transformers"),
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing"),
        ("nltk", "Natural Language Toolkit"),
        ("textblob", "Text processing"),
        ("langdetect", "Language detection"),
        ("redis", "Redis client"),
        ("psycopg2", "PostgreSQL adapter"),
        ("prometheus_client", "Metrics collection"),
    ]
    
    for module, desc in tests:
        total_tests += 1
        if test_import(module, desc):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Import Test Results: {success_count}/{total_tests} successful")
    
    if success_count == total_tests:
        print("✅ All dependencies are available!")
        
        # Test NLP service specific imports
        print("\nTesting NLP service specific imports...")
        try:
            sys.path.append('/workspace/project/SentinentalBERT/services/nlp')
            
            # Test individual service imports
            from models.sentiment_model import SentinelBERTModel
            print("✅ SentinelBERTModel: OK")
        except Exception as e:
            print(f"❌ SentinelBERTModel: FAILED - {e}")
            traceback.print_exc()
            
        try:
            from models.behavior_analyzer import BehavioralPatternAnalyzer
            print("✅ BehavioralPatternAnalyzer: OK")
        except Exception as e:
            print(f"❌ BehavioralPatternAnalyzer: FAILED - {e}")
            
        try:
            from models.influence_calculator import InfluenceCalculator
            print("✅ InfluenceCalculator: OK")
        except Exception as e:
            print(f"❌ InfluenceCalculator: FAILED - {e}")
            
        try:
            from services.model_manager import ModelManager
            print("✅ ModelManager: OK")
        except Exception as e:
            print(f"❌ ModelManager: FAILED - {e}")
            
        try:
            from services.cache_service import CacheService
            print("✅ CacheService: OK")
        except Exception as e:
            print(f"❌ CacheService: FAILED - {e}")
            
        try:
            from services.database import DatabaseService
            print("✅ DatabaseService: OK")
        except Exception as e:
            print(f"❌ DatabaseService: FAILED - {e}")
            
    else:
        print("❌ Some dependencies are missing. Install them first.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
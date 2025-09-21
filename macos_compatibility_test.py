#!/usr/bin/env python3
"""
macOS Compatibility Test for InsideOut Platform
Tests platform compatibility and deployment on macOS systems
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path

def test_macos_compatibility():
    """Test macOS compatibility"""
    print("🍎 Testing macOS Compatibility for InsideOut Platform")
    print("=" * 60)
    
    results = {
        "platform_info": {},
        "docker_compatibility": {},
        "python_compatibility": {},
        "dependency_issues": [],
        "deployment_issues": [],
        "recommendations": []
    }
    
    # Platform detection
    results["platform_info"] = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }
    
    print(f"System: {results['platform_info']['system']} {results['platform_info']['release']}")
    print(f"Architecture: {results['platform_info']['machine']}")
    print(f"Python: {results['platform_info']['python_version']}")
    print()
    
    # Test Docker compatibility
    print("🐳 Testing Docker Compatibility...")
    try:
        docker_version = subprocess.check_output(['docker', '--version'], text=True).strip()
        docker_compose_version = subprocess.check_output(['docker-compose', '--version'], text=True).strip()
        
        results["docker_compatibility"] = {
            "docker_available": True,
            "docker_version": docker_version,
            "docker_compose_version": docker_compose_version,
            "status": "✅ Docker available"
        }
        print(f"✅ {docker_version}")
        print(f"✅ {docker_compose_version}")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        results["docker_compatibility"] = {
            "docker_available": False,
            "status": "❌ Docker not available",
            "recommendation": "Install Docker Desktop for Mac"
        }
        print("❌ Docker not available")
        results["deployment_issues"].append("Docker not installed")
    
    print()
    
    # Test Python dependencies
    print("🐍 Testing Python Dependencies...")
    required_packages = [
        'torch', 'transformers', 'streamlit', 'plotly', 'pandas', 
        'numpy', 'scikit-learn', 'psycopg2-binary', 'redis', 
        'fastapi', 'uvicorn', 'cryptography', 'networkx'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    results["dependency_issues"] = missing_packages
    print()
    
    # Test file system permissions
    print("📁 Testing File System Permissions...")
    test_paths = [
        "/tmp/insideout_test",
        os.path.expanduser("~/insideout_test"),
        "./insideout_test"
    ]
    
    permission_issues = []
    for path in test_paths:
        try:
            os.makedirs(path, exist_ok=True)
            test_file = os.path.join(path, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            os.rmdir(path)
            print(f"✅ {path} - Writable")
        except Exception as e:
            print(f"❌ {path} - Permission denied: {e}")
            permission_issues.append(f"{path}: {e}")
    
    results["permission_issues"] = permission_issues
    print()
    
    # Test network connectivity
    print("🌐 Testing Network Connectivity...")
    test_urls = [
        "https://hub.docker.com",
        "https://pypi.org",
        "https://api.twitter.com",
        "https://graph.facebook.com"
    ]
    
    network_issues = []
    for url in test_urls:
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=5)
            print(f"✅ {url} - Accessible")
        except Exception as e:
            print(f"❌ {url} - Not accessible: {e}")
            network_issues.append(f"{url}: {e}")
    
    results["network_issues"] = network_issues
    print()
    
    # macOS specific issues
    print("🍎 Checking macOS Specific Issues...")
    macos_issues = []
    
    # Check for Apple Silicon compatibility
    if results["platform_info"]["machine"] == "arm64":
        print("⚠️  Apple Silicon (M1/M2) detected")
        macos_issues.append("Apple Silicon may have Docker compatibility issues")
        results["recommendations"].append("Use Docker Desktop with Rosetta 2 emulation if needed")
    
    # Check for Gatekeeper issues
    if results["platform_info"]["system"] == "Darwin":
        print("⚠️  macOS Gatekeeper may block unsigned binaries")
        macos_issues.append("Gatekeeper may block Docker containers")
        results["recommendations"].append("Configure Gatekeeper to allow Docker")
    
    results["macos_issues"] = macos_issues
    print()
    
    # Generate compatibility report
    print("📊 Compatibility Summary")
    print("-" * 40)
    
    compatibility_score = 100
    
    if not results["docker_compatibility"].get("docker_available", False):
        compatibility_score -= 30
        print("❌ Docker not available (-30 points)")
    
    if missing_packages:
        compatibility_score -= len(missing_packages) * 5
        print(f"❌ {len(missing_packages)} missing Python packages (-{len(missing_packages) * 5} points)")
    
    if permission_issues:
        compatibility_score -= len(permission_issues) * 10
        print(f"❌ {len(permission_issues)} permission issues (-{len(permission_issues) * 10} points)")
    
    if network_issues:
        compatibility_score -= len(network_issues) * 5
        print(f"❌ {len(network_issues)} network issues (-{len(network_issues) * 5} points)")
    
    results["compatibility_score"] = max(0, compatibility_score)
    
    print(f"\n🎯 Overall Compatibility Score: {results['compatibility_score']}/100")
    
    if results["compatibility_score"] >= 80:
        print("✅ Good compatibility - Platform should work well on macOS")
    elif results["compatibility_score"] >= 60:
        print("⚠️  Moderate compatibility - Some issues need to be resolved")
    else:
        print("❌ Poor compatibility - Significant issues need to be addressed")
    
    # Recommendations
    if results["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")
    
    # Save results
    with open("macos_compatibility_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: macos_compatibility_results.json")
    
    return results

if __name__ == "__main__":
    test_macos_compatibility()
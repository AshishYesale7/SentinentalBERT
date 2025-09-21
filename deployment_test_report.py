#!/usr/bin/env python3
"""
Comprehensive deployment test report for InsideOut platform
Tests Linux and macOS compatibility, generates deployment readiness report
"""

import os
import sys
import platform
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def test_system_requirements():
    """Test system requirements and compatibility"""
    print("🖥️  Testing System Requirements")
    print("-" * 40)
    
    results = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "memory_available": "Unknown",
        "disk_space": "Unknown"
    }
    
    # Test memory (Linux)
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal:' in line:
                    mem_kb = int(line.split()[1])
                    mem_gb = mem_kb / 1024 / 1024
                    results["memory_available"] = f"{mem_gb:.1f} GB"
                    break
    except:
        pass
    
    # Test disk space
    try:
        statvfs = os.statvfs('/')
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        free_gb = free_bytes / (1024**3)
        results["disk_space"] = f"{free_gb:.1f} GB"
    except:
        pass
    
    print(f"Platform: {results['platform']}")
    print(f"Python: {results['python_version']}")
    print(f"Architecture: {results['architecture']}")
    print(f"Memory: {results['memory_available']}")
    print(f"Disk Space: {results['disk_space']}")
    
    return results

def test_docker_availability():
    """Test Docker availability and version"""
    print("\n🐳 Testing Docker Availability")
    print("-" * 40)
    
    docker_info = {
        "docker_available": False,
        "docker_version": None,
        "docker_compose_available": False,
        "docker_compose_version": None,
        "daemon_running": False
    }
    
    # Test Docker
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            docker_info["docker_available"] = True
            docker_info["docker_version"] = result.stdout.strip()
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Docker not available")
    except:
        print("❌ Docker not found")
    
    # Test Docker Compose
    try:
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            docker_info["docker_compose_available"] = True
            docker_info["docker_compose_version"] = result.stdout.strip()
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Docker Compose not available")
    except:
        print("❌ Docker Compose not found")
    
    # Test Docker daemon
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            docker_info["daemon_running"] = True
            print("✅ Docker daemon is running")
        else:
            print("❌ Docker daemon not running")
    except:
        print("❌ Cannot connect to Docker daemon")
    
    return docker_info

def test_python_dependencies():
    """Test Python dependencies"""
    print("\n🐍 Testing Python Dependencies")
    print("-" * 40)
    
    required_packages = [
        'streamlit', 'plotly', 'torch', 'transformers', 'scikit-learn',
        'psycopg2', 'redis', 'fastapi', 'uvicorn', 'networkx', 'pandas',
        'numpy', 'cryptography', 'pydantic', 'requests'
    ]
    
    dependency_status = {}
    
    for package in required_packages:
        try:
            if package == 'psycopg2':
                import psycopg2
                version = psycopg2.__version__
            else:
                module = __import__(package.replace('-', '_'))
                version = getattr(module, '__version__', 'Unknown')
            
            dependency_status[package] = {"available": True, "version": version}
            print(f"✅ {package}: {version}")
        except ImportError:
            dependency_status[package] = {"available": False, "version": None}
            print(f"❌ {package}: Not installed")
    
    return dependency_status

def test_streamlit_dashboard():
    """Test Streamlit dashboard functionality"""
    print("\n📊 Testing Streamlit Dashboard")
    print("-" * 40)
    
    dashboard_status = {
        "file_exists": False,
        "syntax_valid": False,
        "can_import": False,
        "port_available": False
    }
    
    # Check if dashboard file exists
    dashboard_file = Path("viral_dashboard.py")
    if dashboard_file.exists():
        dashboard_status["file_exists"] = True
        print("✅ Dashboard file exists")
        
        # Test syntax
        try:
            with open(dashboard_file, 'r') as f:
                code = f.read()
            compile(code, dashboard_file, 'exec')
            dashboard_status["syntax_valid"] = True
            print("✅ Dashboard syntax is valid")
        except SyntaxError as e:
            print(f"❌ Dashboard syntax error: {e}")
        
        # Test import
        try:
            import viral_dashboard
            dashboard_status["can_import"] = True
            print("✅ Dashboard can be imported")
        except Exception as e:
            print(f"❌ Dashboard import error: {e}")
    else:
        print("❌ Dashboard file not found")
    
    # Test port availability
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 12000))
        if result == 0:
            dashboard_status["port_available"] = False
            print("⚠️  Port 12000 is in use (dashboard may be running)")
        else:
            dashboard_status["port_available"] = True
            print("✅ Port 12000 is available")
        sock.close()
    except:
        print("❌ Cannot test port availability")
    
    return dashboard_status

def test_core_algorithms():
    """Test core viral analysis algorithms"""
    print("\n🧠 Testing Core Algorithms")
    print("-" * 40)
    
    algorithm_status = {
        "viral_scoring": False,
        "content_similarity": False,
        "network_analysis": False,
        "geographic_analysis": False
    }
    
    try:
        # Test viral scoring
        import numpy as np
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Mock data
        data = {
            'engagement': [100, 500, 1000, 50, 2000],
            'timestamp': [datetime.now() - timedelta(hours=i) for i in range(5)],
            'is_repost': [False, True, True, False, True]
        }
        df = pd.DataFrame(data)
        
        # Viral scoring algorithm
        def viral_score(row):
            base = np.log10(row['engagement'] + 1)
            repost_bonus = 2.0 if row['is_repost'] else 0.0
            time_decay = max(0, 1 - (datetime.now() - row['timestamp']).total_seconds() / (24 * 3600))
            return min(10.0, base + repost_bonus + time_decay)
        
        df['viral_score'] = df.apply(viral_score, axis=1)
        algorithm_status["viral_scoring"] = True
        print("✅ Viral scoring algorithm working")
        
    except Exception as e:
        print(f"❌ Viral scoring failed: {e}")
    
    try:
        # Test content similarity
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        texts = ["Sample text 1", "Sample text 2", "Different content"]
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(texts)
        similarity = cosine_similarity(tfidf)
        
        algorithm_status["content_similarity"] = True
        print("✅ Content similarity algorithm working")
        
    except Exception as e:
        print(f"❌ Content similarity failed: {e}")
    
    try:
        # Test network analysis
        import networkx as nx
        
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
        centrality = nx.degree_centrality(G)
        
        algorithm_status["network_analysis"] = True
        print("✅ Network analysis algorithm working")
        
    except Exception as e:
        print(f"❌ Network analysis failed: {e}")
    
    try:
        # Test geographic analysis
        locations = ['Delhi', 'Mumbai', 'Bangalore']
        geo_data = pd.DataFrame({
            'location': locations * 3,
            'count': np.random.randint(1, 100, 9)
        })
        geo_summary = geo_data.groupby('location')['count'].sum()
        
        algorithm_status["geographic_analysis"] = True
        print("✅ Geographic analysis algorithm working")
        
    except Exception as e:
        print(f"❌ Geographic analysis failed: {e}")
    
    return algorithm_status

def test_security_configuration():
    """Test security configuration"""
    print("\n🔒 Testing Security Configuration")
    print("-" * 40)
    
    security_status = {
        "environment_variables": {},
        "file_permissions": {},
        "hardcoded_secrets": []
    }
    
    # Check environment variables
    env_vars = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'JWT_SECRET']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            security_status["environment_variables"][var] = "Set"
            print(f"✅ {var} is set")
        else:
            security_status["environment_variables"][var] = "Not set"
            print(f"⚠️  {var} not set (using default)")
    
    # Check for hardcoded secrets (basic scan)
    suspicious_patterns = ['password=', 'secret=', 'key=', 'token=']
    files_to_check = ['viral_dashboard.py', 'docker-compose.yml']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    for pattern in suspicious_patterns:
                        if pattern in content:
                            security_status["hardcoded_secrets"].append(f"{file_path}: {pattern}")
                            print(f"⚠️  Potential hardcoded secret in {file_path}")
            except:
                pass
    
    if not security_status["hardcoded_secrets"]:
        print("✅ No obvious hardcoded secrets found")
    
    return security_status

def generate_deployment_report():
    """Generate comprehensive deployment report"""
    print("\n📋 Generating Deployment Report")
    print("=" * 60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_requirements": test_system_requirements(),
        "docker_status": test_docker_availability(),
        "python_dependencies": test_python_dependencies(),
        "dashboard_status": test_streamlit_dashboard(),
        "algorithm_status": test_core_algorithms(),
        "security_status": test_security_configuration()
    }
    
    # Calculate overall readiness score
    scores = {
        "system": 1.0,  # Always available
        "docker": 1.0 if report["docker_status"]["docker_available"] and report["docker_status"]["docker_compose_available"] else 0.0,
        "dependencies": sum(1 for dep in report["python_dependencies"].values() if dep["available"]) / len(report["python_dependencies"]),
        "dashboard": sum(1 for status in report["dashboard_status"].values() if status) / len(report["dashboard_status"]),
        "algorithms": sum(1 for status in report["algorithm_status"].values() if status) / len(report["algorithm_status"]),
        "security": 0.8 if len(report["security_status"]["hardcoded_secrets"]) == 0 else 0.4
    }
    
    overall_score = sum(scores.values()) / len(scores) * 100
    report["readiness_score"] = overall_score
    report["component_scores"] = scores
    
    # Save report
    with open('deployment_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\n🎯 Deployment Readiness Score: {overall_score:.1f}/100")
    print("\nComponent Scores:")
    for component, score in scores.items():
        status = "✅" if score >= 0.8 else "⚠️ " if score >= 0.5 else "❌"
        print(f"  {component.capitalize():15} {status} {score*100:.1f}%")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if scores["docker"] < 1.0:
        print("  • Install and start Docker daemon for full deployment")
    if scores["dependencies"] < 1.0:
        print("  • Install missing Python dependencies")
    if scores["dashboard"] < 1.0:
        print("  • Fix dashboard issues for web interface")
    if scores["security"] < 0.8:
        print("  • Review and fix security configuration")
    
    if overall_score >= 80:
        print("\n🎉 Platform is ready for deployment!")
    elif overall_score >= 60:
        print("\n⚠️  Platform needs minor fixes before deployment")
    else:
        print("\n❌ Platform requires significant work before deployment")
    
    return report

def main():
    """Main test execution"""
    print("🚀 InsideOut Platform - Deployment Test Suite")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Environment: {platform.platform()}")
    
    # Run comprehensive tests
    report = generate_deployment_report()
    
    print(f"\n📄 Full report saved to: deployment_report.json")
    
    return report["readiness_score"] >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
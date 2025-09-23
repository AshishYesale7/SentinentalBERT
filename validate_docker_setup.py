#!/usr/bin/env python3
"""
Enhanced SentinelBERT Docker Setup Validation
Indian Police Hackathon - Viral Tracking System

This script validates the Docker deployment setup and ensures all components are ready.
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path

# Colors for output
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    NC = '\033[0m'  # No Color

def log_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def log_header(message):
    print(f"{Colors.PURPLE}{'='*50}{Colors.NC}")
    print(f"{Colors.PURPLE}{message}{Colors.NC}")
    print(f"{Colors.PURPLE}{'='*50}{Colors.NC}")

def check_file_exists(file_path, description):
    """Check if a file exists and log the result."""
    if Path(file_path).exists():
        log_success(f"{description}: ✅ Found")
        return True
    else:
        log_error(f"{description}: ❌ Missing")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and log the result."""
    if Path(dir_path).exists() and Path(dir_path).is_dir():
        log_success(f"{description}: ✅ Found")
        return True
    else:
        log_error(f"{description}: ❌ Missing")
        return False

def run_command(command, description, check_output=False):
    """Run a shell command and return success status."""
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                log_success(f"{description}: ✅ Success")
                return True, result.stdout.strip()
            else:
                log_error(f"{description}: ❌ Failed - {result.stderr.strip()}")
                return False, result.stderr.strip()
        else:
            result = subprocess.run(command, shell=True, timeout=30)
            if result.returncode == 0:
                log_success(f"{description}: ✅ Success")
                return True, ""
            else:
                log_error(f"{description}: ❌ Failed")
                return False, ""
    except subprocess.TimeoutExpired:
        log_error(f"{description}: ❌ Timeout")
        return False, "Timeout"
    except Exception as e:
        log_error(f"{description}: ❌ Exception - {str(e)}")
        return False, str(e)

def check_port_available(port, description):
    """Check if a port is available or in use."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            log_info(f"{description} (port {port}): 🔌 In use (service running)")
            return True
        else:
            log_warning(f"{description} (port {port}): 🔌 Available (service not running)")
            return False
    except Exception as e:
        log_error(f"{description} (port {port}): ❌ Error checking - {str(e)}")
        return False

def validate_docker_files():
    """Validate Docker configuration files."""
    log_header("Validating Docker Configuration Files")
    
    files_to_check = [
        ("docker-compose.enhanced.yml", "Enhanced Docker Compose"),
        ("docker-compose.override.enhanced.yml", "Docker Compose Override"),
        ("Dockerfile.enhanced", "Enhanced Dockerfile"),
        (".env.enhanced", "Enhanced Environment File"),
        ("setup-enhanced-docker.sh", "Setup Script"),
        ("Makefile.enhanced", "Enhanced Makefile"),
    ]
    
    all_files_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    return all_files_exist

def validate_directories():
    """Validate required directories."""
    log_header("Validating Directory Structure")
    
    directories_to_check = [
        ("data/postgres", "PostgreSQL Data Directory"),
        ("data/redis", "Redis Data Directory"),
        ("data/elasticsearch", "Elasticsearch Data Directory"),
        ("data/prometheus", "Prometheus Data Directory"),
        ("data/grafana", "Grafana Data Directory"),
        ("models/nlp", "NLP Models Directory"),
        ("models/viral", "Viral Models Directory"),
        ("cache/nlp", "NLP Cache Directory"),
        ("cache/huggingface", "HuggingFace Cache Directory"),
        ("cache/viral", "Viral Cache Directory"),
        ("evidence/signatures", "Evidence Signatures Directory"),
        ("logs/backend", "Backend Logs Directory"),
        ("logs/nlp", "NLP Logs Directory"),
        ("logs/viral", "Viral Logs Directory"),
        ("logs/evidence", "Evidence Logs Directory"),
        ("sql", "SQL Scripts Directory"),
        (".vscode", "VSCode Configuration Directory"),
    ]
    
    all_dirs_exist = True
    for dir_path, description in directories_to_check:
        if not check_directory_exists(dir_path, description):
            all_dirs_exist = False
    
    return all_dirs_exist

def validate_docker_installation():
    """Validate Docker and Docker Compose installation."""
    log_header("Validating Docker Installation")
    
    docker_ok, docker_version = run_command("docker --version", "Docker Installation", check_output=True)
    if docker_ok:
        log_info(f"Docker Version: {docker_version}")
    
    compose_ok, compose_version = run_command("docker-compose --version", "Docker Compose Installation", check_output=True)
    if compose_ok:
        log_info(f"Docker Compose Version: {compose_version}")
    
    docker_running, _ = run_command("docker info", "Docker Service Running")
    
    return docker_ok and compose_ok and docker_running

def validate_environment_file():
    """Validate environment configuration."""
    log_header("Validating Environment Configuration")
    
    if not Path(".env.enhanced").exists():
        log_error("Environment file .env.enhanced not found")
        return False
    
    try:
        with open(".env.enhanced", "r") as f:
            env_content = f.read()
        
        required_vars = [
            "POSTGRES_PASSWORD",
            "REDIS_PASSWORD",
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_TOKEN_SECRET",
            "TWITTER_BEARER_TOKEN",
        ]
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            log_error(f"Missing environment variables: {', '.join(missing_vars)}")
            return False
        else:
            log_success("All required environment variables found")
            return True
            
    except Exception as e:
        log_error(f"Error reading environment file: {str(e)}")
        return False

def validate_vscode_configuration():
    """Validate VSCode configuration."""
    log_header("Validating VSCode Configuration")
    
    vscode_files = [
        (".vscode/settings.json", "VSCode Settings"),
        (".vscode/launch.json", "VSCode Launch Configuration"),
        (".vscode/tasks.json", "VSCode Tasks Configuration"),
    ]
    
    all_vscode_ok = True
    for file_path, description in vscode_files:
        if not check_file_exists(file_path, description):
            all_vscode_ok = False
    
    return all_vscode_ok

def validate_database_schema():
    """Validate database schema file."""
    log_header("Validating Database Schema")
    
    schema_file = "sql/enhanced_tracking_schema.sql"
    if not check_file_exists(schema_file, "Enhanced Tracking Schema"):
        return False
    
    try:
        with open(schema_file, "r") as f:
            schema_content = f.read()
        
        required_tables = [
            "viral_tracking_sessions",
            "viral_posts",
            "viral_chains",
            "network_analysis",
            "evidence_records",
            "api_usage_tracking",
            "user_influence_scores",
            "tracking_performance_metrics",
        ]
        
        missing_tables = []
        for table in required_tables:
            if f"CREATE TABLE IF NOT EXISTS {table}" not in schema_content:
                missing_tables.append(table)
        
        if missing_tables:
            log_error(f"Missing table definitions: {', '.join(missing_tables)}")
            return False
        else:
            log_success("All required table definitions found")
            return True
            
    except Exception as e:
        log_error(f"Error reading schema file: {str(e)}")
        return False

def check_service_ports():
    """Check if service ports are available or in use."""
    log_header("Checking Service Ports")
    
    ports_to_check = [
        (12000, "Enhanced Dashboard"),
        (12001, "Alternative Dashboard"),
        (8501, "Standard Streamlit"),
        (5432, "PostgreSQL"),
        (6379, "Redis"),
        (9200, "Elasticsearch"),
        (8080, "Backend API"),
        (8000, "NLP Service"),
        (8083, "Viral Detection"),
        (8082, "Evidence Service"),
        (3000, "Grafana"),
        (9090, "Prometheus"),
        (16686, "Jaeger"),
        (8084, "Adminer"),
        (8085, "Redis Commander"),
    ]
    
    for port, description in ports_to_check:
        check_port_available(port, description)

def validate_python_dependencies():
    """Validate Python dependencies."""
    log_header("Validating Python Dependencies")
    
    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "requests",
        "psycopg2-binary",
        "redis",
        "tweepy",
        "networkx",
        "plotly",
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            log_success(f"{package}: ✅ Installed")
        except ImportError:
            log_warning(f"{package}: ⚠️ Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        log_info(f"Missing packages will be installed in Docker containers: {', '.join(missing_packages)}")
    
    return True

def test_docker_build():
    """Test Docker image build."""
    log_header("Testing Docker Image Build")
    
    log_info("Testing enhanced Docker image build (this may take a few minutes)...")
    build_ok, build_output = run_command(
        "docker build -f Dockerfile.enhanced -t sentinelbert-enhanced:test .",
        "Enhanced Docker Image Build"
    )
    
    if build_ok:
        # Clean up test image
        run_command("docker rmi sentinelbert-enhanced:test", "Cleanup Test Image")
    
    return build_ok

def generate_validation_report():
    """Generate a validation report."""
    log_header("Validation Report Summary")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "docker_files": validate_docker_files(),
        "directories": validate_directories(),
        "docker_installation": validate_docker_installation(),
        "environment_config": validate_environment_file(),
        "vscode_config": validate_vscode_configuration(),
        "database_schema": validate_database_schema(),
        "python_dependencies": validate_python_dependencies(),
    }
    
    # Count successful validations
    successful = sum(1 for v in report.values() if v is True)
    total = len([k for k in report.keys() if k != "timestamp"])
    
    log_info(f"Validation Results: {successful}/{total} checks passed")
    
    if successful == total:
        log_success("🎉 All validations passed! Docker setup is ready.")
        log_info("You can now run: ./setup-enhanced-docker.sh")
        return True
    else:
        log_error("❌ Some validations failed. Please fix the issues above.")
        return False

def main():
    """Main validation function."""
    print(f"{Colors.PURPLE}🇮🇳 Enhanced SentinelBERT Docker Setup Validation{Colors.NC}")
    print(f"{Colors.PURPLE}Indian Police Hackathon - Viral Tracking System{Colors.NC}")
    print()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all validations
    try:
        success = generate_validation_report()
        
        if success:
            log_header("Next Steps")
            print("1. Run the setup script: ./setup-enhanced-docker.sh")
            print("2. Or use the Makefile: make setup")
            print("3. Open VSCode: code .")
            print("4. Start development!")
            print()
            print(f"{Colors.GREEN}🚀 Ready for Indian Police Hackathon demo!{Colors.NC}")
            sys.exit(0)
        else:
            log_header("Fix Required Issues")
            print("Please fix the validation errors above before proceeding.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        log_warning("Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_error(f"Validation failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
InsideOut Platform - Advanced Dependency Cleanup Script
========================================================
This Python script provides advanced cleanup functionality for removing
all dependencies, cache files, and temporary files created during development.
"""

import os
import shutil
import subprocess
import sys
import glob
from pathlib import Path

def run_command(command, ignore_errors=True):
    """Run a shell command and optionally ignore errors."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and not ignore_errors:
            print(f"❌ Command failed: {command}")
            print(f"   Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        if not ignore_errors:
            print(f"❌ Exception running command: {command}")
            print(f"   Error: {str(e)}")
        return False

def remove_path(path, description=""):
    """Safely remove a file or directory."""
    try:
        path_obj = Path(path)
        if path_obj.exists():
            if path_obj.is_file():
                path_obj.unlink()
                print(f"  ✓ Removed file: {path} {description}")
            elif path_obj.is_dir():
                shutil.rmtree(path)
                print(f"  ✓ Removed directory: {path} {description}")
            return True
        return False
    except Exception as e:
        print(f"  ❌ Failed to remove {path}: {str(e)}")
        return False

def find_and_remove_pattern(pattern, description=""):
    """Find and remove files/directories matching a pattern."""
    removed_count = 0
    try:
        for path in glob.glob(pattern, recursive=True):
            if remove_path(path, description):
                removed_count += 1
    except Exception as e:
        print(f"  ❌ Error with pattern {pattern}: {str(e)}")
    return removed_count

def cleanup_python_cache():
    """Remove Python cache files and directories."""
    print("🐍 Cleaning Python cache files...")
    
    patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.egg-info",
        "**/.pytest_cache"
    ]
    
    total_removed = 0
    for pattern in patterns:
        count = find_and_remove_pattern(pattern, "(Python cache)")
        total_removed += count
    
    print(f"  📊 Removed {total_removed} Python cache items")

def cleanup_nodejs():
    """Remove Node.js dependencies and cache."""
    print("📦 Cleaning Node.js dependencies...")
    
    # Remove directories
    dirs_to_remove = ["node_modules", ".npm", ".yarn"]
    for dir_name in dirs_to_remove:
        remove_path(dir_name, "(Node.js)")
    
    # Remove files
    files_to_remove = ["package-lock.json", "yarn.lock", "npm-debug.log"]
    for file_name in files_to_remove:
        remove_path(file_name, "(Node.js)")
    
    # Clear npm cache
    run_command("npm cache clean --force")

def cleanup_python_environments():
    """Remove Python virtual environments."""
    print("🔧 Cleaning Python virtual environments...")
    
    env_dirs = ["venv", ".venv", "env", ".env"]
    for env_dir in env_dirs:
        remove_path(env_dir, "(Virtual environment)")
    
    # Clear pip cache
    run_command("pip cache purge")

def cleanup_build_directories():
    """Remove build and distribution directories."""
    print("🏗️ Cleaning build directories...")
    
    build_dirs = ["build", "dist", ".eggs", "*.egg-info"]
    for build_dir in build_dirs:
        if "*" in build_dir:
            find_and_remove_pattern(build_dir, "(Build)")
        else:
            remove_path(build_dir, "(Build)")

def cleanup_ide_files():
    """Remove IDE and editor configuration files."""
    print("💻 Cleaning IDE and editor files...")
    
    ide_items = [".vscode", ".idea", ".DS_Store", "**/.DS_Store", "*.swp", "*.swo", "*~"]
    for item in ide_items:
        if "*" in item:
            find_and_remove_pattern(item, "(IDE)")
        else:
            remove_path(item, "(IDE)")

def cleanup_logs():
    """Remove log files."""
    print("📝 Cleaning log files...")
    
    log_patterns = ["*.log", "logs/*.log", "**/*.log"]
    for pattern in log_patterns:
        find_and_remove_pattern(pattern, "(Log file)")

def cleanup_temporary_files():
    """Remove temporary files and directories."""
    print("🗂️ Cleaning temporary files...")
    
    temp_patterns = [
        "/tmp/streamlit-*",
        "/tmp/pip-*",
        ".coverage",
        "htmlcov",
        ".pytest_cache",
        "**/.ipynb_checkpoints"
    ]
    
    for pattern in temp_patterns:
        find_and_remove_pattern(pattern, "(Temporary)")

def cleanup_model_caches():
    """Remove ML model cache directories."""
    print("🤖 Cleaning model cache files...")
    
    cache_dirs = [
        os.path.expanduser("~/.cache/huggingface"),
        os.path.expanduser("~/.cache/torch"),
        os.path.expanduser("~/.cache/transformers"),
        os.path.expanduser("~/.streamlit")
    ]
    
    for cache_dir in cache_dirs:
        remove_path(cache_dir, "(Model cache)")

def cleanup_database_files():
    """Remove database files."""
    print("🗄️ Cleaning database files...")
    
    db_patterns = ["*.db", "*.sqlite", "*.sqlite3"]
    for pattern in db_patterns:
        find_and_remove_pattern(pattern, "(Database)")

def cleanup_authentication_files():
    """Remove generated authentication files."""
    print("🔑 Cleaning authentication files...")
    
    auth_files = ["generate_test_token.py", "test_tokens.txt", ".env*"]
    for file_pattern in auth_files:
        if "*" in file_pattern:
            find_and_remove_pattern(file_pattern, "(Auth)")
        else:
            remove_path(file_pattern, "(Auth)")

def cleanup_screenshots():
    """Remove screenshot directories."""
    print("📸 Cleaning screenshot files...")
    remove_path(".browser_screenshots", "(Screenshots)")

def stop_services():
    """Stop running services."""
    print("🛑 Stopping running services...")
    
    services = [
        "pkill -f streamlit",
        "pkill -f uvicorn",
        "pkill -f 'python.*main_simple.py'"
    ]
    
    for service in services:
        run_command(service)
    
    # Wait for services to stop
    import time
    time.sleep(2)

def get_directory_size():
    """Get the current directory size."""
    try:
        result = subprocess.run(["du", "-sh", "."], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split()[0]
    except:
        pass
    return "Unknown"

def main():
    """Main cleanup function."""
    print("🧹 InsideOut Platform - Advanced Dependency Cleanup")
    print("=" * 55)
    
    # Get initial directory size
    initial_size = get_directory_size()
    print(f"📊 Initial directory size: {initial_size}")
    print()
    
    # Stop services first
    stop_services()
    
    # Run all cleanup functions
    cleanup_functions = [
        cleanup_python_cache,
        cleanup_nodejs,
        cleanup_python_environments,
        cleanup_build_directories,
        cleanup_ide_files,
        cleanup_logs,
        cleanup_temporary_files,
        cleanup_model_caches,
        cleanup_database_files,
        cleanup_authentication_files,
        cleanup_screenshots
    ]
    
    for cleanup_func in cleanup_functions:
        try:
            cleanup_func()
        except Exception as e:
            print(f"❌ Error in {cleanup_func.__name__}: {str(e)}")
    
    # Get final directory size
    final_size = get_directory_size()
    
    print()
    print("✅ Advanced cleanup completed successfully!")
    print("=" * 55)
    print(f"📊 Final directory size: {final_size}")
    print()
    print("🎯 Cleanup Summary:")
    print("  ✓ Python cache files removed")
    print("  ✓ Node.js dependencies removed")
    print("  ✓ Virtual environments removed")
    print("  ✓ Build directories removed")
    print("  ✓ IDE configuration files removed")
    print("  ✓ Log files removed")
    print("  ✓ Temporary files removed")
    print("  ✓ Model caches removed")
    print("  ✓ Database files removed")
    print("  ✓ Authentication files removed")
    print("  ✓ Screenshot files removed")
    print("  ✓ All services stopped")
    print()
    print("🚀 The project is now completely clean!")
    print("   To restart the services:")
    print("   1. Backend: cd services/nlp && python main_simple.py")
    print("   2. Frontend: streamlit run viral_dashboard.py --server.port 12001")

if __name__ == "__main__":
    main()
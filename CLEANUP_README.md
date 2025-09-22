# 🧹 InsideOut Platform - Dependency Cleanup Scripts

This directory contains comprehensive cleanup scripts to remove all dependencies, cache files, and temporary files created during the InsideOut Platform development.

## 📋 Available Cleanup Scripts

### 1. 🚀 Quick Cleanup (Recommended)
**File:** `quick_cleanup.sh`
**Usage:** `./quick_cleanup.sh`

**What it removes:**
- Node.js dependencies (`node_modules`, `package-lock.json`, `yarn.lock`)
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`venv`, `.venv`, `env`)
- Log files (`*.log`)
- Build directories (`build`, `dist`, `*.egg-info`)
- Stops running services

**Best for:** Quick cleanup before committing code or sharing the project.

### 2. 🔧 Comprehensive Cleanup
**File:** `cleanup_dependencies.sh`
**Usage:** `./cleanup_dependencies.sh`

**What it removes:**
- All items from Quick Cleanup, plus:
- IDE configuration files (`.vscode`, `.idea`, `.DS_Store`)
- Jupyter notebook checkpoints
- Test cache files (`.pytest_cache`)
- Coverage files (`.coverage`, `htmlcov`)
- Docker files
- Environment files (`.env*`)
- Database files (`*.db`, `*.sqlite`)
- Model cache directories
- Streamlit cache
- Authentication files
- Screenshot files
- Backup files (`*.bak`, `*~`)

**Best for:** Complete project reset or preparing for distribution.

### 3. 🐍 Advanced Python Cleanup
**File:** `cleanup_dependencies.py`
**Usage:** `python cleanup_dependencies.py`

**Features:**
- Advanced pattern matching for file removal
- Detailed progress reporting
- Error handling and logging
- Directory size calculation (before/after)
- Safe removal with exception handling

**Best for:** Developers who want detailed feedback and advanced cleanup options.

## 🎯 Usage Examples

### Quick Cleanup (Most Common)
```bash
# Make executable (first time only)
chmod +x quick_cleanup.sh

# Run cleanup
./quick_cleanup.sh
```

### Comprehensive Cleanup
```bash
# Make executable (first time only)
chmod +x cleanup_dependencies.sh

# Run comprehensive cleanup
./cleanup_dependencies.sh
```

### Advanced Python Cleanup
```bash
# Run with Python
python cleanup_dependencies.py

# Or make executable and run directly
chmod +x cleanup_dependencies.py
./cleanup_dependencies.py
```

## 📊 What Gets Cleaned

| Category | Files/Directories | Scripts |
|----------|------------------|---------|
| **Node.js** | `node_modules/`, `package-lock.json`, `yarn.lock` | All |
| **Python Cache** | `__pycache__/`, `*.pyc`, `*.pyo` | All |
| **Virtual Envs** | `venv/`, `.venv/`, `env/` | All |
| **Build Files** | `build/`, `dist/`, `*.egg-info/` | All |
| **Log Files** | `*.log`, `logs/*.log` | All |
| **IDE Files** | `.vscode/`, `.idea/`, `.DS_Store` | Comprehensive, Advanced |
| **Test Files** | `.pytest_cache/`, `.coverage` | Comprehensive, Advanced |
| **Model Cache** | `~/.cache/huggingface/`, `~/.cache/torch/` | Comprehensive, Advanced |
| **Temp Files** | `/tmp/streamlit-*`, `/tmp/pip-*` | Comprehensive, Advanced |

## ⚠️ Important Notes

1. **Backup Important Data:** These scripts will permanently delete files. Make sure to backup any important data before running.

2. **Services Will Be Stopped:** All scripts will stop running Streamlit and FastAPI services.

3. **Model Downloads:** If you run the comprehensive cleanup, you may need to re-download ML models when restarting the services.

4. **Virtual Environments:** If you're using a virtual environment, you'll need to recreate it after cleanup.

## 🔄 Restarting Services After Cleanup

After running any cleanup script, restart the services:

```bash
# 1. Start the backend NLP service
cd services/nlp
python main_simple.py

# 2. In another terminal, start the frontend dashboard
streamlit run viral_dashboard.py --server.port 12001 --server.address 0.0.0.0
```

## 🎨 Project Structure After Cleanup

After cleanup, your project will contain only the essential source code files:

```
SentinentalBERT/
├── services/
│   └── nlp/
│       └── main_simple.py
├── viral_dashboard.py
├── REMAINING_TASKS.md
├── cleanup_dependencies.sh
├── cleanup_dependencies.py
├── quick_cleanup.sh
└── CLEANUP_README.md
```

## 🚀 Benefits of Regular Cleanup

- **Reduced Storage:** Removes gigabytes of cached and temporary files
- **Faster Git Operations:** Smaller repository size for cloning/pushing
- **Clean Development:** Fresh start without cached conflicts
- **Security:** Removes temporary files that might contain sensitive data
- **Performance:** Eliminates outdated cache files that might cause issues

## 🆘 Troubleshooting

**Permission Denied:**
```bash
chmod +x cleanup_dependencies.sh
chmod +x quick_cleanup.sh
chmod +x cleanup_dependencies.py
```

**Script Not Found:**
Make sure you're in the correct directory:
```bash
cd /workspace/project/SentinentalBERT
ls -la *.sh *.py
```

**Services Won't Stop:**
Manually kill processes:
```bash
pkill -9 -f streamlit
pkill -9 -f uvicorn
```

---

**Happy Cleaning! 🧹✨**
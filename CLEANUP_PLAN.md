# 🧹 VRCPhoto2URL Folder Cleanup & Organization

## 📋 Current Issues
- Multiple documentation files scattered in root directory
- Redundant folders and files
- Unclear project structure
- Documentation spread across multiple locations

## 🎯 Cleanup Plan

### 1. Create Clean Root Structure
```
VRCPhoto2URL/
├── 📱 client/          # Desktop client application
├── 🌐 server/          # Railway server application  
├── 📚 docs/            # All documentation consolidated
├── 🧪 tests/           # All test scripts
├── 🔧 scripts/         # Utility and setup scripts
├── 📋 README.md        # Main project documentation
└── 🚀 quick-start.md   # Quick setup guide
```

### 2. Consolidate Documentation
- Move all `.md` files to `docs/` folder
- Create categorized documentation structure
- Remove duplicate files

### 3. Organize Client & Server
- Move client from `custom-server-file-manager-1/client/` to `client/`
- Move server from `custom-server-file-manager-1/server/` to `server/`
- Clean up redundant folders

### 4. Create Test Suite
- Consolidate all test files into `tests/` folder
- Organize by component (client tests, server tests, integration tests)

### 5. Setup Scripts
- Create easy setup and launch scripts
- Batch files for Windows users
- Python scripts for cross-platform

## 🔄 Cleanup Process
1. Create new folder structure
2. Move files to appropriate locations
3. Update file references and imports
4. Remove old/redundant folders
5. Create new organized documentation

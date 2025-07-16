# 🔍 **COMPREHENSIVE CODEBASE AUDIT PROMPT FOR AI CODING AGENTS**

## **MISSION OBJECTIVE**
Conduct a thorough audit of the Sophia AI repository to identify and eliminate technical debt, unused code, redundant files, and consolidation opportunities while preserving all essential functionality.

## **📋 AUDIT METHODOLOGY**

### **1. STATIC CODE ANALYSIS**

#### **Python Code Analysis:**
```
ANALYZE ALL *.py FILES FOR:
- Unused imports (not referenced in file)
- Dead functions/classes (no callers found via grep/AST analysis)
- Unreachable code (after return statements, in else: pass blocks)
- Duplicate functions across files (same signature, similar logic)
- Empty files or files with only imports
- Commented-out code blocks (# TODO: DELETE, """ OLD CODE """)
- Functions with identical implementations
- Classes with no instantiation found anywhere
```

#### **Frontend Code Analysis:**
```
ANALYZE ALL *.tsx, *.ts, *.js, *.jsx FILES FOR:
- Unused React components (no imports found)
- Unused CSS classes (search for class usage across components)
- Dead API endpoints (frontend calls but no backend route)
- Unused utility functions in utils/ directories
- Orphaned test files for components that no longer exist
- Duplicate styling patterns that could be consolidated
```

### **2. FILE SYSTEM CLEANUP ANALYSIS**

#### **Identify Orphaned Files:**
```
SEARCH FOR FILES THAT SHOULD BE REMOVED:
- Backup files: *.backup, *.bak, *.old, *_backup.*, *-backup.*
- Temporary files: *.tmp, *.temp, temp_*, temporary_*
- Editor files: *.swp, *.swo, *~, .DS_Store
- Log files in unexpected places: *.log outside of logs/ directories
- Empty directories (no files, no purpose)
- Duplicate configuration files (same content, different locations)
- Old migration files that are no longer relevant
```

#### **Script Consolidation Opportunities:**
```
ANALYZE ALL scripts/ DIRECTORIES FOR:
- Scripts with identical or nearly identical functionality
- One-time scripts that should be moved to scripts/one_time/
- Scripts that duplicate existing functionality from other scripts
- Scripts with hardcoded values that should use configuration
- Deployment scripts that overlap in functionality
- Scripts that are no longer called by any CI/CD or documentation
```

### **3. DOCUMENTATION CONSOLIDATION**

#### **Documentation Analysis:**
```
REVIEW ALL *.md FILES FOR:
- Duplicate documentation (same information in multiple files)
- Outdated documentation (references to removed technologies)
- Documentation for features/scripts that no longer exist
- README files that could be consolidated into main README
- Empty or stub documentation files
- Documentation that contradicts other documentation
- Architecture docs that don't match current implementation
```

#### **Documentation Directory Structure:**
```
CONSOLIDATION OPPORTUNITIES:
- Multiple docs/ directories that should be unified
- API documentation scattered across multiple files
- Deployment guides that overlap significantly
- Getting started guides in multiple locations
- Architecture documentation fragmentation
```

### **4. DEPENDENCY AND CONFIGURATION CLEANUP**

#### **Package Management Analysis:**
```
ANALYZE ALL DEPENDENCY FILES:
- requirements.txt vs requirements.docker.txt vs pyproject.toml conflicts
- Unused dependencies (imported packages not found in codebase)
- Duplicate dependencies with different versions
- Development dependencies mixed with production
- Optional dependencies that are actually required
- Dependencies for removed features/integrations
```

#### **Configuration File Cleanup:**
```
REVIEW ALL CONFIG FILES:
- Duplicate configuration files (same purpose, different location)
- Configuration for services/features that were removed
- Environment files with unused variables
- Docker configurations that are no longer used
- Kubernetes manifests for deprecated services
- CI/CD configurations that reference removed scripts/services
```

### **5. INFRASTRUCTURE AS CODE AUDIT**

#### **Infrastructure Cleanup:**
```
ANALYZE INFRASTRUCTURE DIRECTORIES:
- Pulumi/Terraform configurations for removed services
- Docker configurations that are no longer built/deployed
- Kubernetes manifests without corresponding services
- Monitoring configurations for non-existent services
- Network configurations for removed infrastructure
- Cloud resource definitions that are no longer used
```

### **6. TEST FILE ANALYSIS**

#### **Test Suite Cleanup:**
```
REVIEW ALL test*/ DIRECTORIES:
- Test files for functions/classes that no longer exist
- Mock configurations for removed external services
- Integration tests for deprecated API endpoints
- Fixture files for removed test scenarios
- Test utilities that duplicate existing functionality
- Performance tests for removed features
```

### **7. SPECIFIC SOPHIA AI PATTERNS TO LOOK FOR**

#### **Known Redundancy Patterns:**
```
SOPHIA AI SPECIFIC CLEANUP:
- Multiple MCP server implementations with similar functionality
- Duplicate FastAPI route definitions across files
- Multiple database connection managers
- Redundant secret management implementations
- Duplicate LLM client configurations
- Multiple Docker deployment strategies for same service
- Overlapping monitoring/logging implementations
```

#### **Post-Elimination Cleanup:**
```
RECENT ELIMINATION ARTIFACTS:
- References to removed Vercel/Snowflake/Weaviate in comments
- Import statements for eliminated packages
- Configuration sections for removed services
- Documentation that mentions eliminated technologies
- Environment variables for removed integrations
- Kubernetes manifests for eliminated services
```

## **📊 AUDIT REPORTING FORMAT**

### **Required Output Structure:**
```
## CODEBASE AUDIT RESULTS

### 🗑️ IMMEDIATE DELETION CANDIDATES
- [ ] File: path/to/file.py - Reason: No imports found, empty except for boilerplate
- [ ] Directory: old_backups/ - Reason: Contains only .backup files from 2024
- [ ] Script: scripts/duplicate_deploy.sh - Reason: Identical to scripts/deploy_main.sh

### 🔄 CONSOLIDATION OPPORTUNITIES  
- [ ] Merge: [file1.py, file2.py] -> consolidated_file.py - Reason: Identical utility functions
- [ ] Unify: docs/api/ + docs/endpoints/ -> docs/api-reference/ - Reason: Duplicate API docs

### ⚠️ SUSPICIOUS PATTERNS REQUIRING REVIEW
- [ ] Function: utils.py:old_function() - Reason: No callers found, but name suggests utility
- [ ] Config: config/legacy.json - Reason: Unclear if still needed for backward compatibility

### 📈 ESTIMATED IMPACT
- Files to delete: X files (Y MB saved)
- Lines of code reduction: X lines  
- Directories to remove: X directories
- Dependencies to remove: X packages
- Documentation consolidation: X -> Y files
```

## **🚨 SAFETY REQUIREMENTS**

### **Before Deletion Rules:**
```
MANDATORY SAFETY CHECKS:
1. Grep search entire codebase for any reference to file/function name
2. Check git history - was this recently active? (git log --follow)
3. Search documentation for mentions of the file/feature
4. Check if file is referenced in configuration files
5. Verify no dynamic imports (importlib, getattr patterns)
6. Confirm no external systems depend on API endpoints
7. Check CI/CD pipelines for script references
```

### **Preservation Rules:**
```
NEVER DELETE:
- Files modified in last 30 days (unless obviously temporary)
- Anything referenced in main configuration files
- License files, security policies, compliance docs
- Database migration files (even old ones)
- Backup/disaster recovery scripts
- Files with extensive git history and multiple contributors
- External integrations that might be sleeping/seasonal
```

## **🔧 EXECUTION METHODOLOGY**

### **Phase 1: Discovery (Safe Exploration)**
1. Generate comprehensive file inventory with metadata
2. Build dependency graph of imports/references
3. Identify obvious candidates (*.backup, *.tmp, empty files)
4. Create preliminary deletion/consolidation lists

### **Phase 2: Analysis (Deep Investigation)**  
1. Static analysis for dead code patterns
2. Cross-reference with git history and documentation
3. Identify consolidation opportunities with impact analysis
4. Generate safety validation reports

### **Phase 3: Validation (Safety Verification)**
1. Run comprehensive grep searches for each deletion candidate
2. Test build/deployment processes with proposed changes
3. Validate no broken imports/references
4. Create rollback plan for each major change

### **Phase 4: Implementation (Careful Execution)**
1. Start with obvious/safe deletions (*.backup, empty files)
2. Implement consolidations with testing at each step
3. Update documentation and references
4. Validate system functionality after each batch

## **💡 AUTOMATION HINTS**

### **Useful Command Patterns:**
```bash
# Find unused Python imports
find . -name "*.py" -exec python -c "import ast; print('Unused imports in {}')" {} \;

# Find duplicate files
find . -type f -exec md5sum {} \; | sort | uniq -d -w32

# Find large files that might be artifacts
find . -type f -size +10M -not -path "./.git/*"

# Find files not modified in 6+ months
find . -type f -mtime +180 -not -path "./.git/*"

# Search for dead CSS classes
grep -r "class.*=" --include="*.tsx" --include="*.jsx" | grep -o "class.*" | sort | uniq

# Find scripts not referenced in docs or other scripts
find scripts/ -name "*.sh" -exec basename {} \; | while read script; do
  if ! grep -r "$script" . --exclude-dir=.git >/dev/null; then
    echo "Orphaned script: $script"
  fi
done
```

## **🎯 SUCCESS CRITERIA**

### **Quantifiable Goals:**
- [ ] Reduce repository size by 15-25%
- [ ] Eliminate 100+ unused files
- [ ] Consolidate 50+ duplicate/similar files
- [ ] Remove 200+ unused dependencies/imports
- [ ] Unify fragmented documentation (docs/ directories)
- [ ] Achieve sub-2GB repository size
- [ ] Maintain 100% functionality (all tests pass)

### **Quality Improvements:**
- [ ] Cleaner git status (fewer untracked artifacts)
- [ ] Faster repository operations (clone, checkout, search)
- [ ] Clearer documentation structure
- [ ] Reduced developer confusion from duplicate files
- [ ] Improved CI/CD performance (fewer files to process)

---

**🚀 Execute this audit with extreme thoroughness but maximum safety. When in doubt, flag for human review rather than delete. The goal is a lean, clean, maintainable codebase that preserves all essential functionality.** 
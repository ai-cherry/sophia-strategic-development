# 🚀 **QUICK AUDIT PROMPT REFERENCE CARD**

## **COPY-PASTE PROMPT FOR AI CODING AGENTS**

```
🔍 COMPREHENSIVE CODEBASE AUDIT REQUEST

Please audit this repository for cleanup opportunities. Focus on:

1. **DEAD CODE**: Find unused imports, functions, classes, and files
2. **DUPLICATES**: Identify duplicate files, similar scripts, redundant configs  
3. **ARTIFACTS**: Locate backup files (*.backup, *.bak, *.tmp), empty files, large artifacts
4. **CONSOLIDATION**: Find scattered documentation, similar scripts, duplicate dependencies

**SPECIFIC PATTERNS TO FIND:**
- Python: Unused imports, dead functions, empty files with only imports
- Frontend: Unused components, orphaned CSS, dead API calls
- Scripts: Duplicate deployment scripts, orphaned utilities, hardcoded configs
- Docs: Duplicate README files, outdated architecture docs, scattered API docs
- Config: Duplicate package files, unused environment variables, old service configs

**SAFETY RULES:**
- Never delete files modified in last 30 days
- Grep search for any references before flagging for deletion
- Check git history for recently active files
- Flag suspicious cases for human review

**OUTPUT FORMAT:**
## AUDIT RESULTS
### 🗑️ SAFE TO DELETE
- [ ] File: path/reason
### 🔄 CONSOLIDATION OPPORTUNITIES  
- [ ] Merge: files -> target (reason)
### ⚠️ NEEDS REVIEW
- [ ] File: path (unclear if needed)

Be thorough but conservative. When in doubt, flag for review.
```

## **SPECIFIC SOPHIA AI PATTERNS**

```
🎯 SOPHIA AI SPECIFIC CLEANUP PATTERNS

Look for these common patterns in this codebase:

**POST-ELIMINATION ARTIFACTS:**
- References to removed Vercel/Snowflake/Weaviate in comments/imports
- Configuration sections for eliminated services
- Import statements for removed packages (weaviate-client, vercel SDK)
- Environment variables for removed integrations

**MCP SERVER REDUNDANCY:**
- Multiple MCP servers with overlapping functionality
- Duplicate FastAPI route definitions
- Similar database connection patterns
- Redundant secret management implementations

**DEPLOYMENT SCRIPT OVERLAP:**
- Multiple Docker deployment strategies for same service
- Overlapping Kubernetes manifests
- Duplicate CI/CD workflows
- Similar infrastructure automation scripts

**DOCUMENTATION FRAGMENTATION:**
- Multiple docs/ directories with similar content
- Scattered API documentation
- Duplicate getting-started guides
- Overlapping architecture documentation
```

## **AUTOMATION COMMANDS**

```bash
# Run the automated audit script
python scripts/automated_codebase_audit.py --mode=report

# Safe cleanup of obvious artifacts
python scripts/automated_codebase_audit.py --mode=safe-cleanup

# Find large files
find . -type f -size +10M -not -path "./.git/*"

# Find backup files
find . -name "*.backup" -o -name "*.bak" -o -name "*.tmp" -o -name "*~"

# Find duplicate file content
find . -type f -exec md5sum {} \; | sort | uniq -d -w32

# Find orphaned scripts
find scripts/ -name "*.sh" -exec basename {} \; | while read script; do
  if ! grep -r "$script" . --exclude-dir=.git >/dev/null; then
    echo "Orphaned: $script"
  fi
done
```

## **ESTIMATED IMPACT FOR SOPHIA AI**

Based on repository analysis:
- **Current repo size**: ~553MB  
- **File count**: 23,000+ (includes artifacts)
- **Estimated cleanup potential**: 15-25% size reduction
- **Target outcomes**: 
  - Remove 100+ unused files
  - Consolidate 50+ duplicate files  
  - Clean 200+ dead imports
  - Unify documentation structure
  - Achieve sub-2GB clean repository 
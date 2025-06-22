# Sophia AI Codebase Cleanup - Direct Approach

## The Problem
We have a messy codebase with:
- 226MB+ of vendored dependencies committed to Git
- Multiple duplicate files doing the same thing
- Inconsistent patterns throughout

## The Solution - Simple and Direct

### Step 1: Clean Up Vendored Dependencies (Do This First!)
```bash
# Remove the big offenders from Git (but keep them locally)
git rm -r --cached frontend/node_modules
git rm -r --cached sophia_admin_api/venv
git rm -r --cached sophia_venv

# Update .gitignore to prevent this from happening again
echo "node_modules/" >> .gitignore
echo "venv/" >> .gitignore
echo "*_venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".npm/" >> .gitignore

# Commit these changes
git add .gitignore
git commit -m "Remove vendored dependencies and update gitignore"
```

### Step 2: Run the Automated Cleanup Script
```bash
# First, see what it will do (dry run)
python scripts/execute_codebase_cleanup.py --dry-run

# If it looks good, run it for real
python scripts/execute_codebase_cleanup.py

# Validate the cleanup worked
python scripts/execute_codebase_cleanup.py --validate-only
```

### Step 3: Commit the Changes
```bash
# Add all the cleanup changes
git add -A

# Commit with a clear message
git commit -m "Major codebase cleanup: consolidate duplicates, fix structure"

# Push to main (or create a PR if you prefer)
git push origin main
```

## What the Cleanup Does

1. **Removes Vendored Dependencies**
   - Saves ~226MB of repository size
   - Speeds up cloning and builds

2. **Consolidates Duplicate Files**
   - Merges 4 main.py files into 1
   - Combines duplicate integrations
   - Unifies API routes

3. **Fixes Directory Structure**
   - Removes malformed directory names
   - Organizes documentation
   - Cleans up scripts folder

4. **Standardizes Patterns**
   - Single secret management approach
   - Consistent MCP server patterns
   - Unified configuration

## If Something Goes Wrong

### Quick Rollback
```bash
# Undo the last commit
git reset --hard HEAD~1

# Or go back to a specific commit
git reset --hard <commit-hash>
```

### Partial Rollback
```bash
# Undo specific files
git checkout HEAD -- path/to/file
```

## Why This Matters

- **Faster Development**: No more 226MB downloads
- **Clearer Code**: One way to do things, not four
- **Easier Onboarding**: New developers understand the structure
- **Better Performance**: Faster builds and deployments

## Next Steps After Cleanup

1. **Update Your Local Environment**
   ```bash
   # Reinstall dependencies properly
   cd frontend && npm install
   cd ../backend && pip install -r requirements.txt
   ```

2. **Test Everything Works**
   ```bash
   # Start the backend
   cd backend && python main.py

   # In another terminal, test the API
   curl http://localhost:8000/health
   ```

3. **Update Any External Scripts**
   - Check for hardcoded paths
   - Update import statements
   - Fix any broken references

## The Bottom Line

This cleanup is about making the codebase manageable again. No fancy branching strategies, no complex workflows - just clean up the mess and move forward.

The automated script does the heavy lifting. Your job is to:
1. Remove vendored deps from Git
2. Run the cleanup script
3. Test that everything still works
4. Commit and push

That's it. Keep it simple.

# Sophia AI Backend Syntax Fix Checklist

## 🎯 Primary Goal
Get the backend service running on port 8000 with working health endpoints.

## ✅ Pre-Flight Checks
- [ ] Python 3.11+ installed
- [ ] Pulumi CLI installed
- [ ] Access to `scoobyjava-org` Pulumi organization
- [ ] Current working directory is project root

## 🔧 Step-by-Step Fix Process

### Phase 1: Assessment
- [ ] Count total syntax errors: `find backend -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -c "Error"`
- [ ] Identify critical path files
- [ ] Check if `backend/core/auto_esc_config.py` compiles
- [ ] Review existing fix scripts in `/scripts/`

### Phase 2: Fix Critical Blocker (auto_esc_config.py)
- [ ] Check syntax: `python -m py_compile backend/core/auto_esc_config.py`
- [ ] If broken, either:
  - [ ] Fix with automated script
  - [ ] Recreate from the template in QUICK_START_SYNTAX_FIX.md
- [ ] Verify it imports correctly: `python -c "from backend.core.auto_esc_config import config"`

### Phase 3: Run Automated Fixes
- [ ] Execute: `python scripts/fix_docstring_corruption.py`
- [ ] Check progress: `find backend -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -c "Error"`
- [ ] If errors remain, try: `python scripts/fix_critical_syntax_errors.py`

### Phase 4: Test Minimal Backend
- [ ] Set environment: `export PULUMI_ORG=scoobyjava-org`
- [ ] Run backend: `pulumi env run scoobyjava-org/default/sophia-ai-production -- python3 backend/minimal_main.py`
- [ ] Check for import errors in console
- [ ] If backend starts, proceed to health checks

### Phase 5: Verify Health Endpoints
- [ ] Test health: `curl http://localhost:8000/health`
- [ ] Test config: `curl http://localhost:8000/config`
- [ ] Test secrets: `curl http://localhost:8000/test/secrets`
- [ ] Verify ESC integration shows "working" status

### Phase 6: Fix Remaining Core Files (if needed)
- [ ] Fix `backend/main.py`
- [ ] Fix `backend/agents/core/agent_framework.py`
- [ ] Fix `backend/agents/specialized/pay_ready_agents.py`
- [ ] Fix `backend/integrations/snowflake_integration.py`

### Phase 7: Full Backend Test
- [ ] Run full backend: `python backend/main.py`
- [ ] Check all endpoints are accessible
- [ ] Verify no import errors

## 🛠️ Troubleshooting Guide

### Common Issues and Solutions

#### IndentationError in auto_esc_config.py
- **Solution**: The file has corrupted indentation. Recreate it from the template.

#### ImportError: cannot import name 'config'
- **Solution**: The auto_esc_config.py file isn't properly exporting the config singleton.

#### "No module named 'backend'"
- **Solution**: Ensure you're running from the project root directory.

#### Pulumi command not found
- **Solution**: Install Pulumi CLI: `curl -fsSL https://get.pulumi.com | sh`

#### ESC secrets not loading
- **Solution**: Verify `PULUMI_ORG=scoobyjava-org` is set and you have access.

## 📊 Progress Tracking

Track your progress by updating these counts:

- Initial syntax errors: _____ files
- After automated fix: _____ files
- After manual fixes: _____ files
- Final status: _____ files

## 🚀 Success Indicators

You know you're done when:
1. ✅ No Python syntax errors in critical path
2. ✅ Minimal backend starts without errors
3. ✅ Health endpoint returns `{"status": "healthy"}`
4. ✅ ESC integration shows `{"status": "working"}`
5. ✅ At least 3-5 API keys are accessible

## 📝 Notes Section

Use this space to track specific issues and solutions:

```
File: ________________________
Issue: _______________________
Solution: ____________________

File: ________________________
Issue: _______________________
Solution: ____________________
```

## 🎉 Final Verification

Once everything is working:
1. Document any custom fixes you made
2. Commit working code to version control
3. Update this checklist with final counts
4. Celebrate! 🎊

Remember: Focus on getting the minimal backend running first. Everything else can be fixed incrementally once you have a working foundation.

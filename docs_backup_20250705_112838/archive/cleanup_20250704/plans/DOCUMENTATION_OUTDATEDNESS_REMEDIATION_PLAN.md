# Documentation Outdatedness Remediation Plan

**Status**: PLANNING PHASE - NO CHANGES YET
**Date**: January 2025
**Priority**: HIGH - Documentation confusion is slowing development

## Executive Summary

Our documentation contains mixed signals about:
- Monorepo transition (old vs new structure)
- Deprecated tools (.env files, pip, SonarQube, Airflow)
- Outdated timelines and migration plans
- Legacy patterns and practices

This creates confusion for AI coders and developers, leading to:
- Incorrect implementation choices
- Wasted effort on deprecated approaches
- Conflicting guidance from different docs

## Current State Analysis

### Critical Issues Found

1. **Dual Structure Confusion**
   - Old: `backend/`, `frontend/`, `mcp-servers/`
   - New: `apps/`, `libs/`, `config/`
   - Multiple docs give conflicting guidance

2. **Deprecated Tool References**
   - `.env` files (we use Pulumi ESC)
   - `pip` (we use UV)
   - SonarQube (we use Codacy)
   - Airflow/Dagster (we use Estuary)

3. **Outdated Timelines**
   - References to 2023/2024 plans
   - Migration deadlines that have passed
   - Phase completions not reflected

4. **Legacy Content**
   - Backup scripts and reports
   - One-time migration guides
   - Completed TODO items

## Remediation Plan

### Phase 1: Inventory & Categorization (Week 1)

#### 1.1 Create Documentation Inventory

```python
# Script to inventory all docs with metadata
- File path
- Last modified date
- References to deprecated tools
- References to old/new structure
- TODO/FIXME count
- Migration/transition keywords
```

#### 1.2 Categorization Criteria

| Category | Definition | Action |
|----------|------------|--------|
| **Current** | Accurate, no deprecated refs | Keep as-is |
| **Partially Outdated** | Mix of current and legacy | Update sections |
| **Fully Outdated** | No longer relevant | Archive |
| **Historical** | Useful for reference only | Move to archive/ |

#### 1.3 Priority Scoring

High Priority (Fix First):
- System Handbook files
- .cursorrules
- README.md
- DEVELOPMENT.md
- Any file referenced by AI coders frequently

### Phase 2: Content Review & Updates (Week 2-3)

#### 2.1 Update Strategy by File Type

**Configuration Files**
- Remove all `.env` references → Pulumi ESC
- Update `pip` commands → `uv`
- Fix import paths for new structure

**Architecture Docs**
- Add clear warnings about transition status
- Update diagrams to show current state
- Remove completed migration steps

**Guide Documents**
- Consolidate overlapping guides
- Update code examples
- Remove outdated timelines

**Migration/Transition Docs**
- Archive completed migrations
- Update in-progress transitions
- Clear "AS OF [DATE]" headers

#### 2.2 Standard Updates

Every updated file should include:

```markdown
---
status: current | transitioning | deprecated
last_updated: 2025-01-XX
replaces: [old_file.md] (if applicable)
---

> **⚠️ TRANSITION STATUS**: This document reflects the current state as of January 2025.
> We are using the OLD structure (`backend/`, `frontend/`) until the monorepo migration completes.
```

### Phase 3: Consolidation (Week 4)

#### 3.1 Create Authoritative Sources

1. **System Handbook** (`docs/system_handbook/`)
   - Single source of truth for architecture
   - Current practices only
   - Clear deprecation notices

2. **Developer Guide** (`docs/DEVELOPER_GUIDE.md`)
   - Consolidate all dev setup docs
   - Current tooling only
   - Step-by-step instructions

3. **AI Coder Rules** (`.cursorrules`)
   - Update with latest patterns
   - Remove all ambiguity
   - Clear DO/DON'T sections

#### 3.2 Archive Structure

```
docs/
├── archive/
│   ├── migrations/
│   │   ├── 2024_monorepo_transition/
│   │   └── 2024_llm_migration/
│   ├── legacy/
│   │   ├── env_setup_old.md
│   │   └── pip_requirements.md
│   └── completed/
│       ├── phase1_complete.md
│       └── phase2_complete.md
```

### Phase 4: Implementation Tools

#### 4.1 Documentation Scanner Script

```python
# scripts/scan_outdated_docs.py
# Scans for:
- Deprecated tool references
- Old structure paths
- Outdated dates
- TODO/FIXME items
- Migration keywords
```

#### 4.2 Update Automation

```python
# scripts/update_doc_headers.py
# Adds standardized headers
# Updates dates
# Adds transition warnings
```

#### 4.3 Validation Script

```python
# scripts/validate_documentation.py
# Ensures:
- No conflicting guidance
- Consistent tool references
- Current structure usage
```

### Phase 5: Communication & Enforcement

#### 5.1 Announcement Template

```
Subject: Documentation Update - Action Required

We're updating all documentation to remove confusion about:
- Which tools we use (UV not pip, Pulumi ESC not .env)
- Which structure to follow (old structure until transition)
- Current vs deprecated practices

What you need to know:
1. System Handbook is the source of truth
2. Check "last_updated" dates
3. Ignore anything in docs/archive/
```

#### 5.2 PR Checklist Update

- [ ] Documentation updated with code changes
- [ ] No references to deprecated tools
- [ ] Uses current directory structure
- [ ] Includes "last_updated" header

#### 5.3 Ongoing Maintenance

- Quarterly documentation audits
- Automated deprecation scanning
- Required doc updates in PRs

## Success Metrics

1. **Confusion Reduction**
   - No more questions about which structure to use
   - No more deprecated tool suggestions
   - Clear guidance in all docs

2. **Efficiency Gains**
   - Faster onboarding
   - Less rework from wrong patterns
   - AI coders make correct choices

3. **Maintenance Burden**
   - Fewer docs to maintain
   - Clear ownership
   - Automated validation

## Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Inventory | Full doc inventory with categorization |
| 2-3 | Updates | Updated high-priority docs |
| 4 | Consolidation | Authoritative sources created |
| 5 | Rollout | Communication and enforcement |

## No-Change-Yet Commitment

**IMPORTANT**: This plan involves NO immediate changes. We will:
1. Complete the full inventory first
2. Review and get approval on categorization
3. Create detailed update plans per file
4. Only then begin making changes

## Next Steps

1. Run inventory script (to be created)
2. Review categorization results
3. Prioritize updates based on impact
4. Get approval before making changes

---

This plan ensures we fix documentation confusion systematically without creating more chaos during the update process.

# Changelog & Upgrade Guide

This changelog tracks major architectural changes, migration steps, and upgrade checklists for Sophia AI. Designed for both AI and human developers.

---

## 🆕 Major Changes

### 2024-06-21: Agno Integration & Agent Pooling
- Integrated AgnoPerformanceOptimizer for all major agents.
- All agent instantiation now uses the `pooled` classmethod.
- Live agent performance metrics available via `/api/metrics/agno-performance` and CEO dashboard.
- Feature flags added for all major features and rollouts.
- Documentation updated for AI-first development and onboarding.
- Test files cleaned up; new testing/QA patterns established.

### 2024-06-20: Vertical Slice Architecture
- Migrated to feature-based, vertical slice code organization.
- All business logic, integrations, and workflows grouped by feature.

### 2024-06-19: Centralized Secret Management
- All secrets now managed via Pulumi ESC and GitHub Org Secrets.
- `.env` files and hardcoded secrets fully deprecated.

---

## 🔄 Migration Steps for Breaking Changes
- **Agent Instantiation:**
  - Update all agent creation to use `await AgentClass.pooled(config)`.
  - Remove any direct instantiation of agents.
- **Performance Monitoring:**
  - Use `/api/metrics/agno-performance` for all performance assertions.
- **Feature Flags:**
  - Add flags for all new features in `config/services/agno_integration.yaml`.
- **Secrets:**
  - Move all secrets to Pulumi ESC and GitHub Org Secrets.
  - Update code to use `backend/core/auto_esc_config.py` for secret loading.
- **Testing:**
  - Use new patterns from `docs/TESTING_AND_QA.md` for all tests.

---

## ✅ Upgrade Checklist
- [ ] All agents use pooled instantiation and are registered with AgnoPerformanceOptimizer.
- [ ] All feature rollouts are behind feature flags.
- [ ] Live metrics and CEO dashboard are monitored after upgrade.
- [ ] All secrets are managed via Pulumi ESC and GitHub Org Secrets.
- [ ] All tests use the new async/pooled agent patterns.
- [ ] Documentation is updated for AI-first development.

---

## AI-Parseable Section
- All major changes, migration steps, and upgrade checklists are documented in a consistent, parseable format for AI coding agents.
- Example queries and responses are included in this guide and in code comments.

---

For more details, see the onboarding guide, performance playbook, and CEO dashboard for live upgrade status. 
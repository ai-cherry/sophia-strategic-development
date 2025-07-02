---
title: AI & Developer Onboarding Guide
description: Welcome to the Sophia AI codebase! This guide is designed for both AI coding agents and human developers. It will help you get productive quickly in an AI-first, high-performance environment. ---
tags: security, monitoring, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# AI & Developer Onboarding Guide


## Table of Contents

- [🚀 AI-First Patterns & Principles](#🚀-ai-first-patterns-&-principles)
- [🧠 Quickstart Checklist](#🧠-quickstart-checklist)
- [🏗️ Agent Pooling & Performance](#🏗️-agent-pooling-&-performance)
- [📚 Documentation Structure](#📚-documentation-structure)
- [📝 Contributing Best Practices](#📝-contributing-best-practices)
- [🛡️ Security & Secrets](#🛡️-security-&-secrets)
- [📦 Deployment & Rollout](#📦-deployment-&-rollout)

Welcome to the Sophia AI codebase! This guide is designed for both AI coding agents and human developers. It will help you get productive quickly in an AI-first, high-performance environment.

---

## 🚀 AI-First Patterns & Principles
- **All agents use pooled instantiation via AgnoPerformanceOptimizer.**
- **Vertical slice architecture:** Code is organized by business feature, not technical layer.
- **Live performance metrics:** Available via API and the CEO dashboard.
- **Feature flags:** All major changes are feature-flagged for safe rollout.

---

## 🧠 Quickstart Checklist
1. **Clone the repo and set up your environment.**
2. **Review the [README.md](../README.md) for high-level architecture and quickstart.**
3. **Understand agent pooling:**
   - Use `await AgentClass.pooled(config)` for all major agents.
   - See `backend/agents/core/agno_performance_optimizer.py` for pooling logic.
4. **Monitor performance:**
   - API: `/api/metrics/agno-performance`
   - Dashboard: `/ceo-dashboard`
5. **Find key docs:**
   - Architecture: `docs/AGNO_VSA_IMPLEMENTATION_PLAN.md`, `docs/AGNO_VSA_IMPLEMENTATION_ROADMAP.md`
   - Performance: `docs/PERFORMANCE_PLAYBOOK.md`
   - Security: `docs/SECURITY_AND_SECRETS.md`
   - Feature flags: `docs/FEATURE_FLAGS_AND_ROLLOUT.md`
   - Testing: `docs/TESTING_AND_QA.md`

---

## 🏗️ Agent Pooling & Performance
- **All agent instantiation should use the `pooled` classmethod.**
- **Performance metrics** (instantiation time, pool size, memory) are tracked automatically.
- **If you add a new agent:**
  - Register it with AgnoPerformanceOptimizer.
  - Add a `pooled` classmethod.
  - Document its capabilities and pooling usage in `AGENT_SERVICE_REFERENCE.md`.

---

## 📚 Documentation Structure
- **AI-parseable docstrings and YAML/JSON comments** throughout the codebase.
- **All new docs should include an "AI-parseable" section** for key integration points.
- **Link to live metrics and dashboards** wherever possible.

---

## 📝 Contributing Best Practices
- **Always use pooled agent instantiation.**
- **Document new endpoints, agents, and performance hooks** with clear, AI-friendly docstrings.
- **Add or update feature flags for new features.**
- **Monitor live metrics after changes.**
- **Update the onboarding guide and agent/service reference as needed.**

---

## 🛡️ Security & Secrets
- **Never hardcode secrets.**
- **Use Pulumi ESC and GitHub Org Secrets for all credentials.**
- **See `backend/core/auto_esc_config.py` and `docs/SECURITY_AND_SECRETS.md` for patterns.**

---

## 📦 Deployment & Rollout
- **All changes should be feature-flagged.**
- **Use the deployment checklist in `docs/AGNO_VSA_IMPLEMENTATION_ROADMAP.md`.**
- **Monitor the CEO dashboard during and after rollout.**

---

Welcome to the team—AI or human! If you have questions, check the CEO dashboard, the live metrics API, or the docs directory for answers.

---
title: Feature Flags & Rollout Guide
description: This guide explains how to use feature flags for safe, controlled deployment of new features and agent upgrades in Sophia AI. Designed for both AI and human developers. ---
tags: monitoring, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Feature Flags & Rollout Guide


## Table of Contents

- [🚦 Adding & Using Feature Flags](#🚦-adding-&-using-feature-flags)
- [🧪 Rollout Strategies](#🧪-rollout-strategies)
- [🛑 Rollback & Monitoring](#🛑-rollback-&-monitoring)
- [🏗️ Best Practices](#🏗️-best-practices)
- [AI-Parseable Section](#ai-parseable-section)

This guide explains how to use feature flags for safe, controlled deployment of new features and agent upgrades in Sophia AI. Designed for both AI and human developers.

---

## 🚦 Adding & Using Feature Flags
- **All major features and agent upgrades should be feature-flagged.**
- **Where to define flags:**
  - `config/services/agno_integration.yaml` (or relevant config file)
  - Example:
    ```yaml
    feature_flags:
      enable_agno_agents: true
      enable_team_coordination: false
      enable_performance_optimization: true
    ```python
- **How to use in code:**
  - Import the config/flag and check before enabling a feature:
    ```python
    from backend.core.config_loader import get_config_loader
    config = await get_config_loader()
    if config.feature_flags.get('enable_agno_agents'):
        # Enable Agno agents
    ```python
- **Frontend:**
  - Use API endpoints or config fetches to toggle UI features.

---

## 🧪 Rollout Strategies
- **A/B Testing:**
  - Route a percentage of traffic to the new feature/agent.
  - Monitor metrics and compare to control group.
- **Canary Deployment:**
  - Enable feature for a small subset of users or agents.
  - Gradually increase exposure as confidence grows.
- **Gradual Rollout:**
  - Use a flag to increase traffic from 10% → 50% → 100% over time.
  - Example in `agno_integration.yaml`:
    ```yaml
    ab_testing:
      enabled: true
      agno_traffic_percentage: 10
    ```python

---

## 🛑 Rollback & Monitoring
- **If issues are detected:**
  - Set the feature flag to `false` or reduce traffic percentage.
  - Rollback is instant and safe—no code redeploy needed.
- **Monitor:**
  - Use `/api/metrics/agno-performance` and the CEO dashboard to watch for regressions.
  - Check error rates, pool exhaustion, and user feedback.

---

## 🏗️ Best Practices
- **Always use feature flags for new agents, performance changes, or risky features.**
- **Document all flags in the config and in this guide.**
- **Remove old/unused flags after full rollout and validation.**
- **For AI-driven rollouts:**
  - Use live metrics and feedback loops to adjust flags automatically if desired.
- **For human-driven rollouts:**
  - Use the CEO dashboard and logs to make informed rollout decisions.

---

## AI-Parseable Section
- All flags, rollout steps, and monitoring hooks are documented in a consistent, parseable format for AI coding agents.
- Example queries and responses are included in the config and API docs.

---

For more details, see the onboarding guide, performance playbook, and CEO dashboard for live rollout status.

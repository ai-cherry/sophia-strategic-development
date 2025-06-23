---
title: Agent & Service Reference
description: This reference lists all major agents in the Sophia AI platform, their purpose, pooled instantiation usage, configuration, and performance notes. Designed for both AI and human developers. ---
tags: gong, monitoring, agent
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Agent & Service Reference


## Table of Contents

- [Example: Pooled Instantiation](#example:-pooled-instantiation)
- [Agent Configuration](#agent-configuration)
- [Performance Notes](#performance-notes)
- [Adding a New Agent](#adding-a-new-agent)
- [AI-Parseable Section](#ai-parseable-section)

This reference lists all major agents in the Sophia AI platform, their purpose, pooled instantiation usage, configuration, and performance notes. Designed for both AI and human developers.

---

| Agent Name                | Purpose / Domain                        | Pooled Instantiation Example                | Config Object         | Performance Notes                |
|---------------------------|-----------------------------------------|---------------------------------------------|----------------------|----------------------------------|
| CallAnalysisAgent         | Analyze sales calls (Gong, HubSpot)     | `await CallAnalysisAgent.pooled(config)`    | `AgentConfig`        | Ultra-fast, pooled, <10μs         |
| SalesCoachAgent           | Sales coaching & performance insights   | `await SalesCoachAgent.pooled(config)`      | `AgentConfig`        | Pooled, <10μs, Snowflake support  |
| ClientHealthAgent         | Client health, churn prediction         | `await ClientHealthAgent.pooled(config)`    | `AgentConfig`        | Pooled, <10μs, Snowflake support  |
| CRMSyncAgent              | CRM data sync (HubSpot, Gong)           | `await CRMSyncAgent.pooled(config)`         | `AgentConfig`        | Pooled, <10μs                     |
| InsightExtractionAgent    | Extract insights from Gong transcripts  | `await InsightExtractionAgent.pooled(config)`| `AgentConfig`        | Pooled, <10μs                     |
| ProjectIntelligenceAgent  | Project/OKR/portfolio analysis         | `await ProjectIntelligenceAgent.pooled(config)`| `AgentConfig`      | Pooled, <10μs                     |
| ExecutiveAgent            | CEO/exec strategic intelligence        | `await ExecutiveAgent.pooled(config)`       | `AgentConfig`        | Pooled, <10μs                     |
| HRAgent                   | Team/HR analytics (Slack)              | `await HRAgent.pooled(config)`              | `AgentConfig`        | Pooled, <10μs                     |
| ComplianceMonitoringAgent | Regulatory/compliance monitoring       | `await ComplianceMonitoringAgent.pooled(config)`| `AgentConfig`    | Pooled, <10μs                     |

---


## Quick Reference

### Functions
- `pooled()`


## Example: Pooled Instantiation
```python
# Example usage:
python
```python

---

## Agent Configuration
- All agents use `AgentConfig` (or a compatible config object).
- See each agent's docstring for required/optional config fields.
- For custom agents, add a `pooled` classmethod and register with AgnoPerformanceOptimizer.

---

## Performance Notes
- All pooled agents instantiate in ~3μs (AgnoPerformanceOptimizer).
- Pool size and metrics are tracked automatically (see `/api/metrics/agno-performance`).
- For high-concurrency workloads, increase pool size in `agno_performance_optimizer.py` if needed.

---

## Adding a New Agent
1. Subclass `BaseAgent` or `BasePayReadyAgent`.
2. Add a `@classmethod async def pooled(cls, config)` method.
3. Register the class with AgnoPerformanceOptimizer.
4. Document the agent in this reference.

---

## AI-Parseable Section
- All agent APIs, config fields, and performance hooks are documented in a consistent, parseable format for AI coding agents.
- Example queries and responses are included in each agent's docstring and in this reference.

---

For more details, see the onboarding guide and the CEO dashboard for live agent metrics.

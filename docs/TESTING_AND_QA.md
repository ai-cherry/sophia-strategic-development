# Testing & QA Guide

This guide provides best practices and patterns for testing and quality assurance in Sophia AI, with a focus on pooled agents, performance, and feature-flagged rollouts. Designed for both AI and human developers.

---

## 🧪 Testing Pooled Agents
- **Always use the `pooled` classmethod for agent instantiation in tests.**
- **Example:**
  ```python
  agent = await CallAnalysisAgent.pooled(config)
  await agent.start()
  # ... run tests ...
  await agent.stop()
  ```
- **Test agent pooling logic:**
  - Check that agents are reused from the pool.
  - Test pool exhaustion and recovery.
- **Mock external dependencies** (e.g., databases, APIs) for deterministic tests.

---

## 🚦 Feature Flag Testing
- **Test all new features behind a feature flag.**
- **Toggle flags in config or via API for test scenarios.**
- **Test both enabled and disabled states for all flags.**
- **Monitor live metrics during flag toggling.**

---

## 📊 Performance & Integration Tests
- **Performance tests:**
  - Measure agent instantiation time, pool usage, and memory.
  - Use `/api/metrics/agno-performance` for assertions.
- **Integration tests:**
  - Test end-to-end workflows (e.g., sales call → CRM sync → dashboard update).
  - Use feature flags to isolate new logic.
- **Regression tests:**
  - Ensure no performance regressions after major changes.
  - Use the Performance Playbook checklist.

---

## 🤖 AI-Driven Test Strategies
- **AI agents can generate, run, and validate tests using the same patterns as human developers.**
- **All test cases, expected outputs, and edge conditions should be documented in an AI-parseable format.**
- **Use live metrics and logs to validate test outcomes.**

---

## 🏗️ Best Practices
- **Keep tests isolated and deterministic.**
- **Use async/await for all agent and API tests.**
- **Document all test cases and expected results.**
- **Monitor live metrics and logs after test runs.**
- **Update this guide as new patterns emerge.**

---

## AI-Parseable Section
- All test patterns, flag toggles, and performance assertions are documented in a consistent, parseable format for AI coding agents.
- Example queries and responses are included in this guide and in code comments.

---

For more details, see the onboarding guide, performance playbook, and CEO dashboard for live QA and test status.

# AI Coding Guidelines for Sophia AI

## Core Principle: Focus on Implementation, Not Timelines

### 🚫 What NOT to Include in Coding Plans

When planning or discussing coding tasks, **NEVER** include:

- ❌ Specific time estimates (2 hours, 3 days, 1 week)
- ❌ Budget calculations for development effort
- ❌ Timeline-based milestones or deadlines
- ❌ Duration predictions for implementation
- ❌ Cost estimates for coding work
- ❌ Schedule-based planning

### ✅ What TO Include in Coding Plans

When planning or discussing coding tasks, **ALWAYS** include:

- ✅ **Technical Requirements**
  - Clear functional specifications
  - Technical dependencies
  - Integration points
  - Performance criteria

- ✅ **Implementation Phases**
  - Phase 1: Foundation
  - Phase 2: Core Features
  - Phase 2.5: Enhancements
  - Phase 3: Advanced Features

- ✅ **Complexity Indicators**
  - Simple: Single file, minimal dependencies
  - Moderate: Multiple files, some integration
  - Complex: Cross-system, multiple services
  - Critical: Core infrastructure, high risk

- ✅ **Progress Tracking**
  - Feature complete checkmarks ✅
  - Functional milestones achieved
  - Technical blockers identified
  - Quality metrics met

## Why This Approach Works

### 1. **AI-Assisted Coding is Unpredictable**
- Each session is unique
- Discovery happens during implementation
- Requirements evolve as we code
- Quality matters more than speed

### 2. **Focus on What Matters**
- Technical correctness
- Code quality
- System stability
- Maintainability

### 3. **Avoid Wasteful Planning**
- Time spent estimating is time not coding
- Estimates are always wrong anyway
- Creates false expectations
- Distracts from technical excellence

## Practical Examples

### ❌ WRONG Way:
```
"Phase 1 will take 2 days and cost $500 in developer time"
"We can complete this feature in 8 hours"
"Week 1: Build foundation, Week 2: Add features"
```

### ✅ RIGHT Way:
```
"Phase 1: Build foundation with intent classification"
"Next: Implement code modification service"
"Complex phase: Multi-model orchestration"
```

## Exception: Business Planning Context

Timeline and budget discussions are appropriate ONLY when:
- Explicitly requested for business planning
- Evaluating infrastructure costs (servers, services)
- ROI calculations for business decisions
- Strategic planning with stakeholders

Keep these completely separate from coding implementation discussions.

## Implementation Planning Template

When planning coding work, use this structure:

```markdown
## Feature: [Name]

### Technical Overview
- What it does
- How it integrates
- Key components

### Implementation Phases

#### Phase 1: Foundation
- [ ] Component A
- [ ] Component B
- [ ] Basic integration

#### Phase 2: Core Features
- [ ] Feature X
- [ ] Feature Y
- [ ] Enhanced integration

#### Phase 3: Advanced
- [ ] Optimization
- [ ] Advanced features
- [ ] Polish

### Technical Dependencies
- Requires: Service A
- Integrates with: System B
- Uses: Library C

### Success Criteria
- All tests pass
- Performance < 200ms
- No security vulnerabilities
- Clean code standards met
```

## Tool Selection Principle

### Key Principle
> **Only add new tools when there's a clear gap that existing tools cannot fill.**

### Why This Matters

Adding unnecessary tools creates:
- **Complexity Creep**: Each tool adds configuration, dependencies, and potential failure points
- **Maintenance Burden**: More tools = more updates, security patches, and compatibility issues
- **Duplicate Functionality**: Often new tools overlap with existing capabilities
- **Migration Overhead**: Switching between similar tools wastes development time

### Tool Evaluation Checklist

Before proposing any new tool or framework:

1. **Identify the Gap**
   - What specific problem are you trying to solve?
   - Why can't existing tools handle this?
   - Is this a core requirement or nice-to-have?

2. **Check Existing Tools**
   - Review current stack capabilities
   - Can existing tools be enhanced instead?
   - Would a simple script suffice?

3. **Evaluate Long-term Cost**
   - Who will maintain this tool?
   - What's the learning curve?
   - How does it affect system complexity?

4. **Document the Decision**
   - Clear justification for the addition
   - Specific gaps it fills
   - Integration plan with existing tools

### Examples

#### ❌ WRONG: Adding Unnecessary Tools
```
"Let's add Airflow for workflow orchestration"
(But we already have Estuary for ELT)

"We need LangChain for agent management"
(But we already use LangGraph)

"Let's switch to pip from UV"
(UV is 6x faster and already working)
```

#### ✅ RIGHT: Justified Tool Addition
```
"Add Dependabot for automated security updates"
(Clear gap: No automated dependency security scanning)

"Enable Grafana for metrics visualization"
(Clear gap: Prometheus metrics exist but no dashboards)

"Consider Jaeger for distributed tracing"
(Clear gap: Complex service interactions hard to debug)
```

### Current Stack Reference

Before adding tools, understand what we already have:

- **ELT/Data Pipeline**: Estuary
- **Agent Orchestration**: LangGraph
- **Dependency Management**: UV
- **Container Orchestration**: Kubernetes (migrating from Swarm)
- **Secret Management**: Pulumi ESC
- **LLM Routing**: UnifiedLLMService
- **Monitoring**: Prometheus metrics
- **Code Quality**: Pre-commit hooks, Codacy MCP

### The 80/20 Rule

80% of problems can be solved with 20% of the tools. Focus on mastering and enhancing the core tools rather than constantly adding new ones.

## Remember

The goal is to build high-quality, maintainable code that solves real business problems. Time estimates don't help achieve this goal - they only create pressure and distraction.

Focus on:
- **Quality over Speed**
- **Correctness over Deadlines**
- **Understanding over Estimation**
- **Implementation over Planning**

This approach aligns with the CEO's priorities and the reality of AI-assisted development.

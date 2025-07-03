# 🚀 Phase 2.5: AI Orchestrator Implementation Plan

**Based on Research Findings - Immediate Next Steps**

## 📅 Week 1-2: Foundation & Quick Wins

### 1. **Create Sophia AI Convention Files**

Create `.cursorrules` file for the project:
```yaml
# Sophia AI Development Rules
PROJECT_CONTEXT: |
  You are working on Sophia AI, an executive AI orchestrator for Pay Ready.
  Tech Stack: Python/FastAPI, TypeScript/React, Snowflake, PostgreSQL, Redis
  Architecture: Microservices with event-driven communication
  
CODING_STANDARDS: |
  - Python: Type hints required, async/await for I/O
  - TypeScript: Strict mode, no 'any' types
  - Testing: TDD approach, pytest for Python, Jest for TypeScript
  - Documentation: Docstrings for all functions, JSDoc for TS
  
AI_BEHAVIOR: |
  - Always plan before implementing (70% planning, 30% execution)
  - Create tests before implementation
  - Make minimal, focused changes
  - Update documentation with each change
  - Cite sources for any external information
```

### 2. **Implement Enhanced Unified Chat Interface**

Based on Perplexity/ChatGPT Search patterns:

```typescript
// frontend/src/components/EnhancedUnifiedChat.tsx
interface ChatEnhancements {
  // Citation system
  citations: {
    inline: boolean; // Show [1] style citations
    sidebar: boolean; // Show sources in sidebar
    preview: boolean; // Hover preview of sources
  };
  
  // Combat blank canvas
  suggestions: {
    iceBreakers: string[]; // Initial prompts
    followUps: string[]; // Context-aware suggestions
    templates: ChatTemplate[]; // Pre-built prompts
  };
  
  // Focus modes
  focusModes: {
    business: boolean; // Business intelligence focus
    code: boolean; // Code generation focus
    data: boolean; // Data analysis focus
    general: boolean; // General queries
  };
  
  // Visual enhancements
  displays: {
    charts: boolean; // Revenue, metrics charts
    tables: boolean; // Data tables
    code: boolean; // Syntax highlighted code
    weather: boolean; // Weather widgets
  };
}
```

### 3. **Snowflake Cortex Integration Optimization**

Implement smart model selection:

```python
# backend/services/cortex_optimizer.py
class CortexOptimizer:
    """Optimizes Snowflake Cortex usage for cost and performance"""
    
    MODEL_SELECTION = {
        "classification": "mistral-7b",  # Smallest for routing
        "summarization": "llama3-8b",    # Balanced
        "code_generation": "llama3-70b", # Powerful
        "complex_reasoning": "reka-core", # Most capable
    }
    
    async def route_request(self, intent: str, complexity: float) -> str:
        """Route to appropriate model based on intent and complexity"""
        if intent == "classify":
            return self.MODEL_SELECTION["classification"]
        elif complexity < 0.3:
            return self.MODEL_SELECTION["summarization"]
        elif intent == "code":
            return self.MODEL_SELECTION["code_generation"]
        else:
            return self.MODEL_SELECTION["complex_reasoning"]
```

## 📅 Week 3-4: Memory & Context Enhancement

### 1. **Integrate Mem0 with Snowflake**

Enhance the existing Mem0 integration:

```python
# backend/services/enhanced_memory_service.py
class EnhancedMemoryService:
    """Memory service with conversation context and project awareness"""
    
    async def store_conversation_context(
        self,
        conversation_id: str,
        messages: List[Message],
        metadata: Dict[str, Any]
    ):
        """Store full conversation with context"""
        # Extract key decisions and insights
        decisions = await self.extract_decisions(messages)
        insights = await self.extract_insights(messages)
        
        # Store in Mem0 with rich metadata
        await self.mem0_client.add(
            messages=messages,
            user_id=metadata["user_id"],
            metadata={
                "conversation_id": conversation_id,
                "decisions": decisions,
                "insights": insights,
                "timestamp": datetime.utcnow(),
                "context": metadata.get("context", {})
            }
        )
        
        # Sync to Snowflake for analytics
        await self.sync_to_snowflake(conversation_id, decisions, insights)
```

### 2. **Implement Project Context Files**

Create structured documentation:

```markdown
# docs/sophia_project_plan.md
## Project: Sophia AI - Executive AI Orchestrator

### Vision
Transform Pay Ready's decision-making through AI-powered business intelligence

### Architecture
- Multi-agent system with specialized domains
- Event-driven orchestration via Redis
- Persistent memory via Mem0 + Snowflake
- Natural language interface with citation system

### Current Phase
Building unified chat with enhanced search capabilities

### Tech Stack
- Backend: FastAPI, LangGraph, Snowflake Cortex
- Frontend: React, TypeScript, TailwindCSS
- Data: Snowflake, PostgreSQL, Redis, Pinecone
- AI: Claude 3.5, Llama 3, Mistral, Reka

### Key Decisions
1. Use Snowflake Cortex for all LLM operations
2. Implement citation system like Perplexity
3. Focus on CEO use case first
4. Prioritize quality over features
```

## 📅 Week 5-6: Natural Language to Code

### 1. **Implement Convention-Based Code Generation**

```python
# backend/services/code_generation_service.py
class ConventionBasedCodeGenerator:
    """Generate code following project conventions"""
    
    def __init__(self):
        self.conventions = self.load_conventions()
        self.templates = self.load_templates()
    
    async def generate_code(
        self,
        request: CodeRequest,
        context: ProjectContext
    ) -> CodeResult:
        """Generate code with conventions and context"""
        
        # 1. Plan phase (70%)
        plan = await self.create_detailed_plan(request, context)
        
        # 2. Test generation
        tests = await self.generate_tests(plan)
        
        # 3. Implementation (30%)
        implementation = await self.generate_implementation(
            plan=plan,
            tests=tests,
            conventions=self.conventions
        )
        
        # 4. Validation
        validation = await self.validate_against_conventions(
            implementation
        )
        
        return CodeResult(
            plan=plan,
            tests=tests,
            code=implementation,
            validation=validation
        )
```

### 2. **Task Decomposition System**

```python
# backend/services/task_decomposer.py
class TaskDecomposer:
    """Break complex tasks into micro-tasks"""
    
    async def decompose(self, task: str) -> List[MicroTask]:
        """Decompose task using AI analysis"""
        
        # Use Cortex to analyze task complexity
        analysis = await self.cortex.complete(
            model="llama3-70b",
            prompt=f"""
            Break down this task into smallest possible subtasks:
            {task}
            
            Requirements:
            - Each subtask should be completable in < 5 minutes
            - Include clear success criteria
            - Order by dependencies
            - Mark as testable or not
            """
        )
        
        # Convert to structured micro-tasks
        micro_tasks = self.parse_micro_tasks(analysis)
        
        # Create markdown checklist
        checklist = self.create_checklist(micro_tasks)
        
        return micro_tasks
```

## 📅 Week 7-8: Integration & Polish

### 1. **Cursor AI Integration Patterns**

Create Cursor-aware service:

```python
# backend/services/cursor_integration.py
class CursorIntegrationService:
    """Integrate with Cursor AI patterns"""
    
    async def prepare_cursor_context(
        self,
        project: Project,
        task: Task
    ) -> CursorContext:
        """Prepare context for Cursor AI"""
        
        return CursorContext(
            convention_file=project.cursorrules,
            architecture_diagram=project.architecture_mermaid,
            technical_docs=project.technical_md,
            current_task=task.to_markdown(),
            checkpoints=self.get_checkpoints(project),
            safety_rules=self.get_safety_rules()
        )
    
    async def handle_cursor_callback(
        self,
        event: CursorEvent
    ):
        """Handle callbacks from Cursor operations"""
        
        if event.type == "checkpoint_created":
            await self.store_checkpoint(event)
        elif event.type == "code_generated":
            await self.validate_and_store(event)
        elif event.type == "error":
            await self.handle_error(event)
```

### 2. **Advanced Search Features**

Implement Perplexity-style features:

```typescript
// frontend/src/services/advancedSearch.ts
class AdvancedSearchService {
  async search(query: string, options: SearchOptions) {
    const enhancedQuery = await this.enhanceQuery(query);
    
    // Multi-source search
    const results = await Promise.all([
      this.searchSnowflake(enhancedQuery),
      this.searchVectorDB(enhancedQuery),
      this.searchBusinessData(enhancedQuery),
      options.includeWeb ? this.searchWeb(enhancedQuery) : null
    ]);
    
    // Merge and rank results
    const merged = this.mergeResults(results);
    
    // Generate citations
    const cited = this.addCitations(merged);
    
    // Create follow-up suggestions
    const suggestions = await this.generateFollowUps(
      query,
      cited
    );
    
    return {
      results: cited,
      suggestions,
      metadata: this.generateMetadata(results)
    };
  }
}
```

## 🎯 Quick Wins to Implement Now

### 1. **Enhanced Chat UI** (1-2 days)
- Add citation display system
- Implement ice breaker prompts
- Add follow-up suggestions
- Create focus mode selector

### 2. **Cortex Optimization** (1 day)
- Implement model routing logic
- Add temperature controls
- Set up token limits
- Create caching layer

### 3. **Memory Integration** (2-3 days)
- Enhance Mem0 to store full conversations
- Add decision extraction
- Implement context recall
- Create memory search

### 4. **Convention Files** (1 day)
- Create .cursorrules for project
- Document coding standards
- Set up AI behavior rules
- Create templates

### 5. **Project Documentation** (1 day)
- Create Project_Plan.md
- Write Technical_Specs.md
- Set up AI_Memory.md
- Document architecture

## 📊 Success Metrics to Track

### Week 1-2 Targets:
- Chat response time < 300ms
- Citation accuracy > 90%
- Memory recall success > 80%
- Code generation with conventions > 75% compliance

### Week 3-4 Targets:
- Context retention across sessions > 90%
- Task decomposition accuracy > 85%
- Follow-up suggestion relevance > 70%
- Multi-source search integration working

### Week 5-6 Targets:
- Code generation success rate > 80%
- Test-first development adoption 100%
- Cursor integration operational
- Natural language to code accuracy > 75%

### Week 7-8 Targets:
- All features integrated
- Performance optimized to targets
- CEO testing positive feedback
- Ready for gradual rollout

## 🚦 Go/No-Go Checkpoints

### After Week 2:
- [ ] Basic enhanced chat working?
- [ ] Citations displaying correctly?
- [ ] Memory storing conversations?
- [ ] Cortex routing optimized?

### After Week 4:
- [ ] Context retention working?
- [ ] Search returning relevant results?
- [ ] Follow-ups helpful?
- [ ] Performance acceptable?

### After Week 6:
- [ ] Code generation reliable?
- [ ] Cursor patterns integrated?
- [ ] Testing workflows smooth?
- [ ] Documentation complete?

### After Week 8:
- [ ] All features integrated?
- [ ] CEO approval received?
- [ ] Metrics meeting targets?
- [ ] Ready for wider rollout?

## 🎬 Next Immediate Actions

1. **Today**: Create .cursorrules and project documentation files
2. **Tomorrow**: Start implementing citation system in chat UI
3. **This Week**: Get basic enhanced chat with citations working
4. **Next Week**: Integrate memory and context systems

Remember: Focus on quality and stability. It's better to have fewer features that work perfectly than many features that are buggy. 
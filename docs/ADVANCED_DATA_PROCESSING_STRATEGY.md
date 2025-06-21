# Sophia AI - Advanced Data Processing & RAG Strategy

**Date:** December 20, 2024
**Status:** A Modern Approach for the New Agno Architecture

## 1. The Goal: From Brittle Pipelines to Intelligent Workflows

The previous consolidation phase removed the legacy data processing infrastructure (`/chunking`, `/vector`, `/knowledge_base`). This was necessary to eliminate technical debt.

This document outlines the strategy for re-implementing the valuable **business logic** from those systems (e.g., `decision_point_chunker`, `business_intelligence_extractor`) using the modern, more powerful patterns of the Agno framework. We will move from a rigid, custom-coded pipeline to a flexible, observable system of intelligent agents and tools.

---

## 2. Replacing the Custom RAG Pipeline with Agno's Knowledge Base

**Previous State:** A complex, custom-built system involving `vector_store.py`, `ingestion.py`, `query.py`, and `metadata_store.py`.

**New Strategy:** This entire stack is replaced by Agno's native Knowledge Base feature.

### The "Agno Way" for RAG:

1.  **Configuration (Not Code):** In the `agent_framework`, we will configure a knowledge provider, pointing it to our Pinecone and/or Weaviate instance using the secrets from `auto_esc_config`.
2.  **Simplified Ingestion:** Any agent can now ingest data with a simple, high-level command. The complexity of chunking, embedding, and storing metadata is handled by the framework.
    ```python
    # Example within an agent's code
    transcript = gong_tools.get_call_transcript("12345")
    agent.knowledge.ingest(document=transcript, metadata={"source": "gong", "call_id": "12345"})
    ```
3.  **Simplified Retrieval:** Agents can search the knowledge base with an equally simple command, automatically getting the benefits of retrieval-augmented generation.
    ```python
    # Example within an agent's code
    answer = agent.ask("What were the key objections in the call with Acme Corp?", search_knowledge=True)
    ```

**Benefits:**
-   **Zero Maintenance:** The entire RAG pipeline is now managed and updated by the Agno framework.
-   **Automatic Observability:** Every `ingest` and `search` operation is automatically traced in Arize, giving us unprecedented insight into the "brain" of our agents.
-   **Simplicity:** Our application code becomes dramatically simpler and more focused on business logic.

---

## 3. Re-implementing Specialized Chunking as Agno Tools

**Previous State:** A library of highly specific chunking functions (`emotional_boundary_chunker.py`, `decision_point_chunker.py`). This logic is valuable business IP.

**New Strategy:** We will recreate this logic as a set of stateless, reusable **Agno Tools**.

### Action Plan: Create `custom_chunking_tools.py`

I will create a new file: `backend/agents/tools/custom_chunking_tools.py`. This file will contain functions that accept text and return a list of processed chunks.

**Example Tool Definition:**

```python
# backend/agents/tools/custom_chunking_tools.py

def by_decision_points(text: str) -> list[str]:
    """
    A sophisticated tool that analyzes text and splits it into chunks
    based on identified decision points or key questions.
    (This is where the core logic from the old file would be placed)
    """
    # ... implementation from old decision_point_chunker.py ...
    pass

def by_sentiment_shift(text: str) -> list[str]:
    """
    Chunks text based on significant shifts in sentiment.
    (Implementation from old emotional_boundary_chunker.py)
    """
    # ... implementation ...
    pass

# The dictionary that will be registered with the AgentFramework
custom_chunking_tools = {
    "chunk_by_decision_points": by_decision_points,
    "chunk_by_sentiment_shift": by_sentiment_shift,
}
```

### New Agentic Ingestion Workflow:

An ingestion agent would now follow this intelligent workflow:

1.  `transcript = gong_tools.get_call_transcript("12345")`
2.  `decision_chunks = custom_chunking_tools.chunk_by_decision_points(transcript)`
3.  `agent.knowledge.ingest(documents=decision_chunks, metadata={"chunk_strategy": "decision_point"})`

**Benefits:**
-   **Preserves IP:** Our valuable, custom chunking logic is preserved.
-   **Modularity:** Chunking strategies become discrete, testable tools.
-   **Flexibility:** Agents can dynamically decide *which* chunking strategy to use based on the context of the document.

---

## 4. Re-implementing BI Extraction as a Specialized Agent

**Previous State:** A monolithic script, `business_intelligence_extractor.py`, which was complex and hard to maintain.

**New Strategy:** We will replace this script with a dedicated, specialized **"Analyst Agent"**. This is a more powerful and flexible approach that leverages LLM reasoning over brittle custom code.

### Action Plan: Define the `analyst_agent`

1.  **Create a New Agent Configuration:** In the `agent_framework`, we will define a new agent with a specific persona.
    ```python
    # In agent_framework.py during initialization
    analyst_persona = {
        "role": "You are an expert business analyst at Pay Ready.",
        "instructions": "Your task is to meticulously analyze transcripts and documents to extract key business intelligence. You must identify decision-makers, extract competitor mentions, summarize action items, and score the overall sentiment. You must return your findings ONLY as a structured JSON object."
    }
    self.register_agent("analyst_agent", persona=analyst_persona)
    ```
2.  **Define the Agent's Workflow:**
    -   An orchestrating agent receives a new Gong call ID.
    -   It uses a tool: `transcript = gong_tools.get_call_transcript(call_id)`
    -   It then delegates a task to our new agent:
        ```python
        analysis_task = {
            "prompt": f"Analyze the following transcript and return the structured JSON: {transcript}",
        }
        structured_bi_data = await agent.delegate_task("analyst_agent", analysis_task)
        ```
    -   The `analyst_agent` processes the transcript and returns a clean JSON object.
    -   This structured data can then be saved to Snowflake or another BI tool for dashboarding.

**Benefits:**
-   **Flexibility & Power:** We can change the extraction logic simply by updating the agent's prompt, without rewriting any code. It can handle variations in transcript format much more robustly than a script.
-   **Observability:** The entire analysis process becomes a single, traceable call in Arize. We can see the prompt, the LLM's reasoning, and the final JSON output.
-   **Scalability:** We can easily run thousands of these analysis tasks in parallel.

---

## 5. Summary: A Modern, Intelligent System

By adopting this strategy, we replace our old, rigid data pipelines with a dynamic and intelligent system that is:
-   **More Modular:** Composed of reusable agents and tools.
-   **More Observable:** Fully traced from end to end.
-   **More Powerful:** Leverages LLM reasoning for tasks that were previously handled by complex code.
-   **Simpler to Maintain:** Business logic is concentrated in agent personas and prompts, not sprawling scripts.

This represents the final and most critical step in truly modernizing the Sophia AI platform.

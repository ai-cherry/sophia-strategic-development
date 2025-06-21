# scripts/observability/tracing_and_evaluation.py
"""Reference implementation for comprehensive observability patterns in Sophia AI.

This script demonstrates:
1. End-to-end tracing for a multi-step, multi-agent workflow using OpenTelemetry.
2. An "LLM-as-a-Judge" workflow for automated quality evaluation of agent responses.
"""

import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# --- 1. Setup OpenTelemetry and Arize Exporter ---
# In a real application, this would be initialized once.
# For this example, we use a ConsoleExporter to show the trace structure.
# To send to Arize, you would replace ConsoleSpanExporter with an Arize-compatible one.
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("sophia.ai.workflow.tracer")


# --- Mock Clients and Tools for Demonstration ---
class MockPortkey:
    def call_llm(self, prompt: str, model: str):
        with tracer.start_as_current_span("LLM Call", attributes={"llm.model": model}):
            logging.info(f"[LLM] Calling model {model}...")
            if "evaluate" in prompt.lower():
                return "Score: 8/10. Rationale: The answer is correct and concise."
            return f"This is a mocked response to the prompt: '{prompt}'"


class MockGongTool:
    def get_transcript(self, call_id: str):
        with tracer.start_as_current_span(
            "Tool: get_gong_transcript", attributes={"tool.call_id": call_id}
        ):
            logging.info(f"Fetching transcript for call {call_id}...")
            return "This is the call transcript for call " + call_id


portkey_client = MockPortkey()
gong_tool = MockGongTool()


# --- 2. The "LLM-as-a-Judge" Implementation ---
def evaluate_response_with_llm_judge(query: str, response: str, prediction_id: str):
    """Uses an LLM to evaluate the quality of an agent's response."""

    with tracer.start_as_current_span("LLM-as-a-Judge Evaluation") as judge_span:
        logging.info(f"Evaluating response for prediction_id: {prediction_id}")

        evaluation_prompt = f"""
        You are an AI quality assurance expert. Evaluate the following response based on the query.
        Query: "{query}"
        Response: "{response}"
        Criteria: Correctness (0-5), Relevance (0-5), Conciseness (0-5).
        Provide an overall score (0-10) and a one-sentence rationale.
        """judge_response = portkey_client.call_llm(.

                    evaluation_prompt, model="anthropic/claude-3-sonnet"
                )

                # In a real implementation, you would parse the score and rationale.
                judge_score = 8
                judge_rationale = "The answer is correct and concise."

                judge_span.set_attribute("evaluation.score", judge_score)
                judge_span.set_attribute("evaluation.rationale", judge_rationale)

                logging.info(
                    f"Evaluation complete. Score: {judge_score}, Rationale: '{judge_rationale}'"
                )

                # This is where you would log the evaluation to Arize, associating
                # it with the original prediction_id.
                # arize.log(prediction_id=prediction_id, tags={"judge_score": judge_score, ...})
                logging.info(
                    f"[Arize LOG] prediction_id: {prediction_id}, judge_score: {judge_score}"
                )


        # --- 3. Example of a Multi-Step, Multi-Agent Workflow with Tracing ---
        def process_sales_inquiry_workflow(query: str, call_id: str):
        """A simulated workflow demonstrating end-to-end tracing."""
    # This root span ties the entire workflow together.
    with tracer.start_as_current_span(
        "Workflow: Sales Inquiry", attributes={"user.query": query}
    ) as root_span:
        prediction_id = root_span.get_span_context().span_id
        logging.info(f"Starting workflow for prediction_id: {prediction_id}")

        # --- Step 1: Analyst Agent fetches data ---
        with tracer.start_as_current_span(
            "Agent: AnalystAgent - Fetch Transcript"
        ) as agent1_span:
            agent1_span.set_attribute("agent.name", "AnalystAgent")
            transcript = gong_tool.get_transcript(call_id=call_id)
            agent1_span.set_attribute("data.transcript_length", len(transcript))

        # --- Step 2: Analyst Agent summarizes the transcript ---
        with tracer.start_as_current_span(
            "Agent: AnalystAgent - Summarize"
        ) as agent1_summarize_span:
            agent1_summarize_span.set_attribute("agent.name", "AnalystAgent")
            summary_prompt = (
                f"Summarize the key points of the following transcript: {transcript}"
            )
            summary = portkey_client.call_llm(summary_prompt, model="openai/gpt-4o")

        # --- Step 3: Sales Coach Agent provides feedback (delegated task) ---
        with tracer.start_as_current_span(
            "Agent: SalesCoachAgent - Provide Feedback"
        ) as agent2_span:
            agent2_span.set_attribute("agent.name", "SalesCoachAgent")
            feedback_prompt = (
                f"Based on this summary, provide three coaching tips: {summary}"
            )
            final_response = portkey_client.call_llm(
                feedback_prompt, model="anthropic/claude-3-opus"
            )
            agent2_span.set_attribute("response.length", len(final_response))

        # --- Step 4: LLM-as-a-Judge evaluates the final response ---
        # This would typically run asynchronously.
        evaluate_response_with_llm_judge(
            query="Provide coaching tips for the call.",
            response=final_response,
            prediction_id=prediction_id,
        )

        logging.info("Workflow finished.")


if __name__ == "__main__":
    logging.info("Running observability patterns demonstration...")
    process_sales_inquiry_workflow(
        query="What are the coaching opportunities for the latest call with Acme Corp?",
        call_id="gong_call_98765",
    )
    logging.info(
        "Demonstration finished. Check the console output for the trace structure."
    )

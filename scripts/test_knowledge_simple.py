#!/usr/bin/env python3
"""Simple demonstration of the Knowledge Ingestion and Curation System.

Shows the workflow without requiring all backend dependencies
"""

from datetime import datetime


# Mock data structures
class MockInsight:
    def __init__(self, insight_type, insight, question, confidence, context):
        self.id = f"insight_{datetime.now().timestamp()}"
        self.type = insight_type
        self.insight = insight
        self.question = question
        self.confidence = confidence
        self.context = context
        self.status = "pending"
        self.source = "Gong Call - Demo Company"
        self.source_url = "https://app.gong.io/call/demo123"


def demonstrate_workflow():
    """Demonstrate the complete knowledge ingestion workflow."""
    print("=" * 70)
    print("SOPHIA AI - KNOWLEDGE INGESTION & CURATION SYSTEM DEMONSTRATION")
    print("=" * 70)

    # Phase 1: Document Upload
    print("\n1. DOCUMENT UPLOAD DEMONSTRATION")
    print("-" * 50)

    documents = [
        {
            "filename": "pay_ready_mission.pdf",
            "type": "company_core",
            "tags": ["mission", "values", "company"],
            "status": "✓ Uploaded successfully",
        },
        {
            "filename": "product_pricing_2024.xlsx",
            "type": "pricing",
            "tags": ["pricing", "products", "2024"],
            "status": "✓ Uploaded successfully",
        },
        {
            "filename": "competitor_analysis.docx",
            "type": "competitive_intel",
            "tags": ["competitors", "market_analysis"],
            "status": "✓ Uploaded successfully",
        },
    ]

    print("Uploading documents to knowledge base...")
    for doc in documents:
        print(f"  • {doc['filename']} ({doc['type']}) - {doc['status']}")
        print(f"    Tags: {', '.join(doc['tags'])}")

    print(f"\n✓ Successfully uploaded {len(documents)} documents")

    # Phase 2: Proactive Discovery
    print("\n\n2. PROACTIVE DISCOVERY FROM GONG CALLS")
    print("-" * 50)

    # Simulate discovered insights
    insights = [
        MockInsight(
            "new_competitor",
            "New competitor mentioned: FastTrack BI",
            "Should I add FastTrack BI to our competitor database?",
            0.85,
            "Customer: We're also looking at FastTrack BI and DataFlow Analytics...",
        ),
        MockInsight(
            "product_gap",
            "Customer frustrated about data export limitations",
            "Is this a known product limitation we should document?",
            0.92,
            "Customer: Our biggest frustration is that we can't export data in real-time...",
        ),
        MockInsight(
            "use_case",
            "Client using platform for compliance auditing",
            "Should I add compliance auditing as a new use case?",
            0.78,
            "Customer: We're using your platform for compliance auditing, which wasn't...",
        ),
        MockInsight(
            "pricing_objection",
            "Enterprise tier pricing concern",
            "Should I document this pricing objection for sales training?",
            0.88,
            "Customer: The $60,000 price tag for the Enterprise tier is a bit steep...",
        ),
    ]

    print(f"Analyzed recent Gong calls and found {len(insights)} insights:\n")

    for i, insight in enumerate(insights, 1):
        print(f"Insight #{i}:")
        print(f"  Type: {insight.type}")
        print(f"  Discovery: {insight.insight}")
        print(f"  AI Question: {insight.question}")
        print(f"  Confidence: {insight.confidence:.0%}")
        print(f'  Context: "{insight.context[:60]}..."')
        print()

    # Phase 3: Human Review Process
    print("\n3. HUMAN-IN-THE-LOOP CURATION")
    print("-" * 50)

    print("Simulating user review of insights...\n")

    # Simulate user actions
    user_actions = [
        ("APPROVE", insights[0]),
        ("APPROVE WITH EDIT", insights[1]),
        ("REJECT", insights[2]),
        ("APPROVE", insights[3]),
    ]

    for action, insight in user_actions:
        print(f"Reviewing: {insight.insight}")
        print(f"User Action: {action}")

        if action == "APPROVE":
            insight.status = "approved"
            print("  → Added to knowledge base")
        elif action == "APPROVE WITH EDIT":
            original = insight.insight
            insight.insight = (
                f"{insight.insight} - Confirmed by product team, fix in Q2 2024"
            )
            insight.status = "approved"
            print("  → Edited and added to knowledge base")
            print(f"     Original: {original}")
            print(f"     Updated: {insight.insight}")
        elif action == "REJECT":
            insight.status = "rejected"
            print("  → Rejected, will not be added")

        print()

    # Phase 4: Knowledge Curation Chat
    print("\n4. KNOWLEDGE CURATION CHAT")
    print("-" * 50)

    chat_interactions = [
        {
            "user": "What is the price for Enterprise tier?",
            "sophia": "Based on the knowledge base, the Enterprise Tier is priced at $60,000 per year.",
            "source": "product_pricing_2024.xlsx",
            "confidence": 0.95,
            "feedback": "correct",
        },
        {
            "user": "Do we support real-time data export?",
            "sophia": "According to our documentation, real-time data export is not currently supported.",
            "source": "product_specs.pdf",
            "confidence": 0.82,
            "feedback": "incorrect",
            "correction": "We now support real-time data export via our new API v2 launched in January 2024",
        },
        {
            "user": "Who are our main competitors?",
            "sophia": "Our main competitors are Entrata, RealPage, Yardi, and the newly identified FastTrack BI.",
            "source": "competitor_analysis.docx + Discovery Queue",
            "confidence": 0.91,
            "feedback": "correct",
        },
    ]

    print("Demonstrating knowledge curation chat:\n")

    for interaction in chat_interactions:
        print(f"User: {interaction['user']}")
        print(f"Sophia: {interaction['sophia']}")
        print(
            f"        [Source: {interaction['source']} | Confidence: {interaction['confidence']:.0%}]"
        )

        if interaction["feedback"] == "correct":
            print("User Feedback: ✓ Correct")
        else:
            print("User Feedback: ✗ Incorrect")
            print(f"User Correction: {interaction['correction']}")
            print("→ Knowledge base updated with correction")

        print()

    # Summary
    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)

    approved_insights = sum(1 for i in insights if i.status == "approved")

    print(
        f"""
✓ Documents Uploaded: {len(documents)}
✓ Insights Discovered: {len(insights)}
✓ Insights Approved: {approved_insights}
✓ Knowledge Corrections: 1

The Knowledge Ingestion & Curation System provides:
• Multi-format document upload with automatic parsing
• AI-powered discovery of insights from Gong calls
• Human-in-the-loop validation before knowledge base updates
• Interactive chat for testing and refining knowledge
• Continuous improvement through user feedback

This ensures Pay Ready's knowledge base remains:
- Accurate and up-to-date
- Enriched with real customer insights
- Validated by domain experts
- Continuously improving
"""
    )


if __name__ == "__main__":
    demonstrate_workflow()

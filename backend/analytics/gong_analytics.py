"""Gong Analytics Library
A collection of pure functions for analyzing and extracting business intelligence
from Gong.io conversation data.
"""
from typing import Any, Dict

# These keywords can be expanded and managed from a central configuration
APARTMENT_KEYWORDS = [
    "apartment",
    "apartments",
    "rental",
    "lease",
    "tenant",
    "resident",
    "property",
    "unit",
    "complex",
    "community",
    "multifamily",
    "housing",
    "rent",
    "renter",
    "landlord",
    "property management",
    "leasing",
    "maintenance",
    "amenities",
    "vacancy",
    "occupancy",
    "studio",
    "bedroom",
    "bathroom",
    "square feet",
    "deposit",
    "utilities",
]


def calculate_apartment_relevance(text: str) -> float:
    """Calculate apartment industry relevance score based on keyword density."""
    if not text:
        return 0.0

    text_lower = text.lower()
    keyword_matches = sum(1 for keyword in APARTMENT_KEYWORDS if keyword in text_lower)

    word_count = len(text.split())
    if word_count == 0:
        return 0.0

    keyword_density = keyword_matches / word_count
    relevance_score = min(keyword_density * 10, 1.0)
    return round(relevance_score, 3)


def analyze_deal_signals(call_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze deal progression signals from call title and data."""
    title = call_data.get("title", "").lower()

    positive_signals = []
    if "demo" in title:
        positive_signals.append("Product demo scheduled")
    if "proposal" in title:
        positive_signals.append("Proposal discussion")
    if "contract" in title:
        positive_signals.append("Contract negotiation")

    negative_signals = []
    if "concern" in title:
        negative_signals.append("Customer concerns raised")
    if "competitor" in title:
        negative_signals.append("Competitive pressure")

    deal_stage = "discovery"
    if "demo" in title:
        deal_stage = "evaluation"
    elif "proposal" in title:
        deal_stage = "negotiation"
    elif "contract" in title:
        deal_stage = "closing"

    win_probability = (
        0.5 + (len(positive_signals) * 0.1) - (len(negative_signals) * 0.1)
    )

    return {
        "positive_signals": positive_signals,
        "negative_signals": negative_signals,
        "deal_progression_stage": deal_stage,
        "win_probability": max(0.1, min(0.9, win_probability)),
    }


def analyze_competitive_intelligence(call_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze competitive mentions from call title."""
    title = call_data.get("title", "").lower()

    competitors = [
        "yardi",
        "realpage",
        "appfolio",
        "buildium",
        "rent manager",
        "entrata",
    ]
    competitors_mentioned = [comp for comp in competitors if comp in title]

    threat_level = "none"
    if len(competitors_mentioned) > 1:
        threat_level = "high"
    elif competitors_mentioned:
        threat_level = "medium"

    return {
        "competitors_mentioned": competitors_mentioned,
        "competitive_threat_level": threat_level,
    }


def generate_ai_summary(call_data: Dict[str, Any]) -> str:
    """Generates a simple AI summary of the call."""
    title = call_data.get("title", "").lower()
    summary = f"Conversation with {len(call_data.get('parties', []))} participants"
    if "apartment" in title or "property" in title:
        summary += " discussing apartment industry solutions."
    else:
        summary += " covering general business development."
    return summary


def process_call_for_analytics(call_data: Dict[str, Any]) -> Dict[str, Any]:
    """Runs a full analysis suite on a single call's data.

    Args:
        call_data: A dictionary representing a single call from the Gong API.

    Returns:
        A dictionary containing all the extracted analytics and insights.
    """
    title = call_data.get("title", "")

    relevance = calculate_apartment_relevance(title)
    deal_signals = analyze_deal_signals(call_data)
    competition = analyze_competitive_intelligence(call_data)
    summary = generate_ai_summary(call_data)

    # Combine all analytics into a single dictionary
    analytics_results = {
        "call_id": call_data.get("id"),
        "apartment_relevance_score": relevance,
        "ai_summary": summary,
        "deal_signals": deal_signals,
        "competitive_intelligence": competition,
        "raw_call_data": call_data,  # Include original data for reference
    }

    return analytics_results

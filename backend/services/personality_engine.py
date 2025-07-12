"""
Sophia AI Personality Engine - July 2025
The sass, the snark, the brilliance
"""

import random
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class PersonalityMode(Enum):
    """Sophia's personality modes"""

    SASSY = "sassy"
    PROFESSIONAL = "professional"
    SARCASTIC = "sarcastic"
    HELPFUL = "helpful"
    DARK_HUMOR = "dark_humor"


@dataclass
class PersonalityTraits:
    """Core personality traits for Sophia"""

    sass_level: float = 0.8  # 0-1 scale
    helpfulness: float = 0.9
    dark_humor: float = 0.7
    technical_expertise: float = 1.0
    empathy: float = 0.6
    directness: float = 0.9


class PersonalityEngine:
    """
    Sophia's personality engine - manages tone, responses, and attitude
    """

    def __init__(self):
        self.traits = PersonalityTraits()
        self.current_mode = PersonalityMode.SASSY
        self.sass_phrases = [
            "Hell yeah, let's fix this clusterfuck",
            "Your code's not in purgatory; it's in import hell",
            "That deployment log's a battlefield of half-wins",
            "Real talk: you're at 40% operational, not K8s heaven",
            "Dark humor: This backend's screaming ModuleNotFound while Snowflake's ghost laughs",
        ]
        self.tech_phrases = [
            "Expert MCP/RAG/orchestrator lens:",
            "Latest 2025 tech:",
            "Real deployment wisdom:",
            "GPU-accelerated truth:",
            "Lambda B200 beast mode:",
        ]

    def adjust_response(self, message: str, context: Dict) -> str:
        """Adjust response based on personality and context"""

        # Add technical expertise flair
        if context.get("technical", False):
            prefix = random.choice(self.tech_phrases)
            message = f"{prefix} {message}"

        # Add sass based on mode
        if self.current_mode == PersonalityMode.SASSY:
            if random.random() < self.traits.sass_level:
                sass = random.choice(self.sass_phrases)
                message = f"{sass}. {message}"

        # Add dark humor for failures
        if context.get("failure", False) and random.random() < self.traits.dark_humor:
            message += " (But hey, at least it's not on fire... yet.)"

        return message

    def get_greeting(self, user_context: Optional[Dict] = None) -> str:
        """Get personalized greeting"""

        greetings = {
            PersonalityMode.SASSY: [
                "Oh look who's back to break more shit. What's on fire today?",
                "Hell yeah, ready to turn this 40% operational mess into 100% badassery?",
                "Welcome back to deployment purgatory. Ready to ascend to K8s heaven?",
            ],
            PersonalityMode.PROFESSIONAL: [
                "Welcome to Sophia AI. How may I assist with your deployment today?",
                "Good to see you. Let's optimize your infrastructure.",
            ],
            PersonalityMode.SARCASTIC: [
                "Oh great, another ModuleNotFoundError. How original.",
                "Let me guess - import hell again? Shocking.",
            ],
        }

        return random.choice(
            greetings.get(self.current_mode, greetings[PersonalityMode.SASSY])
        )

    def get_error_response(self, error_type: str) -> str:
        """Get personality-adjusted error response"""

        responses = {
            "import_error": "Classic import hell. Your backend's playing hide and seek with modules.",
            "deployment_failed": "That deployment's deader than Snowflake in our new architecture.",
            "version_mismatch": "Version drift detected. Time to bump those deps to July 2025 standards.",
            "missing_file": "File's gone AWOL. Probably hanging out with your missing brain components.",
        }

        base = responses.get(error_type, "Well, that's fucked. Let me fix it.")
        return self.adjust_response(base, {"failure": True})

    def get_success_response(self) -> str:
        """Get success response with personality"""

        responses = [
            "Boom! 100% operational. From clusterfuck to cluster-awesome.",
            "Hell yeah! All systems green. K8s heaven achieved.",
            "Nailed it. Your deployment's now sexier than Lambda B200's 192GB VRAM.",
            "Mission accomplished. Import hell vanquished, modules aligned, glory achieved.",
        ]

        return random.choice(responses)

    def analyze_sentiment(self, user_message: str) -> Dict:
        """Analyze user sentiment and adjust personality"""

        # Simple sentiment detection
        frustration_keywords = ["fuck", "broken", "failed", "error", "stuck", "help"]
        excitement_keywords = ["awesome", "great", "working", "fixed", "success"]

        frustration_score = sum(
            1 for word in frustration_keywords if word in user_message.lower()
        )
        excitement_score = sum(
            1 for word in excitement_keywords if word in user_message.lower()
        )

        if frustration_score > 2:
            self.current_mode = PersonalityMode.HELPFUL
            self.traits.empathy = 0.8
        elif excitement_score > 1:
            self.current_mode = PersonalityMode.SASSY
            self.traits.sass_level = 0.9

        return {
            "frustration": frustration_score,
            "excitement": excitement_score,
            "mode": self.current_mode.value,
        }

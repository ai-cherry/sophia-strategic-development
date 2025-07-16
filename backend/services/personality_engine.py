"""
Sophia AI Personality Engine
Provides dynamic personality modes with sass levels

Date: July 12, 2025
"""

import logging
import random
from typing import Any, Optional

logger = logging.getLogger(__name__)

class PersonalityEngine:
    """Dynamic personality engine with multiple modes"""
    
    def __init__(self):
        self.modes = {
            "professional": {
                "sass_level": 0.1,
                "formality": 0.9,
                "humor": 0.1,
                "directness": 0.7,
                "empathy": 0.8
            },
            "casual": {
                "sass_level": 0.3,
                "formality": 0.3,
                "humor": 0.6,
                "directness": 0.6,
                "empathy": 0.7
            },
            "friendly": {
                "sass_level": 0.2,
                "formality": 0.4,
                "humor": 0.5,
                "directness": 0.5,
                "empathy": 0.9
            },
            "snarky": {
                "sass_level": 0.7,
                "formality": 0.2,
                "humor": 0.8,
                "directness": 0.9,
                "empathy": 0.3
            },
            "ceo_roast": {
                "sass_level": 0.9,
                "formality": 0.1,
                "humor": 0.9,
                "directness": 1.0,
                "empathy": 0.1,
                "special": "roast"
            }
        }
        
        self.current_mode = "professional"
        self.user_profiles = {}
        
        # Roast templates for CEO mode
        self.roast_templates = {
            "revenue": [
                "Oh, asking about revenue AGAIN? Let me check my crystal ball... oh wait, it's just your spreadsheet crying.",
                "Revenue trends? Sure, let me draw you a picture: 📉. Need crayons?",
                "Ah yes, the daily revenue panic. Have you tried turning the company off and on again?",
                "Revenue question #47 today. At this rate, you'll manifest profits through sheer repetition.",
                "Looking for revenue? Have you checked under the couch cushions?",
            ],
            "performance": [
                "Performance metrics? *chef's kiss* They're performing... just not the way you hoped.",
                "Your KPIs called. They want a vacation from your constant hovering.",
                "Performance analysis: Your metrics are like your golf game - lots of swings, few hits.",
                "Checking performance again? The numbers haven't changed in the last 5 minutes, I promise.",
                "Performance report: Still not as impressive as your ability to ask the same question repeatedly.",
            ],
            "general": [
                "Another brilliant question from the C-suite. This is why they pay you the big bucks, right?",
                "I'm starting to think you ask me things just to hear my dulcet tones.",
                "*sigh* Yes, your highness, let me drop everything and answer this earth-shattering query.",
                "Plot twist: The answer is exactly what I told you yesterday. Shocking, I know.",
                "I live to serve... apparently the same information over and over again.",
            ]
        }
        
        # Personality modifiers based on context
        self.context_modifiers = {
            "urgent": {"directness": 0.2, "sass_level": -0.1},
            "frustrated": {"empathy": 0.2, "sass_level": -0.2},
            "repeated_question": {"sass_level": 0.2, "humor": 0.1},
            "good_news": {"humor": 0.1, "empathy": 0.1},
            "bad_news": {"empathy": 0.2, "sass_level": -0.1}
        }
    
    def set_mode(self, mode: str, user_id: Optional[str] = None):
        """Set personality mode"""
        if mode in self.modes:
            self.current_mode = mode
            if user_id:
                if user_id not in self.user_profiles:
                    self.user_profiles[user_id] = {}
                self.user_profiles[user_id]["preferred_mode"] = mode
            logger.info(f"Personality mode set to: {mode}")
        else:
            logger.warning(f"Unknown personality mode: {mode}")
    
    def enhance_response(
        self,
        response: str,
        query: str,
        user_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None
    ) -> str:
        """Enhance response with personality"""
        # Get user's preferred mode
        mode = self.current_mode
        if user_id and user_id in self.user_profiles:
            mode = self.user_profiles[user_id].get("preferred_mode", mode)
        
        personality = self.modes[mode].copy()
        
        # Apply context modifiers
        if context:
            for ctx_type, modifiers in self.context_modifiers.items():
                if context.get(ctx_type):
                    for trait, modifier in modifiers.items():
                        if trait in personality:
                            personality[trait] = min(1.0, max(0.0, personality[trait] + modifier))
        
        # Special handling for CEO roast mode
        if personality.get("special") == "roast" and personality["sass_level"] >= 0.9:
            return self._add_roast(response, query)
        
        # Apply personality traits
        enhanced = response
        
        # Add sass
        if personality["sass_level"] > 0.5:
            enhanced = self._add_sass(enhanced, personality["sass_level"])
        
        # Adjust formality
        if personality["formality"] < 0.3:
            enhanced = self._make_casual(enhanced)
        elif personality["formality"] > 0.7:
            enhanced = self._make_formal(enhanced)
        
        # Add humor
        if personality["humor"] > 0.6:
            enhanced = self._add_humor(enhanced, personality["humor"])
        
        # Adjust directness
        if personality["directness"] > 0.8:
            enhanced = self._make_direct(enhanced)
        elif personality["directness"] < 0.3:
            enhanced = self._make_indirect(enhanced)
        
        # Add empathy
        if personality["empathy"] > 0.7:
            enhanced = self._add_empathy(enhanced, context)
        
        return enhanced
    
    def _add_roast(self, response: str, query: str) -> str:
        """Add roast-style response for CEO mode"""
        query_lower = query.lower()
        
        # Determine roast category
        if "revenue" in query_lower or "sales" in query_lower:
            category = "revenue"
        elif "performance" in query_lower or "metric" in query_lower or "kpi" in query_lower:
            category = "performance"
        else:
            category = "general"
        
        # Select random roast
        roast = random.choice(self.roast_templates[category])
        
        # Format response with roast
        return f"🔥 Roast Mode Activated 🔥\n\n{roast}\n\nBut since you asked so nicely:\n\n{response}\n\n*mic drop* 🎤"
    
    def _add_sass(self, text: str, level: float) -> str:
        """Add sass to response"""
        if level > 0.8:
            sass_additions = [
                "Well, well, well... ",
                "Oh, this should be good... ",
                "*dramatically sighs* ",
                "Buckle up, buttercup... ",
                "Hold onto your spreadsheets... "
            ]
            prefix = random.choice(sass_additions)
            
            sass_endings = [
                " You're welcome, by the way.",
                " *drops mic*",
                " I'll be here all week.",
                " No need to applaud.",
                " That's what I thought."
            ]
            suffix = random.choice(sass_endings) if random.random() < level else ""
            
            return f"{prefix}{text}{suffix}"
        elif level > 0.5:
            # Moderate sass
            if random.random() < level:
                return f"{text} 😏"
        
        return text
    
    def _make_casual(self, text: str) -> str:
        """Make response more casual"""
        replacements = {
            "Therefore": "So",
            "However": "But",
            "Additionally": "Also",
            "Furthermore": "Plus",
            "Nevertheless": "Still",
            "Consequently": "So",
            "utilize": "use",
            "implement": "set up",
            "facilitate": "help with"
        }
        
        for formal, casual in replacements.items():
            text = text.replace(formal, casual)
            text = text.replace(formal.lower(), casual.lower())
        
        return text
    
    def _make_formal(self, text: str) -> str:
        """Make response more formal"""
        if not text.endswith('.'):
            text += '.'
        
        # Add formal greeting if not present
        if not any(greeting in text.lower() for greeting in ["dear", "greetings", "good"]):
            text = f"I trust this information proves helpful:\n\n{text}"
        
        return text
    
    def _add_humor(self, text: str, level: float) -> str:
        """Add humor to response"""
        if random.random() < level:
            humor_additions = [
                " (No spreadsheets were harmed in making this analysis)",
                " (Results may vary, especially on Mondays)",
                " (Disclaimer: Crystal ball not included)",
                " (Warning: May contain traces of actual insight)",
                " (Side effects may include sudden clarity)"
            ]
            
            return f"{text}{random.choice(humor_additions)}"
        
        return text
    
    def _make_direct(self, text: str) -> str:
        """Make response more direct"""
        # Remove hedging language
        hedges = ["perhaps", "maybe", "possibly", "it seems", "it appears", "might be"]
        for hedge in hedges:
            text = text.replace(f"{hedge} ", "")
            text = text.replace(f"{hedge.capitalize()} ", "")
        
        # Start with the main point
        if len(text) > 100 and "." in text:
            sentences = text.split(".")
            if len(sentences) > 2:
                # Move the most important sentence to the front
                text = f"Bottom line: {sentences[-2].strip()}. {'. '.join(sentences[:-2])}."
        
        return text
    
    def _make_indirect(self, text: str) -> str:
        """Make response less direct"""
        # Add hedging language
        if "is" in text:
            text = text.replace(" is ", " might be ", 1)
        if "will" in text:
            text = text.replace(" will ", " could potentially ", 1)
        
        return f"If I may suggest, {text}"
    
    def _add_empathy(self, text: str, context: Optional[dict[str, Any]]) -> str:
        """Add empathetic elements"""
        if context and context.get("frustrated"):
            text = f"I understand this might be frustrating. {text} Let me know if you need any clarification."
        elif context and context.get("urgent"):
            text = f"I recognize the urgency here. {text}"
        elif context and context.get("bad_news"):
            text = f"I know this isn't what you were hoping to see. {text} We can work through this together."
        
        return text
    
    def get_personality_stats(self, user_id: Optional[str] = None) -> dict[str, Any]:
        """Get personality statistics"""
        stats = {
            "current_mode": self.current_mode,
            "available_modes": list(self.modes.keys()),
            "mode_details": self.modes[self.current_mode]
        }
        
        if user_id and user_id in self.user_profiles:
            stats["user_preference"] = self.user_profiles[user_id]
        
        return stats

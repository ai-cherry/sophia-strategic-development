"""
Enhanced Unified Chat Service with Personality
Because bland AI responses are worse than Snowflake latency
"""

import json
from typing import Dict, Optional, Any
from datetime import datetime

from backend.services.sophia_unified_orchestrator import SophiaUnifiedOrchestrator
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
from backend.services.portkey_gateway import PortkeyGateway
from backend.core.logging_config import get_logger


class EnhancedSophiaUnifiedOrchestrator:
    """
    Chat service with personality injection and adaptive responses
    No more boring bot syndrome
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.orchestrator = SophiaUnifiedOrchestrator()
        self.memory = UnifiedMemoryServiceV2()
        self.portkey = PortkeyGateway()

        # Load personalities
        self.personalities = self._load_personalities()
        self.active_sessions = {}  # Track personality per session

    def _load_personalities(self) -> Dict[str, Any]:
        """Load personality configurations"""
        try:
            with open("config/personalities.json", "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load personalities: {e}")
            return {
                "personalities": {
                    "Professional": {
                        "system_prompt": "You are a helpful AI assistant.",
                        "temperature": 0.7,
                    }
                },
                "user_defaults": {"default": "Professional"},
            }

    async def generate_response(
        self, query: str, user_id: str = "default", session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response with personality and multi-hop reasoning
        """
        start_time = datetime.utcnow()

        # Get user profile and determine personality
        profile = await self.memory.get_user_profile(user_id)
        persona = await self._determine_personality(query, user_id, session_id, profile)

        # Check for personality switch commands
        if new_persona := self._check_personality_switch(query):
            persona = new_persona
            if session_id:
                self.active_sessions[session_id] = persona

            # Store preference
            await self.memory.update_user_interaction(
                user_id=user_id,
                query=f"Switch personality to {persona}",
                response=f"Personality switched to {persona}",
                satisfaction=1.0,
            )

        # Multi-hop orchestration
        orchestration_result = await self.orchestrator.orchestrate(query, user_id)
        base_response = orchestration_result["response"]

        # Inject personality
        personality_config = self.personalities["personalities"].get(persona, {})
        system_prompt = personality_config.get("system_prompt", "")
        temperature = personality_config.get("temperature", 0.7)

        # Create personality-enhanced prompt
        enhance_prompt = f"""{system_prompt}

Based on this analysis, provide a response in character:

Query: {query}
Analysis: {base_response}
User Profile: Interaction #{profile.get('interaction_count', 0)}, Focus: {', '.join(profile.get('focus_areas', [])[:3])}

Remember: Stay in character but always provide value. If they ask something stupid, roast them AND solve it.
"""

        # Generate personality-infused response
        personality_response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": enhance_prompt}],
            temperature=temperature,
            max_tokens=2000,
        )

        final_response = personality_response.choices[0].message.content

        # Add personality-specific enhancements
        if persona == "ExpertSnark" and "error" not in orchestration_result.get(
            "debug", {}
        ):
            # Add a snarky performance comment
            perf_time = (datetime.utcnow() - start_time).total_seconds()
            if perf_time < 0.5:
                final_response += f"\n\n*Generated in {perf_time:.3f}s - faster than your brain can process it*"
            else:
                final_response += (
                    f"\n\n*Took {perf_time:.3f}s - blame the infrastructure, not me*"
                )

        # Store interaction with personality context
        await self.memory.update_user_interaction(
            user_id=user_id, query=query, response=final_response
        )

        return {
            "response": final_response,
            "metadata": {
                **orchestration_result["metadata"],
                "personality": persona,
                "personality_traits": personality_config.get("traits", []),
                "response_time": (datetime.utcnow() - start_time).total_seconds(),
                "user_profile": {
                    "interaction_count": profile.get("interaction_count", 0),
                    "focus_areas": profile.get("focus_areas", []),
                },
            },
            "debug": orchestration_result.get("debug", {}),
        }

    async def _determine_personality(
        self, query: str, user_id: str, session_id: Optional[str], profile: Dict
    ) -> str:
        """
        Determine which personality to use based on context
        """
        # Check session override
        if session_id and session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Check user defaults
        user_defaults = self.personalities.get("user_defaults", {})
        if user_id in user_defaults:
            return user_defaults[user_id]

        # Adaptive personality based on query type
        query_lower = query.lower()

        # Complex technical queries get ExpertSnark
        if any(
            term in query_lower
            for term in ["optimize", "performance", "architecture", "latency"]
        ):
            if profile.get("preferences", {}).get("snark_tolerance") == "high":
                return "ExpertSnark"

        # Investigation queries get DataDetective
        if any(
            term in query_lower
            for term in ["investigate", "analyze", "find out", "debug"]
        ):
            return "DataDetective"

        # Philosophical questions
        if any(
            term in query_lower
            for term in ["why", "should we", "best practice", "philosophy"]
        ):
            return "PhilosopherDev"

        # Default
        return user_defaults.get("default", "Professional")

    def _check_personality_switch(self, query: str) -> Optional[str]:
        """Check if user wants to switch personality"""
        query_lower = query.lower()

        switch_rules = self.personalities.get("persona_rules", {}).get("switching", {})
        trigger_keywords = switch_rules.get("trigger_keywords", {})

        for trigger, persona in trigger_keywords.items():
            if trigger in query_lower:
                return persona

        # Direct personality mentions
        for persona_name in self.personalities["personalities"].keys():
            if persona_name.lower() in query_lower and "switch" in query_lower:
                return persona_name

        return None

    async def get_personality_info(self, user_id: str) -> Dict[str, Any]:
        """Get info about available personalities and current state"""
        profile = await self.memory.get_user_profile(user_id)
        current_persona = profile.get("persona", "Professional")

        available = []
        for name, config in self.personalities["personalities"].items():
            available.append(
                {
                    "name": name,
                    "description": config.get("description", ""),
                    "traits": config.get("traits", []),
                    "trigger": f"Say 'switch to {name}' to activate",
                }
            )

        return {
            "current": current_persona,
            "available": available,
            "stats": {
                "interactions": profile.get("interaction_count", 0),
                "preferences": profile.get("preferences", {}),
            },
        }

    async def adjust_snark_level(self, user_id: str, level: int) -> str:
        """Adjust snark tolerance for a user (0-10)"""
        if not 0 <= level <= 10:
            return "Snark level must be between 0 and 10, genius."

        profile = await self.memory.get_user_profile(user_id)

        # Update preferences
        if level <= 3:
            tolerance = "low"
            response = "Fine, I'll be nicer. How boring."
        elif level <= 7:
            tolerance = "medium"
            response = (
                "Balanced snark it is. I'll try not to hurt your feelings too much."
            )
        else:
            tolerance = "high"
            response = (
                "Maximum snark engaged. Don't cry when I roast your terrible ideas."
            )

        # Update profile
        profile["preferences"]["snark_tolerance"] = tolerance

        # Store in Redis
        profile_key = f"user_profile:{user_id}"
        await self.memory.redis.setex(profile_key, 3600, json.dumps(profile))

        return response

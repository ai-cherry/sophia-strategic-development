"""
Prompt Optimizer MCP Server for Sophia AI
Provides intelligent prompt optimization and management
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.core.config_manager import get_config_value
from backend.services.mem0_integration_service import get_mem0_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Global service instance
optimizer_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global optimizer_service

    # Startup
    logger.info("🚀 Starting Prompt Optimizer MCP Server")
    optimizer_service = PromptOptimizerService()

    # Initialize default templates
    default_templates = [
        PromptTemplate(
            name="Business Analysis",
            category="analysis",
            template="You are a business analyst. Analyze {topic} considering:\n1. Current state\n2. Key challenges\n3. Opportunities\n4. Recommendations\n\nFocus on actionable insights for {audience}.",
        ),
        PromptTemplate(
            name="Code Review",
            category="development",
            template="Review the following {language} code for:\n- Code quality and best practices\n- Potential bugs or issues\n- Performance considerations\n- Security concerns\n\nCode:\n{code}\n\nProvide specific suggestions for improvement.",
        ),
        PromptTemplate(
            name="Sales Email",
            category="sales",
            template="Write a professional sales email to {recipient_name} at {company} about {product}.\n\nKey points to cover:\n- {value_proposition}\n- {call_to_action}\n\nTone: {tone}\nLength: {length}",
        ),
    ]

    for template in default_templates:
        await optimizer_service.create_template(template)

    logger.info(f"✅ Loaded {len(default_templates)} default templates")

    yield

    # Shutdown
    logger.info("👋 Shutting down Prompt Optimizer MCP Server")


app = FastAPI(
    title="Prompt Optimizer MCP Server",
    description="Intelligent prompt optimization and management for Sophia AI",
    version="1.0.0",
    lifespan=lifespan,
)


class PromptTemplate(BaseModel):
    """Model for prompt templates"""

    template_id: Optional[str] = None
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category")
    template: str = Field(..., description="Prompt template with placeholders")
    variables: list[str] = Field(default_factory=list, description="Required variables")
    performance_score: float = Field(default=0.0, description="Performance score")
    usage_count: int = Field(default=0, description="Usage count")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PromptOptimizationRequest(BaseModel):
    """Request model for prompt optimization"""

    prompt: str = Field(..., description="Original prompt to optimize")
    context: Optional[dict[str, Any]] = Field(
        default=None, description="Context for optimization"
    )
    optimization_level: str = Field(
        default="balanced",
        description="Optimization level: minimal, balanced, aggressive",
    )
    target_model: Optional[str] = Field(default=None, description="Target LLM model")


class PromptAnalysisResult(BaseModel):
    """Result model for prompt analysis"""

    clarity_score: float = Field(..., description="Clarity score (0-1)")
    specificity_score: float = Field(..., description="Specificity score (0-1)")
    structure_score: float = Field(..., description="Structure score (0-1)")
    overall_score: float = Field(..., description="Overall quality score (0-1)")
    suggestions: list[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )
    token_count: int = Field(..., description="Estimated token count")


class FeedbackRequest(BaseModel):
    """Request model for template feedback"""

    feedback_score: float = Field(
        ..., ge=0, le=1, description="Feedback score between 0 and 1"
    )


class PromptOptimizerService:
    """Service for prompt optimization and management"""

    def __init__(self):
        self.templates: dict[str, PromptTemplate] = {}
        self.optimization_history: list[dict[str, Any]] = []
        self.mem0_service = get_mem0_service()
        self.portkey_url = get_config_value("portkey_url", "https://api.portkey.ai/v1")
        self.portkey_api_key = get_config_value("portkey_api_key", "")

    async def analyze_prompt(self, prompt: str) -> PromptAnalysisResult:
        """
        Analyze prompt quality and structure

        Args:
            prompt: Prompt to analyze

        Returns:
            Analysis result with scores and suggestions
        """
        # Calculate basic metrics
        word_count = len(prompt.split())
        sentence_count = len([s for s in prompt.split(".") if s.strip()])
        has_clear_instruction = any(
            keyword in prompt.lower()
            for keyword in [
                "explain",
                "describe",
                "list",
                "compare",
                "analyze",
                "create",
                "write",
            ]
        )

        # Score calculations
        clarity_score = min(1.0, sentence_count / max(1, word_count / 20))
        if has_clear_instruction:
            clarity_score = min(1.0, clarity_score + 0.2)

        specificity_score = min(1.0, word_count / 50)
        if any(char in prompt for char in ["?", "!", ":"]):
            specificity_score = min(1.0, specificity_score + 0.1)

        structure_score = 0.5
        if prompt.count("\n") > 0:
            structure_score += 0.2
        if any(marker in prompt for marker in ["1.", "2.", "-", "*"]):
            structure_score += 0.3

        overall_score = (clarity_score + specificity_score + structure_score) / 3

        # Generate suggestions
        suggestions = []
        if clarity_score < 0.7:
            suggestions.append("Add clear action verbs to specify what you want")
        if specificity_score < 0.7:
            suggestions.append("Provide more context and details")
        if structure_score < 0.7:
            suggestions.append(
                "Use bullet points or numbered lists for complex requests"
            )
        if word_count < 10:
            suggestions.append("Prompt seems too short - add more context")
        if word_count > 200:
            suggestions.append("Consider breaking down into smaller, focused prompts")

        return PromptAnalysisResult(
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            structure_score=structure_score,
            overall_score=overall_score,
            suggestions=suggestions,
            token_count=int(word_count * 1.3),  # Rough token estimate
        )

    async def optimize_prompt(
        self,
        prompt: str,
        context: Optional[dict[str, Any]] = None,
        optimization_level: str = "balanced",
    ) -> str:
        """
        Optimize a prompt for better LLM performance

        Args:
            prompt: Original prompt
            context: Additional context
            optimization_level: Level of optimization

        Returns:
            Optimized prompt
        """
        analysis = await self.analyze_prompt(prompt)

        optimized = prompt

        # Apply optimizations based on level
        if optimization_level in ["balanced", "aggressive"]:
            # Add role context if missing
            if "you are" not in prompt.lower() and "act as" not in prompt.lower():
                role_context = "You are a helpful AI assistant. "
                if context and "role" in context:
                    role_context = f"You are {context['role']}. "
                optimized = role_context + optimized

            # Add clear instruction if missing
            if analysis.clarity_score < 0.7:
                if not any(prompt.strip().endswith(p) for p in [".", "?", "!"]):
                    optimized += "."
                optimized += " Please provide a clear and detailed response."

            # Structure improvements
            if analysis.structure_score < 0.7 and optimization_level == "aggressive":
                # Add structure markers
                if "steps" in prompt.lower() or "list" in prompt.lower():
                    optimized += (
                        "\n\nPlease structure your response with clear numbered points."
                    )

        # Add context if provided
        if context:
            context_str = "\n\nContext:\n"
            for key, value in context.items():
                if key != "role":
                    context_str += f"- {key}: {value}\n"
            if context_str != "\n\nContext:\n":
                optimized = optimized + context_str

        # Store optimization history
        self.optimization_history.append(
            {
                "original": prompt,
                "optimized": optimized,
                "analysis": analysis.dict(),
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Store in Mem0 for learning
        await self.mem0_service.store_conversation_memory(
            user_id="system",
            conversation=[
                {"role": "user", "content": f"Original prompt: {prompt}"},
                {"role": "assistant", "content": f"Optimized prompt: {optimized}"},
            ],
            metadata={
                "category": "prompt_optimization",
                "analysis_scores": analysis.dict(),
                "optimization_level": optimization_level,
            },
        )

        return optimized

    async def create_template(self, template: PromptTemplate) -> PromptTemplate:
        """Create a new prompt template"""
        template.template_id = f"tpl_{datetime.now().timestamp()}"
        template.created_at = datetime.now()
        template.updated_at = datetime.now()

        # Extract variables from template
        import re

        template.variables = re.findall(r"\{(\w+)\}", template.template)

        self.templates[template.template_id] = template
        return template

    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID"""
        return self.templates.get(template_id)

    async def list_templates(
        self, category: Optional[str] = None
    ) -> list[PromptTemplate]:
        """List all templates, optionally filtered by category"""
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return sorted(templates, key=lambda x: x.performance_score, reverse=True)

    async def apply_template(self, template_id: str, variables: dict[str, str]) -> str:
        """Apply variables to a template"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Check all required variables are provided
        missing = set(template.variables) - set(variables.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        # Apply variables
        result = template.template
        for var, value in variables.items():
            result = result.replace(f"{{{var}}}", str(value))

        # Update usage count
        template.usage_count += 1
        template.updated_at = datetime.now()

        return result

    async def update_template_performance(
        self, template_id: str, feedback_score: float
    ):
        """Update template performance based on feedback"""
        template = self.templates.get(template_id)
        if not template:
            return

        # Weighted average with more weight on recent feedback
        weight = 0.3
        template.performance_score = (
            template.performance_score * (1 - weight) + feedback_score * weight
        )
        template.updated_at = datetime.now()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "prompt_optimizer",
        "timestamp": datetime.now().isoformat(),
        "templates_count": len(optimizer_service.templates) if optimizer_service else 0,
    }


@app.post("/analyze", response_model=PromptAnalysisResult)
async def analyze_prompt(prompt: str = Body(..., embed=True)):
    """Analyze a prompt for quality and structure"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await optimizer_service.analyze_prompt(prompt)
        return result
    except Exception as e:
        logger.error(f"Error analyzing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize")
async def optimize_prompt(request: PromptOptimizationRequest):
    """Optimize a prompt for better performance"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        optimized = await optimizer_service.optimize_prompt(
            request.prompt, request.context, request.optimization_level
        )

        analysis_before = await optimizer_service.analyze_prompt(request.prompt)
        analysis_after = await optimizer_service.analyze_prompt(optimized)

        return {
            "original": request.prompt,
            "optimized": optimized,
            "improvement": {
                "clarity": analysis_after.clarity_score - analysis_before.clarity_score,
                "specificity": analysis_after.specificity_score
                - analysis_before.specificity_score,
                "structure": analysis_after.structure_score
                - analysis_before.structure_score,
                "overall": analysis_after.overall_score - analysis_before.overall_score,
            },
            "analysis": analysis_after,
        }
    except Exception as e:
        logger.error(f"Error optimizing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/templates", response_model=PromptTemplate)
async def create_template(template: PromptTemplate):
    """Create a new prompt template"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        created = await optimizer_service.create_template(template)
        return created
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates", response_model=list[PromptTemplate])
async def list_templates(category: Optional[str] = None):
    """List all templates"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        templates = await optimizer_service.list_templates(category)
        return templates
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates/{template_id}", response_model=PromptTemplate)
async def get_template(template_id: str):
    """Get a specific template"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    template = await optimizer_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@app.post("/templates/{template_id}/apply")
async def apply_template(template_id: str, variables: dict[str, str]):
    """Apply variables to a template"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        result = await optimizer_service.apply_template(template_id, variables)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/templates/{template_id}/feedback")
async def update_template_feedback(template_id: str, request: FeedbackRequest):
    """Update template performance based on feedback"""
    if not optimizer_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    try:
        await optimizer_service.update_template_performance(
            template_id, request.feedback_score
        )
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Error updating template feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_optimization_history(limit: int = 10):
    """Get recent optimization history"""
    history = (
        optimizer_service.optimization_history[-limit:] if optimizer_service else []
    )
    return {
        "history": history,
        "total": len(optimizer_service.optimization_history)
        if optimizer_service
        else 0,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9030)

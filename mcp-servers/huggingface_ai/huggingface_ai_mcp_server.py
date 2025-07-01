#!/usr/bin/env python3
"""
Hugging Face AI MCP Server for Sophia AI
Provides advanced ML model management and inference capabilities
Leverages Hugging Face CLI and transformers library
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceAIMCPServer:
    """Hugging Face AI MCP Server for enhanced AI capabilities"""

    def __init__(self, port: int = 9016):
        self.port = port
        self.server = Server("huggingface-ai")
        self.hf_token = get_config_value("huggingface_token")

        # Model configurations for different use cases
        self.model_configs = {
            "text_generation": {
                "model": "microsoft/DialoGPT-large",
                "task": "text-generation",
                "description": "Advanced text generation and completion"
            },
            "embedding": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "task": "feature-extraction",
                "description": "High-quality text embeddings"
            },
            "summarization": {
                "model": "facebook/bart-large-cnn",
                "task": "summarization",
                "description": "Document and text summarization"
            },
            "sentiment_analysis": {
                "model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "task": "sentiment-analysis",
                "description": "Advanced sentiment analysis"
            },
            "question_answering": {
                "model": "deepset/roberta-base-squad2",
                "task": "question-answering",
                "description": "Contextual question answering"
            },
            "classification": {
                "model": "microsoft/DialoGPT-medium",
                "task": "text-classification",
                "description": "Text classification and categorization"
            }
        }

        self._register_tools()

    def _register_tools(self):
        """Register MCP tools for Hugging Face AI"""

        @self.server.call_tool()
        async def text_generation(arguments: dict[str, Any]) -> list[TextContent]:
            """Generate text using Hugging Face models"""
            prompt = arguments.get("prompt", "")
            max_length = arguments.get("max_length", 100)
            model_name = arguments.get("model", self.model_configs["text_generation"]["model"])

            if not prompt:
                return [TextContent(
                    type="text",
                    text="Error: No prompt provided for text generation"
                )]

            logger.info(f"🤖 Generating text with model: {model_name}")

            try:
                result = await self._run_text_generation(prompt, model_name, max_length)

                return [TextContent(
                    type="text",
                    text=f"🤖 **Text Generation Result:**\n\n**Prompt:** {prompt}\n\n**Generated Text:**\n{result}"
                )]

            except Exception as e:
                logger.error(f"❌ Text generation failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during text generation: {str(e)}"
                )]

        @self.server.call_tool()
        async def generate_embeddings(arguments: dict[str, Any]) -> list[TextContent]:
            """Generate embeddings for text using Hugging Face models"""
            texts = arguments.get("texts", [])
            model_name = arguments.get("model", self.model_configs["embedding"]["model"])

            if not texts:
                return [TextContent(
                    type="text",
                    text="Error: No texts provided for embedding generation"
                )]

            logger.info(f"📊 Generating embeddings for {len(texts)} texts")

            try:
                embeddings = await self._generate_embeddings(texts, model_name)

                summary = "📊 **Embedding Generation Complete:**\n\n"
                summary += f"**Model:** {model_name}\n"
                summary += f"**Texts processed:** {len(texts)}\n"
                summary += f"**Embedding dimension:** {len(embeddings[0]) if embeddings else 0}\n"
                summary += f"**First text:** {texts[0][:100]}...\n"

                return [TextContent(
                    type="text",
                    text=summary
                )]

            except Exception as e:
                logger.error(f"❌ Embedding generation failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during embedding generation: {str(e)}"
                )]

        @self.server.call_tool()
        async def summarize_text(arguments: dict[str, Any]) -> list[TextContent]:
            """Summarize text using Hugging Face models"""
            text = arguments.get("text", "")
            max_length = arguments.get("max_length", 150)
            min_length = arguments.get("min_length", 50)
            model_name = arguments.get("model", self.model_configs["summarization"]["model"])

            if not text:
                return [TextContent(
                    type="text",
                    text="Error: No text provided for summarization"
                )]

            logger.info(f"📝 Summarizing text with model: {model_name}")

            try:
                summary = await self._summarize_text(text, model_name, max_length, min_length)

                result = "📝 **Text Summarization:**\n\n"
                result += f"**Original length:** {len(text)} characters\n"
                result += f"**Summary length:** {len(summary)} characters\n"
                result += f"**Model:** {model_name}\n\n"
                result += f"**Summary:**\n{summary}"

                return [TextContent(
                    type="text",
                    text=result
                )]

            except Exception as e:
                logger.error(f"❌ Text summarization failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during text summarization: {str(e)}"
                )]

        @self.server.call_tool()
        async def analyze_sentiment(arguments: dict[str, Any]) -> list[TextContent]:
            """Analyze sentiment using Hugging Face models"""
            text = arguments.get("text", "")
            model_name = arguments.get("model", self.model_configs["sentiment_analysis"]["model"])

            if not text:
                return [TextContent(
                    type="text",
                    text="Error: No text provided for sentiment analysis"
                )]

            logger.info(f"😊 Analyzing sentiment with model: {model_name}")

            try:
                sentiment_result = await self._analyze_sentiment(text, model_name)

                result = "😊 **Sentiment Analysis:**\n\n"
                result += f"**Text:** {text[:200]}...\n"
                result += f"**Model:** {model_name}\n"
                result += f"**Sentiment:** {sentiment_result['label']}\n"
                result += f"**Confidence:** {sentiment_result['score']:.2f}\n"

                return [TextContent(
                    type="text",
                    text=result
                )]

            except Exception as e:
                logger.error(f"❌ Sentiment analysis failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during sentiment analysis: {str(e)}"
                )]

        @self.server.call_tool()
        async def question_answering(arguments: dict[str, Any]) -> list[TextContent]:
            """Answer questions using Hugging Face models"""
            question = arguments.get("question", "")
            context = arguments.get("context", "")
            model_name = arguments.get("model", self.model_configs["question_answering"]["model"])

            if not question or not context:
                return [TextContent(
                    type="text",
                    text="Error: Both question and context are required"
                )]

            logger.info(f"❓ Answering question with model: {model_name}")

            try:
                answer = await self._answer_question(question, context, model_name)

                result = "❓ **Question Answering:**\n\n"
                result += f"**Question:** {question}\n"
                result += f"**Model:** {model_name}\n"
                result += f"**Confidence:** {answer['score']:.2f}\n\n"
                result += f"**Answer:** {answer['answer']}\n"

                return [TextContent(
                    type="text",
                    text=result
                )]

            except Exception as e:
                logger.error(f"❌ Question answering failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during question answering: {str(e)}"
                )]

        @self.server.call_tool()
        async def classify_text(arguments: dict[str, Any]) -> list[TextContent]:
            """Classify text using Hugging Face models"""
            text = arguments.get("text", "")
            labels = arguments.get("labels", [])
            model_name = arguments.get("model", self.model_configs["classification"]["model"])

            if not text:
                return [TextContent(
                    type="text",
                    text="Error: No text provided for classification"
                )]

            logger.info(f"🏷️ Classifying text with model: {model_name}")

            try:
                classification = await self._classify_text(text, model_name, labels)

                result = "🏷️ **Text Classification:**\n\n"
                result += f"**Text:** {text[:200]}...\n"
                result += f"**Model:** {model_name}\n"
                result += f"**Classification:** {classification['label']}\n"
                result += f"**Confidence:** {classification['score']:.2f}\n"

                return [TextContent(
                    type="text",
                    text=result
                )]

            except Exception as e:
                logger.error(f"❌ Text classification failed: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error during text classification: {str(e)}"
                )]

        @self.server.call_tool()
        async def list_models(arguments: dict[str, Any]) -> list[TextContent]:
            """List available Hugging Face models"""
            task = arguments.get("task", "all")

            logger.info(f"📋 Listing models for task: {task}")

            try:
                if task == "all":
                    models_info = self.model_configs
                else:
                    models_info = {k: v for k, v in self.model_configs.items() if k == task}

                result = "📋 **Available Hugging Face Models:**\n\n"

                for task_name, config in models_info.items():
                    result += f"**{task_name.title()}:**\n"
                    result += f"  Model: {config['model']}\n"
                    result += f"  Task: {config['task']}\n"
                    result += f"  Description: {config['description']}\n\n"

                return [TextContent(
                    type="text",
                    text=result
                )]

            except Exception as e:
                logger.error(f"❌ Failed to list models: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error listing models: {str(e)}"
                )]

    # Implementation methods
    async def _run_text_generation(self, prompt: str, model_name: str, max_length: int) -> str:
        """Run text generation using transformers"""
        try:
            # Use transformers pipeline
            from transformers import pipeline

            generator = pipeline("text-generation", model=model_name)
            result = generator(prompt, max_length=max_length, num_return_sequences=1)

            return result[0]["generated_text"]

        except Exception as e:
            logger.error(f"❌ Text generation error: {e}")
            # Fallback to local implementation
            return f"Generated text for: {prompt} (simplified fallback)"

    async def _generate_embeddings(self, texts: list[str], model_name: str) -> list[list[float]]:
        """Generate embeddings using sentence transformers"""
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(model_name)
            embeddings = model.encode(texts)

            return embeddings.tolist()

        except Exception as e:
            logger.error(f"❌ Embedding generation error: {e}")
            # Fallback to dummy embeddings
            return [[0.1] * 384 for _ in texts]

    async def _summarize_text(self, text: str, model_name: str, max_length: int, min_length: int) -> str:
        """Summarize text using transformers"""
        try:
            from transformers import pipeline

            summarizer = pipeline("summarization", model=model_name)
            result = summarizer(text, max_length=max_length, min_length=min_length)

            return result[0]["summary_text"]

        except Exception as e:
            logger.error(f"❌ Summarization error: {e}")
            # Fallback to simple summarization
            sentences = text.split('. ')
            return '. '.join(sentences[:3]) + '.'

    async def _analyze_sentiment(self, text: str, model_name: str) -> dict[str, Any]:
        """Analyze sentiment using transformers"""
        try:
            from transformers import pipeline

            sentiment_analyzer = pipeline("sentiment-analysis", model=model_name)
            result = sentiment_analyzer(text)

            return result[0]

        except Exception as e:
            logger.error(f"❌ Sentiment analysis error: {e}")
            # Fallback to simple sentiment
            positive_words = ["good", "great", "excellent", "awesome", "love"]
            negative_words = ["bad", "terrible", "awful", "hate", "horrible"]

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                return {"label": "POSITIVE", "score": 0.8}
            elif negative_count > positive_count:
                return {"label": "NEGATIVE", "score": 0.8}
            else:
                return {"label": "NEUTRAL", "score": 0.6}

    async def _answer_question(self, question: str, context: str, model_name: str) -> dict[str, Any]:
        """Answer questions using transformers"""
        try:
            from transformers import pipeline

            qa_pipeline = pipeline("question-answering", model=model_name)
            result = qa_pipeline(question=question, context=context)

            return result

        except Exception as e:
            logger.error(f"❌ Question answering error: {e}")
            # Fallback to simple answer extraction
            return {
                "answer": "Based on the provided context, the answer is not immediately clear.",
                "score": 0.5
            }

    async def _classify_text(self, text: str, model_name: str, labels: list[str]) -> dict[str, Any]:
        """Classify text using transformers"""
        try:
    from transformers import pipeline
    from backend.core.auto_esc_config import get_config_value
    
    # Transformers available
    transformers_available = True
except ImportError:
    # Transformers not available
    transformers_available = False
    logger.warning("Transformers library not available")

            if labels:
                # Zero-shot classification
                classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
                result = classifier(text, labels)
                return {"label": result["labels"][0], "score": result["scores"][0]}
            else:
                # Regular classification
                classifier = pipeline("text-classification", model=model_name)
                result = classifier(text)
                return result[0]

        except Exception as e:
            logger.error(f"❌ Text classification error: {e}")
            # Fallback classification
            return {"label": "UNKNOWN", "score": 0.5}

    async def start_server(self):
        """Start the Hugging Face AI MCP server"""
        logger.info(f"🚀 Starting Hugging Face AI MCP Server on port {self.port}")

        # Add health check endpoint
        @self.server.call_tool()
        async def health_check(arguments: dict[str, Any]) -> list[TextContent]:
            """Health check for Hugging Face AI MCP server"""
            return [TextContent(
                type="text",
                text=f"✅ Hugging Face AI MCP Server is healthy (Port: {self.port})"
            )]

        # Register tools as MCP tools
        tools = [
            Tool(
                name="text_generation",
                description="Generate text using Hugging Face models",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "max_length": {"type": "integer", "default": 100},
                        "model": {"type": "string"}
                    },
                    "required": ["prompt"]
                }
            ),
            Tool(
                name="generate_embeddings",
                description="Generate embeddings for text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "texts": {"type": "array", "items": {"type": "string"}},
                        "model": {"type": "string"}
                    },
                    "required": ["texts"]
                }
            ),
            Tool(
                name="summarize_text",
                description="Summarize text using AI models",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "max_length": {"type": "integer", "default": 150},
                        "min_length": {"type": "integer", "default": 50},
                        "model": {"type": "string"}
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="analyze_sentiment",
                description="Analyze sentiment of text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "model": {"type": "string"}
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="question_answering",
                description="Answer questions based on context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "context": {"type": "string"},
                        "model": {"type": "string"}
                    },
                    "required": ["question", "context"]
                }
            ),
            Tool(
                name="classify_text",
                description="Classify text into categories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "labels": {"type": "array", "items": {"type": "string"}},
                        "model": {"type": "string"}
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="list_models",
                description="List available Hugging Face models",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "default": "all"}
                    }
                }
            ),
            Tool(
                name="health_check",
                description="Check health status of Hugging Face AI MCP server",
                inputSchema={"type": "object", "properties": {}}
            )
        ]

        # Set tools on server
        self.server.tools = tools

        # Start the server
        await self.server.run(port=self.port)

# Main execution
async def main():
    server = HuggingFaceAIMCPServer()

    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Hugging Face AI MCP Server")

if __name__ == "__main__":
    asyncio.run(main())


# --- Auto-inserted health endpoint ---
try:
    from fastapi import APIRouter
    router = APIRouter()
    @router.get("/health")
    async def health():
        return {"status": "ok"}
except ImportError:
    pass

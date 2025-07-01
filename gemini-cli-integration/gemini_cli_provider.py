from datetime import UTC, datetime

#!/usr/bin/env python3
"""
Gemini CLI Provider for Sophia AI
Provides free access to Gemini models through the CLI
"""

import asyncio
import json
import logging
import os
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class GeminiCLIProvider:
    """Wrapper for Gemini CLI to integrate with Sophia AI"""

    def __init__(self):
        self.cli_path = os.getenv("GEMINI_CLI_PATH", "gemini")
        self.default_model = os.getenv("GEMINI_MODEL_PREFERENCE", "gemini-2.5-pro")
        self.verify_installation()

    def verify_installation(self) -> bool:
        """Verify Gemini CLI is installed and authenticated"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info(f"Gemini CLI verified: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.error(f"Gemini CLI not found: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate response using Gemini CLI"""

        model = model or self.default_model

        # Build command
        cmd = [
            self.cli_path,
            "generate",
            "--model",
            model,
            "--temperature",
            str(temperature),
        ]

        if max_tokens:
            cmd.extend(["--max-tokens", str(max_tokens)])

        if system_prompt:
            cmd.extend(["--system", system_prompt])

        # Add prompt
        cmd.extend(["--prompt", prompt])

        try:
            # Run async
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"Gemini CLI error: {stderr.decode()}")

            # Parse response
            response_text = stdout.decode().strip()

            return {
                "success": True,
                "content": response_text,
                "model": model,
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(prompt.split()) + len(response_text.split()),
                },
                "cost": 0.0,  # Free!
            }

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return {"success": False, "error": str(e), "model": model}

    async def count_tokens(self, text: str, model: str | None = None) -> int:
        """Count tokens for a given text"""
        model = model or self.default_model

        cmd = [self.cli_path, "count-tokens", "--model", model, "--text", text]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await process.communicate()

            if process.returncode == 0:
                return int(stdout.decode().strip())
            else:
                # Fallback to word count
                return len(text.split())

        except Exception:
            return len(text.split())

    async def process_large_document(
        self, document: str, operation: str = "summarize", chunk_size: int = 100000
    ) -> dict[str, Any]:
        """Process large documents that exceed normal context limits"""

        token_count = await self.count_tokens(document)

        if token_count <= chunk_size:
            # Process in one go
            prompt = f"{operation}: {document}"
            return await self.generate(prompt)
        else:
            # Split and process in chunks
            chunks = self._split_document(document, chunk_size)
            results = []

            for i, chunk in enumerate(chunks):
                prompt = f"{operation} (part {i + 1}/{len(chunks)}): {chunk}"
                result = await self.generate(prompt)
                if result["success"]:
                    results.append(result["content"])

            # Combine results
            combined = "\n\n".join(results)
            final_prompt = (
                f"Combine these {operation} results into a coherent whole: {combined}"
            )

            return await self.generate(final_prompt, max_tokens=4000)

    def _split_document(self, document: str, chunk_size: int) -> list[str]:
        """Split document into chunks"""
        words = document.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)

        return chunks

    async def analyze_code(
        self, code: str, language: str = "python", analysis_type: str = "review"
    ) -> dict[str, Any]:
        """Analyze code using Gemini"""

        prompt = f"""
Analyze this {language} code for {analysis_type}:

```{language}
{code}
```

Provide:
1. Overview
2. Issues found
3. Suggestions for improvement
4. Security considerations
"""

        return await self.generate(
            prompt,
            system_prompt="You are an expert code reviewer with deep knowledge of best practices and security.",
        )

    async def web_fetch_and_summarize(
        self, url: str, fetch_content: str, summary_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """Process web-fetched content"""

        prompt = f"""
Summarize this content from {url} ({summary_type} summary):

{fetch_content}

Include:
1. Key points
2. Important details
3. Actionable insights
4. Relevance to our context
"""

        return await self.generate(prompt, max_tokens=2000)

    def get_model_info(self) -> dict[str, Any]:
        """Get information about available models"""

        try:
            result = subprocess.run(
                [self.cli_path, "models", "list", "--json"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    "models": [
                        {
                            "name": "gemini-2.5-pro",
                            "context_length": 1048576,
                            "multimodal": True,
                        },
                        {
                            "name": "gemini-2.5-flash",
                            "context_length": 262144,
                            "multimodal": True,
                        },
                    ]
                }
        except Exception:
            return {"models": []}


# Integration with Sophia AI's model routing
class GeminiCLIModelRouter:
    """Routes requests to Gemini CLI based on context and cost optimization"""

    def __init__(self):
        self.provider = GeminiCLIProvider()
        self.usage_tracker = {"total_tokens": 0, "total_requests": 0, "cost_saved": 0.0}

    def should_use_gemini(
        self, context_size: int, task_type: str, api_limits_reached: bool = False
    ) -> bool:
        """Determine if Gemini CLI should be used"""

        # Always use for very large contexts
        if context_size > 200000:
            return True

        # Use if API limits reached
        if api_limits_reached:
            return True

        # Use for cost-sensitive operations
        if task_type in ["batch_processing", "bulk_analysis", "documentation"]:
            return True

        # Use if explicitly requested
        if os.getenv("PREFER_GEMINI_CLI", "false").lower() == "true":
            return True

        return False

    async def route_request(
        self, prompt: str, context: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        """Route request to appropriate model"""

        context_size = len(prompt.split())
        task_type = context.get("task_type", "general")
        api_limits = context.get("api_limits_reached", False)

        if self.should_use_gemini(context_size, task_type, api_limits):
            logger.info(
                f"Routing to Gemini CLI (context: {context_size}, task: {task_type})"
            )

            result = await self.provider.generate(prompt, **kwargs)

            if result["success"]:
                # Track usage
                self.usage_tracker["total_tokens"] += result["usage"]["total_tokens"]
                self.usage_tracker["total_requests"] += 1

                # Estimate cost saved (based on Claude/GPT pricing)
                estimated_cost = (
                    result["usage"]["total_tokens"] * 0.00003
                )  # Rough estimate
                self.usage_tracker["cost_saved"] += estimated_cost

                result["routing_info"] = {
                    "provider": "gemini_cli",
                    "reason": f"context_size={context_size}",
                    "cost_saved": estimated_cost,
                }

            return result
        else:
            # Route to paid API (handled elsewhere)
            return {
                "success": False,
                "route_to": "paid_api",
                "reason": "Not suitable for Gemini CLI",
            }

    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics"""
        return {
            "gemini_cli_stats": self.usage_tracker,
            "timestamp": datetime.now(UTC).isoformat(),
        }

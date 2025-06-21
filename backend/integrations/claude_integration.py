"""Claude Integration for Sophia AI.

Provides unified interface for Claude API operations and "Claude as Code" functionality
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from backend.core.pulumi_esc import pulumi_esc_client

logger = logging.getLogger(__name__)


@dataclass
class ClaudeMessage:
    """Claude message data structure."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None


@dataclass
class ClaudeConversation:
    """Claude conversation data structure."""id: str.

    messages: List[ClaudeMessage]
    model: str
    created_at: str
    updated_at: str
    total_tokens: int = 0
    status: str = "active"


@dataclass
class ClaudeCodeGeneration:
    """Claude code generation result."""id: str.

    prompt: str
    generated_code: str
    language: str
    explanation: str
    created_at: str
    model: str
    tokens_used: int


class ClaudeIntegration:
    """Claude Integration for Sophia AI.

            Provides unified interface for Claude API operations, code generation,
            and "Claude as Code" functionality through the Anthropic API.
    """def __init__(self):.

        self.api_base_url = "https://api.anthropic.com/v1"
        self.default_model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4096
        self._config = None
        self._authenticated = False
        self._session = None

        # Rate limiting
        self.rate_limit_requests = 50  # requests per minute
        self.rate_limit_tokens = 40000  # tokens per minute
        self.request_timestamps = []
        self.token_usage = []

    async def initialize(self) -> bool:
        """Initialize Claude integration with authentication."""try:.

            # Get Claude configuration from Pulumi ESC
            self._config = await self._get_claude_config()

            if not self._config:
                logger.warning("Claude configuration not found in Pulumi ESC")
                return False

            # Initialize HTTP session
            self._session = aiohttp.ClientSession(
                headers={
                    "x-api-key": self._config.get("api_key"),
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=60),
            )

            # Test authentication
            self._authenticated = await self._test_authentication()

            if self._authenticated:
                logger.info("Claude integration initialized successfully")
                return True
            else:
                logger.error("Claude authentication failed")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Claude integration: {e}")
            return False

    async def _get_claude_config(self) -> Optional[Dict[str, Any]]:
        """Get Claude configuration from Pulumi ESC or environment variables."""try:.

            # Try Pulumi ESC first
            try:
                config = await pulumi_esc_client.get_configuration("claude")
                if config:
                    logger.info("Using Claude configuration from Pulumi ESC")
                    return config
            except Exception as e:
                logger.warning(
                    f"Could not get Claude configuration from Pulumi ESC: {e}"
                )

            # Fallback to environment variables
            logger.info("Using Claude configuration from environment variables")
            env_config = {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                "max_tokens": int(os.getenv("CLAUDE_MAX_TOKENS", "4096")),
                "organization_id": os.getenv("CLAUDE_ORGANIZATION_ID", "sophia-ai"),
                "api_base_url": os.getenv(
                    "CLAUDE_API_BASE_URL", "https://api.anthropic.com/v1"
                ),
                "anthropic_version": os.getenv("ANTHROPIC_VERSION", "2023-06-01"),
            }

            if env_config["api_key"]:
                return env_config
            else:
                logger.error(
                    "Claude API key not found in Pulumi ESC or environment variables"
                )
                return None

        except Exception as e:
            logger.error(f"Failed to get Claude configuration: {e}")
            return None

    async def _test_authentication(self) -> bool:
        """Test Claude API authentication."""try:.

            if not self._session:
                return False

            # Test with a simple message
            test_payload = {
                "model": self.default_model,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}],
            }

            async with self._session.post(
                f"{self.api_base_url}/messages", json=test_payload
            ) as response:
                if response.status == 200:
                    logger.info("Claude API authentication successful")
                    return True
                else:
                    logger.error(f"Claude API authentication failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Claude authentication test failed: {e}")
            return False

    async def _check_rate_limits(self, estimated_tokens: int = 1000) -> bool:
        """Check if request is within rate limits."""current_time = time.time().

        # Clean old timestamps (older than 1 minute)
        self.request_timestamps = [
            ts for ts in self.request_timestamps if current_time - ts < 60
        ]
        self.token_usage = [
            (ts, tokens) for ts, tokens in self.token_usage if current_time - ts < 60
        ]

        # Check request rate limit
        if len(self.request_timestamps) >= self.rate_limit_requests:
            logger.warning("Request rate limit exceeded")
            return False

        # Check token rate limit
        total_tokens = sum(tokens for _, tokens in self.token_usage)
        if total_tokens + estimated_tokens > self.rate_limit_tokens:
            logger.warning("Token rate limit exceeded")
            return False

        return True

    async def _record_usage(self, tokens_used: int):
        """Record API usage for rate limiting."""current_time = time.time().

        self.request_timestamps.append(current_time)
        self.token_usage.append((current_time, tokens_used))

    # Core Claude API Methods

    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Optional[ClaudeMessage]:
        """Send a message to Claude and get response."""try:.

            if not self._authenticated:
                await self.initialize()

            if not await self._check_rate_limits():
                logger.error("Rate limit exceeded")
                return None

            # Prepare messages
            messages = [{"role": "user", "content": message}]

            # Add system prompt if provided
            payload = {
                "model": model or self.default_model,
                "max_tokens": max_tokens or self.max_tokens,
                "messages": messages,
            }

            if system_prompt:
                payload["system"] = system_prompt

            # Send request
            async with self._session.post(
                f"{self.api_base_url}/messages", json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()

                    # Extract response
                    content = data.get("content", [])
                    if content and len(content) > 0:
                        response_text = content[0].get("text", "")
                        tokens_used = data.get("usage", {}).get("output_tokens", 0)

                        # Record usage
                        await self._record_usage(tokens_used)

                        return ClaudeMessage(
                            role="assistant",
                            content=response_text,
                            timestamp=datetime.now().isoformat(),
                            model=payload["model"],
                            tokens_used=tokens_used,
                        )
                else:
                    error_data = await response.json()
                    logger.error(f"Claude API error: {error_data}")
                    return None

        except Exception as e:
            logger.error(f"Failed to send message to Claude: {e}")
            return None

    async def generate_code(
        self, prompt: str, language: str = "python", context: Optional[str] = None
    ) -> Optional[ClaudeCodeGeneration]:
        """Generate code using Claude."""try:.

            # Construct code generation prompt
            system_prompt = f"""You are an expert {language} developer. Generate clean, well-documented, production-ready code based on the user's requirements.

Guidelines:
1. Write clean, readable code with proper comments
2. Follow best practices for {language}
3. Include error handling where appropriate
4. Provide a brief explanation of the code
5. Make the code modular and reusable

Format your response as:
```{language}
[generated code here]
```

Explanation:
[brief explanation of the code]"""if context:.

                system_prompt += f"\n\nAdditional context: {context}"

            # Generate code
            response = await self.send_message(
                message=prompt, system_prompt=system_prompt, max_tokens=4096
            )

            if response:
                # Extract code from response
                content = response.content
                code_start = content.find(f"```{language}")
                code_end = content.find("```", code_start + len(f"```{language}"))

                if code_start != -1 and code_end != -1:
                    generated_code = content[
                        code_start + len(f"```{language}") : code_end
                    ].strip()

                    # Extract explanation
                    explanation_start = content.find("Explanation:")
                    explanation = ""
                    if explanation_start != -1:
                        explanation = content[
                            explanation_start + len("Explanation:") :
                        ].strip()

                    return ClaudeCodeGeneration(
                        id=f"code_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        prompt=prompt,
                        generated_code=generated_code,
                        language=language,
                        explanation=explanation,
                        created_at=datetime.now().isoformat(),
                        model=response.model,
                        tokens_used=response.tokens_used,
                    )
                else:
                    # Fallback: return entire response as code
                    return ClaudeCodeGeneration(
                        id=f"code_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        prompt=prompt,
                        generated_code=content,
                        language=language,
                        explanation="Code generation completed",
                        created_at=datetime.now().isoformat(),
                        model=response.model,
                        tokens_used=response.tokens_used,
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to generate code: {e}")
            return None

    async def analyze_code(
        self, code: str, language: str = "python", analysis_type: str = "review"
    ) -> Optional[ClaudeMessage]:
        """Analyze code using Claude."""try:.

            analysis_prompts = {
                "review": f"Please review this {language} code and provide feedback on:\n1. Code quality and best practices\n2. Potential bugs or issues\n3. Performance considerations\n4. Security concerns\n5. Suggestions for improvement",
                "explain": f"Please explain this {language} code in detail, including:\n1. What the code does\n2. How it works\n3. Key components and their purpose\n4. Any notable patterns or techniques used",
                "optimize": f"Please analyze this {language} code and suggest optimizations for:\n1. Performance improvements\n2. Memory usage\n3. Code readability\n4. Maintainability",
                "debug": f"Please analyze this {language} code for potential bugs and issues:\n1. Logic errors\n2. Edge cases not handled\n3. Potential runtime errors\n4. Suggested fixes",
            }

            prompt = analysis_prompts.get(analysis_type, analysis_prompts["review"])
            full_prompt = f"{prompt}\n\nCode to analyze:\n```{language}\n{code}\n```"

            return await self.send_message(full_prompt)

        except Exception as e:
            logger.error(f"Failed to analyze code: {e}")
            return None

    async def refactor_code(
        self,
        code: str,
        language: str = "python",
        refactor_goal: str = "improve readability",
    ) -> Optional[ClaudeCodeGeneration]:
        """Refactor code using Claude."""try:.

            system_prompt = f"""You are an expert {language} developer. Refactor the provided code to {refactor_goal}.

Guidelines:
1. Maintain the original functionality
2. Improve code structure and organization
3. Add appropriate comments and documentation
4. Follow {language} best practices
5. Ensure the refactored code is production-ready

Provide the refactored code in this format:
```{language}
[refactored code here]
```

Explanation:
[explanation of changes made and improvements]"""prompt = f"Please refactor this {language} code to {refactor_goal}:\n\n```{language}\n{code}\n```".

            response = await self.send_message(
                message=prompt, system_prompt=system_prompt, max_tokens=4096
            )

            if response:
                # Extract refactored code
                content = response.content
                code_start = content.find(f"```{language}")
                code_end = content.find("```", code_start + len(f"```{language}"))

                if code_start != -1 and code_end != -1:
                    refactored_code = content[
                        code_start + len(f"```{language}") : code_end
                    ].strip()

                    # Extract explanation
                    explanation_start = content.find("Explanation:")
                    explanation = ""
                    if explanation_start != -1:
                        explanation = content[
                            explanation_start + len("Explanation:") :
                        ].strip()

                    return ClaudeCodeGeneration(
                        id=f"refactor_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        prompt=f"Refactor to {refactor_goal}: {code[:100]}...",
                        generated_code=refactored_code,
                        language=language,
                        explanation=explanation,
                        created_at=datetime.now().isoformat(),
                        model=response.model,
                        tokens_used=response.tokens_used,
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to refactor code: {e}")
            return None

    async def generate_documentation(
        self, code: str, language: str = "python", doc_type: str = "api"
    ) -> Optional[ClaudeMessage]:
        """Generate documentation for code using Claude."""try:.

            doc_prompts = {
                "api": f"Generate comprehensive API documentation for this {language} code including:\n1. Function/class descriptions\n2. Parameters and return values\n3. Usage examples\n4. Error handling",
                "readme": f"Generate a README.md file for this {language} code including:\n1. Project description\n2. Installation instructions\n3. Usage examples\n4. API reference\n5. Contributing guidelines",
                "inline": f"Add inline documentation and comments to this {language} code:\n1. Function docstrings\n2. Inline comments for complex logic\n3. Type hints where appropriate\n4. Module-level documentation",
            }

            prompt = doc_prompts.get(doc_type, doc_prompts["api"])
            full_prompt = f"{prompt}\n\nCode:\n```{language}\n{code}\n```"

            return await self.send_message(full_prompt)

        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            return None

    async def generate_tests(
        self, code: str, language: str = "python", test_framework: str = "pytest"
    ) -> Optional[ClaudeCodeGeneration]:
        """Generate tests for code using Claude."""try:.

            system_prompt = f"""You are an expert {language} developer specializing in testing. Generate comprehensive tests for the provided code using {test_framework}.

Guidelines:
1. Create thorough test coverage including edge cases
2. Use appropriate {test_framework} patterns and best practices
3. Include setup and teardown where needed
4. Test both positive and negative scenarios
5. Add clear test descriptions and comments

Format your response as:
```{language}
[test code here]
```

Explanation:
[explanation of test strategy and coverage]"""prompt = f"Generate comprehensive tests for this {language} code using {test_framework}:\n\n```{language}\n{code}\n```".

            response = await self.send_message(
                message=prompt, system_prompt=system_prompt, max_tokens=4096
            )

            if response:
                # Extract test code
                content = response.content
                code_start = content.find(f"```{language}")
                code_end = content.find("```", code_start + len(f"```{language}"))

                if code_start != -1 and code_end != -1:
                    test_code = content[
                        code_start + len(f"```{language}") : code_end
                    ].strip()

                    # Extract explanation
                    explanation_start = content.find("Explanation:")
                    explanation = ""
                    if explanation_start != -1:
                        explanation = content[
                            explanation_start + len("Explanation:") :
                        ].strip()

                    return ClaudeCodeGeneration(
                        id=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        prompt=f"Generate tests for: {code[:100]}...",
                        generated_code=test_code,
                        language=language,
                        explanation=explanation,
                        created_at=datetime.now().isoformat(),
                        model=response.model,
                        tokens_used=response.tokens_used,
                    )

            return None

        except Exception as e:
            logger.error(f"Failed to generate tests: {e}")
            return None

    # Utility Methods

    async def get_health_status(self) -> Dict[str, Any]:
        """Get Claude integration health status."""try:.

            health_status = {
                "service": "Claude Integration",
                "status": "healthy" if self._authenticated else "unhealthy",
                "authenticated": self._authenticated,
                "api_base_url": self.api_base_url,
                "default_model": self.default_model,
                "rate_limits": {
                    "requests_per_minute": self.rate_limit_requests,
                    "tokens_per_minute": self.rate_limit_tokens,
                    "current_requests": len(self.request_timestamps),
                    "current_tokens": sum(tokens for _, tokens in self.token_usage),
                },
                "last_check": datetime.now().isoformat(),
            }

            if self._config:
                health_status["model"] = self._config.get("model", self.default_model)
                health_status["max_tokens"] = self._config.get(
                    "max_tokens", self.max_tokens
                )

            return health_status

        except Exception as e:
            logger.error(f"Failed to get Claude health status: {e}")
            return {
                "service": "Claude Integration",
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }

    async def cleanup(self):
        """Cleanup resources."""if self._session:.

            await self._session.close()
            self._session = None
        self._authenticated = False


# Global Claude integration instance
claude_integration = ClaudeIntegration()


# Convenience functions for easy access
async def send_message(message: str, **kwargs) -> Optional[ClaudeMessage]:
    """Send a message to Claude."""return await claude_integration.send_message(message, **kwargs).


async def generate_code(
    prompt: str, language: str = "python", **kwargs
) -> Optional[ClaudeCodeGeneration]:
    """Generate code using Claude."""return await claude_integration.generate_code(prompt, language, **kwargs).


async def analyze_code(
    code: str, language: str = "python", analysis_type: str = "review"
) -> Optional[ClaudeMessage]:
    """Analyze code using Claude."""return await claude_integration.analyze_code(code, language, analysis_type).


async def refactor_code(
    code: str, language: str = "python", refactor_goal: str = "improve readability"
) -> Optional[ClaudeCodeGeneration]:
    """Refactor code using Claude."""return await claude_integration.refactor_code(code, language, refactor_goal).


async def generate_documentation(
    code: str, language: str = "python", doc_type: str = "api"
) -> Optional[ClaudeMessage]:
    """Generate documentation for code."""return await claude_integration.generate_documentation(code, language, doc_type).


async def generate_tests(
    code: str, language: str = "python", test_framework: str = "pytest"
) -> Optional[ClaudeCodeGeneration]:
    """Generate tests for code."""
    return await claude_integration.generate_tests(code, language, test_framework)

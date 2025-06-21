"""OpenRouter Secret Management.

Manages OpenRouter API credentials through Pulumi ESC
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.esc.base_secrets import BaseSecretManager, SecretConfig


class OpenRouterSecretManager(BaseSecretManager):
    """Manages OpenRouter API secrets."""

    def get_service_name(self) -> str:
        return "openrouter"

    def get_required_secrets(self) -> Dict[str, SecretConfig]:
        return {
            "OPENROUTER_API_KEY": SecretConfig(
                description="OpenRouter API key for model access",
                required=True,
                validation_pattern=r"^sk-or-v1-[a-zA-Z0-9]{64}$",
            ),
            "OPENROUTER_SITE_URL": SecretConfig(
                description="Site URL for OpenRouter (required for API)",
                required=False,
                default="https://payready.com",
            ),
            "OPENROUTER_APP_NAME": SecretConfig(
                description="Application name for OpenRouter",
                required=False,
                default="Sophia AI Executive Dashboard",
            ),
        }

    def validate_secret_format(self, secret_name: str, secret_value: str) -> bool:
        """Validate OpenRouter secret format."""if secret_name == "OPENROUTER_API_KEY":.

            # OpenRouter API keys start with sk-or-v1-
            return secret_value.startswith("sk-or-v1-") and len(secret_value) == 73
        elif secret_name == "OPENROUTER_SITE_URL":
            # Must be a valid URL
            return secret_value.startswith(("http://", "https://"))
        return True

    def test_secret(self, secret_name: str, secret_value: str) -> bool:
        """Test OpenRouter secret by making API call."""if secret_name == "OPENROUTER_API_KEY":.

            try:
                import asyncio

                import aiohttp

                async def test_api():
                    async with aiohttp.ClientSession() as session:
                        headers = {
                            "Authorization": f"Bearer {secret_value}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": self.get_secret("OPENROUTER_SITE_URL")
                            or "https://payready.com",
                            "X-Title": self.get_secret("OPENROUTER_APP_NAME")
                            or "Sophia AI",
                        }

                        # Test by fetching models list
                        async with session.get(
                            "https://openrouter.ai/api/v1/models", headers=headers
                        ) as response:
                            return response.status == 200

                return asyncio.run(test_api())
            except Exception as e:
                print(f"Failed to test OpenRouter API key: {e}")
                return False

        return True

    def get_secret_metadata(self) -> Dict[str, Any]:
        """Get metadata about OpenRouter secrets."""return {.

            "service": "OpenRouter",
            "description": "AI model routing and access platform",
            "documentation": "https://openrouter.ai/docs",
            "required_for": [
                "Executive strategic chat",
                "Dynamic model selection",
                "Multi-provider AI access",
            ],
            "features": [
                "Access to 100+ AI models",
                "Automatic model routing",
                "Usage analytics",
                "Cost optimization",
            ],
        }

    def setup_local_development(self):
        """Setup OpenRouter for local development."""print("\n🤖 Setting up OpenRouter for local development...").

        # Check if API key exists
        api_key = self.get_secret("OPENROUTER_API_KEY")
        if not api_key:
            print("\n📝 To get an OpenRouter API key:")
            print("1. Go to https://openrouter.ai")
            print("2. Sign up or log in")
            print("3. Go to Keys section")
            print("4. Create a new API key")
            print("5. Copy the key (starts with sk-or-v1-)")

            api_key = input("\nEnter your OpenRouter API key: ").strip()
            if api_key:
                self.set_secret("OPENROUTER_API_KEY", api_key)

        # Set optional configurations
        site_url = self.get_secret("OPENROUTER_SITE_URL")
        if not site_url:
            site_url = input(
                "\nEnter your site URL (default: https://payready.com): "
            ).strip()
            if not site_url:
                site_url = "https://payready.com"
            self.set_secret("OPENROUTER_SITE_URL", site_url)

        # Test the configuration
        if self.test_secret("OPENROUTER_API_KEY", api_key):
            print("✅ OpenRouter API key is valid and working!")

            # Show available models
            print("\n📊 Fetching available models...")
            self._show_available_models(api_key)
        else:
            print("❌ Failed to validate OpenRouter API key")

    def _show_available_models(self, api_key: str):
        """Show available OpenRouter models."""try:.

            import asyncio

            import aiohttp

            async def fetch_models():
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }

                    async with session.get(
                        "https://openrouter.ai/api/v1/models", headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data.get("data", [])
                        return []

            models = asyncio.run(fetch_models())

            if models:
                print(f"\n✨ Found {len(models)} available models")

                # Group by provider
                providers = {}
                for model in models:
                    model_id = model.get("id", "")
                    provider = model_id.split("/")[0] if "/" in model_id else "unknown"
                    if provider not in providers:
                        providers[provider] = []
                    providers[provider].append(model)

                # Show top models by provider
                for provider, provider_models in sorted(providers.items()):
                    print(f"\n{provider.upper()} ({len(provider_models)} models):")
                    for model in provider_models[:3]:  # Show top 3 per provider
                        print(
                            f"  - {model.get('id')}: ${model.get('pricing', {}).get('prompt', 0):.6f}/token"
                        )
                    if len(provider_models) > 3:
                        print(f"  ... and {len(provider_models) - 3} more")

        except Exception as e:
            print(f"Could not fetch models: {e}")


def main():
    """Main entry point for OpenRouter secret management."""
    manager = OpenRouterSecretManager()

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "setup":
            manager.setup_local_development()
        elif command == "test":
            manager.test_secrets()
        elif command == "sync":
            manager.sync_to_github()
        elif command == "show":
            manager.show_secrets()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: setup, test, sync, show")
    else:
        # Interactive mode
        print("🤖 OpenRouter Secret Manager")
        print("\nAvailable commands:")
        print("1. setup - Setup OpenRouter for local development")
        print("2. test  - Test OpenRouter secrets")
        print("3. sync  - Sync secrets to GitHub")
        print("4. show  - Show current secrets (masked)")
        print("5. exit  - Exit")

        while True:
            choice = input("\nEnter command (1-5): ").strip()
            if choice == "1" or choice == "setup":
                manager.setup_local_development()
            elif choice == "2" or choice == "test":
                manager.test_secrets()
            elif choice == "3" or choice == "sync":
                manager.sync_to_github()
            elif choice == "4" or choice == "show":
                manager.show_secrets()
            elif choice == "5" or choice == "exit":
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

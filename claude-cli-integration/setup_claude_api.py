#!/usr/bin/env python3
"""
Setup Script for Claude API Integration with Latest Models
Helps configure Anthropic API key for Sophia AI
"""

import os
from pathlib import Path


def get_config_value(key: str) -> str:
    """Get configuration value from environment"""
    return os.getenv(key.upper()) or os.getenv(f"SOPHIA_{key.upper()}")


def setup_claude_api():
    """Setup Claude API with latest models"""

    # Check current API key
    current_key = get_config_value("anthropic_api_key")
    if current_key:
        (current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "***")

        update = input("\n🤔 Update API key? (y/N): ").strip().lower()
        if update not in ["y", "yes"]:
            return test_api_connection()
    else:
        pass

    # Get new API key

    api_key = input("API Key: ").strip()

    if not api_key:
        return False

    if not api_key.startswith("sk-"):
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm not in ["y", "yes"]:
            return False

    # Add to shell profile
    shell_profiles = [
        Path.home() / ".zshrc",
        Path.home() / ".bashrc",
        Path.home() / ".bash_profile",
    ]

    export_line = f'export ANTHROPIC_API_KEY="{api_key}"'

    for profile in shell_profiles:
        if profile.exists():
            with open(profile) as f:
                content = f.read()

            # Remove existing ANTHROPIC_API_KEY lines
            lines = [
                line
                for line in content.split("\n")
                if not line.strip().startswith("export ANTHROPIC_API_KEY=")
            ]

            # Add new key
            lines.append(export_line)

            with open(profile, "w") as f:
                f.write("\n".join(lines))

            break
    else:
        # Create .zshrc if no profile exists
        zshrc = Path.home() / ".zshrc"
        with open(zshrc, "a") as f:
            f.write(f"\n{export_line}\n")

    # Set for current session
    os.environ["ANTHROPIC_API_KEY"] = api_key

    return test_api_connection()


def test_api_connection():
    """Test the API connection"""

    try:
        import subprocess

        result = subprocess.run(
            ["python", "claude-cli-integration/claude_cli.py", "models"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        return result.returncode == 0
    except Exception:
        return False


def show_usage_examples():
    """Show usage examples"""

    examples = [
        (
            "Code Generation",
            './claude-cli-integration/claude chat "Generate a Python function to parse CSV files"',
        ),
        (
            "Design Analysis",
            './claude-cli-integration/claude chat "Analyze this React component design"',
        ),
        (
            "Business Query",
            'python unified_ai_assistant.py "Analyze our sales performance"',
        ),
        ("Infrastructure", 'python unified_ai_assistant.py "Check system health"'),
        ("Interactive Mode", "python unified_ai_assistant.py"),
    ]

    for _desc, _cmd in examples:
        pass


def main():
    """Main setup function"""
    try:
        success = setup_claude_api()

        if success:
            show_usage_examples()
        else:
            pass

    except KeyboardInterrupt:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    main()

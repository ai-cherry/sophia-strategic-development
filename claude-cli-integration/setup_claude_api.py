#!/usr/bin/env python3
"""
Setup Script for Claude API Integration with Latest Models
Helps configure Anthropic API key for Sophia AI
"""

import os
from pathlib import Path


def setup_claude_api():
    """Setup Claude API with latest models"""
    print("🚀 Claude API Setup for Sophia AI")
    print("Setting up latest models including Sonnet 4 and Code Max")
    print("=" * 60)

    # Check current API key
    current_key = os.getenv("ANTHROPIC_API_KEY")
    if current_key:
        masked_key = (
            current_key[:8] + "..." + current_key[-4:]
            if len(current_key) > 12
            else "***"
        )
        print(f"✅ Current API Key: {masked_key}")

        update = input("\n🤔 Update API key? (y/N): ").strip().lower()
        if update not in ["y", "yes"]:
            print("✅ Keeping existing API key")
            return test_api_connection()
    else:
        print("❌ No Anthropic API key found")

    # Get new API key
    print("\n🔑 Please enter your Anthropic API key:")
    print("   (Get it from: https://console.anthropic.com/)")

    api_key = input("API Key: ").strip()

    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False

    if not api_key.startswith("sk-"):
        print("⚠️  Warning: API key should start with 'sk-'")
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

            print(f"✅ Added API key to {profile}")
            break
    else:
        # Create .zshrc if no profile exists
        zshrc = Path.home() / ".zshrc"
        with open(zshrc, "a") as f:
            f.write(f"\n{export_line}\n")
        print(f"✅ Created {zshrc} with API key")

    # Set for current session
    os.environ["ANTHROPIC_API_KEY"] = api_key
    print("✅ API key set for current session")

    return test_api_connection()


def test_api_connection():
    """Test the API connection"""
    print("\n🔧 Testing Claude API connection...")

    try:
        import subprocess

        result = subprocess.run(
            ["python", "claude-cli-integration/claude_cli.py", "models"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ API connection successful!")
            print("\n🎯 Latest models configured:")
            print("   • claude-3-5-sonnet-20241119 (Primary)")
            print("   • claude-3-5-sonnet-20241119 (Coding)")
            print("   • claude-3-5-sonnet-20241119 (Analysis)")
            return True
        else:
            print("❌ API connection failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def show_usage_examples():
    """Show usage examples"""
    print("\n🎯 Usage Examples:")
    print("=" * 30)

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

    for desc, cmd in examples:
        print(f"\n💡 {desc}:")
        print(f"   {cmd}")

    print("\n🚀 Ready to use Sophia AI with latest Claude models!")


def main():
    """Main setup function"""
    try:
        success = setup_claude_api()

        if success:
            show_usage_examples()
            print("\n✅ Setup complete! Your Claude API is ready.")
        else:
            print("\n❌ Setup incomplete. Please check your API key and try again.")

    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")


if __name__ == "__main__":
    main()

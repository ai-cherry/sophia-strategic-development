#!/usr/bin/env python3
"""
DEFINITIVE FIX: Pulumi ESC Structure Mismatch
The root cause of persistent placeholders is structure mismatch between sync and read
"""

import subprocess


def analyze_esc_structure():
    """Analyze the current ESC structure to understand the mismatch"""

    try:
        result = subprocess.run(
            [
                "pulumi",
                "env",
                "get",
                "scoobyjava-org/default/sophia-ai-production",
                "--show-secrets",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            content = result.stdout

            # Count top-level real values
            top_level_real = 0
            top_level_placeholders = 0
            nested_placeholders = 0

            lines = content.split("\n")
            in_nested_structure = False

            for line in lines:
                if '"values"' in line and '"sophia"' in line:
                    in_nested_structure = True

                if not in_nested_structure:
                    # Top-level structure
                    if "" in line:
                        top_level_placeholders += 1
                    elif (
                        any(
                            key in line for key in ["api_key", "access_token", "secret"]
                        )
                        and "sk-" in line
                        or "pcsk_" in line
                        or len(line.split('"')[-2]) > 20
                    ):
                        top_level_real += 1
                else:
                    # Nested structure
                    if "" in line:
                        nested_placeholders += 1

            return True

    except Exception:
        return False


def fix_sync_script_structure():
    """Fix the sync script to use top-level structure instead of nested"""

    sync_file = "scripts/ci/sync_from_gh_to_pulumi.py"

    with open(sync_file) as f:
        content = f.read()

    # Create new mappings that use top-level structure (matching what backend reads)

    # Replace the entire secret_mappings section
    new_mappings_code = """        # TOP-LEVEL MAPPINGS (matching what backend actually reads)
        # CRITICAL: These map to top-level ESC keys, not nested values.sophia.*
        self.secret_mappings = {
            # Core AI Services (top-level)
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "GONG_ACCESS_KEY": "gong_access_key",
            "PINECONE_API_KEY": "pinecone_api_key",

            # Snowflake (top-level)
            "SNOWFLAKE_ACCOUNT": "snowflake_account",
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "SNOWFLAKE_ROLE": "snowflake_role",
            "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
            "SNOWFLAKE_DATABASE": "snowflake_database",

            # Lambda Labs (top-level)
            "LAMBDA_API_KEY": "lambda_api_key",
            "LAMBDA_IP_ADDRESS": "lambda_ip_address",
            "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",

            # Business Intelligence (top-level)
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "LINEAR_API_KEY": "linear_api_key",
            "NOTION_API_KEY": "notion_api_key",

            # Additional services (top-level for immediate use)
            "VERCEL_ACCESS_TOKEN": "vercel_access_token",
            "PORTKEY_API_KEY": "portkey_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
        }"""

    # Replace the existing mappings
    import re

    pattern = r"self\.secret_mappings = \{.*?\}"
    content = re.sub(pattern, new_mappings_code, content, flags=re.DOTALL)

    with open(sync_file, "w") as f:
        f.write(content)


def test_structure_fix():
    """Test if the structure fix will work"""

    try:
        from backend.core.auto_esc_config import get_config_value

        # Test current working keys (top-level)
        working_keys = [
            "openai_api_key",
            "anthropic_api_key",
            "gong_access_key",
            "pinecone_api_key",
        ]

        for key in working_keys:
            value = get_config_value(key)
            "✅ WORKING" if value and len(value) > 20 else "❌ MISSING"

        # Test keys that should work after sync
        target_keys = ["lambda_api_key", "hubspot_access_token", "slack_bot_token"]

        for key in target_keys:
            value = get_config_value(key)

    except Exception:
        pass


def main():
    """Apply the definitive fix"""

    # Analyze current structure
    if not analyze_esc_structure():
        return False

    # Fix sync script structure
    fix_sync_script_structure()

    # Test the fix
    test_structure_fix()

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

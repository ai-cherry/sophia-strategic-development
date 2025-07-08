#!/usr/bin/env python3
"""
Sync secrets from GitHub to Pulumi ESC
Uses the canonical mapping from secret_mapping.py
"""

import json
import os
import subprocess
import sys

# Add security module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "security"))
from secret_mapping import SecretCategory, get_all_mappings


def run_pulumi_command(args: list[str]) -> tuple[bool, str, str]:
    """Run a Pulumi command and return success, stdout, stderr"""
    env = os.environ.copy()
    env["PULUMI_SKIP_UPDATE_CHECK"] = "true"

    try:
        result = subprocess.run(
            ["pulumi"] + args, capture_output=True, text=True, env=env, check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def sync_secrets():
    """Sync all secrets from GitHub to Pulumi ESC"""

    # Configuration
    esc_environment = "scoobyjava-org/default/sophia-ai-production"

    print("🔄 Starting Secret Sync: GitHub → Pulumi ESC")
    print(f"Target Environment: {esc_environment}")
    print("=" * 60)

    # Track results
    synced = []
    failed = []
    skipped = []

    # Get all mappings
    all_mappings = get_all_mappings()

    # Group by category for organized output
    for category in SecretCategory:
        category_mappings = [m for m in all_mappings if m.category == category]
        if not category_mappings:
            continue

        print(f"\n📁 {category.value.replace('_', ' ').title()}")
        print("-" * 40)

        for mapping in category_mappings:
            # Get secret value from environment
            env_key = f"SECRET_{mapping.github_name}"
            secret_value = os.environ.get(env_key, "")

            if not secret_value:
                if mapping.required:
                    print(f"❌ {mapping.github_name} → MISSING (required)")
                    failed.append((mapping.github_name, "Missing required secret"))
                else:
                    print(f"⏭️  {mapping.github_name} → SKIPPED (optional)")
                    skipped.append(mapping.github_name)
                continue

            # Check for placeholders
            if any(
                p in secret_value.upper()
                for p in ["PLACEHOLDER", "YOUR_", "REPLACE_ME"]
            ):
                print(f"⚠️  {mapping.github_name} → PLACEHOLDER DETECTED")
                failed.append((mapping.github_name, "Placeholder value"))
                continue

            # Sync to Pulumi ESC
            args = [
                "env",
                "set",
                esc_environment,
                mapping.esc_path,
                secret_value,
                "--secret",
            ]

            success, stdout, stderr = run_pulumi_command(args)

            if success:
                # Mask the value in output
                masked_value = (
                    secret_value[:4] + "***" + secret_value[-4:]
                    if len(secret_value) > 8
                    else "***"
                )
                print(f"✅ {mapping.github_name} → {mapping.esc_path} ({masked_value})")
                synced.append(mapping.github_name)
            else:
                print(f"❌ {mapping.github_name} → FAILED: {stderr}")
                failed.append((mapping.github_name, stderr))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SYNC SUMMARY")
    print("=" * 60)
    print(f"✅ Synced: {len(synced)} secrets")
    print(f"❌ Failed: {len(failed)} secrets")
    print(f"⏭️  Skipped: {len(skipped)} optional secrets")
    print(f"📋 Total: {len(all_mappings)} mappings")

    if failed:
        print("\n❌ Failed Secrets:")
        for secret, reason in failed:
            print(f"  - {secret}: {reason}")

    # Generate report
    report = {
        "environment": esc_environment,
        "total_mappings": len(all_mappings),
        "synced": synced,
        "failed": [{"secret": s, "reason": r} for s, r in failed],
        "skipped": skipped,
        "success_rate": len(synced) / len(all_mappings) * 100 if all_mappings else 0,
    }

    with open("sync_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📄 Detailed report saved to: sync_report.json")

    # Exit with error if any required secrets failed
    if failed:
        print("\n❌ SYNC FAILED: Some secrets could not be synced")
        sys.exit(1)
    else:
        print("\n✅ SYNC SUCCESSFUL: All required secrets synced to Pulumi ESC")

        # Verify by reading back one secret
        print("\n🔍 Verifying sync...")
        test_args = ["env", "get", esc_environment, "values.sophia.ai.openai_api_key"]
        success, stdout, stderr = run_pulumi_command(test_args)

        if success and stdout.strip() and not stdout.strip().startswith("PLACEHOLDER"):
            print("✅ Verification successful - secrets are accessible in ESC")
        else:
            print("⚠️  Verification warning - could not read back test secret")


if __name__ == "__main__":
    # Ensure we're logged into Pulumi
    success, stdout, stderr = run_pulumi_command(["whoami"])
    if not success:
        print("❌ Not logged into Pulumi. Please set PULUMI_ACCESS_TOKEN")
        sys.exit(1)

    print(f"👤 Logged in as: {stdout.strip()}")

    # Run sync
    sync_secrets()

#!/usr/bin/env python3
"""Qdrant vector database"""
    print(f"Setting {github_name} → {pulumi_key}")

    cmd = [
        "pulumi",
        "env",
        "set",
        "scoobyjava-org/default/sophia-ai-production",
        "--secret",
        pulumi_key,
        value_placeholder,
    ]

    result = subprocess.run(cmd, check=False, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Set {pulumi_key}")
        return True
    else:
        print(f"❌ Failed to set {pulumi_key}: {result.stderr}")
        return False

def main():
    print("🚀 Mapping ALL GitHub Secrets to Pulumi ESC")
    print("=" * 60)
    print(f"Total secrets to map: {len(GITHUB_TO_PULUMI_MAPPING)}")

    success_count = 0
    fail_count = 0

    # Map each secret
    for github_name, pulumi_key in GITHUB_TO_PULUMI_MAPPING.items():
        if set_secret_in_pulumi(github_name, pulumi_key):
            success_count += 1
        else:
            fail_count += 1

    print("\n📊 Results:")
    print(f"✅ Successfully mapped: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📋 Total: {len(GITHUB_TO_PULUMI_MAPPING)}")

    print("\n📝 Next steps:")
    print("1. GitHub Actions workflows will automatically use these secrets")
    print("2. Backend auto_esc_config.py will load them automatically")
    print("3. Test Docker login: python3 scripts/use_docker_from_pulumi.py")
    print("4. Deploy to Lambda Labs")

    print("\n⚠️  NOTE: The actual secret values need to be synced from GitHub")
    print("This script creates the mapping structure in Pulumi ESC")

if __name__ == "__main__":
    main()

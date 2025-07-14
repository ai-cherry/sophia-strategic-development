#!/usr/bin/env python3
"""
Update ALL workflows, CI/CD, CLI configs, and everything else to use correct GitHub secret names.
This ensures complete consistency across the entire codebase.
"""

import glob
import re

# Standard GitHub secret names (what we have in GitHub Organization)
STANDARD_SECRET_NAMES = {
    # Docker - Use DOCKER_TOKEN (not DOCKER_TOKEN)
    "DOCKER_TOKEN": "DOCKER_TOKEN",
    "DOCKER_TOKEN": "DOCKER_TOKEN",
    "DOCKERHUB_TOKEN": "DOCKER_TOKEN",
    "DOCKER_TOKEN": "DOCKER_TOKEN",
    "DOCKER_TOKEN": "DOCKER_TOKEN",
    "DOCKER_TOKEN": "DOCKER_TOKEN",
    # Docker Username - Use DOCKERHUB_USERNAME
    "DOCKERHUB_USERNAME": "DOCKERHUB_USERNAME",
    "DOCKERHUB_USERNAME": "DOCKERHUB_USERNAME",
    "DOCKERHUB_USERNAME": "DOCKERHUB_USERNAME",
    "DOCKERHUB_USERNAME": "DOCKERHUB_USERNAME",
    # GitHub - Use GH_API_TOKEN
    "GITHUB_TOKEN": "GH_API_TOKEN",
    "GITHUB_ACCESS_TOKEN": "GH_API_TOKEN",
    "GH_TOKEN": "GH_API_TOKEN",
    # Pulumi - Use PULUMI_ACCESS_TOKEN
    "PULUMI_TOKEN": "PULUMI_ACCESS_TOKEN",
    # Snowflake - Standardize
    "SNOWFLAKE_ACCOUNT_IDENTIFIER": "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USERNAME": "SNOWFLAKE_USER",
    "SNOWFLAKE_DB": "SNOWFLAKE_DATABASE",
    # Lambda Labs - Use LAMBDA_LABS_API_KEY
    "LAMBDA_API_KEY": "LAMBDA_LABS_API_KEY",
    "LAMBDA_CLOUD_API_KEY": "LAMBDA_LABS_API_KEY",
    # Slack - Standardize
    "SLACK_TOKEN": "SLACK_BOT_TOKEN",
    # Linear - Use LINEAR_API_KEY
    "LINEAR_TOKEN": "LINEAR_API_KEY",
    # Notion - Use NOTION_API_TOKEN
    "NOTION_API_KEY": "NOTION_API_TOKEN",
    # HubSpot - Use HUBSPOT_ACCESS_TOKEN
    "HUBSPOT_API_KEY": "HUBSPOT_ACCESS_TOKEN",
    "HUBSPOT_TOKEN": "HUBSPOT_ACCESS_TOKEN",
    # Gong - Use GONG_ACCESS_KEY
    "GONG_API_KEY": "GONG_ACCESS_KEY",
    "GONG_TOKEN": "GONG_ACCESS_KEY",
    # Vercel - Use VERCEL_ACCESS_TOKEN
    "VERCEL_TOKEN": "VERCEL_ACCESS_TOKEN",
    # Asana - Use ASANA_API_TOKEN
    "ASANA_API_KEY": "ASANA_API_TOKEN",
    "ASANA_TOKEN": "ASANA_API_TOKEN",
}


def update_file_secrets(file_path, content):
    """Update secret names in file content"""
    updated_content = content
    changes_made = []

    for old_name, new_name in STANDARD_SECRET_NAMES.items():
        # Pattern to match secret references in various formats
        patterns = [
            rf"\$\{{\s*secrets\.{old_name}\s*\}}",  # ${{ secrets.OLD_NAME }}
            rf"secrets\.{old_name}",  # secrets.OLD_NAME
            rf"env:\s*\n\s*{old_name}:",  # env: OLD_NAME:
            rf"{old_name}:\s*\$\{{\s*secrets\.",  # OLD_NAME: ${{ secrets.
            rf"--secret\s+{old_name.lower()}",  # --secret old_name
            rf"export\s+{old_name}=",  # export OLD_NAME=
            rf"{old_name}=\$\{{\s*secrets\.",  # OLD_NAME=${{ secrets.
        ]

        for pattern in patterns:
            if re.search(pattern, updated_content, re.IGNORECASE):
                # Replace with new name
                updated_content = re.sub(
                    pattern,
                    lambda m: m.group(0).replace(old_name, new_name),
                    updated_content,
                    flags=re.IGNORECASE,
                )
                changes_made.append(f"{old_name} → {new_name}")

    return updated_content, changes_made


def update_workflows():
    """Update all GitHub Actions workflows"""
    print("🔄 Updating GitHub Actions workflows...")

    workflow_files = glob.glob(".github/workflows/*.yml") + glob.glob(
        ".github/workflows/*.yaml"
    )

    for workflow_file in workflow_files:
        try:
            with open(workflow_file) as f:
                content = f.read()

            updated_content, changes = update_file_secrets(workflow_file, content)

            if changes:
                with open(workflow_file, "w") as f:
                    f.write(updated_content)
                print(f"✅ Updated {workflow_file}: {', '.join(changes)}")
            else:
                print(f"⚪ No changes needed in {workflow_file}")

        except Exception as e:
            print(f"❌ Error updating {workflow_file}: {e}")


def update_docker_files():
    """Update all Docker files and docker-compose files"""
    print("\n🐳 Updating Docker files...")

    docker_files = (
        glob.glob("**/Dockerfile*", recursive=True)
        + glob.glob("**/docker-compose*.yml", recursive=True)
        + glob.glob("**/docker-compose*.yaml", recursive=True)
    )

    for docker_file in docker_files:
        try:
            with open(docker_file) as f:
                content = f.read()

            updated_content, changes = update_file_secrets(docker_file, content)

            if changes:
                with open(docker_file, "w") as f:
                    f.write(updated_content)
                print(f"✅ Updated {docker_file}: {', '.join(changes)}")
            else:
                print(f"⚪ No changes needed in {docker_file}")

        except Exception as e:
            print(f"❌ Error updating {docker_file}: {e}")


def update_scripts():
    """Update all shell and Python scripts"""
    print("\n📜 Updating scripts...")

    script_files = (
        glob.glob("scripts/*.py")
        + glob.glob("scripts/*.sh")
        + glob.glob("scripts/**/*.py", recursive=True)
        + glob.glob("scripts/**/*.sh", recursive=True)
    )

    for script_file in script_files:
        try:
            with open(script_file) as f:
                content = f.read()

            updated_content, changes = update_file_secrets(script_file, content)

            if changes:
                with open(script_file, "w") as f:
                    f.write(updated_content)
                print(f"✅ Updated {script_file}: {', '.join(changes)}")
            else:
                print(f"⚪ No changes needed in {script_file}")

        except Exception as e:
            print(f"❌ Error updating {script_file}: {e}")


def update_config_files():
    """Update all configuration files"""
    print("\n⚙️  Updating configuration files...")

    config_files = (
        glob.glob("config/**/*.json", recursive=True)
        + glob.glob("config/**/*.yaml", recursive=True)
        + glob.glob("config/**/*.yml", recursive=True)
        + glob.glob("infrastructure/**/*.py", recursive=True)
        + glob.glob("infrastructure/**/*.ts", recursive=True)
        + glob.glob("backend/**/*.py", recursive=True)
    )

    for config_file in config_files:
        try:
            with open(config_file) as f:
                content = f.read()

            updated_content, changes = update_file_secrets(config_file, content)

            if changes:
                with open(config_file, "w") as f:
                    f.write(updated_content)
                print(f"✅ Updated {config_file}: {', '.join(changes)}")
            else:
                print(f"⚪ No changes needed in {config_file}")

        except Exception as e:
            print(f"❌ Error updating {config_file}: {e}")


def update_kubernetes_manifests():
    """Update Kubernetes manifests"""
    print("\n☸️  Updating Kubernetes manifests...")

    k8s_files = glob.glob("kubernetes/**/*.yaml", recursive=True) + glob.glob(
        "kubernetes/**/*.yml", recursive=True
    )

    for k8s_file in k8s_files:
        try:
            with open(k8s_file) as f:
                content = f.read()

            updated_content, changes = update_file_secrets(k8s_file, content)

            if changes:
                with open(k8s_file, "w") as f:
                    f.write(updated_content)
                print(f"✅ Updated {k8s_file}: {', '.join(changes)}")
            else:
                print(f"⚪ No changes needed in {k8s_file}")

        except Exception as e:
            print(f"❌ Error updating {k8s_file}: {e}")


def main():
    print(
        "🚀 Updating ALL workflows, CI/CD, CLI, and configs for consistent secret names"
    )
    print("=" * 80)

    # Update different file types
    update_workflows()
    update_docker_files()
    update_scripts()
    update_config_files()
    update_kubernetes_manifests()

    print("\n✅ ALL FILES UPDATED!")
    print("\n📋 Summary of standardized secret names:")
    for old_name, new_name in STANDARD_SECRET_NAMES.items():
        print(f"  {old_name} → {new_name}")

    print("\n🚀 Next steps:")
    print("1. Commit all changes")
    print("2. Push to GitHub to trigger workflows")
    print("3. GitHub Actions will use correct secret names")
    print("4. Pulumi ESC will load secrets automatically")
    print("5. Deploy to Lambda Labs")


if __name__ == "__main__":
    main()

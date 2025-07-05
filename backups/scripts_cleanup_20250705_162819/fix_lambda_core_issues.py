#!/usr/bin/env python3
"""
Lambda Labs Core Issues Fix Script
=================================

Fixes the most critical issues identified in Lambda Labs deployment testing:
1. Generate requirements.txt from pyproject.toml
2. Fix Dockerfile to use requirements.txt
3. Create environment variables template

Date: July 5, 2025
"""

import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_requirements():
    """Generate requirements.txt from pyproject.toml"""
    logger.info("🔧 FIX 1: Generating requirements.txt from pyproject.toml")

    try:
        # Try UV export first
        result = subprocess.run(
            [
                "uv",
                "export",
                "--format",
                "requirements-txt",
                "--output-file",
                "requirements.txt",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info("✅ Generated requirements.txt from pyproject.toml using UV")

            # Create requirements.docker.txt as alias
            shutil.copy("requirements.txt", "requirements.docker.txt")
            logger.info("✅ Created requirements.docker.txt alias")
            return True

        else:
            # Fallback: create basic requirements.txt
            logger.warning("⚠️ UV export failed, creating manual requirements.txt")

            basic_requirements = """fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
python-multipart==0.0.20
snowflake-connector-python[pandas]==3.12.3
openai==1.58.1
anthropic==0.40.0
pinecone-client==5.0.1
requests==2.32.3
redis==5.2.1
asyncio-compat==0.1.2
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
aiofiles==24.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
"""

            with open("requirements.txt", "w") as f:
                f.write(basic_requirements)
            with open("requirements.docker.txt", "w") as f:
                f.write(basic_requirements)

            logger.info("✅ Created manual requirements files")
            return True

    except Exception as e:
        logger.error(f"❌ Requirements fix failed: {e}")
        return False


def fix_dockerfile():
    """Update Dockerfile to use requirements.txt instead of requirements.docker.txt"""
    logger.info("🔧 FIX 2: Updating Dockerfile for compatibility")

    try:
        dockerfile_path = Path("Dockerfile.production")
        if not dockerfile_path.exists():
            logger.error("❌ Dockerfile.production not found")
            return False

        # Backup original
        backup_path = Path(
            f"Dockerfile.production.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy(dockerfile_path, backup_path)
        logger.info(f"📁 Backed up original to {backup_path}")

        # Read and fix Dockerfile
        with open(dockerfile_path) as f:
            content = f.read()

        # Replace requirements.docker.txt with requirements.txt
        fixed_content = content.replace("requirements.docker.txt", "requirements.txt")

        # Add fallback for missing requirements
        if "COPY requirements.txt" not in fixed_content:
            # Insert requirements copy after WORKDIR
            lines = fixed_content.split("\n")
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.startswith("WORKDIR"):
                    new_lines.append("")
                    new_lines.append("# Copy requirements first for better caching")
                    new_lines.append("COPY requirements.txt ./")

            fixed_content = "\n".join(new_lines)

        with open(dockerfile_path, "w") as f:
            f.write(fixed_content)

        logger.info("✅ Updated Dockerfile to use requirements.txt")
        return True

    except Exception as e:
        logger.error(f"❌ Dockerfile fix failed: {e}")
        return False


def create_env_template():
    """Create environment variables template"""
    logger.info("🔧 FIX 3: Creating environment variables template")

    try:
        env_content = f"""# Lambda Labs Deployment Environment Variables
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Docker Hub Configuration
export DOCKER_USER_NAME="scoobyjava15"
export DOCKER_PERSONAL_ACCESS_TOKEN="your_docker_hub_token_here"

# Lambda Labs Configuration
export LAMBDA_LABS_API_KEY="your_lambda_labs_api_key_here"
export LAMBDA_LABS_INSTANCE_IP="146.235.200.1"

# Pulumi Configuration (Already configured)
export PULUMI_ORG="scoobyjava-org"

# Application Configuration
export ENVIRONMENT="prod"

echo "🔧 Lambda Labs environment variables loaded"
echo "📋 Fill in missing values and run: python scripts/validate_deployment_env.py"
"""

        with open(".env.lambda-labs", "w") as f:
            f.write(env_content)

        logger.info("✅ Created environment template: .env.lambda-labs")
        return True

    except Exception as e:
        logger.error(f"❌ Environment template creation failed: {e}")
        return False


def main():
    """Main execution function"""
    print("🔧 Lambda Labs Core Issues Fix")
    print("=" * 40)
    print("📅 Date: July 5, 2025")
    print("")

    fixes = [
        ("Generate requirements.txt", fix_requirements),
        ("Fix Dockerfile", fix_dockerfile),
        ("Create environment template", create_env_template),
    ]

    success_count = 0

    for description, fix_func in fixes:
        try:
            if fix_func():
                success_count += 1
            else:
                logger.error(f"❌ {description} failed")
        except Exception as e:
            logger.error(f"❌ {description} failed with error: {e}")

    print("")
    print(f"📊 RESULTS: {success_count}/{len(fixes)} fixes applied successfully")

    if success_count == len(fixes):
        print("🎉 All core fixes applied successfully!")
        print("")
        print("📋 NEXT STEPS:")
        print("1. Fill in missing values in .env.lambda-labs")
        print("2. Run: source .env.lambda-labs")
        print("3. Run: python scripts/validate_deployment_env.py")
        print("4. Test Docker build: docker build -t test -f Dockerfile.production .")
        return 0
    else:
        print(f"⚠️ {len(fixes) - success_count} fixes failed - check logs above")
        return 1


if __name__ == "__main__":
    exit(main())

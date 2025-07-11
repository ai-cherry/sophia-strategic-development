#!/usr/bin/env python3
"""
Deploy Sophia AI backend to Railway
"""
import subprocess
import sys


def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "SUCCESS": "\033[92m",
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "INFO": "\033[94m",
        "HEADER": "\033[95m",
    }
    reset = "\033[0m"
    color = colors.get(status, "")
    symbol = (
        "✅"
        if status == "SUCCESS"
        else "❌"
        if status == "ERROR"
        else "⚠️"
        if status == "WARNING"
        else "ℹ️"
    )
    print(f"{color}{symbol} {message}{reset}")


def create_railway_config():
    """Create Railway configuration file"""
    config = """
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python backend/app/unified_chat_backend.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "services": {
    "backend": {
      "envVars": {
        "PORT": "8001",
        "ENVIRONMENT": "production",
        "SNOWFLAKE_ACCOUNT": "${{SNOWFLAKE_ACCOUNT}}",
        "SNOWFLAKE_USER": "${{SNOWFLAKE_USER}}",
        "SNOWFLAKE_PAT": "${{SNOWFLAKE_PAT}}",
        "REDIS_URL": "${{REDIS_URL}}",
        "OPENAI_API_KEY": "${{OPENAI_API_KEY}}"
      }
    }
  }
}
"""
    with open("railway.json", "w") as f:
        f.write(config.strip())
    print_status("Created railway.json configuration", "SUCCESS")


def create_nixpacks_config():
    """Create nixpacks configuration for Railway"""
    config = """
[phases.setup]
nixPkgs = ["python312", "gcc", "postgresql"]

[phases.install]
cmds = ["pip install -r backend/requirements.txt"]

[phases.build]
cmds = ["echo 'Build complete'"]

[start]
cmd = "cd backend && python app/unified_chat_backend.py"
"""
    with open("nixpacks.toml", "w") as f:
        f.write(config.strip())
    print_status("Created nixpacks.toml configuration", "SUCCESS")


def create_procfile():
    """Create Procfile for Railway"""
    procfile = """web: cd backend && python app/unified_chat_backend.py"""
    with open("Procfile", "w") as f:
        f.write(procfile.strip())
    print_status("Created Procfile", "SUCCESS")


def main():
    print_status("DEPLOYING SOPHIA AI BACKEND TO RAILWAY", "HEADER")
    print("=" * 60)

    # Check if Railway CLI is installed
    try:
        subprocess.run(["railway", "--version"], capture_output=True, check=True)
        print_status("Railway CLI is installed", "SUCCESS")
    except:
        print_status("Railway CLI not found", "ERROR")
        print("\nInstall Railway CLI:")
        print("brew install railway")
        print("or")
        print("npm install -g @railway/cli")
        sys.exit(1)

    # Create configuration files
    create_railway_config()
    create_nixpacks_config()
    create_procfile()

    print("\n" + "=" * 60)
    print_status("NEXT STEPS", "HEADER")
    print("\n1. Login to Railway:")
    print("   railway login")

    print("\n2. Create a new project:")
    print("   railway init")

    print("\n3. Link to existing project or create new:")
    print("   railway link")

    print("\n4. Add environment variables:")
    print("   railway variables set SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222")
    print("   railway variables set SNOWFLAKE_USER=SCOOBYJAVA15")
    print("   railway variables set SNOWFLAKE_PAT=<your-pat-token>")
    print("   railway variables set REDIS_URL=<railway-redis-url>")

    print("\n5. Deploy:")
    print("   railway up")

    print("\n6. Get your deployment URL:")
    print("   railway domain")

    print("\n" + "=" * 60)
    print_status(
        "Configuration files created. Follow the steps above to deploy!", "SUCCESS"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Deploy Sophia AI Backend to AWS Lambda (Serverless)
No servers to manage, auto-scaling, pay per request!
"""

import os
import subprocess


def create_serverless_yml():
    """Create serverless.yml for AWS Lambda deployment"""
    serverless_config = """service: sophia-ai-backend

provider:
  name: aws
  runtime: python3.12
  stage: ${opt:stage, 'prod'}
  region: ${opt:region, 'us-east-1'}
  environment:
    ENVIRONMENT: prod
    SNOWFLAKE_ACCOUNT: ${env:SNOWFLAKE_ACCOUNT}
    SNOWFLAKE_USER: ${env:SNOWFLAKE_USER}
    SNOWFLAKE_PRIVATE_KEY_PASSPHRASE: ${env:SNOWFLAKE_PRIVATE_KEY_PASSPHRASE}
    REDIS_URL: ${env:REDIS_URL}
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    ANTHROPIC_API_KEY: ${env:ANTHROPIC_API_KEY}
  apiGateway:
    binaryMediaTypes:
      - '*/*'

functions:
  api:
    handler: backend/app/lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
      - http:
          path: /
          method: ANY
          cors: true
    timeout: 30
    memorySize: 1024

plugins:
  - serverless-python-requirements
  - serverless-offline

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
    strip: false
    layer: true
    fileName: backend/requirements.txt
"""

    with open("serverless.yml", "w") as f:
        f.write(serverless_config)

    print("✅ Created serverless.yml")


def create_lambda_handler():
    """Create Lambda handler wrapper for FastAPI"""
    handler_code = '''"""
AWS Lambda handler for Sophia AI Backend
"""
from mangum import Mangum
from backend.app.unified_chat_backend import app

# Create the Lambda handler
handler = Mangum(app, lifespan="off")
'''

    os.makedirs("backend/app", exist_ok=True)
    with open("backend/app/lambda_handler.py", "w") as f:
        f.write(handler_code)

    print("✅ Created Lambda handler")


def update_requirements():
    """Add Lambda-specific requirements"""
    with open("backend/requirements.txt", "r") as f:
        requirements = f.read()

    if "mangum" not in requirements:
        requirements += "\nmangum==0.17.0  # AWS Lambda adapter for FastAPI\n"

    with open("backend/requirements.txt", "w") as f:
        f.write(requirements)

    print("✅ Updated requirements.txt with mangum")


def install_serverless():
    """Install Serverless Framework if not present"""
    result = subprocess.run("which serverless", shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing Serverless Framework...")
        subprocess.run("npm install -g serverless", shell=True)
        subprocess.run("npm install -g serverless-python-requirements", shell=True)
        subprocess.run("npm install -g serverless-offline", shell=True)
    else:
        print("✅ Serverless Framework already installed")


def create_env_template():
    """Create .env template for Lambda"""
    env_template = """# AWS Lambda Environment Variables
# Add these to your AWS Lambda console or use AWS Secrets Manager

SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=your_passphrase_here
REDIS_URL=redis://your-redis-endpoint:6379
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
"""

    with open(".env.lambda", "w") as f:
        f.write(env_template)

    print("✅ Created .env.lambda template")


def main():
    print("🚀 DEPLOYING SOPHIA AI TO AWS LAMBDA")
    print("=" * 50)

    # Check for AWS credentials
    aws_creds = subprocess.run(
        "aws sts get-caller-identity", shell=True, capture_output=True
    )
    if aws_creds.returncode != 0:
        print("❌ AWS credentials not configured!")
        print("Please run: aws configure")
        print("Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return

    print("✅ AWS credentials found")

    # Create necessary files
    create_serverless_yml()
    create_lambda_handler()
    update_requirements()
    create_env_template()
    install_serverless()

    print("\n📦 Installing Python requirements...")
    subprocess.run("pip install mangum", shell=True)

    print("\n🚀 READY TO DEPLOY!")
    print("=" * 50)
    print("To deploy to AWS Lambda:")
    print("\n1. Set environment variables:")
    print("   export SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222")
    print("   export SNOWFLAKE_USER=SCOOBYJAVA15")
    print("   export SNOWFLAKE_PRIVATE_KEY_PASSPHRASE=your_passphrase")
    print("   export REDIS_URL=redis://your-redis-endpoint:6379")
    print("   export OPENAI_API_KEY=your_key")
    print("   export ANTHROPIC_API_KEY=your_key")
    print("\n2. Deploy:")
    print("   serverless deploy")
    print("\n3. Or test locally first:")
    print("   serverless offline")
    print("\n🎯 Your API will be available at:")
    print("   https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod")
    print("\n💡 Benefits:")
    print("   - No servers to manage")
    print("   - Auto-scaling")
    print("   - Pay only for requests")
    print("   - Built-in HTTPS")
    print("   - Global availability")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Deploy Sophia AI with Lambda Labs Serverless Inference API
Use Lambda's ultra-cheap AI inference ($0.015/M tokens) for all LLM calls
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv("local.env")


def configure_lambda_inference():
    """Configure Lambda Labs Inference API for AI model calls"""
    print("🤖 Configuring Lambda Labs Serverless Inference API...")

    # Create Lambda inference configuration
    lambda_config = {
        "provider": "lambda-inference",
        "api_key": os.getenv("LAMBDA_CLOUD_API_KEY"),
        "base_url": os.getenv("LAMBDA_INFERENCE_API_BASE", "https://api.lambda.ai/v1"),
        "models": {
            "default": "llama3.3-70b-instruct-fp8",  # $0.12/M input tokens
            "fast": "llama3.2-3b-instruct",  # $0.015/M input tokens
            "complex": "llama-3.1-405b-instruct",  # $0.80/M tokens
            "code": "qwen2.5-coder-32b-instruct",  # $0.07/M tokens
        },
        "openai_compatibility": True,
    }

    # Save configuration
    with open("config/lambda_inference.json", "w") as f:
        json.dump(lambda_config, f, indent=2)

    print("✅ Lambda Inference API configured")
    print("   Models available:")
    for purpose, model in lambda_config["models"].items():
        print(f"   - {purpose}: {model}")

    return lambda_config


def create_ai_service_wrapper():
    """Create a service that routes AI calls to Lambda Inference"""
    service_code = '''"""
Sophia AI Service with Lambda Labs Inference API
Routes all LLM calls through Lambda's serverless API for massive cost savings
"""

import os
import json
from openai import OpenAI
from typing import Optional, Dict, Any

class LambdaInferenceService:
    """Service for Lambda Labs Serverless Inference"""
    
    def __init__(self):
        # Load Lambda configuration
        with open("config/lambda_inference.json", "r") as f:
            self.config = json.load(f)
        
        # Initialize OpenAI-compatible client
        self.client = OpenAI(
            api_key=self.config["api_key"],
            base_url=self.config["base_url"]
        )
        
        self.models = self.config["models"]
    
    async def chat_completion(
        self,
        messages: list,
        model_type: str = "default",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Make a chat completion request to Lambda Inference API
        
        Model types:
        - default: Balanced performance (llama3.3-70b)
        - fast: Quick responses (llama3.2-3b) - $0.015/M tokens!
        - complex: Advanced reasoning (llama-405b)
        - code: Code generation (qwen2.5-coder)
        """
        model = self.models.get(model_type, self.models["default"])
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Lambda Inference error: {e}")
            # Fallback to local model or raise
            raise
    
    async def embedding(self, text: str, model: str = "nomic-embed-text-v1.5") -> list:
        """Generate embeddings using Lambda's embedding models"""
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            raise
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model_type: str = "default") -> float:
        """Estimate cost for a request"""
        pricing = {
            "fast": {"input": 0.000015, "output": 0.000025},      # Per token
            "default": {"input": 0.00012, "output": 0.0003},
            "complex": {"input": 0.0008, "output": 0.0008},
            "code": {"input": 0.00007, "output": 0.00016}
        }
        
        rates = pricing.get(model_type, pricing["default"])
        cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])
        return cost

# Singleton instance
_lambda_service = None

def get_lambda_inference_service():
    """Get Lambda Inference service instance"""
    global _lambda_service
    if _lambda_service is None:
        _lambda_service = LambdaInferenceService()
    return _lambda_service
'''

    os.makedirs("backend/services", exist_ok=True)
    with open("backend/services/lambda_inference_service.py", "w") as f:
        f.write(service_code)

    print("✅ Created Lambda Inference service wrapper")


def update_backend_for_lambda():
    """Update backend to use Lambda Inference instead of OpenAI directly"""
    print("\n🔧 Updating backend to use Lambda Inference...")

    # Create updated orchestrator that uses Lambda
    orchestrator_update = '''# Add this to your orchestrator imports
from backend.services.lambda_inference_service import get_lambda_inference_service

# In your orchestrator class, replace OpenAI calls with:
async def process_with_lambda(self, query: str, context: dict):
    """Process query using Lambda Labs Inference"""
    lambda_service = get_lambda_inference_service()
    
    # Route to appropriate model based on query complexity
    if len(query) < 100 and "simple" in query.lower():
        model_type = "fast"  # Use cheap 3B model
    elif "code" in query.lower() or "function" in query.lower():
        model_type = "code"
    elif "complex" in query.lower() or len(query) > 500:
        model_type = "complex"
    else:
        model_type = "default"
    
    messages = [
        {"role": "system", "content": "You are Sophia AI, an executive assistant."},
        {"role": "user", "content": query}
    ]
    
    response = await lambda_service.chat_completion(
        messages=messages,
        model_type=model_type
    )
    
    # Estimate and log cost
    est_cost = lambda_service.estimate_cost(
        input_tokens=len(query.split()) * 1.3,  # Rough estimate
        output_tokens=len(response.split()) * 1.3,
        model_type=model_type
    )
    print(f"💰 Lambda Inference cost: ${est_cost:.6f}")
    
    return response
'''

    with open("docs/LAMBDA_INFERENCE_INTEGRATION.md", "w") as f:
        f.write(orchestrator_update)

    print("✅ Backend integration guide created")


def deploy_backend_with_lambda():
    """Deploy backend configured for Lambda Inference"""
    print("\n🚀 Deploying Backend with Lambda Inference...")

    # Create deployment configuration
    deploy_config = {
        "name": "sophia-ai-lambda-inference",
        "env": {
            "LAMBDA_CLOUD_API_KEY": os.getenv("LAMBDA_CLOUD_API_KEY"),
            "LAMBDA_INFERENCE_API_BASE": "https://api.lambda.ai/v1",
            "USE_LAMBDA_INFERENCE": "true",
            "ENVIRONMENT": "prod",
        },
        "features": {
            "smart_routing": True,  # Route to different models based on query
            "cost_tracking": True,  # Track inference costs
            "fallback_enabled": False,  # No fallback to expensive OpenAI
        },
    }

    # For Vercel deployment
    print("\n📦 Preparing for Vercel deployment...")

    # Update vercel.json for Lambda inference
    vercel_config = {
        "version": 2,
        "env": deploy_config["env"],
        "functions": {
            "api/*.py": {"maxDuration": 30, "memory": 1024, "runtime": "python3.12"}
        },
    }

    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)

    print("✅ Vercel configuration updated")

    return deploy_config


def show_cost_comparison():
    """Show cost comparison between providers"""
    print("\n💰 COST COMPARISON (per 1M tokens):")
    print("=" * 50)
    print("Lambda Labs Serverless Inference:")
    print("  - Llama 3.2 3B:     $0.015 input / $0.025 output")
    print("  - Llama 3.3 70B:    $0.12 input / $0.30 output")
    print("  - DeepSeek V3:      $0.34 input / $0.88 output")
    print("\nOpenAI:")
    print("  - GPT-3.5:          $0.50 input / $1.50 output")
    print("  - GPT-4o-mini:      $0.15 input / $0.60 output")
    print("  - GPT-4o:           $2.50 input / $10.00 output")
    print("\n🎯 Savings: Up to 97% cheaper than OpenAI!")


def main():
    print("🚀 SOPHIA AI + LAMBDA LABS SERVERLESS INFERENCE")
    print("=" * 50)
    print("Ultra-cheap AI inference for your backend!")
    print()

    # Configure Lambda Inference
    lambda_config = configure_lambda_inference()

    # Create service wrapper
    create_ai_service_wrapper()

    # Update backend
    update_backend_for_lambda()

    # Deploy configuration
    deploy_config = deploy_backend_with_lambda()

    # Show cost comparison
    show_cost_comparison()

    print("\n✅ DEPLOYMENT READY!")
    print("=" * 50)
    print("\n🎯 Next Steps:")
    print("1. Deploy to Vercel:")
    print("   vercel --prod")
    print("\n2. Or test locally with Lambda inference:")
    print("   python backend/app/unified_chat_backend.py")
    print("\n3. Monitor costs in Lambda dashboard:")
    print("   https://lambda.ai/dashboard")
    print("\n💡 Your AI costs just dropped by 90%+!")
    print("   Using Lambda's $0.015/M token models")
    print("   Instead of OpenAI's $2.50/M tokens")


if __name__ == "__main__":
    main()

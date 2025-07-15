#!/usr/bin/env python3
"""Qdrant vector database"""
    print("🚀 Creating Unified Deployment Orchestrator...")
    print("=" * 60)
    
    # Create main orchestrator
    orchestrator_path = create_unified_deployment_orchestrator()
    
    # Qdrant vector database
    test_path = create_weaviate_cloud_test()
    
    print("=" * 60)
    print("✅ Deployment scripts created successfully!")
    print()
    print("📋 Next steps:")
    print(f"1. Test Weaviate Cloud: python {test_path}")
    print(f"2. Run deployment: python {orchestrator_path} --environment production")
    print()
    print("🔧 Prerequisites:")
    print("- Set environment variables: LAMBDA_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY")
    print("- Ensure SSH key exists: ~/.ssh/sophia_correct_key")
    print("- Install dependencies: pip install weaviate-client requests")

if __name__ == "__main__":
    main() 
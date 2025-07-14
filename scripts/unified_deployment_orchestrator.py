#!/usr/bin/env python3
"""Qdrant vector database"""
    parser = argparse.ArgumentParser(description="Unified Sophia AI Deployment")
    parser.add_argument("--environment", default="production", 
                       choices=["development", "staging", "production"],
                       help="Deployment environment")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate prerequisites")
    
    args = parser.parse_args()
    
    orchestrator = UnifiedDeploymentOrchestrator(args.environment)
    
    if args.validate_only:
        success = await orchestrator.validate_prerequisites()
        sys.exit(0 if success else 1)
    else:
        success = await orchestrator.deploy_full_stack()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

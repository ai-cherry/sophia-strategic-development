#!/usr/bin/env python3
"""Qdrant vector database"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Strategic Integration V4")
    parser.add_argument("--quick", action="store_true", 
                       help="Quick deployment (skip some phases)")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate existing deployment")
    
    args = parser.parse_args()
    
    deployer = StrategicIntegrationV4Deployer()
    
    try:
        if args.validate_only:
            await deployer._validate_deployment()
        else:
            await deployer.deploy_strategic_integration_v4()
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
"""Qdrant vector database"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Qdrant Integration")
    parser.add_argument("--mode", choices=["full", "quick"], default="full",
                       help="Deployment mode: full or quick setup")
    parser.add_argument("--skip-migration", action="store_true",
                       help="Skip data migration from Weaviate")
    
    args = parser.parse_args()
    
    orchestrator = QdrantDeploymentOrchestrator()
    
    try:
        if args.mode == "quick":
            await orchestrator.quick_setup()
        else:
            await orchestrator.deploy_complete_integration()
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
"""Qdrant vector database"""
    print("=" * 60)
    print("🚀 PHASE 1: MAX-SCALE BI INGESTION & VALIDATION")
    print("=" * 60)
    
    validator = MaxIngestValidator()
    
    try:
        # Initialize
        await validator.initialize()
        
        # Run max ingestion
        ingestion_results = await validator.run_max_ingestion()
        
        # Validate embeddings
        validation_results = await validator.validate_embeddings()
        
        # Test fused RAG
        rag_result = await validator.test_fused_rag()
        
        # Generate report
        report = validator.generate_report(ingestion_results, validation_results, rag_result)
        
        print(report)
        
        # Save report
        with open('PHASE_1_VALIDATION_REPORT.md', 'w') as f:
            f.write(report)
        
        print("\n✅ Report saved to PHASE_1_VALIDATION_REPORT.md")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 
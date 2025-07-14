"""Qdrant vector database"""
    adapter = UnifiedETLAdapter()
    await adapter.initialize()
    return adapter

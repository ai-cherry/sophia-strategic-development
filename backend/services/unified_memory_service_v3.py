"""Qdrant vector database"""
    global _memory_service_v3_instance
    if _memory_service_v3_instance is None:
        _memory_service_v3_instance = UnifiedMemoryService()
        await _memory_service_v3_instance.initialize()
    return _memory_service_v3_instance 
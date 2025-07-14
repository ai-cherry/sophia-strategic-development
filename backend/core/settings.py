"""Qdrant vector database"""
    return Settings()


# Create a singleton instance
settings = get_settings()


# Export commonly used settings
__all__ = ["Settings", "get_settings", "settings"]

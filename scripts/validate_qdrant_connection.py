#!/usr/bin/env python3
"""
Qdrant Connectivity Validation Script
Tests Qdrant connection and resolves common issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from qdrant_client import QdrantClient
    from backend.core.auto_esc_config import get_config_value
    
    # Test Qdrant connection
    qdrant_url = get_config_value("QDRANT_URL")
    qdrant_api_key = get_config_value("QDRANT_API_KEY")
    
    if qdrant_url and qdrant_api_key:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        collections = client.get_collections()
        print(f"✅ Qdrant connection successful: {len(collections.collections)} collections")
    else:
        print("❌ Qdrant credentials not configured")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Connection error: {e}")

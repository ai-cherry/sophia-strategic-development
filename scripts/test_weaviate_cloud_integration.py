#!/usr/bin/env python3
"""
Test Weaviate Cloud Integration
Validates connection and basic operations
"""

import asyncio
import os
import sys
from datetime import datetime

try:
    import weaviate
    import requests
except ImportError:
    print("❌ Missing dependencies. Install with: pip install weaviate-client requests")
    sys.exit(1)

class WeaviateCloudTester:
    """Test Weaviate Cloud integration"""
    
    def __init__(self):
        self.cluster_url = "https://w6bigpoxsrwvq7wlgmmdva.c0.us-west3.gcp.weaviate.cloud"
        self.api_key = "VMKjGMQUnXQIDiFOciZZOhr7amBfCHMh7hNf"
    
    def test_connection(self) -> bool:
        """Test basic connection"""
        print("🔷 Testing Weaviate Cloud connection...")
        
        try:
            response = requests.get(
                f"{self.cluster_url}/v1/meta",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                meta = response.json()
                print(f"   ✅ Connected to Weaviate Cloud")
                print(f"   📍 Hostname: {meta.get('hostname', 'Unknown')}")
                print(f"   🔧 Modules: {len(meta.get('modules', {}))}")
                return True
            else:
                print(f"   ❌ Connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return False
    
    def test_client_v4(self) -> bool:
        """Test Weaviate v4 client"""
        print("🔷 Testing Weaviate v4 client...")
        
                 try:
             client = weaviate.connect_to_weaviate_cloud(
                 cluster_url=self.cluster_url,
                 auth_credentials=weaviate.auth.AuthApiKey(self.api_key)
             )
            
            # Test basic operations
            if client.is_ready():
                print("   ✅ Client v4 connection successful")
                
                # Get cluster info
                meta = client.get_meta()
                print(f"   📊 Cluster ready: {client.is_ready()}")
                
                client.close()
                return True
            else:
                print("   ❌ Client not ready")
                return False
                
        except Exception as e:
            print(f"   ❌ Client v4 error: {e}")
            return False
    
    def test_schema_operations(self) -> bool:
        """Test schema operations"""
        print("🔷 Testing schema operations...")
        
                 try:
             client = weaviate.connect_to_weaviate_cloud(
                 cluster_url=self.cluster_url,
                 auth_credentials=weaviate.auth.AuthApiKey(self.api_key)
             )
             
             # List existing collections
             collections = client.collections.list_all()
             print(f"   📚 Existing collections: {len(collections)}")
             
             # Test collection creation (if needed)
             test_collection_name = "SophiaTest"
             
             if test_collection_name not in [c.name for c in collections]:
                 print(f"   🔧 Creating test collection: {test_collection_name}")
                 
                 from weaviate.classes.config import Configure, Property, DataType
                 
                 collection = client.collections.create(
                     name=test_collection_name,
                     properties=[
                         Property(name="content", data_type=DataType.TEXT),
                         Property(name="timestamp", data_type=DataType.DATE)
                     ]
                 )
                 print(f"   ✅ Test collection created")
             else:
                 print(f"   ✅ Test collection already exists")
             
             client.close()
             return True
            
        except Exception as e:
            print(f"   ❌ Schema operations error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🚀 Starting Weaviate Cloud integration tests...")
        print("=" * 50)
        
        tests = [
            ("Connection Test", self.test_connection),
            ("Client v4 Test", self.test_client_v4),
            ("Schema Operations", self.test_schema_operations)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            except Exception as e:
                results.append(False)
                print(f"❌ FAIL {test_name}: {e}")
            
            print()
        
        success_rate = sum(results) / len(results)
        print("=" * 50)
        print(f"📊 Test Results: {sum(results)}/{len(results)} passed ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            print("🎉 Weaviate Cloud integration is ready!")
            return True
        else:
            print("⚠️  Weaviate Cloud integration needs attention")
            return False

def main():
    """Main test function"""
    tester = WeaviateCloudTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

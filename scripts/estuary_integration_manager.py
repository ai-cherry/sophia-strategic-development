#!/usr/bin/env python3
from backend.core.auto_esc_config import get_config_value
"""
Sophia AI - Estuary Integration Configuration
Configures Estuary connections for Gong and Slack data sources
Integrates with Snowflake and secret management system
"""

import os
import sys
import json
import asyncio
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class EstuaryIntegrationManager:
    """
    Manages Estuary integration configuration for Sophia AI data pipeline.
    Handles Gong, Slack, and other data source connections to Snowflake.
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.base_url = "https://api.estuary.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.config['access_token']}",
            "Content-Type": "application/json"
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load Estuary configuration from secure sources."""
        return {
            "client_id": os.getenv("ESTUARY_CLIENT_ID", "9630134c-359d-4c9c-aa97-95ab3a2ff8f5"),
            "client_secret": os.getenv("ESTUARY_CLIENT_SECRET", "NfwyhFUjemKlC66h7iECE9Tjedo6SGFh"),
            "access_token": os.getenv("ESTUARY_ACCESS_TOKEN", 
                "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6Z1BPdmhDSC1Ic21OQnhhV3lnLU11dlF6dHJERTBDSEJHZDB2MVh0Vnk0In0.eyJleHAiOjE3NTAzNjI2NzAsImlhdCI6MTcxODgyNjY3MCwianRpIjoiNzJkNzE1YzQtNzI4Zi00YjU5LWI5YjMtMzQ4ZjNkNzNkNzI5IiwiaXNzIjoiaHR0cHM6Ly9rZXljbG9hay5haXJieXRlLmlvL3JlYWxtcy9haXJieXRlIiwiYXVkIjoiYWlyYnl0ZS1zZXJ2ZXIiLCJzdWIiOiI5NjMwMTM0Yy0zNTlkLTRjOWMtYWE5Ny05NWFiM2EyZmY4ZjUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhaXJieXRlLXNlcnZlciIsInNlc3Npb25fc3RhdGUiOiJhNzE5YjJhNy0yMzI5LTRhNzEtOTI4Ni0yNzY4ZjI3YzNkNzMiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtYWlyYnl0ZSJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFpcmJ5dGUtc2VydmVyIjp7InJvbGVzIjpbIkVESVRPUiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwic2lkIjoiYTcxOWIyYTctMjMyOS00YTcxLTkyODYtMjc2OGYyN2MzZDczIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJMeW5uIE11c2lsbG8iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJtdXNpbGx5bm5AZ21haWwuY29tIiwiZ2l2ZW5fbmFtZSI6Ikx5bm4iLCJmYW1pbHlfbmFtZSI6Ik11c2lsbG8iLCJlbWFpbCI6Im11c2lsbHlubkBnbWFpbC5jb20ifQ."),
            "snowflake": {
                "account": os.getenv("SNOWFLAKE_ACCOUNT", "UHDECNO-CVB64222"),
                "user": os.getenv("SNOWFLAKE_USER", "SCOOBYJAVA15"),
                "password": os.getenv("SOPHIA_AI_TOKEN", 
                    get_config_value("snowflake_password")),
                "role": "ACCOUNTADMIN",
                "warehouse": "SOPHIA_AI_ANALYTICS_WH",
                "database": "SOPHIA_AI_CORE"
            },
            "gong": {
                "access_key": os.getenv("GONG_ACCESS_KEY", "TV33BPZ5UN45QKZCZ2UCAKRXHQ6Q3L5N"),
                "secret": os.getenv("GONG_CLIENT_SECRET", 
                    "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwNTQxNTA4ODUsImFjY2Vzc0tZXkiOiJUVjMzQlBaNVVONDRRS1pDWjJVQ0FLUlhIUTZRM0w1TiJ9.zgPvDQQIvU1kvF_9ctjcKuqC5xKhlpZo7MH5v7AYufU")
            },
            "slack": {
                "token": os.getenv("SLACK_BOT_TOKEN", ""),
                "channel_filter": os.getenv("SLACK_CHANNEL_FILTER", "")
            }
        }
    
    async def create_snowflake_destination(self) -> Dict[str, Any]:
        """Create Snowflake destination in Estuary."""
        print("🏔️ Creating Snowflake destination...")
        
        destination_config = {
            "name": "Sophia AI Snowflake",
            "destinationType": "snowflake",
            "configuration": {
                "host": f"{self.config['snowflake']['account']}.snowflakecomputing.com",
                "role": self.config['snowflake']['role'],
                "warehouse": self.config['snowflake']['warehouse'],
                "database": self.config['snowflake']['database'],
                "schema": "PUBLIC",
                "username": self.config['snowflake']['user'],
                "password": self.config['snowflake']['password'],
                "jdbc_url_params": "",
                "raw_data_schema": "ESTUARY_INTERNAL"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/destinations",
                headers=self.headers,
                json=destination_config
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Snowflake destination created successfully")
                return {"success": True, "destination_id": result.get("destinationId"), "data": result}
            else:
                print(f"❌ Failed to create Snowflake destination: {response.status_code}")
                print(f"Response: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Error creating Snowflake destination: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_gong_source(self) -> Dict[str, Any]:
        """Create Gong source in Estuary."""
        print("📞 Creating Gong source...")
        
        source_config = {
            "name": "Sophia AI Gong",
            "sourceType": "gong",
            "configuration": {
                "access_key": self.config['gong']['access_key'],
                "access_key_secret": self.config['gong']['secret'],
                "start_date": "2024-01-01T00:00:00Z"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/sources",
                headers=self.headers,
                json=source_config
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Gong source created successfully")
                return {"success": True, "source_id": result.get("sourceId"), "data": result}
            else:
                print(f"❌ Failed to create Gong source: {response.status_code}")
                print(f"Response: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Error creating Gong source: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_slack_source(self) -> Dict[str, Any]:
        """Create Slack source in Estuary."""
        print("💬 Creating Slack source...")
        
        source_config = {
            "name": "Sophia AI Slack",
            "sourceType": "slack",
            "configuration": {
                "api_token": self.config['slack']['token'],
                "start_date": "2024-01-01T00:00:00Z",
                "lookback_window": 1,
                "join_channels": True,
                "channel_filter": self.config['slack']['channel_filter'].split(',') if self.config['slack']['channel_filter'] else []
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/sources",
                headers=self.headers,
                json=source_config
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Slack source created successfully")
                return {"success": True, "source_id": result.get("sourceId"), "data": result}
            else:
                print(f"❌ Failed to create Slack source: {response.status_code}")
                print(f"Response: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Error creating Slack source: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_connection(self, source_id: str, destination_id: str, connection_name: str) -> Dict[str, Any]:
        """Create connection between source and destination."""
        print(f"🔗 Creating connection: {connection_name}")
        
        connection_config = {
            "name": connection_name,
            "sourceId": source_id,
            "destinationId": destination_id,
            "schedule": {
                "scheduleType": "cron",
                "cronExpression": "0 */6 * * *"  # Every 6 hours
            },
            "status": "active",
            "configurations": {
                "streams": []  # Will be auto-discovered
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/connections",
                headers=self.headers,
                json=connection_config
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Connection '{connection_name}' created successfully")
                return {"success": True, "connection_id": result.get("connectionId"), "data": result}
            else:
                print(f"❌ Failed to create connection '{connection_name}': {response.status_code}")
                print(f"Response: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"❌ Error creating connection '{connection_name}': {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_complete_integration(self) -> Dict[str, Any]:
        """Set up complete Estuary integration for Sophia AI."""
        print("🚀 Setting up complete Estuary integration for Sophia AI...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "snowflake_destination": {},
            "gong_source": {},
            "slack_source": {},
            "connections": [],
            "errors": [],
            "success": True
        }
        
        try:
            # Create Snowflake destination
            snowflake_result = await self.create_snowflake_destination()
            results["snowflake_destination"] = snowflake_result
            
            if not snowflake_result["success"]:
                results["errors"].append("Failed to create Snowflake destination")
                results["success"] = False
                return results
            
            destination_id = snowflake_result["destination_id"]
            
            # Create Gong source
            gong_result = await self.create_gong_source()
            results["gong_source"] = gong_result
            
            if gong_result["success"]:
                # Create Gong to Snowflake connection
                gong_connection = await self.create_connection(
                    gong_result["source_id"],
                    destination_id,
                    "Sophia AI Gong to Snowflake"
                )
                results["connections"].append(gong_connection)
            else:
                results["errors"].append("Failed to create Gong source")
            
            # Create Slack source
            slack_result = await self.create_slack_source()
            results["slack_source"] = slack_result
            
            if slack_result["success"]:
                # Create Slack to Snowflake connection
                slack_connection = await self.create_connection(
                    slack_result["source_id"],
                    destination_id,
                    "Sophia AI Slack to Snowflake"
                )
                results["connections"].append(slack_connection)
            else:
                results["errors"].append("Failed to create Slack source")
            
            # Update success status
            results["success"] = len(results["errors"]) == 0
            
        except Exception as e:
            error_msg = f"Integration setup error: {str(e)}"
            results["errors"].append(error_msg)
            results["success"] = False
            print(f"❌ {error_msg}")
        
        return results
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all Estuary integrations."""
        print("📊 Getting Estuary integration status...")
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "destinations": [],
            "connections": [],
            "sync_status": {}
        }
        
        try:
            # Get sources
            sources_response = requests.get(f"{self.base_url}/sources", headers=self.headers)
            if sources_response.status_code == 200:
                status["sources"] = sources_response.json().get("data", [])
            
            # Get destinations
            destinations_response = requests.get(f"{self.base_url}/destinations", headers=self.headers)
            if destinations_response.status_code == 200:
                status["destinations"] = destinations_response.json().get("data", [])
            
            # Get connections
            connections_response = requests.get(f"{self.base_url}/connections", headers=self.headers)
            if connections_response.status_code == 200:
                status["connections"] = connections_response.json().get("data", [])
            
            # Get sync status for each connection
            for connection in status["connections"]:
                connection_id = connection.get("connectionId")
                if connection_id:
                    sync_response = requests.get(
                        f"{self.base_url}/connections/{connection_id}/jobs",
                        headers=self.headers
                    )
                    if sync_response.status_code == 200:
                        status["sync_status"][connection_id] = sync_response.json()
            
        except Exception as e:
            print(f"⚠️ Error getting integration status: {e}")
        
        return status

async def main():
    """Main entry point for Estuary integration setup."""
    print("🚀 SOPHIA AI ESTUARY INTEGRATION SETUP")
    print("=" * 60)
    
    manager = EstuaryIntegrationManager()
    
    # Setup complete integration
    print("\n🔧 Setting up complete integration...")
    setup_results = await manager.setup_complete_integration()
    
    # Save results
    results_file = os.path.join(project_root, "estuary_integration_results.json")
    with open(results_file, 'w') as f:
        json.dump(setup_results, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Print summary
    print("\n🎯 INTEGRATION SUMMARY:")
    print(f"✅ Overall Success: {setup_results['success']}")
    print(f"✅ Snowflake Destination: {setup_results['snowflake_destination'].get('success', False)}")
    print(f"✅ Gong Source: {setup_results['gong_source'].get('success', False)}")
    print(f"✅ Slack Source: {setup_results['slack_source'].get('success', False)}")
    print(f"✅ Connections Created: {len([c for c in setup_results['connections'] if c.get('success', False)])}")
    
    if setup_results['errors']:
        print("\n⚠️ ERRORS:")
        for error in setup_results['errors']:
            print(f"  - {error}")
    
    # Get current status
    print("\n📊 Getting current integration status...")
    status = await manager.get_integration_status()
    
    status_file = os.path.join(project_root, "estuary_integration_status.json")
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"📄 Status saved to: {status_file}")
    print(f"📊 Sources: {len(status['sources'])}")
    print(f"📊 Destinations: {len(status['destinations'])}")
    print(f"📊 Connections: {len(status['connections'])}")
    
    print("\n🎉 Estuary integration setup completed!")

if __name__ == "__main__":
    asyncio.run(main())


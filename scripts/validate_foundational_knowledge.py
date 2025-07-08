#!/usr/bin/env python3
"""Validate the foundational knowledge system is working correctly."""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import httpx
from notion_client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FoundationalKnowledgeValidator:
    """Validate the foundational knowledge system."""

    def __init__(self):
        self.notion_api_key = os.getenv(
            "NOTION_API_KEY", "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"
        )
        self.mcp_base_url = os.getenv("NOTION_MCP_URL", "http://localhost:9003")
        self.notion = Client(auth=self.notion_api_key)
        self.validation_results = []

    async def check_notion_connection(self):
        """Check Notion API connection."""
        try:
            # Try to get current user
            user = self.notion.users.me()
            self.validation_results.append(
                {
                    "test": "Notion Connection",
                    "status": "✅ PASS",
                    "details": f"Connected as: {user.get('name', 'Unknown')}",
                }
            )
            return True
        except Exception as e:
            self.validation_results.append(
                {"test": "Notion Connection", "status": "❌ FAIL", "details": str(e)}
            )
            return False

    async def check_databases_exist(self):
        """Check if all required databases exist."""
        # Load configuration if it exists
        config_file = "notion_config.json"
        if not os.path.exists(config_file):
            self.validation_results.append(
                {
                    "test": "Database Configuration",
                    "status": "❌ FAIL",
                    "details": f"Configuration file {config_file} not found",
                }
            )
            return False

        with open(config_file) as f:
            config = json.load(f)

        database_ids = config.get("database_ids", {})
        all_exist = True

        for db_name, db_id in database_ids.items():
            try:
                # Try to query the database
                self.notion.databases.retrieve(database_id=db_id)
                self.validation_results.append(
                    {
                        "test": f"Database: {db_name}",
                        "status": "✅ PASS",
                        "details": f"Database exists: {db_id}",
                    }
                )
            except Exception as e:
                self.validation_results.append(
                    {
                        "test": f"Database: {db_name}",
                        "status": "❌ FAIL",
                        "details": str(e),
                    }
                )
                all_exist = False

        return all_exist

    async def check_mcp_server(self):
        """Check if MCP server is running."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.mcp_base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    self.validation_results.append(
                        {
                            "test": "MCP Server Health",
                            "status": "✅ PASS",
                            "details": f"Server healthy: {data}",
                        }
                    )
                    return True
                else:
                    self.validation_results.append(
                        {
                            "test": "MCP Server Health",
                            "status": "❌ FAIL",
                            "details": f"Status code: {response.status_code}",
                        }
                    )
                    return False
            except Exception as e:
                self.validation_results.append(
                    {
                        "test": "MCP Server Health",
                        "status": "❌ FAIL",
                        "details": f"Cannot connect: {str(e)}",
                    }
                )
                return False

    async def test_search_functionality(self):
        """Test search functionality."""
        test_queries = [
            {"query": "Smith", "entity_type": "employees"},
            {"query": "Acme", "entity_type": "customers"},
            {"query": "product", "entity_type": None},
        ]

        async with httpx.AsyncClient() as client:
            for test in test_queries:
                try:
                    response = await client.post(
                        f"{self.mcp_base_url}/search", json=test
                    )

                    if response.status_code == 200:
                        data = response.json()
                        self.validation_results.append(
                            {
                                "test": f"Search: {test['query']}",
                                "status": "✅ PASS",
                                "details": f"Found {data.get('count', 0)} results",
                            }
                        )
                    else:
                        self.validation_results.append(
                            {
                                "test": f"Search: {test['query']}",
                                "status": "❌ FAIL",
                                "details": f"Status code: {response.status_code}",
                            }
                        )
                except Exception as e:
                    self.validation_results.append(
                        {
                            "test": f"Search: {test['query']}",
                            "status": "❌ FAIL",
                            "details": str(e),
                        }
                    )

    async def test_employee_lookup(self):
        """Test employee lookup functionality."""
        test_email = "jane.smith@payready.com"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.mcp_base_url}/employees/lookup", json={"email": test_email}
                )

                if response.status_code == 200:
                    data = response.json()
                    if "error" not in data:
                        self.validation_results.append(
                            {
                                "test": "Employee Lookup",
                                "status": "✅ PASS",
                                "details": f"Found: {data.get('name', 'Unknown')}",
                            }
                        )
                    else:
                        self.validation_results.append(
                            {
                                "test": "Employee Lookup",
                                "status": "⚠️  WARN",
                                "details": data.get("error"),
                            }
                        )
                else:
                    self.validation_results.append(
                        {
                            "test": "Employee Lookup",
                            "status": "❌ FAIL",
                            "details": f"Status code: {response.status_code}",
                        }
                    )
            except Exception as e:
                self.validation_results.append(
                    {"test": "Employee Lookup", "status": "❌ FAIL", "details": str(e)}
                )

    async def test_natural_language_queries(self):
        """Test natural language query patterns."""
        test_queries = [
            "Who is Jane Smith?",
            "Tell me about Acme Corp",
            "What products do we offer?",
            "Show me our competitors",
        ]

        # This would integrate with Sophia AI chat service
        # For now, we'll just test the search API
        async with httpx.AsyncClient() as client:
            for query in test_queries:
                # Extract search term from natural language
                if "who is" in query.lower():
                    search_term = (
                        query.lower().replace("who is", "").strip().rstrip("?")
                    )
                    entity_type = "employees"
                elif "tell me about" in query.lower():
                    search_term = query.lower().replace("tell me about", "").strip()
                    entity_type = "customers"
                elif "products" in query.lower():
                    search_term = "product"
                    entity_type = "products"
                elif "competitors" in query.lower():
                    search_term = ""
                    entity_type = "competitors"
                else:
                    search_term = query
                    entity_type = None

                try:
                    response = await client.post(
                        f"{self.mcp_base_url}/search",
                        json={"query": search_term, "entity_type": entity_type},
                    )

                    if response.status_code == 200:
                        data = response.json()
                        self.validation_results.append(
                            {
                                "test": f"NL Query: {query}",
                                "status": "✅ PASS",
                                "details": f"Would return {data.get('count', 0)} results",
                            }
                        )
                    else:
                        self.validation_results.append(
                            {
                                "test": f"NL Query: {query}",
                                "status": "❌ FAIL",
                                "details": f"Status code: {response.status_code}",
                            }
                        )
                except Exception as e:
                    self.validation_results.append(
                        {
                            "test": f"NL Query: {query}",
                            "status": "❌ FAIL",
                            "details": str(e),
                        }
                    )

    def generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("📊 FOUNDATIONAL KNOWLEDGE VALIDATION REPORT")
        print("=" * 60)
        print(f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")

        # Group results by status
        passed = [r for r in self.validation_results if "PASS" in r["status"]]
        failed = [r for r in self.validation_results if "FAIL" in r["status"]]
        warned = [r for r in self.validation_results if "WARN" in r["status"]]

        # Summary
        total = len(self.validation_results)
        print("📈 Summary:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {len(passed)} ({len(passed)/total*100:.1f}%)")
        print(f"   ❌ Failed: {len(failed)} ({len(failed)/total*100:.1f}%)")
        print(f"   ⚠️  Warnings: {len(warned)} ({len(warned)/total*100:.1f}%)")
        print()

        # Detailed results
        print("📋 Detailed Results:")
        print("-" * 60)

        for result in self.validation_results:
            print(f"{result['status']} {result['test']}")
            if result["details"]:
                print(f"   → {result['details']}")

        print("-" * 60)

        # Recommendations
        if failed:
            print("\n⚠️  RECOMMENDATIONS:")
            if any("MCP Server" in r["test"] for r in failed):
                print(
                    "   1. Start the MCP server: cd infrastructure/mcp_servers/notion_simple && python server.py"
                )
            if any("Database" in r["test"] for r in failed):
                print(
                    "   2. Run setup script: python scripts/setup_notion_simple.py <parent_page_id>"
                )
            if any("Notion Connection" in r["test"] for r in failed):
                print("   3. Check your NOTION_API_KEY environment variable")

        # Overall status
        print("\n" + "=" * 60)
        if len(failed) == 0:
            print("✅ SYSTEM STATUS: READY FOR PRODUCTION")
        elif len(failed) < 3:
            print("⚠️  SYSTEM STATUS: PARTIALLY OPERATIONAL")
        else:
            print("❌ SYSTEM STATUS: NOT READY")
        print("=" * 60 + "\n")

        # Save report
        report_file = (
            f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "total": total,
                        "passed": len(passed),
                        "failed": len(failed),
                        "warned": len(warned),
                    },
                    "results": self.validation_results,
                },
                f,
                indent=2,
            )

        print(f"📄 Report saved to: {report_file}")

    async def run_validation(self):
        """Run all validation tests."""
        print("🚀 Starting Foundational Knowledge System Validation...")

        # Test 1: Notion connection
        await self.check_notion_connection()

        # Test 2: Database existence
        await self.check_databases_exist()

        # Test 3: MCP server health
        await self.check_mcp_server()

        # Test 4: Search functionality
        await self.test_search_functionality()

        # Test 5: Employee lookup
        await self.test_employee_lookup()

        # Test 6: Natural language queries
        await self.test_natural_language_queries()

        # Generate report
        self.generate_report()


async def main():
    """Main validation function."""
    validator = FoundationalKnowledgeValidator()
    await validator.run_validation()


if __name__ == "__main__":
    asyncio.run(main())

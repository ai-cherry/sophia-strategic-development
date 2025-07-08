#!/usr/bin/env python3
"""Simplified Notion setup for foundational knowledge - based on real data patterns."""

import json
import logging
import os
from datetime import datetime

from notion_client import Client
from notion_client.errors import APIResponseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Notion API Configuration
NOTION_API_KEY = os.getenv(
    "NOTION_API_KEY", "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"
)
notion = Client(auth=NOTION_API_KEY)


class SimplifiedNotionSetup:
    """Simplified setup for foundational knowledge in Notion."""

    def __init__(self):
        self.notion = notion
        self.database_ids = {}

    def create_databases(self, parent_page_id: str) -> dict:
        """Create all foundational knowledge databases with simplified schema."""

        logger.info("🚀 Creating simplified Notion databases...")

        # Create Employees database
        employees_db = self._create_employees_database(parent_page_id)
        self.database_ids["employees"] = employees_db["id"]
        logger.info(f"✅ Created Employees database: {employees_db['id']}")

        # Create Customers database
        customers_db = self._create_customers_database(parent_page_id)
        self.database_ids["customers"] = customers_db["id"]
        logger.info(f"✅ Created Customers database: {customers_db['id']}")

        # Create Competitors database
        competitors_db = self._create_competitors_database(parent_page_id)
        self.database_ids["competitors"] = competitors_db["id"]
        logger.info(f"✅ Created Competitors database: {competitors_db['id']}")

        # Create Products database
        products_db = self._create_products_database(parent_page_id)
        self.database_ids["products"] = products_db["id"]
        logger.info(f"✅ Created Products database: {products_db['id']}")

        return self.database_ids

    def _create_employees_database(self, parent_id: str):
        """Create employees database with fields based on sample data."""
        return self.notion.databases.create(
            parent={"type": "page_id", "page_id": parent_id},
            title=[{"type": "text", "text": {"content": "👥 Employees"}}],
            properties={
                "Full Name": {"title": {}},
                "Email": {"email": {}},
                "Job Title": {"rich_text": {}},
                "Department": {
                    "select": {
                        "options": [
                            {"name": "Sales", "color": "blue"},
                            {"name": "Engineering", "color": "purple"},
                            {"name": "Marketing", "color": "green"},
                            {"name": "Operations", "color": "orange"},
                            {"name": "Customer Success", "color": "yellow"},
                            {"name": "Executive", "color": "gray"},
                        ]
                    }
                },
                "Slack ID": {"rich_text": {}},
                "Gong ID": {"rich_text": {}},
                "Manager Email": {"email": {}},
                "Start Date": {"date": {}},
                "Location": {"rich_text": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Active", "color": "green"},
                            {"name": "On Leave", "color": "yellow"},
                            {"name": "Former", "color": "red"},
                        ]
                    }
                },
            },
        )

    def _create_customers_database(self, parent_id: str):
        """Create customers database with fields based on sample data."""
        return self.notion.databases.create(
            parent={"type": "page_id", "page_id": parent_id},
            title=[{"type": "text", "text": {"content": "🏢 Customers"}}],
            properties={
                "Company Name": {"title": {}},
                "Industry": {
                    "select": {
                        "options": [
                            {"name": "Technology", "color": "blue"},
                            {"name": "Healthcare", "color": "green"},
                            {"name": "Finance", "color": "yellow"},
                            {"name": "Retail", "color": "orange"},
                            {"name": "Manufacturing", "color": "red"},
                            {"name": "Other", "color": "gray"},
                        ]
                    }
                },
                "Customer Since": {"date": {}},
                "Annual Revenue": {"number": {"format": "dollar"}},
                "Employee Count": {"rich_text": {}},
                "Website": {"url": {}},
                "Health Score": {
                    "select": {
                        "options": [
                            {"name": "Green", "color": "green"},
                            {"name": "Yellow", "color": "yellow"},
                            {"name": "Red", "color": "red"},
                        ]
                    }
                },
                "CRM ID": {"rich_text": {}},
                "HubSpot ID": {"rich_text": {}},
                "Last Activity": {"date": {}},
                "Notes": {"rich_text": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Prospect", "color": "yellow"},
                            {"name": "Active", "color": "green"},
                            {"name": "Churned", "color": "red"},
                        ]
                    }
                },
            },
        )

    def _create_competitors_database(self, parent_id: str):
        """Create competitors database with simplified fields."""
        return self.notion.databases.create(
            parent={"type": "page_id", "page_id": parent_id},
            title=[{"type": "text", "text": {"content": "🥊 Competitors"}}],
            properties={
                "Company Name": {"title": {}},
                "Competitor Type": {
                    "select": {
                        "options": [
                            {"name": "Direct", "color": "red"},
                            {"name": "Indirect", "color": "yellow"},
                            {"name": "Emerging", "color": "orange"},
                        ]
                    }
                },
                "Website": {"url": {}},
                "Key Strengths": {"rich_text": {}},
                "Key Weaknesses": {"rich_text": {}},
                "Win/Loss Notes": {"rich_text": {}},
                "Last Updated": {"date": {}},
                "Threat Level": {
                    "select": {
                        "options": [
                            {"name": "High", "color": "red"},
                            {"name": "Medium", "color": "yellow"},
                            {"name": "Low", "color": "green"},
                        ]
                    }
                },
            },
        )

    def _create_products_database(self, parent_id: str):
        """Create products database with simplified fields."""
        return self.notion.databases.create(
            parent={"type": "page_id", "page_id": parent_id},
            title=[{"type": "text", "text": {"content": "📦 Products"}}],
            properties={
                "Product Name": {"title": {}},
                "Product Code": {"rich_text": {}},
                "Category": {
                    "select": {
                        "options": [
                            {"name": "Core Platform", "color": "blue"},
                            {"name": "Integration", "color": "green"},
                            {"name": "Add-on", "color": "orange"},
                            {"name": "Service", "color": "purple"},
                        ]
                    }
                },
                "Status": {
                    "select": {
                        "options": [
                            {"name": "Active", "color": "green"},
                            {"name": "Beta", "color": "yellow"},
                            {"name": "Deprecated", "color": "red"},
                            {"name": "Planned", "color": "blue"},
                        ]
                    }
                },
                "Description": {"rich_text": {}},
                "Key Features": {"rich_text": {}},
                "Pricing": {"rich_text": {}},
                "Launch Date": {"date": {}},
                "Documentation URL": {"url": {}},
                "Last Updated": {"date": {}},
            },
        )

    def save_configuration(self, filename: str = "notion_config.json"):
        """Save the database configuration."""
        config = {
            "database_ids": self.database_ids,
            "created_at": datetime.utcnow().isoformat(),
            "notion_api_key": NOTION_API_KEY,
        }

        with open(filename, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"💾 Configuration saved to {filename}")
        return config

    def create_sample_data(self):
        """Create a few sample entries to test the databases."""

        if not self.database_ids:
            logger.error("No database IDs found. Run create_databases first.")
            return

        # Sample employee
        if "employees" in self.database_ids:
            try:
                self.notion.pages.create(
                    parent={"database_id": self.database_ids["employees"]},
                    properties={
                        "Full Name": {"title": [{"text": {"content": "Jane Smith"}}]},
                        "Email": {"email": "jane.smith@payready.com"},
                        "Job Title": {
                            "rich_text": [{"text": {"content": "VP of Sales"}}]
                        },
                        "Department": {"select": {"name": "Sales"}},
                        "Status": {"select": {"name": "Active"}},
                    },
                )
                logger.info("✅ Created sample employee")
            except Exception as e:
                logger.error(f"Error creating sample employee: {e}")

        # Sample customer
        if "customers" in self.database_ids:
            try:
                self.notion.pages.create(
                    parent={"database_id": self.database_ids["customers"]},
                    properties={
                        "Company Name": {"title": [{"text": {"content": "Acme Corp"}}]},
                        "Industry": {"select": {"name": "Technology"}},
                        "Status": {"select": {"name": "Active"}},
                        "Health Score": {"select": {"name": "Green"}},
                        "Annual Revenue": {"number": 5000000},
                    },
                )
                logger.info("✅ Created sample customer")
            except Exception as e:
                logger.error(f"Error creating sample customer: {e}")


def main():
    """Main setup function."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python setup_notion_simple.py <parent_page_id>")
        print("\nTo get the parent page ID:")
        print("1. Create a page in Notion called 'Pay Ready Foundational Knowledge'")
        print("2. Copy the page ID from the URL")
        print("3. Run: python setup_notion_simple.py YOUR_PAGE_ID")
        return

    parent_page_id = sys.argv[1]

    setup = SimplifiedNotionSetup()

    try:
        # Create databases
        database_ids = setup.create_databases(parent_page_id)

        # Save configuration
        config = setup.save_configuration()

        # Create sample data
        setup.create_sample_data()

        print("\n✅ Setup completed successfully!")
        print("\n📋 Database IDs:")
        for name, db_id in database_ids.items():
            print(f"  {name}: {db_id}")

        print("\n🚀 Next steps:")
        print("1. Review the databases in Notion")
        print("2. Run: python scripts/analyze_sample_data.py")
        print(
            "3. Import your data using: streamlit run scripts/foundational_knowledge_staging.py"
        )

    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

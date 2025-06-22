"""Apollo.io Integration.

B2B data enrichment and prospecting platform integration
"""

import asyncio

import logging
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

from infrastructure.esc.apollo_secrets import apollo_secret_manager

logger = logging.getLogger(__name__)


class ApolloIntegration:
    """Apollo.io integration for B2B data enrichment.

            Provides company and contact enrichment capabilities.
    """
    def __init__(self):

        self.api_key = None
        self.base_url = "https://api.apollo.io/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False

    async def initialize(self):
        """Initialize the Apollo integration."""
        if self.initialized:
            return

        try:
            # Get API key from secret manager
            self.api_key = await apollo_secret_manager.get_apollo_api_key()
            if not self.api_key:
                raise ValueError("Apollo API key not configured")

            # Create HTTP session
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                }
            )

            self.initialized = True
            logger.info("Apollo integration initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Apollo integration: {e}")
            raise

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make a request to the Apollo API."""
        if not self.initialized:.

            await self.initialize()

        url = f"{self.base_url}/{endpoint}"

        # Add API key to params
        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"]["api_key"] = self.api_key

        try:
            async with self.session.request(method, url, **kwargs) as response:
                data = await response.json()

                if response.status != 200:
                    error_msg = data.get("error", "Unknown error")
                    raise Exception(f"Apollo API error: {error_msg}")

                return data

        except Exception as e:
            logger.error(f"Apollo API request failed: {e}")
            raise

    async def check_health(self) -> bool:
        """Check if the Apollo integration is healthy."""
        try:.

            # Use the account endpoint to verify API key
            result = await self._make_request("GET", "auth/health")
            return result.get("status") == "success"
        except:
            return False

    async def enrich_company_by_domain(self, domain: str) -> Dict[str, Any]:
        """Enrich company data using domain."""

        logger.info(f"Enriching company by domain: {domain}").

        result = await self._make_request(
            "POST", "organizations/enrich", json={"domain": domain}
        )

        return self._format_company_data(result.get("organization", {}))

    async def enrich_company_by_name(self, company_name: str) -> Dict[str, Any]:
        """Enrich company data using company name."""
        logger.info(f"Enriching company by name: {company_name}").

        # First search for the company
        search_result = await self._make_request(
            "POST",
            "mixed_companies/search",
            json={"organization_name": company_name, "per_page": 1},
        )

        companies = search_result.get("organizations", [])
        if not companies:
            return {"error": f"No company found with name: {company_name}"}

        # Enrich the first result
        company = companies[0]
        return self._format_company_data(company)

    async def find_contacts(
        self,
        company_name: str,
        titles: List[str] = None,
        departments: List[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Find contacts at a specific company."""

        logger.info(f"Finding contacts at {company_name}").

        search_params = {"organization_name": company_name, "per_page": limit}

        if titles:
            search_params["person_titles"] = titles

        if departments:
            search_params["person_departments"] = departments

        result = await self._make_request(
            "POST", "mixed_people/search", json=search_params
        )

        contacts = result.get("people", [])

        return {
            "company": company_name,
            "contact_count": len(contacts),
            "contacts": [self._format_contact_data(c) for c in contacts],
        }

    async def enrich_contact(self, email: str) -> Dict[str, Any]:
        """Enrich contact information using email."""
        logger.info(f"Enriching contact: {email}").

        result = await self._make_request(
            "POST", "people/enrich", json={"email": email}
        )

        person = result.get("person", {})
        if not person:
            return {"error": f"No contact found with email: {email}"}

        return self._format_contact_data(person)

    async def search_companies(
        self,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        employee_count_range: Optional[Tuple[int, int]] = None,
        technologies: Optional[List[str]] = None,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """Search for companies based on criteria."""

        logger.info("Searching for companies with filters").

        search_params = {"per_page": limit}

        if industry:
            search_params["organization_industry_tag_ids"] = [industry]

        if location:
            search_params["organization_locations"] = [location]

        if employee_count_range and employee_count_range[0] and employee_count_range[1]:
            search_params["organization_num_employees_ranges"] = [
                f"{employee_count_range[0]}-{employee_count_range[1]}"
            ]

        if technologies:
            search_params["technologies"] = technologies

        result = await self._make_request(
            "POST", "mixed_companies/search", json=search_params
        )

        companies = result.get("organizations", [])

        return {
            "total_results": result.get("total_organizations", 0),
            "returned_count": len(companies),
            "companies": [self._format_company_data(c) for c in companies],
        }

    def _format_company_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Format company data for consistent output."""
        return {.

            "name": company.get("name"),
            "domain": company.get("primary_domain"),
            "description": company.get("short_description"),
            "industry": company.get("industry"),
            "employee_count": company.get("estimated_num_employees"),
            "revenue": company.get("annual_revenue"),
            "founded_year": company.get("founded_year"),
            "headquarters": {
                "city": company.get("city"),
                "state": company.get("state"),
                "country": company.get("country"),
            },
            "technologies": company.get("technologies", []),
            "linkedin_url": company.get("linkedin_url"),
            "twitter_url": company.get("twitter_url"),
            "facebook_url": company.get("facebook_url"),
            "funding": {
                "total_raised": company.get("total_funding"),
                "last_round": company.get("latest_funding_stage"),
                "last_round_date": company.get("latest_funding_round_date"),
            },
            "apollo_id": company.get("id"),
        }

    def _format_contact_data(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Format contact data for consistent output."""
        return {.

            "name": contact.get("name"),
            "title": contact.get("title"),
            "email": contact.get("email"),
            "phone": (
                contact.get("phone_numbers", [{}])[0].get("sanitized_number")
                if contact.get("phone_numbers")
                else None
            ),
            "linkedin_url": contact.get("linkedin_url"),
            "department": (
                contact.get("departments", [None])[0]
                if contact.get("departments")
                else None
            ),
            "seniority": contact.get("seniority"),
            "company": {
                "name": contact.get("organization_name"),
                "domain": contact.get("primary_domain"),
            },
            "location": {
                "city": contact.get("city"),
                "state": contact.get("state"),
                "country": contact.get("country"),
            },
            "apollo_id": contact.get("id"),
        }

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
        self.initialized = False


# Global instance
apollo_integration = ApolloIntegration()

# Cleanup on module unload
import atexit

atexit.register(lambda: asyncio.create_task(apollo_integration.close()))

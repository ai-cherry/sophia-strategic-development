"""
Mock integrations for Phase 1 testing
These are placeholder implementations for max ingestion validation
"""

class GongIntegration:
    """Mock Gong integration"""
    async def fetch_calls(self, limit: int = 100) -> list:
        return []

class HubSpotIntegration:
    """Mock HubSpot integration"""
    async def fetch_contacts(self, limit: int = 100) -> list:
        return []

class SlackIntegration:
    """Mock Slack integration"""
    async def fetch_messages(self, limit: int = 100) -> list:
        return []

class NotionIntegration:
    """Mock Notion integration"""
    async def fetch_pages(self, limit: int = 100) -> list:
        return []

class AsanaIntegration:
    """Mock Asana integration"""
    async def fetch_tasks(self, limit: int = 100) -> list:
        return []

class GitHubIntegration:
    """Mock GitHub integration"""
    async def fetch_issues(self, limit: int = 100) -> list:
        return []

class LinearIntegration:
    """Mock Linear integration"""
    async def fetch_issues(self, limit: int = 100) -> list:
        return [] 
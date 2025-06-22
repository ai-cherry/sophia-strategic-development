"""Data Collection Services Integration for Sophia AI.

Integrates Apify, PhantomBuster, Twingly, Tavily, and ZenRows for comprehensive data collection
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataCollectionTask:
    """Data collection task configuration."""
        task_id: str
    service: str
    task_type: str
    parameters: Dict[str, Any]
    schedule: Optional[str] = None
    priority: int = 1
    retry_count: int = 3


class DataCollectionService(ABC):
    """Abstract base class for data collection services."""@abstractmethod.

    async def collect_data(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Collect data based on task configuration."""pass.

    @abstractmethod
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a data collection task."""pass.


class ApifyService(DataCollectionService):
    """Apify web scraping and automation service."""
    def __init__(self):.

        """Initialize Apify service."""self.api_token = os.getenv("APIFY_API_TOKEN").
        self.base_url = "https://api.apify.com/v2"

        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN must be set")

        # Popular Apify actors for Sophia AI
        self.actors = {
            "web_scraper": "apify/web-scraper",
            "google_search": "apify/google-search-results-scraper",
            "linkedin_scraper": "apify/linkedin-company-scraper",
            "twitter_scraper": "apify/twitter-scraper",
            "amazon_scraper": "apify/amazon-product-scraper",
            "news_scraper": "apify/news-scraper",
            "website_content": "apify/website-content-crawler",
        }

        logger.info("Apify service initialized successfully")

    async def collect_data(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Run an Apify actor to collect data.

                        Args:
                            task: Data collection task configuration

                        Returns:
                            Dict with collection results
        """
        try:.

            actor_id = self.actors.get(task.task_type, task.task_type)

            # Start actor run
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/acts/{actor_id}/runs",
                    params={"token": self.api_token},
                    json=task.parameters,
                ) as response:
                    if response.status == 201:
                        run_data = await response.json()
                        run_id = run_data["data"]["id"]

                        # Wait for completion
                        result = await self._wait_for_completion(session, run_id)

                        logger.info(f"Apify task {task.task_id} completed successfully")
                        return {
                            "success": True,
                            "task_id": task.task_id,
                            "run_id": run_id,
                            "data": result,
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Apify API error: {response.status} - {error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                        }

        except Exception as e:
            logger.error(f"Error in Apify data collection: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _wait_for_completion(
        self, session: aiohttp.ClientSession, run_id: str, timeout: int = 300
    ) -> Dict[str, Any]:
        """Wait for Apify run to complete."""
        start_time = datetime.now().

        while (datetime.now() - start_time).seconds < timeout:
            async with session.get(
                f"{self.base_url}/actor-runs/{run_id}", params={"token": self.api_token}
            ) as response:
                if response.status == 200:
                    run_data = await response.json()
                    status = run_data["data"]["status"]

                    if status == "SUCCEEDED":
                        # Get results
                        async with session.get(
                            f"{self.base_url}/actor-runs/{run_id}/dataset/items",
                            params={"token": self.api_token},
                        ) as results_response:
                            if results_response.status == 200:
                                return await results_response.json()

                    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                        return {"error": f"Run {status.lower()}"}

            await asyncio.sleep(5)  # Wait 5 seconds before checking again

        return {"error": "Timeout waiting for completion"}

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of an Apify task."""
        # Implementation would track task IDs to run IDs.

        return {"status": "unknown", "task_id": task_id}


class PhantomBusterService(DataCollectionService):
    """PhantomBuster automation and data extraction service."""
    def __init__(self):.

        """Initialize PhantomBuster service."""self.api_key = os.getenv("PHANTOM_BUSTER_API_KEY").
        self.base_url = "https://api.phantombuster.com/api/v2"

        if not self.api_key:
            raise ValueError("PHANTOM_BUSTER_API_KEY must be set")

        self.headers = {
            "X-Phantombuster-Key": self.api_key,
            "Content-Type": "application/json",
        }

        # Popular PhantomBuster phantoms for Sophia AI
        self.phantoms = {
            "linkedin_network": "LinkedIn Network Booster",
            "twitter_followers": "Twitter Follower Collector",
            "instagram_posts": "Instagram Post Likers",
            "facebook_groups": "Facebook Group Members",
            "google_maps": "Google Maps Reviews Scraper",
            "email_finder": "Email Finder",
            "lead_generation": "LinkedIn Lead Generation",
        }

        logger.info("PhantomBuster service initialized successfully")

    async def collect_data(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Launch a PhantomBuster phantom to collect data.

                        Args:
                            task: Data collection task configuration

                        Returns:
                            Dict with collection results
        """
        try:.

            # Get phantom ID (would need to be configured)
            phantom_name = self.phantoms.get(task.task_type, task.task_type)

            # Launch phantom
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/phantoms/launch",
                    headers=self.headers,
                    json={"id": phantom_name, "argument": task.parameters},
                ) as response:
                    if response.status == 200:
                        launch_data = await response.json()
                        container_id = launch_data.get("containerId")

                        # Wait for completion
                        result = await self._wait_for_phantom_completion(
                            session, container_id
                        )

                        logger.info(
                            f"PhantomBuster task {task.task_id} completed successfully"
                        )
                        return {
                            "success": True,
                            "task_id": task.task_id,
                            "container_id": container_id,
                            "data": result,
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"PhantomBuster API error: {response.status} - {error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                        }

        except Exception as e:
            logger.error(f"Error in PhantomBuster data collection: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _wait_for_phantom_completion(
        self, session: aiohttp.ClientSession, container_id: str, timeout: int = 600
    ) -> Dict[str, Any]:
        """Wait for PhantomBuster phantom to complete."""
        start_time = datetime.now().

        while (datetime.now() - start_time).seconds < timeout:
            async with session.get(
                f"{self.base_url}/containers/fetch-output",
                headers=self.headers,
                params={"id": container_id},
            ) as response:
                if response.status == 200:
                    output_data = await response.json()
                    if output_data.get("status") == "finished":
                        return output_data.get("output", {})

            await asyncio.sleep(10)  # Wait 10 seconds before checking again

        return {"error": "Timeout waiting for phantom completion"}

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a PhantomBuster task."""
        return {"status": "unknown", "task_id": task_id}.


class TwinglyService(DataCollectionService):
    """Twingly news monitoring and blog search service."""
    def __init__(self):.

        """Initialize Twingly service."""self.api_key = os.getenv("TWINGLY_API_KEY").
        self.base_url = "https://api.twingly.com/blog/search/api/v3/search"

        if not self.api_key:
            raise ValueError("TWINGLY_API_KEY must be set")

        logger.info("Twingly service initialized successfully")

    async def collect_data(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Search for news and blog posts using Twingly.

                        Args:
                            task: Data collection task configuration

                        Returns:
                            Dict with search results
        """
        try:.

            query = task.parameters.get("query", "")
            language = task.parameters.get("language", "en")
            start_date = task.parameters.get("start_date", "")
            end_date = task.parameters.get("end_date", "")

            # Build search query
            search_params = {
                "apikey": self.api_key,
                "q": f"{query} lang:{language}",
                "format": "json",
            }

            if start_date and end_date:
                search_params["q"] += f" start-date:{start_date} end-date:{end_date}"

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=search_params) as response:
                    if response.status == 200:
                        results = await response.json()

                        logger.info(
                            f"Twingly search for '{query}' returned {len(results.get('posts', []))} results"
                        )
                        return {
                            "success": True,
                            "task_id": task.task_id,
                            "query": query,
                            "results_count": len(results.get("posts", [])),
                            "data": results,
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Twingly API error: {response.status} - {error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                        }

        except Exception as e:
            logger.error(f"Error in Twingly data collection: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a Twingly task."""
        return {"status": "completed", "task_id": task_id}  # Twingly is synchronous.


class TavilyService(DataCollectionService):
    """Tavily AI-powered search service."""
    def __init__(self):.

        """Initialize Tavily service."""self.api_key = os.getenv("TAVILY_API_KEY").
        self.base_url = "https://api.tavily.com"

        if not self.api_key:
            raise ValueError("TAVILY_API_KEY must be set")

        logger.info("Tavily service initialized successfully")

    async def collect_data(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Perform AI-powered search using Tavily.

                        Args:
                            task: Data collection task configuration

                        Returns:
                            Dict with search results
        """
        try:.

            query = task.parameters.get("query", "")
            search_depth = task.parameters.get("search_depth", "basic")
            include_answer = task.parameters.get("include_answer", True)
            include_raw_content = task.parameters.get("include_raw_content", False)
            max_results = task.parameters.get("max_results", 10)

            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "max_results": max_results,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/search", json=payload
                ) as response:
                    if response.status == 200:
                        results = await response.json()

                        logger.info(
                            f"Tavily search for '{query}' completed successfully"
                        )
                        return {
                            "success": True,
                            "task_id": task.task_id,
                            "query": query,
                            "results_count": len(results.get("results", [])),
                            "data": results,
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Tavily API error: {response.status} - {error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                        }

        except Exception as e:
            logger.error(f"Error in Tavily data collection: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a Tavily task."""
        return {"status": "completed", "task_id": task_id}  # Tavily is synchronous.


class ZenRowsService(DataCollectionService):
    """ZenRows web scraping service with proxy rotation."""
    def __init__(self):.

        """Initialize ZenRows service."""self.api_key = os.getenv("ZENROWS_API_KEY").
        self.base_url = "https://api.zenrows.com/v1/"

        if not self.api_key:
            raise ValueError("ZENROWS_API_KEY must be set")

        logger.info("ZenRows service initialized successfully")

    async def collect_data(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Scrape web pages using ZenRows.

                        Args:
                            task: Data collection task configuration

                        Returns:
                            Dict with scraping results
        """
        try:.

            url = task.parameters.get("url", "")
            js_render = task.parameters.get("js_render", False)
            premium_proxy = task.parameters.get("premium_proxy", False)
            proxy_country = task.parameters.get("proxy_country", "US")

            params = {"apikey": self.api_key, "url": url}

            if js_render:
                params["js_render"] = "true"
            if premium_proxy:
                params["premium_proxy"] = "true"
                params["proxy_country"] = proxy_country

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        content = await response.text()

                        logger.info(
                            f"ZenRows scraping of '{url}' completed successfully"
                        )
                        return {
                            "success": True,
                            "task_id": task.task_id,
                            "url": url,
                            "content_length": len(content),
                            "data": {
                                "content": content,
                                "headers": dict(response.headers),
                            },
                        }
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"ZenRows API error: {response.status} - {error_text}"
                        )
                        return {
                            "success": False,
                            "error": f"API error: {response.status}",
                        }

        except Exception as e:
            logger.error(f"Error in ZenRows data collection: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a ZenRows task."""
        return {"status": "completed", "task_id": task_id}  # ZenRows is synchronous.


class SophiaDataCollectionOrchestrator:
    """Orchestrator for all data collection services in Sophia AI."""
    def __init__(self):.

        """Initialize data collection orchestrator."""self.services = {.
            "apify": ApifyService(),
            "phantombuster": PhantomBusterService(),
            "twingly": TwinglyService(),
            "tavily": TavilyService(),
            "zenrows": ZenRowsService(),
        }

        self.task_queue = []
        self.active_tasks = {}

        logger.info("Sophia data collection orchestrator initialized successfully")

    async def submit_task(self, task: DataCollectionTask) -> str:
        """Submit a data collection task.

                        Args:
                            task: Data collection task to submit

                        Returns:
                            str: Task ID
        """self.task_queue.append(task).

        logger.info(f"Task {task.task_id} submitted for service {task.service}")
        return task.task_id

    async def execute_task(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Execute a data collection task.

                        Args:
                            task: Data collection task to execute

                        Returns:
                            Dict with execution results
        """
        try:.

            if task.service not in self.services:
                return {"success": False, "error": f"Unknown service: {task.service}"}

            service = self.services[task.service]
            self.active_tasks[task.task_id] = {
                "task": task,
                "status": "running",
                "start_time": datetime.now(),
            }

            result = await service.collect_data(task)

            self.active_tasks[task.task_id]["status"] = "completed"
            self.active_tasks[task.task_id]["end_time"] = datetime.now()
            self.active_tasks[task.task_id]["result"] = result

            return result

        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {str(e)}")
            self.active_tasks[task.task_id]["status"] = "failed"
            self.active_tasks[task.task_id]["error"] = str(e)
            return {"success": False, "error": str(e)}

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a data collection task."""
        if task_id in self.active_tasks:.

            return self.active_tasks[task_id]
        else:
            return {"status": "not_found", "task_id": task_id}

    async def process_queue(self, max_concurrent: int = 5):
        """Process the task queue with concurrency control."""while self.task_queue:.

            # Get next batch of tasks
            batch = []
            for _ in range(min(max_concurrent, len(self.task_queue))):
                if self.task_queue:
                    batch.append(self.task_queue.pop(0))

            if batch:
                # Execute batch concurrently
                tasks = [self.execute_task(task) for task in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                logger.info(f"Processed batch of {len(batch)} tasks")

            await asyncio.sleep(1)  # Brief pause between batches


# Global orchestrator instance
sophia_data_collector = None


def get_data_collector() -> SophiaDataCollectionOrchestrator:
    """Get or create global data collection orchestrator."""global sophia_data_collector.

    if sophia_data_collector is None:
        sophia_data_collector = SophiaDataCollectionOrchestrator()
    return sophia_data_collector


# Convenience functions for common data collection tasks
async def scrape_website(
    url: str, js_render: bool = False, service: str = "zenrows"
) -> Dict[str, Any]:
    """Convenience function for website scraping."""
        collector = get_data_collector().

    task = DataCollectionTask(
        task_id=f"scrape_{datetime.now().timestamp()}",
        service=service,
        task_type="web_scraper",
        parameters={"url": url, "js_render": js_render},
    )
    return await collector.execute_task(task)


async def search_news(
    query: str, days_back: int = 7, service: str = "twingly"
) -> Dict[str, Any]:
    """Convenience function for news searching."""
        collector = get_data_collector().

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    task = DataCollectionTask(
        task_id=f"news_{datetime.now().timestamp()}",
        service=service,
        task_type="news_search",
        parameters={
            "query": query,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        },
    )
    return await collector.execute_task(task)


async def ai_search(
    query: str, depth: str = "basic", service: str = "tavily"
) -> Dict[str, Any]:
    """Convenience function for AI-powered search."""
        collector = get_data_collector()
    task = DataCollectionTask(
        task_id=f"search_{datetime.now().timestamp()}",
        service=service,
        task_type="ai_search",
        parameters={
            "query": query,
            "search_depth": depth,
            "include_answer": True,
            "max_results": 10,
        },
    )
    return await collector.execute_task(task)

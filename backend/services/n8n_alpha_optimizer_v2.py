"""
Sophia AI n8n Alpha Grid Optimizer v2
Dynamic alpha tuning with Prometheus metrics and X trend injection

Date: July 12, 2025
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Optional

import httpx
import numpy as np
from prometheus_client import Counter, Gauge, Histogram

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

# Prometheus metrics
api_latency = Histogram('n8n_api_latency_seconds', 'API latency in seconds', ['endpoint', 'service'])
alpha_value = Gauge('n8n_alpha_value', 'Current alpha value', ['service'])
trend_injections = Counter('n8n_trend_injections_total', 'Total trend injections')
optimization_runs = Counter('n8n_optimization_runs_total', 'Total optimization runs')


class XTrendFetcher:
    """Fetch trends from X (Twitter) for injection"""
    
    def __init__(self):
        self.x_api_key = get_config_value("x_api_key")
        self.x_api_url = "https://api.twitter.com/2"
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def fetch_trends(self, topic: Optional[str] = None) -> list[dict[str, Any]]:
        """Fetch trending topics from X"""
        cache_key = f"trends_{topic or 'general'}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now(UTC) - timestamp).seconds < self.cache_ttl:
                return cached_data
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.x_api_key}"}
                
                if topic:
                    # Search for specific topic trends
                    response = await client.get(
                        f"{self.x_api_url}/tweets/search/recent",
                        headers=headers,
                        params={
                            "query": f"{topic} -is:retweet",
                            "max_results": 10,
                            "tweet.fields": "created_at,public_metrics"
                        }
                    )
                else:
                    # Get general trends
                    response = await client.get(
                        f"{self.x_api_url}/trends/place",
                        headers=headers,
                        params={"id": "1"}  # Worldwide trends
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    trends = self._parse_trends(data, topic)
                    self.cache[cache_key] = (trends, datetime.now(UTC))
                    return trends
                else:
                    logger.warning(f"X API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching X trends: {e}")
            return []
    
    def _parse_trends(self, data: dict[str, Any], topic: Optional[str]) -> list[dict[str, Any]]:
        """Parse trend data from X API response"""
        trends = []
        
        if "data" in data:
            # Search results
            for tweet in data.get("data", []):
                trends.append({
                    "text": tweet.get("text", ""),
                    "metrics": tweet.get("public_metrics", {}),
                    "created_at": tweet.get("created_at"),
                    "relevance": self._calculate_relevance(tweet, topic)
                })
        else:
            # Trending topics
            for trend in data.get("trends", []):
                trends.append({
                    "name": trend.get("name", ""),
                    "tweet_volume": trend.get("tweet_volume", 0),
                    "relevance": 1.0  # General trends are always relevant
                })
        
        # Sort by relevance
        trends.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return trends[:5]  # Top 5 trends
    
    def _calculate_relevance(self, tweet: dict[str, Any], topic: Optional[str]) -> float:
        """Calculate relevance score for a tweet"""
        if not topic:
            return 1.0
        
        text = tweet.get("text", "").lower()
        topic_lower = topic.lower()
        
        # Check for exact match
        if topic_lower in text:
            relevance = 1.0
        else:
            # Check for partial matches
            topic_words = topic_lower.split()
            matches = sum(1 for word in topic_words if word in text)
            relevance = matches / len(topic_words) if topic_words else 0
        
        # Boost by engagement
        metrics = tweet.get("public_metrics", {})
        engagement = (
            metrics.get("retweet_count", 0) * 2 +
            metrics.get("like_count", 0) +
            metrics.get("reply_count", 0) * 3
        )
        engagement_boost = min(0.5, engagement / 1000)
        
        return min(1.0, relevance + engagement_boost)


class AlphaGridOptimizer:
    """Dynamic alpha grid tuning for n8n workflows"""
    
    def __init__(self):
        self.prometheus_url = get_config_value("prometheus_url", "http://localhost:9090")
        self.n8n_url = get_config_value("n8n_url", "http://localhost:5678")
        self.trend_fetcher = XTrendFetcher()
        
        # Alpha grid configuration
        self.alpha_range = (0.45, 0.55)  # Dense range for >150ms APIs
        self.grid_points = 11  # 0.45, 0.46, ..., 0.55
        self.current_alphas = {}  # Service -> alpha mapping
        self.performance_history = {}
        
    async def optimize_alpha(self, service: str, window_minutes: int = 5) -> float:
        """Optimize alpha value for a service based on Prometheus metrics"""
        optimization_runs.inc()
        
        # Get recent performance metrics
        metrics = await self._fetch_prometheus_metrics(service, window_minutes)
        
        if not metrics:
            logger.warning(f"No metrics found for service {service}")
            return self.current_alphas.get(service, 0.5)
        
        # Calculate optimal alpha
        optimal_alpha = await self._calculate_optimal_alpha(service, metrics)
        
        # Update current alpha
        self.current_alphas[service] = optimal_alpha
        alpha_value.labels(service=service).set(optimal_alpha)
        
        logger.info(f"Optimized alpha for {service}: {optimal_alpha}")
        return optimal_alpha
    
    async def _fetch_prometheus_metrics(
        self, 
        service: str, 
        window_minutes: int
    ) -> list[dict[str, Any]]:
        """Fetch metrics from Prometheus"""
        try:
            async with httpx.AsyncClient() as client:
                # Query for API latency
                query = f'api_latency{{service="{service}"}}'
                response = await client.get(
                    f"{self.prometheus_url}/api/v1/query_range",
                    params={
                        "query": query,
                        "start": (datetime.now(UTC) - timedelta(minutes=window_minutes)).timestamp(),
                        "end": datetime.now(UTC).timestamp(),
                        "step": "15s"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_prometheus_response(data)
                else:
                    logger.error(f"Prometheus query failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching Prometheus metrics: {e}")
            return []
    
    def _parse_prometheus_response(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse Prometheus response"""
        metrics = []
        
        for result in data.get("data", {}).get("result", []):
            values = result.get("values", [])
            for timestamp, value in values:
                metrics.append({
                    "timestamp": datetime.fromtimestamp(float(timestamp), UTC),
                    "latency": float(value),
                    "labels": result.get("metric", {})
                })
        
        return metrics
    
    async def _calculate_optimal_alpha(
        self, 
        service: str, 
        metrics: list[dict[str, Any]]
    ) -> float:
        """Calculate optimal alpha based on metrics"""
        if not metrics:
            return 0.5
        
        # Extract latencies
        latencies = [m["latency"] for m in metrics]
        
        # Calculate statistics
        avg_latency = np.mean(latencies)
        p95_latency = np.percentile(latencies, 95)
        std_latency = np.std(latencies)
        
        # Grid search for optimal alpha
        alpha_grid = np.linspace(self.alpha_range[0], self.alpha_range[1], self.grid_points)
        best_alpha = 0.5
        best_score = float('-inf')
        
        for alpha in alpha_grid:
            # Score based on latency threshold
            if p95_latency > 0.15:  # >150ms
                # Prefer higher alpha for slow APIs
                score = alpha * (1 - std_latency / avg_latency)
            else:
                # Prefer lower alpha for fast APIs
                score = (1 - alpha) * (1 - std_latency / avg_latency)
            
            # Penalty for high variance
            if std_latency > avg_latency * 0.5:
                score *= 0.8
            
            if score > best_score:
                best_score = score
                best_alpha = alpha
        
        # Store in history
        if service not in self.performance_history:
            self.performance_history[service] = []
        
        self.performance_history[service].append({
            "timestamp": datetime.now(UTC),
            "alpha": best_alpha,
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "std_latency": std_latency
        })
        
        # Keep only recent history
        self.performance_history[service] = self.performance_history[service][-100:]
        
        return round(best_alpha, 2)
    
    async def inject_trends(
        self, 
        workflow_data: dict[str, Any],
        topic: Optional[str] = None
    ) -> dict[str, Any]:
        """Inject X trends into n8n workflow data"""
        trend_injections.inc()
        
        # Fetch trends
        trends = await self.trend_fetcher.fetch_trends(topic)
        
        if not trends:
            return workflow_data
        
        # Inject trends into workflow
        enriched_data = workflow_data.copy()
        enriched_data["x_trends"] = trends
        enriched_data["trend_timestamp"] = datetime.now(UTC).isoformat()
        
        # Add trend embeddings if needed
        if topic and trends:
            trend_texts = [t.get("text") or t.get("name", "") for t in trends]
            enriched_data["trend_context"] = " ".join(trend_texts[:3])
        
        logger.info(f"Injected {len(trends)} trends into workflow")
        return enriched_data
    
    async def auto_tune_workflow(
        self,
        workflow_id: str,
        service_endpoints: list[str]
    ) -> dict[str, float]:
        """Auto-tune alpha values for all services in a workflow"""
        tuned_alphas = {}
        
        for service in service_endpoints:
            # Optimize alpha for each service
            optimal_alpha = await self.optimize_alpha(service)
            tuned_alphas[service] = optimal_alpha
            
            # Apply to n8n workflow
            await self._apply_alpha_to_workflow(workflow_id, service, optimal_alpha)
        
        return tuned_alphas
    
    async def _apply_alpha_to_workflow(
        self,
        workflow_id: str,
        service: str,
        alpha: float
    ):
        """Apply alpha value to n8n workflow configuration"""
        try:
            async with httpx.AsyncClient() as client:
                # Update workflow configuration
                response = await client.patch(
                    f"{self.n8n_url}/api/v1/workflows/{workflow_id}",
                    json={
                        "nodes": {
                            service: {
                                "parameters": {
                                    "alpha": alpha,
                                    "timeout": int(alpha * 10000),  # Dynamic timeout
                                    "retries": int((1 - alpha) * 5)  # Dynamic retries
                                }
                            }
                        }
                    },
                    headers={"X-N8N-API-KEY": get_config_value("n8n_api_key")}
                )
                
                if response.status_code == 200:
                    logger.info(f"Applied alpha {alpha} to {service} in workflow {workflow_id}")
                else:
                    logger.error(f"Failed to update workflow: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error applying alpha to workflow: {e}")
    
    async def get_optimization_report(self, service: Optional[str] = None) -> dict[str, Any]:
        """Get optimization report for services"""
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "services": {}
        }
        
        services = [service] if service else list(self.current_alphas.keys())
        
        for svc in services:
            if svc in self.performance_history:
                history = self.performance_history[svc]
                recent = history[-10:] if len(history) > 10 else history
                
                report["services"][svc] = {
                    "current_alpha": self.current_alphas.get(svc, 0.5),
                    "avg_latency": np.mean([h["avg_latency"] for h in recent]),
                    "p95_latency": np.mean([h["p95_latency"] for h in recent]),
                    "optimization_count": len(history),
                    "last_optimized": recent[-1]["timestamp"].isoformat() if recent else None
                }
        
        return report 